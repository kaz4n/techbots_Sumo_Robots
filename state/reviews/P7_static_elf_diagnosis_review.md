# Proposed D145 one-file diagnostic collection review

25 September 2026. Separate reused-context same-model source/design review.
Read-only inspection of the proposed composition and existing code/receipts;
no collector, runner, helper, transport or compiler execution. Only this review
was written. A concrete collector and separate D145 decision are still pending.

The minimal composition is viable: use unchanged runner
`983e86d7eb68f437c50b4b790e96ca4520e092abe53e4d29e8ffe1a97502b208`
and helper `8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8`
to read the existing D144 final ELF without calling prepare, execute, run_probe,
collect, remote inventory, claim, query or compiler paths. It must not convert the
D144 negative result into successful structural admission.

## Required details before execution

1. **MAJOR if omitted: restore transport admission bypassed by this composition.**
   Runner main lines666-674 checks the exact three SUMO values, ADB absolute
   path/nonsymlink ancestry and executable hash. Probe constructor/dispatch do
   not repeat those checks. `board_tool.remote` lines81-86 instead selects its
   transport from the environment, whose default is SSH; dispatch's BOARD check
   and Windows command-length calculation do not force ADB. The collector must
   perform the same exact main admission before any transport. Any launcher
   supplies/restores only the reviewed transient process environment, with
   Python `-B` and the existing nested-cache guard intact.

2. **MAJOR if omitted: restore local path admission and exclusive claim.**
   Probe construction does not call validate_request or create receipt_dir.
   Reuse runner validate_request/safe_path (or the literal same checks) on the
   fixed fresh diagnostic path before creation. Its parent must already exist
   with no linked/reparse ancestry; mkdir must be exclusive, with no fallback,
   reuse or deletion. Keep Probe.run_id equal to the old D144 run ID; use a
   distinct local diagnostic directory, never write into the original run.

3. Pin and decode captured bytes from the three exact D144 receipts before
   assigning first_identity, claim and files. Validate completed receipt identity
   and success, exact helper envelope/action/run ID, inventory schema/identity,
   claim boot/directory IDs and all eight typed FileRecords through unchanged
   functions. Admit only the original run
   `f0220228320c4b2aa20c3e5e8264c813` and exact ELF170616 bytes/SHA256
   `5cc2dfdec597f1421d6250936569bc113542723c362786f23be62834b5ba0386`.
   No caller-selected source, run, path, length or hash.

4. Bind the collector's own reviewed source before use; load the runner from
   captured hash-verified bytes with its real __file__, then verify all17 inputs
   and use unchanged module loaders/Probe construction. Local pin/stage checks
   run before the read and independently afterward, including a failed read.
   A later check/receipt failure must not replace the original exception. Preserve
   compact local admission/input, single command and success/failure evidence.

5. Invoke read_elf exactly once, retain its unchanged dispatch/helper and60s
   timeout, and require zero query/compile attempts and one read dispatch on the
   success path. The admitted size is below262144, so its existing loop makes
   exactly one chunk request. No retry or additional remote check follows any
   outcome. Save the complete returned ELF exclusively only after unchanged
   length/hash checks and successful local postchecks. Name the result as
   diagnostic collection, not STATIC_LAYOUT_PACKAGE_PASS or probe acceptance.

## Existing read protections and evidence binding

Runner read_elf lines576-593 already binds returned Claim, full typed FileRecord,
filename, offset/length, canonical base64 and both chunk/full-file SHA256. Helper
claimed lines444-467 verifies current boot plus existing run/build/artifacts
directory identities and ownership through descriptor traversal. read_action
lines620-634 verifies a stable nonempty regular final ELF, the requested full
hash and remaining chunk extent, then observes it again before returning bytes.
It creates no remote directory and runs no subprocess or validator. The host's
FileRecord comparison rejects replaced files even when their content hash agrees.

Required historical receipt hashes, independently rechecked under
`P7_static_link_probe_raw/runs/f0220228320c4b2aa20c3e5e8264c813/`:

| Receipt | SHA256 |
|---|---|
|0001.json|`534da2e8de0d846d850288c956f3c5a51b13f641b3329c6475dc5857930f32a7`|
|0009.json|`3f57a292649a0d20ddf88daf3f80a8b3d75a90e18460f3c7208c1eb17c6b45d4`|
|0021.json|`c44e85bcb22dcb69c405b1bddeea74f7c30e4c9e3f1444370995f806162e3127`|

No additional framework or relaxed parser is necessary. Review the concrete
collector's exact branch/argv and original-error handling before its scoped GO;
the two omitted-entry-point guards above must be explicit. This plan alone is
not execution authorization. The resulting bytes, if collected, would support
local diagnosis only; D144 remains STRUCTURAL-VALIDATION-REJECTED, with no new
compile, admission change, fit/runtime result, upload/reset or human gate.

## Concrete composition inspection

Reviewed `P7_static_elf_diagnosis_plan.md`, 6,075 bytes, SHA256
`35cfd40b83f4403cc10b6616d01e3576b81cc6a3b97cb4eac093aecf0dc317b1`.
Lines43-47 restore exact process-local ADB settings, nonsymlink path and executable
hash before loading unchanged board.remote. Lines49-51 and73 restore canonical
fresh local path admission and exclusive creation. **Both omitted-entry-point
findings are closed by inspection.** A dedicated Python process contains the
three environment changes; no shell/persistent configuration is changed.

The composition pins historical receipts, validates the retained identity,
Claim and eight typed FileRecords, fixes the old run and exact ELF identity,
invokes only read_elf, performs independent local postchecks and an additional
runner-source check, preserves the original read error if later checks/result
write fail, and saves exclusively only after all checks succeed. It permits no
query/compiler, remote claim, inventory, layout or retry. Its success status
explicitly denotes diagnostic byte collection.

**MAJOR, open: source admission uses removable assertions.** Plan lines31,32,37
use Python assert for repository, -B and, critically, the runner hash immediately
before exec at40. An inherited PYTHONOPTIMIZE setting removes these assertions;
-B does not disable optimization. Replace all three with unconditional if/raise
checks before exec. This is a small correction to the fixed-source admission,
not a new framework or parser expectation. No execution occurred for this review.

## Fixed admission closure

Re-read plan SHA256
`5f52f30631fe07d5ecaa0105e46f1b08293421f2d9ae4e10380232e72fed8de9`
(6,210 bytes). Lines31-40 now use unconditional if/raise ValueError checks for
repository, -B and exact runner bytes before exec at43. No assert statement
remains in the literal composition. The source-binding finding is **closed by
inspection**; the remaining composition is unchanged.

**No open material composition finding remains.** The exact plan is suitable
for a separate coordinator D145 authorization of this one diagnostic read.
This review does not execute it or issue that authorization. Existing tested
functions remain unchanged; any collected bytes must match the fixed historical
FileRecord/hash and retain D144's negative structural outcome.
