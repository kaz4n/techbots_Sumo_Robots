# D176 closed inert diagnostic capture contract

Scope: host implementation/tests only in existing capture_remote.py. No native
call, firmware change, upload/reset, new run permission or historical repinning.
Keep collect(), checked_bindings(), all default/static run01/run02 behavior and
module globals unchanged. Reuse descriptor ownership, one_read, process/stream
limits, pause, final checks and cleanup; do not clone a launcher or traversal.

New public API:
collect_motor_fault(helper, relocation, loader_image, *, fs_root=Path('/'),
                   executor=None, clock=None, sleeper=None, bindings=None,
                   run_id='motor-fault-8f592937-run01')
relocation is the real tools/runtime_capture.py module; reuse its find_bss(adapter,
2632), not its collect entry or heap decoder. No firmware snapshot decoder runs
inside this API. The caller later binds all dependencies and decodes saved bytes
locally with tools/motor_fault_decode.py. No arbitrary plan/address/config override.
Only exact built-in str run_id above; any other identifier fails before ownership.
Existing collect cannot admit the diagnostic profile.

Binding shape matches legacy capture exactly: schema,run_id,source_sha256,boot_id,
uid,output,files,loader_image. Fixed schema=fixed-motor-fault-capture-v1, source=
8f592937961a0c95b7cc4db88617169fcc9504644aa8b8b7dcf62f83c4c33f36, uid1000,
output=/home/arduino/sumox26_codex_build/motor-fault-8f592937-run01-capture.
Boot syntax/type unchanged. Pin shapes/hash checks and detached JSON copy remain.
Five file roles/paths fixed:
- openocd: /opt/openocd/bin/openocd
- config: /home/arduino/sumox26-capture-tools/app-default-beeffff315b2e28a95a20dc1e26477fc924b2da26d1fdd8a8b36fb013ca110e1/p0_mem_read.cfg
- swj: /opt/openocd/share/openocd/scripts/target/swj-dp.tcl
- loader: /home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf
- sketch: /home/arduino/sumox26_codex_build/motor-fault-active01/_app_builds/native-app-v1/8f592937961a0c95b7cc4db88617169fcc9504644aa8b8b7dcf62f83c4c33f36/bench-default/3aafdd0129f64799b4db51efe78e5c44/build/motor_fault.ino.elf-zsk.bin
Derived loader_image exact extent263680B, sketch29836B. As for existing loader
upload, actual byte/hash pins are checked but supplied by a separately reviewed
native caller; controlled fixtures may substitute matching finite bytes. This
profile alone proves neither production artifact origin nor run permission.

Admit identity/allfive files/derived loader/process conflicts, then claim a fresh
exclusive consumed directory. Admission failures never create a directory or
launch a child. Never mutate caller bindings or shared module globals. Receipt
schema prefixes motor-fault-capture-attempt-v1 and motor-fault-capture-result-v1;
source/run consistently diagnostic. Preserve existing top-level report fields and
statuses. Attempt plan is this literal finite summary (not caller-configurable):
{'profile':'motor-fault-v1','max_reads':24,'max_requested_bytes':593424,
 'loader_bytes':263680,'sketch_bytes':29836,'bss_bytes':2632,
 'snapshot_bytes':2592,'extension_nodes':3,'sample_gap_seconds':2}.
Per-read command/result schema, filename prefix and passive argv shape unchanged.

Read sequence, successful names and bytes:
1. before.loader.0..4 from0x08000000, each65536B except final1536B;
   before.sketch.0 from0x08100000 for29836B. Compare full assembled images to
   checked references before ANY SRAM access. On mismatch fail immediately.
2. relocation.find_bss via a private adapter; expose report flash_identity_verified
   True only after those comparisons. Prefix reads before.llext-list (8B at
   0x200017bc), before.node-1..3 (196B each), before.llext-list-confirm (8B).
   Reuse real traversal for bounded aligned SRAM/cycle/nul-name/one-sketch/tail/
   expectedBSS/list-confirm semantics. Additionally require selected BSS base
   aligned8. Adapter permits only these names/types/sizes and expected read order,
   SRAM-bound nodes; no arbitrary read surface. Retain all traversal raw receipts.
3. first.diagnostic at BSS+0 for2592B; existing checked2second pause; then
   second.diagnostic at SAME address for2592B. No partial-field or heap reads.
4. Repeat traversal with after.* prefixes. Require entire ordered read sequence
   (address and raw bytes, including both list samples and every node) and selected
   extension metadata identical to before. After mismatch fail without extra reads.
5. after.sketch.0 for29836B, then after.loader.0..4 as above; require complete
   flash images equal checked references. Changed bytes fail the capture.

For N=1..3 nodes in BOTH matching traversals, successful exact counts are
commands=reads=18+2N and requested_bytes=592248+392N (max24/593424).
Failed launch attempts count against ceilings. Check command/byte ceiling before
launch; never exceed ceiling even if a supplied traversal misbehaves. Addresses
and sizes must match named flash segments, exact list/node or selected snapshot
regions. Existing30s child/600s total, <=65536 flash and <=2592 SRAM limits remain.
Traversal cannot request a fourth node or exceed three nodes per pass. One failed
read aborts further collection; preserve raw streams/partial files/first error
and still run independent final file/identity/owned-directory checks.

For diagnostic analysis use exact keys schema,flash,relocation,snapshots,coherence:
- schema='motor-fault-capture-analysis-v1'; coherence='UNPROVEN' always.
- flash keys before_loader,before_sketch,after_loader,after_sketch, bool flags;
  initialize False, set each from actual full comparison.
- relocation keys before,after: initiallyNone, then detached real find_bss extension
  record {node_address,bss_address,bss_size,visited_nodes} after successful traversal.
- snapshots: list of successful first/second diagnostic read metadata, same shape
  as report['reads'] entries (name,address,bytes,sha256,file); raw files always kept.
Retain partial analysis on failure. COLLECTED requires full finite sequence,
matching flash/relocation, two snapshots, exact N-derived counts and no first error
or failed final checks. It means only successfully gathered structurally bound
raw observations; no terminal/success lifecycle predicate or decoder execution.
If a later decoder rejects, all raw evidence remains unchanged. Different two
snapshot contents alone are permitted; matching contents do not prove atomicity.

Independent tests before first execution: 1/2/3-node successful paths and exact
sequence/counts; eight-byteBSS alignment; all traversal faults and changed node/
list/relocation/flash; no private read before fullflash match; fixed bindings and
ownership/isolation; count/byte ceilings even failedcalls; two snapshot raw retention
on later failures and offline decoder success/rejection; time/stream/final-check
failure paths. Use real find_bss with crafted node bytes and existing descriptors,
not an all-success traversal mock as sole evidence. Keep all established tests
unchanged; legacy static suites run, historical consumed hash mismatches retain
original failing status/disposition rather than repinning. No native calls.
