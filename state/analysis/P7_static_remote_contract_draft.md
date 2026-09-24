# Proposed fixed remote actions for the static/M0 probe

25 September 2026. **Design only; no implementation or execution authority.**
This narrows the [runner proposal](P7_static_runner_proposal.md), preserves the
frozen [parent](P7_static_link_probe_contract.md) and
[D142 interface](P7_static_artifact_contract.md), and leaves production admission
and D139's 592-byte dynamic deficit unchanged. Only this draft was written.

## Invocation and immutable inputs

Propose one small standard-library Linux I/O helper, `static_remote.py`, whose
reviewed UTF-8 source bytes are `H`. Every call uses the unchanged
`board_tool.remote('2629958581', argv, capture=True, timeout=T)`:

```text
python3 -I -B -c H ACTION RUN_ID [ACTION_ARGUMENTS]
```

`H` is one argv element read from the locally hash-pinned helper, not shell text
assembled from inputs. Python's `-I -B` prevents local-module/environment imports
and bytecode writes. No implicit/default action, stdin program, arbitrary path,
command, profile, build flag, validator callback, or helper-side subprocess API.
The helper never compiles, queries CLI properties, uploads, resets or deletes.
Those two permitted CLI operations remain explicit runner argv from the proposal.
No source/module is installed or written remotely by this interface.

`RUN_ID` is exactly 32 lowercase hex digits. Constants are:

```text
SOURCE = fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2
R = /home/arduino/sumox26_codex_build
S = R/SOURCE/app
U = R/_app_builds/static-app-probe-v1/SOURCE/bench-default/RUN_ID
B = U/build
A = U/artifacts
```

The helper pins the exact D139 stage manifest SHA
`56ab12b990ebe664941677e29dfef783197bc98c3a9de1985b54d57bb30da56a`.
The runner supplies its exact bytes as one canonical RFC4648 base64 argv element
`M`; the helper verifies that literal hash before JSON parsing. `M` is data, not
an authority to accept another source. Its exact 102-file map and literal SOURCE
must agree. The runner separately retains the unchanged D139 local verifier and
its 103-source/102-stage checks and all local pins from the existing proposal.

For `layout`, `V` is canonical base64 of the unchanged D142 module bytes, pinned
inside the helper to
`d30372dd4b8fb8c2661d00affc4a215cc88e3f62511995ff6303827bed4b7368`.
After checking those exact bytes, load them into a fresh module namespace and
call only its public `validate_artifacts(dict[str, bytes])`. Do not rewrite,
normalize, patch globals or replace its error behavior. This sends approximately
one small source module, not encoded artifact contents. The D142 contract hash is
`b6a18e4d27e500d6306587141cbb27bcd7e546ce9bb507f148f28591634bec54`.
The runner must add both D142 hashes and the newly reviewed helper's literal hash
to its fixed local authority before any future execution. A helper hash is not
available until implementation/review; this draft does not invent one.

## Common response and path rules

Each action emits exactly one UTF-8 JSON object followed by LF; no banners or
progress on stdout. The exact envelope is:

```json
{"schema":"static-remote-v1","action":"ACTION","run_id":"RUN_ID",
 "ok":true,"data":{},"error":null}
```

Failure keeps the same keys, sets `ok:false`, and supplies
`error:{"code":"CODE","message":"text"}`; `data` retains completed action
observations. Exit 0 requires `ok:true`; validation/operational rejection exits
2. Unexpected exceptions exit 3 with a complete traceback on stderr and an
`INTERNAL_ERROR` envelope if emission remains possible. Invalid JSON, duplicate
keys, nonfinite numbers, extra/missing schema fields, wrong types (including bool
as integer), wrong action/run identity or status/return-code disagreement fail
at the runner. A successful helper has empty stderr. Successful layout JSON is
bounded to 1 MiB; exceeding it is `REPORT_LIMIT`, never truncated success.
The closed error-code set is `BAD_REQUEST`, `IDENTITY`, `RESOURCE_MINIMUM`,
`PROCESS_INSPECTION`, `COMPILER_PRESENT`, `PATH`, `SOURCE_SET`, `SOURCE_DRIFT`,
`CLAIM_EXISTS`, `CLAIM_INCOMPLETE`, `OUTPUT_PRESENT`, `ARTIFACT_SET`, `FILE_READ`,
`LAYOUT_REJECTED`, `POSTCHECK_FAILED`, `REPORT_LIMIT`, `INTERNAL_ERROR`.
Unknown codes are malformed responses. Failed manifest/module literal hashes
are `BAD_REQUEST`; unsuccessful claim-handle comparisons are `PATH`.

`DirId` is exactly `{device:int,inode:int}`. `FileId` is exactly
`{device:int,inode:int,bytes:int,mtime_ns:int,ctime_ns:int}`. Sizes are nonnegative;
device/inode values are nonnegative integers. Metadata is replacement detection,
not proof of provenance. `Claim` is exactly
`{run_id:str,boot_id:str,directories:{run:DirId,build:DirId,artifacts:DirId}}`.
Its canonical JSON/base64 representation is `C`; it is an observed handle, not a
bearer permission. Every later run action checks C against the actual directories
and current boot ID. The runner accepts C only from its own successful claim.

Walk each path component from `/` with directory descriptors and no-follow opens;
use descriptor-relative operations for enumeration, mkdir and files. Reject
symlinks, nondirectories, path escape and identity changes; do not rely on a
single `resolve()` followed by pathname access. Files require no-follow open,
regular-file fstat and stable FileId before/after reading; recheck that the
directory entry still names the same inode. Never follow an artifact/source
symlink or read a FIFO/device. U/B/A and newly created parents belong to the
effective user; creation mode is 0700. Existing fixed ancestry must be directories
without symlinks; `/home/arduino` and R must belong to the `arduino` account.
An unknown/failed observation is a rejection, not an empty success.

## Public actions and data schemas

The timeout below is the outer transport timeout in seconds, not a promise that
remote work has ended when the local wait expires.

| Action and exact trailing arguments | T | Operation and exact success `data` |
|---|---:|---|
| `inventory RUN_ID` | 30 | `{identity:Identity,resources:Resources,compiler_candidates:[]}` |
| `source RUN_ID M` | 60 | `SourceCheck` |
| `claim RUN_ID` | 30 | `{claim:Claim,created:[absolute paths in creation order]}` |
| `absent RUN_ID C` | 30 | `{claim:Claim,outputs:{OutputKey:"absent" for all eight}}` |
| `artifacts RUN_ID C` | 60 | `{claim:Claim,files:{OutputKey:FileRecord for all eight}}` |
| `layout RUN_ID C V` | 120 | `{claim:Claim,validator_sha256:str,files:{OutputKey:FileRecord for all eight},report:D142Result}` |
| `read RUN_ID C NAME OFFSET LENGTH SHA256` | 60 | `{claim:Claim,name:str,file:FileRecord,offset:int,length:int,chunk_sha256:str,base64:str}` |
| `postcheck RUN_ID C M` | 90 | `{claim:Claim,identity:Identity,resources:Resources,compiler_candidates:[],source:SourceCheck,files:{OutputKey:FileRecord for all eight}}` |

There are no other arguments. Every action validates its whole argument list
before filesystem mutation. All SHA256 strings are 64 lowercase hex characters;
decimal integer argv uses canonical unsigned decimal, with no signs/whitespace.
Duplicate invocations do not gain permission for another query or compiler.

`Identity` is exactly `{user,uid,gid,home,sysname,release,machine,boot_id,python}`:
strings except uid/gid, and `python` is a three-integer version list. Require
effective account `arduino`, home `/home/arduino`, nonroot uid, `sysname:"Linux"`,
Python >=3.9 and a valid kernel boot UUID. Record release/machine instead of
inventing new exact-version pins. The transport's selected serial is independently
bound by the launcher; this Linux report cannot prove USB identity on its own.

`Resources` is exactly `{available_ram_bytes,root_available_bytes,tmp_available_bytes}`,
read from `/proc/meminfo` MemAvailable (KiB multiplied by1024) and `statvfs` user-
available blocks for R and `/tmp`. Proposed conservative preflight floors are
512 MiB available RAM and 1 GiB free on R and `/tmp`; these are scheduling guards
for coordinator adoption, not measured compiler maxima or firmware capacities.
Record post-run resources without applying a preflight floor to a completed run.

Compiler detection scans `/proc/[0-9]+/{exe,cmdline,comm}` without running ps or
searching arbitrary filesystem trees. Identify the executable basename from exe,
removing only the kernel's terminal ` (deleted)` marker; check argv[0] too where
available. A non-kernel process with neither readable identity fails inspection.
A candidate is `arduino-cli` with first argument `compile`, or a basename
matching `(?:.*-)?(?:gcc|g\+\+|cc|c\+\+|cc1|cc1plus|collect2|as|ld|ld\.bfd|ld\.gold|lto1|clang|clang\+\+|rustc)`.
Each candidate is `{pid:int,comm:str,argv0:str,reason:str}`; a nonempty list returns
`COMPILER_PRESENT` with that list intact. Kernel threads with genuinely empty
cmdline are excluded. A process vanishing with ENOENT is a normal race; other
unreadable/incomplete process records fail. Bound inventory to4096 PIDs and64 KiB
per cmdline, rejecting overflow. This is a snapshot, not a machine-wide compiler
lock; the coordinator still ensures serial execution. Never kill/wait out a
candidate or change a service. The helper's own command contains source text, so
matching text anywhere in command lines would be an incorrect detector.

`SourceCheck` is exactly
`{path:S,source_sha256:SOURCE,file_count:102,total_bytes:int,files:{relative_name:{bytes:int,sha256:str}}}`.
Walk the entire tree without following links; require exactly the manifest's
102 regular-file names, with no missing/extra files or special nodes. Empty regular
directories do not change that file-set rule. Hash each file, then compute SOURCE
as SHA256 of sorted `relative_name.encode('utf-8') + b'\0' + raw_bytes` concatenated.
Reject changed content or mutation during the walk; re-enumerate the names and
recheck metadata after hashing. Bound traversal to4096 entries/64 levels. Source
and path checks make no writes. Local source binding remains a separate mandatory
check; neither one substitutes for the other.

`claim` requires R to exist. It may create only the missing fixed parents below
R: `_app_builds`, `static-app-probe-v1`, SOURCE, `bench-default`; existing parents
receive the same no-symlink checks. `mkdir(U)` is exclusive and atomic: existence
of any U entry is failure, including an empty directory or dangling link. Create
B and A exclusively within the newly held U descriptor; return their identities.
There is no transactional rollback: a partial failure retains created paths and
returns `CLAIM_INCOMPLETE` plus `created` and obtained directory identities. No
retry/reuse/removal can turn that failed claim into success. This is an exclusive
run claim, not a claim that three separate mkdir operations are atomic together.

## Fixed artifact names, reads and structural report

`OutputKey` uses literal build/export-relative keys, never caller paths:

| OutputKey | Maximum bytes |
|---|---:|
| `build/app.ino.elf` | 16777216 |
| `build/app.ino_debug.elf` | 16777216 |
| `build/app.ino_temp.elf` | 16777216 |
| `build/app.ino.bin` | 786416 |
| `build/app.ino.bin-zsk.bin` | 786432 |
| `build/app.ino.elf-zsk.bin` | 16777216 |
| `build/app.ino.map` | 16777216 |
| `artifacts/app.ino.bin-zsk.bin` | 786432 |

`absent` checks all eight using no-follow entry lookup; **any** entry fails,
including empty files, directories and dangling links. Query-generated scratch
outside these eight is allowed; it cannot stand in for a required artifact.

`FileRecord` is exactly `{state:str,identity:FileId|null,sha256:str|null}`. State
is one of `regular`, `missing`, `nonregular`, `empty`, `oversize`, `unstable`.
Only `regular` has a nonnull hash, after reading all bytes within its fixed bound.
Nonregular/missing identities are null; empty/oversize retain regular-file fstat
metadata without reading contents. Unstable retains the first observed metadata
but no accepted hash. `artifacts` and `postcheck` enumerate all eight even after
one fails, return `ARTIFACT_SET` for any nonregular state, and preserve observations.
Their normal success also requires exported BIN-ZSK byte equality to its canonical
build copy (size/hash followed by direct bounded byte comparison).

`layout` performs its own complete eight-file checks and reads exactly the seven
build files into the dict with the basenames required by D142. Their maximum
combined payload is85,458,928 bytes; there is no unbounded directory capture.
Invoke the pinned pure validator unchanged, then recheck file identities and
rehash all eight before returning. Require its `report.artifacts` identities to
equal the read bytes and the helper's records. Preserve ValueError as
`LAYOUT_REJECTED` with message and completed identities, exit2. Do not replace an
unexpected layout with a relaxed parser. `report` is the complete D142 return
object, including weak names, sections and its limited
`STATIC_LAYOUT_PACKAGE_PASS` status; no stronger success status is introduced.

`read` accepts NAME only from the seven build basenames, maps it internally to B,
and requires the expected full-file hash from the accepted metadata receipt.
OFFSET must be a multiple of262144; LENGTH must equal
`min(262144,file_size-OFFSET)` and be positive. Reject negative/overflow/out-of-
bounds/repeated-overlap inputs at the runner; rehash the whole bounded file and
check stable identity before/after returning that chunk. Canonical base64,
decoded length and chunk hash must agree. The adopted runner should call `read`
only for final `app.ino.elf`, in increasing offsets with exact coverage and final
whole-file hash verification. Debug/temp/BIN/map remain remotely retained; this
interface permits only bounded named reads for any separately approved later
review, not their automatic collection. No binary contents appear in ordinary
inventory, metadata or layout stdout.

`postcheck` combines same-boot/claim verification, read-only inventory, source
verification and complete eight-file metadata/hash/export checks. Attempt each
independent observation even if another fails, returning `POSTCHECK_FAILED` with
the completed fields and null for unavailable identity/resources/source/files.
Use `compiler_candidates:null` if process inspection itself failed. Preserve each
subcheck error in the failure data's additional `failures` list of
`{check:str,code:str,message:str}`. Success contains only the table's fields.
This allows a failed compile to retain its partial artifacts and independent
source checks without pretending that collection passed.

## Runner sequence, failures and retained evidence

1. Validate fixed local hashes and D139 local stage; claim a fresh local receipt
   directory. Invoke inventory/source; retain unchanged CLI version/core/config
   directory commands, common override checks and all18+8 installed pins.
2. Claim U; run absent; issue the sole expanded-properties query and validate it
   with D141. Immediately before the sole compile repeat inventory, source,
   absent, local bindings, overrides and26 pins. Invoke the exact jobs1 compiler
   from the existing proposal, without a helper wrapper around it.
3. On a terminal compiler result, retain the original return code/stdout/stderr,
   run postcheck and repeat local/installed/override checks even on compile failure.
   If compiler/policy/postchecks pass, run layout, read only final ELF, and perform
   final postcheck/binding checks after collection. Stop after this attempt.

Every transport dispatch gets a numbered planned argv, timeout and start UTC
receipt before execution; append end UTC, actual return code and complete observed
stdout/stderr afterward. Preserve `CalledProcessError` and `TimeoutExpired`
outputs without lossy conversion. A timeout/launch error has no invented exit0;
compile completion stays unknown and no artifact success, retry, reset or new
compiler follows. Automatic postchecks apply to terminal results, not an outer
compile timeout whose remote process may still be running. Additional read-only
diagnosis after such a timeout needs coordinator direction.

Keep the first failure as primary and all later check failures separately; a
successful postcheck never changes a failed compiler result. Preserve source,
dependency and directory identities, original query/compiler receipts, compact
structural JSON, all read chunk receipts and one checked final ELF locally. Keep
all seven artifacts plus the exported copy at their unique remote paths, including
failed/partial outputs. No cleanup is part of this interface. Full entry/native
binding/constructor/ABI review remains separate under the parent contract;
structural success and these receipts alone cannot return full-probe PASS.

Independent runner tests can supply the existing public command substitute and
assert these exact argv/action/JSON/exception contracts, ordering, one-query/
one-compile counts and rejection before later transport calls. They need no
production monkeypatch and cannot substitute validator booleans. The helper's
implementation, fixed hashes, proposed resource floors and controlled filesystem
tests still require their own adoption/freeze/review before any board invocation.
