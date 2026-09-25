# D194 file-only ABI reader host validation

The bounded ABI wrapper is implemented and host-tested. No D194 board call,
owner claim, file-tool child, upload, reset or MCU access has occurred.

Contract SHA256 `889d6a7697f2ddc0051ef73f52f82c1dd43f35fa45af9fc2d4958f44441bf8ff`
was frozen before implementation. Wrapper SHA256
`297eac8b2c9878b8c8e5480053e5541dfc48e9bd35c1a99a924eadc9374d632d`
is unchanged from first execution; source/contract were committed in2ca0f06f.
It privately projects the pinned historical file-only reader, adds member-based
polls queries, and interprets readelf decimal/hex size spelling in a private copy.
Historical source, raw results, safety limits and native ownership remain intact.

## Independent tests and original failure

The separate same-model oracle author read the contract and historical public
sources without reading the new implementation. Original oracle fcbb950e and
first result (43PASS/1FAIL of44 methods) are retained in974de230 and
`P7_app_motor_observe_abi_raw/linux_test01.json`. The failure required the parser
to receive the identical Python layout object; the contract requires unchanged
contents. Author and separate reviewer independently agreed this was a new
fixture defect. Only that method changed: compare contents, save a snapshot,
and verify original layout preservation. All other assertions remain.

Corrected oracle SHA256 is
`ac571bd4a1e4eeba9516795236c9d79329a0d2967999c22f81a953f7aa957cb2`.
The corrected freeze is ec6cf28d. Both final invocations returned zero and all135
coordinator-pinned files remained unchanged:

| Environment | Result | Suite time | Receipt |
|---|---|---:|---|
| WSL Ubuntu/Python3 | 44PASS, no skips | 12.988s | linux_test02.json |
| Windows/Python3.13 | 42PASS, two skips | 1.518s | windows_test01.json |

Windows skips are unavailable symlink-creation privilege (WinError1314) and the
Linux-only FIFO race. Both execute successfully on Linux. Windows hardlink and
cross-API timestamp checks still execute. Fixtures use owned RAM on Linux and
small temporary files on Windows; subprocess/socket endpoints are blocked.

The suite exercises projection/pin drift, passive imports and private namespaces,
CLI refusal before loading, actual projected compiler loading, pre-read
descriptor/link/FIFO guards, observed polls sizes/offsets, unchanged raw data,
strict ABI/command/stream parsing, controlled prepare/execute ownership and
independent failure closure. Command composition stays within the unchanged
Windows bound; oversized composition refuses before dispatch. These are host
fixtures, not observed target ABI or tool behavior.

## Next admitted operation and boundaries

The native owner `P7_app_motor_observe_compile_raw/native_abi_static01` is unused.
After final review and a clean committed HEAD, run check-only then one execute
using the wrapper, Python-B and that exact40hex reviewed HEAD. It reads only the
checked D193 files through the existing four bounded file-tool commands and must
revalidate target identity, artifact hashes and every closing check.

Local C:space fell below the preserved128MiB admission threshold (latest about
11MiB). The user was asked to free200MB outside the project; no response or
storage recovery is presumed. Recheck live space before any native admission.
Earlier policy-denied deletions must not be retried. The next operation cannot
be replaced by an unguarded read to bypass the space limit.

Actual new member layout/GDB syntax remains unobserved. Entry/disassembly checks
and a separate finite inhibited upload/capture follow actual ABI observation.
D190 is still the latest flashed image; the original IO fault, production
memory/loading, recorder lifecycle, physical acceptance and human gates remain
open. Separate same-model source/host review passed with no material findings:
`../reviews/P7_app_motor_observe_abi_review.md`, SHA256
`bb0d2b1111fc3bc357133e398dad48a9cbe0ccb0ef8e584bf04efe3932b9c719`.
