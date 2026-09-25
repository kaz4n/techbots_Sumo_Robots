# One inert static startup observation

Target: standalone UNO Q, ADB2629958581, expected boot
6d4aca1b-ac1f-4caf-b1ef-e127ce3956f6, Arduino Linux UID1000/aarch64.
The user reports this board alone and permits testing it. This scope uses that
permission and D051 engineering delegation; it grants no motor-capable run.

Operation static-fcddbd8e-run01 uses D155 launcher6f86e645 and its scoped
review26fcf2f7. The committed native_run01_scope.json binds the five exact
launcher/independent-test/contract/design-review/code-review files. CLI
--reviewed-head must equal the commit containing that scope. No scope exists
for a second attempt; neither a failure nor a transport interruption permits retry.

Firmware is the existing D144 static/default **MOTORS_ALLOWED=0** image, source
fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2,
artifact run f0220228320c4b2aa20c3e5e8264c813. No rebuild or firmware change.
The raw CLI selector app.ino.bin has SHA256bd03c2e7; its static upload sibling
app.ino.bin-zsk.bin has93096 bytes/SHA2565f08afe0. Final ELF5cc2dfde and original
directory/FileRecords remain checked before and after. Installed loader ELF
39d4a4fd supplies the complete physical reference263680 bytes/SHAe9322826.

Exactly six allowed command forms: original source/artifact packet check,
26 installed hashes, both frozen F166 file-only inventories, fixed D154 upload,
and conditional D153 capture. A clean run uses14 dispatches: four admission
checks, upload, four intermediate checks, capture, four final checks. Local
HEAD/source/transport and durable attempt checks also run; no compiler command.

The one upload uses the reviewed CLI static recipe with empty configuration and
fixed minimal environment. Its intrinsic OpenOCD sequence may program the
packaged loader and sketch, reset the MCU, wait100ms and write0xCAFFEEEE to
0x40036400. Those intrinsic actions are within this inert scope. No extra reset,
activation command, privilege change, recovery, upload or retry is permitted.
Remote upload budget180s, child120s and owned-group reap5s; host timeout195s.

Only a strictly successful upload report and clean intermediate checks permit
the separate capture. It performs exactly18 passive MEM-AP reads/713656 bytes,
checks complete loader/sketch flash before RAM and again afterward, and observes
two runtime/transaction prefixes separated by at least2s. Remote budget600s,
each read30s/+5s reap; host timeout630s. It does not halt/reset/write MCU memory.

Raw capture bytes and command receipts remain at
/home/arduino/sumox26_codex_build/static-startup-fcddbd8e-run01-capture;
upload receipts at the same prefix ending -upload. Local exclusive records go
to state/analysis/P7_static_startup_raw/native_run01. No duplicate binary export.

Any failure preserves available evidence, runs independent permitted file-only
final checks and ends the attempt. Unknown upload outcome suppresses capture.
COLLECTED/COMPLETED mean completed evidence collection; the decoder separately
reports progress, no progress, sampled fault or invalid/mismatched evidence.
Observed progress is not whole-robot WCET, free-memory, pin-map, sensor, motor,
ring, release or human-gate acceptance. Production static admission is unchanged.
