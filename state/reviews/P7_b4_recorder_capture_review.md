# D218 recorder capture and local decoder review

FINAL PASS, 2026-09-26. Independent reviewer using the same model and reused project context; not human or cross-model review. The reviewer inspected sealed source, normative data, independent fixtures and saved host receipts without importing/executing subjects, running tests or contacting the board. No material finding remains open.

## Reviewed identities

Receipt paths below are relative to `state/analysis/P7_b4_recorder_capture_raw/`; all hashes are SHA-256 and sizes are bytes.

| Evidence | Bytes | SHA-256 |
|---|---:|---|
| `../P7_b4_recorder_capture_contract.md` | 12517 | c6eba89ae4a5567d220fd69ccc73190c2918e05e6fac57eba35697ca5460bc6b |
| `plan01.json` | 8384 | 14137f101e508e93c556eff2c0e2526cde4f63217def6e7c376d5f5078e3e5f7 |
| repository `tools/b4_recorder_capture.py` | 9769 | e28d01312742389737c0ca0d6914ab8593d59f93b1a67ac302029749f11b4189 |
| repository `tools/decode_b4_capture.py` | 10061 | 1c0f75c001b8f66e9b3f5f4ed2be8472c8aaf1991265cfb6f91e4372043f6109 |
| `derivation02.json` | 9819 | 115a27cbe3548fd04c832a2a0ec84ff35107fe07311535450229f57201b23099 |
| `repair01.json` | 1715 | 0e665a2d2cc70d4bd89d7b9e56fe00d357e02ab45e992609ca725bd4ab2c8af6 |
| repository `tests/tooling/test_b4_recorder_capture.py` | 31592 | d0476af156990efcc182750584e9d2af451937c3ef450c72efba0cf82ac828dd |
| `capture_oracle02.json` | 12201 | bf14d974be5f9b905ac2e263862c555ea1d14d095b8c9865ae006aed46b36993 |
| `capture_oracle_repair02.json` | 3960 | 4d2a3b0bda260ea4dc60660e556501d2de66fbc938e261376d1e9ab291b6089a |
| `capture_coordinator_freeze02.json` | 6617 | 48e05f6863711f005f81803c306322c1f72c8a749e5dd40a22d23fb643bbb7d4 |
| `capture_host_closing01.json` | 8096 | 321ab6747d7167b45f55cbfd389c51dfd6b9a7ff2e2402f9cf6b647c9f3237c8 |

## Source and data

All 15 derivation inputs, both current subjects and the 17 independent oracle basis pins match. Fixed bindings, three dependency snapshots and read-plan constants equal the normative plan. All dependency bytes are checked before private execution. The native module overrides exactly profile_bindings, prepare_plan, gather and complete. All 32 recorded historical Capture/_collect function spans reconcile with the pinned support source; inherited algorithms are unchanged. Their existing admission, exclusive ownership, command receipts, process bounds, first-error handling, final checks and finally-close path remain the applicable lifecycle boundary. A returned report is attributable only after that call returns successfully; a previously written durable report cannot prove close success.

The plan is exactly 26 reads/852624 requested bytes: loader/sketch comparisons before and after twelve SRAM reads, including ten owner chunks totaling159200 bytes and two120-byte lifecycle brackets. Before-loader/sketch comparison failures stop before the first SRAM read. gather refreshes analysis in finally after every attempted read, preserves incomplete raw evidence through the inherited lifecycle and adds no wait, reset, halt or MCU write. Phase remains numeric, and all three pairwise lifecycle comparisons remain observations with UNPROVEN coherence.

The local decoder enforces exact input types and finite byte/file bounds before hashing/parsing, strict duplicate/nonfinite/UTF-8/JSON handling, returned-close attribution, the fixed13-file set, durable/embedded report identity and exact types, timestamps/counts, ordered records and all SRAM lengths/hashes. It checks four flash flags and seven paired chunk hashes, recomputes owner/lifecycle/equalities, and verifies the exact D215 layout before calling unchanged D216. Supplied flash metadata is explicitly structural evidence. No source I/O, transport, native dependency loading or output write occurs in local decode. Nested D216 export refusal remains separate from capture-bundle success.

One pre-test source defect was found and corrected: raw_owner was assigned only after validating the final lifecycle bracket. It now publishes immediately after validated owner.9, retaining the complete owner if the later bracket fails while refusing READS and leaving decoder unset. Incomplete owners never publish. Reversing exactly the three declared count-one edits reconstructs the original10009-byte host source /4080c15f9185ff26dd21db7a2795943fa724071d6a8175b1b1b4608ee8f0deae; native source and all other behavior remain unchanged. The original derivation and bounded correction are preserved.

## Independent fixture and host closure

Fifteen focused methods cover exact dependency/unchanged-body identity, current/stale binding types, fixed geometry, all four flash-stop boundaries, partial native observations, complete owner and literal D073 CSV output, late bracket retention, all SRAM hashes, lifecycle mismatch, nested decoder refusal, envelope/closure eligibility, exact record/type/analysis/layout requirements, bounds before hashing and I/O prohibition. Native reads are substituted in memory; historical filesystem/process coverage is retained by exact dependency identity rather than replayed. Windows import-only POSIX stubs prohibit their native operations. These fixtures are synthetic, using the fresh actual ABI as immutable layout data.

The original Linux run executed15 methods:14 passed; the JSON method had two assertion failures. One fixture kept a stale durable-report hash, so REPORT refusal correctly preceded parsing. The other assumed a2048-level array must trigger parser recursion, whereas supported Python parsed it and then correctly refused ENVELOPE. The authorized single-method repair refreshes durable identity, allows only the applicable parser-or-shape refusal codes for real deep arrays, and adds deterministic json.loads RecursionError requiring INPUT_JSON. REFUSED, raw preservation and no nested decoder remain mandatory; invalid UTF-8/syntax/duplicate/nonfinite cases retain exact INPUT_JSON assertions. All bytes outside that method and the other14 methods remain exact. Original test/oracle/failure streams are retained; production was unchanged after the pre-test source repair.

Corrected Linux02 passed all15 methods, no skips, in0.822 seconds internally/11.7410975 externally. Windows02 passed the same15, no skips, in0.876/1.2024547 seconds. The reviewer independently reconciled all30 ordered outcomes, all12 saved files including the original failure, all36 coordinator pins, unchanged freeze evidence and empty stdout. Neither corrected run timed out or changed inputs. Windows temporary ownership is retained empty and was checked locally; no separate Linux remnant inventory is claimed.

The bounded host drivers are exact metadata derivatives: driver01 changes five D217 labels/paths; driver02 changes only freeze/output ownership. Current driver02 is3508 bytes /7c95b58bfacede2580db38f8689f9c58c8c2a0eebb8e92b5298958c46d720e29. Both corrected runs use isolated Python with bytecode disabled, fresh exclusive receipt owners and a360-second bound. Independent positive fixtures fit the unchanged limits:5393-byte report,5870-byte envelope and13files/164833 bytes, including the159200-byte owner. These are fixture sizes, not captured target data.

## Boundary

Accept D218 software components and corrected focused host evidence. This does not admit or record a native capture, upload, firmware run or motor operation. A qualified caller must still supply exact staged inputs, successful returned closure and complete retrieval; the currently loaded ordinary image is expected to fail the fixed B4 flash comparison before SRAM. D216's provenance/loss/lifecycle results remain independent of structural bundle success. Equal brackets, sealed phase, local hashes or incomplete=false prove neither atomicity, common attempt, hardware origin, transport integrity, completed B4 motion, physical inhibition, WCET nor a phase gate. No new standalone capture launcher or upload policy is implied.
