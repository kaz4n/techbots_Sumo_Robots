# D193 compile projection: source and host review

26 September 2026. Reviewer `/root/cleanup_fix`, separate same-model context
from the launcher implementer and independent oracle author. PASS for SOURCE
and HOST scope; no open material finding. I read the contract, launcher,
original modules, frozen oracles, repair diffs and actual host receipts. I did
not execute tests, dispatch tools to the board, compile target firmware, edit
implementation/tests or commit. This review file is my only write in this scope.

Reviewed launcher `tools/compile_app_motor_observe.py`: 7583 bytes, SHA256
`70e1f016cec041b40c98c7c5dd5ee20223d75c4a876c76d2fcdea3d790d63827`.
Contract `state/analysis/P7_app_motor_observe_compile_contract.md`: SHA256
`0301726f47c0c438a7984ddd232f81c4891c511651ba81a986b15f5ef91dbfb4`.

The three original modules remain byte-exact: caller `cf0c826f...`, adapter
`3e5d49e4...`, remote observer `1428b934...`; their full hashes match the
contract. Ordered literal projections match its counts and original/projected
identities. Import defines only functions/constants, invalid arguments are
rejected before loading, and all three sources/projections are verified before
private caller execution. The historical main guard remains false. Private
ModuleType instances are not published in sys.modules or used to mutate an
existing module. Synthetic original __file__ values preserve root/default and
dependency derivation.

| Projected source | Bytes | SHA256 |
|---|---:|---|
| Caller | 29904 | `830299e516c9221db35f81e2b01100cd5f0444cd7a78ca6148048805d2078884` |
| Adapter | 8266 | `e3d23d5c6b2bd2d088f954a2dd2b574188edca8ca95d65a4432e54de759d169d` |
| Remote observer | 6897 | `f7886c869980afc969082b66ce8d3fc35801fe7c11134b406af158f06049160c` |

ADAPTER/REMOTE_HELPER and self.code retain original disk bytes. REQUIRED and
HARD_PINS include the original caller/remote plus every inherited dependency;
the manifest binds the new launcher/contract without a self-hash cycle. Local
and closing checks continue to verify these original inputs. Only the adapter
and remote payloads are projected for their designated calls, including the
remote source_sha and projected adapter bundle hash. Derived aliases and paths
remain constructed by their checked definitions. Original source mapping,
exclusive owners, static/default/MATCH0/MOTORS0/probe1 flags, one query/compiler,
jobs1, deadlines, first-error retention and independent closing checks survive.

Payload/compression/canonical response limits and the final composed Windows
argv bound of 30000 UTF16 units remain enforced. The inherited controlled command-composition case
passed on Linux and Windows, including the refusal of an oversized command
before subprocess dispatch. This is host composition evidence, not a native
execution claim or an exact byte-length measurement reported by this review.

## Findings and resolutions

Initial launcher `e7b8582b...` admitted a pathname, then used a blocking open and
read before checking the descriptor identity. A regular-file-to-FIFO swap could
block before rejection. The repaired source uses O_NONBLOCK where supported
and rejects nonregular, multiple-link, reparse or identity-mismatched handles
before fdopen/read. Final ancestry/path/descriptor drift checks, Windows ctime
separation and primary-error-over-close behavior remain. The reversible change
is retained in `analysis/P7_app_motor_observe_compile_raw/bootstrap_review_fix01.json`;
the frozen real FIFO and pre-read identity tests passed on Linux. CLOSED.

The first Windows caller run failed at fixture symlink construction with
WinError1314, before the subject was called. The original 58-case oracle and
failed receipt were retained, including commit `9eb8c9c7`. The independently
adjudicated fixture-only correction split all three mandatory hardlink checks
into a separate method. Symlink creation skips only the explicit Windows1314
case; all other errors propagate, and all file/parent symlink assertions remain
on Linux. Conditional cleanup restores originals if creation fails. No product
or inherited oracle changed. The diff and corrected freeze are retained in
`caller_fixture_repair01.json` and `caller_independent_freeze02.json`. CLOSED.

The initial caller suite did not execute the projected remote observer or the
adapter's artifact validator. The separate frozen 35-case supplemental oracle
now executes both, preserving 14 original remote assertions, 15 metadata
assertions and three artifact delegation/name assertions, plus three new
identity/bundle binding checks. Actual passing receipts close that coverage gap.

## Actual host evidence

All receipts below are under `state/analysis/P7_app_motor_observe_compile_raw/`.
Durations in the table are unittest-reported durations, not outer process wall
times. I read the results and independently hashed the cited final receipts.

| Receipt | Result | Duration | Frozen input result |
|---|---|---:|---|
| caller_linux_first.json | 58 passed | 31.144 s | 195 pins unchanged |
| caller_windows_first.json | 55 passed, 1 fixture error, 2 skips | 59.010 s | 195 pins unchanged |
| caller_linux_final.json | 59 passed | 33.906 s | 197 pins unchanged |
| caller_windows_final.json | 56 passed, 3 explicit platform skips | 58.993 s | 197 pins unchanged |
| remote_linux_first.json | 35 passed | 41.604 s | 196 pins unchanged |
| remote_windows_first.json | 19 passed, 16 Linux-only descriptor skips | 6.297 s | 196 pins unchanged |

Corrected caller oracle: SHA256
`ae42938cace40745068421bf6e8e813295b12c16b376c93bd00b019b311b724d`.
Supplemental oracle: SHA256
`897ae6e468aaa619ff72fa03532278458a250cfc440add52fd8eff180d587413`.
Final caller Linux/Windows receipts:
`cdff63debf9724bfb8d0192043131fb2e68185f2f4fdba689fb9057643b042f3` /
`d2b58da96279a1cc693864616ec99ddbd645be7e5e2f072fe749d0bb9cd961a9`.
Supplemental Linux/Windows receipts:
`7af317879015688da67ae442061fdcee7315c6652c1a6f99732418ccce8b862e` /
`d0cfa9774d00b87972242d7e5e98a0e6887db611e6596c27705db445ba2334ef`.

The final Windows hardlink method passed; Windows lacks the privilege for real
symlink fixtures and lacks Linux FIFO/descriptor semantics. Linux provides the
corresponding real-path coverage. These explicit skips are not hardware checks.

No actual manifest/board admission or native compile scope is approved by this
review. Fresh exact source/boot/owner bindings, clean reviewed HEAD and separate
actual-scope review remain required. Target layout/loadability, sustained
runtime, the historical IO fault, live RAM/stack/WCET, electrical/sensor/motor
acceptance and all human phase gates remain unresolved by host results.
