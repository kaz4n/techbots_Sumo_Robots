# D106 native pin table deduplication

2026-09-23 Asia/Dubai. IMPLEMENTED / HOST-TESTED / TARGET-COMPILED.
Separate same-model final scoped review PASS is recorded in
reviews/P2_pin_table_review.md and raw/final_review.json. D105-R2 is closed for
these exact replacement profiles only; no physical or human gate follows.

One const binding now shares the installed gpio_dt_spec table across motor,
opponent, QTR and ADC owners. No pin/config/device-tree/core-installation change
was made. Original includes, validation order, alias/bounds checks, permissions,
operations and cleanup remain intact. Tests/locked and src/core are unchanged.
The four consumer diffs are mechanical, as proved in raw/worker/mechanical_diff.json.

Installed wiring_private.h is hashed in raw/worker/installed_stdout.json. All
four old560-byte arrays have identical descriptor bytes and70 device relocations.
The final91-file source is d72bff70aa420aab50d4591efe3b267e2581b19623bf829e38d0819462f403a2.
All final ELF stages retain one genuine table. TABLE resolves to that table;
COUNT is the sizeof-derived70. No extra constructor, owner, I/O or new import.

| Exact checked receipt | Profile | Compiler payload | Conditional loader peak | Remaining span |
|---|---|---:|---:|---:|
| d63c11aab30e4df7b321419b25749ec9 | default bench |256880|261688|456|
| b9322331ff22401a8768a2589d014129 | Immediate bench |256880|261688|456|
| b5403185105742a6b50c72cac7670c4e | Immediate MATCH, compile only |255296|260056|2088|

The pool is262144 bytes. Default/Immediate final ELF bytes are identical.
Default net peak saving is1424 bytes versus D105c05916c6: copied rodata saves1672,
text grows232, symbol metadata grows16. Every ordered allocation must fit, not
just the compiler payload. These are pinned pristine-pool/persistent-flash
models, not loaded free-RAM, stack-watermark or WCET observations.

Independent author cross-unit tests passed10 normal/sanitized variants with
sizes1/3/17/70/71, exact descriptor/count/reference identity, immutability,
no constructor or I/O, and three expected const-mutation compile refusals.
Separate reviewer repeated them and full host tests on exact final source.
Existing motor/opponent native suites passed27 methods; ADC/QTR passed26.
Integration passed22/23; the remaining method's old additive config context
omitted three already-approved D096 constants. A new spec-derived wrapper
passes the unchanged nested18 checks and rejects three altered-value profiles.
No original assertion changed. See raw/registry_validation.md and root
P2_app_build_raw/d106_* command/exit receipts. Eight old harness changes only
add source dependencies; P2_pin_table_harness_audit.py verifies complete AST
equivalence after removing those additions.

Original failures remain: omitted Arduino.h in the new author fixture; native
motor substitute declarations lost when a production include was removed;
the stale registry invocation. Repair preserved every assertion and restored
the original includes. Exact final ELF matches the first15566689 target bytes.
ADC/QTR variant receipts straddle that include restoration; executable semantics
are unchanged, and the final all-profile ELF identity is checked independently.

Offline target ABI gives Runtime166376 bytes in bench and166304 in MATCH,
alignment8; report24, threshold bank20, SetupGrants21. The exporter mutable
state and formatter path are absent from MATCH. Default writeCalibrationOutput
has a136-byte direct frame and formatConfig176 bytes; their nested contribution
alone is312 bytes, excluding callers/callees/interrupts. First offline GDB read
hit its default max-value-size for large types; raw stderr is preserved and the
large_types retry succeeds. No actual stack high-water measurement is claimed.

No D105/D106 firmware was uploaded. Bare UNO Q remains frozen at the verified
D104200001-epoch inert probe. Native hardware, physical gates and full-app
worst-case execution remain pending. Source/target evidence does not authorize
motor runs or refresh historical inert upload keys.
