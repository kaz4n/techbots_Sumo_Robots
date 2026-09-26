# D194 Windows pathname/descriptor mode correction review

26 September 2026, Asia/Dubai. **PASS for the amended source and host scope;
no open material finding.** This supplements the historical D194 source/host
review; it does not establish a successful actual ABI query. Reviewer
`/root/fresh_review` is a separate same-model reused context, not a fresh
whole-project reviewer. Only this review file was written. Review used local
source/receipt reads, hashing, Git diffs and AST parsing; no subject import,
test execution, device call or native invocation was performed by the reviewer.

## Cause and preserved failure

The first actual check-only invocation refused before the local native owner
or any board action. Receipt `preflight_actual01.json` has SHA-256
`5b6f2b27b985b621b09a1acc58bbc6b0e2c8a6b20274992afc565f342a616f44`.
Independent passive inspection of the real pinned ADB file confirmed pathname
mode `0o100777` versus descriptor mode `0o100666`, with full snapshots stable
within each API. Other cross-API fields matched apart from the already handled
Windows ctime distinction. Content remained SHA-256
`e79dc8fc3c6385192bdccd7ff7eabe3d5c1ec292475a06b04d82759f07655982`.
The executable was read as data and never launched by this reviewer.

This was a real platform compatibility defect in the original contract/source,
not an observed file change or a fixture-only failure. CPython 3.13.11 adds all
three execute bits to Windows pathname results for case-insensitive final
`.exe`, `.bat`, `.cmd` and `.com` extensions; the descriptor conversion produces
the regular-file read/write modes without that filename-based addition.
See [pathname implementation](https://github.com/python/cpython/blob/v3.13.11/Modules/posixmodule.c#L1831-L1852)
and [attribute conversion](https://github.com/python/cpython/blob/v3.13.11/Python/fileutils.c#L999-L1028).
The original strict refusal is preserved in commit `a4362e7b`; the independently
frozen regression and original-subject failures are preserved in `d519a2f3`.

## Amended scope and source

| Item | Bytes | SHA-256 |
|---|---:|---|
| Amended contract | 12283 | `0d81956d0be277a077f048a4d2eccda0ad13c44437d453a94a78ab154a1f26aa` |
| Corrected wrapper | 9318 | `497f756e4eab440d659a4d26ef38ec8d92abdd9f92a5938d1da04705745f42d5` |
| Existing 44-method oracle | 46134 | `b43b384aafc77499b4752af7633e2a94c98e67e955554f75490f5dc30e45bcbe` |
| New 14-method regression | 9907 | `9777060b05f041f409a822e30c68c1630192b0354d6462b89f47cb1a2b1ac687` |

The contract explicitly changes the former cross-API mode equality rule.
The wrapper adds six lines of predicate/comparison handling and its explanatory
comment, plus the updated contract pin. Exact mode equality remains valid.
Additional acceptance requires Windows, an eligible final extension, two
regular-file modes, `path_mode == (fd_mode | 0o111)` and
`(path_mode ^ fd_mode) == 0o111`. Independent AST inspection confirms that the
unparenthesized XOR in the source has precisely this comparison grouping.
Partial, reversed, noneligible, non-Windows and other-bit differences remain
rejected. This is not a general execute-bit mask.

Only the temporary handle-identity tuple receives the pathname mode for the
cross-API comparison. The original path/ancestor stamps and opened descriptor
stamp retain their full modes; their after-read comparisons are unchanged.
All other cross-API identity fields remain exact under the existing ctime rule.
The early ordinary-file/link/reparse gate still runs before fdopen/read.
Byte limits, bounded reads, content digest, descriptor cleanup and primary-error
preservation are unchanged. The private projection, original source pins,
compiler/manifest/artifact bindings, parser and native lifecycle are unchanged.
The existing oracle changes only CONTRACT_SHA; no assertion was removed.

## Independent regression and actual host receipts

The new oracle was frozen before source correction, derived from the proposed
contract and primary CPython references. Its declaration of independence is
recorded in `windows_mode_independent_freeze01.json`, SHA-256
`1078596486fbf60864ec363762cde20118f4713ca651ba95f2492e358f42b917`.
The same unchanged regression first exercised old subject `297eac8b...`: Windows
reported 14 methods with 14 subtest/errors and 7 failures; Linux reported 14
methods with 13 subtest/errors and 7 failures. Counts include subtests and must
not be read as 21 distinct failing methods. These expected failures include the
real Windows executable-named file and fixtures unable to reach the required
late checks because the old implementation rejects the mode difference early.

The reviewer read all four corrected receipts and the complete regression.
The regression reads a real tiny mixed-case `.EXe` file without launching it.
Controlled metadata covers all four extensions and case, read-only modes,
ordinary exact equality, all stated negative mode cases, other identity fields,
nonregular/reparse/multiple-link rejection, full raw path/descriptor mode drift,
ctime stability and wrong content digest. Early failures assert no fdopen/read;
late failures must actually reach the bounded read. Linux uses `/dev/shm` and
Windows small temporary files. Process and socket endpoints are blocked.

| Receipt in P7_app_motor_observe_abi_raw | Observed result | SHA-256 |
|---|---|---|
| windows_mode_original_windows01.json | Old subject: exit 1, 14 methods, 14 errors / 7 failures | `a57e7762d326f7cda55c86b3ea30cca4f2e8df3bc9890797672d7d2fd79f891f` |
| windows_mode_original_linux01.json | Old subject: exit 1, 14 methods, 13 errors / 7 failures | `2936704eed225413b43533414dd71aacf6805f06216618164a0b6ff5e112a9e1` |
| windows_mode_fixed_windows_regression01.json | 14 PASS, 0 skips, exit 0, 0.142 s | `712557f91a93b229fc94db260c08eec2716fd8766f0ff4f66d44a236760b8338` |
| windows_mode_fixed_windows_legacy01.json | 42 PASS, 2 skips, exit 0, 1.221 s | `3daad9586c1dc3cd297181276c0bac54b93a7d0a26c349ce1f8e38752cd7627e` |
| windows_mode_fixed_linux_regression01.json | 14 PASS, 0 skips, exit 0, 0.052 s | `72e95c1267dbbceb4b83f3580f9f701bb12a48dc3d4db337487184379a769751` |
| windows_mode_fixed_linux_legacy01.json | 44 PASS, 0 skips, exit 0, 8.304 s | `e41c8bc97de7f65d98afc2e130d75ec804fe765569cc70dadab660658a25fffa` |

All commands use Python -B, unittest discovery and verbosity. Windows retains
exactly the known real-symlink WinError 1314 skip and Linux-only FIFO fixture
skip; both corresponding tests pass on Linux. New regression has no skips.
Thus Linux is 58/58 PASS and Windows is 56 PASS / 2 explicit skips.

## Pin closure and limits

The reviewer independently hashed all 136 current files against
`coordinator_freeze03.json` (SHA-256
`6d024ca44a7d488eff11d6bdefd118561d0155e408b8a22f6be0a38478808dfc`):
all match. Relative to the prior 135-pin freeze, exactly the wrapper, amended
contract and existing oracle metadata changed, and the new regression was
added; no pin was removed. D193 source/artifacts and historical original
reader/normalizer/launcher bindings remain unchanged. The local native owner
`P7_app_motor_observe_compile_raw/native_abi_static01` remains absent.

This evidence supports committing and separately admitting the corrected
caller under a clean reviewed HEAD. Actual check-only success, fresh board
identity, query execution and closing receipts remain unobserved in this
review. The tests use synthetic transport/ABI data and tiny local fixtures;
they do not establish target layout, firmware execution, motor permission,
physical qualification, fault repair or any human phase gate.
