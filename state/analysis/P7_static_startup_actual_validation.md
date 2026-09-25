# D156 actual inert startup attempt: failed upload

**FAILED / scope consumed / zero capture attempts.** The one identified run at
04:11 Dubai on25 September used reviewed HEAD e173053c and unchanged M0 source
fcddbd8e. It did not establish current-image startup or any physical gate.

The [invocation](P7_static_startup_raw/native_invocation.json) returned1. All nine
numbered transport calls returned0 with empty transport stderr: four admission
checks, the upload wrapper, and four independent final checks. The wrapper
correctly reported a failed child; transport success is not upload success.

The [result](P7_static_startup_raw/native_run01/result.json) retains:

- One upload attempt; child exit1, reaped true, timed_out false.
- Uploader diagnostic: `write /tmp/remoteocd/zephyr-arduino_uno_q_stm32u585xx.elf: file too large`.
- Upload FAILED; no capture intent, dispatch or MCU samples.
- Empty postcheck errors; source, original packet, installed hashes, prerequisites
  and reviewed HEAD remained unchanged in the recorded checks.

The cause is a host-tool policy defect. D154 installed D153's1,048,576-byte
RLIMIT_FSIZE in the CLI child, which also limits files written by descendants.
The required loader ELF is2,303,728 bytes. Thus the cap prevents the uploader's
temporary loader copy; the mock-based host suite did not model this operation.
The software review/tests were insufficient to establish this native boundary.

Pinned remoteocd0.1.1 copies binaries, then configs, then invokes OpenOCD.
A binary-copy failure returns before that invocation. This supports a
source-based inference that this particular error occurred before OpenOCD
launch; it is not a direct MCU-state observation or global quiescence proof.
The separate [actual review](../reviews/P7_static_startup_actual_review.md)
retains the MAJOR policy defect and verifies failure containment.

A subsequent [file-only inventory](P7_static_startup_raw/failed_upload_temporary_inventory.json)
returned0 on the same boot. /tmp/remoteocd (device34/inode800) contains exactly
one regular, nonsymlink loader file, inode801/UID1000/mode0664, exactly1,048,576
bytes, SHA256b6fced5c7a35d75e5e5b681ad9806510bb1f066f8097a198b9186d06867d50cf.
It remains on the board as partial failure evidence. No deletion, retry,
additional reset or capture followed the failure.

The [local prefix check](P7_static_startup_raw/failed_upload_fragment_match.json)
confirms those bytes match the first1MiB of the existing fully hash-checked loader
ELF under P2_ui_adc_probe_raw/root_capture_inputs. No additional firmware copy or
board call was needed for that check.

Next task: design and test an upload-specific finite file cap compatible with
the largest pinned copied input (2,303,728 bytes). Keep D153 capture unchanged.
The smallest correction may retain the <1MiB diagnostic acceptance limit while
explicitly permitting larger transient stream files; do not claim that this
preserves the old physical stream ceiling. The real harmless child/descendant
copy regression now passes4/4 cases,0.393s/exit0: original-cap failure reproduces
the exact prefix; exact2303728 succeeds; one byte beyond fails and one byte below
succeeds. [Frozen source/reference](P7_static_startup_raw/file_limit_freeze.json)
and [first result](P7_static_startup_raw/file_limit_first.json) remain unchanged.
Both uploader stream boundaries and the replacement entry still need validation.
Preserve all original scopes, sources, assertions and failure evidence in their
historical context. A later reviewed scope must handle the known temporary
residue and use fresh one-shot ownership; D156 must never be rerun.

No production firmware, pin, configuration, locked test, capture helper, release
tag or human gate changed. Last known successful MCU upload remains D118; this
failed D156 invocation does not establish current MCU contents or readiness.
