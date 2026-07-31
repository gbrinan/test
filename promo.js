// api/promo.js — 프로모션 코드 검증 (서버 전용 조회)
// POST { code } → { ok, tier, dino_name, dino_name_en, expires_at }
const SUPABASE_URL = process.env.SUPABASE_URL || "https://menfdmsmixasfkywydut.supabase.co";

export default async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store");
  if (req.method !== "POST") return res.status(405).json({ ok: false, reason: "method_not_allowed" });

  const SERVICE = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!SERVICE) return res.status(500).json({ ok: false, reason: "server_not_configured" });

  const { code } = req.body || {};
  if (!code || !/^[A-Z0-9-]{6,40}$/i.test(code)) {
    return res.status(400).json({ ok: false, reason: "invalid_code" });
  }
  try {
    const r = await fetch(
      `${SUPABASE_URL}/rest/v1/promo_codes?code=eq.${encodeURIComponent(code.toUpperCase())}&select=code,dino_name,dino_name_en,tier,expires_at`,
      { headers: { apikey: SERVICE, Authorization: `Bearer ${SERVICE}` } }
    );
    const rows = await r.json();
    const p = rows?.[0];
    if (!p) return res.status(404).json({ ok: false, reason: "not_found" });
    if (new Date(p.expires_at) < new Date()) return res.status(410).json({ ok: false, reason: "expired" });
    return res.status(200).json({ ok: true, tier: p.tier, dino_name: p.dino_name, dino_name_en: p.dino_name_en, expires_at: p.expires_at });
  } catch (e) {
    console.error("promo error:", e);
    return res.status(500).json({ ok: false, reason: "server_error" });
  }
}
