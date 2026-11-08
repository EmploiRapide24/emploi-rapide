// Emploi Rapide 24 – alertes par e-mail (fonction Supabase « alertes »)
// Chaque matin (pg_cron), envoie à chaque abonné les nouvelles offres du jour qui correspondent à ses critères.
// GET ?desabo=<jeton> : désabonnement en un clic depuis l'e-mail.
import { createClient } from "jsr:@supabase/supabase-js@2";

const SB = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
const BREVO = Deno.env.get("BREVO_API_KEY") ?? "";
const SITE = "https://emploirapide24.com";
const FN = (Deno.env.get("SUPABASE_URL") ?? "") + "/functions/v1/alertes";

type Offre = Record<string, any>;
const norm = (s: unknown) => String(s ?? "").toLowerCase().normalize("NFD").replace(/\p{M}/gu, "");
const L = (x: unknown) => (Array.isArray(x) ? x : x ? [x] : []) as string[];
const esc = (s: unknown) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]!));
function hid(s: string) { let h = 0x811c9dc5; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 0x01000193) >>> 0; } return h.toString(36); }
const zoneOf = (j: Offre) => j.z || "Afrique francophone";
const deb = (j: Offre) => j.c === "Stage" || j.c === "Volontariat" || j.exp === 0 || /stagiaire|stage|graduate|junior|jeune dipl|debutant/.test(norm(j.t));

function match(j: Offre, s: Record<string, any>) {
  const f = new Set<string>(s.f || []);
  if (s.z && zoneOf(j) !== s.z) return false;
  if (s.pays && j.p !== s.pays) return false;
  if (s.secteur && j.s !== s.secteur) return false;
  if (s.contrat && j.c !== s.contrat) return false;
  if (s.k && j.k !== s.k) return false;
  if ((f.has("deb") || f.has("stage")) && !deb(j)) return false;
  if (f.has("mail") && !j.mail) return false;
  if (f.has("direct") && !j.d) return false;
  if (f.has("li") && !j.li) return false;
  if (f.has("tt") && !j.tt) return false;
  if (f.has("ouv") && !j.ouv) return false;
  if (f.has("monde") && zoneOf(j) === "Afrique francophone") return false;
  const q = norm(s.q).trim();
  if (q) {
    const hay = norm([j.t, j.e, j.v, j.p, j.s, j.desc, j.c, L(j.mis).join(" "), L(j.pro).join(" "), L(j.plus).join(" "), j.sal].join(" "));
    if (!q.split(/\s+/).every((w) => hay.includes(w))) return false;
  }
  return true;
}

const page = (titre: string, texte: string) => new Response(
  `<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${titre}</title>
  <body style="font-family:Arial,sans-serif;max-width:520px;margin:40px auto;padding:0 20px;color:#1f2937">
  <p style="font-size:22px;font-weight:800;color:#1d5bd8">Emploi Rapide <span style="color:#22c55e">24</span></p>
  <h1 style="font-size:20px">${titre}</h1><p>${texte}</p><p><a href="${SITE}" style="color:#1d5bd8">Retour sur emploirapide24.com</a></p></body>`,
  { headers: { "content-type": "text/html; charset=utf-8" } });

function emailHTML(libelle: string, offres: Offre[], total: number, jeton: string) {
  const lignes = offres.map((j) => {
    const lieu = [j.v && j.v !== j.p ? j.v : "", j.p].filter(Boolean).join(", ");
    const lim = j.lim ? ` · Date limite : ${new Date(j.lim + "T00:00:00").toLocaleDateString("fr-FR", { day: "numeric", month: "long" })}` : "";
    return `<tr><td style="padding:12px 0;border-bottom:1px solid #e5e7eb">
      <a href="${SITE}/offre/${hid(j.t + "|" + j.e)}.html" style="font-size:16px;font-weight:700;color:#1d5bd8;text-decoration:none">${esc(j.t)}</a>
      <div style="font-size:14px;color:#374151;margin-top:2px">${esc(j.e)} · ${esc(lieu)}</div>
      <div style="font-size:13px;color:#6b7280;margin-top:2px">${esc(j.c === "Emploi" ? "Contrat non précisé" : j.c)}${lim}</div></td></tr>`;
  }).join("");
  const plus = total > offres.length ? `<p style="font-size:14px">Et ${total - offres.length} autre(s) sur <a href="${SITE}" style="color:#1d5bd8">emploirapide24.com</a>.</p>` : "";
  return `<div style="font-family:Arial,Helvetica,sans-serif;max-width:560px;margin:0 auto;padding:20px;color:#1f2937">
  <p style="font-size:22px;font-weight:800;color:#1d5bd8;margin:0 0 12px">Emploi Rapide <span style="color:#22c55e">24</span></p>
  <p style="font-size:16px;margin:0 0 4px">Bonjour,</p>
  <p style="font-size:16px;margin:0 0 12px">${total} nouvelle(s) offre(s) pour votre alerte <b>${esc(libelle)}</b> :</p>
  <table style="width:100%;border-collapse:collapse">${lignes}</table>${plus}
  <p style="font-size:13px;color:#4b5563;margin-top:16px">⚠️ Un vrai recruteur ne demande jamais d'argent. Ne payez jamais pour postuler.</p>
  <p style="font-size:12px;color:#9ca3af;margin-top:16px">Vous recevez cet e-mail car vous avez créé cette alerte sur emploirapide24.com.
  <a href="${FN}?desabo=${jeton}" style="color:#9ca3af">Se désabonner de cette alerte</a>.</p></div>`;
}

Deno.serve(async (req) => {
  const url = new URL(req.url);
  const desabo = url.searchParams.get("desabo");
  if (desabo) {
    if (!/^[0-9a-f-]{36}$/i.test(desabo)) return page("Lien invalide", "Ce lien de désabonnement n'est pas valide.");
    await SB.from("abonnements").update({ actif: false }).eq("jeton", desabo);
    return page("Vous êtes désabonné", "Vous ne recevrez plus d'e-mails pour cette alerte. Vous pouvez en recréer une à tout moment sur le site.");
  }
  if (req.method !== "POST") return new Response("ok");
  if (new Date().getUTCHours() < 7) return Response.json({ envoyes: 0, raison: "trop tôt (avant 7 h)" });
  if (!BREVO) return Response.json({ erreur: "BREVO_API_KEY manquante" }, { status: 500 });

  const d = await (await fetch(`${SITE}/data.json?t=${Date.now()}`)).json();
  const jour: string = d.maj;
  const nouvelles: Offre[] = (d.offres || []).filter((o: Offre) => (o.add || "") === jour);
  const { data: abos, error } = await SB.from("abonnements").select("id,email,criteres,libelle,jeton,dernier_envoi").eq("actif", true);
  if (error) return Response.json({ erreur: error.message }, { status: 500 });

  let envoyes = 0, sansOffre = 0;
  for (const a of abos ?? []) {
    if (a.dernier_envoi === jour) continue;
    const m = nouvelles.filter((j) => match(j, a.criteres || {}));
    if (!m.length) { sansOffre++; continue; }
    const r = await fetch("https://api.brevo.com/v3/smtp/email", {
      method: "POST",
      headers: { "api-key": BREVO, "content-type": "application/json", accept: "application/json" },
      body: JSON.stringify({
        sender: { name: "Emploi Rapide 24", email: "noreply@emploirapide24.com" },
        to: [{ email: a.email }],
        subject: `${m.length} nouvelle${m.length > 1 ? "s" : ""} offre${m.length > 1 ? "s" : ""} : ${a.libelle || "votre alerte"}`,
        htmlContent: emailHTML(a.libelle || "Toutes les offres", m.slice(0, 15), m.length, a.jeton),
      }),
    });
    if (r.ok) { envoyes++; await SB.from("abonnements").update({ dernier_envoi: jour }).eq("id", a.id); }
  }
  return Response.json({ jour, nouvelles: nouvelles.length, abonnes: abos?.length ?? 0, envoyes, sansOffre });
});
