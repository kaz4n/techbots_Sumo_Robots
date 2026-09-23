# D117 explicit native FIFO transport validation

IMPLEMENTED / HOST-TESTED / TARGET-COMPILED / SCOPED-REVIEW-PASS. Final review is in
`state/reviews/P2_dump_fifo_review.md`; this is P2 software evidence, not a gate.

The existing native dump owner now has an explicitly selected FIFO8 mode. Default
construction preserves legacy behavior. Only the app and recorder sketches select
FIFO8; their existing disabled setup/grants remain unchanged. Three fixed owned
setup writes, exact readbacks, AUTOCR validation, conditional cleanup and permanent
poison preserve the adopted contract. The packet, 8-store/80us/100ms limits and
Transfer's 300s total deadline are unchanged. No config, core, Runtime, factory,
installed driver, locked test or upload allowlist changed.

Contract `00a6c36c` was adopted in `3510f682`. Separate same-model contexts authored
implementation and public-contract tests; executable expectations were frozen
before their first execution. The test author did not inspect implementation
bodies. Frozen Python harness `ae9e2c84` passed its first unchanged run: 26 methods,
zero failures/errors/skips, comprising 12 new FIFO methods, 11 unchanged D090
methods and 3 unchanged D116 methods. Each normal/sanitizer native profile runs
201 subprocess stimuli and 21,915,290 checks. Six actual-sketch profiles preserve
existing startup behavior; app setup still initializes its existing Gate/clock,
while absent grants cause no newly selected native-dump calls. Recorder disabled
startup remains callback-passive. See `P2_dump_fifo_raw/author/run1_*` and its
source/test freezes for exact commands, identities and results.

The FIFO fixture models eight queued entries plus a separate shifting byte with
exact rational nominal115200 8N1 timing. Full D116 source replay passes the real
native packet owner and strict host receiver without byte loss. Unrestricted raw
capacity stress preserves 5001 frames and 4096 events, producing 1,148,071 payload
bytes, 1,496,311 wire bytes and 215,676 modeled calls. Deliberately extreme raw
values are labeled synthetic and do not assert semantic validity or Robot origin.
The independent conservative width/call model bounds 1,505,629 wire bytes and
217,659 calls at eight effective stores, 288,575 at six, and refuses the slower
331,091-call five-store case. An eight-store ceiling does not establish a measured
minimum service rate. Existing D116 full-pipeline checks retain 22 cases and
4,202,902 assertions per normal/sanitizer profile, source comparisons, config
refusals and the slow-progress TOTAL failure.

Root full host normal and ASan/UBSan each pass 1478 main cases/50,172,466 assertions
and 187 active-Gate cases/4,536,952 assertions. The unchanged actual factory probe
passes all193 checks under sanitizers. Commands and exit0 receipts are
`P2_app_build_raw/d117_host_normal`, `d117_host_sanitize` and `d117_factory193`;
actual LastTest logs and hashes are under `P2_dump_fifo_raw/coordinator`.

The first native source `5d1d3439` compiled but its default app ELF `0ac42e6c`
exceeded the pristine262144-byte loader model by8 bytes. That failure and all
original artifacts remain in `P2_dump_fifo_fit_failure.md` and raw target evidence.
Repair1 changes only the three-value setup stack table into equivalent bounded
index expressions. Native source is now
`fdd3df0bff64a510a1333dd906f0aa0a1031214caf1bca0c00508ab7507b27fe`.
Separate source/machine-code review confirms the same setup sequence and checks;
no test or capacity was changed to obtain fit. All executable validation above
uses this final source.

| Exact checked final target | Source prefix | Receipt | ELF prefix | Payload | Ordered peak | Remaining span / largest payload |
|---|---|---|---|---:|---:|---:|
| App default, inert | e820c0e1 | d92f929c6cc84961bb86dfea3da2ad00 | 8379f152 | 257280 | 262136 | 8 / 4 |
| App MATCH Immediate, compile-only | e820c0e1 | 4860c2338d2549878d84e75ca348cc0f | 79844885 | 255696 | 260504 | 1640 / 1636 |
| Recorder default, inert | ce5a1f4e | 22ca46d5551b41cca13dbe02b6f1bfd0 | 44297059 | 217340 | 220744 | 41400 / 41396 |

All three exact target audits pass source/ELF/object/startup/import/native-ABI
checks and conditional ordered allocation. App source has91 files, recorder95.
The native object is208 bytes in initialized data, not the former204-byte BSS
object; Runtime is166376 in default and166304 in MATCH, and recorder Runner164176.
Original reviewer harness
assumptions/errors and corrections remain in raw evidence. Collector offline GDB
queries load symbols only, with bounded commands and before/after artifact hashes.
The default app's8-byte modeled margin is extremely narrow; no loaded-memory or
stack measurement is claimed. Debug/temporary ELFs are audit inputs, not substitute
deployment images. Exact hashes, allocation records and qualified imported startup
paths are in `P2_dump_fifo_raw/reviewer/target_*.json`.

There was no upload, reset, MCU execution or UART operation for D117. Board-side
commands compiled and inspected files on Linux only. The last MCU image remains
the completed D114 ADC probe `396bcc45`; its identified run is consumed. Native
setup ACK reliability, UART ownership/clean framing, effective service rate,
receiver delivery, full-app loaded RAM and complete800us physical tick remain
pending. DUMP-RATE-1's legacy deterministic capacity defect has a tested FIFO
software solution; hardware delivery remains unqualified. No motor permission,
physical acceptance or human phase gate is inferred.
