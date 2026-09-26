# D243 current target compilation and retained observer validation

27 September 2026, Dubai. **PASS for current compilation and offline target
retention/exclusion.** Both native builds are COMPILE_CHECKED. The independent
[actual review](../reviews/P7_outer_loop_timing_actual_review.md) records its scope. This is compile and offline binary
inspection evidence, not an MCU timing run or physical P2.2 acceptance.

## Frozen source and host preparation

Observer source commit: `6cda7d82c21117f13055d58a9ebbd90963ea2195`.
Frozen build HEAD: `ce15bb967614af54cf7f059dc541949ce754c776`.
Common app source digest:
`fcb9a31adef28ca7d2f79335cc466dcc4ddb31007ff2da4341a33fb07983cace`.

The source/host review88cfdc2d accepted 16 cases/143 assertions and 15 serial
commands, including ordinary-profile exclusion and optimized host retention.
All 177 host inputs stayed fixed; preserved failures and the unexecuted defensive
post-completion invariant-failure seam are described in
[P7_outer_loop_timing_validation.md](P7_outer_loop_timing_validation.md).
No broad inherited suite was repeated.

## Two serial current native builds

| Build | Profile | Elapsed | Transport calls | Package bytes | Structural RAM remaining |
|---|---|---:|---:|---:|---:|
| Timing | p4_timing / M0 | 411.576 s | 237 | 92480 | 84112 |
| Production | match / M1 | 252.399 s | 25 | 92092 | 91280 |

Each build used one compiler process, one properties query, nine reaped checked
children and nine successful closing checks. All 136 current input bytes match
the reviewed Git blobs;106 staged files include the new observer header.
Timing used `arduino:zephyr:unoq:link_mode=static`, MATCH0/M0 and the existing
P4-reactive/timing macros. Production used
`arduino:zephyr:unoq:link_mode=static,wait_linux_boot=no`, MATCH1/M1 and all eight
probe macros zero. No upload/reset or MCU execution occurred in this work.

- Timing owner: `P7_commissioning_build_raw/commission-p4_timing-m0-5e497d4294e4`.
  Package92480B SHA256
  `176f764273a5e32511800c641db589bc71f7b48a7783aae7fc4de12d73af5552`.
  Final ELF165380B SHA256
  `47a6d01c58205e4d48e8c8531cea1d67b4908a49764e4265f9c6ef903342499c`.
  Root retained1001 original owner files/1756389B plus six outer receipts.
- Production owner: `P7_match_static_raw/match-static-match-m1-c1c267697b5d`.
  Package92092B SHA256
  `7895a4d8991bd2158e63c69cb37ebcdc4f39632311a1dbf47401c3a34f664c86`.
  Final ELF165836B SHA256
  `ba9766a8a207564fa0d2bd25dd6472a16f176f09740eda4689e167e81536a666`.
  Root retained153 original owner files/1037328B plus six outer receipts.

Both the production package and final ELF are byte-identical to D241's accepted
production image. The debug ELF differs and is separately hash-bound. The later
compile reused the already verified common remote source directory; it did not
skip compilation. Copy closures under the two native_*01 raw folders reconcile
all durable files. RAM figures above are linker accounting, not live free RAM.

## File-only retained code and layout

The scoped helper uses pinned ADB, existing pinned ELF/TLS parsers and pinned ARM
GDB. It brackets source inputs, exact final/debug ELF files, board identity and
GDB bytes before/after; saves original command streams; and pulls only the final
ELF for local parsing. GDB auto-loading and inferior function calls are disabled.
No MCU connection, target-memory read, upload, reset, inferior start or run occurs.

Timing target object `outer_loop_timing` is 6688 B in writable `.bss`; DWARF confirms
Observer/Data 6688 B with 8 B alignment. Both profile file inspections close with no
first or secondary error. Production has no outer observer object/helpers; its
16-byte loop consists of the existing Runtime tail call and literal pool.
Final `target_timing03` closes with script3409bf71 and summary SHA256
`3436401eb39e3efe61d3d0318f60a0b8d38fdfb32da4c9af26cb6e89787cf4bb`.
Manual ARM review confirms the unique observer at 0x2003d430 and reachable stores
for status, contexts, anchors and both histogram bases (0 and 3236 bytes).
The literal-pool callee is 0x081000c9; its exact 108-byte function stores sample
count, indexed bin/overflow, maxima, anchors and saturation fields. Active and
terminal paths each reach Runtime::step once. This proves retained compiled work,
not observed target execution. Production `target_match01` summary SHA256 is
`8a397fea91fbfe3c73244876b7be40936acf914ccd3f79952c61ca7df65640bb`.
No production repeat was needed after the timing-only range-selector correction.

## Preserved inspection history and limits

`target_timing01` failed locally before any command: Windows Python3.13 path stat
and descriptor fstat expose different ctime values. The exact failed script is
retained. The narrow fix uses the consistent Windows birthtime while retaining
file identity/type/link-count/size/mtime and SHA checks; Linux ctime is unchanged.
`target_timing02` and `target_match01` pass file/layout closure with scriptf6b1571a.
The timing dump omitted an indirectly called Distribution::observe function,
so `target_timing03` adds its exact 108-byte ELF function extent under the same
bound and closes the manual retention review. Prior scriptf6b1571a is also saved.
No failure or incomplete review was relabeled as full retention acceptance.

The five-minute population is conservative consecutive-entry wall time, including
observer/framework work. Whole final straddler and one separate drain survive;
the final drain-freeze tail stays outside the population. First-entry warmup,
clock/classification errors and incomplete evidence remain explicit. Neither
static retention nor the initialization latch establishes continuously live
sensors, five minutes of valid robot operation or an 800 us physical WCET bound.
The loaded image remains the previously accepted D239 M0 synthetic recorder.
B7/R6 policy resolution, physical qualifications, human gates and conditional P6
eligibility remain separate. No new run permission or phase pass is created.
