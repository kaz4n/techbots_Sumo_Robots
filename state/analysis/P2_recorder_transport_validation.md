# D116 complete synthetic recorder transport bench

IMPLEMENTED / HOST-TESTED / TARGET-COMPILED / SCOPED-REVIEW-PASS.
This is software preparation for P2 B8, not physical acceptance.

`bench/recorder` composes the existing Transaction, Robot, inert MotorGate,
AttemptRecorder and Transfer. It records the complete 200-second synthetic
attempt, preserves the actual STOP tail, qualifies the service reset, navigates
the actual LOG_DUMP menu, and exports retained source through the existing port.
The default sketch is disabled and its grants are false. No upload key is added.
Existing core, HAL, config and locked tests are unchanged by D116.

The independently authored executable expectations were frozen before execution
against contract `056c69c8`. Source `first_source_freeze.json` and test
`first_test_freeze.json` retain their original bytes under
`P2_recorder_transport_raw/implementer` and `/author`. Both are reused separate
same-model contexts, not cross-model review. The public header prefix matches
adopted commit `99555b80` exactly.

The first independent normal and ASan/UBSan runs passed 22 cases and 4,202,902
assertions each. Full-length normal, wrap and partial-write captures retain all
5001 frames; the strict Python receiver compares every exported frame, status,
event and summary with the retained source. The ideal run contains 8 events,
532,562 payload bytes in 10,027 chunks and CRC 1022767091. A one-byte sink reaches
the existing TOTAL timeout at exactly 300,000 bytes, preserves the exact positive
prefix and all source frames, and cannot publish a successful received bundle.
These are host results and protocol counts, not native UART measurements.

Three initial copied-config cases failed to compile before reaching the intended
Runner guard: zero debounce/long values and long24 violate existing countdown
static assertions. Original failures remain in `author/run1_*`. The reviewed
`fixture1.diff` preserves the two zero cases as reason-specific compile refusals
and uses copied debounce596/long600 for the runtime G==long boundary, satisfying
the existing MODE_SHORT_MS600 dependency. The affected-method rerun passes all
five runtime profiles (224 assertions each) and both upstream compile refusals.
No production or other executable oracle changed. Final Python harness0fab202a
and its pre-execution freeze, source hashes and cumulative results are retained
in `author/validation.json`; the source still matches its first implementation.

Full host normal and ASan/UBSan each pass1478 main cases/50,172,466 assertions and
187 active-Gate cases/4,536,952 assertions, with no failed/skipped cases. All183
controlled build-policy methods pass, including8 new recorder cases and175
unchanged earlier cases. Commands, UTC times and exit0 are in
`P2_app_build_raw/d116_host_normal`, `d116_host_sanitize` and `d116_policy183`;
both actual LastTest logs are copied under `raw/coordinator`.

The board-Linux checked compile-only receipt is
`build/app-receipts/eb77072537df44eeb3d7c36fe049c642`, preserved with the collector
under `raw/target_e2cd303f_bench-default_checked`. Exact 95-file source:
`e2cd303f701fdff5699c17e40ae401713de0f28fca0c8f2d5ba24a2333e6b4a2`.
The source freeze, three ELFs, ZSK, ten ABI layouts, tool identities and sixteen
offline command results were collected successfully. Independent whole-image
audit passes: final ELF `538a7c81a9ee17ebdd9a9d2f6b1bc99a37c7f3de4772b9c373f43cf5675a4462`
is102104 bytes; ZSK is `96b5f84353a26a0ec17bd894f2c83d6de37091fef23a827ee43817df5f375aba`.
Every function matches final/debug and relocation-normalized temporary code;
the sole initializer and false-grant startup remain passive, the loop hook is
strong/empty, and all used imports resolve against the pinned loader. Actual
ABI gives Runner164176 bytes and native owner204. Compiler payload216932 bytes
is distinct from the ordered pristine-pool allocation peak220280, leaving
span41864/largest payload41860. These are conditional model results, not loaded
RAM. Three distinct reviewer harness assumptions were corrected with original
failures retained; no source/artifact/test change resulted. No upload, MCU reset
or new firmware run occurred.

The native FIFO-disabled throughput blocker is explicit in F143,
`spec_conflicts.md` DUMP-RATE-1 and `P2_native_dump_throughput_audit.md`.
The observed synthetic payload would require 682,967 UART bytes after packet
overhead, above the current mode's source-derived 600,000-byte upper bound.
Fast host callbacks do not resolve that blocker. D117's proposed FIFO mode needs
its own contract, tests, implementation and target review. Native framing,
ownership, receiver delivery, full tick timing, physical B8 and human gates remain
pending; the current MCU is still the completed D114 ADC probe.

Final review is `state/reviews/P2_recorder_transport_review.md`: separate reused
same-model scoped PASS with no new finding. Its private final11-method run
reproduces the22-case normal/sanitizer pipeline, complete and truncated receiver
checks, native/default probes, flags, config profiles and policy cases. Exact
author and reviewer stream hashes agree. No phase gate is claimed.
