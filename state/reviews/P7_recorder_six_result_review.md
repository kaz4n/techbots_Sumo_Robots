# D238 independent diagnostic projection review

**PASS: amended 65-field source and host preparation for this fixed six-store
recorder image.** No material blocker found. Actual ABI extraction and passive
observation remain separate evidence. The earlier 64-field checkpoint is
superseded, preserved in raw evidence, and did not admit a native operation.

Reviewed isolated root:
`C:/Users/narut/AppData/Local/Temp/sumox-recorder-six-result-20260927`.
Historical compile HEAD `1b2af246cd88e6207e846ee340f8c4e46a5bb980`, attempt
`771c04943d4c4a759055d794fa4b706e`, session `8582740024591403637`, source
`289300a4be9547cd294dc1f753bbe17a429d16776c46467fec5417b1290f4ffc`, static/default
recorder.ino, MATCH=0/MOTORS_ALLOWED=0. Package: 55376 bytes, SHA256
`3b4812a7a57ec964437d6d1048f96724e3fed5d0a3f9419acd26adbcd5e70a5d`.
The collector's reviewed clean HEAD is separate from that historical build HEAD.

## Delta and evidence

All three tools independently reverse byte-for-byte to the pinned accepted D233
templates after undoing the recorded substitutions. Direct source diffs contain
only identity, path, module, scope and consequent capture-helper size/hash
changes, plus the two schema additions for packet_started_us. No execution path,
lifecycle, firmware, deadline or existing field layout/guard changed.
All 145 compiled input hashes independently match current files and historical
Git blobs. The four copied compile records match the actual closed native owner
byte-for-byte and match plan.json. Its query inventory is 537 lines: four added
marker/query lines obtain the exact native member offset and extent.

All 193 flat preparation-manifest pins independently match their files.
The eight saved Windows methods pass with zero failures/errors/skips; receipt
stdout/stderr hashes reconcile. Inspection confirms meaningful coverage of full
reverse equality and stale executable identities, all 65 fields/12 windows/nine
types, first-record enum inventory, extent/overlap/width refusals, invalid bool
and enum decoding, real 145-input/110-stage owner construction and real fixed
capture adapter/action/full-flash composition. The construction test disables
native transport; synthetic layouts are not target observations. Unchanged
D230/D233 lifecycle evidence remains the accepted basis, without another broad
suite or duplicated native action.

The same eight-byte first-failure record is retained. File-only extraction has
four bounded offline children and twelve closing file guards. Its fixed readelf
and GDB commands do not attach to or read the MCU. Passive capture retains full
263680-byte loader and 55376-byte sketch comparisons before SRAM and afterward,
two status snapshots, strict decoding, fixed retrieval and closing checks. The
ten-transport bound, descriptor/boot/source/image guards, no-clobber owners and
original/closing-error preservation are unchanged. No prior ABI address fills
a missing fresh observation.

The added packet_started_us window is native_dump.started_us_, exactly one
four-byte uint field, outside the native_* boolean selector. Fresh DWARF offset
and sizeof queries feed the existing initialized-object, width, alignment and
nonoverlap guards. The new fixture rejects a three-byte extent, out-of-object,
misaligned and overlapping offsets, missing window and wrong width/kind; it
decodes zero, packet-scale and near-wrap uint32 values without truncation. Its
synthetic offset is not a target address. Firmware inspection confirms prepare
sets this timestamp at packet start and abort/poison preserve it. Comparison
with retained runner clocks must use modular uint32 arithmetic and source
ordering; it is not the exact failing clock sample and does not by itself identify
which branch of the unchanged shared deadline predicate failed.

## Frozen pins

| File | Bytes | SHA256 |
| --- | ---: | --- |
| recorder_six_result_abi.py | 24902 | 9606ab96576b1cae5382fdd383b5c8c05d7ef3bf5f9469809c7fa97b3954ba8c |
| recorder_six_result_capture.py | 11770 | 2dfd19f72aa913660f8b32b113093047976d03c218bb793a7aa973b0d2765d5d |
| run_recorder_six_result_capture.py | 19593 | b46893c3e6cf7ce258a3eeaf221074770d1d80b64a425ff7058321c9c99114c2 |

- preparation_manifest01.json, 30426 bytes:
  `4cde3692c27d1c86141519ecf2c3ebc921a932355c22f9e95240a1c45905c330`.
- ABI contract, 5406 bytes:
  `fb99e07039fb4f23f919f7ce30adb694f65a08e9df9f800f94a374b3d080aeff`.
- Caller contract, 4193 bytes:
  `df00b8e267b9c27f5beba2c4c1a8c910aad18438f7943c2ec74150c64f380fa5`.
- Validation, 4357 bytes:
  `9a7e908f69225f074c9c7abe81c876309a24b2bee2e02702f8f1f9d79c619928`.
- plan.json, 32689 bytes:
  `bae4e3a971f62ca883153c2e32df51b66c821ad65757d9dcb81907d075c1f1ae`.
- tests02.json, 478 bytes:
  `c37409dcf3303562f8beaf8d94667f35ff0568d632a138593996034e865dbe2e`.

The original seven-method receipt and 14-file checkpoint archive are retained,
along with superseded_64_field_review.md (5034 bytes,
`a24b08885646ee3ef4373401fb9a8f026198cedfb1112456ea4f04b54f9f7a03`).

## Accepted next-action boundary

After exact commit, root may run the contract's file-only check and one execution
from this isolated clean collector HEAD. Since compilation is closed and these
commands only inspect compiled files, they may overlap the bounded receiver
under the recorded D051/D238 scheduling decision. There is no source-level
dependency on delivery completion for that offline step.

Root then accepts the actual ABI and uses its exact hash for the existing
prepare-bindings command. The three mechanically derived absent-only files and
actual ABI evidence are committed before capture check/execute at the resulting
clean collector HEAD. No second source-review chain is needed for those exact
data bindings. Passive MCU capture waits for delivery/receiver closure and may
be omitted if fully validated delivery makes it unnecessary. Failed owners are
consumed; no retry, reset, upload, UART operation or cleanup is added here.

Snapshot coherence remains UNPROVEN even with equal fields. Status and packet
offsets do not prove delivery, acknowledged bytes, deadline branch or cleanup
root cause. No motor permission, timing qualification or phase gate follows.
The reviewer performed local read-only inspection and hashing, no test or native
execution, and wrote only this review file.
