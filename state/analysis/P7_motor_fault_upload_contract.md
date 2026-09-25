# D175 closed inert diagnostic upload profile

Scope: extend only P7_static_startup_raw/upload_remote.py's existing public
upload_loader(..., bindings=None, run_id=...) interface. Host preparation only;
no upload occurs until capture preparation and an identified native scope exist.
Default upload()/static run01/run02 behavior, globals and frozen tests remain.

The sole added run_id is motor-fault-8f592937-run01 (exact str). Reject unknown,
similar/prefix, traversal and non-string identifiers before ownership or execution.
Selected profile is per instance; never rebind SOURCE/BUILD/SKETCH/FILE_PATHS/
ABSENT/BINDINGS or rewrite caller-owned bindings. No new global configuration.

New fixed selection:
- source_sha256=8f592937961a0c95b7cc4db88617169fcc9504644aa8b8b7dcf62f83c4c33f36
- bindings schema=fixed-motor-fault-upload-v1
- output=/home/arduino/sumox26_codex_build/motor-fault-8f592937-run01-upload
- sketch directory=/home/arduino/sumox26_codex_build/motor-fault-active01/motor_fault
- build directory=active_verified.json build_path, literally bound in implementation
- files.raw path=<build>/motor_fault.ino.elf
- files.sketch path=<build>/motor_fault.ino.elf-zsk.bin
- other15 file-role paths and all3 directory selections unchanged
- absences retain all11 shared paths; replace only the final3 sketch.yaml/yml/json
  paths with the selected diagnostic sketch directory.

Fixed argv (no caller argv/flags/environment override): /usr/bin/arduino-cli
--config-file /dev/null upload --fqbn arduino:zephyr:unoq --input-file
<build>/motor_fault.ino.elf <diagnostic sketch directory>.
The CLI input is the raw ELF selector. The reviewed dynamic recipe selects its
ELF-ZSK sibling; passing ELF-ZSK as --input-file would select the wrong sibling.

New attempt/command/result schemas are respectively motor-fault-upload-attempt-v1,
motor-fault-upload-command-v1,motor-fault-upload-result-v1; their source and run
fields use the selected profile. All existing receipt fields/statuses and error
precedence remain. Source/path/schema from one profile cannot mix with another.

Keep the existing pin contract: supplied file sizes/hashes are validated, read
and checked against actual bytes; a separate reviewed caller must bind the
production metadata before native execution. Fixtures may use tiny substitutes.
This profile selection alone proves neither artifact origin nor run permission.
Actual observed raw ELF and both ELF-ZSK copies are29836B; hashes f9460a16/b4416792
and complete paths are in active_verified.json and deployment_files01/result.json.

Preserve descriptor/ancestry/file/directory/absence/process checks, exclusive
consumed ownership, explicit environment, one launch,180s total/120s child bounds,
group kill/reap, first-error and partial-stream retention, independent final checks.
Preserve upload_loader's2303728B child file cap and strict <1MiB accepted streams.
No compile, automatic retry, capture, motor capability, source/stage cleanup or
legacy-manifest repinning. Test normal and failed actual public loader paths with
controlled Linux files/commands, plus unchanged legacy suites; no board operation.
