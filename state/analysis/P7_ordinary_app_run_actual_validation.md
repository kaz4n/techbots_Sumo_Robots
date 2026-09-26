# Ordinary application board observation, 26 September 2026

The single D212 ordinary application upload and passive observation completed at
reviewed commit b5017310b9a93b64fc428327e067af670b5c8b52. The ordinary app source
is 9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a:
static/default, MATCH=0, MOTORS_ALLOWED=0, probe=0, all setup grants zero.

Check-only returned0 in1.3866s; execute returned0 in277.9450s. There was one upload
and one capture,13 transports,28 reads/715858bytes, all four full-image comparisons
and all seven before/after flash-chunk pairs matched. All380 coordinator pins
closed unchanged. Native closure: c843482d. No rebuild, motor-capable operation
or safety-bound change occurred.

One separate file-only retrieval returned0, verified16 saved files and their
closing rereads, and kept all eight local pins unchanged. Packet1fe00614 contains
the exact saved upload/capture reports and14 SRAM windows. Decoder3deb755b returned
DECODED,214 selected scalar observations, no application findings, and coherence
UNPROVEN. Full raw bytes remain in the packet and decoded output.

| Selected Runtime field | First sample | Second sample |
|---|---:|---:|
| phase / fault | RUNNING / NONE | RUNNING / NONE |
| epochs |142768|145878|
| maximum_execution_us |477|477|
| missed_releases |0|0|
| initialization_complete |false|false|

All selected motor duties/pulses are zero and motors_enabled is false in both
sets. Both sets retain Robot BOOT and all21 grant bytes zero. Transaction phase
is ACQUIRING in the first window and IDLE in the second. Native settled_ differs
false/true; these are live bookkeeping samples, not a fault or electrical test.
attempted_ is true, but app.ino does not retain begin's return value. The first
transaction mixes ACQUIRING/decision_made=false/finished=false with
timing_valid=true/execution_us437; the second is IDLE/finished=true with
robot.token0 and feedback.token146278. Preserve these live, potentially mixed
lifecycle values rather than interpreting either window as a coherent transaction.

The sampled epoch count increased by3,110. These separate samples do not prove
uninterrupted execution or reset continuity, and tearing remains unexcluded.
The477us software counter does not establish initialized operational WCET below800us. Missing
hardware grants leave initialization incomplete; sensor, button, IMU, recorder
delivery, motor/ring behavior, live stack/RAM and human gates remain unqualified.
Snapshots may tear, and the MCU continues after collection. No final halt,
reset continuity or physical inhibition is inferred. D195 and D201 failures remain
preserved; this successful observation does not prove an intermittent fault cured.

Evidence: P7_ordinary_app_run_raw/native_invocation01.json,
native_inert_run01/result.json, native_actual_closing01.json,
retrieved_inert_run01/0001-read-saved-results/stdout and decoded.json.
Independent actual review is the remaining acceptance step for this record.


Independent actual review173dd5c2 PASS accepted 2026-09-26T19:05:17.329579+04:00. It reconciles380prerequisitepins,156nativeinputs,13transportstreams,16retrievedfiles and214typedscalars. The user confirms only the board is connected; no sensor/driver/robot qualification follows. D212 is now the latest verified flashed ordinaryM0 application.
