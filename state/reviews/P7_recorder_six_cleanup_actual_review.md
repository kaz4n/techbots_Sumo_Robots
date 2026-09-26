# D236 actual exact scratch cleanup review

FINAL PASS for the saved five-action cleanup and its closing evidence. No open
material finding. Reviewed2026-09-27 from local retained receipts only. The
reviewer performed no native action, deletion, credential operation or tests
and wrote only this report. This acceptance is limited to the observed cleanup.

## Reviewed-to-actual binding

Owner: `state/analysis/P7_recorder_six_cleanup_raw` on MAIN.
Remote stage: `/home/arduino/sumox26_codex_build/cleanup-recorder-six-root01`.
Preparation manifest remains
`5bd1a09806d995513d0b96d435deeec6b47003dd5e49cda33f5106b0a80bdd02`;
preparation review remains
`b37db06c5616f7aa05f00a66ad08be002cca7988556fc598f5a99d956b0d1131`.

The actual6533-byte dispatcher SHA-256 is
`92d197080ffa428f25bb50e2391adb41e472999d5dd0e1406b2365c6a035e079`.
It exactly equals the reviewed template after only the two manifest/review
hash substitutions. Independently rehashed all65 unique inputs appearing in
the five invocation receipts. Each final action record retains the exact
invocation action/time/intent/input snapshot and its expected intent hash.

Verify/retrieve bound programs exactly reproduce their templates after inserting
the actual checked stage stamp and verified source identities. Their argv
contains those exact programs; command lengths27625/28015 UTF-16 units remain
below30000. Absence/stage are the reviewed19074/19575-unit commands. The fixed
authentication command remains319 units, with no-clobber result_root01.json,
empty sudo prompt and protected stdin credentials. No credential is present in
the reviewed program, arguments or saved receipt fields.

## Actual sequence and result

The five exclusive actions ran in order at21:51:28.906658,21:51:29.525222,
21:51:30.149201,21:51:34.682059 and21:52:04.148670 UTC on2026-09-26:
absence, stage, verify, authenticated, retrieve. Every action returned0 with
null first_error, empty stderr/closing_errors and local_input_closure=true.
Authentication's empty stdout is consistent with its fixed remote result-file
redirection; retrieval supplies the saved result bytes.

| Action receipt | Bytes | SHA-256 |
| --- | ---: | --- |
| `cleanup_absence01.json` | 18557 | `18f861151814c24a449c7316a6ab306b3c0d30844f329ac8f29c41a521e808ac` |
| `cleanup_stage01.json` | 18526 | `74bc5fcc29e7692ff97e18f7e8c9361081dcca55d0547f6b991c6e6d66290aaa` |
| `cleanup_verify01.json` | 26250 | `e3df311a2bf18a92d3d39e72de51ab09216ad25ac80d1539f16b77d57344f2a0` |
| `cleanup_authenticated01.json` | 16829 | `0a6223f3836d770a540be47c7ad135261865ebe74ffc2be618c9ef85ceb6dd1a` |
| `cleanup_retrieve01.json` | 33102 | `a300f4aa14c3e1a54581ac80a588c6ba7bb5ac1e0dcf2ccd735556578a045be4` |

The independently decoded retrieved result is byte-for-byte equal to local
result_root01.json:6345B / SHA-256
`f46a31b266352d5c9940e55c4fb8a52d600f5957a3f8f0075857379704430e4c`.
Its captured cleanup_stdout parses exactly to the nested cleanup_result.
Both report REMOVED_EXACT_STALE_COPIES with returncode0 and no first error.
Source pins and projected recipe hash match the accepted package.

The complete pre-deletion directory stamp and each file identity/hash match
fresh admissionbc2a9423: `/tmp/remoteocd`, device34/inode6818, UID/GID1000.
The sorted removed set is exactly flash_sketch.cfg680B,
recorder.ino.bin-zsk.bin55376B and the2303728-byte loader ELF:2359784B total.
The emptied directory was then removed. The recorder copy is the55376-byte
D233 package b13a32b5e92993a49f165b907d5d6036fa933e1680bb23ff2738620b294fd584.
No additional removed path is recorded.

All three protected process scans correspond exactly to the nested cleanup
use_checks. Each reports166 process names and three same-UID handle sets, with
no scan/restoration error. Before/after credentials are UIDs/GIDs[1000,1000,0];
during each scan UIDs are[1000,0,0] and GIDs remain[1000,1000,0]. Thus the
reviewed wrapper's scan completes and restores Arduino credentials before the
dependent exact unlink. Final UIDs and GIDs are both[1000,1000,1000], with no
privilege_drop_errors. This preserves the scoped scan's stated visibility
boundary rather than claiming inspection of every other user's descriptor.

Independent verification and retrieval each pass all six closing checks.
Board identity/boot and ordinary credentials agree before/after. All retained
original records exactly match the fresh admission, including the D233 build
package and installed config/loader. Staged source identities are stable.
Both retrieval scratch_absent checks are true. These establish absence at
retrieval, not a guarantee against a later authorized upload recreating scratch.

Root closure352B / SHA-256
`605b6c8bd4a1689c934b3a6bd9261c0574c2da94f17404517c17aa09a25275a8`
matches the independently reconciled counts, source-directory identity and
result pin. The native owner and all five action owners are consumed. This
cleanup changed no firmware or MCU state and supplies no UART repair/delivery,
motor authority, physical qualification or phase gate.
