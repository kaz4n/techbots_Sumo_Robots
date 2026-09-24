# P3 software preparation and deferred physical acceptance

Software scheduling proceeds under D051/D122 and the user's instruction to defer
hardware testing. This packet does not close GATE P3. The original seven physical
criteria remain in `docs/prompts/P3_first_drive.md`.

| P3 criterion | Software available | Evidence still required |
|---|---|---|
| 3.1 Fifty legal starts | Actual receipt-derived START/FIRST recorder markers; D127 tested offline analyzer | Fifty identified actual starts; each first applied duty at least 5.1 s after release; spread strictly below 5 ms; qualified recordings |
| 3.2 R_room | Original hardware measurement procedure | Three front and three per rear corner measurements, from first white to loss boundary |
| 3.3 Stopping table | D126 finite stopping profile, all five duties, full edge escape, real Governor/Gate | Three actual runs per duty, voltage and original at-rest distance; supplemental compatible peak/R_room measurements under SC-AN; evidence-backed cap approval |
| 3.4 Turns | D124/D125 finite signed 90/180 degree trials, real IMU/fallback, finite brake | Five actual trials per angle/direction within 5 degrees; measured fallback timing coefficient |
| 3.5 Edge escapes | D123 SEARCH/edge profile and existing full escape controller | Eight approach angles, three runs each; 24/24 stay in at approved cap |
| 3.6 Brown lines | Actual line classifier/events | Ten actual crossings, zero false edge events |
| 3.7 Solo reliability | D123 continuous SEARCH without combat/openers | Twenty actual 60-second runs, zero exits/resets and observed deliberate pattern |

Completed implementation receipts: D123 `feca04dc`, D124 `0366d1d7`, D125
`f39c9929`, D126 `6b4c353b`. See their validation and separate review files.
All ten host targets pass at D126. New stopping profile and default app compiled
on the UNO Q Linux toolchain with compile-only policy; no MCU operation occurred.
Target compilation is not a motor or ring test.

For later measurements, identify the exact build/config, target, session and run,
and retain raw observations/logs. Each motor-capable upload/run still requires
fresh identified STAND OK or RING OK. Source/pin/electrical readiness must be real;
software overlays and user scheduling assumptions cannot supply those grants.
No additional hardware connection is requested now.

Do not derive translation from duty alone. Preserve both the original at-rest
measurement and separately observed peak outward excursion; do not infer their
offset after reverse/pivot escape. No-edge timeouts do not qualify a stopping run.
The precise turn/stopping report timestamps are not serialized by the existing
25 Hz frame format; use real external timing/angle evidence where needed. A
programmed fallback duration divided by its requested angle is not calibration.

The real P3 gate still needs physical criteria 3.1-3.7, evidence-backed tuning,
independent review without safety blockers and a human GATE P3 PASS record.
The original end-of-28-September scope-cut rule remains based on that real gate.
