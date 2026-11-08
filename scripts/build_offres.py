"""Régénère les pages d'offres (offre/*.html), sitemap.xml et robots.txt à partir de data.json.
Usage : python3 scripts/build_offres.py   (depuis la racine du dépôt)"""
import json, os, re, shutil
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(SITE, "data.json")))
os.environ.setdefault("ER_DOMAIN", "https://emploirapide24.com")
# 4) Pages d'offres (partage WhatsApp + Google for Jobs) et plan du site
import html, datetime
DOMAIN = os.environ.get("ER_DOMAIN", "https://VOTRE-DOMAINE").rstrip("/")
def hid(s):
    h = 0x811c9dc5
    b = s.encode("utf-16-le")
    for i in range(0, len(b), 2):
        h ^= b[i] | (b[i+1] << 8)
        h = (h * 0x01000193) & 0xffffffff
    n, out, al = h, "", "0123456789abcdefghijklmnopqrstuvwxyz"
    while True:
        n, r = divmod(n, 36); out = al[r] + out
        if n == 0: break
    return out
COUNTRY = {"Sénégal":"SN","Côte d'Ivoire":"CI","Cameroun":"CM","RD Congo":"CD","Congo":"CG","Gabon":"GA","Bénin":"BJ","Togo":"TG","Burkina Faso":"BF","Mali":"ML","Niger":"NE","Guinée":"GN","Mauritanie":"MR","Madagascar":"MG","Maroc":"MA","Tunisie":"TN","Tchad":"TD","Ghana":"GH","Kenya":"KE","Haïti":"HT","Belgique":"BE","France":"FR","Suisse":"CH","Luxembourg":"LU","Canada":"CA","Espagne":"ES","Italie":"IT","Autriche":"AT","États-Unis":"US","Singapour":"SG","Thaïlande":"TH","Panama":"PA"}
ETYPE = {"CDI":"FULL_TIME","CDD":"TEMPORARY","Stage":"INTERN","Volontariat":"VOLUNTEER","Consultant":"CONTRACTOR","Freelance":"CONTRACTOR","Saisonnier":"TEMPORARY"}
odir = os.path.join(SITE, "offre"); shutil.rmtree(odir, ignore_errors=True); os.makedirs(odir)
today = d.get("maj", "")
urls = [DOMAIN + "/"]
E = lambda x: html.escape(str(x or ""), quote=True)
for j in d["offres"]:
    if j.get("lim") and j["lim"] < today: continue
    i = hid(j["t"] + "|" + j["e"]); j_url = f"{DOMAIN}/offre/{i}.html"
    lieu = (j.get("v") + ", " if j.get("v") and j.get("v") != j["p"] else "") + j["p"]
    desc = j.get("desc") or f"Offre d'emploi {j['t']} chez {j['e']} ({lieu})."
    apply = j.get("lien") or j["u"]
    ld = None
    if j.get("desc") and j.get("c") not in ("Programme", "Forum", "Concours"):
        secs = "".join("<p><b>"+t+"</b></p><ul>"+"".join("<li>"+html.escape(str(x))+"</li>" for x in (j.get(k) if isinstance(j.get(k),list) else [j.get(k)]) if x)+"</ul>" for t,k in (("Missions","mis"),("Profil recherché","pro"),("Conditions et avantages","plus")) if j.get(k))
        ld = {"@context":"https://schema.org/","@type":"JobPosting","title":j["t"],"description":"<p>"+html.escape(j["desc"])+"</p>"+secs,
              "datePosted": j.get("pub") or j.get("add") or today,
              "hiringOrganization":{"@type":"Organization","name":j["e"]},
              "directApply": False, "url": j_url}
        if j.get("lim"): ld["validThrough"] = j["lim"] + "T23:59:59"
        if j.get("tt"):
            ld["jobLocationType"] = "TELECOMMUTE"; ld["applicantLocationRequirements"] = {"@type":"Country","name":"Monde"}
        else:
            ld["jobLocation"] = {"@type":"Place","address":{"@type":"PostalAddress","addressLocality": j.get("v") or j["p"],"addressCountry": COUNTRY.get(j["p"], j["p"])}}
        if j.get("c") in ETYPE: ld["employmentType"] = ETYPE[j["c"]]
    mails = [m for m in re.split(r"[,;]\s*", j.get("mail") or "") if m]
    page = f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(j['t'])} – {E(j['e'])} ({E(lieu)}) | Emploi Rapide 24</title>
<meta name="description" content="{E(desc[:155])}">
<link rel="canonical" href="{j_url}">
<meta property="og:type" content="website"><meta property="og:title" content="{E(j['t'])} – {E(j['e'])}">
<meta property="og:description" content="{E(desc[:200])}"><meta property="og:url" content="{j_url}"><meta property="og:image" content="{DOMAIN}/icons/icon-512.png">
<meta name="theme-color" content="#1d5bd8"><link rel="icon" href="../icons/icon-192.png">
{('<script type="application/ld+json">'+json.dumps(ld, ensure_ascii=False).replace("</","<\\/")+'</script>') if ld else ''}
<style>body{{font:16px/1.6 system-ui,sans-serif;max-width:720px;margin:0 auto;padding:24px 18px;color:#0f1a33;background:#ffffff}}h1{{font-size:24px;line-height:1.25;margin:8px 0}}.m{{color:#56607a}}.b{{display:inline-block;background:#1d5bd8;color:#fff;padding:10px 16px;border-radius:10px;text-decoration:none;font-weight:650;margin:6px 6px 0 0}}.g{{background:#0f1a33}}.box{{background:#ffffff;border:1px solid #dde2ee;border-radius:12px;padding:12px 14px;margin:14px 0}}a{{color:#1d5bd8}}</style></head><body>
<p><a href="../#o={i}">← Toutes les offres sur Emploi Rapide 24</a></p>
<h1>{E(j['t'])}</h1>
<p class="m"><b>{E(j['e'])}</b> · {E(lieu)} · {E(j['s'])} · {E('Contrat non précisé' if j['c']=='Emploi' else j['c'])}</p>
{f'<p class="m">Date limite : <b>{E(j["lim"])}</b></p>' if j.get('lim') else ''}
{f'<p>{E(j["desc"])}</p>' if j.get('desc') else ''}
{''.join(f'<h2 style="font-size:17px;margin:16px 0 4px">{t}</h2><ul>'+''.join(f'<li>{E(x)}</li>' for x in (j.get(k) if isinstance(j.get(k),list) else [j.get(k)]) if x)+'</ul>' for t,k in (('Missions','mis'),('Profil recherché','pro'),('Conditions et avantages','plus')) if j.get(k))}
<div class="box"><b>Comment postuler</b><br>
{''.join(f'✉️ <a href="mailto:{E(m)}">{E(m)}</a><br>' for m in mails)}
{f'<p style="margin:6px 0 0">{E(j["cons"])}</p>' if j.get('cons') else ''}
<a class="b g" href="{E(apply)}" rel="noopener" target="_blank">Postuler / voir l'annonce d'origine</a>
<a class="b" href="../#o={i}">Préparer ma candidature</a></div>
<p class="m" style="font-size:13px">Source : {E(j['src'])}. Résumé rédigé par Emploi Rapide 24 ; seule l'annonce d'origine fait foi. Un vrai recruteur ne demande jamais d'argent.</p>
</body></html>"""
    open(os.path.join(odir, i + ".html"), "w").write(page)
    urls.append(j_url)
open(os.path.join(SITE, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls) + "</urlset>\n")
open(os.path.join(SITE, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")
print("ok", len(d["offres"]), "pages", len(urls)-1)
