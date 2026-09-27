# D244 B7 source and host validation

27 September 2026, Dubai. **PASS within the software and host scopes below.**
Actual B7 acceptance still requires the half-charged assembled robot, fresh
specific STAND OK, twenty forward/reverse cycles and independent continuous
uptime evidence. No motor-capable image was uploaded or run for these checks.

The human-approved policy is D244. Its frozen contract/API is commit2802eed3;
implementation1ba538e1 remains unchanged through these runs. The dedicated
profile defaults off, conflicts with MATCH and every other bench profile, and
uses genuine Robot/Governor/MotorGate feedback. It counts forty full-electrical
endpoint dwells and permanently stops on completion/interruption. Production
R6 remains unchanged. All five new constants are diagnostic selections, not
physical tuning. The bench wrapper retains absent setup grants and M0.

## Focused strict C++17 and UBSan results

| Selection | Cases | Assertions | Original raw output |
|---|---:|---:|---|
| B7 M0, default setup | 24 | 25,840 | P2_b7_brownout_raw/host02/02.stdout |
| B7 M0, synthetic A1 windows | 25 | 41,249 | P2_b7_brownout_raw/host02/04.stdout |
| B7 M1, default setup | 24 | 369,633 | P2_b7_brownout_raw/host03/02.stdout |
| B7 M1, synthetic A1 windows | 25 | 385,042 | P2_b7_brownout_raw/host03/04.stdout |
| Ordinary M0 safety/governor | 205 | 9,278,871 | P2_b7_brownout_raw/host03/06.stdout |
| Ordinary M1 safety/governor | 205 | 9,082,491 | P2_b7_brownout_raw/host03/08.stdout |

All listed executions passed. Source provenance is in each run's result.json;
host03 also closes its before/after input identities. Source bytes stayed equal
across all three runs. No existing locked test changed. Synthetic A1 windows
exist only in copied host source and establish no real electrical fact.

Coverage includes full countdown, real forty-dwell/twenty-cycle histories,
low/high battery full electrical endpoints, slew and sign-zero reversal,
strict reach deadlines and delayed receipts, continuous dwell/gap bounds,
wrap/duplicate/backwards clocks, receipt ownership, M0 timeout without credit,
same-observation STOP/edge/source/receipt precedence over final completion,
immutable terminal evidence, public reset consumption and both service-reset
refusals. Actual Transaction and Runtime composition and absent setup grants are
covered. Host03 also admits each ordinary profile independently and rejects its
B7 combination, rejects nonboolean B7 values, and proves default B7=0.

## Preserved failures and independent adjudication

The independent oracle froze before implementation execution. Original host01
is FAILED: a disabled receipt incorrectly retained nonzero duties, and the ramp
fixture treated the first post-GO output as the first output. The reviewer
confirmed valid disabled/zero receipts are endpoint loss, malformed disabled/
nonzero is APPLICATION, and GO already issues the first legal .02 duty step.
Commitfefe1088 corrects fixtures and adds a malformed-receipt case; it also
checks the M0 timeout row as STOPPED/zero instead of active OPENER.

Host02 is also retained as FAILED overall: its two M0 executions above passed,
while the full-cycle M1 test repeated the same initial-output mistake. Reviewer
adjudication authorized commitdcb17b25: check the GO output explicitly and use
it as the next slew baseline. Every reversal/count/dwell assertion is retained.
That case immediately returns in M0, so only M1 and pending ordinary/profile
checks were rerun in host03. No failed run is relabeled PASS and no firmware
change was needed to satisfy the oracle.

## Build tooling and configuration

New compile-only tools are committed at96a19c1d; their independent strengthened
oracle is4a367f2b. P2_b7_build_raw/host02 passes all seven methods with stable
source/test hashes: exact grammar/types/flags, isolated M0/M1 modules, unchanged
D222 pins, metadata and full ELF/TLS/export checks, bundle tamper refusal,
exclusive/read-only admission, and one-query/one-compile/nine-closing lifecycle.
Host01's seven methods passed but an overlapping test-only strengthening changed
its oracle hash; it is retained and excluded from stable-source acceptance.

test_b7_config_registry supplies literal approved D243 window and D244 constants
through the existing registry. Its two cases retain all eighteen legacy checks
and reject the historical wrong UART width. Both pass; raw nested receipts are
P2_b7_brownout_raw/config01/registry_cases.jsonl. No declaration-set assertion
or accepted configuration value was weakened.

Current target compilation follows separately in
P2_b7_brownout_actual_validation.md. Host receipt acknowledgements do not prove
waveforms, continuous EN, physical power/direction, uptime, live RAM or WCET.
