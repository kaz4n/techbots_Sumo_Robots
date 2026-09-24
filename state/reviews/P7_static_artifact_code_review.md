# D142 static artifact component code review

Date: 2026-09-25. Separate reused-context, same-model Codex reviewer; not a
fresh-context, cross-model or human gate. Scope: pure host structural component,
frozen synthetic tests, bounded private probes and receipt/report consistency.
No implementation/test/contract edits by the reviewer; no board, compiler,
upload/reset or production-policy action.

**Disposition: PASS for the D142 host component; no open BLOCKER, MAJOR or MINOR.**
Two MAJOR cross-form consistency defects were identified before implementation
execution, preserved, fixed, and subsequently reproduced against the original
Git bytes. Neither test assertions nor the accepted contract were weakened.

## Exact identities

| Item | SHA-256 |
|---|---|
| Adopted artifact contract | `b6a18e4d27e500d6306587141cbb27bcd7e546ce9bb507f148f28591634bec54` |
| Frozen parent contract | `d9090cc49a657bdaf08d47def5b9f1fdc8b7da620e19335a0a10b338da32abae` |
| Original parser, preserved in `a986ffdb` | `50d067223087fe8a64fd34378cd4cf255b1d46a654d0c156aa50e86db70ab793` |
| Reviewed final `state/analysis/P7_static_link_probe_raw/static_artifacts.py` | `d30372dd4b8fb8c2661d00affc4a215cc88e3f62511995ff6303827bed4b7368` |
| Original public test freeze | `535f985874ec0cd0395516b7ff73175ce31760928a84b48b950ead890e64bab1` |
| Public consistency supplement freeze | `ba5c6444815e7b7d81ccbbadfb031e8c1dc519deaa51c6c2f256dea2e6239163` |
| Public first-run receipt `P7_static_link_probe_raw/artifacts_first.json` | `ac5602988c92b24dd1bcd4f653c40b8ae0c2db2b17e30af721647c840c0e27bd` |
| Private probe `P7_static_artifact_review_raw/test_artifact_consistency.py` | `2b2e4f4cd0667243d728dfd8a1781e99ad1a049f1dc55ccaec9837b437e750a7` |
| Private freeze `P7_static_artifact_review_raw/freeze_consistency.json` | `250ed35e5b102a10047461f010f08f03f1b4475ebe4845806cb75538b4dbd06f` |

Paths beginning `P7_` in this table are under `state/analysis/`.

## Findings and closure

1. **MAJOR, closed — empty allocation records escaped comparison.** Original
   source lines 214 and 302-304 excluded zero-size allocated sections before
   comparing the three ELF forms. This violated artifact-contract lines 134-137;
   only the returned section report, at lines 44-46, is restricted to nonempty
   allocations. A valid empty `.rodata` could disappear or change address or
   alignment in one form while the original parser returned success. The fix
   normalizes every allocated record; nonempty load mapping and report semantics
   remain unchanged. Private negative controls reproduce nine accepted-invalid
   subcases in the original and reject all nine in the fix.
2. **MAJOR, closed — entry-symbol identity was reduced to its address.** Original
   lines 285-300 validated each entry independently but returned only symbol
   values; line 357 therefore missed differing valid sizes, bindings and
   visibility across forms, contrary to contract lines 159-160. The fix compares
   value, size, type, binding, visibility and semantic section name. It does not
   compare raw section indices, which may legitimately change. Nine private
   one-form mutations reproduce the defect in the original and reject in the
   fix; matching variants and section/symbol-index renumbering pass both.

The inspected repair is limited to these comparisons. Essential copy/zero values,
entry placement, byte mapping, limits and package checks were not relaxed.

## Verification and limits

The independently authored original 39 methods plus separately frozen six-method
supplement passed their first execution on the repaired source: **45/45**, zero
failures/errors, unittest 1.825 seconds, invocation 1.960 seconds. The author did
not read implementation bodies. Both freezes preceded execution; all 11 distinct
public frozen inputs were independently rehashed unchanged during this review.

The reviewer-owned six-method probe was frozen before its execution and binds
the public fixtures/freezes and both source hashes. It is not represented as an
implementation-blind oracle. The original module was read from Git and executed
in memory, without checkout or source overwrite: three negative methods exposed
18 failed subcases, while all three positive methods passed; zero harness errors,
exit 1. The unchanged probe on the fix passed all six methods, exit 0.

Exact retained private evidence:

- `state/analysis/P7_static_artifact_review_raw/original_consistency.json`, SHA-256
  `b5f9204424114419f9bc562410c6062769a56f640fb845b8d4571ea5fd0b741b`, and
  `original_consistency.txt`, SHA-256
  `1ca714e1dee32051f3baa5b7891625e24f17bfbc317fb491ef0fca4352b25f95`.
- `state/analysis/P7_static_artifact_review_raw/fixed_consistency.json`, SHA-256
  `84a89281fd142a013f571ffd59698243ed0b16d0bdf36e30b4631183a08b2759`, and
  `fixed_consistency.txt`, SHA-256
  `6b40e4655c1ade71c75cc1cca63826e5c52360519f609f594186ed530abba77d`.

Code inspection and public controls cover strict seven-input admission,
bounded/overlap-safe ELF tables and sections, symbol encoding/partition/index
rules, named allocations, LOAD permissions/coverage/physical extents, distinct
VMA/LMA, exact BIN gaps/content, BSS reservation versus clearing, both package
pairs, no input mutation and forbidden-effect tripwires. AST inspection confirms
24 functions, maximum 31 lines. The module imports only `hashlib` and `struct`.

Production `tools/app_build_policy.py`, `app_build_commands.json` and
`app_build_pins.json` remain at `d5a4ce59`, `63f6c41e` and `55720e65`; the D141
static policy and reference remain at `ec3d8a5e` and `1dc8ac6d`. No production
static admission path was added. The root-owned validation report was read for
claim consistency; no material mismatch was found in its pending-review draft.

This establishes synthetic host structure/package validation only. Exact ABI
flags remain a derived admission expectation. Source/run freshness, map and
instruction review, constructor/static-thread order, native/wrapper/heap and
strong-main bindings, ABI layouts, the full runner, query/compiler authorization,
real static fit and runtime qualification remain separate parent obligations.
`STATIC_LAYOUT_PACKAGE_PASS` does not imply `STATIC_ARTIFACT_PROBE_PASS`, resolve
D139's 592-byte dynamic deficit, or pass any physical/human gate.
