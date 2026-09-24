# P2 D118 standalone default-app guard review

2026-09-24, separate reviewer. **PASS_SOFTWARE_GUARD_REVIEW**. No open BLOCKER,
MAJOR or MINOR finding in the reviewed guard scope. This is not the combined
source/target/capture/run approval and does not authorize a live upload.

## Reviewed identity and context

Read AGENTS.md in full, current PROGRESS/checkpoints, the D118 adoption, the full
run contract, exact-app bare eligibility, relevant shared build functions, and
the frozen new tests. The local date was Thursday 24 September, the PLAN section
3 sensor-bench/P1-P2 development day; no human gate was inferred from the date.

| Input | SHA256 |
|---|---|
| `tools/app_default_run.py` | `7fbeceb269912321b3b06c2b9ea9cace466c2faf4f06bebf6ec1d4ebf4d5da58` |
| `tests/tooling/test_app_default_run.py` | `6a4dcde69c82736acea513d1c6ef2b503e6b5d9548ceacbd0622e33e534f058a` |
| `state/analysis/P2_app_default_run_contract.md` | `7b364da5fb496d24f0c5be4c58bcd0d19cd65cf31b0720d56c25385fd825cd61` |
| `tools/p0_inert_sources.json` | `a1587931afa5f817bf8b93054f384918dc8cd36d4fb71c8f7b083d76e6128802` |

The reviewed route is solely `app-default-e820c0e1-run01`, target `2629958581`,
explicit ADB, default startup, MATCH0/MOTORS_ALLOWED0, source e820c0e1, ELF8379f152
and ZSKc60443cd. The app includes actual inhibited native EN LOW/PWM zero/timer
setup. Optional grants remain false. The human-reported bare-board premise does
not prove wiring, voltages, motor permission, actual loading or physical safety.
The last MCU image remains the separately consumed D114 run per current state;
this reviewer performed no board operation.

## Source assessment

- `tools/app_default_run.py:73` and `:389` constrain request fields before board
  lookup. `:211` validates explicit environment, exact bounded schemas, original
  record/review bytes, every reviewed tool pin, the exact 91-file source digest,
  current local HEAD and absence of an earlier claim/outcome. Existing and
  dangling links are rejected; relevant file ancestry is checked.
- `:321`, `:334` and `:349` use the unchanged single stage/core/sync/checked
  compile sequence. The returned checked artifact directory is retained and
  strictly limited to the selected source/mode/root plus a lowercase UUID.
  Profiles, extra staged files, special entries and source changes refuse.
- `:292` independently checks current scope, exact artifact path and ELF/ZSK
  hashes, then current staged/local source and scope again. The claim contains
  the bound identities and exact upload argv. `:264` exclusively creates,
  flushes, fsyncs and closes that claim before any upload invocation.
- `:272` makes exactly one unchanged `board.remote` upload call with capture and
  timeout120. Actual nonzero status, launch failure, timeout output and error
  state are retained; evidence-write failure propagates. Partial claims and
  outcomes do not permit replay. No reset, capture, recovery or retry is added.
- `:145` and `:349` retain local Git command/status/output/timing in the exclusive
  orchestration receipt, including preparation failures. Source/artifact and
  checked-receipt identities remain in that receipt. No successful command is
  relabeled as loaded, running, completed, RAM-qualified or gate-passed.

Read-only Git diff checks found no modifications to existing firmware/config,
locked tests, existing tracked tests, board/build policies, shared P0 capture/
heap helpers or the manifest. The nine-key manifest test passes with its exact
prior bytes and no app key. Generic app upload remains rejected in unchanged
`tools/board_tool.py:318`. The coordinator owns the broader old-regression run;
this review does not claim to have repeated it.

## Independent execution evidence

All execution was local WSL Python3.12.3 with TMPDIR=/dev/shm. Board and Git calls
were controlled test substitutes; unhandled subprocess/network operations were
denied. No ADB, network, MCU read/write, real compile or real upload was used.

1. Frozen public oracle: **22/22 PASS**, zero failures/errors/skips. Command:
   `TMPDIR=/dev/shm python3 state/analysis/P2_app_default_probe_raw/guard_author/run_tests.py privateGuard1`.
   Evidence: `state/analysis/P2_app_default_probe_raw/guard_author/privateGuard1/receipt.json`
   and sibling `unittest.txt`. Exact source and oracle hashes are in the receipt.
2. Independent reviewer probes: **6/6 PASS**, zero failures/errors/skips. Command:
   `TMPDIR=/dev/shm python3 state/analysis/P2_app_default_probe_raw/guard_reviewer/private_probes.py run1`.
   Evidence: `state/analysis/P2_app_default_probe_raw/guard_reviewer/run1/receipt.json`
   and sibling `unittest.txt`; probe source hash
   `6ac0a79724cbcf950d97fa73fd3c9b887c6613c573bf962fa39a68049e4b0d2c`.
   Reused only public fixture scaffolding; reviewer-authored assertions cover
   KeyboardInterrupt at four preparation stages, staged content/addition during
   remote hash validation, self-consistent review/approval/run replacement,
   outcome-specific fsync failure and consumed replay, original nonzero Git
   status/output retention, root symlink and staged FIFO refusal.

## Limitations and handoff

The contract deliberately uses a non-hostile workspace control, not a filesystem
lock or signature against concurrent malicious changes. Existing checked build,
sync and inventory operations have no uniform end-to-end deadline. The120s upload
timeout bounds caller observation and does not establish remote cancellation;
unknown consumed attempts remain consumed. These declared limits were preserved.

Changed only this review and reviewer probe/evidence files; the authorized unique
public-suite result folder was added by the existing harness. No implementation,
public/old/locked test, helper, contract, firmware, grant or manifest edit occurred.

Next: coordinator completes the separate collector and exact source/target/run
review, preserves old-regression evidence, commits reviewed software, and binds
actual current-HEAD live records only when all required review conditions hold.
This software review supplies no live records, motor-run permission, physical
acceptance or human phase gate.
