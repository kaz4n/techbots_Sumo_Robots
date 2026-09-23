"""Preserve exact cached primary-source excerpts for the fixed ADC1 pair audit."""
from pathlib import Path
import hashlib
import json
import pymupdf

root = Path(__file__).resolve().parents[4]
out = Path(__file__).resolve().parent
pdf = root / "build/cache/RM0456_Rev6_52152e41.pdf"
pdf_hash = hashlib.sha256(pdf.read_bytes()).hexdigest()
assert pdf_hash == "52152e414e2ac329cfd9038481b97e8ff70592f9892d171dcb63b7d283722616"
manifest = {"scope": "Cached primary-source extraction plus pinned official overlay refresh receipt; no board access",
            "pdf": str(pdf.relative_to(root)), "pdf_sha256": pdf_hash,
            "pdf_url": "https://www.stmcu.jp/wp/wp-content/uploads/2021/07/RM0456_Rev6.pdf",
            "pages": [], "headers": []}
doc = pymupdf.open(pdf)
pages = [1272, 1273, 1282, 1283, 1284, 1285, 1287, 1288, 1289, 1297,
         1352, 1353, 1354, 1355, 1356, 1447, 1448, 1449, 1450,
         1467, 1468, 1469, 1479, 1480]
for number in pages:
    page = doc[number - 1]
    body = page.get_text().encode("utf-8")
    path = out / f"RM0456_p{number}.txt"
    path.write_bytes(body)
    entry = {"page": number, "text": path.name,
             "text_sha256": hashlib.sha256(body).hexdigest()}
    if number in (1353, 1354, 1355, 1467, 1468, 1479):
        rendered = out / f"RM0456_p{number}.png"
        page.get_pixmap(matrix=pymupdf.Matrix(1.2, 1.2)).save(rendered)
        entry["rendered"] = rendered.name
        entry["rendered_sha256"] = hashlib.sha256(rendered.read_bytes()).hexdigest()
    manifest["pages"].append(entry)

headers = root / "state/analysis/P2_adc_ownership_raw/headers"
original = json.loads((headers / "manifest.json").read_text())
expected = {row["name"]: row for row in original["files"]}
selections = {
    "stm32u5xx_ll_adc.h": [(470, 490), (1160, 1190), (4610, 4720), (5200, 5275),
                            (6235, 6365), (7850, 7910), (7980, 8035)],
    "stm32u585xx.h": [(3850, 4120), (5340, 5540), (5650, 5780)],
    "stm32u5xx_ll_gpio.h": [(305, 325), (520, 540), (745, 765)],
    "stm32u5xx_ll_dac.h": [(300, 460)],
}
for name, ranges in selections.items():
    raw = (headers / name).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == expected[name]["sha256"], name
    lines = raw.decode("utf-8").splitlines()
    text = "\n\n".join("\n".join(f"{i+1}: {lines[i]}" for i in range(a-1, b))
                          for a, b in ranges) + "\n"
    excerpt = out / (name + ".excerpt.txt")
    excerpt.write_text(text, encoding="utf-8", newline="\n")
    manifest["headers"].append({"name": name, "reused_local": str((headers/name).relative_to(root)),
        "source_sha256": digest, "installed_source": expected[name]["source"], "ranges": ranges,
        "excerpt": excerpt.name, "excerpt_sha256": hashlib.sha256(excerpt.read_bytes()).hexdigest()})

receipt = root / "state/analysis/P2_adc_native_raw/installed_source_01.json"
records = json.loads(receipt.read_text())
selected = []
for record in records:
    if record["path"].endswith("devicetree_generated.h"):
        lines = [(n, line) for n, line in record["lines"]
                 if (line.startswith("#define DT_N_S_soc_S_adc_42028000_S_channel_a_")
                     or "adc1_in10_pa5" in line and len(line) < 300
                     or "digital_pin_gpios_IDX_15" in line
                     or "adc_pin_gpios_IDX_1" in line or "io_channels_IDX_1" in line)]
    elif record["path"].endswith(".overlay"):
        lines = [(n, line) for n, line in record["lines"] if 275 <= n <= 310 or 375 <= n <= 435]
    else:
        continue
    selected.append({"path": record["path"], "sha256": record["sha256"], "lines": lines})
binding = out / "installed_binding_excerpts.json"
binding.write_text(json.dumps({"reused_receipt": str(receipt.relative_to(root)),
    "receipt_sha256": hashlib.sha256(receipt.read_bytes()).hexdigest(), "records": selected}, indent=2)+"\n",
    encoding="utf-8")
manifest["binding_excerpt_sha256"] = hashlib.sha256(binding.read_bytes()).hexdigest()
manifest["reviewed_implementation"] = [{"path": name,
    "sha256": hashlib.sha256((root/name).read_bytes()).hexdigest()}
    for name in ("src/hal/power.cpp", "src/hal/power.h")]
manifest["official_overlay_refresh"] = json.loads((out/"unoq.receipt.json").read_text())
(out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"pages": len(pages), "headers": len(selections), "pdf_sha256": pdf_hash}))
