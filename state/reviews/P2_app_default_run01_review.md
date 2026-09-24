# D118 exact default-app run01 review

Verdict: **PASS_EXACT_DEFAULT_APP_SOURCE_TARGET_CAPTURE_GUARD**.
2026-09-24. No open BLOCKER, MAJOR or MINOR finding for the exact prospective
scope below. This is continued review by the separate same-model guard reviewer;
it is neither a cross-model review nor a human phase gate.

The scope is one fresh checked default/MATCH0/MOTORS_ALLOWED0 app upload for
`app-default-e820c0e1-run01` to serial `2629958581` through explicit ADB, followed
only after successful upload command and outcome by one passive capture. The
human-reported setup is a bare UNO Q. Existing native EN LOW, zero PWM, device/
pad/timer setup and repeated inhibited ticks are explicitly included. Every
optional SetupGrant remains false. No motor connection/energization permission,
STAND/RING, PINMAP, electrical or physical acceptance follows.

| Binding | Exact value |
|---|---|
| Current software commit | `9b4afcb22823ce48cb20cb4cb951cd55229ac1f2` |
| Source, exact91 files | `e820c0e16c29cfd289889273f02721a995e5336b14397f64d6093cffd42b8b69` |
| ELF,176048 bytes | `8379f152554649fd1b96165f29fda1f165c2b5cfc51d8dca430a37e19f693257` |
| ZSK,176048 bytes | `c60443cd8d90c26a85591153dfa38d5f9233bd686b413b2ab7daa3e1457f6df5` |
| Upload guard | `7fbeceb269912321b3b06c2b9ea9cace466c2faf4f06bebf6ec1d4ebf4d5da58` |
| Collector | `beeffff315b2e28a95a20dc1e26477fc924b2da26d1fdd8a8b36fb013ca110e1` |
| Coordinator, `raw/execute_run01.py` | `05648dbe42db6ab0ac21006978379644be52f6d71c3627ebd8d82075c4854e7f` |

Here `raw/` means `state/analysis/P2_app_default_probe_raw/`. The exact twelve
tool/contract hashes, rehashed91-source aggregate, target artifact bytes, current
local Git output, protected-tree diff and staging/review hashes are retained in
`raw/guard_reviewer/runScope3/receipt.json`. The prospective request is
`raw/run01_review_request.json`; the coordinator remains unexecuted at review.

The guard retains the reviewed current-HEAD/source/tool/run/approval/review
checks, exact fresh checked build return, ELF/ZSK verification, exclusive fsynced
attempt before one120s upload and retained outcome. The nine-key manifest remains
byte-identical and has no app entry; generic app upload remains refused. Guard
source review and independent22+private6 results are in
`P2_app_default_guard_review.md`; collector source and independent/private68
results are in `P2_app_default_capture_review.md`. The latter review is relied on
as the separate collector assessment, supplemented here by inspecting its actual
identity checks, finite read phase machine and subprocess/config command surface.

Saved Linux staging receipts show the exact two176048-byte input files and four
collector/helper/config files copied into exclusive fixed directories, all
commands exit0 and final hashes matching current local bytes. These receipts
prove their recorded file preparation, not present MCU state. The coordinator
rehashes the four deployed tools immediately before executing the pinned
collector; the collector rechecks its exact input/tool/loader identities before
commands. Its two full flash sweeps bracket bounded heap/node/live-prefix reads:
at most62 reads,66 commands and1405088 bytes, with600s lifetime and30s child bounds.
The pinned MEM-AP configuration uses no reset, Cortex halt, flash writer or debug
server. No UART/sensor grant or recovery command is introduced.

Coordinator ordering was checked statically and with five isolated host probes:
success, guard failure, capture nonzero, capture timeout and capture launch
failure. All pass; each admitted case launches one guard, guard failure launches
zero captures, all other cases launch at most one capture, and every replay
refuses on exclusive execution intent. Capture intent is flushed/fsynced before
launch; timeout/launch partial text and unknown status are retained. The script
adds no readiness sleep, retry, reset or restoration. Host-substituted probes
never used ADB, network, MCU, real build, upload or collector execution.

Original reviewer `runScope1` WSL Git-diff timeout and `runScope2` Windows default
text-decoder assertion are preserved. The only harness correction specifies
UTF-8 when reading the coordinator's already UTF-8 timeout text, preserving the
same expected `partial\ufffd` value. The initial harness remains
`raw/guard_reviewer/run_scope_probe_initial.py`; corrected Windows `runScope3`
passes. No product or established test was changed.

This verdict is prospective and applies only with final live run/approval JSON
binding these bytes, this review hash and the unchanged current commit. Those
records were not created by this reviewer and require final read-only admission.
Do not commit or change reviewed inputs between admission and launch. Failed or
uncertain upload/capture is consumed; timeout does not prove remote cancellation.
After capture the app remains loaded and may continue inhibited native ticks.
No terminal firmware success, actual transient RAM margin, coherent snapshot,
stack headroom, full WCET, powered behavior or human gate is asserted.
