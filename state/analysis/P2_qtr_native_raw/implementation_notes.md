# D085 native QTR implementation notes

2026-09-23 Asia/Dubai. Scope: actual cooperative `line_qtr::Reader`, private
fixed-size state/helpers, and the inert `p2_qtr_native_compile` probe. Public
Reader methods and public result structs remain the frozen contract. No shared
core/config/test/ledger files were edited by this implementation owner.

The implementation follows `P2_qtr_native_contract.md` and the saved installed
ABI/register evidence in `P2_qtr_native_audit.md`. It uses checked native
`gpio_pin_configure_dt` with OUTPUT_HIGH/INPUT and `gpio_pin_get_raw`; no Arduino
void GPIO wrapper, IRQ registration, clock/peripheral initialization, EXTI/NVIC
mutation or implicit pad takeover is added. Construction/destruction performs no
I/O. A granted and preflighted owner keeps the static claim until firmware reset.

Per-pad state packs the exact mode, output type, speed, pull, AFR and output latch.
Failed-transition cleanup accepts only its explicitly captured old/requested
state. A partial change that matches neither is skipped and remains unconfirmed;
the implementation does not broaden ownership merely to make cleanup succeed.
Cleanup statuses/masks are separate from acquisition statuses and every still
eligible pad is attempted once even after an earlier cleanup failure or deadline.
An unchanged HIGH output latch in neutral INPUT is permitted, as documented by
the native GPIO source. Every configured pin receives exact readback checks.

All loops have four-pad/fixed-bank bounds. Start never waits for charge; advance
does at most one discharge-read pass. Before release all charged pads must read
digital HIGH. Actual per-pad release/observation times preserve sampled bounds,
late LOW takes precedence over timeout and timeout has no finite upper bound.
Whole-frame elapsed time accumulates widened increments, including cleanup.
Final successful call timestamps include final ownership/native-readiness checks.
Valid means bounded complete raw evidence, not color qualification or electrical
acceptance. BUSY/NOT_DUE preserve saved identity; faults never reinitialize.

Validation performed by this owner: strict native-source compilation, exit0:

```
g++ -std=c++17 -Wall -Wextra -Werror -pedantic -DARDUINO_ARCH_ZEPHYR \
    -I tests/native_qtr -c src/hal/line_qtr.cpp -o /tmp/qtr_native_impl.o
```

The controlled headers are owned independently by the test author. This owner
did not inspect independent assertions or alter those fixtures. Initial compile
failed only because fixture extraction duplicated LL_EXTI_LINE_ALL_0_31; the
test author corrected the extraction. The reviewer identified that final
ownership-check cost was outside three final timestamps; the implementation
moved those checks before the final timestamp and passed strict compilation.
Independent behavioral/sanitizer tests and target/startup checks are separate
coordinator evidence; this note does not claim they passed prematurely.

The inert probe retains actual begin/start/advance/cancel/report in its unused
exercise function. Globals supply no ownership grant, setup only publishes the
function address and loop is empty. No upload key, upload, board/MCU/pad/sensor/
motor operation, physical measurement, PINMAP approval or human gate was added.
SC-AJ/F091, hardware handoff/color separation and whole-tick WCET remain open.

Source SHA256 at the strict-compile checkpoint:

| File | SHA256 |
|---|---|
| src/hal/line_qtr.cpp | cf018f5abd16360129d8ffdb9de10d1badb8969767ca9c14cc6bfedab14f5760 |
| src/hal/line_qtr.h | a5127bb26470c1a842ed417be6e953706cacbe47a9c64f01f45e1a1da7d52e24 |
| bench/p2_qtr_native_compile/p2_qtr_native_compile.ino | 282c95efa9b5dad2a729fc0430052c9b3995afb9be672161bfead2b74e8219e4 |
| bench/p2_qtr_native_compile/src/qtr_native_probe.h | cd57a79749a460e56c249376a27178fdefff28f5ac1d0aea4d64ed073e87f187 |
| bench/p2_qtr_native_compile/src/qtr_native_probe.cpp | 7f5bfd60fa657cb16b1409f99dfe284ac22144249b399ff9e226a54d5ed3ac01 |

Next action: independent contract fixtures, actual inert target compilation and
fresh source/ELF review, followed by the coordinator's controller integration
evidence. No hardware acceptance follows from any compile-only result.

## Follow-up: excluded-device admission and retained consumer path

At the coordinator's request, separatePin now rejects excluded motor/opponent/
battery proposal metadata unless its port is the exact named GPIOA, GPIOB or
GPIOC device. The prior non-null/callback/flag/pin-mask and actual pad-overlap
checks remain. An unknown but structurally plausible device can no longer be
used to manufacture non-overlap. Named GPIOC support is sourced in the saved
P2_opp_gpio_audit.md installed table; it does not add GPIOC operations or handoff.

The never-called probe exercise now passes the actual Reader advance snapshot
through applySnapshot and Robot::step, provides a memory-only disabled receipt
to retain the following-tick recording path, and retains the frame codec using
the decision's actual state and masks. The exercise's Snapshot return signature
is unchanged. All additional globals are inert candidate/result memory; setup
still only publishes the address and loop remains empty.

The extended probe source strictly compiles with -std=c++17 -Wall -Wextra -Werror
-pedantic -Isrc, exit0. The first tightened native compile explicitly identified
the independent fixture's missing GPIOC named binding; its owner was notified.
This is a fixture header gap, not evidence of an installed GPIOC API failure.

Updated source identities:

| File | SHA256 |
|---|---|
| src/hal/line_qtr.cpp | 98f445e1b00fb5840427c3e63ac24c6dbbfd24d45d334837aacd9900e8e20bb8 |
| bench/p2_qtr_native_compile/p2_qtr_native_compile.ino | 4e6960285190998538b1ac5194328d0c10e611b9664d856a92b33327d3375234 |
| bench/p2_qtr_native_compile/src/qtr_native_probe.h | 130603bb43ab73defe9a115959b227b1649f0366bf631a48a8dc17e5bf40ee74 |
| bench/p2_qtr_native_compile/src/qtr_native_probe.cpp | c46a4feb13872ac722f54c6a962ec8332318bcfdc3c881da3b8584ed2bde7b47 |

The Reader header remains unchanged from the earlier identity. No board access,
upload, MCU execution, startup acquisition, upload key or shared-file edit occurred.

## First actual target compile failure and repair

The coordinator's actual target compile_initial failed because the installed
Arduino api/Common.h defines the function-like macro bit(b), which collided with
the native source's local bit(unsigned) helper. This failure was observed in the
actual target build, not inferred from host fixtures. Its original coordinator
compile receipt remains preserved. The local helper and all calls were renamed
padBit; no Arduino macro was undefined or altered. This is a naming-only repair.

Final native source SHA256 after repair:
ba6e5a3a2ca02049117f2a8f47896ea43989f2f15cafc37b5bdbcae4d90b10aa.
Strict native-header compilation now passes exit0 with -std=c++17 -Wall -Wextra
-Werror -pedantic and the independent fixture's added GPIOC binding. The actual
target rebuild and its verification remain coordinator-owned.
