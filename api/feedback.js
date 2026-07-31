// api/feedback.js — 설문·피드백 수집 (서버 전용 저장)
// POST { rating, ease, nps, best, worst, wish, email?, chapter_ctx?, progress_ctx? }
//      + (선택) Authorization: Bearer <세션 토큰> → user_id 기록
// 저장은 service role 로만 (feedback 테이블은 RLS 잠금 = 클라이언트 직접 접근 불가)
const SUPABASE_URL = process.env.SUPABASE_URL || "https://menfdmsmixasfkywydut.supabase.co";
const SUPABASE_ANON = "sb_publishable_GpBf-BQ4CIgKnFvo2W5cpQ_pdqUCaLQ";

const clampInt = (v, lo, hi) => {
  const n = Number(v);
  return Number.isFinite(n) && n >= lo && n <= hi ? Math.round(n) : null;
};
const clip = (s, max) => (typeof s === "string" ? s.trim().slice(0, max) : null);

export default async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store");
  if (req.method !== "POST") return res.status(405).json({ ok: false, reason: "method_not_allowed" });

  const SERVICE = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!SERVICE) return res.status(500).json({ ok: false, reason: "server_not_configured" });

  const b = req.body || {};
  const row = {
    rating: clampInt(b.rating, 1, 5),
    ease: clampInt(b.ease, 1, 5),
    nps: clampInt(b.nps, 0, 10),
    best: clip(b.best, 2000),
    worst: clip(b.worst, 2000),
    wish: clip(b.wish, 2000),
    email: clip(b.email, 200),
    chapter_ctx: clip(b.chapter_ctx, 200),
    progress_ctx: clip(b.progress_ctx, 200),
  };
  // 최소 한 가지는 답해야 저장 (빈 제출 방지)
  if (row.rating == null && row.nps == null && !row.best && !row.worst && !row.wish) {
    return res.status(400).json({ ok: false, reason: "empty_feedback" });
  }

  // 로그인 사용자면 user_id 식별 (본인 토큰으로 조회 — 위조 불가)
  const bearer = (req.headers.authorization || "").replace(/^Bearer\s+/i, "");
  if (bearer) {
    try {
      const ur = await fetch(`${SUPABASE_URL}/auth/v1/user`, {
        headers: { apikey: SUPABASE_ANON, Authorization: `Bearer ${bearer}` },
      });
      if (ur.ok) {
        const u = await ur.json();
        if (u?.id) { row.user_id = u.id; row.email = row.email || u.email || null; }
      }
    } catch (e) { /* 익명 제출로 진행 */ }
  }

  try {
    const r = await fetch(`${SUPABASE_URL}/rest/v1/feedback`, {
      method: "POST",
      headers: {
        apikey: SERVICE, Authorization: `Bearer ${SERVICE}`,
        "Content-Type": "application/json", Prefer: "return=minimal",
      },
      body: JSON.stringify(row),
    });
    if (!r.ok) {
      console.error("feedback insert failed:", await r.text());
      return res.status(500).json({ ok: false, reason: "insert_failed" });
    }
    return res.status(200).json({ ok: true });
  } catch (e) {
    console.error("feedback error:", e);
    return res.status(500).json({ ok: false, reason: "server_error" });
  }
}
