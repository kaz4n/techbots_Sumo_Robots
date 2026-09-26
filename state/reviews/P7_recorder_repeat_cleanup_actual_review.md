# D239 actual exact-scratch cleanup review

**PASS: the identified three stale D237 upload copies and their empty directory
were removed with the required retained-original and closure evidence.** No
material blocker found. This accepts the completed cleanup only, not the outcome
of any later compile/upload/delivery attempt.

Evidence is MAIN `state/analysis/P7_recorder_repeat_cleanup_raw`. The accepted
preparation manifest SHA256 is
`38c40bb89d4ac126f0754da8f22047fe3dc2af6a15b8e426f54852d5ae0ae8f2`; its source
review is `aad639c7ae926ba53aedc6a48a0a87d7a09fa5f1f171c9b65f5a4edd09b90e8c`.
The actual 6539-byte dispatcher, SHA256
`6237779c4cae4f914a62476ea0e577b35ea3ffdbda50afdb1dcfe1a698b9e002`, independently
equals the reviewed template with only those two hash substitutions. The binding
receipt agrees. All 63 distinct inputs recorded across the five actions still
match their exact sizes/hashes; every action reports successful local closure.

## Actual sequence and identity

Absence, stage, verify, authenticated and retrieve were invoked once each, with
ordered durable intents at 22:25:12.845018, 22:25:13.364073, 22:25:13.871791,
22:25:18.647574 and 22:25:39.206405 UTC on 2026-09-26. All five return zero,
have empty stderr, null first_error and empty closing_errors. Authentication's
empty stdout is consistent with its fixed redirection to result_root01.json.

The fresh remote stage is
`/home/arduino/sumox26_codex_build/cleanup-recorder-repeat-root01`, device
66341/inode 283669, mode 0700 and UID/GID 1000. Verify/retrieve bound programs
independently reproduce from their reviewed templates using only the successful
stage identity and verified source identities. The actual argv embeds those
exact bound programs. Staged source identities remain identical through both
independent verification and retrieval before/after records.

The deletion target is `/tmp/remoteocd`, device 34/inode 7093, UID/GID 1000.
Its saved initial directory stamp and all three file identities/hashes exactly
equal fresh admission SHA256
`18b59196f50a3fb9bc098a74339ee35844cbbe780c0753ea9fa4992328f5a524`.
The result lists exactly:

- flash_sketch.cfg: 680 bytes.
- recorder.ino.bin-zsk.bin: 55376 bytes, SHA256
  `3b4812a7a57ec964437d6d1048f96724e3fed5d0a3f9419acd26adbcd5e70a5d`.
- zephyr-arduino_uno_q_stm32u585xx.elf: 2303728 bytes.

The independently summed removal is 2359784 bytes. directory_removed is true;
there is no broader removal list. The recipe's embedded stdout decodes exactly
to its structured cleanup_result, with cleanup_returncode=0 and first_error=null.

## Protected scans, originals and result closure

Three retained pre-unlink observations each report 165 process names and three
same-UID handle inspections, with no errors. Each begins and ends with real and
effective UID/GID 1000 and saved root IDs; effective UID alone is zero during its
read-only observation. The reviewed unchanged wrapper restores Arduino
credentials before each deletion. Final real/effective/saved UID and GID are all
1000, with empty privilege_drop_errors. The scan's stated visibility limitation
is retained; this is not a broader process-use clearance claim.

Independent verification has six closing PASS records. Independent retrieval
also has six: stage/result reopen, scratch-absence reopen, originals reopen,
board identity, credentials and root descriptor close. Retrieval observes scratch
absent before and after. Original records match the fresh admission exactly in
verification and retrieval before/after; the recorder build original and installed
config/loader are retained. Board boot and Arduino identity remain unchanged.

The saved authenticated result is 6354 bytes, SHA256
`30b958cb8126a13e7db34bc07df6fad768a73860187592ae1f5a24a2fe6b7c01`, status
REMOVED_EXACT_STALE_COPIES. Its bytes exactly equal the decoded independent
retrieval payload. Root's separate 347-byte closure also reconciles, SHA256
`a3a8e620b93e431d6296811da738289b81b63a7e49037f8d76a30dbf6fe566e4`.

Principal action receipt SHA256 pins:

- absence: `d8fa61558d7aa63cd3423a8d0e9aca6939bcd0f2d052fe48026164a98d13d44a`.
- stage: `cf419afe2b9393cb7f242dc22fef9ebac95ef5bde1ce1afba72c1219279d0da5`.
- verify: `ae9fa2961d577e04f7d81d58a450c25a63c65af70535e9f1a8119cc309f1760f`.
- authenticated: `3f0df995ebea1ea6cf914224c13da968189027823884977bd92195551a7dde1a`.
- retrieve: `c3933071c8822e8b2538e89840b45a9784c6151a249540dd4ebde2e16b029e75`.

The completed owner remains consumed. Absence is established at these closing
observations, not promised after a future uploader recreates scratch. No MCU
state, UART repair, delivery success, motor permission or phase gate follows.
The separate fresh D239 compile is outside this report. Reviewer performed
local read-only reconciliation only, no native command, test, credential action
or deletion, and wrote only this actual-review file.
