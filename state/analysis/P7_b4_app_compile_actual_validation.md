# B4 motor-disabled native compile — 26 September 2026

The UNO Q completed one fixed B4 compile-only attempt at reviewed clean commit
`34c1b965f4ed2a9332c4f890ee2a4a27d89a7ba0`. The outcome is `COMPILE_CHECKED`.
This uses the ordinary application entry, static linking, default startup,
`MATCH=0`, `MOTORS_ALLOWED=0`, `SUMOX_B4_STAND=1`, and the other seven profile
macros set to zero. Source remains `9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a`.
Only the controller board is connected.

The local check-only and execute calls returned zero, taking 0.706 and 274.602
seconds respectively. There was one properties query and one compiler child,
using one compiler process. The compiler child took 226.749 seconds within its
720-second deadline. All 25 transports completed; nine independent closing
checks passed. The two source-payload transfers retained the same final file
identity and hash at closing. No upload, MCU read, reset or privileged command
was performed.

| Checked artifact | Bytes | SHA-256 |
|---|---:|---|
| Packaged image | 82,912 | `84667b0a22ff7701059a266b6c82bb61de1f7ccec96280e4f13b5692bf785a28` |
| Raw binary | 82,896 | `6fcad2f09c90bbc7dd72760e7a794305811d042a9d2e578e03d5154cc368a471` |
| ELF | 152,780 | `12a24abfb96e89863c46f2475d05fb44a549db95cb157411cd794657f15fd422` |
| Debug ELF | 1,779,680 | `4c0fc8e2d3881019aaef222d7a9ab77779da7ca116bca49d1c6badeefeb83f7d` |

The independent layout validator returned `STATIC_B4_APP_LAYOUT_PACKAGE_PASS`
with an exact integer `motors_allowed=0`. Structural RAM remainder is 94,352
bytes; the compiler reports 94,348 bytes. These are separate static accounting
results, not measured free RAM. The initialized zero span is 167,352 bytes;
the complete `.bss` section is 167,584 bytes. No cause is inferred for either
accounting difference.

`P7_b4_app_compile_raw/native_closing01.json` (34,317 bytes,
`7a43d0be1d4f51f11d198c431b11cc7c0a277735fc897bf49c6e2d238e14eb17`)
reconciles 244 prerequisite files against both current bytes and the native
commit, 224 coordinator pins, 130 manifest entries and 17 scope inputs. It
also checks raw child streams, all transport results, the two artifact
observations, payload closure, and 104 mapped stage files totaling 764,405
bytes. The outer receipt is 9,114 bytes with hash
`c2c5dfba3315f6ee79067baa31a6a9b014961ac4e2173974dfcb2df284761bd4`.

Independent actual review is recorded separately in
`state/reviews/P7_b4_app_compile_actual_review.md`. Original host failures and
their bounded corrections remain preserved; accepted composed host coverage
is documented in `P7_b4_app_compile_validation.md`.

The compile owner is consumed. Preserve its target artifacts for fresh B4
ABI analysis. The previously accepted D212 ordinary M0 application remains
the latest verified flash. B4 loading, initialized timing/live memory,
retained-recorder capture, actual wiring/calibration/motor tests and human
phase gates remain unqualified. A bare-board run with absent setup grants
cannot establish completion of the B4 directional sequence.

Independent actual review is FINAL PASS: 8,486 bytes, SHA-256 `7490c2325668a744ebaf3685a12c24365843be402c2d9dae166a79e4a1e4faad`. No open material compile finding remains.
