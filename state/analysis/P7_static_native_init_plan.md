# D151: observe only the missing device-init wrapper

D150 is terminal FAILED, not retried: GDB returned zero but emitted
`No function contains specified address.` and the by-name disassembly section
was empty. Its other 49 sections remain partial evidence. The same failed name
lookup already exists in P2_adc_ownership_raw/installed_02.json records[12];
records[13] successfully disassembles do_device_init at 0x08019e2c, including
the load/call of device.ops.init at offset20. D150's `whatis` returned a const
void pointer for the exported name, so name resolution cannot identify the body.

Retained P2_dump_raw/native/native_symbols.txt gives the actual function start
0x08019e5c and next symbol 0x08019e6e; the P0 PWM export record independently
gives the Thumb pointer0x08019e5d. Observe exactly those18 bytes, rather than
repeat the unsuccessful name query or infer the wrapper-to-helper branch.

After scoped review, run hash-bound read_native_init.py once with Python-B.
It composes the unchanged D143 before/after identity/source/file and installed
hash checks around one GDB query: `disassemble /r 0x08019e5c,0x08019e6e`.
Use the pinned packaged loader and GDB, -nx -nh -batch, object auto-loading off
before opening the file, no target/inferior/call. Preserve first failure,
independent postchecks, complete small output and source hashes before/after.
Fresh exclusive native_init receipts; no retry or compiler/upload/reset/write.
Local preparation/positive and negative marker checks make zero dispatches.

This closes only a missing file-evidence edge if the actual instructions show
it. D150's original failure stays unchanged. No production/test/config edits,
static adoption, live-memory/timing/startup, motor run or physical/human gate.
