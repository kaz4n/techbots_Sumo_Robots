# D245 B7 deployment preparation review

Date: 2026-09-27. Reviewer: independent `b7_reviewer` subagent.
Verdict: **PASS_SOURCE_AND_HOST**. No open material finding in this scope.

This review covers only the guarded deployment preparation in
`tools/b7_app_upload.py` and `tools/deploy_b7_app.py`, against
`state/analysis/P2_b7_deploy_contract.md`. The reviewer read source, inherited
guards, the independent oracle and saved evidence; the reviewer executed no
tests, native transport, upload, MCU operation or motor action. The only file
written by this review is this report. The earlier D244 source/host review
`P2_b7_brownout_review.md` remains unchanged at SHA256
`f00d39fea72d8fd6b14f91d732982f9d513ce714a3cfaa647ddd1994401c5a70`.

## Reviewed identity

The new subjects, contract and independently authored oracle were committed at
`98b13db0` before the first run. Saved before/after hashes from both runs equal
the live reviewed files, and the reviewed files have no diff from that commit.

| File | SHA256 |
| --- | --- |
| `tools/b7_app_upload.py` | `567966d5dfcb7abe7ccddbfc8c2d2b2d7f9f84056ea031bb54b94aeca3a17f22` |
| `tools/deploy_b7_app.py` | `81b5585535dc074a2bf0150e7971fee1e3eae3184c2f6ee8771205edd252f95c` |
| `state/analysis/P2_b7_deploy_contract.md` | `b0ae1655ab3402d88cec650c997048e91117e9f77ded776362656d521f00c0dd` |
| `tests/tooling/test_b7_deploy.py` | `0f9edc64b798d105dc23d4c4f384971e07fdb7adc22b5c46e36816304a392b68` |

## Material source checks

- The native adapter differs from the existing commissioning adapter only in
  its three explanatory header lines and the sole allowed profile tuple.
  Exact built-in string `b7_brownout` and exact built-in integer motor value
  0/1 are required. The commissioning owner, static/default upload selection,
  bounded tokens, source/package/export binding, canonical payload, descriptor
  protection, child handling and result checks are preserved.
- The caller reads the exact 32,202-byte D227 caller at SHA256
  `e030c2497605fc77938c70e7cb76e8c29db65322bdb4cba87381a70d2ddcfde4`
  with plain-path, link, descriptor identity and complete hash checks before
  applying count-checked literal substitutions in a new private namespace.
  It does not alter legacy module globals or legacy source files.
- The adapted checked-code closure includes the new caller/adapter/contract,
  pinned B7 compiler, pinned D227 caller, pinned D222 compiler, inherited fixed
  dependencies and actual reviewed Git blobs. Compiler admission separately
  retains the complete source/input closure and exact B7 policy. All eleven
  receipt bindings, one query/one compiler, nine successful closing checks,
  exact flags, artifact metadata, clean reviewed HEAD and source/config/image
  linkage remain required.
- Only B7 maps to `GATE P1 PASS`. M1 qualification requires operation `stand`,
  all enabled grant evidence, opponent/ADC/QTR grants, configured disjoint A1
  windows and all eight physical checks. Fresh exact `STAND OK` is bound to the
  whole request digest under the existing strict one-hour expiry rule.
  `RING OK` is refused. M0 retains absent grants and null qualification and
  authorization; it cannot qualify an operational B7 trial.
- Public facades expose no identified-delivery parameter. The private adapted
  caller explicitly refuses non-null `_delivery` and non-false `identified`.
  Ordinary configuration parsing requires zero identified stream/session
  values. The retained internal delivery helpers therefore add no reachable
  bypass through this route.
- The original lifecycle retains boot/UID/tool and conflict checks, absent
  scratch, exclusive consumed owners, bounded single upload, child reaping,
  before/after observations, independent closing checks and original-error
  precedence. Failure cannot become success through a closing or evidence-write
  failure. No retry, rollback or scratch cleanup was added.

## Saved host evidence

| Evidence owner | Environment | Result | Outer elapsed |
| --- | --- | --- | --- |
| `state/analysis/P2_b7_deploy_raw/host01` | WSL Ubuntu, `python3 -B -m tests.tooling.test_b7_deploy` | 12 methods PASS, exit 0, all four pins stable | 27.114 s |
| `state/analysis/P2_b7_deploy_raw/host02` | Windows Python 3.13, `python.exe -B -m tests.tooling.test_b7_deploy` | 12 methods PASS, exit 0, all four pins stable | 101.156 s |

Both `result.json` records and saved test output were inspected. These were
the first frozen runs on their respective platforms, with no source or fixture
correction. The oracle uses synthetic Git/compiler/qualification records and
refused or controlled fake-board callbacks. It checks exact identities,
private isolation, stand-only authorization/expiry, missing checks/grants,
button overlap, M0 truth, compile semantics, actual Git closure, unavailable
identified configuration, one controlled upload, consumed ownership, timeout,
closing failure and evidence-write failure. Inherited lower-level native
guards are retained by unchanged checked source; these two runs are not
independent real-board executions of those guards.

## Evidence boundary and next action

This pass admits the preparation software for a future qualified scope. It
does not admit a real deployment or supply setup grants, physical acceptance,
a phase gate or fresh motor-run authorization. No real deployment scope,
transport, upload, reset or motor run is established by these host results.
The D244 native compile review is separate. Actual B7 still requires accepted
setup and fresh specific `STAND OK`, a half-charged pack, twenty observed full
forward/reverse cycles, and independent uninterrupted-uptime evidence.
