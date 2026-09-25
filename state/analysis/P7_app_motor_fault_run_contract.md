# Fixed inhibited full-app diagnostic upload and capture

Scope: one new `app-motor-fault-21df6ae8-run01` attempt. This adapter collects
evidence for D186/D188; it does not interpret callback fields, approve production
firmware, change the firmware, or establish a physical/human gate. The user has
connected the bare UNO Q. The coordinator owns fresh admission, source and local
input pins, reviewed HEAD, entry/global-initializer evidence, transport, installed
Python/F166 dependencies, and sequencing upload before capture.

## Exact identity

- Source: `21df6ae82cca4b09dc6b1e0de5bc719cf98ec6887800d5ce8297522e491a7950`.
- Configuration: `arduino:zephyr:unoq:link_mode=static`, default wait startup,
  `MATCH=0`, `MOTORS_ALLOWED=0`, `SUMOX_MOTOR_FAULT_PROBE=1`.
- Sketch: `/home/arduino/sumox26_codex_build/<source>/app_motor_fault`.
- Build: `/home/arduino/sumox26_codex_build/app-motor-fault-static01/build`.
- CLI input selector: `app_motor_fault.ino.bin`, 95312 bytes,
  SHA256 `18598e13f2b5601db504f5272826b0952b95477dd2b1b8d397d20bd2ff899144`.
- Selected sibling package: `app_motor_fault.ino.bin-zsk.bin`, 95328 bytes,
  SHA256 `deb40317e5c444af26e65da4b6f1d0e577d9897d59dbddff3bce03a7bc14335c`.
- Loader ELF: 2303728 bytes,
  SHA256 `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`.
- Derived loader flash image: 263680 bytes,
  SHA256 `e9322826c422fb234ac8c2e79ea38a050d0dd8dc32b2a89f6930e0a0ff7ebab2`.

Upload and capture claim separate exclusive directories under
`/home/arduino/sumox26_codex_build/`, named `<run_id>-upload` and
`<run_id>-capture`. Historical owners are not reused or repinned. A failed or
partially executed attempt stays consumed; there is no retry.

## Public remote interface and independent test seams

`state/analysis/P7_app_motor_fault_run_raw/remote.py` is Linux-only. Importing it
does not execute native commands or load dependencies. Public functions:

1. `load_dependencies(sources)` accepts exactly `upload`, `capture`, `helper`
   byte strings, validates all three SHA256 values before executing any, and
   returns a `SimpleNamespace` containing three fresh private modules. Expected
   sources are unchanged `P7_static_startup_raw/upload_remote.py`
   (`e926b7ba5586475664b0541370e7cfb5c50e40d8dc8b47b18e35db3e0a0a25c1`),
   `P7_static_startup_raw/capture_remote.py`
   (`95b0344d01886b6db30d55aa18a536f9a481b82348e22643e7920d817dbfac3e`),
   and `P7_static_link_probe_raw/static_remote.py`
   (`8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8`).
   Only the private uploader's `selected_profile` reference is replaced with
   this adapter's fixed profile. Original files/modules are untouched.
2. `selected_profile(support, run_id=RUN_ID)` returns the original uploader's
   profile shape, rejecting any other run ID/type. It fixes all native file
   paths, output owner, source, static FQBN and exact CLI argument list. Its
   upload schema is `fixed-app-motor-fault-upload-v1`; schema prefix is
   `app-motor-fault-upload-`. Historical shadow/config absence and installed
   directory checks are retained, with only the three sketch-local paths changed.
3. `checked_upload_bindings(dependencies, bindings)` delegates the original
   exact-shape validator, then also requires the exact raw/package/loader size
   and hashes above. Other file hashes are supplied by the coordinator's frozen
   fresh binding and checked before and after execution by the old lifecycle.
4. `checked_capture_bindings(dependencies, bindings)` accepts exactly schema,
   run_id, source_sha256, boot_id, uid, output, files, loader_image. It requires
   schema `fixed-app-motor-fault-capture-v1`, fixed source/owner/run, UUID boot,
   integer UID1000 (not bool), original five file names, exact native paths,
   exact package/loader/derived-image identities above, and Python `-B`.
5. `read_plan()` returns 26 `(name,address,bytes)` tuples described below;
   no input can enlarge or redirect the plan.
6. `upload(dependencies, *, fs_root=Path('/'), executor=None, clock=None,
   bindings=None)` performs the original `upload_loader` lifecycle using the
   fixed profile and checked bindings. Test-only filesystem/executor/clock seams
   are the inherited ones. The coordinator's native invocation always uses `/`
   and real execution.
7. `collect(dependencies, loader_image, *, fs_root=Path('/'), executor=None,
   clock=None, sleeper=None, bindings=None)` uses a small subclass of the original
   `Capture`. The supplied loader-image function is the coordinator's pinned
   existing parser. Only profile, plan, gathering and completeness are adapted;
   exclusive output creation, reads, subprocesses, deadlines, failure evidence,
   final file/identity checks and cleanup remain inherited.

Every API rejects malformed binding types, extra/missing fields, source/run/
owner/path/identity substitution and changed dependency bytes before execution.
No firmware compiler, dynamic relocation, new process executor or target command
parser is added. The adapter never downloads a debug ELF.

## Exact passive read sequence

Use original OpenOCD `dump_image` command composition, unchanged pinned passive
config and SWJ file. Capture does not halt/reset/write the MCU, poll serial,
enable sensors or issue motion commands. Brackets are complete images, split
into at most 65536-byte reads:

1. `before.loader.0` through `.4`: 263680 bytes at `0x08000000`.
2. `before.sketch.0` through `.1`: 95328 bytes at `0x08100000`.
3. Six `first.<name>` SRAM windows in the following table order.
4. One measured separation of at least two seconds.
5. Six `second.<name>` SRAM windows in the same order.
6. `after.sketch.0` through `.1`, then `after.loader.0` through `.4`.

| Name | Actual static address | Bytes | ABI source member |
|---|---:|---:|---|
| trace | 536951180 | 2128 | trace_.report_ |
| report | 537119696 | 1168 | report_ |
| runtime | 537117984 | 600 | runtime_.report_ |
| transaction | 537115448 | 504 | runtime_.transaction_.report_ |
| previous | 537115952 | 48 | runtime_.transaction_.previous_ |
| gate | 536953520 | 88 | runtime_.transaction_.gate_ |

These are file-observed D188 ABI windows from
`P7_app_motor_fault_compile_raw/abi_static01_interpreted.json`, not historical
D149 offsets or D173 dynamic relocation. Each sample is 4536 bytes. Total is
**26 reads and 727088 requested bytes**. Check the full before images against
the pinned references before any SRAM read. Check both complete after images
again. Any failed command, mismatch, short/extra read or time/identity failure
stops further reads and retains the partial attempt.

## Bounded execution and evidence acceptance

Preserve upload's 120-second child deadline, 180-second attempt budget, 5-second
kill/reap bound, exact environment/cwd, descriptor-bound admission and final
tool/artifact/installed-directory/shadow/process/identity checks. Use the
existing loader-copy file cap of 2303728 bytes. Upload calls CLI once with
`--config-file /dev/null upload --fqbn arduino:zephyr:unoq:link_mode=static
--input-file <fixed raw selector> <fixed sketch>`; it does not compile.

Preserve capture's 30-second child deadline, 600-second overall budget,
5-second kill/reap bound, 1MiB child stream limit, no shell and final file/
identity/owned-directory checks. Capture admits the same installed openocd,
passive config, SWJ and loader; all checks stay descriptor-bound. No subsequent
read follows an earlier failed read; no retry or fall-through to old profiles.

Only a successful one-shot upload returns `UPLOADED`. Only all 26 exact reads,
all four flash equality checks, twelve retained SRAM windows, measured wait and
successful closing checks return `COLLECTED`. Result schemas respectively are
`app-motor-fault-upload-result-v1` and `app-motor-fault-capture-result-v1`.
Capture `analysis` has schema `app-motor-fault-capture-analysis-v1`, an exact
`flash` object with boolean `before_loader`, `before_sketch`, `after_loader`,
`after_sketch` flags, a `snapshots` list of retained SRAM read records and
`coherence: "UNPROVEN"`; it reports collection only. Field decoding occurs later
against the observed ABI. Equal separated samples do not prove atomicity,
worst-case execution, free RAM, electrical outputs, original-fault resolution,
or a human gate. All original failure and cleanup evidence is preserved.

Independent tests must freeze before first execution, use controlled substitutes,
exercise exact profiles/identities/commands/plans and inherited failure seams,
and label results HOST-TESTED only. Source review precedes native use. Actual
initialization evidence and fresh coordinator admission are required separately.
