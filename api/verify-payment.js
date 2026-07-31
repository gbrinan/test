// api/verify-payment.js — PortOne V2 결제 검증 (Vercel 서버리스 함수)
//
// 흐름: 브라우저가 PortOne.requestPayment() 성공 후 { paymentId, expectedAmount } 를 POST.
//       서버가 PortOne API로 실제 결제를 조회해 status=PAID 이고 금액이 일치하는지 확인.
//       (클라이언트만 믿으면 금액 위변조가 가능하므로 반드시 서버에서 재확인)
//
// 환경변수 (Vercel Project Settings → Environment Variables):
//   PORTONE_API_SECRET = 포트원 관리자콘솔에서 발급한 V2 API Secret (절대 프론트에 두지 말 것)
//
// 실제 서비스에서는 여기서 '이미 처리된 paymentId 인지(중복 지급 방지)'를
// DB(예: Supabase)에 기록/조회하고, 사용자 계정에 entitlement(등급) 를 부여해야 합니다.
// 이 파일은 검증 로직의 골자만 담습니다.
//
// 등급 가격표: 결제된 실제 금액으로 서버가 등급을 판정합니다(클라이언트를 신뢰하지 않음).
// 프론트(claude-guide-demo.html)의 TIERS 가격과 반드시 일치시키세요.
const AMOUNT_TO_TIER = {
  33000: 1, // 초급
  66000: 2, // 중급
  150000: 3, // 고급
};

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ ok: false, reason: "method_not_allowed" });
  }

  const { paymentId, expectedAmount } = req.body || {};
  // paymentId 형식 제한: 프론트가 생성하는 "payment-<uuid>" 패턴만 허용 (경로 조작·이상 입력 차단)
  if (!paymentId || typeof paymentId !== "string" || !/^payment-[0-9a-f-]{36}$/i.test(paymentId)) {
    return res.status(400).json({ ok: false, reason: "invalid_paymentId" });
  }
  // 금액은 필수 + 가격표에 있는 값만 허용 (미전송 우회 차단)
  if (expectedAmount == null || !(Number(expectedAmount) in AMOUNT_TO_TIER)) {
    return res.status(400).json({ ok: false, reason: "invalid_amount" });
  }

  const SECRET = process.env.PORTONE_API_SECRET;
  if (!SECRET) {
    return res.status(500).json({ ok: false, reason: "server_not_configured" });
  }

  try {
    // 1) PortOne 서버에서 실제 결제 조회
    const resp = await fetch(
      `https://api.portone.io/payments/${encodeURIComponent(paymentId)}`,
      { headers: { Authorization: `PortOne ${SECRET}` } }
    );
    if (!resp.ok) {
      return res.status(502).json({ ok: false, reason: "portone_lookup_failed" });
    }
    const payment = await resp.json();

    // 2) 상태 확인 (PAID = 결제 완료, VIRTUAL_ACCOUNT_ISSUED = 가상계좌 발급 대기)
    const paid = payment.status === "PAID";

    // 3) 금액 위변조 확인 (expectedAmount 는 위에서 필수·가격표 값으로 검증됨)
    const amountOk = payment.amount?.total === Number(expectedAmount);

    if (paid && amountOk) {
      // 실제 결제 금액으로 등급 판정 (클라이언트가 보낸 등급을 믿지 않음)
      const tier = AMOUNT_TO_TIER[payment.amount?.total] ?? null;
      if (tier == null) {
        return res.status(200).json({ ok: false, reason: "unknown_amount" });
      }

      // ── 로그인 사용자면 Supabase 계정에 등급 기록 (서버 전용 · 멱등) ──
      // 환경변수: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY (Vercel 서버 전용, 프론트 노출 금지)
      const SB_URL = process.env.SUPABASE_URL;
      const SB_SVC = process.env.SUPABASE_SERVICE_ROLE_KEY;
      const bearer = (req.headers.authorization || "").replace(/^Bearer\s+/i, "");
      let persisted = false;
      if (SB_URL && SB_SVC && bearer) {
        try {
          // 1) 토큰 → 사용자 확인
          const uResp = await fetch(`${SB_URL}/auth/v1/user`, {
            headers: { apikey: SB_SVC, Authorization: `Bearer ${bearer}` },
          });
          const user = uResp.ok ? await uResp.json() : null;
          if (user?.id) {
            const h = {
              apikey: SB_SVC, Authorization: `Bearer ${SB_SVC}`,
              "Content-Type": "application/json",
            };
            // 2) 결제 멱등 기록 — 이미 처리된 paymentId면 등급 재지급 안 함
            const pIns = await fetch(`${SB_URL}/rest/v1/payments`, {
              method: "POST",
              headers: { ...h, Prefer: "resolution=ignore-duplicates,return=representation" },
              body: JSON.stringify({ payment_id: paymentId, user_id: user.id, amount: payment.amount.total, tier }),
            });
            const inserted = pIns.ok && (await pIns.json()).length > 0;
            if (inserted) {
              // 3) 등급 누적 저장: max(기존, 신규)
              const cur = await fetch(
                `${SB_URL}/rest/v1/entitlements?user_id=eq.${user.id}&select=tier`,
                { headers: h }
              ).then(r => r.json());
              const newTier = Math.max(cur?.[0]?.tier ?? 0, tier);
              await fetch(`${SB_URL}/rest/v1/entitlements`, {
                method: "POST",
                headers: { ...h, Prefer: "resolution=merge-duplicates" },
                body: JSON.stringify({ user_id: user.id, tier: newTier, updated_at: new Date().toISOString() }),
              });
            }
            persisted = true;
          }
        } catch (e) {
          console.error("entitlement persist error:", e); // 결제 자체는 유효 — 지급 실패만 로깅
        }
      }

      return res.status(200).json({ ok: true, status: payment.status, tier, persisted });
    }

    return res.status(200).json({
      ok: false,
      reason: !paid ? "not_paid" : "amount_mismatch",
      status: payment.status,
    });
  } catch (e) {
    // 내부 에러 상세는 클라이언트에 노출하지 않음 (서버 로그로만)
    console.error("verify-payment error:", e);
    return res.status(500).json({ ok: false, reason: "verify_error" });
  }
}
