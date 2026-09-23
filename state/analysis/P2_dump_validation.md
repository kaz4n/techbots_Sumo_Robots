# D090 bounded IDLE dump validation

2026-09-23 Asia/Dubai. Active P2 software under D051/D075; no human phase gate.
Implementation extends the actual B13/B15 recorder to a bounded IDLE-only owner,
native transmit-only internal UART port and receive-only CSV capture tool.

## Scope and sources

Read AGENTS, active P2, B13/B15, persistent state and D070/D073-D075/D089. Exact
contract is P2_dump_contract.md; native contract, lifecycle audit and native source
audit are adjacent. Installed core1.0.0, RouterBridge0.4.3, RPClite0.3.1 and pinned
Zephyr1743741760ee/native/router artifacts are preserved with path/hash receipts.
Linux router0.10.0 version agrees with source tag; binary reproducibility unproved.

Source audit rejected stock Bridge/Monitor/Serial runtime calls because they use
blocking locks, retry loops and dynamic strings. The replacement emits exact
MessagePack mon/write notifications with <=64 payload bytes and <=8 nonwaiting
UART stores per call, checks ready/ownership/80us call/100ms packet bounds, and
acknowledges only after physical UART TC. No Linux delivery acknowledgement is
invented. Reset/cancellation permanently poisons the native instance; UE/TE off
and disabled readback cannot restore the Linux decoder or recall shifted bytes.
The earlier narrative packet arithmetic was corrected to15+64=79bytes; raw
protocol bytes were already correct. FIFO-only TXFRQ is not used.

Transfer binds a retained recorder epoch/summary and current inhibited IDLE Robot
result. It validates identity, freshness, lifecycle and source before bounded
formatting/transmission. STOPPED cannot dump. The real software reset API can
preserve evidence, but no new local reset UI or remote reset command is provided.
Receiver validates order/session/counts/raw CSV/CRC, preserves reported losses,
and atomically publishes a unique directory only after existing bundle validation.
Failures retain partial evidence. Origin and optional identity remain declarations.

## Actual validation

- Independent test author read public contracts/headers and pinned native headers,
  not new implementation bodies.26owner cases/4052assertions pass, including real
  Robot -> MotorGate -> AttemptRecorder -> Transfer and synthetic C++ wire output.
- Full normal:1281main cases/24481257assertions plus65enabledMotorGate cases/
  3847552assertions,2/2PASS6.07s. Full ASan/UBSan same counts pass; exact runtime in
  P2_dump_raw/sanitizer.txt (24.83s). No existing or locked tests changed.
-33receiver methods pass, including actual C++ roundtrip,5001frames/4096events,
  fragments/truncation/CRC/session/path rejection, atomic no-overwrite, failed
  remoteEND, rawCR preservation and exact transport outcomes; includes18original
  strict config checks with additive expected D088-D090 constants.
-11native methods/154normal+sanitizer scenario processes/4870assertions pass:
  exact79-byte packets, grants, API failures, context/ownership/clock/registers,
  TXE/TC,80us and100ms boundaries, wrap, cancellation and permanent poison.
- Actual UNO Q Linux compilation (no upload) passed for final source
  `b8bb9366458c2472d856e81ea4678716ff16d00a3b3d16b51d008e1624818307`:
  315332program bytes/238596compiler global RAM bytes; compiler reports23548
  remaining and low-memory warning.72source files match current physical bytes;
  three ELF artifacts,40native imports and42AEABI imports have captured evidence.
  This is not measured free RAM or successful dynamic loading.

Receipts: P2_dump_raw/{host_with_enabled,sanitizer,target_compile_final,
target_audit_final}.{json,txt}, target_b8bb9366_bench-default.json, source_exact.json,
host_last_test.txt, host-sanitize_last_test.txt and author/HANDOFF.md. Preserve
initial author fixture/contract-clarification failures. Root's first existing
tooling invocation used an invalid module name/import path; tooling_existing
records that invocation error, not a production/test failure.

Fresh separate same-model reviewer (not cross-model) owns
state/reviews/P2_dump_review.md and its raw receipts. At this writing final ELF/
source approval was subsequently issued in source_approval.json; the reviewer independently reproduced owner normal/
sanitizer and44tooling methods, and verified corrected MINOR receiver/path/wire
findings. Final review disposition and remaining tooling receipts follow below.

Supplemental link_bodies.json captures actual main/serial-buffer constructor
instructions and nonnull fmod/sqrt exports. The first supplemental artifact name
collided with the recorder receipt name and was overwritten; its command receipt
remains, and the distinct final artifact was recollected. The recorder helper now
refuses such a post-command collision. Windows parser16cases passed during an
invocation with one wrong publication-class name; a corrected4method Windows
publication/no-overwrite/transport-outcome selection passes without skips. These
invocation/evidence-path mistakes did not require changing production behavior.

## Limits and next task

No MCU upload/reset/attachment, native runtime, daemon restart, external pin or
sensor operation occurred. Last-known running image remains D088 ui_matrixe50c6da3.
Native setup deliberately uses installed device_init only during setup; its
TEACK/REACK waits are unbounded. Clock assumptions remain conditional (SC-AJ).
New empty strong hook needs final ELF review; whole app timing/initialization,
free RAM/200s/no-gap, Linux-loss cleanup and physical B8 remain unproved.

Next eligible P2 work is an identified inert bare-board recorder/runtime probe,
with synthetic origin, retained memory instrumentation and known clean decoder
precondition. Do not assume MCU reboot cleans Linux framing. A deliberate router
restart has MCU-reset side effects and must be part of the explicitly reviewed
inert run scope, never an automatic recovery. No sensors are required for that
software/transport probe, and it cannot substitute for assembled-robot acceptance.
Then continue actual app scheduler/service integration under D075. SC-A button
windows, physical sensors/motors/WCET and human gates remain pending.


## Final software disposition

Fresh separate same-model review PASS, no open BLOCKER/MAJOR/MINOR in
state/reviews/P2_dump_review.md. Reviewer independently ran26owner cases in
normal/sanitizer and44tooling methods; verified72sources, three strong hooks,
actual main relocation,11initializers,40native42AEABI+fmod/sqrt nonnull bindings.
No static threads in captured base/sketch tables. Six existing registry keys
approved/refreshed; no new upload key. Final56existing controlled tooling methods
PASS79.241s (25SSH+24ADB+5matrix+2staging); four Windows publication/outcome methods
PASS. All production/test bytes remain frozen. Firmware upload-format ELF SHA256
132ca07034d6ad825cba1b545eae83db62b86f619c7d4555ba4e6c62c6ef44d1.
D090 closes its bounded software scope; actual runtime and project remain pending.
