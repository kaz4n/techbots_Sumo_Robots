# Exact failed-fragment cleanup: source review

25 September 2026, Asia/Dubai. Same-model review using D156 failure context;
no execution, deletion, native upload or approval assumption by reviewer.
Reviewed remove_failed_fragment.py SHA256
`3b3d899bb5cb572c8c3b612485c78f8785370265c11b4222e3940c39a60eb2cd`.

**Pre-action scoped source PASS; no open material finding.** Execution still
requires the coordinator's separately recorded exact cleanup scope and fresh
checks. This review does not revive run01 or authorize any upload/capture.

The only candidate is /tmp/remoteocd/zephyr-arduino_uno_q_stm32u585xx.elf,
1048576B/SHA b6fced5c7a35d75e5e5b681ad9806510bb1f066f8097a198b9186d06867d50cf,
matching diagnosis receipt6cca1b01. Exact device34/inode801/UID1000/mode0664,
mtime, regular type and single link are required; the folder is device34/inode800,
UID1000 and contains only that name. The retained loader prefix is reproducible
and independently matched by the four real host-copy tests; failed-run logs remain.

Identity requires the fixed boot, UID1000 and aarch64 before and after hashing.
Two bounded process scans reject OpenOCD/remoteocd/arduino-cli conflicts. Held
no-follow descriptors, bounded hash read and fresh path/descriptor checks precede
one relative unlink. Only then may one relative rmdir remove the empty exact
folder; held descriptors' zero link counts and path absence confirm the result.
Failure retains partial-action flags and exits nonzero; no recursive removal.

Initial missing-comm/PID-disappearance and pre-rmdir identity findings are fixed
at:36-41 and:83-89. These checks detect observed drift; they do not provide atomic
conditional unlink/rmdir, a filesystem lock or global process/MCU quiescence.
Any execution failure/uncertainty is evidence, not permission for an automatic retry.

Actual D159 receipt review: intent29485d09 and resultfb99a50a record one execution
at commit e2fdacf3520bb1fa0d1c9b2dbd2ea7709fca9dd5, UTC00:32:40.643934-
00:32:40.896365. The intent's dispatched source exactly matches reviewed3b3d899b
and the unchanged current source. Returncode0, empty stderr and REMOVED retain
the exact1048576B/hash above, unlinked=true and directory_removed=true on the
required boot. **Scoped cleanup receipt PASS.** This verifies the recorded
completed action, not continuing absence or global quiescence. Failed-run logs
remain evidence; run01 stays consumed and no upload/capture grant follows.
