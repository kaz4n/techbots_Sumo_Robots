# Codex handoff - 25 September 2026, Asia/Dubai

## Current result

D191 cleanup is verified and D190 run02 completed successfully on the UNO Q.
The latest flashed image is source21df6ae8/static/default/MATCH0/MOTORS_ALLOWED0/
probe1, raw ELF2f8dc9f1/package deb40317. It completed four application epochs,
retained41 successful native callbacks and froze after its explicit inhibited
halt. The original D160/D161 full-app IO fault did not recur and is still open.

Read [actual validation](analysis/P7_app_motor_fault_run02_validation.md), its
linked raw receipts and actual review. Clean reviewed execution HEAD was
b3e584d1ce265f2c469ce0edc39bafe4121b65f0. Check-only/execute each returned0;
13transports, one upload,26passive reads727088B, all four full flash brackets and
closing checks passed. The saved pre-abort state is RUNNING/NONE/epochs4,
maximum_execution_us582/missed0; final FAULT/ABORTED/STOPPED fields follow the
intentional diagnostic abort. All peripheral setup grants remain absent.

Both samples of each of six SRAM windows are byte-identical. Their coherent
atomicity is UNPROVEN. The14saved files17913B were fetched in one file-only query
with hashes/identity/closing rereads verified; no duplicate firmware downloaded.
The fixed interpreter uses observed D188 offsets, not the older D149/D173 layout.
Raw bytes remain in retrieved_inert_run02/0001-read-saved-results/stdout.
No native process or local execution session remains active.

## Exact next task

Define a longer bounded inhibited observation to investigate the unreproduced
full-app native IO fault. It must retain the first failing callback and useful
application state without overflowing the fixed trace or unbounded sampling.
Start from the successful D190 predicates and the existing D186/D162 source.
Do not weaken the150us settle limit, change pins/setup grants, or call the old
fault fixed. Preserve existing diagnostic source/evidence and locked tests.
New firmware needs scoped independent tests/review, compile/artifact/ABI binding,
fresh board identity and a separate native owner before execution. Reuse existing
bounded primitives; do not create another general orchestration framework.

D190run02, D189run01 and every prior native owner/scope are consumed. Do not retry
historical launchers, repin consumed scopes, or treat their boot as a fresh fact.
A successful short diagnostic is not sustained application qualification. Current
D185 main-app dynamic bench/MATCH compilations are complete but retain their
conditional low-memory blockers; see P7_current_app_compile_validation.md.

## Cleanup and authentication

The user supplied authentication for the already prepared D191 cleanup. One
unchanged4192f23e wrapper removed exactly3obsoleteD184scratchcopies2334244logicalB,
kept originals unchanged and permanently dropped to UID/GID1000. Resultc0e45b30
and observation02 were independently inspected. Credential went through stdin,
not argv or repository files; do not retain/repeat it. Permission was restricted
to this exact cleanup, not general privileged access. Earlier CLEANUP DONE clicks
had not executed anything; original missing-result/refusal receipts remain.

## Boundaries and schedule

Active phase: P7 software/release preparation, under D051/D075/D122/D137.
P0-P5 physical/human acceptance and P7 release remain open; P6 is conditional.
No STAND OK/RING OK for a motor-capable run, PINMAP approval or human phase gate
has been created. Sensor/electrical acceptance, actual RAM/stack/WCET, D121 B7/R6,
native dump lifecycle and release readiness remain open. Header IO stays3.3V.

Actual P3 not passed by end28Sep invokes reactive+SIDESTEP/DIRECT+recorder and
drops ARC/WAIT/P6 polish. P6 also needs actual P4 by30Sep. Freeze1Oct21:00Dubai,
rehearsal2Oct, competition3Oct. Scheduled dates create no acceptance.

## Storage and resumption

Recheck C: before work; recently about340MB free and fluctuating. Keep unique
raw receipts/source/hash-based reproduction; no duplicate firmware/debug/source
snapshots, Python bytecode or parallel heavy builds. See STORAGE_LOG.md for
retention/disposal purposes and exact savings. Do not retry any policy-denied
cleanup target, including both old motor-fault stages, build/stage/app, the2B
input.wire directory or the37historical denied stage folders. Do not modify paging
or persistent virtual disks. Current board capture/artifact originals stay retained.

Read AGENTS.md fully, docs/prompts/CODEX_RESUME.md, CODEX_EXECUTION.md and latest
PROGRESS/DECISIONS/FACTS/TUNING_LOG before work. Preserve user changes and commit
bounded tasks locally; never push or rewrite history. PROGRESS is append-only
with legacy bytes: its first140971B SHA256 is
1dbbeb53c3dc046128494af3bef240b9a00353929d6121991900c90bb2838b77.
Historical handoff checkpoints remain in Git; use this current next action.
