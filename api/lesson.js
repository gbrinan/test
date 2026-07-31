// api/lesson.js — 프리미엄 챕터 본문 전달 (등급 확인 후에만)
//
// 흐름: 클라이언트가 { id } + Authorization: Bearer <사용자 세션 토큰> 으로 POST.
//       서버가 사용자 토큰으로 entitlements 를 조회(RLS: 본인 행만 보임)해
//       등급이 충분할 때만 본문·퀴즈를 반환한다.
// 특징: service role 키 불필요 — 사용자 자신의 토큰 + publishable 키로 RLS 조회.
import { PREMIUM } from "./_premium.js";

const SUPABASE_URL = process.env.SUPABASE_URL || "https://menfdmsmixasfkywydut.supabase.co";
const SUPABASE_ANON = "sb_publishable_GpBf-BQ4CIgKnFvo2W5cpQ_pdqUCaLQ"; // 공개 키 (프론트와 동일)

export default async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store");
  if (req.method !== "POST") {
    return res.status(405).json({ ok: false, reason: "method_not_allowed" });
  }
  const { id } = req.body || {};
  const lesson = id && PREMIUM[id];
  if (!lesson) {
    return res.status(404).json({ ok: false, reason: "not_found" });
  }
  // 티저 정책: 각 유료 파트의 첫 챕터는 본문 없이 퀴즈만 무료 개방 (비로그인 포함)
  const teaserPayload = () => res.status(200).json({ ok: true, teaser: true, body: "", quiz: lesson.quiz });

  const bearer = (req.headers.authorization || "").replace(/^Bearer\s+/i, "");
  const { promo } = req.body || {};
  // 프로모션 코드 경로 (기간 한정 체험) — 서비스 키로 서버만 조회
  if (!bearer && promo) {
    const SERVICE = process.env.SUPABASE_SERVICE_ROLE_KEY;
    if (SERVICE && /^[A-Z0-9-]{6,40}$/i.test(promo)) {
      try {
        const pr = await fetch(
          SUPABASE_URL + "/rest/v1/promo_codes?code=eq." + encodeURIComponent(promo.toUpperCase()) + "&select=tier,expires_at",
          { headers: { apikey: SERVICE, Authorization: "Bearer " + SERVICE } }
        );
        const rows = await pr.json();
        const p = rows && rows[0];
        if (p && new Date(p.expires_at) > new Date()) {
          if (p.tier < lesson.tier) {
            return res.status(403).json({ ok: false, reason: "tier_required", need: lesson.tier, have: p.tier });
          }
          return res.status(200).json({ ok: true, body: lesson.body, quiz: lesson.quiz });
        }
      } catch (e) { /* 프로모 조회 실패 시 아래 일반 응답으로 */ }
    }
    return res.status(401).json({ ok: false, reason: "promo_invalid" });
  }
  if (!bearer) {
    if (lesson.teaser) return teaserPayload();
    return res.status(401).json({ ok: false, reason: "login_required" });
  }

  try {
    // 사용자 토큰으로 본인 entitlement 조회 (RLS가 타인 행 차단)
    const r = await fetch(
      `${SUPABASE_URL}/rest/v1/entitlements?select=tier`,
      { headers: { apikey: SUPABASE_ANON, Authorization: `Bearer ${bearer}` } }
    );
    if (!r.ok) {
      return res.status(401).json({ ok: false, reason: "invalid_token" });
    }
    const rows = await r.json();
    const tier = rows?.[0]?.tier ?? 0;
    if (tier < lesson.tier) {
      if (lesson.teaser) return teaserPayload();
      return res.status(403).json({ ok: false, reason: "tier_required", need: lesson.tier, have: tier });
    }
    return res.status(200).json({ ok: true, body: lesson.body, quiz: lesson.quiz });
  } catch (e) {
    console.error("lesson error:", e);
    return res.status(500).json({ ok: false, reason: "server_error" });
  }
}
