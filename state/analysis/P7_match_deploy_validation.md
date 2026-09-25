# D183 precompiled MATCH deployment: HOST-TESTED / REVIEWED

25 September 2026, Dubai. Implements the remaining guarded dynamic/Immediate
deployment software using the existing transport and D182/frozen uploader.
No compiler, native child, board query/upload/reset, real scope, qualification
or motor permission occurred. Positive records were synthetic RAM fixtures.

## Source and independent expectations

Initial implementation396e3359; independent oracle721e090b (63methods) was derived
from the public contract and existing interfaces without reading new source.
First run59PASS/4FAIL is retained9dfb0eb1. Separate reviewer/spec-only author
adjudicated two new fixture assumptions: os.open-only injection missed Path.open,
and the in-process bootstrap fixture omitted required isolation. Corrections
preserve every existing assertion, reach actual framing guards, and add missing
flag/no-resource/no-JSON-reread regressions; corrected oraclec98b1873 has66methods.
No established or locked test changed.

Source69bb9981 fixes three separately reviewed defects: save failure now retains
UNKNOWN/primary error/attached outcome; local binding checks avoid Linux-only
resource imports; policy reads use the already checked JSON snapshots. Existing
frozen modules and actual uploader lifecycle remain unchanged.

Corrected tests pass126methods (66new+60unchanged compiler/parser checks),7.066s
unittest/14.249s WSL wrapper; Windows payload25methods also pass. Those simple
fixtures alone missed realistic command entropy. Additional composition using
current source digest and historical nonrepetitive metadata rejects30303/30289
UTF16 units for ADB/SSH, correctly enforcing30000. Retain6ed1bfd5.

Reviewer-authored source-aware supplemental623150b7 independently reproduces
both refusals (original3aa66688). It is accurately labeled supplemental, not an
independent spec-only oracle. Source8a1c8523 shortens only trusted bootstrap
internal names/diagnostics; the same24 predicates, schema, payload, codec and
limits remain. No protocol/source-pin/permission relaxation.

## Final checks

- Unchanged66 independent methods: PASS/no skips,5.616s unittest/12.509s wrapper,
  output SHA b7c3fb7e50d190d656fcb4176ae5228ad7d5417127ceb6b00786108a04d6687c.
- Windows25payload+1realistic supplemental: PASS/no skips,0.522s unittest,
  output SHA ceb8604903770d6379067d68724e12730a83c3fe1080aabe7ba798d344239db9.
  Measured actual source composition29919ADB/29904SSH units includingNUL.
  Only81/96units remain for this fixture; each real request is independently
  checked and may be explicitly refused. Never increase the limit to force it.
- Comment-only35e86452 adds decoder variable explanations. Complete Python AST
  equals tested8a1c8523, including exact transmitted bootstrap. Tests not repeated
  for comments; raw hash7962e8bd recorded in comment_identity.json.
- Native Windows3.13.11 successfully builds pure binding/policy views without
  resource and reads18 installed pins. Windows and WSL current virtual app source
  digest agrees:37a2099f6938baf6430cfed2b5a002793d9748820fe0876e9cd039fd94330c29.
- Final18task pins checked (explicit comment-only delta),6D182/10D180/24D179pins
  exact; firmware/bench/locked files unchanged fromfddd318d; PROGRESS legacy prefix
  exact. Owned RAM remnants0; actual deployment owner/scope0.
- Initial closing assertion wrongly assumed raw Git/worktree equality for two
  existing newline-normalized files: board_tool.py and app_build_pins.json.
  integrity.json retains the distinction, raw/Git hashes and line-ending mapping.
  Normalized bytes match; no source or old evidence was rewritten.
- final_freeze.json retained a caller source_commit69bb9981 label while its
  actual payload byte pin correctly identifies8a1c8523. integrity.json supplies
  the exact provenance mapping; frozen record unchanged.

Commands/statuses/outputs are in `analysis/P7_match_deploy_raw/` relative to
state. Relevant final commands:

```
wsl -d Ubuntu -- python3 -B -m unittest tests.tooling.test_match_payload tests.tooling.test_match_deploy -v
python -B -m unittest tests.tooling.test_match_payload state.analysis.P7_match_deploy_raw.test_realistic_composition -v
```

Separate fresh-context same-model review76fbc5ef PASS, no open BLOCKER/MAJOR;
see reviews/P7_match_deploy_review.md. Reviewer inspected actual source/diffs/
receipts and authored the labeled supplemental but did not run tests/native
commands. It is not cross-model review or a human phase approval.

## Remaining acceptance

Offline route implementation is complete. Actual deployment remains refused
without a current source-bound checked target build, fresh identity/prerequisites,
same target/runtime/artifact qualification and a current-session identified human
STAND OK/RING OK. A JSON file cannot authenticate physical truth or human authorship.
Current app target compilation, the inert MotorGate fault diagnosis, actual RAM/
stack/WCET, electrical/sensor/motor/ring checks and human phase gates are pending.
No release tag or competition-completion claim is made. The exact hardware resume
task remains in CODEX_HANDOFF.md; there is no background process.
