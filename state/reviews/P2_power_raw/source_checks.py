"""Verify saved native-source identities and retain reviewer-selected RM pages."""
from pathlib import Path
import hashlib
import json
import pymupdf

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
headers = ROOT / "state/analysis/P2_adc_ownership_raw/headers"
manifest = json.loads((headers / "manifest.json").read_text())
checks = []
for item in manifest["files"]:
    raw = (headers / item["name"]).read_bytes()
    checks.append(dict(name=item["name"], bytes=len(raw),
        sha256=hashlib.sha256(raw).hexdigest(),
        matched=len(raw) == item["bytes"] and hashlib.sha256(raw).hexdigest() == item["sha256"]))
pdf = ROOT / "build/cache/RM0456_Rev6_52152e41.pdf"
pdf_hash = hashlib.sha256(pdf.read_bytes()).hexdigest()
assert pdf_hash == "52152e414e2ac329cfd9038481b97e8ff70592f9892d171dcb63b7d283722616"
doc = pymupdf.open(pdf)
pages = []
for p in (410, 411, 1276, 1277, 1278, 1280, 1281, 1288, 1289, 1297, 1344, 1345, 1347, 1351, 1353, 1361, 1366, 1367):
    text = doc[p - 1].get_text()
    pages.append(dict(page=p, text_sha256=hashlib.sha256(text.encode()).hexdigest(), text=text))
result = dict(kind="offline-source-only", all_headers_match=all(x["matched"] for x in checks),
    headers=checks, pdf_sha256=pdf_hash, pages=pages)
assert result["all_headers_match"]
(OUT / "source_checks.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(dict(all_headers_match=result["all_headers_match"], headers=len(checks),
    pdf_sha256=pdf_hash, retained_pages=len(pages))))
