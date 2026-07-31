// api/admin-set-tier.js — 관리자용 회원 등급 설정
// POST { email, tier } + Authorization: Bearer <관리자 세션 토큰>
// 검증: 호출자 본인의 entitlements.is_admin (RLS: 본인 행만) → 참일 때만 서비스 키로 대상 유저 등급 upsert
const SUPABASE_URL = process.env.SUPABASE_URL || "https://menfdmsmixasfkywydut.supabase.co";
const SUPABASE_ANON = "sb_publishable_GpBf-BQ4CIgKnFvo2W5cpQ_pdqUCaLQ";

export default async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store");
  if (req.method !== "POST") return res.status(405).json({ ok: false, reason: "method_not_allowed" });

  const SERVICE = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!SERVICE) return res.status(500).json({ ok: false, reason: "server_not_configured" });

  const bearer = (req.headers.authorization || "").replace(/^Bearer\s+/i, "");
  if (!bearer) return res.status(401).json({ ok: false, reason: "login_required" });

  const { email, tier } = req.body || {};
  const t = Number(tier);
  if (!email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email) || !(t >= 0 && t <= 3)) {
    return res.status(400).json({ ok: false, reason: "invalid_input" });
  }

  try {
    // 1) 호출자가 관리자인지 (본인 토큰 + RLS)
    const me = await fetch(`${SUPABASE_URL}/rest/v1/entitlements?select=is_admin`, {
      headers: { apikey: SUPABASE_ANON, Authorization: `Bearer ${bearer}` },
    });
    if (!me.ok) return res.status(401).json({ ok: false, reason: "invalid_token" });
    const meRows = await me.json();
    if (!meRows?.[0]?.is_admin) return res.status(403).json({ ok: false, reason: "admin_required" });

    // 2) 대상 유저 조회 (서비스 키 — Auth Admin API)
    const ur = await fetch(
      `${SUPABASE_URL}/auth/v1/admin/users?page=1&per_page=1&email=${encodeURIComponent(email)}`,
      { headers: { apikey: SERVICE, Authorization: `Bearer ${SERVICE}` } }
    );
    const uj = await ur.json();
    const target = (uj.users || []).find(u => (u.email || "").toLowerCase() === email.toLowerCase());
    if (!target) return res.status(404).json({ ok: false, reason: "user_not_found" });

    // 3) 등급 upsert (정확히 지정값으로 — 강등도 허용)
    const up = await fetch(`${SUPABASE_URL}/rest/v1/entitlements`, {
      method: "POST",
      headers: {
        apikey: SERVICE, Authorization: `Bearer ${SERVICE}`,
        "Content-Type": "application/json", Prefer: "resolution=merge-duplicates,return=representation",
      },
      body: JSON.stringify({ user_id: target.id, tier: t, updated_at: new Date().toISOString() }),
    });
    if (!up.ok) {
      const detail = await up.text();
      console.error("upsert failed:", detail);
      return res.status(500).json({ ok: false, reason: "upsert_failed" });
    }
    return res.status(200).json({ ok: true, email, tier: t });
  } catch (e) {
    console.error("admin-set-tier error:", e);
    return res.status(500).json({ ok: false, reason: "server_error" });
  }
}
