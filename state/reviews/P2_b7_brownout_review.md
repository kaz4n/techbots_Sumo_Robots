# D244 independent B7 source and host review

27 September 2026. **PASS_SOURCE_HOST_AND_COMPILE_TOOLING** within the scope
below. No open material source or host-contract finding remains. Target
compilation and all physical B7 acceptance remain pending and require separate
evidence; this is not a phase gate or authorization to upload/run motors.

## Independence and reviewed identities

The reviewer read the frozen contract/API, inspected production and tooling
sources, adjudicated the original oracle failures against public fixture
semantics, and inspected the saved raw runs. The reviewer did not implement or
edit firmware, tooling or tests, execute tests, contact the board, or perform
native actions. This report is the reviewer's only file change.

- Policy approval: D244, recorded at `fc0434fa`.
- Frozen behavior/API: `2802eed3`,
  `state/analysis/P2_b7_brownout_contract.md` and
  `src/core/brownout_sequence.h` (API SHA256
  `ff16d6a4fab0dcc19fbe16068d347d96a60947a96d3776b142655c68705a89f7`).
- Firmware implementation: `1ba538e1`. The current `src/` and bench sources
  have no diff from this implementation commit.
- Fixture corrections: `fefe1088` and `dcb17b25`; these alter no firmware.
- Compile-only tooling/build contract: `96a19c1d`; strengthened independent
  tooling oracle: `4a367f2b`.

## Source conclusions

The B7 profile defaults off and excludes MATCH and every existing alternate
profile. Its actual Robot route retains initialization, source admission,
qualified START release/countdown, one Governor pass and sole MotorGate writes.
The new electrical profile uses scale 1 only for B7; ordinary B6 compensation,
finite battery checks, slew, brake/inhibit and sign-zero reversal remain intact.
MotorGate's exception checks active B7 phase, consumed/started state, leg/count
coherence, direction, matching full endpoints and absence of stopping/edge
interruption. Ordinary centered-contact full-duty eligibility remains unchanged.

Previous receipts are staged by `receiveBrownout` and consumed only after
current lifecycle/source/fault/edge arbitration. Pending phase and leg metadata
prevent reassignment across a leg change. The helper requires exact enabled
endpoints on both sides, a strictly pre-deadline first endpoint, bounded ordered
decision/application gaps and a continuous 500 ms acknowledged dwell. Duplicate
decisions are passive; replayed tokens on new decisions fail. Loss during dwell
terminates without restarting. Forty completed dwells produce twenty pairs;
M0 feedback never receives endpoint credit and times out.

STOP/fault preempts sequence progress. Edge interruption preserves normal R5
escape/caps and prevents any stress-sequence continuation; successful escape
exit inhibits and requests terminal STOP. Completion inhibits immediately and
requests lifecycle STOP on the next distinct tick. Public Robot reset preserves
tokens/evidence, consumes a not-yet-terminal instance and requests STOP without
claiming immediate hardware I/O. Runtime/Transaction service-reset routes refuse
B7. The new native wrapper retains M0 and empty setup grants.

The three new compiler tools retain a checked private D222 caller, fresh
per-selection module state, exact B7-only grammar/flags, dependency byte pins,
source/HEAD admission, exclusive owners, jobs 1 and inherited closing checks.
They add no upload, reset, remote motion, setup grant or deployment acceptance.
The installed D222 bootstrap and new policy bytes match their literal size/hash
pins. Local policy and remote artifact adapter select the same B7 flags.

## Saved evidence independently inspected

All C++ selections below use strict C++17 warnings and UBSan. These are host
callbacks and synthetic source fixtures, not physical measurements.

| Selection | Passed cases | Passed assertions | Saved output |
|---|---:|---:|---|
| B7 M0 default | 24 | 25,840 | `../analysis/P2_b7_brownout_raw/host02/02.stdout` |
| B7 M0 synthetic A1 windows | 25 | 41,249 | `../analysis/P2_b7_brownout_raw/host02/04.stdout` |
| B7 M1 default | 24 | 369,633 | `../analysis/P2_b7_brownout_raw/host03/02.stdout` |
| B7 M1 synthetic A1 windows | 25 | 385,042 | `../analysis/P2_b7_brownout_raw/host03/04.stdout` |
| Ordinary M0 safety/governor | 205 | 9,278,871 | `../analysis/P2_b7_brownout_raw/host03/06.stdout` |
| Ordinary M1 safety/governor | 205 | 9,082,491 | `../analysis/P2_b7_brownout_raw/host03/08.stdout` |

Host03 records PASS_HOST_ONLY. All 30 command exit codes match their expected
success/rejection, including exclusive-profile and nonboolean/default checks.
Every current `src/` hash was independently compared with both host03 pin sets;
there were no differences. `git diff 2802eed3 -- tests/locked` is empty. Saved
host02/host03 receipts confirm removal of their owned temporary build scratch.

`../analysis/P2_b7_build_raw/host02` records seven successful tooling methods,
exit 0, stable before/after tool/oracle pins and accepted=true. Reviewed cases
cover exact argument/type/profile refusal, isolated M0/M1 state, unchanged
inherited pins, metadata/ELF/TLS/export validation, changed-bundle rejection,
read-only/exclusive admission and one-query/one-compile/nine-closing behavior.
This is controlled host evidence; no target compiler result is claimed here.

The additive `tests/tooling/test_b7_config_registry.py` supplies the approved
D243 window and five D244 literals through the existing registry. Its saved
`../analysis/P2_b7_brownout_raw/config01/registry_cases.jsonl` includes a successful
current-six registry path and an expected wrong-eight failure at the original
literal-value assertion. All eighteen legacy config assertions remain present;
the declaration-set check is unchanged.

## Findings and failure disposition

1. The first endpoint-loss fixture disabled a receipt while leaving nonzero
   duties. APPLICATION refusal was correct for this invalid receipt. The
   corrected fixture uses disabled/zero for ENDPOINT_LOST and adds a separate
   disabled/nonzero APPLICATION negative case. No receipt validation was relaxed.
2. Two slew fixtures incorrectly initialized their baseline to zero after the
   actual GO tick had already requested .02. The correction checks the GO request
   explicitly and uses it as the next baseline. Every later slew, reversal,
   dwell and cycle assertion is retained. M0's expected timeout row is checked
   as STOPPED/zero rather than incorrectly requiring OPENER.
3. The build contract initially claimed every artifact reply carried HEAD.
   Its corrected wording accurately places HEAD in the checked parent input/
   check/outcome envelopes and binds the inherited artifact reply through that
   parent identity. No artifact validation was removed.
4. The existing config registry lacked the new B7 literals and the already
   approved D243 window. The additive wrapper closes that integration gap without
   editing or weakening inherited assertions.

Firmware host01 and host02 remain FAILED overall in their original evidence.
The two successful M0 executions within host02 are accepted separately; the
subsequent amendment concerns only a test that immediately returns under M0.
Host03 reruns M1 and the pending ordinary/profile checks. Tool host01 is excluded
from stable-source acceptance because its oracle changed during that run;
tool host02 supplies the stable replacement. None of these failures required a
firmware change, and no failed run has been relabeled PASS.

## Limits and next action

`../analysis/P2_b7_brownout_validation.md` agrees with the inspected counts,
failure dispositions and scope. Its source-continuity statement refers to
firmware source: oracle bytes intentionally changed in the documented repairs.

Next, perform the separately admitted compile-only B7 M0/M1 and ordinary
production checks against a clean reviewed source, then review the actual saved
target artifacts separately. Do not infer deployment permission from compilation.
Physical B7 still needs actual verified setup, a half-charged assembled robot,
fresh specific STAND OK, observed direction and continuous observer-owned
uptime/boot evidence through final stop. A volatile report or acknowledged PWM
receipt proves neither continuous EN-high nor absence of an earlier reset.
No waveform, wheel motion, power, live RAM, WCET, physical acceptance or human
phase gate is established by this review.
