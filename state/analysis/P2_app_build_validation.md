# D099/D100 actual build acceptance

2026-09-23 Asia/Dubai. The human explicitly resumed from2ded06a. P2 software
continues under D051/D075; no physical acceptance or motor-run authority follows.

## Corrected wrapper, actual UNO Q Linux builds

All commands use the installed explicit USB ADB target2629958581 and dedicated
/home/arduino/sumox26_codex_build root. The state query exited0/device with empty
stderr. CLI1.5.1/core1.0.0 and18 installed file pins are checked by the wrapper.
Every build passed the separate expanded-property preflight, six override/profile
refusals,84 effective command checks, real compilation and postcompile hashing.
No upload/reset/start command was run.

| Command after `python tools/board_tool.py flash` | Exit | Program | Static payload | Nominal remaining |
|---|---:|---:|---:|---:|
| app --compile-only |0|153684B|248308B|13836B|
| app --startup immediate --compile-only |0|153684B|248308B|13836B|
| app --match --compile-only |0|154156B|248684B|13460B|

Exact commands/times/process statuses are in P2_app_build_raw/d100_target_*.json
and their text outputs. Raw wrapper receipts and audited artifacts are in
P2_app_acceptance_raw/{default,immediate,match}_receipt and corresponding mode
directories. P2_app_acceptance_audit.md explains the reused collector and detailed
source/object/ELF comparisons. All82 source files retain the exact570ef35f source
aggregate. All nineELFs and threepackages match actual wrapper hashes. Default
finalELF remains identical to D098; Immediate changes only package byte14.

MATCH differs only in the three existing enabled MotorGate/native motor-write
function sections; all1435 other allocated object sections/relocations remain.
Startup,493 project function identities,176 imports,39 native exports and42 AEABI
bindings remain intact. No Bridge/RPC singleton roots return. This is compiled
branch inspection, not a physical output trace or permission to execute MATCH.

## Explicit external library experiment

The existing phase-independent fixture was copied into a private temporary
library search directory without installing or editing any library. Exact local
and remote fixture file sets/hashes are checked before and after compilation;
installed pins and nonempty ELF/package hashes are retained.

Fixed0 candidate e6e7e84e7b5a4eeda78c094829685d45/phase0 passed at6172B program,
208B static payload and discovered SumoPolicyFixture1.0.0. Correct ordinary control
c4a32af6b4554bb2aa542bdb695124ca passed at73512B program,29788B static payload and
discovered the same fixture plus the six ordinary Bridge dependencies. The actual
successful envelopes are rejected by the app validator specifically for their
nonempty external-library lists. This demonstrates normal explicit discovery
under the override, not compatibility of arbitrary third-party library behavior.

The initial forced-literal1 control failed; P2_app_library_failure.md records the
root cause and corrected stock-template control. All failed compiler evidence
remains in P2_app_library_raw and the reviewer receipts. The successful fixed0
build was reused, not unnecessarily repeated. The experiment runner and exact
source identities are preserved alongside the receipts.

## Review, adoption and limits

The existing local implementation is unchanged from2ded06a:46 new+78 established
tooling cases and fresh local review already passed. They were not rerun without
new code. Fresh same-model target review is recorded separately in
../reviews/P2_app_acceptance_review.md, including an independent ELF decoder and
actual fixture verification. This is neither cross-model review nor a phase gate.

Compiler low-memory warnings remain. Conditional pristine-loader peaks are
252472B inert and252856B MATCH; largest modeled payloads9668B/9284B. These are
model results, not measured loaded freeRAM/fragmentation/stack or complete800us
WCET. Native dump/local reset/calibration delivery still need app integration and
new final-source memory checks. Last known deployed image remains D0911502e948.
No firmware/config/locked test/inert upload key changed; no MCU or motor operation,
new physical fact, human gate, push or tag. Full P0-P7 remains incomplete.
