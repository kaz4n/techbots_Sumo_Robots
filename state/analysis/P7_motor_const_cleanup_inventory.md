# D201 uploader scratch inventory

One nonprivileged read-only inventory completed successfully after source review
P7_motor_const_cleanup_inventory_review.md (5672 bytes / dd2bce49). The observer
is the exact five-substitution D200 derivative, 9769 bytes / 462c0534; all five
bound input files remain unchanged. No credential or firmware operation ran.

The saved admission01.json is24555 bytes / addee38e. Both
expected_originals_match and exact_three_d201_copies are true. The scratch
folder /tmp/remoteocd is currently device34/inode1452, UID/GID1000, with exactly
three files totaling2399928 bytes:

| File | Inode | Bytes | SHA256 prefix |
|---|---:|---:|---|
| app_motor_observe.ino.bin-zsk.bin | 1454 | 95520 | e4000781 |
| flash_sketch.cfg | 1455 | 680 | 38706cee |
| zephyr-arduino_uno_q_stm32u585xx.elf | 1453 | 2303728 | 39d4a4fd |

All bytes match their retained originals. The package is the D198 image uploaded
by D201, under app-motor-settle-static01; its basename still contains observe.
Scratch and original descriptor/path identities close unchanged, expected board
identity and boot agree, and all five closing checks pass. The local input
closure passes, transport returns0 with empty stderr, and the command is18657
UTF-16 units within30000. No recognized compiler process names were observed.

Protected process cwd/fd handles were not inspected. This inventory does not
establish that the files are unused and does not authorize deletion. A future
cleanup must bind these fresh identities, recheck them and protected handles,
preserve originals, and use a new attempt owner; D200/root04/inode1172 are
consumed. The existing upload guard refuses an occupied /tmp/remoteocd.
No file was deleted and no storage recovery is claimed.
