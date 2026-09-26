# D212 ordinary remote/actions source and host review

Status: FINAL PASS for the scoped remote/actions implementation and corrected native host evidence. No open material findings. This is a separate same-model review using reused context, not human or cross-model review. The reviewer authored the independent decoder oracle; this review concerns the separately authored native remote/actions sources and native oracle only. Caller source and decoder acceptance remain separate.

## Checked identities

Paths below are relative to `state/analysis/P7_ordinary_app_run_raw/` unless stated otherwise. SHA-256 values identify exact bytes.

| Input | Bytes | SHA-256 |
|---|---:|---|
| `remote.py` | 11269 | a2c2fc9d32694a96a406b6de499bfb04a2a159710443c8b37ca56e92921a536f |
| `actions.py` | 12496 | 07c03a65fad73f49064abd0af77161b5ed10e2c6002bb6c442e7ab5b28ee25b1 |
| `native_fixture_derivation01.json` FINAL03 | 194972 | 8cfd7f553c4e17334a899c575d2b4935cbcfd69c332b43c7fe0a84bfc1f95372 |
| `native_independent_freeze01.json` FINAL03 | 89811 | f0238fde982c1f2f35dec11f8f3d4316cee85471a3303cca13973886df3df786 |
| `native_coordinator_freeze02.json` | 58246 | 7ef6cd290b97581a16fc41ba71c5ce9797ab855d6950da9490532f65249b97ab |
| `host_driver02.py` | 3688 | 758ac4e15f8b7dda2458cd43c122fb0683ea1b97209bd77b9390729d6b58edda |
| `native_host_closing01.json` | 33561 | 90f4d6b5f479bff1f427912864de5565451f1a0b1c836e09ed4526580689175c |

The adopted contract is25120B/828b334235877131580618908cc164381a988f297c4e22235eb72e34fe200e75; derivation119497B/9a8ef9caa96f0e30a8ad741319d5ea59668b8e6066d0c96fb59defd35f896d66. Current tests are `tests/tooling/test_ordinary_app_remote.py`9831B/674c832edf77a2365234f80a17cf629fd6fedcc49501337c9c2984c2d3ac6083 and `tests/tooling/test_ordinary_app_actions.py`7125B/d7e5fefd3739288fd7f2076ddb8440d4a450a4f9dcbe945c72681989bad91847. All332 independent inputs and, after the corrected hosts, all344 coordinator inputs matched. The closing receipt records the coordinator pin and exact method outcomes without duplicating its full pin inventory.

## Source and fixture conclusions

Independent byte reconstruction confirms exactly17 remote and11 actions metadata steps from the pinned D207 subjects, with no other operational change. Artifact/source/run identities, ordinary paths, schemas, adapter identity and seven current windows agree with adopted data. The plan is28 reads/715858B: two263680B loader brackets, two92944B sketch brackets and two1305B SRAM sets. First/second sets begin7/14; flash completions are4/6/22/27; waits remain30s then2s. Raw92928B and packaged92944B artifacts stay distinct.

Pinned dependency checks precede dependency execution; fixed identity/path/absence bindings and fresh owners remain enforced. The inherited descriptor/no-follow, file-hash, process/resource, child timeout/reap, bounded output, exact read, durable prefix and first-error/closing checks remain. Failed upload or outward failure suppresses capture; durable-unattributed recovery cannot become successful returned evidence. Capture retains its600s budget and30s children; upload and action envelope bounds are unchanged. Windows command bounds remain30000 UTF-16 units including NUL, with the existing base85 fallback. No retry, arbitrary command, scope expansion or privilege operation was added.

Reconstructed private provider/core projections retain42 remote and24 action behavior methods and267 assertion sites; five ordinary cases per suite add53 test-body assertion sites. The shared recipe helper now has four assertion sites, one more than before. All106 native method inventories remain unchanged. Linux descriptor tests and explicit Windows skips are preserved. Fresh typed/stale source, run, image, adapter, schema, wait, malformed receipt and owner negatives retain real rejection paths. Current byte equality and ordinary binding equality are retained, not replaced by success stubs.

Three fixture findings are closed, with original evidence preserved:

- Before execution, the action flash-hash mutation moved from historical index19 to ordinary index21. It now targets after-sketch data rather than SRAM; all assertions remain. Original proposal/oracles are preserved at57ff804f.
- First Linux remote run had45 passes, one failure and one error. `assert_recipe` incorrectly passed normative rows lacking intermediate hashes to strict `project`; the corrected helper performs an ordered occurrence-checked loop, while strict `project` stays byte-identical. Both inherited binding fixtures also carried an old boot ID; one projected helper keyword now sets the adopted boot ID. Every other field already matched. Product sources did not change. Failed receipt and FINAL02 are preserved at0331c9d3; adjudication is saved in `first_host_adjudication01.json`.
- Review-only bookkeeping refusals involved AST-segment versus complete-line method pins and an unnecessarily exact expectation for equivalent keyword formatting. Corrected read-only comparisons established exact line pins and the sole authorized boot-keyword AST addition. These were not product/test executions or evidence changes.

## Saved host results and closure

| Suite | Linux | Windows | Outer seconds Linux / Windows |
|---|---|---|---|
| Remote |47 PASS |29 PASS,18 explicit skips |19.971 /2.017 |
| Actions |29 PASS |24 PASS,5 explicit skips |19.237 /1.127 |

All152 ordered remote/actions outcomes match their frozen inventories. Each of the23 Windows skipped IDs passed on Linux. Raw intent/result/stdout/stderr hashes, empty actual Windows temporary directories, no timeout, unchanged freeze and no changed inputs were checked independently. Both platforms measured actual full Windows argv at29662 upload and28722 capture units including NUL.

At root's separate request the reviewer also reconciled caller receipts as data, without adopting its source-review scope:30 Linux PASS and9 Windows PASS/21 explicit skips. Thus the compact native closure contains212 outcomes for106 methods,106 Linux passes,62 Windows passes and44 skips, all covered by Linux passes. All six corrected suites returned0. A single saved read-only WSL check after native suites confirmed UID/GID1000 and no `/dev/shm` entries for `sumox_d189_`, `sumox-d189-bootstrap-` or `sumox-d189-run-`. All three Windows temporary directories were actually empty. No deletion was performed. C: free space was7404572672B.

## Acceptance boundary

This accepts source and controlled host behavior for the fixed native remote/actions scope. It does not admit an actual upload/capture, decode application SRAM, prove continuity/coherence, physical inhibition, firmware initialization, WCET or a phase gate. Ordinary firmware remains continuous; capture completion is a host collection outcome, not terminal firmware/final-halt evidence. Separate decoder correction/host closure and final board/resource/scope/clean-HEAD admission are still required. The reviewer ran no tests, imported no subjects and made no device calls; the only local subprocess beyond data/Git reads was the authorized read-only WSL remnant listing. Review and native closure were written as exact UTF-8 LF bytes; writes to these two finalized files are stopped.
