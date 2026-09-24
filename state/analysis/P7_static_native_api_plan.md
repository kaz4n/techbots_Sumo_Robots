# D150: existing native API boundary observation

Close only the remaining direct app/native GPIO, PWM, RCC and device-init ABI
questions from P7_static_native_dispatch_next.md. Retained audits already bind
the actual call instructions and driver addresses; do not rebuild or collect
another ELF. Internal packaged-driver dependencies are identified as inherited
behavior, not expanded into an audit of the entire operating system.

After scoped review, execute captured, hash-pinned read_native_api.py once with
Python-B. Reuse the unchanged runner/helper, 17 local/26 installed pins, current
103 source/102 stage bindings, original D144 Claim and eight FileRecords.
Five commands only: existing-file/source/identity check, installed hashes, one
file-only GDB observation, then independent repeats of the first two checks.
Always finish independent local postchecks and preserve the first failure.

GDB uses -nx -nh -batch and -iex 'set auto-load no' before opening either file.
The 50 labelled queries cover eight exact types and five scalar widths in both
the existing app debug ELF and packaged loader, nine devices, three driver
vectors, eleven signatures and z_impl_device_init disassembly. Only file,
ptype, p/x, sizeof, whatis, disassemble
and echo commands are admitted by this fixed composition. No target connection,
inferior, native call, scripts, compiler, upload, reset or remote write.
Dispatch remains bounded to 30000 Windows command units, 60 seconds and a 1MiB
accepted response; full stdout/stderr/status stays in its sole command receipt.
Require all labels in order, nonempty sections, successful process and no stderr.
Collection success is not a comparison pass: review and interpret each required
field and calling convention against the retained actual instruction evidence.

Host preflight exercises preparation and positive/negative marker parsing with
zero dispatches. Any actual failure ends this one-shot observation; do not retry
or change established tests/production to turn negative evidence into a pass.
Native loading/startup, stack/heap/WCET, physical acceptance, static production
admission and all human gates remain separate. No extra hardware is requested.
