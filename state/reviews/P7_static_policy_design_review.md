<!-- Reviews the D141 fixed policy interfaces and source-derived reference data. -->
<!-- Separates host-policy authority from the pending static artifact experiment. -->
<!-- Verified by independent local expansion, exact-byte hashing and retained receipts. -->
# D141 policy design and reference review

2026-09-25 Asia/Dubai. Separate fresh-context same-model reviewer. **PASS within
the policy-design/reference scope; no open BLOCKER, MAJOR or MINOR.** No policy
implementation or independent test suite was read or executed for this review.
The earlier draft-contract review remains unchanged.

## Exact reviewed identities

| Repository-relative path | SHA-256 |
|---|---|
| `state/analysis/P7_static_link_probe_contract.md` | `d9090cc49a657bdaf08d47def5b9f1fdc8b7da620e19335a0a10b338da32abae` |
| `state/analysis/P7_static_link_probe_raw/static_reference.json` | `1dc8ac6dec8534536acfcc4da73516416ea465cfcc1a349900fd13e210144a2b` |
| `state/analysis/P7_static_link_probe_raw/additional_pins.json` | `d8dc249656cef0a852af8385d59fbdd3e9e30ace2dcb113921bf7964483fe924` |
| `state/analysis/P7_static_link_probe_raw/references_note.md` | `667cb43ea6133028498518910d69f45ec56298c7f7c062dc9432238b2ac698fa` |
| `tools/app_build_policy.py` | `d5a4ce59870574ac601c3d8837b472adf7eec81e86982794fa16a7b3b354a7c6` |
| `tools/app_build_commands.json` | `63f6c41e34bae9fce1d945c3271b3fe86343f27544affe25ae14788438d62e1d` |
| `tools/app_build_pins.json` | `55720e65b03f6cd28964c675ceeec76619824cd11525549fbac0503b8efa972b` |

## Independent derivation checks

- Expanded all 84 properties independently from retained pinned
  `P2_bridge_dependency_raw/installed/core/platform.txt` and `boards.txt`, using
  D139's captured property context for environmental values and literal
  static/M0/wait selection. All 84 strings match byte-for-byte; their key set is
  identical to the production controlled-key set. Exactly 14 values change from
  the dynamic reference after fixing its safety/startup tokens. The inactive
  `build.check_command-dynamic` correctly inherits the selected static wraps.
- Only `@DATA_DIR@` and `@BUILD_PATH@` remain as variable reference tokens.
  Existing brace placeholders, quoting and whitespace remain exact. Source
  platform/board bytes independently match their existing production pins.
- All eight additional paths are disjoint from the 18 existing production pins.
  The six build dependencies and GDB match D140 closing hashes. The readelf pin
  matches the retained exit-zero identity and later fixture receipt, and a fresh
  hash of the local retained `fixture_tools/readelf.bin` independently matches
  `c37462dcd380ae1039eb8a0aab379a619415e1100472291ffea2eae34161092e`.
  These are historical/retained identities, not fresh installed-board checks.
- All 14 input hashes in the finalized preparation note match current local
  bytes. One MINOR synchronization issue was closed before this disposition:
  the note initially named an earlier contract hash; its final version binds the
  current SHA-guard/upload-extension contract. The reference and pin maps did
  not change during that documentation correction.

## Interface and authority boundary

The two fixed public validators return the full validated property mapping and
raise `ValueError` for invalid input. Fixed app/static/M0/wait identity,
`upload.extension=bin-zsk.bin`, existing empty overrides, complete controlled-key
equality, canonical data/build paths and the literal reference-byte SHA guard
are coherent with the source-derived reference. Compile-library rejection is
separate from properties-only preflight. The interface has no transport,
subprocess, network or write effects and no caller-controlled profile option.

D141 adopts only this pure policy implementation and host tests after the
independent oracle freezes. Exact implementation review and first host-test
evidence remain pending. Production admission stays dynamic-only. This review
does not authorize artifact/runner implementation, a properties query, native
compiler, upload/reset, runtime measurement or a phase gate.

The note's proposed `e_flags=0x05000400` is explicitly derived from the pinned
executable loader and hard-float selection, not an observed static app. It and
the exact named-section/placement acceptance still require separate artifact
scope adoption, independent fixtures and review. A policy pass cannot produce
`STATIC_ARTIFACT_PROBE_PASS`; D139's 592-byte dynamic deficit remains unresolved.

Only this new review file was written by the reviewer. All checks used local
reads and in-memory source expansion/hashing; no implementation/test execution,
board command, native tool query, build, download or cleanup occurred.
