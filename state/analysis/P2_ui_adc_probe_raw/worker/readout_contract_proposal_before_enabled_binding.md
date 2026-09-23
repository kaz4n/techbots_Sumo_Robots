# D114 readout contract proposal

Draft only, 2026-09-24. No decoder implementation, test execution or board action.
This specializes the adopted `P2_ui_adc_probe_contract.md`; no run/upload key is
authorized here. The coordinator selected the full flash checks before/after
below. All D114 enabled-image pins and ABI verification remain pending.

## One pure decoding API

Propose `decode_runner_pair(first: bytes, second: bytes) -> dict` in the eventual
narrow capture module. It performs no file, clock, process or board operation.
Both arguments must be immutable bytes of exactly the pinned Runner size;
otherwise raise ValueError. No permissive truncation, bytearray coercion, firmware
function invocation or caller-supplied ABI/address/config argument.

Return exactly these keys:

```
schema_version: 1
first_sha256: lowercase SHA256 of the complete first Runner
second_sha256: lowercase SHA256 of the complete second Runner
byte_identical: bool
snapshots: [first_decoded, second_decoded]
frozen: bool
acquisition: "COMPLETE_128" | "FAULT" | "NONTERMINAL" | "UNAVAILABLE"
physical_acceptance: false
```

Each decoded snapshot has exactly `valid` (bool), `errors` (array of objects with
exactly `code` and `path` strings), `report` (the full public Report below), and
`captures` (the committed prefix, or null if count is outside0..128). Scalar
fields use their actual unsigned integer values, including bool storage bytes;
do not coerce an invalid boolean byte into true. Known booleans must be0 or1.
Unknown enum/nonsensical values remain visible and add an error; never replace
them with default/healthy values. Errors are ordered by report fields, timing,
phase/count, then capture index/field and cross-record consistency. Use codes
`BOOL`, `ENUM`, `COUNT`, `TIMING`, `PHASE`, `SOURCE`, `DECODER`, `CONSISTENCY` and
their exact source-style field path, such as `captures[0].sample.sequence`.

`valid` means all structural/consistency rules below pass. It does not mean the
native operation succeeded. With two valid byte-identical snapshots, COMPLETE
means frozen=true/acquisition=COMPLETE_128, FAULT means frozen=true/acquisition=FAULT,
and other known phases mean frozen=false/acquisition=NONTERMINAL. Any unequal
bytes or invalid snapshot means frozen=false/acquisition=UNAVAILABLE. Thus a
frozen setup/ADC failure remains a recorded failure, and two equal RUNNING reads
never become terminal. No overall diagnostic PASS or calibrated-time claim.

Compare **all Runner bytes**, including padding, port pointers, unused captures
and private state. Do not interpret those ignored fields as measurements or
require any padding byte to be zero. Equal nonzero padding is allowed; changing
padding makes the pair unstable. This is sampled consistency, not an atomic
snapshot or proof that no future instruction can change a flag.

## Public fields and candidate ABI

All multibyte integers are little-endian. The following offsets are D112 evidence
or explicitly identified derived expectations, not D114 address pins. Every
size/member offset must be reconfirmed against the enabled debug ELF before the
independent literal fixtures freeze. No automatic ABI adaptation at runtime.

The preserved D112 offline GDB output is in
`P2_ui_bench_raw/target_bf67d46d_bench-default_checked/audit.json` (`abi.stdout`).
It directly gives Runner9892, Native32, Report132 at Runner+16, and captures at
Runner+148 with9728bytes/128elements. See `d112_abi_reference.json` for exact
source/artifact hashes and the unmodified GDB text.

| Report-relative offset | Field / extent |
|---|---|
| 0,1 | phase u8, fault u8 |
| 2..7 | fresh, clock_fault, counter_saturated, sample_seen, last_read_accepted, decode_matches_sample; six u8 bool representations |
| 8 | setup: status u8 at0, shutdown u8 at1, ready u8 at2; extent3 |
| 12 | sample: ButtonSample extent20 |
| 32 | decoded: ButtonDecode extent28 |
| 60,64,68 | captured_samples, not_due, missed_releases; u32 |
| 72,92,112 | setup_timing, read_timing, poll_timing; each extent20 |

ButtonSample relative fields: status0:u8, shutdown1:u8, raw2:u16,
started_us4:u32, completed_us8:u32, sequence12:u32, valid16:u8.
ButtonDecode: qualification0:u8, evidence4:ButtonEvidence extent20,
candidate_mask24:u8. ButtonEvidence: explicit_values0:u8, contract_valid1:u8,
presence2:u8, level3:u8, raw4:u16, sequence8:u32, started_us12:u32,
completed_us16:u32. Timing: calls0, measured_calls4, last_us8, maximum_us12
(u32), last_valid16:u8. These nested offsets are directly in D112 GDB output.

Capture's **derived candidate** layout is sample0:20, decoded20:28, then seven
u32 fields: call_started_us48, call_returned_us52, poll_closed_us56, source_us60,
read_us64, poll_us68, missed_before72; stride76. This follows the public field
order (`bench/ui/src/ui_bench.h:31-41`) and actual D112 array stride, but the
enabled audit must explicitly print `ptype /o ui_bench::Capture` as well.

Enum integers are the unchanged public headers: Phase0 NOT_STARTED,1 DISABLED,
2 RUNNING,3 COMPLETE,4 FAULT; Fault0 NONE,1 PORT,2 CONFIG,3 SETUP,4 ADC,
5 CONTRACT,6 SOURCE_ORDER,7 CLOCK. power::Status0..14 and Shutdown0..2 retain
`src/hal/power.h:9-14` order. ButtonQualification0 ABSENT,1 VALID,2 UNCONFIGURED,
3 UNKNOWN,4 AMBIGUOUS,5 INVALID (`src/hal/ui.h:9`); ButtonPresence1 ABSENT,
2 VALID,3 INVALID; ButtonLevel0 NONE,1 START,2 MODE,3 BOTH (`core/types.h:19-22`).
Do not describe integer0/NONE with INVALID presence as a release.

## Minimal consistency checks

- Report and decoded published fields must have known enum domains and bool bytes.
  Count is0..128; COMPLETE requires128 and faultNONE; FAULT requires nonzero fault
  and count<128; other phases have faultNONE/count<128. clock_fault requires FAULT;
  faultCLOCK requires clock_fault. NOT_STARTED/DISABLED have no committed records.
- Each Timing has measured_calls<=calls, last_us<=maximum_us<2^31, and last_valid
  implies measured_calls>0. With measured_calls0, both numeric durations and
  last_valid are0. An unmeasured most-recent attempt may retain older durations;
  do not require last_us=0 when last_valid=0. Counters are not physical durations.
- Validate only the first count Capture records. Each has native OK/valid1,
  NOT_ATTEMPTED shutdown, raw<=16383 and sequence=index+1. Preserve repeated raw
  values and endpoints; no voltage/noise threshold. For modulo-u32 differences,
  `0<=start-S<=completed-S<=A-S<=C-S<2^31`, completed-start<100,
  source_us=completed-start, read_us=A-S and poll_us=C-S. Use unsigned differences
  so natural micros wrap is accepted; never infer a wholly unobserved full wrap.
- First missed_before is0. For later records, the forward age from previous
  sample.started_us to current S is in[1000,2^31), and missed_before=age//1000-1.
  Current S follows previous C within a half-range. Published sequences are
  contiguous; a new128-sample Reader cannot naturally wrap its sequence.
- Each committed decoded result must be the fixed unconfigured profile's actual
  shape: qualification2, explicit_values1, contract_valid1, presence3, level0,
  candidate_mask0, with raw/sequence/start/completion identical to its sample.
  This checks the pinned profile's published evidence; it does not reimplement
  the general window classifier or assign a physical logical level.
- Keep Report.sample and Report.decoded exactly as read. In FAULT/nonterminal
  states do not require them to equal the last Capture, apply success-only source
  brackets to failed native results, or pair them when decode_matches_sample=0.
  Last accepted flags may legitimately remain historical after a bad-S failure.
  A source/clock/contract fault can follow an actual valid native return. These
  diagnostic fields are not silently replaced by the committed prefix.
- COMPLETE additionally requires healthy setup (OK/ready1/NOT_ATTEMPTED),
  clock_fault0, sample_seen1/last_read_accepted1/decode_matches_sample1, latest
  sample/decoded semantically equal to the final capture, setup calls=measured=1
  with setup last_valid=1,
  read calls=measured=128 and poll measured=128. Read/poll last and maximum values
  equal the corresponding committed-record statistics; their last_valid=1.
  poll calls=saturating(128+not_due); missed_releases=saturating sum(missed_before).
  On other phases, missed_releases may include a failed/unpublished final call:
  require only that it is at least the saturated sum of committed missed counts.

No unqualified report duration, failure sample or uncommitted slot is promoted
to a successfully admitted conversion. No attempt to infer frozen-time recovery,
ADC shutdown, IRQ absence, external wiring or calibrated100us from decoded RAM.

## Narrow collector and complete read arithmetic

Keep `p0_capture.py`/`p0_mem_read.cfg` unchanged and pinned. Reuse its pure
`loader_image`, `uint32`, `in_range`, `ram_range`, `require`; its unchanged
`no_symlinks`/`file_hash` may serve file guards. Do not instantiate p0.Capture,
whose16-read/32-command/120s limits differ. D104's collector is a pattern, not a
new inherited runtime policy (`runtime_capture.py:33-38,149-208,245-287`).

Pin one reviewed D114 artifact directory, source/config/ELF/ZSK hashes, actual
debug ABI, tool/helper/config/loader hashes, final BSS size/section and the exact
LOCAL OBJECT Runner symbol. The D112 final ELF symbol is
`_ZN12_GLOBAL__N_16runnerE`, size9892, st_value0x1690 with .bss sh_addr0x1690 and
size0x26a5. This shows why blindly copying D104's raw-st_value offset handling is
wrong for this layout: the candidate section-relative offset is0. Confirm enabled
symbol/section normalization against actual LLEXT relocation semantics, then pin
it explicitly; never guess an address from the old image or silently accept
another mangled symbol. Runner must fit entirely in its verified relocated BSS.
The overall BSS byte size need not be divisible by4 (D112 is9893); only the
actual Runner address/alignment and exact read extent are required. Do not copy
D104's unrelated whole-BSS size/alignment predicate.

Allow only four non-memory commands: pinned OpenOCD --version, readelf --version,
readelf -hSW and -sW for that exact final ELF. Every MEM-AP command is the existing
read-only config plus one purpose-bound dump_image and shutdown; no cortex target,
halt/reset/write, peripheral readout, service operation or arbitrary command.
All exact argv/status/timestamps/stdout/stderr/original binaries remain retained.

After local identity/layout/read-budget checks, perform this finite sequence:

1. Compare deployed loader's full PT_LOAD image and exact ZSK sketch package, in
   fixed64KiB chunks. As in p0.loader_image/D104, loader ELF load bytes are the
   reference; retain the separately pinned package-BIN comparison without assuming
   that package BIN equals the deployed loader image.
2. Read8-byte LLEXT list and at most3 distinct196-byte nodes. Validate bounds,
   links/tail, unique NUL-terminated sketch name, expected BSS size and exact
   symbol range. No cycle, duplicate sketch or unconstrained node traversal.
3. Read the complete Runner twice, each <=16KiB. Save both original blobs before
   semantic decoding. Do not invoke accessor/member functions on the MCU.
4. Read the same list and visited nodes again and require full byte equality,
   including the sketch descriptor's BSS mapping. No allocator/heap scan is needed.
5. Repeat full loader and sketch flash comparisons. Require both identical to
   the same pinned references; no post-read identity change is accepted.

Let L=263680 pinned loader bytes, B=actual D114 ZSK bytes, R=actual Runner bytes,
N=3 maximum nodes, F=65536. Worst-case reads are
`2*(ceil(L/F)+ceil(B/F))+2+2*N+2`; bytes are
`2*(L+B)+16+2*N*196+2*R`; commands are reads+4. For the **D112 baseline only**
B=19840,R=9892:22reads,588016bytes,26commands. Calculate again using D114 pins,
and reject before the first memory operation if any ceiling would be exceeded.
Keep48reads,2097152total bytes,16384per RAM read,64commands,600s total and30s per
command. A command timeout is min(30s,remaining sequence time); count attempts
and requested bytes before execution. No automatic retry, polling wait or budget
extension. Flash chunks have exact indexed addresses/sizes and separate labels
for first/last passes; RAM purposes admit only the fixed list, verified nodes
and the one relocated Runner. No caller supplies memory ranges.

## Collection report and independent acceptance

Collector report retains the existing identity/command/read records, both raw
snapshot files/hashes and decoder result. Add explicit
`collection_integrity: "VERIFIED"|"FAILED"`, `diagnostic: pair result|null` and
`physical_acceptance:false`. VERIFIED requires all planned reads and both flash/
mapping brackets, independently of whether the diagnostic is COMPLETE or FAULT.
Any failed identity, command, read extent or mapping check is FAILED with an
explicit error and retained partial bytes; do not return a frozen result from
unverified mappings. CLI exits0 only for VERIFIED plus valid frozen COMPLETE or
FAULT; otherwise1. A zero exit with FAULT means a frozen failure was collected,
not successful acquisition. Decoder invalidity/nonterminal/instability remains
visible even if byte collection itself was VERIFIED.

Before any implementation execution, an independent author freezes literal byte
fixtures against the confirmed enabled ABI: complete128; setup rejection; partial
ADC/source/clock failure; actual valid sample with bad-A historical decoder;
bad-S retaining previous accepted flags; RUNNING/NOT_STARTED/DISABLED; one changed
field/private byte/unused slot/padding byte; equal nonzero padding; short/oversized
or mutable input; unknown enums/boolean bytes/count; exact source and half-range
boundaries/time wrap; repeated raw0/16383; cadence/missed-count/counter history;
permitted failed native timestamps; and all collector identity/budget/command/
node/address failures. Literal construction must not import decoder offsets as
its oracle. No private seed or hardware execution is needed. Test the unchanged
p0 helper dependency hash and refusal of every unpinned artifact or command.

Next: coordinator confirms D114 target/relocation/ABI and freezes this schema or
explicit revisions; author freezes fixtures; only then implement the narrow
collector. Its implementation and the eventual identified run remain separate.
