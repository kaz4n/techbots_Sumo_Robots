# D204 actual file-only ABI evidence review

26 September 2026, Asia/Dubai. Separate same-model reviewer, reusing the closed
source/host and admission review context. Only this new review file is written.
Inspection used saved JSON/base64 streams, static source/command parsing,
literal program reconstruction, hashing and Git reads. No subject import,
test, compiler, device transport, ELF retrieval, native file tool or cleanup
was executed by this reviewer. Earlier reviews remain unchanged.

**FINAL PASS for the single completed D204 file-only ABI attempt and its
saved commands, current layouts/symbols and closing evidence. No open material
finding.** The new artifact ABI is observed; instruction semantics, runtime
repair and timing improvement remain separate and unestablished.

## Attempt and immutable input closure

The saved local check-only and execute records both exit zero at reviewed HEAD
`d3bcfaa026e971c902f33c1f4c648338a6263677`. Current Git HEAD still equals that
commit during this review. The check output agrees exactly with corresponding
fields in inputs.json; execute output parses to the exact local_result.json.
The current source remains
`4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2`,
serial `2629958581`, boot `55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`.

All 238 coordinator pins, eight fixed-scope pins and 143 runtime local pins
were independently rehashed and remain exact. They link the completed host
review `ae662c11...`, admission review `763b0c82...`, accepted D203 compile and
the current raw/debug ELF identities `390b69c1...` / `b3520cac...`. No previous
ABI packet or historical address is substituted for this attempt's output.

| Saved item | Bytes | SHA256 |
|---|---:|---|
| inputs.json | 33427 | `9e8db724955f5bcf5c5e206d862ff445778b08c7a48808f447b14884d46f124c` |
| result.json | 904847 | `bbdecb404a42237fafaf0bf4b2e38690b62ee45119cdfabd9b2f7dde17a6b9b0` |
| abi.json | 5410 | `6fed52b884c6015a2c9d2f6803bea20e764418fcc94cffe144161026259f6a97` |
| local_result.json | 275 | `3cd224b237fc1b18586d7b2fb22c2a47833a801fea06b96b338027102db5d55d` |
| Outer invocation | 1258 | `856d8d5eff568e2c05817b069c36f3c3dc3b233647f938be13da69a2ebf5ac1a` |
| Root independent closing | 6866 | `e181ebe1febecf4cd8c6c60d477217f593b11b555e181a5b3181205fd3f20666` |

The first four files are under
`analysis/P7_motor_const_compile_raw/native_abi_static01/`; the last two are
`native_abi_static01_invocation.json` and `abi_native_closing01.json` in its
parent directory. The native owner is now consumed.

## Exact transport, file commands and closing checks

The sole transport's intent/result argv, timeout and command units agree;
transport return code is zero and its stderr is empty. Its saved stdout parses
to the exact durable result.json. Independent Windows command-line accounting
reproduces 6225 UTF-16 units including NUL, below 30000. The transport uses the
fixed ADB serial, shell-T, minimal environment and remote Python-I-B with the
unchanged 400-second bound.

Data-only decompression of the submitted command yields 20817 bytes, SHA256
`19891b2560f5da2422eb0b69d636ad973fe6934f64e386f1176c5a2d8ae941b4`.
This equals the saved program hash. Independent full reconstruction from the
pinned identity preamble, fixed absent-scope guard, original stop/reap function
bodies, literal pins/commands and unchanged remote-read body reproduces every
submitted byte. No additional operation is hidden in the compressed program.

The observed identity is UID1000/arduino, the required boot and CLI digest,
no recognized conflicting processes and 13,914,439,680 free home bytes. All
twelve file pins are current D203 artifacts or the pinned readelf/GDB/loader/TLS
inputs. Each of the four child argv lists equals both the saved input list and
the independently reconstructed contract query list. The children are:

- GNU readelf version: Zephyr SDK 1.0.1, binutils 2.43.1.
- GNU GDB version: Zephyr SDK 1.0.1, GDB 16.2.
- Complete readelf header, sections and symbols on the current raw ELF.
- Guarded GDB type/layout/offset/enum queries on the current debug ELF.

All four return zero, are reaped, do not time out and have empty stderr.
Their saved per-child deadlines remain 60 seconds with five-second reap.
Canonical base64 encodings independently match the declared stream byte
counts: 283, 281, 158419 and 504466 stdout bytes, all below 1 MiB. Their own
saved timestamps establish sequential child execution; durations are about
0.0120, 0.0727, 0.0300 and 0.4478 seconds. These file-query durations are not
firmware timing measurements.

All thirteen remote closing rows match the exact runtime insertion order:
eight artifacts, GDB, readelf, loader, TLS and final board identity. All are
PASS, result status is OBSERVED and first_error is null. The submitted code
requires stable device/inode/size/mtime/ctime across opening/closing hashing
for each file. Individual numerical stamp arrays are internal to that program;
the saved receipt reports their accepted equality through the PASS rows,
not an independently emitted stamp inventory.

The local closure is STATIC_ABI_OBSERVED with one transport, null first_error
and a PASS local check. Its local timestamps span 09:22:50.234562 to
09:22:52.615863 UTC. No ordering inference is made between independent host
and target wall clocks.

The coordinator's first ad hoc audit, and independently this review's first
closure-order comparison, initially treated sorted serialized pin dictionaries
as runtime order. The submitted literal pin map preserves the actual order;
checking its complete thirteen rows resolves that audit-only assumption.
No reader, guard, fixture, saved result or native attempt changed or reran.

## Fresh observed ABI and report

The saved readelf output identifies a static ELF32 little-endian ARM EXEC
image, nine sections and one complete .symtab with exactly 2299 rows.
Independent parsing recovers every consecutive index 0 through 2298. The
Runner and separate report are unique LOCAL/OBJECT/DEFAULT rows in numeric
section 5, the freshly observed .bss NOBITS section at 0x20013960 with size
171680 and alignment eight.

Runner is at **0x20013960**, 169736 bytes, observed alignment eight. The
separate SETTLE report is at **0x2003d3e8**, 28 bytes, observed alignment four.
Both lie wholly within the checked initialized zero-BSS interval
`[536951136, 537121800)`, and their half-open ranges do not overlap. These
coordinates equal historical coordinates but were obtained from the current
D203 files in this attempt. They do not describe current MCU contents.

Independent query reconstruction confirms exactly 223 expressions. Independent
raw-output parsing matches all 111 ordered markers and 88 unique numerical
answers to the saved ABI summary: 23 size/alignment/layout groups in total,
eleven Runner offsets, eleven SETTLE field offset/width pairs and nine reason
values. The precise group count is **22 TYPES plus terminal bool**, totaling
23; earlier contract/review shorthand saying 23 plus bool did not describe an
additional query. No query or oracle change is involved in this clarification.

All Runner window addresses are recomputed from the current base and observed
offsets, with bounds and alignment checked. Sample size/alignment is 12/4,
Report 28/4 and Reason 1/1. The raw GDB ptype blocks independently display the
expected Sample members, both nested report samples, presence bytes and
reserved bytes. Enum answers are NONE0, SUCCESS1, NULL_CONTEXT2,
PRECONDITION3, INITIAL_BANK4, POLL_DEADLINE5, POLL_BANK6, FINAL_DEADLINE7 and
POLL_LIMIT8. The contiguous polls block observes unsigned int with size and
alignment four, immediately followed by bool.

The original raw readelf uses Runner size token `0x29708`. Independently
replacing only that exact row's size token with `169736` reproduces the saved
private normalization byte count and digest. Original readelf remains 158419
bytes / `5632ddc6...`; the private copy is 158418 bytes / `76bad013...`.
Raw readelf/GDB encodings and caller receipts are preserved.

## Current emitted motor helper inventory

The complete current symbol table contains these exact unique FUNC rows in
section 1. Values below are the emitted Thumb symbol values; the odd low bit
must be handled explicitly by any separately adopted instruction-range task.

| Short symbol name | Symbol value | Bytes | Binding |
|---|---|---:|---|
| candidatePeriod | 0x08110c91 | 20 | LOCAL |
| publishSettle | 0x08110cd5 | 60 | LOCAL |
| mapChannel | 0x08110da1 | 264 | LOCAL |
| UnoQPort::timerValid | 0x081111a5 | 384 | GLOBAL |
| UnoQPort::writePwm | 0x08111411 | 228 | GLOBAL |
| UnoQPort::bankValid | 0x081114f5 | 68 | GLOBAL |
| UnoQPort::settle | 0x08111539 | 292 | GLOBAL |

The exact candidateRate, expectedRate and expectedPeriod mangled symbols each
have zero rows. All selected present/absent rows independently agree with the
root closing receipt. Exact-name absence does not exclude inlined computation,
clones or division instructions inside consumers. No disassembly or runtime
instruction was observed in D204, so neither constant-selection emission nor
removal of runtime division is established by this review.

## Final evidence disposition

The root closing receipt's per-command stream hashes, durations, local closure,
selected symbols and complete eight-file inventory all independently match
the saved evidence. The native owner contains eight files totaling 1,857,008
logical bytes. The root validation document agrees with these observations
and correctly records 23 total groups. Its saved local free-space observation
is 9,487,302,656 bytes. No binary download, manual cleanup or storage recovery
is claimed.

Accept this one consumed file-only attempt. It supplies current ABI coordinates
and complete symbols for a new, separately adopted entry contract. Such a task
must derive ranges from these current rows and review actual instruction
semantics before any later separately reviewed inhibited runtime attempt.
D201 remains the latest flashed image. No SETTLE repair, timing gain, WCET,
atomic publication, physical acceptance, motor permission or human gate follows.
