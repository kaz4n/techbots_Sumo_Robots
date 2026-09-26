<!-- Records the one actual inhibited B4 retained-memory capture and CSV export. -->
<!-- Keeps empty recording, coherence and physical qualification separate. -->
<!-- Validated against saved native results, exact input pins and independent review. -->
# B4 retained-memory capture and CSV export

26 September 2026. The fixed motor-disabled B4 application was loaded by D221.
D219 then completed one read-only capture and local CSV export on the bare UNO Q
at clean commit `256dbd5da6661fdf01b6a954c02380cd8c60cc8c`. The result is a
successful collection/export path with an **EMPTY recorder: zero frame rows,
zero event rows and one summary row**. It is not a match recording or a physical
B4 trial. No sensor or motor hardware was connected according to the user.

The [independent actual review](../reviews/P7_b4_recorder_actual_review.md) is
FINAL PASS for this bounded collection/export outcome (review SHA-256
`25b53987ddbda8de83b5e9f1122abf8e98ab3e583e66c0a6b409a4a5adafc4b5`).
Native capture, upload
and cleanup owners are consumed; do not repeat them to recreate this evidence.

## Actual evidence

- [Invocation receipt](P7_b4_recorder_run_raw/capture_native_invocations01.json):
  one successful check-only (0.882 s), then one execution (268.930 s); no first,
  closing or changed-input errors. All 282 prerequisites matched current files
  and the native commit byte for byte.
- [Root closing receipt](P7_b4_recorder_run_raw/capture_native_closing01.json),
  SHA-256 `4eb576015b18e34b7c4845d43ea9456aa9b1d25ffcb63c6aa8c106a695a871f9`,
  pins all 64 saved attempt files (863,639 bytes). Ten bounded transports returned
  zero with empty stderr; one capture and one fixed retrieval were dispatched.
- [Full capture report](P7_b4_recorder_run_raw/native_capture01/capture_result.json),
  5,423 bytes, SHA-256 `0568c17beb07c530d222e1f32a80c77d1da7baa49d7487eb80eba9fd691a7a27`,
  records COLLECTED, 26 reads totaling 852,624 requested bytes in 256.835 s.
  Complete loader and B4 sketch comparisons passed before and after the SRAM
  reads. The report was retrieved and matched the returned envelope. The host
  retained the prescribed 13 report/SRAM leaves; remaining raw flash leaves
  remain on the board.
- [Export report](P7_b4_recorder_run_raw/native_capture01/export.json) records
  bundle, layout binding, format integrity, owner-summary consistency and CSV
  export PASS with no errors. The ten chunks assemble a 159,200-byte owner at
  address 536954120, SHA-256
  `6ef672428954b00d018442c98dec7874da9fd46feb76dfc9452bce634ac1a9e0`.
  No duplicate assembled owner file was created.
- Actual CSV files: [frames](P7_b4_recorder_run_raw/native_capture01/frames.csv)
  (164 bytes, header only), [events](P7_b4_recorder_run_raw/native_capture01/events.csv)
  (54 bytes, header only), and [summary](P7_b4_recorder_run_raw/native_capture01/summary.csv)
  (627 bytes, one data row). Lifecycle is EMPTY, phase 0, loss NONE_REPORTED.
  `incomplete=0` does not establish a finished recording.

## Interpretation and limits

The selected epoch token, last-frame token and phase are zero and agree across
before/body/after. The complete 120-byte lifecycle brackets differ at offsets
96 and 97. Raw-only little-endian u64 values at offset 96 are 534757, 583347 and
583483 respectively. These bytes are retained without promoting that internal
field into decoder status. The changing brackets do not establish an atomic or
coherent snapshot.

Both decoders retain body origin and coherence UNPROVEN, common-attempt,
transport-verification and hardware-acceptance flags false, and provenance
ABSENT/UNKNOWN. The observed bounded transport completion is not a reason to
change those declarations. Firmware remains the checked B4 static/default
MATCH0/MOTORS_ALLOWED0 profile, all setup grants absent, source digest
`9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a`.
No reset, halt, MCU write or motor authorization was added by this capture.

Native UART/Bridge log delivery, initialized worst-case execution time and live
RAM/stack margins, sensor/button/battery calibration, motor/edge/ring trials,
operator rehearsal and human phase gates remain open. This MEM-AP retrieval
also does not replace the original B15/P2 B8 IDLE dump requirement. Review the
[current completion packet](P7_software_acceptance_packet.md) before deployment.

D220 removed the three verified stale D212 upload copies (2,397,352 bytes).
D221 recreated upload scratch with an unobserved current inode/content inventory;
it remains retained. Automatic approval review previously blocked deletion of
the 764,405-byte local B4 staging copy with reason "blocked by policy". That copy
is retained without retry; see the [saved block receipt](P7_b4_app_compile_raw/local_stage_cleanup_blocked01.json).
