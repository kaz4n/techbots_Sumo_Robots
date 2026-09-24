"""Adapt existing exact artifact accounting to candidate2 without changing old receipts."""
from pathlib import Path

out = Path(__file__).resolve().parent
account = (out / 'account_candidate.py').read_text().replace("folder = out / 'app_attempt02'", "folder = out / 'app_candidate2'")
account = account.replace("for label, path in (\n", "for label, path in (\n    ('candidate1', out / 'app_attempt02/app.ino.elf'),\n")
(out / 'account_candidate2.py').write_text(account)
abi = (out / 'collect_candidate_abi.py').read_text()
abi = abi.replace("profiles = [('candidate1', out / 'app_attempt02/receipt/verified.json'),\n            ('D134_default', root / 'state/analysis/P5_native_compile_raw/app/receipt/verified.json')]",
                  "profiles = [('candidate2', out / 'app_candidate2/receipt/verified.json')]")
abi = abi.replace("'candidate1'", "'candidate2'")
abi = abi.replace("summary['existing_sizes_alignments_identical'] =", "summary['D134_default'] = json.loads((out / 'abi_comparison.json').read_text())['D134_default']\nsummary['existing_sizes_alignments_identical'] =")
abi = abi.replace("out / 'abi_comparison.json').write_text", "out / 'candidate2_abi_comparison.json').write_text")
(out / 'collect_candidate2_abi.py').write_text(abi)
finalize = (out / 'finalize_evidence.py').read_text()
for old, new in (
    ('build/p5_default_fit_candidate', 'build/p5_default_fit_candidate2'),
    ('materialized_manifest_attempt02.json', 'candidate2_materialized_manifest.json'),
    ('candidate_manifest.json', 'candidate2_manifest.json'),
    ('app_attempt02', 'app_candidate2'),
    ('abi_comparison.json', 'candidate2_abi_comparison.json'),
    ('actual_remote_commands_attempt02.jsonl', 'candidate2_actual_remote_commands.jsonl'),
    ("abi['candidate1']", "abi['candidate2']"),
    ('final_verification.json', 'candidate2_final_verification.json'),
    ("assert source == json.loads((out / 'app/source_manifest.json').read_text())", "assert source['source_sha256'] != json.loads((out / 'app/source_manifest.json').read_text())['source_sha256']"),
    ("'source_identical_after_fixture_repair': True", "'candidate2_source_distinct_and_bound': True"),
):
    finalize = finalize.replace(old, new)
(out / 'finalize_candidate2.py').write_text(finalize)
print('Prepared candidate2 account, ABI and final source-bound verification; no additional compile')
