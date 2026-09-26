# D243 outer-loop timing independent source and host review

27 September 2026, Dubai. **PASS for scoped source and host preparation; no open material finding.** This is not P2.2 acceptance, target timing or physical qualification. The reviewer inspected source and retained receipts only, performed no tests/native actions, and wrote only this report. This reused reviewer context supplied bounded measurement-design advice; it did not implement the observer or author its fixtures.

Reviewed the contract checkpoint a4540854c3a730fe3531a0f6188153e2d0340891, actual Runtime/Transaction boundaries, final observer/app/config changes, focused fixtures/runner, preserved earlier attempts and final validation. Existing Runtime, HAL, D229 distribution and locked tests have no diff in this change. Other agents' unrelated edits were left untouched.

## Source disposition

The timing-profile-only entry binding measures consecutive entry timestamps. Each retained wall interval includes the preceding Runtime step, D229/completion bookkeeping, observer work, context storage, return and framework/interruption gap. It is neither isolated CPU time nor calibrated WCET. Runtime still executes exactly once per application loop, including observer closure and error calls. Ordinary default/MATCH branches contain no new observer, diagnostic timestamp or update.

The first entry anchors the half-open 300000000-us start cohort. The complete final straddler retains its own start, closing end and overshoot. A separate single drain records last-publication work outside that population; its final timestamp/storage/freeze/escape tail remains explicitly unmeasured. Missing the next entry leaves an incomplete population or drain. Sealed and error states stop all subsequent diagnostic reads/writes without aborting or resetting Runtime.

Raw modular chronology admits ordinary wrap and bounded equal-clock quantization; reverse/ambiguous or stalled clocks preserve the first offending anchor/context and known prefix. Histogram/count saturation remains partial evidence. Both all-poll and completed-labelled distributions are required: many idle calls cannot hide completed-poll p99. Delayed histogram cost may land in a following idle interval, so the completed-labelled statistic is not a reconstructed per-epoch CPU budget. Runtime completion/failure can overlap; impossible context transitions and saturated epoch inference remain explicitly uncertain.

Summary scans are outside application-loop sampling/sealing. A named owner and scoped compiler escape retain diagnostic data; no capture protocol, guessed address, source grant or new deployment framework was introduced. The source functions remain below 60 lines. Initialization_complete is context only, not continuous all-sensor readiness.

## Findings closed before acceptance

1. The original entry path overwrote the last in-window interval's start with the drain start. The final header retains last_population_entry_us before that overwrite. Focused assertions check the exact straddler start through draining and sealing.
2. Original uncertainty considered epoch arithmetic alone, allowing impossible phase/result transitions to appear certain. Final contextValid/coherent checks preserve raw facts while marking invalid phase/fault domains, terminal mutation and incompatible active results uncertain. Six focused negative contexts cover the repair.

Original host01 header/test/runner and host02 header/test bytes match their respective saved input pins. Host01's real Runtime suite passed 15 cases/110 assertions, then the typed entry substitute failed compilation because it omitted the real runtime header's epoch_timing dependency. That fixture import repair is disclosed. Host02 passed 15/113 and entry checks but predates finding 2's repair; only host03 is final evidence.

## Evidence reconciled

All 96 flat closure pins match current bytes. All 177 final execution inputs match current bytes, and before/after pins are identical. All 15 saved final compiler/process commands returned zero; every final stderr is empty. No broad suite was repeated by this reviewer.

The final strict C++17/O1/no-exceptions/no-RTTI/UBSan run passed **16 cases and 143 assertions**, with no failure or skip. It covers cohort endpoints/straddlers, pending and failed drain, clock wrap/stall/error, immutable closure, percentile dilution/overflow/saturation, overlapping and uncertain classifications, actual Runtime completion/early/source-failure/terminal paths and heap-operation guards.

The actual app.ino is copied byte-for-byte into typed native substitutes for default, MATCH and timing profiles. These Os/LTO/section-GC executions verify one Runtime call per loop, profile exclusion, both distributions, drain and no later diagnostic mutation. Both ordinary binaries omit the observer symbol. The timing owner is 6688 host bytes; Summary is 96 bytes and Runtime remains 169888 bytes. A separate executable whose main never reads diagnostics retains the named owner; saved disassembly contains both histogram update calls and counter/bin stores, not merely an unused symbol. These are host retention/layout observations, not target ELF evidence.

**Explicit coverage limit:** the defensive real Runtime post-completion stop-bookkeeping invariant-failure branch was not forced. Its completion-before-failure order was source-reviewed, and the observer's overlapping classification is tested with synthetic captured context. Real ordinary failure and other Runtime paths were executed. This disclosed limitation was accepted by the coordinator; no production test hook, private-state corruption or weakened assertion was introduced to manufacture that branch execution.

Principal frozen files:

| File | SHA-256 |
|---|---|
| src/app/outer_loop_timing.h | 372542f723779761d07061858c7a24600331c818e534fbfccd61edfee752800c |
| src/app/app.ino | d7d7458c4fedc193ebd8a7350ab96420f8e0a71b9ae58d169a6464abddfd6302 |
| src/config.h | d4646fcfc8b95465958d624cd460b34cabf3558065c861cbe73089b1eb275a26 |
| tests/test_outer_loop_timing.cpp | b89afa4c252543129429adcebb843c8796dec3de6430414a60fba92e0d77cbaa |
| tests/tooling/test_outer_loop_timing.py | d34c498874fff159eca05a086c0098b6e18784aed895a0106f555c6ab9c08539 |
| state/analysis/P7_outer_loop_timing_contract.md | 236c30d2e99b0269a4d3e04abb264304a4cba2de3b1eaa43c8d755420983a350 |
| state/analysis/P7_outer_loop_timing_validation.md | 2b4e5a5ea3353f8ad2b6c66402fcd906658f22e431722134b91ff28495608eef |
| state/analysis/P7_outer_loop_timing_raw/host03/result.json | 6961c79ba2a526f6b7bbbeb0aa08b805cf7a72821d73835b11efb5314c59b1e9 |
| state/analysis/P7_outer_loop_timing_raw/closure_manifest.json | 2e1531f36243287e99eb0a64530607141d6f80eb376f6bf688cca3da12c211ec |

Accept this exact software/host checkpoint for integration and the coordinator's separately scoped timing-M0 compile-only work. A later target check must verify the retained symbol, actual layout and ordinary-profile exclusion before any fresh source-bound readout. The first-entry cohort includes warmup; SEALED does not prove five minutes of live sensors, all durations below 800 us, calibrated continuity, physical WCET, safe motor operation or any phase gate. No native run or deployment is admitted by this report.
