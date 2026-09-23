Adopted readout software contract under D114 at 2026-09-24T02:05:42.112669+04:00.
Root inspected the confirmed enabled ABI, public schema and bounded command
plan; independent public preflight preceded the API clarifications. This
adoption supersedes draft-status wording in the preserved proposal below only.
Independent fixtures must freeze before execution; no upload/run is granted.

# D114 readout contract proposal

Draft only, 2026-09-24. No decoder implementation, test execution or board action.
This specializes the adopted `P2_ui_adc_probe_contract.md`; no run/upload key is
authorized here. The coordinator selected the full flash checks before/after
below. The enabled target and public decoding ABI are now bound below; adoption,
independent fixtures, implementation review and any identified run remain separate.

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
phase/count, then capture index/field and cross-record consistency. Diagnostics
are ordered, non-exhaustive and deduplicated by(code,path): a failed prerequisite
may suppress dependent checks, but each invalid snapshot has at least one error. Use codes
`BOOL`, `ENUM`, `COUNT`, `TIMING`, `PHASE`, `SOURCE`, `DECODER`, `CONSISTENCY` and
their exact source-style field path, such as `captures[0].sample.sequence`.
Wrapper S/A/C chronology is TIMING at `captures[i]`; inconsistent source_us is
SOURCE at `captures[i].source_us`. Unknown enum and boolean errors use the exact
field path; count errors use `report.captured_samples`. Do not require an
exhaustive duplicate/cascade list in tests.

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

## Public fields and confirmed enabled ABI

All multibyte integers are little-endian. The actual enabled target audit is
`P2_ui_adc_probe_raw/target_396bcc45_bench-default_checked/audit.json`, SHA256
`369d535afcb8ee9c905dd0addf92dc912ddaa7a08395467717fa850c9d889a10`.
Its96-source digest is
`396bcc45fbaf30d38b170bf0c0063c555d5e88cdad512829b86a52ffede18642`;
receipt is `73d13df1e7244ddc8a71d1a7e52c0ed8`. The captured offline GDB command
exited0 and explicitly printed Runner/Report/Capture/ButtonSample/ButtonDecode.
`d114_enabled_abi_reference.json` preserves that unmodified command/output,
artifact/tool identities, direct raw ELF symbol extraction and full read arithmetic.
No automatic ABI adaptation at runtime.

The enabled ELF confirms Runner9892, Native32, Report132 at Runner+16, and
captures at Runner+148 with9728bytes/128elements. The retained
`d112_abi_reference.json` and `readout_contract_proposal_before_enabled_binding.md`
are superseded baseline evidence, not enabled pins. In particular, their initial
nm/st_value wording is explicitly corrected in the symbol section below.

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
(u32), last_valid16:u8. These nested offsets are directly confirmed in enabled GDB output.

Capture's **directly confirmed** layout is sample0:20, decoded20:28, then seven
u32 fields: call_started_us48, call_returned_us52, poll_closed_us56, source_us60,
read_us64, poll_us68, missed_before72; stride76. The enabled audit explicitly
printed `ptype /o ui_bench::Capture`; it agrees with the public field order
(`bench/ui/src/ui_bench.h:31-41`).

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
LOCAL OBJECT Runner symbol. Actual ELF32 raw symbol bytes give
`_ZN12_GLOBAL__N_16runnerE`, st_value0, size9892, st_info1(LOCAL OBJECT),
st_other0(DEFAULT), st_shndx8. Section8 is .bss/NOBITS, sh_addr0x1690,
sh_offset0x19d8, size0x26a5(9893), alignment4. **Use raw st_value0 directly as
its section-relative offset; do not subtract sh_addr.** nm displays0x1690 because
it adds the section VMA; the earlier draft incorrectly labelled that display
as st_value. Both earlier files remain intact as explicitly superseded evidence.

Pinned source `P2_memory_validation_raw/llext_load.c:47-55,457-469,756-782`
(commit1743741760ee; source SHA256
68c999737ed275a4bb81801d571fc044a2db0ef760d21214d9a34b4f7b388413)
uses relocated section base+raw st_value for ET_REL, subtracting section address
only for ET_DYN. Its region map has one BSS, aligned file offset and zero prepad
for this image. This agrees with the installed-loader ABI recorded in
`P0_installed_debug_contract.md:190-234` and the prior exact ET_REL audits
`P0_gpio_binary_audit_20260923.md:26-39` and
`P0_qtr_binary_audit_20260923.md:89-99`. No live address is asserted: after full
loader/sketch identity, runtime address is verified sketch BSS base+0.

The overall BSS byte size need not be divisible by4; only the actual Runner
address/alignment and exact read extent are required. Require exactly the
pinned raw symbol/section layout, not an arbitrary fitting replacement.

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
`2*(L+B)+16+2*N*196+2*R`; commands are reads+4. The **enabled D114**
B=19840,R=9892 gives22reads,588016bytes,26commands. Recalculate from exact pinned
file sizes, and reject before the first memory operation if any ceiling would
be exceeded.
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

Next: coordinator adopts this enabled-bound schema and public seams below;
author freezes independent fixtures before their implementation execution.
Implementation review and the eventual identified run remain separate.

## Frozen collector API, CLI and test seams

The one proposed module is `tools/ui_adc_capture.py`. Import is passive; there
is no CLI option to change a pin, address, read budget, source, command or timeout.
Public callables are:

```python
decode_runner_pair(first: bytes, second: bytes) -> dict
Capture(folder: Path, report: dict)
Capture.run(argv, attach=False) -> str
Capture.read(label, address, size, region='ram') -> bytes
check_identities(capture, artifact_dir) -> tuple[Path, Path]  # ELF, ZSK
read_layout(capture, elf) -> dict
collect(capture, artifact_dir) -> dict  # same report object, populated
main(argv=None) -> int
```

`Capture` construction initializes counters/deadline and command/read arrays;
it does not launch a process or read memory. `run` accepts only the four exact
metadata argv or the internally armed single MEM-AP command for the current
read. `attach` never means Cortex attach. Direct arbitrary argv fail before
subprocess invocation. `read` requires one currently admitted purpose with
the exact expected address/extent, cannot repeat a consumed purpose, and retains
its requested range and every partial file on failure. Calls out of the finite
sequence fail before invoking a command. Public methods are not authorization
to override private execution state; independent tests may substitute
`subprocess.run`/clock/filesystem functions to exercise actual validation without
hardware. The constructor has no injected runtime transport/callback framework.

`check_identities` validates exact directory and files, records hashes and full
worst-case plan, then runs the two version commands. `read_layout` runs the two
ELF commands and returns/stores exactly the pinned layout described below;
both raise ValueError for violated contracts. `collect` performs these calls
and the five finite stages above, then decodes both original Runner blobs and
returns the same report. On incomplete collection it raises, retaining report
progress and files; it never resumes at a later stage. OSError/subprocess failures
are also retained by the command/read records and propagated. `main` writes the
final success/failure report even on a collection error after output creation.

CLI is `python3 tools/ui_adc_capture.py --artifact-dir EXACT [--output DIRECTORY]`.
The artifact argument is required and must exactly equal ARTIFACT_DIR. No
positional address or additional mode. `--output` follows unchanged p0 rules:
fresh direct child of `/home/arduino/sumox26-capture`, name matching
`[A-Za-z0-9][A-Za-z0-9_-]{0,95}`, no symlink ancestry, exclusive0700 creation.
If omitted, generate `ui-adc-<UTC timestamp>-<PID>` under that root. Existing
directories refuse; no overwrite/reuse/retry. Argument parse errors exit2,
otherwise main returns the collection exit0/1 defined above and prints the
JSON report containing the output directory; original `capture.json`, command
stdout/stderr and all memory blobs remain in that directory. Error text is
diagnostic, not a stable exception-message oracle.

Top-level constants are literal pins. `PINNED_LAYOUT` has exactly:

```python
{'bss_section': 8, 'bss_address': 5776, 'bss_file_offset': 6616,
 'bss_size': 9893, 'bss_alignment': 4,
 'symbol': '_ZN12_GLOBAL__N_16runnerE', 'symbol_value': 0,
 'symbol_size': 9892, 'symbol_binding': 'LOCAL',
 'symbol_type': 'OBJECT', 'symbol_visibility': 'DEFAULT',
 'runner_offset': 0, 'report_offset': 16, 'report_size': 132,
 'captures_offset': 148, 'capture_stride': 76, 'capture_count': 128}
```

`read_layout` requires ELF32/little-endian/ARM/ET_REL, exactly one .bss and one
exact Runner symbol, and all listed values. This is an image-specific check,
not a general ELF loader. `LIST_ADDRESS=0x200017bc`, list length8, head+0/tail+4;
`NODE_BYTES=196`, next+0:u32, name+4:16 bytes with a NUL, BSS pointer+32:u32,
BSS size+92:u32. `SRAM=(0x20000000,0x200c0000)`; node/list/Runner addresses are
4-byte aligned, nonempty extents wholly contained without uint32 overflow.
Only nodes reached from the admitted head/previous next may be read, at most3;
unique addresses, null termination, tail equals last visited, exactly one name
`sketch`, and its BSS size9893 are mandatory. Record each first node verbatim;
the second pass reads those same addresses, never follows newly supplied links.

Purpose labels, with an integer index formatted as two decimal digits for flash:
`loader-before-00`..`04`, `sketch-before-00`, `llext-list-before`,
`node-before-1`..`3` (only actual reachable nodes), `runner-first`, `runner-second`,
`llext-list-after`, the same `node-after-1`..`3`, then
`loader-after-00`..`04`, `sketch-after-00`. Regions are only `loader`, `sketch`,
`ram`. Flash bases are respectively0x08000000 and0x08100000; each offset is
index*65536 and each size is min(65536,total-offset). First successful full
flash comparison admits private RAM; complete identical descriptor and final
flash comparisons admit collection integrity. No failed-read purpose is reusable.

`ARTIFACT_DIR` is the literal absolute path
`/home/arduino/sumox26-capture-input/ui_adc_probe_396bcc45fbaf30d38b170bf0c0063c555d5e88cdad512829b86a52ffede18642`.
Require both `ui_adc_probe.ino.elf` and `ui_adc_probe.ino.elf-zsk.bin` in that
directory, each19840bytes and respectively SHA256
`76e23fe03631d5cc2144578d35ca78b9bafd44158e0d18b2ab026922e4c9d05b` and
`567fb90da6965cf74efc5ac2221e543d6d2150e3bf70ddae3e2346e6646c7fb9`.
The audit collected ELF from the unique receipt `/build` and ZSK from its
`/artifacts`; the coordinator will explicitly create this new two-file input
directory with copy/hash receipts and no overwrite. Neither existence nor a
completed copy is claimed here. No implicit fallback or source lookup at runtime.
Debug ELF SHA256 is
`7544d2477751f099ecd43c1779cef05376ca73a4a3fa946c5b20bf682dae8781`;
it proves this offline ABI, and is not needed for runtime memory reads.

`EXPECTED_HASHES` includes the unchanged p0 OPENOCD/HELPER/LOADER/LOADER_ELF/CONFIG
path/hash entries verbatim, plus READELF at its pinned tool path with SHA256
`c37462dcd380ae1039eb8a0aab379a619415e1100472291ffea2eae34161092e`, and sibling
`p0_capture.py` SHA256
`885c4e4206aea4ac9e03c4e92e48258db2a0ae302ff83a86430e6913afeeb57c`.
Every file/path is checked before any command. Runtime code imports p0 but does
not import or require runtime_capture/recorder_heap. The literal `MAXIMUM_READ_PLAN` is
`{'reads':22,'bytes':588016,'commands':26,'extension_nodes':3}`. Constants keep
the exact limits48/2097152/16384/64/600.0/30.0/65536/3 listed above.

Independent author may freeze the pure decoder suite separately after schema
adoption and the collector suite after these public seams/pins are adopted.
Each suite must freeze before its first execution against implementation; neither
uses implementation-derived fixture values. No split freeze authorizes a board run.

## Collector boundary clarification before collector test freeze

Require the entire declared BSS extent, as well as the Runner extent, to fit
within SRAM without overflow. Its size need not be divisible by4; its base is
4-byte aligned. A fitting Runner does not excuse an out-of-range trailing BSS
byte. Public collect/Capture substitutes may isolate main CLI reporting tests;
actual collector/read validation is exercised separately without private seeds.
