# D205 current instruction reader host validation

The exact adopted reader passed both first host suites: 30 tests on Linux and
30 on Windows, with no skips, retries or source changes. This is fixture evidence;
current instruction semantics and timing remain unobserved.

The contract is6663d1ea, binding7417ff70 and derivationae6ef0de, adopted at
commitd9753932 after fresh preparation review4edbac30. After independent oracle
FINAL, root reconstructed all12 wrapper substitutions from the pinned D199
predecessor. The actual14941-byte reader matchesa71eb624 exactly. Reader and
parser projections remain17075/580abb32 and10866/c4c4f9e2. The implementation
receipt63280104 closes21 inputs without oracle inspection or execution.

The independent oracle is16089 bytes/daf208fa; fixture derivation40005/7e699de0;
independent freeze50828/16402cc8 binds260 inputs. All23 historical methods and
119 assertion/rejection calls are preserved through24 D199 fixture and12 class
fixture substitutions. Seven new methods add64 assertion calls. Seven emitted
functions receive the inherited symbol and incomplete-disassembly negatives.
Historical method names are retained, including a name mentioning29 ranges;
its current fixture and assertion require the adopted32-group packet.

Root's entry_coordinator_freeze01.json is44433 bytes/2e02ce58 and binds268 files.
The source-reviewed entry_host_driver01.py is3502 bytes/e1c5c725, an exact five
metadata substitution derivative of the passing D204 driver. It runs each suite
once, serially, with360-second bounds and fresh owners. Linux uses/dev/shm;
Windows sets a dedicated TEMP/TMP/TMPDIR before interpreter startup.

| First owner | Passed | Skipped | Outer elapsed | Stderr SHA256 |
|---|---:|---:|---:|---|
| entry_first_linux01 | 30 | 0 | 29.066 s | 9978f7d41457c198953f41bad2ca4ac0c473346b815633589ff0a76281131e71 |
| entry_first_windows01 | 30 | 0 | 13.271 s | 5886612e24cf363d993f70a5363563e410b48d9cfab50d87ca8b3332f3625b8f |

Both streams reconcile with their saved receipts. All30 unique method names run
in the same order, both freezes close unchanged, and no timeout occurred.
entry_host_closing01.json is1937 bytes/60995dee and independently verifies all
268 current pins, the eight result/stream files and empty Linux RAM, shared
Windows and dedicated Windows fixture inventories. C: free space at closing
was6858928128 bytes. No manual deletion or reclaimed-size claim is made.

Final source/host review PASS: reviews/P7_motor_const_entry_review.md,
16398 bytes / 0c2e5fac514767619d1434a5f415ddbd00bed58d6d23f8eb7b325fd6ad821ddd.
No open material finding. The reviewer recorded and corrected only its initial
CRLF parsing assumption; raw byte hashes and actual test results are unchanged.
A separately reviewed fixed scope, clean committed HEAD and local check-only
must precede one new file-only entry observation. Its32 ranges,34 aliases,
65 expressions and3834 selected bytes remain fixed. All four file children,
13 remote closing checks, independent local closure and first-error handling
remain inherited. No compile, upload, reset, MCU read or motor operation has
occurred for D205. D201 remains the latest flashed image. Actual instruction
review and a later separately reviewed inhibited run are still required before
claiming constant selections or a SETTLE timing benefit.

Fixed scope entry_native_scope01.json:3815 bytes/4b2f9f5f,13 exact bindings.
Separate admission review PASS:reviews/P7_motor_const_entry_admission_review.md,
5863 bytes/2e187d66647e6d9a8b9330d5b86fc1a6d3c61b2d29c44719bc0bca0b080e6971.
All outside writers stopped before the clean commit and native observation.
