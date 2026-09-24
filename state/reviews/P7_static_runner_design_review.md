# Static runner/helper draft design review

2026-09-25. Separate reused-context, same-model Codex review; not fresh-context,
cross-model or human review. Read-only review of drafts and the unchanged
transport/stage-verifier sources. No helper, board, compiler or transport was
executed. Only this review file was written.

**Disposition: initial findings addressed as described below; both drafts remain
UNADOPTED. This is not design closure, implementation permission or a gate.**
The remaining interface prerequisites below must be settled before adoption and
independent test freeze. No new material defect was identified in this bounded
revision beyond that explicit unfinished work.

## Exact drafts

| Document | Initial SHA-256, preserved in `a57265f5` | Reviewed current SHA-256 |
|---|---|---|
| `state/analysis/P7_static_runner_contract.md` | `ff43fda46af494247e11fc4e0425cf3b9e82acf9681c5d334948bb5676bd9497` | `40abe1a3c09fb60fdac1915caa03aa0d07184255f9cc498ceb14ccae03bf0ffa` |
| `state/analysis/P7_static_remote_contract_draft.md` | `b658317f641e30191e6bf927b2c26d4f97abd9d943f4eccec5d374d3886baf21` | `359ee5997963d692b95069ce8f128dde5d3b5523364636c68bffef9f238ada3c` |

Frozen parent D141 remains `d9090cc49a657bdaf08d47def5b9f1fdc8b7da620e19335a0a10b338da32abae`;
D142 remains `b6a18e4d27e500d6306587141cbb27bcd7e546ce9bb507f148f28591634bec54`.

## Initial findings and dispositions

- **MAJOR — Windows command size: design remedy accepted; exact bootstrap pending.**
  Initial remote lines 16/46-52 placed raw helper H and base64 validator V in one
  ADB command. V alone was 24,432 characters; unchanged `board_tool.remote:81-86`
  plus one-character H/C placeholders already required 24,600 Windows command
  characters. The documented limit is 32,767 including NUL. Current remote
  lines 59-84 use bounded zlib/base64 H/M/V, literal raw-byte hashes, strict stream
  framing and an exact quoted-command limit of 30,000 UTF-16 code units including
  NUL. This addresses the transport budget without installing remote code or
  changing the transport. Exact BOOT bytes still need freeze/review and boundary
  tests. [Microsoft CreateProcessW](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw).
- **MAJOR — nonroot process inspection: closed in the revised design.** Initial
  remote lines 139-148 could reject ordinary inaccessible `/proc/PID/exe` links
  and confused empty cmdline with kernel identity. Current lines 183-204 admit
  EACCES/EPERM only when cmdline/comm remain complete, distinguish Kthread/Z
  exclusions through status, and retain failure for missing identity. No elevated
  access or process control is added. Required status-field availability on the
  target remains an observation; missing fields fail rather than imply no jobs.
- **MINOR — conflicting postcheck failure codes: closed.** Current remote
  lines 252-255 retain `ARTIFACT_SET` as the files subcheck code inside the outer
  `POSTCHECK_FAILED` aggregate.
- **MINOR — sequence/resource/identity inconsistencies: partly closed.** The
  runner now checks absence before the query, uses companion helper timeouts,
  requires 512 MiB available RAM and 1 GiB free on both R and `/tmp`, and agrees
  with the helper's aarch64 requirement. A single complete dispatch/postcheck
  order and attempt-count anchor remain to be frozen.
- **MINOR — potentially blocking special-file open: closed in design.** Remote
  lines 136-144 now require no-follow, O_NONBLOCK and regular-file fstat before
  reading, alongside stable identity checks. FIFO and replacement-race tests
  remain necessary.
- **MINOR — unnecessary broader collection route: closed.** Remote lines
  269-279 now allow only `app.ino.elf`; no other basename or arbitrary path can
  use the read action.

## Controlled filesystem seam

Current remote lines 86-96 provide the small sufficient seam:
`main(argv, *, fs_root=Path('/')) -> int`, with production entry always using `/`
and no CLI/environment root override. Real Linux descriptor operations act below
the fixture root while response paths and all validators remain unchanged.
Use WSL with an existing nonroot account and a small RAM-backed exact stage
fixture. Mock only raw account/architecture/resource observations and individual
OS operations for controlled races/errors; retain real UID ownership and inode
checks. No validator callback, chroot, service or filesystem framework is needed.
Existing intermediate-directory ownership checks are consistent with this seam.

## Remaining prerequisites: still open

1. Freeze the exact BOOT source and hash/argv handling, H literal binding and
   bounded decoder behavior. Test malformed/capped/trailing compressed inputs
   and the fully serialized Windows command-size boundary before dispatch.
2. Specify per-action failure-data shapes, including pre-parse failures,
   partial claims, source/file observations, unavailable postcheck fields and
   independent error ordering. BOOT rejection must remain a command failure.
3. Publish one canonical successful dispatch sequence and each terminal failure
   path, including final collection postchecks. Anchor attempt increments after
   successful planned-receipt persistence and immediately before dispatch; no
   callback outcome may enable another query/compiler attempt. Preserve the first
   failure and the no-remote-postcheck rule after unknown compile completion.
4. Freeze host acceptance of the complete nested D142 report, all eight file
   records and cross-action identity/hash comparisons, plus exact final-ELF chunk
   coverage. A schema-valid test substitute is simulation, not target evidence.
5. Independently author/freeze runner and WSL helper tests before implementation
   execution, then review exact implementation, command vectors and first results.

The fixed parent obligations for source/tool identity, freshness, native entry,
constructors, wrappers/heaps and ABI audit remain separate. No query/compiler GO,
static fit, runtime result, production-policy expansion, upload/reset, motor
permission or human phase gate follows from this review.

## Final interface review, 2026-09-25

The following later revision supersedes the earlier pending-interface disposition
above. **No open material design finding remains. Recommend adoption only for
HOST implementation and independently frozen host/WSL tests.** Adoption itself
belongs to the coordinator; no native query/compiler GO follows.

| Final reviewed input | Bytes | SHA-256 |
|---|---:|---|
| `state/analysis/P7_static_runner_contract.md` | 18342 | `35473ed0eb59b9d7fd097cb25554b591ec6bd470703504e1a525219b2fdba7e7` |
| `state/analysis/P7_static_remote_contract_draft.md` | 23571 | `a4be3733d40632b4ae79e3bbbab3300f720b8f7f13f3337d35d96dfc90373b39` |
| `state/analysis/P7_static_link_probe_raw/static_bootstrap.txt` | 1096 | `a6bb46737bea18fc564e77bbd7124c20771258b4fe4ca41a17cbd4cce9798419` |

Read-only inspection closes the outstanding interface-definition items: runner
lines 150-194 give canonical dispatch/postcheck order, attempt anchoring and
primary/secondary failure rules; lines 196-240 define nested report/file/chunk
acceptance and command receipts. Remote lines 295-325 give partial failure-data
shapes, independent check ordering and a per-source 1 MiB bound. The fixed BOOT
template uses canonical base64, cap+1 decompression, EOF/tail rejection and the
literal raw-source hash before UTF-8 decoding/execution; its sole substitution
and argv adjustment are explicit. BOOT/helper execution was not performed.

An additional **MAJOR, now closed**, was identified in interim runner
`9918d2a602ce60e49b05ff475fc997127814231d474eda8578e438d72033be58`,
lines 178-182: treating every integer CalledProcessError return code as proof of
remote compiler completion could authorize remote postchecks after transport
loss. AOSP's client distinguishes a received shell exit packet from unexpected
disconnection, and its daemon's hangup handling does not establish observed
compiler termination at the client. These primary sources explain the evidence
gap; they do not qualify the installed ADB binary. [ADB client source](https://android.googlesource.com/platform/packages/modules/adb/+/refs/heads/main/client/commandline.cpp),
[ADB daemon source](https://android.googlesource.com/platform/packages/modules/adb/+/refs/heads/main/daemon/shell_service.cpp).
Final runner lines 178-185 and remote lines 336-350 conservatively classify every
nonzero compile transport result/CalledProcessError, timeout, launch error and
malformed result as unknown, permitting only local checks. A well-formed zero
result with rejected D141 metadata is a known failed terminal path and retains
the full independent postchecks. No completion wrapper, retry or new command is
introduced.

Independent oracle freeze still precedes implementation execution. Exact helper
bytes/hash, instantiated bootstrap, runner/launcher pins and complete command
vectors must be bound, tested and separately code-reviewed before a later native
GO. The fixed production policies and D141/D142 contracts remain unchanged;
native entry/constructor/binding/ABI audit, actual static fit, runtime and human
gates remain pending. This remains a reused-context same-model design review.
