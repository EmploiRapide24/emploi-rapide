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
from urllib.parse import quote
_open = [x for x in d["offres"] if not (x.get("lim") and x["lim"] < today)]
def simil(j):
    c = [x for x in _open if x is not j and x["p"] == j["p"] and x.get("s") == j.get("s")]
    c += [x for x in _open if x is not j and x["p"] == j["p"] and x not in c]
    c += [x for x in _open if x is not j and x.get("s") == j.get("s") and x not in c]
    c = c[:5]
    if not c: return ""
    return '<h2 style="font-size:17px;margin:20px 0 4px">Offres similaires</h2><ul class="sim">' + "".join('<li><a href="' + hid(x["t"] + "|" + x["e"]) + '.html">' + E(x["t"]) + '</a><span>' + E(x["e"]) + " · " + E(x["p"]) + '</span></li>' for x in c) + '</ul>'
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
    ldjs = ('<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace("</", "<\\/") + '</script>') if ld else ''
    page = f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(j['t'])} – {E(j['e'])} ({E(lieu)}) | Emploi Rapide 24</title>
<meta name="description" content="{E(desc[:155])}">
<link rel="canonical" href="{j_url}">
<meta property="og:type" content="website"><meta property="og:title" content="{E(j['t'])} – {E(j['e'])}">
<meta property="og:description" content="{E(desc[:200])}"><meta property="og:url" content="{j_url}"><meta property="og:image" content="{DOMAIN}/icons/og.png">
<meta name="theme-color" content="#1d5bd8"><link rel="icon" href="../icons/icon-192.png"><script src="../ga.js" defer></script>
{ldjs}
<style>body{{font:16px/1.6 system-ui,sans-serif;max-width:720px;margin:0 auto;padding:24px 18px;color:#0f1a33;background:#ffffff}}h1{{font-size:24px;line-height:1.25;margin:8px 0}}.m{{color:#56607a}}.b{{display:inline-block;background:#1d5bd8;color:#fff;padding:10px 16px;border-radius:10px;text-decoration:none;font-weight:650;margin:6px 6px 0 0}}.g{{background:#0f1a33}}.wa{{background:#25d366}}.al{{background:#f5b800;color:#0f1a33}}.sim{{list-style:none;padding:0}}.sim li{{border:1px solid #dde2ee;border-radius:10px;padding:8px 12px;margin:6px 0}}.sim a{{font-weight:650;text-decoration:none}}.sim span{{display:block;font-size:13px;color:#56607a}}.box{{background:#ffffff;border:1px solid #dde2ee;border-radius:12px;padding:12px 14px;margin:14px 0}}a{{color:#1d5bd8}}</style></head><body>
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
<a class="b wa" href="https://wa.me/?text={quote(j['t']+' – '+j['e']+' ('+lieu+') : '+j_url)}" target="_blank" rel="noopener">💬 Partager sur WhatsApp</a>
<a class="b al" href="../#alerte={quote(j['p'])}">📧 Recevoir les offres {E(j['p'])} par e-mail</a>
{simil(j)}
<p class="m" style="font-size:13px">Source : {E(j['src'])}. Résumé rédigé par Emploi Rapide 24 ; seule l'annonce d'origine fait foi. Un vrai recruteur ne demande jamais d'argent.</p>
</body></html>"""
    open(os.path.join(odir, i + ".html"), "w").write(page)
    urls.append(j_url)
# Page « Toutes les offres » (liste publique regroupée par pays)
groupes = {}
for j in d["offres"]:
    if j.get("lim") and j["lim"] < today: continue
    groupes.setdefault(j["p"], []).append(j)
ordre = sorted(groupes, key=lambda p: (-len(groupes[p]), p))
def ligne(j):
    i = hid(j["t"] + "|" + j["e"])
    v = j.get("v") if j.get("v") and j.get("v") != j["p"] else ""
    c = "Contrat non précisé" if j.get("c") == "Emploi" else (j.get("c") or "")
    lim = ("Date limite : " + j["lim"]) if j.get("lim") else ""
    meta = " · ".join(x for x in (E(j["e"]), E(v), E(c), E(lim)) if x)
    return '<li><a href="offre/' + i + '.html">' + E(j["t"]) + '</a><span>' + meta + '</span></li>'
blocs = "".join('<h2 id="' + E(hid(p)) + '">' + E(p) + ' <small>(' + str(len(groupes[p])) + ')</small></h2><ul>' + "".join(ligne(j) for j in sorted(groupes[p], key=lambda j: (j.get("lim") or "9999", j["t"]))) + '</ul>' for p in ordre)
sommaire = " · ".join('<a href="#' + E(hid(p)) + '">' + E(p) + ' (' + str(len(groupes[p])) + ')</a>' for p in ordre)
n_total = sum(len(v) for v in groupes.values())
liste = ('<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
 '<title>Toutes les offres d\'emploi (' + str(n_total) + ') – Emploi Rapide 24</title>'
 '<meta name="description" content="Liste complète des ' + str(n_total) + ' offres d\'emploi ouvertes en Afrique francophone et dans le monde, mise à jour chaque matin.">'
 '<link rel="canonical" href="' + DOMAIN + '/offres.html"><script src="ga.js" defer></script><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;800&display=swap">'
 '<style>body{font-family:Nunito,system-ui,sans-serif;margin:0;color:#1f2937;background:#f3f6fb}main{max-width:1100px;margin:0 auto;padding:20px 16px 60px}'
 'h1{font-size:26px;margin:6px 0 4px;color:#1d5bd8}h2{font-size:19px;margin:26px 0 8px;padding-top:6px;border-top:1px solid #dbe3f0}h2 small{color:#6b7280;font-weight:600}'
 '.som{font-size:14px;line-height:1.9}.som a,ul a{color:#1d5bd8;text-decoration:none}.som a:hover,ul a:hover{text-decoration:underline}'
 'ul{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:8px}li{background:#fff;border:1px solid #e3e8f2;border-radius:12px;padding:10px 12px}'
 'li a{font-weight:800;display:block}li span{font-size:13px;color:#6b7280}.top{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap}.btn{background:#1d5bd8;color:#fff;border-radius:999px;padding:8px 16px;text-decoration:none;font-weight:700}</style></head><body><main>'
 '<div class="top"><a href="./" style="font-weight:800;color:#1d5bd8;text-decoration:none;font-size:20px">Emploi Rapide <span style="color:#f5b800">24</span></a><a class="btn" href="./">Rechercher et filtrer</a></div>'
 '<h1>Toutes les offres d\'emploi (' + str(n_total) + ')</h1><p style="margin:0 0 10px;color:#4b5563">Mise à jour du ' + E(today) + '. Classées par pays, puis par date limite.</p>'
 '<p class="som">' + sommaire + '</p>' + blocs +
 '<p style="font-size:13px;color:#6b7280;margin-top:30px">Un vrai recruteur ne demande jamais d\'argent. Seule l\'annonce d\'origine fait foi.</p></main></body></html>')
# Pages par pays, par pays × secteur et stages (SEO)
import unicodedata
def slug(x):
    x = unicodedata.normalize("NFKD", x).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", x).strip("-")
PREP = {"Sénégal":"au Sénégal","Côte d'Ivoire":"en Côte d'Ivoire","Cameroun":"au Cameroun","RD Congo":"en RD Congo","Congo":"au Congo","Gabon":"au Gabon","Bénin":"au Bénin","Togo":"au Togo","Burkina Faso":"au Burkina Faso","Mali":"au Mali","Niger":"au Niger","Guinée":"en Guinée","Mauritanie":"en Mauritanie","Madagascar":"à Madagascar","Maroc":"au Maroc","Tunisie":"en Tunisie","Tchad":"au Tchad","Algérie":"en Algérie","Centrafrique":"en Centrafrique","Burundi":"au Burundi","Rwanda":"au Rwanda","Djibouti":"à Djibouti","Comores":"aux Comores","Haïti":"en Haïti","France":"en France","Belgique":"en Belgique","Suisse":"en Suisse","Canada":"au Canada","Luxembourg":"au Luxembourg","Monde (télétravail)":"en télétravail"}
MOIS = ["janvier","février","mars","avril","mai","juin","juillet","août","septembre","octobre","novembre","décembre"]
mois = MOIS[int(today[5:7])-1] + " " + today[:4] if len(today) >= 7 else ""
edir = os.path.join(SITE, "emploi"); shutil.rmtree(edir, ignore_errors=True); os.makedirs(edir)
def ligne2(j):
    return ligne(j).replace('href="offre/', 'href="../offre/')
def page_cat(fn, titre, h1, intro, offres, liens=""):
    n = len(offres)
    html_ = ('<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
     '<title>' + E(titre) + '</title><meta name="description" content="' + E(intro[:155]) + '">'
     '<link rel="canonical" href="' + DOMAIN + '/emploi/' + fn + '"><meta property="og:image" content="' + DOMAIN + '/icons/og.png"><link rel="icon" href="../icons/icon-192.png"><script src="../ga.js" defer></script>'
     '<style>body{font-family:system-ui,sans-serif;margin:0;color:#1f2937;background:#f3f6fb}main{max-width:1000px;margin:0 auto;padding:20px 16px 60px}h1{font-size:25px;margin:8px 0 6px;color:#1d5bd8}p{text-align:justify}'
     'ul{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:8px}li{background:#fff;border:1px solid #e3e8f2;border-radius:12px;padding:10px 12px}li a{font-weight:800;display:block;color:#1d5bd8;text-decoration:none}li span{font-size:13px;color:#6b7280}'
     '.tags a{display:inline-block;margin:3px 4px 3px 0;padding:5px 11px;border-radius:999px;background:#fff;border:1px solid #dbe3f0;color:#1d5bd8;text-decoration:none;font-size:14px;font-weight:600}.cta{display:inline-block;margin:10px 8px 14px 0;padding:10px 16px;border-radius:10px;text-decoration:none;font-weight:700}</style></head><body><main>'
     '<p><a href="../" style="font-weight:800;color:#1d5bd8;text-decoration:none;font-size:19px">Emploi Rapide <span style="color:#f5b800">24</span></a> › <a href="../offres.html" style="color:#1d5bd8">Toutes les offres</a></p>'
     '<h1>' + E(h1) + '</h1><p>' + E(intro) + '</p>'
     '<a class="cta" style="background:#f5b800;color:#0f1a33" href="../#alerte">📧 Recevoir ces offres par e-mail</a>'
     '<a class="cta" style="background:#25d366;color:#fff" href="https://wa.me/?text=' + quote(h1 + ' : ' + DOMAIN + '/emploi/' + fn) + '" target="_blank" rel="noopener">💬 Partager sur WhatsApp</a>'
     + liens + '<ul>' + "".join(ligne2(j) for j in sorted(offres, key=lambda j: (j.get("lim") or "9999", j["t"]))) + '</ul>'
     '<p style="font-size:13px;color:#6b7280;margin-top:26px">Liste mise à jour le ' + E(today) + '. Résumés rédigés par Emploi Rapide 24 ; seule l\'annonce d\'origine fait foi. Un vrai recruteur ne demande jamais d\'argent.</p></main></body></html>')
    open(os.path.join(edir, fn), "w").write(html_); urls.append(DOMAIN + "/emploi/" + fn)
n_off = len(urls) - 1
cats = {}
for pays_, lst in groupes.items():
    if len(lst) < 3: continue
    pr = PREP.get(pays_, "– " + pays_)
    secs = {}
    for j in lst: secs.setdefault(j.get("s") or "Autres", []).append(j)
    stg = [j for j in lst if j.get("c") in ("Stage", "Volontariat") or j.get("exp") == 0]
    sub = []
    for sec, l2 in sorted(secs.items(), key=lambda x: -len(x[1])):
        if len(l2) >= 3:
            fn2 = "offres-emploi-" + slug(pays_) + "-" + slug(sec) + ".html"
            page_cat(fn2, f"Emploi {sec} {pr} ({len(l2)} offres) – {mois} | Emploi Rapide 24", f"Offres d'emploi {sec} {pr}",
                     f"{len(l2)} offres d'emploi ouvertes dans le secteur {sec} {pr}, vérifiées et mises à jour chaque matin, avec l'adresse et les étapes pour postuler.", l2,
                     '<p class="tags"><a href="offres-emploi-' + slug(pays_) + '.html">← Toutes les offres ' + E(pr) + '</a></p>')
            sub.append((sec, fn2, len(l2)))
    if len(stg) >= 2:
        fn3 = "stages-" + slug(pays_) + ".html"
        page_cat(fn3, f"Stages et premiers emplois {pr} ({len(stg)}) – {mois} | Emploi Rapide 24", f"Stages et premiers emplois {pr}",
                 f"{len(stg)} stages, volontariats et postes ouverts aux débutants {pr}, mis à jour chaque matin.", stg,
                 '<p class="tags"><a href="offres-emploi-' + slug(pays_) + '.html">← Toutes les offres ' + E(pr) + '</a></p>')
        sub.insert(0, ("Stages et débutants", fn3, len(stg)))
    fn = "offres-emploi-" + slug(pays_) + ".html"
    tags = ('<p class="tags">' + "".join('<a href="' + f + '">' + E(t) + ' (' + str(n) + ')</a>' for t, f, n in sub) + '</p>') if sub else ""
    page_cat(fn, f"Offres d'emploi {pr} ({len(lst)}) – {mois} | Emploi Rapide 24", f"Offres d'emploi {pr}",
             f"{len(lst)} offres d'emploi ouvertes {pr} : entreprises, institutions et ONG. Chaque offre est vérifiée à la source, avec l'adresse et les étapes pour postuler. Mise à jour chaque matin.", lst, tags)
    cats[pays_] = fn
liste = liste.replace('<p class="som">', '<p class="som"><b>Pages par pays :</b> ' + " · ".join('<a href="emploi/' + cats[p] + '">' + E(p) + '</a>' for p in ordre if p in cats) + '</p><p class="som">', 1)
open(os.path.join(SITE, "offres.html"), "w").write(liste)
urls.insert(1, DOMAIN + "/offres.html")
open(os.path.join(SITE, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls) + "</urlset>\n")
open(os.path.join(SITE, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")
print("ok", len(d["offres"]), "pages", n_off, "categories", len(os.listdir(edir)))
