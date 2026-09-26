# Recorder failure ABI: actual observation

The single D230 file-only observation passed. Independent review
[P7_recorder_failure_abi_actual_review.md](../reviews/P7_recorder_failure_abi_actual_review.md)
accepts the retained ELF/DWARF layout evidence. It establishes no MCU status or
failure cause. The D228 UART capture remains failed with zero bytes.

At collector `b90fd291`, check-only completed in 1.620 s and the one execution
in 4.784 s. All four fixed children returned 0 and were reaped; twelve remote
file checks, board identity and local closure passed. Historical firmware
source remains `004dc7cf`; current source and historical bindings match.

The accepted ABI is 231,321 bytes, SHA-256
`de0cb0ecb558937a9ad251fd81168fe340bf2440aa9ebd3108a60d7758b89ee9`.
Fresh layouts place the runner in its checked BSS initialization interval and
the native dump object in its checked data copy interval. Ten status windows
merge to six aligned ranges totaling 684 bytes per snapshot.

Raw files and the compact root inventory are retained under
[P7_recorder_failure_raw/native_abi01](P7_recorder_failure_raw/native_abi01).
The owner is consumed. No upload, reset, MCU read, UART operation or cleanup ran.
Next is one reviewed passive capture with full loader/sketch comparisons before
and after the two status snapshots.
