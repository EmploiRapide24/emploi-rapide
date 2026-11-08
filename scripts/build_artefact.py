"""Construit artefact/index.html (page autonome pour l'artefact claude.ai) à partir de data.json.
Usage : python3 scripts/build_artefact.py   (depuis la racine du dépôt)"""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(ROOT, "data.json"), encoding="utf-8"))
tpl = open(os.path.join(ROOT, "artefact", "template.html"), encoding="utf-8").read()
emb = json.dumps(d, ensure_ascii=False).replace("</", "<\\/")
out = tpl.replace("__DATA__", emb, 1)
open(os.path.join(ROOT, "artefact", "index.html"), "w", encoding="utf-8").write(out)
print("ok", d.get("maj"), len(d.get("offres", [])), "offres", len(out), "octets")
