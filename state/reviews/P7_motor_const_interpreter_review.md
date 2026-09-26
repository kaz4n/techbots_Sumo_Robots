# D207 corrected interpreter, field map and first host review

Status: PASS, no material findings. The actual fixed interpreter, current observed field map and first independent Linux/Windows host results satisfy this bounded review. This is local evidence-format validation; it does not establish a native diagnostic result, runtime cure, coherent RAM, physical safety, WCET, motor permission or phase acceptance.

The reviewer read the actual new interpreter/map only after the separate decoder oracle FINAL barrier closed. No subject import, test execution, device command, compiler, authentication, upload/reset or cleanup was performed by this reviewer. Only this new review file was written; prior final reviews and other contributors' work are preserved.

## Identities and closure

| Item | Bytes | SHA-256 |
|---|---:|---|
| `state/analysis/P7_motor_const_run_raw/interpret_run01.py` | 31259 | `d96c0bec92a5e49571ccfa2fd669afa7bcb27e1fa4243cd20d819ad592b003ab` |
| `state/analysis/P7_motor_const_compile_raw/abi_static01_decode_fields.json` | 16755 | `ecceef9168975b206cf3b3c7d11f24dc9feb16083dbf0f68e11c7b7b94433709` |
| `tests/tooling/test_motor_const_interpreter.py` | 70999 | `a262021875097d93a6e4a6bb362d2d215a4136b246a01b7f20f7c01084a60bd2` |
| `state/analysis/P7_motor_const_run_raw/interpreter_fixture_derivation01.json` | 12214 | `8e04406bef0e643dc70e40c53eaff90bd0d327f7b21243aaf393ba94311e13c6` |
| `state/analysis/P7_motor_const_run_raw/interpreter_independent_freeze01.json` | 37712 | `16561476f8f4eb462cac6a85cdf277c081c12c7ac40c3978f94c23bf78a28483` |
| `state/analysis/P7_motor_const_run_raw/interpreter_coordinator_freeze01.json` | 29804 | `67aa3ca3170dc834d75925650a1252d62a155a34b53a4b71c9bd6606976d4350` |

The adopted D207 contract is `1949c7db32bfda4c3318095597b740ea17644ec5b0109cc2e589387842dbbf85`, and normative `run_derivation01.json` is `c90961438062c153f9c99621eba0617b3fc26b0f3dbdd2c35859ec2e744b5bfb`. All 177 independent oracle inputs and all 184 coordinator inputs were independently rehashed and matched; the latter were checked again after the first suites.

## Exact source preservation

The reviewer reconstructed the actual interpreter from the accepted corrected D201 source, 31266 bytes / `ea43a42f582f6e8bf2dfa4e2090efb03313f3333036cc1a3159d72295f680c88`, through exactly seven declared metadata replacements. Every replacement count and intermediate before/after byte/hash matched, and the final bytes equal the actual subject. These replacements update current paths, map length/hash, run/source/schema identity and the 95368-byte packaged-sketch extent. All operational code is otherwise identical.

In particular, the corrected `_flash`, `_receipt_types`, `_counts`, `_read_types` and `_read_rows` function source bytes are unchanged. The first D201 failures and corrected predecessor are preserved; no earlier faulty implementation was substituted. All 55 function names remain. The fixed plan is six windows, 4516 bytes per sample, 26 reads and 727128 bytes overall, with packaged-sketch tail chunks of 29832 bytes. The previous-live window stays excluded.

Source inspection confirms strict UTF-8 JSON, duplicate-key and nonfinite-number refusal, stable recursion-error rejection, exact Python types excluding bool-as-int, bounded packet/map reads, canonical base64, exact path sets, lengths and hashes, and the fixed upload/capture identities. The map's exact byte/hash admission precedes decoding. Scalar decoding stays explicitly little-endian; Boolean storage must be binary and floating values finite. Nested ranges and widths are bounded. The trace retains all 64 slots and loss fields; it is not truncated to a declared count or promoted to a finished recording.

Receipt validation preserves the corrected error order: exact keys/types/identities, upload success, capture error/clock shapes, counts, ordered reads, exact files, waits, flash boundaries, then capture status. Attempted/successful count prefixes are constrained to the declared plan. Partial failures preserve admitted receipts and successfully decoded preceding windows. Unread tails are distinguished from declared-but-missing bodies. A failed capture remains PARTIAL even if every read exists; it cannot become DECODED through flags alone. A complete capture requires all reads, successful brackets, no errors, matching before/after chunk hashes and the bounded duration. Repeated fields may be compared while coherence remains `UNPROVEN`.

SETTLE interpretation preserves every raw number and keeps presence/availability separate from a zero value. Absent or unknown flags do not create measurements. Nine reason numbers retain their fixed labels; unknown reason, validity or freshness bits are preserved and reported as issues. The existing 150 us deadline and 4095 final poll-index boundaries remain. First failure is independent of a later successful current sample. Semantic inconsistency produces annotations without replacing raw data or falsely claiming a structural decode failure. The output retains the first structural error and all prior verified evidence.

The CLI still requires an exact packet SHA-256 and Python bytecode disable, reads fixed local inputs with limit-plus-one bounds, creates `decoded.json` exclusively, serializes without nonfinite values and returns distinct DECODED/PARTIAL/REJECTED codes. Filesystem/output failures propagate without deleting or replacing evidence. Pure interpretation contains no native action.

## Field map against current file observations

The reviewer independently applied all seven declared map metadata changes with every intermediate hash check. Canonical JSON exactly equals the actual 16755-byte map. All sixteen type definitions and 115 selected fields remain identical to the accepted predecessor; only provenance metadata changed.

The current raw ABI receipt is `state/analysis/P7_motor_const_compile_raw/native_abi_static01/result.json`, SHA-256 `bbdecb404a42237fafaf0bf4b2e38690b62ee45119cdfabd9b2f7dde17a6b9b0`; its interpreted ABI summary is `6fed52b884c6015a2c9d2f6803bea20e764418fcc94cffe144161026259f6a97`. The reviewer decoded the saved command-3 GDB output as data and independently extracted all sixteen complete selected `SUMOX_LAYOUT` blocks. Each equals the corresponding D199 block byte-for-byte and matches the declared block byte count and hash, without projection.

All six map windows match current observed addresses/sizes. The retained before-abort previous tick is nested inside the report at offset 1120; the old live previous address is not a capture window. All eleven SETTLE field offsets and widths match current ABI observations, including 12-byte samples, 28-byte report, current offset 0, first failure offset 12, presence offsets 24/25 and reserved bytes at 26. The nine enum values agree with current observations; enum size/alignment remain one byte. Validity masks 1/2/4/7 are explicitly pinned-source semantics, not falsely described as queried ABI metadata. The source pin remains `2eced554fce20ff938daf44866ee0bad6d99fa28e377af762bb0f037376b75a8` for `src/hal/motor_settle_probe.h`.

This is file-observed layout provenance. It does not prove MCU content, publication atomicity, cross-window correlation or host ABI equivalence.

## Independent oracle preservation

The predecessor oracle is the corrected accepted D201 file, 67442 bytes / `1800b0cd3772e06020bff45d0637ea8a9c8f70ab7a6624a81f6a05af30fdde66`. Static literal reconstruction reproduced the pre-supplement fixture, 67425 bytes / `862caecd77ff15c57731c514bbcff5963a7e2910e52475ae477ef280961f2995`. All 67 inherited test-method ASTs equal their projected counterparts, retaining 125 assertion calls. All sixteen independent field declarations remain unchanged and match the current map. The entire corrected portable deep-JSON recursion fixture remains byte-identical; no recursion-limit change was introduced.

The three added methods contribute nineteen assertion calls: exact seven-step source/map identities; refusal of D201 run/source identities in both receipt roles; refusal of the old map, padded old map and obsolete 95520-byte package-tail reads. They supplement the retained inverse packers, all selected fields/aliases, every Boolean leaf, finite/nonfinite float cases, all 53 legal attempted/read prefix pairs, exact error ordering, clock/wait/flash boundaries, first-error preservation, output exclusivity and pure-seam no-I/O checks. They do not replace inherited assertions or derive expected scalar values from the implementation.

Before decoder execution, the reviewer also checked the companion host driver: 3669 bytes / `611d499d28bb4c6c3907dbe8008494d98419a8c85e29cac4d3656d169b501fa4`. It differs from the pinned 3687-byte `48685b07b563becb14a855495eea1c90c7e47ae666fdb266c147c14b3d89f476` driver only in restricting the suite to interpreter and adding unittest `-v` to the two platform argv lists. Exclusive owner creation, 600-second outer limit, stream preservation and closing pin checks remain. Linux uses `/dev/shm`; Windows uses its dedicated owned temporary directory. These are host fixtures, not actual board operations.

## First actual host receipts

The reviewer checked both original saved result receipts, intent argv, full streams, stream hashes, every test result and matching method order. Both suites returned zero, ran all seventy methods with no skips, had empty stdout, unchanged freezes and no changed pins. Windows temporary remnants are empty.

| Platform | Test time | Outer elapsed | Result receipt SHA-256 |
|---|---:|---:|---|
| Linux | 5.306 s | 18.0962437 s | `6ee617191408de5c5a5f1c7db4424258c3fd92790ec7e9e092ac00a7cf3ed103` |
| Windows | 5.303 s | 5.7291064 s | `84eedd27e7a97dcc2a31504bd4cde11c683adaf4ddf8645ddf17d87b54d79ac1` |

Receipts are `first_interpreter_linux01/result.json` (882 bytes) and `first_interpreter_windows01/result.json` (948 bytes) in the run raw directory. Stderr hashes are respectively `2e7c5e8bcb49c2830ddee20025cd6413a5c1323dc6d1dc863c0e96d701376d01` and `040956781ed0242db0d0f780d91087a1b8b9a559fe16ffb5b3795285896f5ddc`. No decoder retry, source repair or oracle amendment was needed for these first results.

## Disposition

Source, current map and first host evidence PASS. Separate accepted fresh board admission, exact committed native scope and guarded one-shot execution remain prerequisites to obtaining any D207 native result. That result and its decoding require their own independent actual review. Host success cannot establish that the D201 setup deadline fault is repaired or that later epochs will complete.

Final review; STOPPED WRITES to this file after recording its external hash.
