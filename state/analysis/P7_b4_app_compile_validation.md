# D214 fixed-M0 B4 compile preparation

The existing ordinary `app.ino` entry now has a separate B4 compile-only tool.
It selects static linking, default startup, MATCH0, MOTORS_ALLOWED0 and the
complete ten-macro B4 profile. All 105 firmware source files and configured
grants are unchanged. The user has only the UNO Q connected.

`tools/compile_b4_app_static.py` retains the checked D208 source mapping,
ownership, one-query/one-compiler, serial build and closing guards. The remote
validator binds the accepted D213 policy and its five exact source snapshots.
The eight-source validation payload exceeded Windows' command-line ceiling,
so two bounded transfers store it under the fresh compile owner. Descriptor,
identity, hash and independent closing checks protect this source-only file.
The largest final command is29352 UTF-16 units including NUL, below30000.

Independent tests exposed a missing descriptor-relative directory-open argument.
Source review also found that incomplete transfers skipped their final file
observation. Both product defects are corrected. The original source, oracle and
first Linux failures are preserved in commit8b669d77. Corrected product and full
revision02 evidence are preserved in3f6ad8bb. A subsequent Windows-only fixture
sentinel permits importing the Linux helper while refusing every account API
call; the actual policy/validators and all test assertions remain unchanged.

Final coverage is explicitly composed from86 unchanged revision02 methods and
five freshly run portable methods on each platform:

| Platform | Passed | Skipped |
|---|---:|---:|
| Linux |91|0|
| Windows |69|22|

Every Windows skipped method passed on Linux. This is not a new full91-method
run after the fixture-only correction. `P7_b4_app_compile_raw/host_closing01.json`
reconciles all outcomes, exact method/function changes,16 saved invocation files
and224 unchanged final inputs. Both Windows temporary roots are empty and kept
as zero-payload ownership evidence; no independent Linux remnant inventory is
claimed. No broader repeated suite was needed for the unchanged code.

Native compilation still requires the independent final source/host review,
fresh read-only board admission, exact manifest/scope, clean committed reviewed
HEAD and one successful check-only invocation. No B4 upload, reset or MCU read
is authorized by this tool. D212 remains the latest verified flashed firmware.
Loading B4, its own ABI/capture, live memory/timing, recording delivery, physical
commissioning and human gates remain separate.


## Native outcome

The preparation requirements above have now completed. One native attempt returned COMPILE_CHECKED and independent actual review7490c232 is FINAL PASS. See P7_b4_app_compile_actual_validation.md for exact artifacts, timing, closure and remaining qualification boundaries. Do not rerun the consumed native owner.
