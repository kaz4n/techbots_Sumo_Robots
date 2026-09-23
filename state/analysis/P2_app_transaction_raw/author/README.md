# D095 independent author evidence

Public-spec author read the complete frozen D095 contract and public headers.
No production C++ implementation body was read. Production sources were copied,
hashed and compiled as opaque bytes. All commands ran locally under WSL; transport
tests used controlled fixtures/mocks and did not access a board.

Final authored files and SHA-256:

| File | SHA-256 |
|---|---|
| tests/locked/test_motor_halt.cpp | 3766863f06ecb4b3f9eeabb6140122f0d04a1fa33ef54b1cee42491d8f15a49f |
| tests/test_app_transaction.cpp | 9f9de2c9e9c5b88bdb9950db6446cd7d7e8a3b0f6c7ee6ac534d53f91959ee73 |
| tests/fixtures/app_transaction_fixture.h | eb9bcab2f3a5c19d40e312a272e82738085ac1d7a3e74990ae4cc7b41daa40d1 |
| tests/native_motors/app_transaction_probe.cc | 54c754a9f60150187c39aa31755a4abb0f108c7dd147755c54d9ecb09b43de87 |
| tests/tooling/test_app_transaction.py | 2c72c509723e5e0df58f2f0a18d36397ce73438d21e9715910f57f5282ec801b |

## Passing evidence

The six original tooling methods passed together using:

`python3 -m unittest tests.tooling.test_app_transaction -v`

- Actual halt/Transaction composition, strict C++17 with UBSan and no recovery:
  default motors: 28 cases,617259 assertions; enabled host motors:28 cases,
  617260 assertions. Receipts `command_1790175831952123461.json` and
  `command_1790175842158214552.json`.
- Actual retained probe with actual native motor implementation linked against
  the existing installed-shaped fixture:2 cases/9 assertions in each macro mode.
  Both startup/10000 loops are inert;1000 actual owner cycles plus terminal abort
  allocate/deallocate nothing. Receipts `command_1790175858023993831.json` and
  `command_1790175872079612406.json`.
- Eight attempted upload configurations refuse before target/transport/remote.
- App and bench shared-support staging preserves `src/app` include layout and
  root sketch placement, excludes shared .ino, and compiles the synthetic support.
- A controlled compile failure propagates without upload or false success.
- Sketch-local `src/app` shadow fails before transport.

Two additive tooling methods then passed using:

`python3 -m unittest tests.tooling.test_app_transaction.AppTransactionTests.test_actual_staged_transaction_cpp_and_header_resolve_without_root_include_flags tests.tooling.test_app_transaction.AppTransactionTests.test_flash_propagates_staging_error_before_any_remote_command -v`

These compile actual staged transaction.cpp and its public header without project
root include flags, and prove the identical controlled staging exception reaches
the flash caller before verify_core/remote invocation. All8 final methods have
passing evidence; the last two were added after the six-method full run.

Each command JSON preserves exact argv, stdout/stderr, exit code and source/test
SHA-256. Staging/upload/error receipts preserve exact controlled inputs/results.
The 200-second test executes200000 actual1kHz owner epochs after START plus the
real final tail, retaining5001 frames and194901 GO-through-STOP timing members,
zero overruns/loss and expected exact START/GO timestamps. These are synthetic
host clocks/sensors, never physical runtime or full-HAL WCET evidence.

## Initial failures and corrections

1. `command_1790175729523833434.json`: new test used a doctest-decomposed `||`
   expression unsupported by its assertion syntax. Replaced it with an exact
   enum expectation. No production or established test changed.
2. Initial shadow test expected literal word `reserved`, although D095 only
   requires diagnostic refusal. Actual diagnostic was `sketch-local src/app
   conflicts with project source`. Corrected the new test to require `src/app`
   and `conflicts`; retained refusal/no-transport assertions. Initial stderr is
   preserved by the first shadow staging receipt.
3. `command_1790175792476739459.json`:28 cases,26 passed,2 failed/4 assertions.
   The author initially treated common S..C half-range invalidity as RECEIPT;
   the public contract reserves invalid A chronology for RECEIPT, while invalid
   completion clock is CLOCK. Corrected only that new expectation; all explicit
   invalid application-time cases still require RECEIPT.
4. The same receipt records a clean-final-tail expectation using the sparse
   `go()` convenience path. Multi-second omitted epochs correctly produce
   skipped recorder frames. Kept the no-loss assertion and replaced the shortcut
   with5100 genuine1kHz countdown owner epochs, then actual STOP and tail.

These are provisional author-test corrections before establishment, not production
fixes or weakened existing/locked assertions. The new halt file is frozen after
its successful run; no pre-existing test was edited. Parent owns full suite,
target compilation, separate fresh review, shared ledgers and commits.
