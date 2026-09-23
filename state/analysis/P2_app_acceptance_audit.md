# D099/D100 actual app source and ELF acceptance audit

2026-09-23 Asia/Dubai. P2 software under D051/D075. This audit reads completed
corrected-wrapper builds from board Linux over ADB serial2629958581. It performs
no compilation, upload, reset, MCU attachment/access or motor operation. The
coordinator runs and records the separate compilations and library experiment.
This is an implementation-side evidence audit; separate review remains distinct.

**Scoped result: PASS for all three completed source/object/ELF audits.**
No collection/identity/dependency/startup check failed. Local inspection-helper
corrections are recorded in `P2_app_acceptance_raw/audit_harness_corrections.md`.
This result alone does not adopt the build policy or qualify target execution.

## Reproducible evidence

`P2_app_acceptance_collect.py` extracts the unique literal remote program from
`P2_bridge_dependency_target_audit.py` using AST, records both hashes, and reuses
that existing offline audit. A small supplement recomputes the complete source
digest and returns the three real ELF files plus packaged ZSK bytes. It refuses
an incomplete or pre-D100 receipt. Raw command, timestamps, stdout/stderr, decoded
audit and exact artifacts are retained separately for each mode under
`P2_app_acceptance_raw/`. The corresponding wrapper receipts are copied intact.

All collected builds use the exact82-file source
`570ef35fa0ed25601b5f04097d5e5361545c357d958530d62092c5c5c77c6d84`,
matching D098's frozen candidate, the current repository source enumeration and
the board's full source enumeration. All three ELF and ZSK hashes match each
wrapper's completed verified receipt. Historical D098 evidence is unchanged.

`P2_app_acceptance_raw/analyze.py` reuses the prior review's ELF32/ARM decoder,
relocation parser and relocation-aware startup comparison without executing
their review entry scripts. The reused source hashes and detailed results are
in `comparison.json`. This is a new execution of the saved decoding/model code,
not a new independent model or new cross-model review.

## Default and inert Immediate

Both modes retain the D098 candidate's exact final ELF
`9808dc594d77be8f43865a17542a48b715b4d5ee4a1277d6f946d0a6ccb09e65`.
Each has73objects and1438allocated object sections: all content hashes,
size/alignment and relocation records match the candidate. Debug/temp ELF hashes
are checked individually; their debug paths need not equal the older build.

The generated INO CPP remains
`b4f05a6e010af374a876085c654597977cae7581efd58a09936af0085d27130f`.
Each mode supplies73expanded commands,117dependency files and121checked metadata
payloads. C/C++ commands use phase0 and MATCH0/MOTORS_ALLOWED0; the unchanged
assembly recipe does not consume the discovery macro. No dependency-file text
names the six removed Bridge/RPC-related libraries, and no command uses an
Arduino library include directory. The wrapper's successful CLI envelope has
no discovered libraries; the coordinator's explicit-library fixture tests that
separate rejection boundary.

Immediate changes the FQBN's wait_linux_boot option and uses the installed
`-immediate` packaging argument. Its packaged ZSK differs from default at exactly
offset14, value0 to4; every other byte matches. Each package is byte-identical to
its final ELF after the16-byte header. This is observed packaging evidence, not
an observed boot. Default ZSK SHA256 is
`aea3dfc5043cba49a4e7ec08787a2c079fe04852cc2122d69d2b6b14882ace7d`;
Immediate is `96b4a7dfbfc926c2f982390ea9a7584dd9619d3979bb4582f7a539020e39f09e`.

## MATCH Immediate and the enabled-motor compile branch

MATCH uses MATCH1/MOTORS_ALLOWED1 and Immediate explicitly. All82sources,
73objects,117dependency files and493project function identities remain. Of the
1438common allocated object sections, exactly three change content and
relocations, in the two source files containing MOTORS_ALLOWED branches:

| Function | Inert section | MATCH section | Inspected compiled difference |
|---|---:|---:|---|
| UnoQPort::writeEnable |84B|140B| High path checks settled state, all four written channels and valid timer bank before the existing pin ownership/write/readback sequence |
| UnoQPort::writePwm |228B|228B| Pulse may be nonzero but remains bounded by period; configured channel, low enable, mapping, timer checks and post-write checks remain |
| MotorGate::transact |104B|420B| Computes signed channel pulses and applied feedback, writes enable low, writes four channels, settles, then conditionally enables; failures still call inhibit |

All other1435allocated sections and their relocations match D098 exactly,
including MotorGate command/hold validation, governor, edge arbitration, Runtime,
native pin tables and application startup. No allocated object section is added
or removed. Saved `motor_macro_disassembly.txt` files expose the actual inert and
MATCH instructions used in this inspection. This inspects the existing compile
branches; it is not a new hardware trace or claim of permission to run them.

Final linkage additionally retains the existing ten-byte `__aeabi_d2uiz` veneer,
which relocates to the already present `__real___aeabi_d2uiz` import. There is no
new undefined import. Net text grows376B after layout/alignment; the temporary
global-symbol allocation grows8B. Final ELF SHA256 is
`523f8c12aad4a9f62ff82d8d923bd90dcdd47299b9c026df5c8c2c8ad8fc38b6`;
packaged ZSK is `42a84c6fcbf4ac581cc567e642752c88b7ef1ed028fc2aabda1e0c1608467d76`.
MATCH's package uses `-immediate` and equals its ELF after the16-byte header.

## Retained execution and dependency boundary

The actual main, initVariant, static-thread startup, setup, loop, application
static constructor and strong empty loop hook retain their normalized code,
relocations and resolved BSS targets. Main remains exported; the loop hook is
the strong two-byte return `7047`. One init entry calls `_GLOBAL__sub_I_setup`;
there are no fini entries.493reviewed project functions remain. Runtime is
168888B and NativeSources848B; recorder capacity, tunables and source did not
change. No Bridge/Serial/RPC singleton roots reappear.

The176undefined imports remain identical in all nine collected ELF files to D098's
candidate.39native exports and42AEABI bindings retain nonzero addresses in the
same pinned loader; its SHA256 is
`39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`.
Static-thread symbols remain unchanged. These are offline native-binding checks,
not execution of any imported API.

## Memory and remaining limitations

| Build | Actual compiler exit | Program bytes | Compiler payload | Nominal remainder | Conditional load peak | Conditional largest payload |
|---|---:|---:|---:|---:|---:|---:|
| Default,0/0|0|153684|248308|13836|252472|9668|
| Immediate,0/0|0|153684|248308|13836|252472|9668|
| MATCH Immediate,1/1|0|154156|248684|13460|252856|9284|

The actual compiler warnings about low memory are preserved. Conditional load
peaks reapply the prior pinned model to each final ELF. Remaining chunk span is
9672B for inert modes and9288B for MATCH. These calculations assume a pristine
pool, persistent-flash peeks, the same loader/configuration and no extra
constructor/interleaved allocations. BSS remains169780B in every mode; only the
MATCH copied text and temporary symbol table grow.

No result here measures loaded free RAM, fragmentation, stack, startup execution,
the complete800us tick, physical sensors, UART, motors or any human gate. The
app still does not instantiate the native dump owner; this audit neither adds
nor budgets future UART/calibration-snippet/local-reset integration. The previous
D091 synthetic recorder image is not replaced by any action of this audit.
No inert-source approval key, firmware/config, locked test or installed package
was changed. Full P0-P7 and physical acceptance remain incomplete.
