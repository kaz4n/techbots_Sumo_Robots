# D-074 local CSV evidence validation - 2026-09-23

IMPLEMENTED / HOST-TESTED / SCRIPT-TESTED / REVIEWED within the selected offline
B8 scope. Contract5e25917 preceded independent source and test work. The project,
runtime recorder and original human/physical gates remain incomplete.

## Delivered behavior

tools/validate_csv_bundle.py reads three local D-073 CSV files and an optional
caller-declared manifest. It checks exact schemas, numeric widths, raw-byte
agreement, bounded regular-file snapshots, retained counts, lifetime status counts
and loss consistency. Report sections distinguish format integrity, contradictory
owner metadata, reported loss, lifecycle and supplied provenance. It accepts
arbitrary ordinals, unknown raw codes and timestamp wrap without rewriting data.
Input bytes remain the detailed evidence; the JSON report contains summaries.

No board tools, network/process APIs, firmware/config reads or file writes.
All common-attempt, transport and hardware-verification flags remain false.
Declared hashes cannot authenticate a source/session. Absent metadata remains
unknown, and sealed/clean metadata does not establish physical completion or IDLE.
CLI and exact manifest schema are documented in tools/README.md and the contract.

## Actual checks and independence

- Independent test author read frozen contracts/public headers/prior tests only,
  never Python or C++ implementation bodies.38 methods plus table-driven cases
  exercise schemas, each wire range/raw offset, arbitrary codes/ordinals, every
  loss field/phase, overwritten/saturated lifetime counters, all nullable manifest
  fields, duplicate keys/types/hashes/rows/capacities, bounded/changed files,
  symlinks/network prefixes, CLI exits, quiet import and no writes.
- First run38 methods exit1: a reviewer-discovered mixed Windows UNC prefix
  caused two failure reports in one guarded test. Full original module/hash and
  red receipt retained. First repair rejects all two-separator combinations
  before filesystem lookup. No test predicates changed; retry38PASS2.890s.
- Separate fresh same-model read-only reviewer reproduced38PASS2.584s, no skips;
  closed the MAJOR and a README wording MINOR. Final verdict PASS/no open findings.
- Full relevant tooling378PASS169.749s, exit0, no skips. This includes the actual
  public C++ formatter compiled and exercised on host, then validated by this
  tool against independently expected bytes. The unchanged993-case C++ suites
  were not rerun redundantly; their previous normal/sanitizer receipts remain.
- Synthetic25Hz200-second fixture has5001frames and4096events. It tests local
  validation only, not physical acquisition, RAM fit, transport or no-gap delivery.
- Two native Windows Python3.13.11 CLI calls pass: no manifest -> ABSENT;
  explicit synthetic partial metadata -> PARTIAL_DECLARATION/SYNTHETIC. Empty
  owner remains EMPTY/NONE_REPORTED, all physical flags false, input hashes
  unchanged. WSL tests use Python3.12.3 and g++13.3.0; exact version receipts kept.

All46 protected source/locked/inert-manifest paths remain byte-identical. No
firmware/config/CMake/existing test or upload guard change. Final validator SHA:
1c4781fdd0f77a610998644db610bf6adf5a2373d4f32f3ec7ca486185ff52f2;
independent test SHA56d580f8a462abe24989c058877e0f59d03f5096860eff434e5dd0451813a0ac.
All27 module functions remain under60 lines. Raw receipts and pre-fix source
are byte-preserved in P2_csv_bundle_validation_raw/ with SHA256.json; review is
state/reviews/P2_csv_bundle_codex.md. No board connection/compile/upload/reset or
MCU/peripheral/motor operation occurred. No new target-size or timing result.

## Remaining project scope

This is a local validator, not tools/dump_match.sh. Actual B8 still requires
runtime recording, measured free RAM, real200-second data and live IDLE-safe
transport with no gaps. D-068/D-074 exclude runtime integration, and P2 integration
requires the still-absent human GATE P1 PASS. P0 optical/cold-start/electrical/
PINMAP and P1 EXPLAINED/gate records remain absent. See
P2_offline_scope_completion_audit.md and the existing P0/P1 gate packets.
No additional metadata infrastructure is needed to finish this selected scope.
