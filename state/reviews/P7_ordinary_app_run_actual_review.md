# D212 ordinary application actual observation review

FINAL PASS for the bounded collection, saved-file retrieval and scalar interpretation, 2026-09-26. No material discrepancy remains within this scope. This is a same-model, reused-context review, not a fresh-context, cross-model or human review. The reviewer previously prepared the ordinary observation contract and reviewed the caller. This audit independently read the actual receipts and decoded the saved scalar bytes without importing or running the production interpreter. Only this review was written; no tests, compiler, device commands or firmware changes were performed by the reviewer.

## Evidence identities

Paths below are relative to `state/analysis/P7_ordinary_app_run_raw/`.

| Evidence | Bytes | SHA256 |
|---|---:|---|
| `native_invocation01.json` | 1171 | `8a6b9127a11adcbc85b6cd95552500e868e598b7ad9ea6e6493f82b2201b1bb3` |
| `native_inert_run01/result.json` | 59671 | `c41453c23373e7a24215acfff7e95d80b27e4a34eb4abddbe0d65a236293825f` |
| `native_inert_run01/final_checks.json` | 50241 | `b7ce87a3b8d7adc1e9740bd95a3e9ab7120dcf87e9b889b8b0de45c493e040dc` |
| `native_actual_closing01.json` | 10473 | `c843482de7bd0105080fa7e9a8e1280ee21f142cad2ac78cc0567e93e0928cc4` |
| `retrieved_inert_run01/0001-read-saved-results/result.json` | 20200 | `9c1abca5b147dd858328a1cb12d86e959681aa170a56dd6c2a6ab5a61b28f071` |
| `retrieved_inert_run01/0001-read-saved-results/stdout` | 20172 | `1fe00614a1c3324432ec24aa416f346fb910151e5ecea8e18364aee99b20649b` |
| `ordinary_scalar_map01.json` | 42416 | `d8f4eb7eb36430cff975e3032168fa61f2c249e55596401a67862b272bb08fb7` |
| `retrieved_inert_run01/decoded.json` | 61257 | `3deb755b3c3d1e32507768c02a7236ded53c5dc9ae57fa1b0c3b5c12f166bbdd` |

## Native attempt and closure

The recorded clean reviewed HEAD is `b5017310b9a93b64fc428327e067af670b5c8b52`. Python `-I -B` check-only returned0 in1.3866 seconds; the one execute invocation returned0 in277.9450 seconds, with empty outer stdout/stderr. The source remains `9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a`: ordinary app.ino, static/default, MATCH0, MOTORS_ALLOWED0, probe0 and zero setup grants. The accepted D208/D209/D210 compile, ABI and entry provenance remains exact. This attempt used the existing artifact; it did not compile firmware.

I rehashed all380 coordinator prerequisites, all11 scope-role files and all156 native input hashes. All matched. The source manifest still contains125 pins; the three capability observations agree byte-for-byte and report104 mapped source files totaling764405 bytes, independently matched to current source bytes. The final diagnostics JSON equals the diagnostics embedded in the result. All44 saved Git records have successful return/empty errors; HEAD and scope remain fixed, with only this attempt's owned evidence appearing as untracked files after owner creation. There are no local, prerequisite, transport, finish, first-error or postcheck errors.

All13 actual transport intents, argv, result records and stdout/stderr hashes match the closing inventory. There is one adapter claim/push, three rounds of the three fixed inventory/capability queries, one upload and one capture. Every transport returned0 with empty stderr. Upload and capture command sizes are29662 and28722 UTF-16 units including NUL, below the unchanged30000 ceiling; their outer bounds remain195 and630 seconds. All three initialization observations, all three builtin observations and all three capability observations are individually identical within their categories. The returned action envelopes equal the saved upload/capture transport stdout JSON.

The upload report records one attempt, UPLOADED, reaped child return0 and no timeout. Its full1799-byte saved report hashes to `409725db096f931e62fcd44f257afdb311cd72e1fe8b24c8b0cfa57f2560c3ed`. The retained OpenOCD transcript includes its debug-request halt during upload and extra erase-range warning; neither is erased from the evidence or confused with a passive-capture halt. The package binding remains92944 bytes / `7fa9d41da043931e1237712e1e88bda4151c82933af2ecec97ce3a02184d23ad`.

Capture is COLLECTED with28 commands/reads requesting715858 bytes. I independently reconstructed the exact order, names, addresses, lengths and numbered filenames: five loader chunks and two package chunks before, two sets of seven SRAM windows, two package chunks and five loader chunks afterward. Each full loader interval is263680 bytes, each package interval92944 bytes, and both SRAM sets total2610 bytes. All seven matching before/after chunk hashes agree. The saved remote comparator records all four complete-image comparisons true against the pinned images. Those remote comparison records are retained evidence; this review did not retrieve or independently rehash the entire flash byte payload. The recorded capture span is247.985620775 seconds, pre-sample delay30.000397796 seconds and inter-set delay2.000443840 seconds. No extra capture, adaptive polling or retry appears.

## Saved-file retrieval and independent scalar reconciliation

The separately reviewed retrieval ran once, returned0 in0.35745 seconds and kept all eight local input pins exact. Its argv equals the fixed intent, with18059 command units and75-second outer bound. The packet records full identical before/after identity, including board scope2629958581, arduino UID/GID1000 and boot `55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`. It contains exactly16 distinct files and16 closing rereads: the two reports and14 SRAM windows,12235 payload bytes total. I strictly base64-decoded each file and checked its length/hash/path against the intent and native envelopes. Both parsed reports match the native returned reports, allowing only the intentionally omitted upload stdout/stderr in the compact envelope. The retrieved capture report is7826 bytes / `1c15e030e2b20e0044aec9da5bc2a0d2ba805ea453c1471599a09a384303ca89`.

Using only the frozen map, Python integer byte conversion and IEEE754 unpacking, I independently checked all214 selected scalar observations:107 across each seven-window set, not107 per window. Window field counts are10 report,36 transaction,9 previous,15 gate,21 grants,1 attempted and15 motor-port. Every raw window, scalar raw hex, unsigned integer, typed value, enum label and issue list equals decoded.json. Every observed boolean is canonical and every selected float finite. The decoder's packet/map hashes, report copies, DECODED status, null decode error, empty application findings and seven repeated-field comparison results match the raw evidence. Only grants and attempted have equal selected fields between sets; the other five differ. The three unselected attempted-word neighbors, all padding, pointers and other members remain opaque.

## Observed application values and limits

| Selected observation | First | Second |
|---|---:|---:|
| Runtime phase / fault | RUNNING / NONE | RUNNING / NONE |
| Runtime epochs |142768|145878|
| Runtime maximum_execution_us |477|477|
| Runtime missed_releases / service_passes |0 / 0|0 / 0|
| Runtime initialization_complete / raw_lines |false / true|false / true|
| Transaction phase / fault |ACQUIRING / NONE|IDLE / NONE|
| Gate last_token_ |143437|146561|
| Native settled_ |false|true|

Both sets have21 zero grant bytes, attempted_=true, Robot BOOT, zero Robot contract-fault bits, escape fault NONE and match_start_eligible=false. All selected Robot/applied/previous duties and native PWM pulses are zero; all selected motors_enabled values are false. Gate initialized_ and began_ are true, armed_, hold_complete_ and halted_ false, and gate fault NONE. Native enable_configured_/enable_low_ are true, configured/written masks15, initialized timers7, active channels15 and PWM indices1,2,3,6. Both transaction and gate halt records show attempted=false and inhibition_confirmed=false. These are sampled RAM bookkeeping values, not electrical verification or a final-inhibition receipt. Source writeEnable/writePwm clear settled_ during ordinary transactions, so its differing sample does not itself record a callback failure.

Coherence is UNPROVEN, including within a single window. For example, the first transaction window contains ACQUIRING with decision_made=false/finished=false, yet timing_valid=true and execution_us437. The second contains IDLE/finished=true and robot.token0 while applied.feedback.token is146278. Current Transaction::open clears the report, while completion fills fields before setting IDLE; these live reads cannot be treated as coherent completed transactions. Distinct tokens across the separately read windows likewise do not identify a common epoch. Empty application_findings means the decoder's bounded scalar checks raised no listed finding, not that cross-field consistency or every application invariant was established.

The sampled epoch integers differ by3110. This is sampled arithmetic, not proof of continuous advancement, elapsed runtime, no reset or uninterrupted health. The477-us software maximum is not initialized operational WCET qualification. Zero grants and source readiness conditions explain why RUNNING can coexist with initialization_complete=false and BOOT; they do not establish sensor, button, IMU or recorder readiness. attempted_ is not begin()'s unretained return value. No phase, initialization or FAULT value is a cleanup/publication barrier.

The ordinary firmware has no diagnostic terminal freeze or limit-triggered abort; the host capture ends without ordering a final halt. Its subsequent state is not measured here. The user's board-only setup does not supply missing peripheral measurements. Physical inhibition, motor/ring behavior, stack/RAM margin, competition readiness and human gates remain unqualified. Historical D195/D201 failures and the D212 host-fixture failures stay preserved; this observation does not establish that an intermittent failure is cured. PASS closes this finite observation and its interpretation only. Writes stopped after the final seal.
