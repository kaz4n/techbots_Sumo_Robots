# D144 native static attempt: negative result review

25 September 2026. Separate reused-context same-model review of retained local
receipts only; no transport, helper, compiler, upload/reset or implementation
execution by this reviewer. This is an evidence review, not a phase gate.

**Disposition: TARGET-COMPILED / STRUCTURAL-VALIDATION-REJECTED.** The single
authorized run `f0220228320c4b2aa20c3e5e8264c813` stopped correctly. No material
inconsistency was found in the retained result. Structural admission remains
blocked by D142's `unsupported symbol encoding` rejection. These receipts do
not establish which symbol caused it, whether the artifact is otherwise valid,
static fit, native ABI/binding compatibility or runtime behavior.

Evidence directory: `state/analysis/P7_static_link_probe_raw/runs/f0220228320c4b2aa20c3e5e8264c813/`;
launcher captures are in its `.launcher` sibling. There are25 numbered command
receipts and no local `app.ino.elf` or ELF-read command.

## Verified boundaries and identities

- Recorded runner `983e86d7eb68f437c50b4b790e96ca4520e092abe53e4d29e8ffe1a97502b208`
  and helper `8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8`
  match current bytes and launcher before/after hashes. All17 recorded local
  input pins match; transmitted helper and D142 validator bytes also match.
- Source digest is `fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2`.
  The102 local stage files match their frozen hashes; both source observations
  and both postchecks match every name/hash/byte count (753,087 bytes total).
  The input receipt retains the D139103-source/102-stage verification.
- Inventory records user arduino/UID1000, Linux aarch64, Python3.13.5, boot
  `6d4aca1b-ac1f-4caf-b1ef-e127ce3956f6`, adequate declared floors and no compiler
  candidates. Claim IDs remain device66341, run inode267649, build267650,
  artifacts267651. All eight destinations were absent before query and compile.
- `0011` query and `0017` compiler return0 with success=true and empty upload
  results. Their exact argv retain static/MATCH0/MOTORS_ALLOWED0, jobs1, the
  authorized source and unique run paths. Both sets of84 controlled properties
  independently match the frozen reference after the two path substitutions.
  All four26-pin responses match the exact18+8 map and argv order.
- `0018`-`0020` terminal postchecks pass. `0021` observes eight regular files.
  `0022` returns2 with ok=false, `LAYOUT_REJECTED`, message
  `unsupported symbol encoding`, validator
  `d30372dd4b8fb8c2661d00affc4a215cc88e3f62511995ff6303827bed4b7368`, and report=null.
  Its complete FileRecords equal those in artifacts and both postchecks,
  including device/inode/size/timestamps/hash.
- Required final checks `0023`-`0025` pass. Result is FAILED, phase layout,
  query_attempts=1, compile_attempts=1, postcheck_errors=[]; the primary error is
  the actual layout CalledProcessError. Launcher exit1, no launch/hash-read error.
  The25 recorded commands contain no retry, upload/reset or cleanup.

## Observed artifact identities

These are the reviewed remote observations, not locally downloaded artifacts.
Names below are under this run's `build/`, except the selected export.

| File | Bytes | SHA256 |
|---|---:|---|
| app.ino.elf |170616|`5cc2dfdec597f1421d6250936569bc113542723c362786f23be62834b5ba0386`|
| app.ino_debug.elf |1764708|`0f7f2825329466e06f15144f07a5188435ac309aa1a3aff71a1a9f1be87a27bd`|
| app.ino_temp.elf |1764708|`0f7f2825329466e06f15144f07a5188435ac309aa1a3aff71a1a9f1be87a27bd`|
| app.ino.bin |93080|`bd03c2e7ff19e599f78f4e1c1861e6216ad88f949b009b4b7c93070028f704ed`|
| app.ino.bin-zsk.bin |93096|`5f08afe0fc2d261b093644f6bca6720182c277009d00e646207151e7f940629a`|
| app.ino.elf-zsk.bin |170616|`1794da3ded9cf602f1f21407357f5076fa8c45d7d6cb51d933499afeeff959ed`|
| app.ino.map |666298|`15da1417d5a7f781195d86ba1554dd449e4e14548dde1ea8052e8da78cd16806`|
| artifacts/app.ino.bin-zsk.bin |93096|`5f08afe0fc2d261b093644f6bca6720182c277009d00e646207151e7f940629a`|

Key receipt hashes: result.json
`bc5271822efc54deb4f2d84540d3fea39444403a5a1ac8f31263be9b427bbd17`;
0017.json `3c8cc9df2256be9967dd71b1afa3ec22215dbfc92cdcd910823efc4eeb78d6df`;
0022.json `842455da012dc9562aa25a6fd3e124eaa4ad00c9b9b764458109deeca4f65c44`;
launcher completed.json
`a54d27f7ae0fa6fb94354eabe59087dba70c08477fc180eb7728601ea0605408`.

The observed rejection ends D144's one-attempt authority. Preserve all originals;
further diagnosis, parser/contract changes or another compilation require a
separate scope. No repair, additional board read, adoption or phase pass is
recommended by this result review. D139's592-byte dynamic deficit is unchanged.
