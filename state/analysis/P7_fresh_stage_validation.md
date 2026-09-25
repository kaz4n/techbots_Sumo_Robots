# D170 fresh staging validation

Status: IMPLEMENTED / HOST-TESTED. No new target build or device action.
Implementation: 0160d1a6, tools/board_tool.py SHA25673f14c294903d58fb8540739197aa98d2d400fc0fbdd10723bb10047b1eb35ce.
Final independent test: 7b3efe5882c46a4cd8343a050b8a338a24019a195b705a9658c44aecb4ec075d.
Contract: analysis/P7_fresh_stage_contract.md (539cf1c6).

The explicit keyword-only attempt claims a new checked directory and preserves
existing staging, including partial failures. Legacy callers and the shared
Arduino copy/layout/config checks keep their behavior. No CLI, firmware, pin,
flag, locked-test or native child-execution changes are included.

Commands and full outputs are in P7_motor_fault_raw/fresh_stage_*.json:
- `python -B -m unittest tests.tooling.test_fresh_stage -v`, with isolated empty
  cache prefixes: WSL Python3.12 has25 PASS/1 Windows-only skip; Windows
  Python3.13.11 has17 PASS/9 missing-symlink-privilege skips. All26 methods pass
  on an applicable platform; actual Windows junction refusal passes.
- WSL Python3.12, TMPDIR=/dev/shm: five unchanged suites test_tools,
  test_app_transaction, test_ui_adc_probe_policy, test_mode_availability and
  test_compile_executor:91/91 PASS,129.369s,exit0. The UBSan app owner builds
  each pass28 cases (617259/617260 assertions); probe builds each pass2 cases
  and9 assertions. These use host substitutes, not Arduino hardware.
- All9 repaired source/test pins remain exact. Postcheck confirms all104
  retained D168 staged files/764049B preserve content and mtime, aggregate
  df0fb658fa6b617e557837e78e244a44f29267daa721148b1ebd6fae405ffb03.
  Original PROGRESS prefix is unchanged; zero Windows/RAM fixture remnants.

The first Windows run had one fixture failure: copyfile injection missed
Python3.13's CopyFile2 path. Original tests/receipts are preserved0160d1a6;
failure analysis explains the independent fixture-only correction. Every
assertion remains; production never changed after that first execution.
The unexecuted layout draft is preserved2a586e22. No failed test was hidden.

Separate fresh-context same-model reviewer: reviews/P7_fresh_stage_review.md,
SHA2568233de35d6046d97a4c09f518df712a9146fe8eefc2ea70da614a40c13a8cb34,
PASS/no open findings. Reviewer inspected root-run evidence and did not run tests.

Storage: all fixture binaries/sources released;20 required command/staging
receipts244837B retained, indexed in fresh_stage_postcheck.json. Incremental Git
packing recovered11,196,416 reported bytes with refs/reflogs/history preserved;
see STORAGE_LOG.md and storage_repack_20260925_d170.json. Denied targets untouched.

Next: extend the existing bounded diagnostic compile caller with one separately
owned active profile using this explicit API, preserving consumed compile01/02
and their manifests. Freeze/test/review the minimal mapping before a fresh
identified target compile. Active diagnostic execution and physical gates remain
pending; no hostile concurrent-filesystem guarantee is claimed by D170.
