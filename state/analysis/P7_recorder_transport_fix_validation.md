# D228 identified recorder transport correction

The first native D225 run stopped before the receiver and upload because its
private dump helper still consulted ambient SUMO_TRANSPORT. The compiled image
passed; the run recorded zero upload attempts and no closing errors. Firmware
remains the previously loaded D221 inhibited B4 application. The consumed
36370b3b911165b926583f33448b0b09 owner and its evidence are retained unchanged.

The corrected caller gives its private receiver module the same fixed ADB mode
and serial already enforced by ReceiverCommands. It checks that private binding
before arming. It changes neither the ambient environment nor the original board
module. Exact command whitelist, executable hash, session, connection ordering,
stream limits, deadlines, latch, process reaping and upload guards remain intact.
No firmware, configuration, pin, motor authority or locked test changed.

## Evidence

The two new positive-route tests were first run against the exact committed old
caller (SHA-256 9ea1be98388139343be02bc74857c220faa75c32b876b9938f855188d750b6cd).
Both failed as expected: conflicting ambient routing was inherited and absent
SUMO_TRANSPORT raised the native observed error before arming. Original stdout,
stderr, source bytes and receipt remain under P7_recorder_transport_fix_raw.

The corrected source then passed all 17 affected receiver methods on Windows
and all 17 on Linux, with zero failures/skips. Four new methods cover missing or
conflicting ambient values, the real connected iterator's exact command at the
controlled no-spawn boundary, empty-environment arming and altered private
binding refusal before capture/thread construction. Thirteen existing receiver
ownership/lifetime tests are inherited unchanged; one existing fake dump fixture
now supplies its actual private board field. Tests never launch ADB or upload.
All three source/test input hashes remained stable before and after both runs.
The prior D224 firmware/core and other D225 suites were not needlessly repeated.

## Scope and next action

Independent review 751e30a3 is FINAL PASS. After an exact clean source commit,
one fresh positive-session attempt may run check-only, compile and run in order,
without changing HEAD between compile/run. Every existing live admission and
closing condition remains mandatory; no environment override or old-owner retry.
Actual delivery remains unproved until retained native capture passes. BOARD ONLY
provides no sensor/motor acceptance, physical timing/RAM proof or human phase gate.
