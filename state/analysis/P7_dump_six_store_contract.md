# D235 six-store UART service candidate

Objective: reduce work per native UART service call after D233 retained
TIMEOUT / STORE_DEADLINE at packet offset 7 of 74, payload 59. That record does
not distinguish the shared predicate's 80 us service limit from its 100 ms
packet-age limit. This change is a candidate, not a measured cure.

The sole production edit is `src/config.h` DUMP_UART_STEP_BYTES from 8U to 6U,
committed separately as 1b2af246cd88e6207e846ee340f8c4e46a5bb980 on
77ee8a66efc593d34aa579a5c0625919aa8fa30c. The 80 us, 100 ms and 300000 ms
limits, FIFO selection, owner/IRQ/readiness checks, packet identity, exact
cleanup verification, poisoning and D231 first-failure record are unchanged.
No locked test, wiring, motor permission or native action belongs to this work.
Root separately owns compile-only scheduling, integration and any later run.

The existing independent unrestricted capacity model has 23303 packets,
1156084 payload bytes and 1505629 wire bytes. Reserving one completion call
per packet gives 288575 one-millisecond calls at six stores, within 300000
with 11425 nominal calls remaining. Five needs 331091 and therefore fails;
four is slower. A maximum 79-byte packet takes ceil(79/6)+1 = 15 model calls.
These assumptions establish neither a hardware minimum rate nor immunity to
preemption, ownership loss, READY changes or real deadline failure.

## Focused fixture scope

The existing FIFO model still has eight FIFO entries and one shifter. It uses
the real native owner and formatter. Current-six assertions cover exact store
count, per-packet call count, FIFO-full refusal, final stop-bit completion and
the retained pre-cancel offset. Historical eight-store literal assertions stay
in explicit branches. A historical test class changes only the staged config
6U to 8U, records that profile and its complete source hashes, and never edits
production config. Other profile values and unexpected input bytes refuse.

The default FIFO suite uses current six. Every write retains the original
eight-store upper-bound assertion and adds the tighter six-store assertion;
IRQ preservation, clock-call bound, zero foreign writes, zero RDR reads and
zero FIFO overflow stay unchanged. Live loss is injected before the first,
after the first and after the profile's final store. Current native tests
retain all D231 reason/site/progress/cleanup retention checks.

The focused runner executes current native guards (12 methods), current FIFO
guards and both full streams (11), the original capacity model (1), current
config registry positive and wrong-eight refusal (2), and four historical
eight methods covering packet/FIFO/TC, deadline/wrap/identity, live loss and
real Transfer failure followed by cancel. Historical full streams are not
repeated. Native C++ executions use the existing normal and ASan+UBSan
profiles, one compiler at a time. No broad host suite or sketch build is added.

Current full-capacity coverage uses all 5001 frame and 4096 event slots, the
actual formatter and native packet writer, then independently reconstructs
every MessagePack packet and checks row/raw-byte contents, counts and CRC.
Raw invalid enum stress rows are intentionally not a valid Robot session.
The separate retained D116 stream is replayed byte-exactly, independently
decoded and passed through the existing receiver and CSV validator. Neither
host stream establishes target delivery or physical provenance.

Only the existing dump config registry expectation changes to six. The new
focused wrapper supplies already-adopted later declarations using the current
setup registry's literal defaults, runs all 18 original config assertions,
and proves the old eight value is rejected by that value assertion alone.

## Evidence and next action

Run from this isolated checkout under WSL Ubuntu:

    python3 -B state/analysis/P7_dump_six_store_raw/run_host.py --output /dev/shm/d235-host03

Use a fresh Linux-filesystem output owner for another execution: the existing
receiver's renameat2 publication is unsupported on the Windows /mnt/c mount.
The runner seals a verified archive and per-member hashes before its WSL process
exits; transient output must not be the sole evidence after process closure.
Retain command transcripts,
source/profile hashes, model results and a compact archive of generated stream
hashes/validation receipts. Completed executables and staged sources are owned
temporary directories removed by the existing harness. Release only verified
reproducible output copies after recording their hashes and validation; retain
all failures, source, reviewed target artifacts and prior evidence.

Independent source/host review precedes candidate acceptance and any upload.
D233's cleanup READBACK_FAILED remains unresolved: no actual returned CR1
value was captured. The pinned LPUART material does not justify importing a
USART FIFOEN/UE restriction or relaxing the current cleanup comparison.
