# D198 actual compile review

Verdict: PASS for the single completed compile-only attempt and its recorded source/tool/artifact closure. No material blocker found within this scope. This establishes checked target build artifacts; it does not establish the settle report's target ABI or retained publication instructions, target execution, the internal failure cause, timing qualification or physical acceptance.

Reviewer: separate same-model agent, reused context, 2026-09-26. Local read-only inspection of saved receipts, submitted code as data, source bytes, hashes and Git state; no subject imports, tests, compiler or board calls. Only this review was written. It incorporates the prior source/host review `50a276b9...` and prepared-scope review `8c83401d...` without repeating their executions.

## Exact attempt and inputs

The attempt binds reviewed HEAD `18c1135c5b4602405fdcffa3c7d6fe3dbcd38490`, scope `e292bcca95ce464bf6cdec4267bcf83a9aebc12ea28ab1280e950caa07236344`, manifest `aa314548521968fd3b1b7b1ef415da3c72c90a6bc914d0a9204ff707bcd7d282` and source `117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da`. The invocation records check-only exit 0 followed by one execution exit 0. Its completion JSON exactly equals the saved result. The current HEAD still equals that reviewed HEAD; Git reports no diff in any of the 129 manifest paths. This review independently rehashed all 129 manifest, 167 host-freeze and nine scope bindings with no mismatch.

The root intent, check-only output and result consistently identify `app_motor_observe.ino`, static FQBN, default startup, `-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1`, board serial 2629958581 and boot `55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`. Fresh attempt `app-motor-settle-static01` owns its local output/stage and remote build/artifact directories. The content-addressed remote sketch ends in the exact new source digest and `/app_motor_observe`. Its source-admission receipt says `reused: false`. These owners are now consumed.

All paths below are under `state/analysis/P7_motor_settle_compile_raw/`.

| Evidence | Bytes | SHA256 |
|---|---:|---|
| `native_static01_invocation.json` | 3560 | `fc38c8e10d601588dae8a96240686b77b5c31d88b7dc1d6de2e78cca9cf69fe6` |
| `native_static01/intent.json` | 902 | `0d1f08db3b3c11bee1859829b9823e36d88fe5718e0f2756c7141522764391e4` |
| `native_static01/result.json` | 1608 | `9b7f0c445cc84ad6d526445bf8e93ea189f718f0c883da8a1bf5cf077e741af5` |
| `native_static01/artifacts.json` | 9648 | `e18384c14c0b1367667b265ab4c532a4010be65697460a1cd45487bccd9eca10` |
| `native_closing01.json` | 1123 | `e33e324d0b135710c31f6df223acb5acd4bbc5f5e247a63c76706bf5a27bd041` |

## Actual commands and closure

Result status is COMPILE_CHECKED, first_error is null, starting 06:06:01.438052 UTC and finishing 06:11:52.774054 UTC on 2026-09-26. All 238 sequential transport directories have matching durable intent/result argv, limits and recorded command units, return code zero and empty stderr. The largest command is 29685 UTF-16 units, below 30000. Counts independently reconcile: 111 identity checks, two initialization inventories, two builtin inventories, one command-owner creation, one source admission, 108 file pushes, two complete source-set checks, nine checked subprocesses and two artifact observations.

There is exactly one expanded-properties query and one compiler run. Their checked envelopes use the admitted static flags/paths, controlled environment, jobs=1, respective 60/720-second deadlines and 5-second reap bounds. Both completed, were reaped and did not time out; measured child durations are about 1.602 and 224.499 seconds. The seven other checked subprocesses are the expected version/config/override/installed-pin observations, including closing repeats. No upload, reset or MCU read appears in this operation.

The compiler reports success=true, empty compiler_err and empty upload_result. All 318 query/compiler properties agree except extra.time.utc and extra.time.local; project, source/build paths, platform arduino:zephyr 1.0.0, static link mode and C/C++ flags agree. The saved text outputs are Windows LF-to-CRLF renderings of the checked child stdout; independently normalizing only those newlines reproduces the original envelope bytes exactly. Raw child bytes remain preserved in the base64 envelopes. Stderr is empty in both representations.

The 108 push paths exactly cover the stage map and each current source hash, under the one reviewed canonical sketch. Local staged files, initial remote source-set receipt and final remote source-set receipt match exactly. Independently recomputing the local stage's sorted name-NUL/raw-byte digest reproduces the admitted source SHA, with 108 files / 780479 bytes.

All 111 compact identity observations agree on UID 1000, arduino user, boot, CLI hash and empty conflicts; free space remains above the guard. Initial and final full initialization/builtin observations are identical, including UID/GID, home, kernel, architecture, Python and boot. Independently combining their hashes, both 18-file installed-pin observations, CLI identity and TLS observation covers all 28 installed inputs from admission02 with no omission or mismatch. The two override subprocesses succeed. All eight final checks are PASS with null errors: local, identity, initialization, builtins, remote_sources, installed_pins, overrides and artifacts.

## Artifact binding and inherited structural validation

The two artifact observations are exactly equal as parsed JSON and match artifacts.json, including all eight file identities, loader/TLS identities, first_error=null and three PASS postchecks. Independently unpacking the submitted artifact-observer payload as data confirms the recorded payload digest and 6895-byte projected remote source `dc359de3...`; its four bundled dependencies match the frozen projected adapter `e3d23d5c...`, base `d30372dd...`, extension `cd52a29a...` and helper `8ba9b190...`. No new parser or unchecked validator substituted for the reviewed ones.

All seven artifact aliases and hashes agree between the outer file records and inherited validator report. The exported package matches the build package by size/hash; debug and temporary ELF hashes match. The observation reports STATIC_APP_MOTOR_OBSERVE_LAYOUT_PACKAGE_PASS and the inherited STATIC_NATIVE_TLS_LAYOUT_PACKAGE_PASS, six native TLS symbols and no weak undefined symbols. Loader `39d4a4fd...` and TLS source `68bb1476...` remain unchanged. This reviewer inspected the saved validator evidence and exact submitted validator bytes; target binary files were not downloaded or independently re-parsed locally.

| Target artifact | Bytes | SHA256 |
|---|---:|---|
| Raw ELF | 172840 | `6091f27dbd136e0a694900bc68507b1cc6806073c6bfd50f5e57d892df6daeb9` |
| Debug/temporary ELF | 1839060 each | `dc610650600803c9e36c141e300cdcec478af4f03f4a350669ebe0a4699877b7` |
| Raw binary | 95504 | `d1033e627420e0de5d8ca90ebdf79c284228a23448f3d3e99130651d5afc65cc` |
| Build/exported package | 95520 each | `e400078166394d0f8ea44b601e9ba2948992c4f263c5c7ee5fb3942433c143d0` |
| Packaged ELF | 172840 | `eca3493c47b494a52c645f57a8034685a27a965ed749d09cd5ba4624cdd1ec7a` |
| Link map | 452000 | `914eb508828e1d73ce08d12e08be03315056736f4dc4b4194101c7912a84ff42` |

CLI accounting is 95520 program bytes and 171892 global-data bytes, leaving 90252 of its 262144-byte limit. Structural validation reports 208 bytes copied to data, 170664 bytes cleared in BSS, a 171680-byte .bss section and a 90256-byte RAM tail. Relative to D193, copied data remains 208, cleared BSS grows by 32 and the .bss section/global accounting grows by 1024. These are observed accounting differences; this review does not attribute them to report size, padding or alignment, and none measures live free RAM, stack use or WCET.

The local closing receipt agrees on result/manifest/artifact/invocation hashes and 1004 retained receipt files totaling 1699771 logical bytes, independently counted here. Source and checked target artifacts remain needed for the next file-only inspection. No material compile closure issue remains. Future work must establish the new report's actual target symbol/layout/initialization and emitted publication path from these exact artifacts before a fresh inhibited capture. No native runtime result, fault repair, motor authorization, physical acceptance or phase gate follows from this successful compile.
