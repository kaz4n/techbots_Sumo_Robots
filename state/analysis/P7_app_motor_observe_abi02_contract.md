# D194 file-only ABI attempt02 query correction

26 September 2026. Attempt01 is FAILED and consumed. Its four file children
returned0 with all13 remote closing checks and local closure PASS, but GDB16.2
emitted86 stderr bytes for alignof(member-expression). No complete ABI was
accepted. Raw member SIZE was4, LAYOUT was `type = unsigned int`, and OFFSET
was168572. These are observed partial data, not an assumed typedef/alignment.

Keep all existing source, tests, contracts, original failures and owners intact.
Add only a small wrapper at
state/analysis/P7_app_motor_observe_compile_raw/inspect_static_abi02.py and
independent tests. No copied transport/owner lifecycle or toolchain action.

## Fixed provenance

| Input relative to repository | Bytes | SHA256 |
|---|---:|---|
| state/analysis/P7_app_motor_observe_compile_raw/inspect_static_abi.py | 9318 | 497f756e4eab440d659a4d26ef38ec8d92abdd9f92a5938d1da04705745f42d5 |
| state/analysis/P7_app_motor_observe_compile_raw/native_abi_static01/result.json | 893217 | e83afc5f10cec2ed72f88d6567f6f13e5809518e1b89f3d5988d988b297e78f5 |
| state/analysis/P7_app_motor_observe_compile_raw/native_abi_static01/local_result.json | 336 | 589b78d1ff3cacbe96869f2f2c43d3fc546a9ff2cbfc26c34d1ad3a3d9b9ec01 |

The original wrapper retains its contract0d81956d, source3a08ddeb, D193
ELF2fd70da8/debug33e3b34d/package85b05c56 and all inherited exact pins. Pin this
supplementary contract by its final SHA in the new wrapper. No original file is
modified. Bind both failed receipts as provenance, never as a successful ABI.

## Bootstrap and public interface

Public helpers: project_reader(raw), summarize(result, layout, *, summary),
load_reader(*, root=ROOT), main(argv). ROOT is this repository. Import defines
only; no reads, subprocess, device, module registration or bytecode side effects.
main first requires exact list[str] arguments
--check-only|--execute --reviewed-head <40 lowercase hex> and Python-B before any
input read; then delegates exactly once to the private reader's unchanged main.
No additional CLI profile, source, type, owner or target option.

Bootstrap must retain the repaired original `_stamp`, `_plain_chain`,
`_read_handle`, `pinned`, and `require` implementations exactly as source text.
This small copied bootstrap is needed to verify the original wrapper before
executing it; do not duplicate lifecycle code. All ancestry, link, reparse,
pre-read descriptor, Windows executable-mode, same-API stability, byte bounds,
hash, close and primary-error protections remain. Compare helper source bodies
against the pinned original in independent tests.

load_reader reads/verifies the original wrapper and both failed receipts and
this contract using that bootstrap BEFORE executing the wrapper definitions in
a fresh private ModuleType, with the original absolute __file__, never __main__
or sys.modules. Also check the three fixed byte lengths. Save its original
project_reader, replace it privately by composition that first calls the saved
original projection and then the new project_reader below. Call its unchanged
load_reader(root=root), extend the returned HARD_PINS with all four new inputs,
and preserve every inherited pin. SELF binds the new wrapper via reviewedHEAD.

## Exact supplementary projection

project_reader accepts exact bytes, requiring16833 bytes and SHA256
f359bebbbba176036891027412327b6b59e47d849e46c37cfe3363cd70a95c14.
Perform only these ordered count-checked replacements:

| Old | New | Count |
|---|---|---:|
| '/inspect_static_abi.py' | '/inspect_static_abi02.py' | 1 |
| 'native_abi_static01' | 'native_abi_static02' | 1 |
| app-motor-observe-abi-static01 | app-motor-observe-abi-static02 | 1 |
| D194_STATIC_FILE_ONLY_ABI | D194_STATIC_FILE_ONLY_ABI02 | 2 |

Finally replace the unique bytes `expression + '(' + subject + ')'` with:

```python
expression + '(' + ('unsigned int' if name == 'report_.polls' and
                            label == 'ALIGN' else subject) + ')'
```

Require final16937 bytes and SHA256
b03561df65e768cf582a42d520e6241a9cd02c3563685b87070bd3dfc820e981.
No replacement changes D193 build OWNER/artifacts, other query tags, windows,
SIZE/member LAYOUT/OFFSET or the existing parser/lifecycle. Polls ALIGN now
queries `alignof(unsigned int)`, using the observed actual member type. The
returned numeric alignment must be observed anew; do not supply4 or another
alignment from source, offset divisibility or a fixture.

## Current type confirmation and output

Wrap only the returned reader's summarize callable, saving the existing
normalized summary first. Public summarize requires exact dict result with
exactly four dict command records, a callable summary, and command3 UTF8 stdout
decoded from validated Base64. Require exactly one polls LAYOUT marker and
exactly one contiguous block `SUMOX_LAYOUT report_.polls`, `type = unsigned int`,
`SUMOX_SIZE bool` (LF or CRLF), in that order with no intervening material.
Thus current actual member type is confirmed again before summary delegation.
Reject missing/duplicate/malformed/other type; never rewrite the result or
layout. Delegate once with the original arguments to the saved normalized
summary. Return its dict fields plus polls_alignment_type containing
`type: unsigned int` and `evidence_sha256: e83afc5f10cec2ed72f88d6567f6f13e5809518e1b89f3d5988d988b297e78f5`.
Retain readelf normalization metadata and complete numeric tags/BSS/window checks.

## Native scope and validation

Exclusive new local owner native_abi_static02; absent remote scope
/home/arduino/sumox26_codex_build/app-motor-observe-abi-static02. The file-only
reader does not create the remote scope. Attempt01 stays consumed/FAILED.
Retain all four commands,60s child/5s reap/1MiB streams,400s transport,
30000UTF16 command units,128MiB local storage, exact source/artifact/tool/boot
pins, clean reviewedHEAD, before/after remote checks and independent local
closure. Strict empty stderr remains; no selective error suppression.
No upload, reset, compiler, MCU read, motion, credential or firmware change.

Independent oracle must freeze before seeing the new implementation. Test
invalid CLI/passive import, exact bootstrap equality, original-first bounded
projection/rejections, private composition/pins, exact ALIGN-only query change,
new/old owner separation, current-type strictness/raw preservation, complete ABI
summary and failure/closure delegation. Reuse existing contract fixtures where
they apply; preserve all old tests/assertions. Run Linux and Windows serially,
freeze inputs and review before native admission. File evidence does not prove
runtime behavior, physical acceptance, motor permission, RAM/WCET or human gates.
