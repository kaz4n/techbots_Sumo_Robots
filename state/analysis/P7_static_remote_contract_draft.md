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
python3 -I -B -c BOOT HZ ACTION RUN_ID [ACTION_ARGUMENTS]
```

`BOOT` is a fixed reviewed bootstrap that checks compressed HZ against the
locally pinned raw H hash, then executes those exact UTF-8 source bytes. It is
not caller shell text. Framing and command-size limits are defined below.
Python's `-I -B` prevents local-module/environment imports
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
The runner supplies its exact bytes as one compressed canonical-base64 argv element
`M`; the helper verifies that literal hash before JSON parsing. `M` is data, not
an authority to accept another source. Its exact 102-file map and literal SOURCE
must agree. The runner separately retains the unchanged D139 local verifier and
its 103-source/102-stage checks and all local pins from the existing proposal.

For `layout`, `V` is compressed canonical base64 of unchanged D142 module bytes, pinned
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

## Transport framing and controlled filesystem entry

HZ, M and V each contain one RFC1950 zlib stream produced with compression level9,
then standard RFC4648 base64 without whitespace. Reject noncanonical base64,
truncated streams, concatenated streams, trailing bytes, or decompressed sizes
above98,304/65,536/32,768 bytes respectively. Use bounded decompression to cap+1,
require EOF with no unused data or unconsumed tail, and verify the literal raw-byte
SHA before UTF-8 decoding, JSON parsing or code execution. Do not require identical
compressed bytes from different zlib versions; the raw input hash is authoritative.
Claim C remains uncompressed canonical JSON/base64: UTF-8, sort_keys=True,
separators=(',', ':'), ensure_ascii=True, no NaN/Infinity.

BOOT removes only HZ from sys.argv before executing H in a fresh namespace with
__name__='__main__'. Freeze its exact source alongside implementation; the accepted
H hash is a reviewed literal, never a caller flag. BOOT decode/hash failure exits
nonzero without a helper success envelope and remains the original command failure.
No remote file is installed.
The exact template is [static_bootstrap.txt](P7_static_link_probe_raw/static_bootstrap.txt),
SHA256 a6bb46737bea18fc564e77bbd7124c20771258b4fe4ca41a17cbd4cce9798419.
Replace its single @HELPER_SHA256@ token with the runner's literal helper pin;
no other template transformation or caller-provided replacement is allowed.

Before every transport call, compute exactly
`subprocess.list2cmdline([ADB, '-s', '2629958581', 'shell', '-T', shlex.join(argv)])`.
Its UTF-16-LE byte count divided by2, plus1 for NUL, must be<=30,000. Reject before
dispatch if larger. This leaves margin below Windows' documented32,767-character
limit; do not truncate, split or retry. Current unchanged D142 bytes encode to7,232
compressed base64 characters instead of24,432 raw-base64 characters; the manifest
encodes to6,296 rather than13,588. These are local RAM observations, not transport tests.

The public host-test entry is
`main(argv: list[str], *, fs_root: Path = Path('/')) -> int`, emitting the envelope
to stdout. Open fs_root once and use real descriptor-relative, no-follow operations
for all unchanged logical paths below it; receipts retain logical absolute names.
The serialized production entry calls main(sys.argv[1:]) with default '/'; no CLI
or environment root option exists. No validation function is replaceable.
Positive tests use a temporary Linux tree and actual nonroot UID/GID/ownership;
they may mock pwd name/home, uname architecture and statvfs observations at OS
boundaries. If WSL starts as root, use an existing nonroot account. Individual OS
operation wrappers may inject races/errors while performing real fixture operations.
No chroot, installed service or filesystem abstraction is added.

Primary references: [Windows command limit](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw),
[Python bounded zlib decompression](https://docs.python.org/3/library/zlib.html#zlib.Decompress.decompress).

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
O_NONBLOCK plus regular-file fstat before reading, and stable FileId before/after
reading; recheck that the
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
`machine:"aarch64"`, Python >=3.9 and a valid kernel boot UUID. Record release
without an exact kernel-version pin. The transport's selected serial is independently
bound by the launcher; this Linux report cannot prove USB identity on its own.

`Resources` is exactly `{available_ram_bytes,root_available_bytes,tmp_available_bytes}`,
read from `/proc/meminfo` MemAvailable (KiB multiplied by1024) and `statvfs` user-
available blocks for R and `/tmp`. Proposed conservative preflight floors are
512 MiB available RAM and 1 GiB free on R and `/tmp`; these are scheduling guards
for coordinator adoption, not measured compiler maxima or firmware capacities.
Record post-run resources without applying a preflight floor to a completed run.

Compiler detection scans `/proc/[0-9]+/{exe,cmdline,comm,status}` without running
ps or searching unrelated trees. Read regular proc records with64KiB bounds and
strict UTF-8; cmdline is NUL-delimited and must end in NUL when nonempty. Require
one State and one Kthread field in status; only Kthread=1 or State=Z permits an
empty cmdline. These excluded processes cannot run a compiler. For other processes,
require nonempty argv[0] and readable comm. exe EACCES/EPERM is optional metadata
when cmdline/comm are complete; any other unreadable identity fails inspection.
Strip only terminal ` (deleted)` from exe and check its basename and argv[0].
A candidate is `arduino-cli` with a `compile` argument, or either basename
matching `(?:.*-)?(?:gcc|g\+\+|cc|c\+\+|cc1|cc1plus|collect2|as|ld|ld\.bfd|ld\.gold|lto1|clang|clang\+\+|rustc)`.
Each candidate is `{pid:int,comm:str,argv0:str,reason:str}`, ordered by PID, with
reason exactly `arduino-cli compile` or `compiler executable` (the CLI reason has
priority). Do not return the rest of cmdline. A nonempty list returns
`COMPILER_PRESENT` with that list intact. A process vanishing with ENOENT/ESRCH is
a normal race; other incomplete process records fail. Bound inventory to4096 PIDs and64 KiB
per cmdline, rejecting overflow. This is a snapshot, not a machine-wide compiler
lock; the coordinator still ensures serial execution. Never kill/wait out a
candidate or change a service. The helper's own command contains source text, so
matching text anywhere in command lines would be an incorrect detector.
The [kernel proc documentation](https://docs.kernel.org/filesystems/proc.html)
defines State and Kthread. Actual availability on the connected target is still
an observation; missing fields never become an assumed empty compiler list.

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
receive the same no-symlink and effective-UID ownership checks. All existing
intermediate directories below R must belong to that UID. `mkdir(U)` is exclusive and atomic: existence
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
For postcheck, `POSTCHECK_FAILED` is the outer aggregate code and `ARTIFACT_SET`
is retained as the files subcheck's failure code. Their normal success also requires exported BIN-ZSK byte equality to its canonical
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

`read` accepts NAME only as the literal `app.ino.elf`, maps it internally to B,
and requires the expected full-file hash from the accepted metadata receipt.
OFFSET must be a multiple of262144; LENGTH must equal
`min(262144,file_size-OFFSET)` and be positive. Reject negative/overflow/out-of-
bounds/repeated-overlap inputs at the runner; rehash the whole bounded file and
check stable identity before/after returning that chunk. Canonical base64,
decoded length and chunk hash must agree. The adopted runner should call `read`
only for final `app.ino.elf`, in increasing offsets with exact coverage and final
whole-file hash verification. Debug/temp/BIN/map remain remotely retained; this
interface has no broader collection route. No binary contents appear in ordinary
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

## Failure-data completion and independent checks

Before valid action/argument admission, emit BAD_REQUEST with data={} and no
filesystem mutation. action/run_id are the supplied strings when present and
otherwise null; invalid tokens are not normalized into valid ones. After admission,
failure data retains exactly that action's success keys, with null for an
unavailable whole field, except the following explicit additions/partial shapes:

- Source failure retains path, SOURCE, file_count (observed count or null),
  total_bytes (sum of successfully hashed files), and files (only completed hashes).
- Claim failure additionally has partial_directories:{run,build,artifacts}, each
  a checked DirId or null. claim is null until all three directories are claimed;
  created contains every successful mkdir in order. Success has no partial field.
- absent outputs contains all eight keys, each `absent`, `present`, or null if
  lookup failed; only eight `absent` entries can succeed.
- Artifact/layout failure retains every completed FileRecord; files is null if
  no claimed directories could be checked. Layout report is null until validation
  succeeds. read fields that were not observed are null, never invented chunks.
- postcheck always attempts independent checks in order `claim`, `identity`,
  `resources`, `processes`, `source`, `files`. Its failure-only `failures` list uses
  those exact check strings, each with code/message. A failed claim prevents
  reading its output directories; record files failure PATH while still attempting
  the unrelated identity/resources/processes/source checks. All other independent
  failures preserve completed observations. Resource observation after compile
  does not apply minimum floors. Outer code is always POSTCHECK_FAILED.

All action filesystem reads are bounded and nonblocking where special files
could otherwise hang. Because M contains hashes without lengths, use a1MiB
per-source-file limit and the fixed102-file set, then require exact literal hashes. This is a helper
resource bound, not a source change. Total source bytes are independently matched
by the runner to the local stage. No custom exception object crosses transport.

## Runner sequence, failures and retained evidence

1. Validate fixed local hashes and D139 local stage; claim a fresh local receipt
   directory. Invoke inventory/source; retain unchanged CLI version/core/config
   directory commands, common override checks and all18+8 installed pins.
2. Claim U; run absent; issue the sole expanded-properties query and validate it
   with D141. Immediately before the sole compile repeat inventory, source,
   absent, local bindings, overrides and26 pins. Invoke the exact jobs1 compiler
   from the existing proposal, without a helper wrapper around it.
3. On a well-formed zero compiler transport result, retain original code/stdout/stderr,
   run postcheck and repeat local/installed/override checks even on compile failure.
   If compiler/policy/postchecks pass, run layout, read only final ELF, and perform
   final postcheck/binding checks after collection. Stop after this attempt.

Every transport dispatch gets a numbered planned argv, timeout and start UTC
receipt before execution; append end UTC, actual return code and complete observed
stdout/stderr afterward. Preserve `CalledProcessError` and `TimeoutExpired`
outputs without lossy conversion. A timeout/launch error has no invented exit0;
compile completion stays unknown and no artifact success, retry, reset or new
compiler follows. Automatic postchecks apply to terminal results, not an outer
compile timeout or nonzero ADB result whose remote process may still be running.
The runner's canonical sequence defines those as COMPILE_OUTCOME_UNKNOWN with
local checks only; a local nonzero return is not a remote completion indicator. Additional read-only
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
