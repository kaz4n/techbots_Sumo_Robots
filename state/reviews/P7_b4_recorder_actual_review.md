<!-- Reviews saved D219 capture and export evidence without executing its subjects. -->
<!-- Separates successful collection from recorder lifecycle and physical qualification. -->
<!-- Validated by independent local byte, packet, scalar and CSV reconciliation. -->
# D219 actual capture review

FINAL PASS, 26 September 2026. No material finding in this bounded actual-result review. This is a separate same-model reviewer using reused project context, not a human or cross-model review. Only saved evidence and source text were inspected; no subject import, test, device action, retry or regenerated capture was performed.

The accepted outcome is one completed read-only capture and local CSV export of an EMPTY recorder. It does not establish a useful match recording, atomic snapshot, initialized hardware or physical B4 behavior.

## Pinned evidence

Paths below are under `state/analysis/P7_b4_recorder_run_raw/` unless stated otherwise.

| Evidence | Bytes | SHA-256 |
|---|---:|---|
| capture_native_invocations01.json | 1919 | c5fbd231a809539172ce91bc7f341a64f94aee3caaf7bdee6f2e3a9393851235 |
| capture_native_closing01.json | 23251 | 4eb576015b18e34b7c4845d43ea9456aa9b1d25ffcb63c6aa8c106a695a871f9 |
| native_capture01/result.json | 58833 | 783d3e995274a2da7664fd815b331e24e4ab353b8c0ca397091eb0532a576a6e |
| native_capture01/capture_result.json | 5423 | 0568c17beb07c530d222e1f32a80c77d1da7baa49d7487eb80eba9fd691a7a27 |
| native_capture01/export.json | 7903 | d7e615c66eab0a79ada798e9bf2637cc8ffce9b09cc2e9f5529077b87ba921b6 |
| native_capture01/0007-retrieve/stdout | 222950 | 0829a13e3e9b08daa31ac8c99c6e453f8d30f718fe27e08913ed21dc22157bda |

The prerequisite manifest remains 47363 bytes / `fbd92f2b91bbece2eff2f98235ef7469098da43bc69651fb162be6536fc108ad`. Prior source/host review `bb218eadd0a500d22082e0cd50cef9bd84eee24eb1989d6a9ec1c1520cbf6d02` and native admission `98546722e03f9e885905e0543539146e3cbc66b329c38b0021aea8656f148b03` remain immutable.

## Actual provenance and closure

All 282 prerequisite files independently matched both current bytes and native HEAD `256dbd5da6661fdf01b6a954c02380cd8c60cc8c`; the prerequisite manifest and admission review also matched that commit. All 171 native input hashes matched current files. The outer driver saved one successful check-only (0.8822424 s) and one execution (268.9295202 s), with no first/closing error, timeout, changed input or changed HEAD.

The ten saved transports reconcile in order: adapter claim, adapter push, initial CLI observation, built-in file observation, capabilities, capture, retrieval, then the same three closing observations. Intents/results, command hashes, fixed timeouts and Windows command bounds match. All returned zero with empty stderr. The sequence is COMPLETED, with exactly one capture and one retrieval, no first error and no postcheck error. The root closing receipt's complete 64-file inventory (863639 bytes) independently matches saved bytes.

The returned envelope and retrieved durable report agree. The original ADB envelope is retained with its CRLF ending; the local canonical envelope has LF and identical parsed content. Strict JSON parsing rejected duplicate/nonfinite forms in the review reader. All 13 retrieval records have exact base64, length, hash and local-file equality; opening/closing identity agrees and all 13 closing file checks completed. Local audit field/serialization assumptions were corrected against saved records without altering evidence or retrying an action.

The COLLECTED report has 26 exact planned reads totaling 852624 requested bytes, no wait operation and no errors. Its four complete loader/sketch comparisons before and after SRAM are true; the five loader and two sketch before/after chunk hash pairs also agree. This review reconciles the executed report and its pinned collection path. The remaining raw flash leaves were not downloaded, so this is not an independent local comparison of those raw flash bytes.

## Raw owner and exported values

The ten saved SRAM chunks assemble, in memory only, to 159200 bytes at address 536954120, SHA-256 `6ef672428954b00d018442c98dec7874da9fd46feb76dfc9452bce634ac1a9e0`. The exact accepted D215/D216 ABI map binds the current B4 artifact and source. All 35 selected little-endian scalar values independently match the decoder: all are zero except `summary_.mode=1`. All nine booleans are zero; the three selected payload/status arrays contain zero bytes.

All 36 summary fields and the OR of all 22 loss terms independently reconcile with the raw values and CSV. Frames contain zero data rows (164 bytes), events zero (54 bytes), and summary one (627 bytes); saved CSV lengths and SHA-256 values match export and closing receipts. Bundle, layout, format, consistency and export status are PASS with no errors. Lifecycle EMPTY, phase 0 and loss NONE_REPORTED describe these bytes; `incomplete=0` does not mean a finished recording or prove loss-free operation outside this empty observation.

The selected epoch token, last-frame token and phase are zero and equal in before/body/after. However, each pair of complete 120-byte brackets differs at offsets 96 and 97. The raw-only u64 at bracket offset 96 (owner offset 159176, `highest_token_` in the accepted layout) is respectively 534757, 583347 and 583483. These unselected bytes remain preserved and do not become decoder lifecycle evidence. Equality of three selected fields does not make the changing owner atomic or coherent.

## Acceptance boundary

Both decoders retain body origin/coherence UNPROVEN; common-attempt, transport-verification and hardware-acceptance flags remain false. Provenance stays ABSENT with UNKNOWN closure/evidence kind. Observed bounded transport completion does not override those conservative declarations. The changing raw field is not proof of successful initialization, a complete epoch, or a completed attempt.

The current artifact remains fixed MATCH0/MOTORS_ALLOWED0 B4 with all setup grants absent. This capture adds no upload, reset, halt or MCU write. It proves neither physical inhibition nor sensor readiness, native UART/Bridge dumping, WCET, live RAM/stack margins, competition performance, phase gates or motor authorization. The existing source/fixture failure evidence remains retained; accepted host tests were not repeated.

`state/analysis/P7_b4_recorder_actual_validation.md` accurately states this bounded outcome and the bracket limitation. Its pending-review status may be updated to reference this acceptance; no circular validation-file pin is required. All writes stop after sealing this review.
