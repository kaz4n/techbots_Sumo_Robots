# D177 host action integration validation

2026-09-25T11:08:31.211321+04:00. IMPLEMENTED / HOST-TESTED / REVIEWED. Board disconnected; native calls: 0.

The thin `P7_motor_fault_raw/inert_actions.py` composes source-pinned commands,
admits bounded upload/capture reports and sequences capture only after checked
upload success. It reuses D175/D176 APIs; it does not own a native run or change
firmware, pins, motor permissions, locked tests or human gates.

- Final source: `58d32dda`, SHA256 `8ffb65c0f1284f261ae1237bcf260e866176e83433a3538908780962513f1104`.
- Original independent oracle: `6c9c264b`, SHA256 `bfffda215aaa04e45ec6b653f048ac9f6ca2c8dd95f2c83c9bb84e16b6d0492f`.
- Additive codec oracle: `9f49252c`, SHA256 `4a907281df3a6b4573c448a1ecd106804efde616aeb14a1ee1e25bde7d73c727`.
- First tested-source repair: unchanged original **46/46 PASS** in0.320s,
  independent additional **16/16 PASS** in0.337s. WSL Python3.12.3, Python-B;
  all11 frozen source/oracle/input/dependency pins unchanged. No persistent fixtures.
- Production composition with Windows Python3.13.11: upload **28,989 UTF16 units**
  (canonical Base85 fallback), capture **25,231** (original Base64), both within
  the unchanged30,000 limit. Source bytes/digests and shell roundtrips checked.
- Separate fresh-context same-model reviewer, reused for repairs: PASS,
  no open findings. Reviewer inspected actual source/receipts; did not run tests.
  `state/reviews/P7_motor_fault_actions_review.md`, commit `b1de6217`, SHA256
  `c40c9436ea0df0aaf327e435b165a6197dfb10043db51956f267d72eacf7bee3`.

Original evidence is retained: source9917fbf1 needed bracket-digest consistency;
first frozen sourcee9481f5c gave45PASS/1FAIL when bytecode writes were re-enabled
at runtime; full production upload composition exceeded the command limit.
Receipts838fa1f1 remain. The first tested-source repair checks startup and current
bytecode suppression, and uses compact encoding only when necessary. Original
46 assertions were not changed; no limit was raised or failure hidden.

Evidence index (all under `P7_motor_fault_raw/`): `action_preparation.json` plus
`action_preparation_check.json` bind historical observations; `action_freeze.json`,
`action_first.json`, `action_composition_first.json` preserve original results;
`action_repair1_freeze.json`, `action_repair1.json`, and
`action_composition_repair1.json` preserve revised inputs and actual checks.
Twenty committed raw observation/action blobs byte-match current files; the
140971-byte historical PROGRESS prefix remains unchanged. All39 module/bootstrap
functions are below60 lines (maximum33); in-memory syntax checks passed.

Limitations and next step: this is host preparation, not a board run. Before a
fresh identified inert scope, verify current board identity/artifacts/prerequisites
and target bz2/Base85 support, then review the minimal native caller using existing
CompileOnce transport, the checked APIs and D177 sequencing. Do not rerun consumed
native scopes or use historical boot/tool observations as current admission.
Retrieve and retain actual raw snapshots before offline D174 decoding; COHERENCE
remains UNPROVEN. Native startup/RAM/WCET, physical tests and human gates remain
pending. No board connection or extra hardware is requested in this checkpoint.

Storage: retained compact action JSON receipts total34,249B before closure, plus
source/oracles/review needed for reproduction. No compiler tree, target binary,
download, source clone or new Python cache. Existing policy-denied targets remain
untouched. C: observed2527780864B free; this fluctuates independently of cleanup.
