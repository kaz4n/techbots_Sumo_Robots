# SumoX-26 continuation handoff

Updated **27 September 2026, 14:26 Dubai**. For any engineer or coding agent
taking over. The objective remains a working, qualified competition robot;
the project is **not physically accepted or release-ready**.

## Start here

1. Read [AGENTS.md](AGENTS.md) fully, then this handoff.
2. Inspect `git status --short`, `git log -5 --oneline`, today's date and disk
   space. Preserve other people's changes. Start from current `main`, not an old
   temporary worktree or historical diagnostic branch.
3. Read the latest [PROGRESS](state/PROGRESS.md), [DECISIONS](state/DECISIONS.md),
   [FACTS](state/FACTS.md) and [TUNING_LOG](state/TUNING_LOG.md) entries.
   PROGRESS contains legacy non-UTF8 bytes; append without re-encoding history.
4. Select work using the [full requirement audit](state/analysis/P7_full_requirement_audit_20260927.md)
   and check [PLAN section 3](docs/PLAN.md#3-schedule-and-gates) against today's date.

The formal phase registry remains **P0; no human gates passed**. Software
preparation has advanced through P7 under recorded decisions, including
D051/D075/D122/D137. This does not pass the physical phases or require restarting
completed software. The overall goal was marked **blocked** after three
consecutive checks found missing hardware/acceptance prerequisites.

## Repository and code checkpoint

All unique code and accepted evidence were committed on `main` before this
handoff began. Starting HEAD was
`fbd39d9ea8c4ed4841c8c28a24d60ba26cd380d6`; this handoff is a later documentation
commit. Use `git log -1` for the latest commit. No remote publication is part of
this handoff.

| Checkpoint | Commit | Meaning |
|---|---|---|
| B7 implementation | `1ba538e1` | Default-disabled brownout sequence and application integration |
| Frozen native build input | `97e32fde` | Exact input to all three latest compile-only operations |
| B7 deployment source | `98b13db0` | Separate guarded deployment route and independent oracle |
| B7 deployment acceptance | `cfe7412d` | Linux/Windows checks and independent review accepted |
| Latest engineering closure | `10758c28` | Three native builds, reviews and acceptance summaries committed |
| Blocked goal checkpoint | `fbd39d9e` | Missing physical evidence recorded; no firmware change |

All 143 inputs pinned by the accepted B7 native manifest still match current
files. Common application source SHA256:
`85b320de79f0fe26602bd6b714d77136718f4a6ab32ba989ea8322b7b92a481a`.
No firmware change or build rerun was needed for this handoff.

The handoff audit checked 19 registered worktrees. Apparently branch-only code
was already integrated on main, with patch or touched-file equivalence checked.
All 4,600 untracked, nonignored historical worktree files were duplicates:
4,181 matched tracked main files byte-for-byte; 419 matched members of the
retained first-failure receipt archives. No source merge or force-add was needed.
Historical worktrees remain preserved; use main as the continuation branch.

Main code locations:

- `src/core/`: pure C++17 behavior, countdown, edge response, perception,
  Governor, openers, state machine and recorder encoding.
- `src/hal/`: UNO Q interfaces, including the sole MotorGate output path.
- `src/app/`: runtime, source qualification, scheduling and services.
- `src/config.h`: tunables, profiles and explicit setup declarations.
- `bench/`, `tools/`, `host/`, `tests/`: commissioning and host validation.
  Locked safety tests require explicit approval to change.
- `state/analysis/`, `state/reviews/`: contracts, original results, failures and
  independent reviews. These are retained evidence, not disposable builds.

## What is verified

| Work | Verified result | Evidence |
|---|---|---|
| D239 inhibited recorder | One complete synthetic board recording: 607,508 wire bytes, 5,001 frames, 8 events, expected session/CRC, SEALED, no reported loss | [Actual delivery](state/analysis/P7_recorder_repeat_delivery_actual_validation.md) |
| D240/D241 release tools | Guarded application delivery, static/Immediate compilation, deployment and paired recording preparation | [Application delivery](state/analysis/P7_app_identified_delivery_validation.md), [production tools](state/analysis/P7_match_static_validation.md) |
| D243 timing preparation | 16 cases/143 assertions; timing and production compiles plus offline ARM retention/exclusion checks | [Timing validation](state/analysis/P7_outer_loop_timing_actual_validation.md) |
| D244 B7 behavior | Four host selections: 98 case executions/821,764 assertions; ordinary safety/Governor regression: 410 executions/18,361,362 assertions | [Host validation](state/analysis/P2_b7_brownout_validation.md) |
| D244 current target builds | B7 M0, B7 M1 and ordinary MATCH M1 passed; nine closing checks each | [Native validation](state/analysis/P2_b7_brownout_actual_validation.md), [review](state/reviews/P2_b7_brownout_actual_review.md) |
| D245 B7 deployment preparation | 12 tests on Linux and 12 on Windows; independent review; no real B7 deployment | [Deployment validation](state/analysis/P2_b7_deploy_validation.md) |

M0 means motors disabled at compilation; M1 means motor support compiled in.
B7 packages are 84,284 B (M0) and 84,656 B (M1). The ordinary MATCH package is
92,092 B, SHA256
`7895a4d8991bd2158e63c69cb37ebcdc4f39632311a1dbf47401c3a34f664c86`.
Its package and final ELF are byte-identical to D241/D243. These three builds
were compile-only: no upload, reset or motor operation followed.

Build RAM figures are linker accounting, not measured live RAM, stack usage or
worst-case execution time. Earlier host fixture and native failures remain saved;
only the identified passing scopes are accepted.

## Board and operating limits

Latest human hardware report: **UNO Q only**. Last verified upload:
**D239 M0 synthetic recorder diagnostic**, not production MATCH or B7.
Recorded source `3d9306d7`, package `3a1bbd2f`, session `3840709944287840472`.
No board was contacted for this handoff. Re-establish current identity and
firmware before a new native operation.

All 17 `APP_GRANT_*` declarations remain zero; IMU axes remain unconfigured.
Compiled M1 artifacts do not establish an operationally qualified robot. Do not
turn grants on simply to satisfy a tool or test.

D244 approves B7's **bench-only** exception to centered-contact full duty while
retaining countdown, Governor slew/reversal braking, MotorGate and stop/edge
guards. Actual B7 needs qualified setup, a half-charged pack, **fresh run-specific
STAND OK**, twenty real forward/reverse cycles and independent continuous
no-reset evidence. D245 rejects RING OK for this route. Other motor-capable
operations still need their own specific STAND/RING authorization.

All cited operations are closed. No build, upload or diagnostic process is
handed off in progress. Historical process IDs and consumed run directories are
evidence, not instructions to resume or repeat an operation.

## Next substantive work

1. Obtain actual assembly/wiring facts and PINMAP acceptance. Qualify sensors,
   ADC/button windows, IMU mounting, power, motor directions and interface limits
   using [HARDWARE](docs/HARDWARE.md) and the P0/P2 bench requirements.
2. Record physical facts and approved configuration changes; complete required
   human gates. Create a fresh qualified source/build/run scope with the existing
   guarded tools. Preserve each original failure and result.
3. With specific run authority, execute outstanding P2 bench and timing/RAM
   measurements, then P3-P5 countdown, stopping, edge, search and opponent trials.
4. Complete qualified release configuration/deployment, human explanation,
   organizer answers, printing, packing and physical rehearsal. The
   [runbook](docs/RUNBOOK.md) and [mode card](docs/MODE_CARD.md) are prepared;
   their existence does not prove their physical checks passed.

The latest bounded scope audit found no additional currently authorized software
preparation. Repeating accepted builds or synthetic captures does not satisfy
the missing physical requirements.

Schedule: if actual P3 has not passed by the **end of 28 September**, retain
reactive behavior, SIDESTEP, DIRECT and recorder; drop ARC, WAIT and P6 polish.
P6 also needs actual P4 by **30 September**. Code freeze is **1 October,
21:00 Dubai**, rehearsal **2 October**, competition **3 October 2026**.
Apply date rules when due; no scheduled date creates a passed gate.

## Commands and reproduction

Host prerequisites are Ubuntu WSL (or Linux), CMake, g++, Python and Bash.
Windows ADB workflows use native Windows Python and the installed ADB tool;
the local CLI/tool binaries are not vendored in Git. Configure the transport
from verified facts: `SUMO_TRANSPORT`, `SUMO_ADB_SERIAL`, optional
`SUMO_ADB_EXECUTABLE`, and the build's `SUMO_REMOTE_ROOT`. SSH additionally needs
`SUMO_SSH_TARGET` and verified host keys. Follow the tool-specific environment
instructions; keep credentials outside the repository.

Read [tools/README.md](tools/README.md) and the relevant contract before native
work. A fresh operation needs an unused attempt name, reviewed clean HEAD,
current board/tool identity and valid source/artifact binding. Never reuse a
consumed owner or relabel an old scope as new evidence.

For necessary host regression after a code change, these PowerShell commands
use Ubuntu WSL and one compiler. Run each only if its predecessor passes:

```powershell
wsl -d Ubuntu -- cmake -S host -B build/host -DCMAKE_BUILD_TYPE=Debug
wsl -d Ubuntu -- cmake --build build/host --parallel 1
wsl -d Ubuntu -- ctest --test-dir build/host --output-on-failure
```

The legacy `tools/test_host.sh` helper uses two jobs; prefer the serial commands
while memory is constrained. Focused B7 commands and raw receipts are in its host
validation. Do not overwrite existing receipt directories.

| Purpose | Tool / contract |
|---|---|
| B7 compile-only, M0 or M1 | `tools/compile_b7_app.py` / [D244 build](state/analysis/P2_b7_build_contract.md) |
| Qualified B7 deployment | `tools/deploy_b7_app.py` / [D245 deployment](state/analysis/P2_b7_deploy_contract.md) |
| Static/Immediate MATCH compile/deploy | `tools/compile_match_static.py`, `tools/deploy_match_static.py` / [D241](state/analysis/P7_match_static_contract.md) |
| Qualified MATCH upload and recording | `tools/run_match_identified_delivery.py` / D241 and [identified delivery](state/analysis/P7_app_identified_delivery_contract.md) |

Start with documented `--check-only` mode. Compilation and deployment are
separate actions; these entries do not grant run authorization. Generic legacy
MATCH flashing does not replace qualification.

## Storage and historical records

C: had approximately 6.28 GB free during preparation; recheck before heavy work.
Preserve checked target artifacts, original evidence, unique failures, source,
credentials and Git history. Build outputs, Python caches, the local CLI binary
and credentials are intentionally ignored; do not force-add them.

Historical sparse worktrees and staging copies remain in local Temp. Read
[STORAGE_LOG](state/STORAGE_LOG.md) before touching them. Automatic approval
previously blocked several deletions, including the three latest B7/production
stages totaling 2,399,358 B. They remain in place; do not retry through another
method or prune worktrees containing denied paths. Exact latest inventory:
[cleanup receipt](state/analysis/P2_b7_build_raw/stage_cleanup_blocked01.json).

[CODEX_HANDOFF](state/CODEX_HANDOFF.md) and
[CODEX_EXECUTION](state/CODEX_EXECUTION.md) retain historical checkpoints.
Their older active-process and next-diagnostic paragraphs are superseded by this
snapshot and later dated entries; they are not a second task queue.

## Handoff verification

The documentation update passed an independent read-only review. All 69 local
link targets checked in the updated documents exist; all 143 frozen native
input hashes still match. The hand-authored diff passes whitespace checks.
The worktree audit above found no missing source integration. No firmware tests,
builds, board actions or cleanup were repeated for this documentation-only task.
