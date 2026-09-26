# D230 independent review: file-only ABI checkpoint

Reviewed 2026-09-27. Verdict: **PASS for the frozen file-only ABI source/host
scope and its concrete check-only/one-execution sequence below**. No material
blocker was found in that scope. The passive capture adapter's source and
synthetic tests were also inspected, but the complete local passive execution,
staging and retrieval workflow is **PENDING**. It is not admitted by this
checkpoint. No native command or source/test edit was performed by this reviewer.

Frozen checkpoint SHA256 identities:

| File | Bytes | SHA256 |
| --- | ---: | --- |
| tools/recorder_failure_abi.py | 23716 | 2191e8d77513ee3b2d9f47497523cf3199a70112e325e01d1543b8e3aca1add6 |
| tools/recorder_failure_capture.py | 11767 | 13fc387d0cb6d0475232aa4683bf47423ad2f85255db543f62da71ea5c8420b2 |
| tests/test_recorder_failure.py | 16807 | a85a3b6ff6d6c84d16db0e7882da2f2da278642caeaac5235874d3d2822ea6c2 |
| P7_recorder_failure_contract.md | 5271 | 565cbdf85ddb03db1cd843eb7b2d0a31d875c8e55ed3027e1e3a56bd3cd50279 |
| P7_recorder_failure_raw/plan.json | 26015 | 6bdfd2a6652f6c9309bafa525b8ce9db181c36d6f367e8d2452acc9c7d1290b1 |
| P7_recorder_failure_validation.md | 4818 | dd0a1fca6d678e979f7e9801b3c283b0f7b2c408062916a904a4ea4c9f89c1a0 |
| P7_recorder_failure_raw/host_closure.json | 3499 | 65ab9e40be42259ad6fc2991c5ee1e07221c3f190b80800aa161617433ee10d2 |

Analysis paths in the table are relative to state/analysis. All19 closure pins
were independently recomputed and match. The20-file checkpoint comprises
those19 entries and the closure itself; this review is separate.

The historical compiler identity remains HEAD
004dc7cff534896a851901f9d7d0ba6066cae060, attempt
377911abefabd094971ee6d089326604, session3997245574426120340 and source
702ad99ee4f888c58de1715cb91512cb0a174a646d914db6ce9155489ffa63e8.
Current collector HEAD is independently supplied and must be exact and clean.
The code reuses the existing recorder admission to check144 input bytes against
historical Git blobs and109 staged entries, including the identified header.
The four pinned compile records are validated against that owner and its
checked artifact packet. Collector code, plan, contract and pinned helpers are
independently checked against the new collector HEAD. This correctly avoids
requiring a documentation-only collector commit to equal the compile HEAD.

The executable ABI sequence is concrete: four fixed children query installed
readelf/gdb versions, the current ELF header/sections/symbols, and435 bounded
offline GDB expressions on its matching debug ELF. The fixed expressions obtain
8 layouts,10 windows and56 scalar fields. GDB retains -nx/-nh/-batch,
auto-load disabled and may-call-functions off. There is no target, attach,
inferior, call, UART, memory examination, upload, reset or motor command.
The source declares exact enum values and widths consistent with the current
Runner, transaction and dump headers. Strict inherited parsers reject missing,
reordered, duplicate, unavailable or incomplete answers and malformed unsigned
numeric responses.

The runner must fit its exact initialized BSS interval. native_dump must fit
the corresponding verified BSS or data-copy interval; the checked `.data`
load/destination/size and ELF section must agree. Objects, windows and fields
must fit, align and not overlap. No historical B4 address, old296-byte schema,
or uninitialized BSS tail supplies an answer. Four D209 descriptor-reader bodies
are unchanged. D188's execute/finally body is reused with only the fixed scope
label substituted; D173's GDB builder and remote read/closing body are reused.
All12 remote files and board identity close independently, followed by local
closure even after command or parsing failure. First failures and raw bounded
streams are retained. The existing child60s/reap5s, stream1MiB, transport400s,
reply8MiB, command30000 UTF16 units and local free128MiB limits remain.
Local native_abi01 is absent-only and consumed by partial output; the fixed
remote scope is checked absent and never created by this file-only operation.

Host evidence closes with18/18 Windows and18/18 Linux methods passing. The
reviewer inspected the actual method bodies and both complete method receipts.
The construction fixture uses real historical admission and production payload
construction, producing4 children,12 pins and7913 command units; only its live
clean-HEAD/ADB gate is substituted, and accidental transport is rejected. Thus
this is useful construction evidence, not actual native check-only admission.
Failure/closure, exact inherited descriptor bodies, data/BSS boundaries,
duplicate layouts/symbols, marker/type/enum/field refusals, flash-before-SRAM,
missing/invalid snapshots and final brackets are covered. The initial Windows
fixture error and Linux DrvFS metadata refusal are preserved. The Linux pass
uses an exact-byte /dev/shm fixture mirror with explicit historical Git context;
the cause of the earlier metadata change remains unproved. No production guard
was relaxed and no closed test suite was rerun by the reviewer.

After integrating this frozen checkpoint at one clean exact collector HEAD,
root may run these existing commands, in sequence:

```
python -B tools/recorder_failure_abi.py --check-only --reviewed-head <collector HEAD>
python -B tools/recorder_failure_abi.py --execute --reviewed-head <same collector HEAD>
```

Only a successful check-only admits that one execution. Retain any refusal or
partial result; this is not a retry allowance. Reconcile all4 command receipts,
12 file checks, board identity and local closure before accepting abi.json.
The expected boot remains55c386b9-fe6d-4388-a7f4-1d91e0bb49d8 and serial2629958581.
No MCU observation or failure cause is established by this file-only step.

The reviewed four-hook capture component mechanically hashes the accepted ABI
and canonical spec, uses two bounded aligned SRAM snapshots with2s separation,
and brackets them with full263680-byte loader and55104-byte sketch comparisons.
Initial flash mismatch stops before SRAM. Invalid bool/enum values retain raw
evidence, fail collection and permit final flash checks when reads succeed;
session mismatch remains an observation, including possible setup-time0.
Inherited directory, file, process, child, deadline and finalization guards
remain, and coherence is always UNPROVEN. These component observations are not
acceptance of a complete capture caller: validation steps4-5 still leave its
local staging/invocation/retrieval unspecified. That additive caller and its
exact runnable sequence require completion and scoped review before passive
execution. Mechanical ABI/spec identity binding then needs no recursive source
review chain. No firmware/grant change, receiver retry, motor permission,
physical qualification or phase pass follows from this checkpoint.
