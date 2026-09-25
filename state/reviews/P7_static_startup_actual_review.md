# D156 actual startup attempt review

25 September 2026, Asia/Dubai. Same-model review reusing earlier design/code
context. Local receipts and pinned-version upstream source only; no board
command, retry, cleanup, source change or new MCU observation by this reviewer.

**Disposition: D156 FAILED and consumed; failure handling evidence accepted.
One MAJOR upload-policy defect blocks another native startup attempt until a
separate repair/test/review and new identified run scope.** No capture occurred.

Reviewed actual launcher invocation at HEAD
e173053c52b7aff4fec3c6f93a9e4c8a1cc6b2f6, native_invocation.json SHA256
`d2e524995ab04eac78dc4a694f753e2821c6222d8d68daef049733dfd282242a`:
one invocation, exit1,00:11:16.566224..00:11:24.484123 UTC.
native_run01/result.json SHA256
`fff23bd0f0e2fcbab4f5148f5ddc2af6f429c8167600b3ab53b11cf4f5ed06ba`
retains upload_attempts1, capture_attempts0, captureNone, statusFAILED. The
upload child returned1, timed_outFalse, reapedTrue; its report is FAILED with
stderr identifying a file-too-large write to
/tmp/remoteocd/zephyr-arduino_uno_q_stm32u585xx.elf. The host's first error is
"Wrong report status"; it also preserves the complete failed upload report.

All nine numbered transport receipts return0 with empty transport stderr:
four prerequisite dispatches, one upload wrapper, four final file checks.
Transport success is not child/upload success. Final result postcheck_errors,
local/prerequisite error lists are empty; query/compile attempts0. Independently
compared before/after packet claim, identity, source and FileRecords: unchanged.
final_checks.json SHA5e2fa837dcc7116109e65f1fbaf130600d637c4e0850b9114ef4087342d685de.
The host and remote upload claims remain consumed; capture was never attempted.

R1 **MAJOR: inherited file cap prevents a required loader copy.** Frozen
upload_remote.py:342 uses support.limit_child_output; capture_remote.py:122-123
sets both RLIMIT_FSIZE limits to1048576. The pinned loader ELF is2303728B.
RLIMIT_FSIZE limits regular files the process can create/extend, not just its
stdout/stderr; descendants inherit it across fork/exec. This explains the
observed write failure without a firmware defect inference.
[Linux getrlimit(2)](https://man7.org/linux/man-pages/man2/getrlimit.2.html).
The frozen D154 contract required this reuse; its mocked tests asserted the
limit but did not exercise the uploader's legitimate multi-megabyte copy.
Prior host PASS receipts/reviews remain historical evidence, not native proof.

MCU boundary: remoteocd0.1.1 flash.go:27-30 returns immediately when pushFiles
fails; pushFiles:49-53 returns the copy error. Its OpenOCD invocation is later
at:39, after both binary/config copying. LocalCmd.CopyTo performs a file copy;
the board-local upload branch calls this flash sequence.
[flash.go](https://github.com/arduino/remoteocd/blob/0.1.1/flash.go#L20-L53),
[local.go](https://github.com/arduino/remoteocd/blob/0.1.1/board/local.go#L19-L35),
[main.go](https://github.com/arduino/remoteocd/blob/0.1.1/main.go#L70-L109).
Therefore this observed loader-copy error precedes OpenOCD launch in the
audited remoteocd path: that path did not reach its flash/reset/activation
recipe. This is source-order inference, not a direct MCU trace, confirmation
of unrelated-process inactivity, current loaded image or global quiescence.
No static startup observation or successful MCU programming follows.

Recommended next scope, with all original code/receipts/reviews preserved:

- Prepare a separate upload revision with its own finite regular-file cap,
  minimum2303728B for the pinned loader, without changing frozen D153's cap.
  Keep stdout/stderr acceptance strictly below1MiB; explicitly allow larger
  transient stream files up to the upload cap before rejection. Retain the
  one-child deadline/group-reap behavior and unchanged upload selection.
- Add a real Linux host subprocess regression under that cap, copying exactly
  2303728 synthetic bytes and exercising descendants, plus oversized-stream
  rejection. Preserve the old failure and freeze new expectations first;
  mocked setrlimit assertions alone cannot cover this integration defect.
- Keep run01 consumed. Any future attempt needs fresh paths, reviewed hashes
  and a separate concrete scope. Possible /tmp/remoteocd residue is evidence:
  inspect it file-only before any explicitly scoped handling; do not silently
  delete, overwrite or reuse it to satisfy the old absence guard.

No repair, new run grant, cleanup or retry is performed or implied here.

Later separate file-only diagnosis (not another D156 dispatch), receipt
failed_upload_temporary_inventory.json SHA6cca1b012a87355064632e3b9c4c3682f72d15b187e5593cd68a2ec074ecb1b9:
COLLECTED, exit0/empty stderr, same boot. Exactly one regular nonsymlink loader
ELF exists under /tmp/remoteocd,1048576B, UID1000/mode0664, inode801;
directory device34/inode800. File SHA256
`b6fced5c7a35d75e5e5b681ad9806510bb1f066f8097a198b9186d06867d50cf`.
Its exact cap-sized truncation corroborates R1; it is not a complete loader or
MCU-state observation. The minimum cap above refines the earlier4MiB example;
at that checkpoint, copy/boundary regression and replacement code/scope remained pending.

Later bounded host proof: reviewed test_upload_file_limit.py SHA163ed282,
file_limit_freeze.json SHAf995f952 and matching file_limit_first.json.
Freeze preceded execution; all four cases PASS, exit0/0.393s, both source and
loader-reference pins unchanged. Actual Linux parent/descendant processes copy
the retained loader into owned /dev/shm scratch:1MiB reproduces EFBIG and the
exact b6fced5c prefix;2303728B permits the full39d4a4fd copy; limits one byte
below/above that size fail/succeed as expected. This closes the copy-boundary
regression only. It does not execute or repair the uploader, test larger-stream
acceptance, authorize cleanup/retry, or supply native startup evidence.
