# Exact failed-loader fragment cleanup

The user requested deletion of unneeded temporary files. The only target here is
/tmp/remoteocd/zephyr-arduino_uno_q_stm32u585xx.elf on UNO Q ADB2629958581,
then its empty parent directory. This is board temporary storage, not Windows C:.
No upload, reset, capture, compiler, process termination or service action.

D156 failed before remoteocd launches OpenOCD by versioned source ordering.
The partial file is reproducible: its entire1,048,576 bytes match the prefix of
the retained checked2,303,728-byte loader ELF. Preserve native_run01, original
failure/inventory/prefix-match receipts and full retained loader. There is no
unique data in this temporary copy and no reason to copy it to scarce host disk.

Run remove_failed_fragment.py once, after its exact source review. It admits
only boot6d4aca1b-ac1f-4caf-b1ef-e127ce3956f6, UID1000/aarch64; directory device34,
inode800/UID1000; one regular nonsymlink file device34/inode801/UID1000/mode0664,
size1048576/mtime_ns1790295081758518138/linkcount1 and full SHA256b6fced5c7a35d75e5e5b681ad9806510bb1f066f8097a198b9186d06867d50cf.
Bounded process-name observations must find no openocd, remoteocd or arduino-cli.
Read failures for surviving PID entries abort. Recheck exact file/path and parent
identities immediately before unlink/rmdir, then observe held descriptors' zero
link counts and path absence. Any drift/failure stops; no automatic retry.

These checks are observations, not a global process-quiescence proof or atomic
conditional unlink against hostile simultaneous replacement. The task targets
known task-owned residue after a reaped, failed copy; no other writer is expected.
Keep exclusive local intent plus actual raw result/returncode and reviewed code
hash. Removal does not revive consumed run01 or authorize a new upload. The normal
uploader's preexisting-temp check stays unchanged and requires fresh absence.
