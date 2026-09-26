# D194 observer entry preparation review

26 September 2026, Asia/Dubai. **PASS for prepared source / host scope; no open
material finding.** Reviewer `/root/fresh_review` is a separate same-model reused
context. Review used local source, contract, fixture and receipt reads, hashes
and static AST/data comparisons. The reviewer did not import subjects, run
tests, invoke native tools or contact the board. Only this review was written.

## Fixed scope and source

| Item | Bytes | SHA-256 |
|---|---:|---|
| Entry contract | 11303 | `437f8cb87b7456f0dfc766e506830e0f5ba23cc5b605de5957ff458b5603caaa` |
| New inspect_static_entry.py | 9394 | `0c3a3dd1fd19ffc51dc90b3d47081cf4bb8d2cc4b84076756ff92b4a49d893ad` |
| Independent 19-method oracle | 29705 | `b7db0b43ae5e487cd6475e0b6dd6272d33a8316bcfba64a07f6c2a3e2c0415d8` |

The wrapper privately composes the unchanged ABI02 reader with the preserved
historical entry parser. All five input lengths/hashes and the new contract
hash are checked before private execution. Independent source-body comparison
confirms all five bootstrap helpers are exact copies of ABI02, preserving
ancestry, single links, reparse rejection, bounded reads, descriptor identity,
Windows execute-bit handling, full same-API stamps, digest and closure behavior.
The module namespaces remain private, with original absolute __file__ paths;
historical entry load/main are never called. Inherited pins remain and the
six new inputs are added. Strict CLI/Python -B checks precede input reads.

Static application of the literal replacement tables, without subject execution,
confirmed every occurrence count and both exact projected identities:

- Reader: 16955 bytes, `93729533a1d02e54f6812142aa94cf38e7a93a04d5e03d8a5fc4902386f6a421`.
- Parser: 10333 bytes, `6a82a9e5381aace9375673678bd763db95f93ad5de6d90d8d26abea2e2852767`.

The reader diff contains exactly the nine prescribed identity/owner/output
substitutions. Parser changes are exactly its build-path literal, six Runner
namespace occurrences and 32 address-literal replacements. No lifecycle or
parser logic is changed. Returned queries and summary are replaced directly
with the private entry parser functions; ABI02 polls-tag interpretation is
not applied to disassembly. All historical source/tests/contracts and consumed
owners remain intact. D193 build OWNER and artifact bindings are unchanged.

## Current range evidence

The reviewer independently decoded the accepted ABI02 readelf and confirmed
its byte identity with attempt01: 158577 bytes / SHA-256
`b3542b0d38be98be71ff1318648b3f1817ce406e9f62cf64e1dcdcc9c0e4fc0b`.
All 27 projected function groups agree with its exact address/size/type/binding/
section tuples, including Thumb bits and both C1/C2 aliases for Runner and Trace.
All ranges lie inside the current .text section; all six initialization-bound
symbols match. Section1 .text is at `0x08100010`, size `0x16228`; section2
.init_array is at `0x08116238`, size 4, with end `0x0811623c`.

These addresses are bound to the successful ABI02/D193 evidence, not guessed
from the older build. The initializer FUNC symbol is `0x08100105`, but ABI02 did
not read .init_array contents. The proposed readelf -x query must observe that
word anew. The four commands retain pinned tools and guarded file-only GDB,
with 27 exact marker-delimited disassembly ranges. No target connection,
function call, compile, upload, reset or MCU read is introduced.

## Independent oracle and first host results

The oracle was frozen from contract437f8cb8 and pinned historical public parser/
fixture interfaces before its author read the new implementation. Independent
freeze `entry_independent_freeze01.json` is SHA-256
`057451b0c2009840d2c9cb837d6b7306e7cdceba510c46fa41b9322f8bcb0190`.
The reviewer read the complete oracle. It constructs synthetic complete symbol
tables, all 27 disassembly blocks, constructor aliases, initializer bytes and
bounds independently from the fixed contract map. Process/socket endpoints are
blocked; Linux scratch is /dev/shm and temporary files are cleaned automatically.

Coverage includes passive import/strict CLI, exact copied bootstrap bodies,
both projections/rejections, all six inputs checked before private execution,
original-first composition, no historical load/main, direct entry replacement,
retained pins/new owners, exact commands/ranges, decimal/hex sizes, both opcode
widths, exact raw block hashes, symbol/alias/Thumb/binding/section failures,
initializer span/pointer failures, marker/order/format/gap/overlap/coverage
failures, raw retention, consumed-owner rejection and local/primary-error
closure. Synthetic mnemonics establish framing, not instruction semantics.
No material fixture defect was found for this bounded scope.

| Receipt in P7_app_motor_observe_abi_raw | Result | SHA-256 |
|---|---|---|
| entry_first_windows01.json | 19 PASS, no skips, exit 0; 1.472 s | `55e60bef33935c9d1521a6ac578cbe892536a2a9984ff2034bdb0b2feef62d65` |
| entry_first_linux01.json | 19 PASS, no skips, exit 0; 7.344 s | `9f9e862fef658658d735b14f738f831bf7b62a4c45460267b574f474be1d9c1e` |

Both first runs used Python -B and verbose unittest discovery. No failure-driven
source/oracle change occurred. The reviewer independently hashed all 150 files
against `entry_coordinator_freeze01.json`, SHA-256
`6ad2e4340f16094e7e2243f82bb398b43b47a48b7f45b14c20ec1a7adc6add0b`:
all match. All prior 142 inputs remain unchanged; eight new entries were added
and none removed. Local `native_entry_static01` is absent. Unrelated scratch
inventory or future upload preparation is outside this review.

This PASS supports separate clean-HEAD/live admission for the exact entry scope.
Actual file-tool output, initializer word and complete disassembly remain
pending, followed by separate instruction review of wiring, construction,
inhibited grants, bounds, stop priority, capture and terminal behavior. Parser
success alone does not prove those semantics. No runtime, motor permission,
physical acceptance, RAM/WCET or human phase gate follows from these host tests.
