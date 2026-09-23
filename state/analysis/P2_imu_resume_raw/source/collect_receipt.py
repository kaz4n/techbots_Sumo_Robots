"""Recheck retained source identity for the resumable IMU audit.

This reads local evidence only and writes receipt.json beside this script.
Assertions verify exact PDFs/header and explicitly LF-normalized page extracts.
"""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent


def record(path):
    blob = (ROOT / path).read_bytes()
    return {
        "path": path,
        "bytes": len(blob),
        "sha256": hashlib.sha256(blob).hexdigest(),
    }


rm = record("build/cache/RM0456_Rev6_52152e41.pdf")
assert rm["sha256"] == "52152e414e2ac329cfd9038481b97e8ff70592f9892d171dcb63b7d283722616"
ll = record("state/analysis/P2_i2c_native_raw/stm32u5xx_ll_i2c.h")
installed = json.loads((ROOT / "state/analysis/P2_i2c_native_raw/installed_02.json").read_text())
capture = next(x for x in installed["records"] if x.get("path", "").endswith("stm32u5xx_ll_i2c.h"))
assert ll["sha256"] == capture["sha256"] and ll["bytes"] == capture["bytes"]
assert hashlib.sha256(capture["text"].encode()).hexdigest() == ll["sha256"]
ll["installed_path"] = capture["path"]
ll["capture"] = "P2_i2c_native_raw/installed_02.json; reused offline, no fresh board read"
ll["locators"] = ["1724-1804 ISR predicates", "1946-1948 STOPCF", "2305-2320 CR2 update", "2397-2411 RXDR/TXDR"]
manifest = json.loads((ROOT / "state/analysis/P2_i2c_native_raw/manual_pages.json").read_text())
expected = {x["page"]: x["text_sha256"] for x in manifest["pages"]}
pages = []
for page in [2697, 2698, 2699, 2700, 2712, 2713, 2714, 2717, 2718, 2721, 2740, 2741, 2743, 2744, 2745, 2746, 2747, 2748, 2749, 2750, 2751, 2752]:
    item = record(f"state/analysis/P2_i2c_native_raw/RM0456_p{page}.txt")
    blob = (ROOT / item["path"]).read_bytes()
    item["LF_sha256"] = hashlib.sha256(blob.replace(b"\r\n", b"\n")).hexdigest()
    assert item["LF_sha256"] == expected[page]
    item["page"] = page
    item["matches_prior_text_manifest_after_CRLF_to_LF"] = True
    pages.append(item)
mpu = record("state/analysis/P2_mpu6050_sample_raw/RM_MPU6000A_Rev4_0.pdf")
assert mpu["sha256"] == "ccaa6312b9d86a9da79e26e511101e1150dc85a48255600010a854369cf7c05d"
receipt = {
    "date": "2026-09-23 Asia/Dubai",
    "baseline": "2f0981cbe570b3bc6d041072455efe81ebb5bff5",
    "scope": "offline primary and retained installed-source audit; no board, config, implementation, test or ledger writes",
    "verification_note": "Initial strict raw-page-hash check failed because retained text files use CRLF. Original receipt hashes match LF-normalized bytes. Both identities are retained; existing source files were not rewritten.",
    "RM0456": {
        "pdf": rm,
        "source_url": "https://www.stmcu.jp/wp/wp-content/uploads/2021/07/RM0456_Rev6.pdf",
        "fresh_web_open": "2026-09-23 failed: web reader Internal Error / URL not accessible; cached Rev6 retained",
        "page_texts": pages,
        "visually_inspected_figures": [{"page": 2699, "figure": 783}, {"page": 2717, "figure": 798}, {"page": 2721, "figure": 801}],
    },
    "LL": ll,
    "ES0499": {
        "url": "https://www.st.com/resource/en/errata_sheet/es0499-stm32u575xx-and-stm32u585xx-device-errata-stmicroelectronics.pdf",
        "fresh_web_open": "2026-09-23 success; ES0499 Rev12 June2026; 51pages",
        "inspected": "sections2.20.1-2.20.3; printedpages32-33; readerlines1350-1394",
        "local_pdf_hash": None,
        "source_assertions": ["Kernel frequency must accommodate transmitter setup time; standard Fast-mode100ns minimum requires at least10MHz.", "Controller BERR can be spurious without ending transfer.", "SMBus target-timeout limitation is outside selected mode.", "No service-gap bound or application WCET follows from these sections."],
    },
    "MPU": {
        "pdf": mpu,
        "source_url": "https://cdn.sparkfun.com/datasheets/Sensors/Accelerometers/RM-MPU-6000A.pdf",
        "revision": "RM-MPU-6000A-00 Rev4.0; prior retrieval reused; no fullRev4.2 claim",
        "page_texts": [record(f"state/analysis/P2_mpu6050_sample_raw/RM_Rev4_0_p{p}.txt") for p in [27, 28, 29, 30, 31, 32]],
    },
    "implementation_and_contracts": [record(p) for p in ["src/hal/imu_bus_unoq.cpp", "state/analysis/P2_imu_bus_contract.md", "state/analysis/P2_imu_acquisition_contract.md", "state/analysis/P2_app_schedule_dependencies.md"]],
    "created_figures": [record(p.relative_to(ROOT).as_posix()) for p in sorted(OUT.glob("RM0456_*.png"))],
}
(OUT / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"RM_pdf": "PASS", "RM_LF_page_hashes": len(pages), "LL_exact_installed_match": "PASS", "MPU_pdf": "PASS", "figures": len(receipt["created_figures"])}))
