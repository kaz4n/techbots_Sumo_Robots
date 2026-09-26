# D207 fixed native adapter source and host review

Status: PASS, no material findings. This is an independent local source/data review of the fixed remote adapter and its first host results. It does not admit an upload by itself or establish target runtime success, coherent RAM, physical acceptance, a human phase gate, or motor authorization.

The reviewer read the actual subject only after the coordinator reported the native oracle FINAL barrier closed. No subject import, test, compiler, device command, authentication or cleanup was performed by this reviewer. Only this new review file is owned here; prior reviews and other contributors' work are preserved. The caller/actions review is separately owned and required by the exact scope.

## Reviewed identities

| Item | Bytes | SHA-256 |
|---|---:|---|
| `state/analysis/P7_motor_const_run_raw/remote.py` | 11331 | `51c60cd5ac87b823b84b2c7d993933690f0a3110e4d89c7cb958549fb5f111bc` |
| `tests/tooling/test_motor_const_remote.py` | 10067 | `809f9cecf0bce5a5d67c6f44027c0f92a1b7fd1da186aed80db00ccba5bc69cd` |
| `state/analysis/P7_motor_const_run_raw/native_fixture_derivation01.json` | 43519 | `361ca074ab97596afca1cf43a44009fbe80d28ed27581e54c7636e8c1d2659e6` |
| `state/analysis/P7_motor_const_run_raw/native_independent_freeze01.json` | 66977 | `7a426a2f946e645e1373d1153ee18708e4ccdd1c7c4b78eed64c1c2618d09336` |

The adopted contract is `state/analysis/P7_motor_const_run_contract.md`, SHA-256 `1949c7db32bfda4c3318095597b740ea17644ec5b0109cc2e589387842dbbf85`, with normative `run_derivation01.json`, SHA-256 `c90961438062c153f9c99621eba0617b3fc26b0f3dbdd2c35859ec2e744b5bfb`. All 290 independent native input pins and all 302 coordinator input pins were independently rehashed and matched. Coordinator freeze SHA-256 is `f86281252c5dd8124d9db63bc696221d9b94b3d2cab158cb2b41cd73cce03f45`.

## Source findings

The reviewer independently applied the ten declared literal metadata substitutions to the pinned D201 predecessor, checking each occurrence count, before/after length and hash. Reconstructed bytes exactly equal the actual adapter. No additional operational change is present. The bound source is `4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2`; run owner is `app-motor-const-4bc3a2e6-run01`. Previous owners are not reused.

Import remains passive. All three dependency byte/hash checks precede private dependency execution; private modules are not installed in `sys.modules`. Exact key/type/path/source/run/UID/boot/artifact checks and defensive binding copying remain. The fixed upload profile is the default-startup `app_motor_observe.ino`, MATCH=0, MOTORS_ALLOWED=0, fault probe enabled; no motion grant is manufactured. Installed paths and fourteen upload shadow-file absences remain constrained. The adapter does not compile or select an arbitrary sketch.

The current raw image is 95352 bytes / `76d2846dfe99602b1a4dd680f19c8150a02af4dba3b4f3411fafd7c55e3824d3`; packaged sketch is 95368 bytes / `f15c7ce1f0ff5fea2d44d0b60f0607f9adae22b83ba5043fe4de5e2b21fa26f7`. Loader identity and extracted loader image stay independently bound. The capture plan is exactly:

| Window | Address | Bytes |
|---|---:|---:|
| trace | 536951180 | 2128 |
| report | 537119696 | 1168 |
| runtime | 537117984 | 600 |
| transaction | 537115448 | 504 |
| settle | 537121768 | 28 |
| gate | 536953520 | 88 |

Each sample is 4516 bytes. The previous-live window is excluded. Each loader bracket has five reads, and each sketch bracket two. The ordered plan is before-loader, before-sketch, first six windows, second six windows, after-sketch, after-loader: 26 reads and 727128 bytes. Full image comparisons occur at indices 4, 6, 20 and 25. A mismatch before SRAM prevents sampling; a later mismatch remains failure.

The first sample still waits thirty seconds after successful initial flash brackets, with strictly more than thirty seconds of remaining budget. The independent two-second sample pause remains. Timing failure preserves the partial wait record and first error; budget origin is not reset. Snapshots are retained through `finally`. Completion requires all four flash comparisons, twelve snapshots, the exact count/byte accounting and successful initial wait. The result continues to state coherence `UNPROVEN`.

The inherited one-shot upload/capture lifecycle, descriptor ownership, exclusive owners, child timeout/stream bounds, first-error preservation and closing pin/identity checks remain unchanged. No retry, new reset, widened capture, stale artifact fallback or motor capability is added. The 150 us / 4096-poll settle policy and later runtime limits are unchanged by this metadata adapter. A future setup success would not establish a runtime cure.

## Independent oracle and actual host evidence

Static AST/literal reconstruction, without importing tests, reproduced the current historical provider: 21190 bytes / `fb90838accf91e6af276451b8418b74763257e699f403ebf7070f93097c222fd`; sixteen higher-level methods and 72 assertion calls remain. The reconstructed core is 38547 bytes / `7bd7ca7fcbb4a56af664236b472d2d91da4eb1fc1be6a2aefdc44de0abe8168b`; all 26 core methods and 135 assertion calls remain. The three D201 outer methods remain, with two added current-source/consumed-owner and fixed-wait checks. Historic method names mentioning old replacement/read counts are retained lineage labels; their actual expectations and fixed data match D207.

The tests cover dependency refusal before execution, exact binding schemas, fresh owners, source/artifact/identity/process drift, shadow and symlink refusals, flash brackets, partial/extra/short reads, no retry, clock/deadline/wait failures, preserved first errors and failing closure, bounded child handling, and stale D193/D201 inputs. The added tests do not replace the negative lifecycle assertions.

The reviewer read the first saved outer receipts and complete test streams, checked stream hashes, counted every method result and compared platform coverage:

| Platform | Result | Test time | Outer elapsed | Result receipt SHA-256 |
|---|---|---:|---:|---|
| Linux | 47 PASS, 0 skips | 17.151 s | 37.0021805 s | `c60d27c1e1c150f3d7124e62f1242be57f1d621d0b0bcef6af07bbf557535719` |
| Windows | 29 PASS, 18 explicit skips | 0.721 s | 0.9622186 s | `7031b596c9c039aa2cc244789f1ef0642e30f8af8cefcbb673a2019732113204` |

Receipts are `first_remote_linux01/result.json` and `first_remote_windows01/result.json` under the run raw directory. Their stderr hashes are respectively `6e2e1b12f8159fae235f35270d4873f2369ab93dd1452be397c26637abf7c65d` and `1403175fdf1178fbb179b3a467ea8c63d1d1b7cda920da1d395f6cd73ed80339`; stdout is empty. Both returned zero, had no changed inputs and preserved the freeze. Windows temporary remnants are empty. All eighteen Windows skips are inherited Linux-dependent lifecycle/wait cases, each passing on Linux; they are not additional Windows passes.

These are controlled host results, not native evidence. The earlier coordinator-builder `files`/`inputs` error was reported before owner/test execution and is retained separately; it is not a subject failure or a consumed native attempt. No rerun was needed for these remote results.

## Disposition

The remote source and first host evidence satisfy this bounded D207 review. Separate caller/actions and corrected-interpreter/map reviews, accepted fresh read-only admission, exact actual scope, committed clean-HEAD check-only and the one-shot execution guard still precede any inhibited native attempt. Actual raw results require their own independent review. No physical or competition qualification follows from this PASS.

Final review; STOPPED WRITES to this file after recording its external hash.
