# D086 fixed A0/A1 acquisition validation

2026-09-23 Asia/Dubai. Contract f194579; implementation327c5db. Actual P2 B6
software under D051/D075, not physical acceptance or a phase pass.

## Implemented

The existing native ADC1 owner now offers beginWithButtons/readButtons. Default
battery begin/read stays compatible. The opt-in profile configures PA4/channel9
and PA5/channel10 with fixed sampling/preselection, switches only the single
rank while enabled/ready/idle, and retains exact selected-rank history. Narrow
tracked old/requested states permit bounded cleanup after ignored writes;
unknown state forbids blind repair. PA5 and DAC2 guards are independent of PA4.
A common boot-lifetime claim/fault latch covers both methods. Button results
contain raw14bit data, actual start/completion times and success-only sequence;
no battery scaling or logical START/BOTH inference. Existing100us acceptance
and separate100us cleanup bounds remain. No old B16 value or locked test changed.

## Validation actually run

Paths below are under P2_adc_pair_raw unless otherwise stated.

| Check | Result/evidence |
|---|---|
| Root normal host |2/2PASS,1173main cases/22840417assertions plus37enabled MotorGate/3796846. `host_build`, `host_final` receipts;6.23s CTest |
| Root ASan/UBSan host |Same cases PASS2/2; `sanitizer_build`, `sanitizer_final`;21.83s CTest. These host targets exclude native MMIO source |
| Independent native review |15methods PASS,150positive cases/1329parent assertions across103positive executable runs.210command receipts:208exit0 plus2required negative assertion/crash sentinels. UBSan native substitutes, not ASan or board measurements. `state/reviews/P2_adc_pair_raw/pair_final` and `final_evidence_audit.json` |
| Independent author |Tests derived from contract/public headers/primary-source audit without reading production CPP bodies. Final15methodsPASS278.692s and handoff in `author/`;25new cases,48metadata variants,2probe modes/eight refusals. Draft failures retained. Existing nine battery methods/assertions unchanged |
| Config |17methodsPASS, `config_initial`. Only BUTTON_INPUT_PIN15 added; existing declarations/values retained |
| Existing tools/staging |25toolsPASS28.031s and2stagingPASS3.777s under WSL, `tooling_final`/`staging_discovery_final`.59distinct scoped methods including native15+config17; not all-tooling |
| Actual target compile only |Final source5f2c2329d566b6940d41a3574141773f3e80378358104b3c96fb9a6e7bcb0eb0,83912Bprogram/34700Bcompiler globals,exit0. `target_final` |
| Target source/ELF |Current56file map exactly matches actual compiled source;3ELFs,36nonzero native exports and42AEABIbindings. `target_5f2c2329_bench-default.json`, `root_target_integrity.json`; reviewer independently verifies startup/retention |
| Existing inert registry |Exactly5existing keys independently approved, reproduced and adopted; no new key. `manifest_adoption.json`; reviewer `inert_approval.json` |
| Review |Fresh separate same-model context, not cross-model or human approval. Final disposition `state/reviews/P2_adc_pair_review.md`; raw final evidence verdict PASS/no open finding |

Compiler environment refreshed: WSLGCC13.3.0/CMake3.28.3/Python3.12.3 and Windows
Git2.52.0; `environment` receipt. Board CLI/core remain the installed pinned path
used by the actual compile command. USB serial2629958581 was visible. No install.

## Findings, failures and interpretation

Root identified inherited P0_QTR_PINS-only nonalias checks; pair admission now
also checks the actual QTR_INPUT_PINS bank. Implementer found missing persistent
ADRDY qualification after enable; final controlsOwned requires it while ADEN is
owned. Independent cases cover ready loss in four setup transitions and final
guard time. Original pre-guard target76174658 compiled83904/34688B and is retained
as superseded evidence, not final source proof.

Author draft failures: overbroad zero-GPIO-write assertion incorrectly forbade
D078's existing PA4-neutral setup; repaired to preserve PA5/unrelated fields.
Typed timing fixture initializer repaired its UInt/UL compile mismatch. Rank
corruption at the write readback correctly returns READBACK/UNCONFIRMED; draft
expected OWNERSHIP. Contract-based corrections and original results remain in
author evidence; no established assertion changed.

Root staging invocations failed collection twice: nonexistent module then wrong
package import for an existing sibling import. Correct unittest discovery passed
unchanged tests. P2_adc_pair_invocation_failure.md preserves both errors and
review escalation. Initial checkpoint writing failed on default cp1252 decoding before any write; explicit UTF-8 succeeded. PROGRESS also corrects a manually mistyped kickoff time.

Implementer historical command summaries are explicitly reconstructed, not raw
stdout or exact-source proof; final strict compile was directly captured. Use
independent final native receipts for the frozen-source claim. Git text identity
receipt shows only CRLF normalization in three new cases, runner and registry;
production/probe bytes match committed source exactly. Raw receipts are binary
preserved; no inferred child assertion total or physical success is reported.

## Remaining work

No upload/reset/MCU/pad/sensor/motor action occurred. Board work was Linux compile
and offline ELF inspection. Last-known MCU image remains inertP0QTR61d7a2d0;
no fresh runtime claim. ADC reference/divider, PA5 settling/carryover/accuracy,
START/BOTH separation, live ownership and whole-tick800us remain unverified.
IMU600+motor150+twoADC100 already total950us in acceptance ceilings before other
work. SC-A/SC-AJ/F091 and every physical/human gate stay open.

Next actual task: B6 button evidence decoder/adapter and existing logical service
integration, per `next_button_task.md`. Freeze explicit ambiguity/source identity/
absence/expiry semantics; failed input must never synthesize NONE or START release.
Matrix output, actual scheduler and remaining original P2-P7 work remain unfinished.
Full project goal ACTIVE/incomplete; no additional hardware request needed now.
