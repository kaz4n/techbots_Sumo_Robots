# P7 D198 motor-settle compile preparation review

Verdict: PASS for the bounded launcher implementation, corrected host evidence and prepared compile inputs. No material source finding remains. Actual compilation requires a separately recorded clean reviewed HEAD and the unchanged caller's live admission; no native compile, upload, reset or MCU observation is established by this review.

Reviewer: separate same-model agent, reused context, local read-only source/AST/byte/hash/receipt inspection. The reviewer did not import subjects, execute tests or compilers, contact the board, or edit implementation/oracles. Only this review was written. Review date: 2026-09-26.

## Source and lifecycle

Reviewed contract `state/analysis/P7_motor_settle_compile_contract.md`: 14344 bytes, SHA256 `c0b352810c41c8b3744acdd1c15bc4b21ecb76bc15d76d4fedea4fdde37dc756`. Launcher `tools/compile_motor_settle_probe.py`: 7570 bytes, `b98a5f54e2be122162e76074673190f52ef4218c766d517125b48127bb4b8b62`.

Independent raw-byte reconstruction confirms exactly the contract's ten ordered/count-checked substitutions from the preserved D193 launcher `70e1f016cec041b40c98c7c5dd5ee20223d75c4a876c76d2fcdea3d790d63827`. They change the decision/comment, launcher/contract/raw-directory names, attempt identifiers, private module label and the two resulting projected byte identities. No lifecycle body is newly duplicated or loosened.

All three pinned historical sources remain exact. Independently reconstructed private outputs are caller 29889 bytes / `9a9d8df4130369eb4a31a348b76ddd7c2b3ca63c1e448250cc7d60dfc1d3158c`, adapter 8266 / `e3d23d5c6b2bd2d088f954a2dd2b574188edca8ca95d65a4432e54de759d169d`, and remote 6895 / `dc359de37aab994e5dfbbadda1997235213da4e50c7f19f44141df18f2df7160`. Original byte/hash checks and counted output checks precede private execution. The adapter is identical to D193's projected adapter. Private loading does not instantiate an owner, invoke a main guard or register shared module aliases; the original caller and remote source pins are retained in HARD_PINS/REQUIRED.

Inherited bootstrap ancestry, ordinary-file/reparse/link checks, bounded nofollow/nonblocking descriptor reads, full same-API stamps and primary-error preservation remain intact. The existing Windows cross-API ctime exception is unchanged. Fresh exclusive local/raw/remote owners, exact manifest checks, durable intents, first-failure handling and independent closing checks are preserved. The fixed attempt is `app-motor-settle-static01`; sketch remains `app_motor_observe.ino`, static FQBN, default startup, flags `-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1`. This does not use the earlier compile owners.

The admitted operation remains one properties query (60 s) and one compiler (720 s, jobs=1), with inherited reap/deadline and output bounds. The 128 MiB local and 1 GiB board guards, artifact/package/TLS validation and exact exports remain unchanged. No new target-address assumptions or upload/MCU operations are introduced. A later compiled settle report still needs its own ABI and instruction evidence.

## Independent oracle and actual host results

The frozen oracle design preserves all 94 historical methods through whole-original and counted private-projection hashes, adding six caller and two remote cases. New coverage checks exact launcher metadata, private pins, the new header's inventory/digest/real staged bytes, header omission/missing/drift refusals, old owner preservation and previous D188/D193 manifest/artifact/build-path refusals. Inherited coverage retains admission, descriptor drift/special files, bounded endpoints, durable intent, first failures, closing checks and actual artifact validators under controlled host fixtures.

Original independent freeze `4bd4b435e5e4c8574022c9a06e7e252e8b71816eaf162d4509a27931ec57fa49` preceded execution and source-body inspection by the oracle author. First Linux caller receipt `caller_first_linux01/result.json` / `ada74d77453014cbbca24289b3be41f361aa14a53811379234d61831f4c34ac9` records 64 PASS / 1 ERROR, not a clean pass. Stderr `42930daf986f4141cba17696919a6088074cbe627504a966469317cf16329b18` identifies the missing staged header. The simultaneous original remote group passed 37 methods. These original oracles/receipts are retained at commit `4c61913e`.

Independent adjudication: the new fixture called `prepare()` and immediately read staged bytes. Production `prepare()` only loads checked modules; `stage()` performs and verifies staging. The established inherited staging fixture uses controlled endpoints and `local(); prepare(); claim(); stage()`. The repair adopts that exact lifecycle, leaving all assertions intact; its coupled remote SUPPORT_SHA alone is refreshed. It does not bypass admission, mock out local staging, alter production code or weaken a requirement.

Corrected caller oracle SHA256 `71371f9361ef20ae0a64feb156e10e24e22722b1b31d8d426816d69bd6db962a`; remote `b2da457db6da3d01412dd300d495f075a8631294c75627f66b91dc1ee9fbd2e7`. Independent freeze02 is `bc5f0d8827c7ee7ead4c2d2813c44a3e433b30b4b6137157226687ebd2c203ed`. Coordinator freeze02 is `edd831f15ab4bd17cb85ba0b3a01468d36c9340c36a92fdb1f9719c969ba5dc8`; this reviewer independently rehashed all 167 pins with zero mismatches after the four corrected serial runs.

All paths below are under `state/analysis/P7_motor_settle_compile_raw/`. Every result returned zero, recorded no changed inputs, and its stdout/stderr hashes matched the saved bytes.

| Actual result | Outcome | Result SHA256 |
|---|---|---|
| `caller_corrected_linux01/result.json` | 65 PASS, 0 skips; 29.937 s unittest | `d2629b1614193bc59482a8f4ee54dbc5df2a6766710919efe07f781fea557f32` |
| `remote_corrected_linux01/result.json` | 37 PASS, 0 skips; 30.433 s | `aade42b32a0da18ecb4d055690fe7a6cf51f8b2cfa95f9b3e311016a042b7cad` |
| `caller_corrected_windows01/result.json` | 62 PASS, 3 skips; 51.534 s | `9cf2725a576df42c6f94f982d12e1f2b3bf62fed76a8292d188d4ebf20fca295` |
| `remote_corrected_windows01/result.json` | 19 PASS, 18 skips; 5.456 s | `5b52045917d544d4194b6cdfadf78d5783b7c0caf7c8a11136f4a2f3bce3a7ec` |

Thus Linux executed all 102 methods, Windows passed 81 with 21 explicit skips. Windows skips comprise 19 Linux descriptor cases and two unavailable symlink-creation privileges; all ran successfully on Linux. No corrected product or test failure remains. These are controlled host results, not an actual compiler invocation on the robot.

## Prepared inventory and read-only admission

`inputs_static.json` SHA256 `aa314548521968fd3b1b7b1ef415da3c72c90a6bc914d0a9204ff707bcd7d282` has the expected schema, current boot and exactly 129 pins: 110 source inventory entries plus 19 required support inputs. Independent local enumeration found no linked/reparse/special source entries; every pin matched current raw file bytes. Independently reconstructing the mapping produced 108 files / 780479 bytes from 781347 inventoried source bytes, with exact name-NUL/raw-content digest `117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da`. Exclusions are exactly `src/app/.gitkeep` and `src/app/app.ino`. Against D193 source pins, only the separately reviewed D197 motor_port_unoq.cpp and new motor_settle_probe.h differ. Both new local owners were absent at inspection.

Read-only admission02: 31070 bytes / `1c6c5ca35bea3c816de390d57bc8a2431e9b1f6e09d2f3313e45c1e6679c9212`. Both children returned zero with empty stderr. All 28 installed hashes match; full identity/boot and UID/GID triples remain unchanged through closing, owner paths remain absent and process conflicts are empty. Recorded root/home free space is 2935316480 / 13958955008 bytes, available RAM 3232317440 bytes. All 21 local pre-admission support pins were independently rehashed current.

The first admission failure is retained as `admission01.json` / `1b5c4a57ba08957ca76913021b17496c1690b9ea02496db4d2fab7c0ae9b0eb9`; its coordinator observer had added `st_nlink==1` for installed compiler files. Separate metadata receipt `08e2ebb26e2ba1704856311e9bce9a09c006a0bc83ea2e812715c679ada83805` observes stable regular gcc/g++ files with nlink 2 and ld with nlink 4 and exact expected hashes. Inspection confirms the admission02 program removes only that conjunct, returning to D193's original regular-file/size predicate. Full link-count-bearing before/open/read/after stamps still match. This is a narrow coordinator observation correction, not a production guard relaxation; both failure and diagnostic receipt are correctly hash-bound.

The admission records file reads and process inspection only. It is point-in-time evidence, not permission to reuse owners or bypass the caller's later checks. A new clean reviewed HEAD, native check-only and the single admitted execute still need their own records. Actual compiler success, settle report layout/retention, failure cause, WCET, motor behavior, physical qualification and phase gates remain unproved here.
