# D232 root02 actual cleanup review

FINAL PASS - exact cleanup evidence accepted. The three admitted D228 scratch
copies, totaling 2359512 bytes, and their empty directory were removed. Their
retained originals were unchanged. No open material finding in these saved
results. Reviewed 2026-09-27 using local receipts only; no tests, native actions
or source changes were performed by the reviewer.

## Bound execution

Preparation review:
`69b429c9cf6f93de8aa4244307f7135e6bd0932e1228c5f7d45440c761124bc8`.
Manifest:
`a6524df882d2d99aff1b57a17ba9e2fdbbb357962e68e457ab622d34df0e04a7`.
The final dispatcher is 6549 bytes / SHA-256
`86f5944e8e82f53ec258124513abc15eb0a6fbadd019ee0e1bd482c5c447d7cf`.
It equals the reviewed template with only the two permitted hash bindings.
The isolated ROOT and fresh `cleanup-recorder-next-root02` stage are unchanged.

All five exclusive invocation records reconcile to their final dispatch
receipts, in order: absence, stage, verify, authenticated, retrieve. Each has
return0, no first error, empty stderr, no closing errors and local input closure
true. Independently rehashed all 57 unique recorded local input pins. Every
intent pin matches the invoked intent. Verification/retrieval program bodies
equal their templates with exactly the permitted checked stamp substitutions;
their argv remain within the bound at 27655/28045 Windows UTF-16 units.

| Saved receipt | SHA-256 |
| --- | --- |
| `cleanup_absence01.json` | `bd34185634eaeff8a1cfd051c9dfd39ee4dc0feac34a492c6d4e5f0364f3a85d` |
| `cleanup_stage01.json` | `5e0659c7a28d0360d9cfe6f6886fdf4a798a4895782ad3eab319b8733cc19f8e` |
| `cleanup_verify01.json` | `b879ca6c850a20450ac6faf2d17fd6de9f795e0c06a3df78911fe02190e0789e` |
| `cleanup_authenticated01.json` | `64c689a9a3c04ae9180108e2807e586ac6845fb49aa06386e3b117225f532108` |
| `cleanup_retrieve01.json` | `ba556e528b166bfeca6b5e64992ca33386c6028bfd1aba619c6d9c2192ee9b79` |

## Independently reconciled outcome

Absence and stage observations agree with admission17cfc318 on all three copy
identities/hashes. Stage device66341/inode282817 is mode0700, UID/GID1000; the
three staged sources are regular single-link mode0600 files with the exact
reviewed hashes. Verification reopens the same stage, scratch and originals,
finds no result yet, and passes all six ordered closing checks.

The authenticated action's empty stdout is expected: its fixed no-clobber
command writes the result to the remote result file. Retrieval's decoded
base64 bytes exactly equal local `result_root01.json`, 6348 bytes / SHA-256
`ee4aed5046a01dccb8500dbf1748b53b60f047e00b73636268ed1da45b607da2`.
The result descriptor stamp, byte count and hash agree before/after reopen.
Parsed cleanup_stdout equals the nested cleanup_result; both schemas, source
pins and projected recipe match the accepted package.

The cleanup identifies `/tmp/remoteocd`, device34/inode6292, and the admitted
boot `55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`. Its pre-removal directory stamp and
complete child records equal admission and verification. The exact ordered
removals are:

- `flash_sketch.cfg`: 680 bytes.
- `recorder.ino.bin-zsk.bin`: 55104 bytes.
- `zephyr-arduino_uno_q_stm32u585xx.elf`: 2303728 bytes.

The empty directory removal is true. All three protected process observations
report 167 process names and three same-UID handle sets; each matches its nested
use check and has no errors. Each observation starts and ends at UID/GID triples
[1000,1000,0], with effective UID0 only during the protected scan. Final UID/GID
triples are [1000,1000,1000], with no privilege-drop error. This remains bounded
process evidence with the inherited race/other-user-FD limitations, not a
general lock or future clearance.

Independent retrieval reports scratch absent both before and after its reopen
checks. Full original-file records are identical across admission, verification
and retrieval, including retained recorder build original and installed config/
loader originals. Staged source files also remain identical. Both board
identity and Arduino credential checks agree before/after, and all six ordered
retrieval closing checks pass. Wrapper/cleanup first errors are null and the
cleanup return code is zero.

Root summary `root_actual_closure01.json`, 639 bytes / SHA-256
`b3bbb56dc855440168b5ca16329e296299944e88b6968f951c008ac70fd27fd4`,
agrees with these independent recomputations.

The earlier root01 stale-inode failure and erroneous review remain preserved
and superseded. Root02 is now consumed; this acceptance does not authorize
another cleanup. Scratch absence describes the saved retrieval time, not any
later upload. The cleanup changed no MCU image and establishes no UART cause,
recorder delivery, motor permission, physical qualification or phase gate.
