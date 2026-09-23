# D093 independent test-author handoff

2026-09-23. Objective: test the frozen D093 input owner using contract/public
headers and existing independent fixtures, without inspecting production bodies.
All author work is new tests or evidence. No existing assertion, production file,
configuration, shared build directory, ledger, commit or hardware was changed.

## Final results

| Surface | Result |
|---|---|
| Host owner and actual Robot/MotorGate, MOTORS_ALLOWED=0 | 24 cases / 2421 assertions PASS |
| Same host cases, MOTORS_ALLOWED=1 | 24 cases / 2421 assertions PASS |
| Actual native Reader + readerInputPort + owner | 5 cases PASS; 24 parent process-isolation assertions |
| Seeded counter saturation and A1 sequence wrap | 2 cases / 30 assertions PASS |
| Configuration variants | 11 invalid variants, 5 assertions each; 4 valid boundary variants, 2 each; all PASS |
| Actual inert probe startup and 10000 loops, both macro modes | 1 case / 14 assertions per mode PASS |
| Additive configuration registry | All 18 established configuration checks PASS through the unchanged D090 wrapper |
| Controlled compile-only upload refusal | All 8 transport/match/startup combinations refuse before target, remote or transport calls |

The seven Python methods all have passing executions. The initial aggregate had
six passing methods and a host compile failure. After the fixture corrections,
the host method passed independently in both modes. No production failure was
found. All C++ executions used UBSan with no recovery and strict warnings as errors.
Native child assertions are enforced by the established isolation listener; the
reported 24 parent assertions must not be called a total of child assertions.

## Reproduction and receipts

PowerShell commands, with no board access:

```
wsl.exe -d Ubuntu --cd /mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots -- python3 -m unittest tests.tooling.test_power_inputs -v
wsl.exe -d Ubuntu --cd /mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots -- python3 -m unittest tests.tooling.test_power_inputs.PowerInputsTests.test_host_owner_contract_both_motor_settings -v
```

`commands.jsonl` preserves every compiler/executable argv, exit code, complete
stdout/stderr and opaque staged production/config hashes. Builds were isolated in
`/tmp/sumox_d093_author_*`. `registry.jsonl` and `upload_refusals.jsonl` retain the
noncompiler checks. `final_sha256.json` identifies final new tests and the tested
contract/header/production/config versions.

Two authoring failures are retained:

1. Missing `<initializer_list>` in the new fake fixture prevented the host test
   from compiling. Adding that direct include fixed the harness; native/config/
   probe tests were already passing.
2. Three `CHECK_FALSE(conditional ? callA : callB)` expressions were decomposed
   incorrectly by doctest, producing 40 assertion failures even though every
   accompanying fault/diagnostic assertion passed. Saving the conditional result
   in a local bool before checking it preserves the expected false value and
   fixes the test expression. The rerun passed all 2421 assertions in both modes.

## Coverage and boundaries

Host tests cover inert lifecycle, copied ports, null context and missing callbacks,
setup shapes and priority, clock equality/wrap/half range, first due and refusal,
9999/10000/10001 scheduling, strict19999/20000/20001 age, exact native float scaling,
raw endpoints and malformed fields, 0/99/100/101 intervals, call-bracket failures,
same-time genuine A1 reads, old A0 replay, identical new A0 bytes after observed
full wraps, saturating age, all fourteen known native error codes, shared first
fault preservation and callback suppression, projection isolation, explicit
invalid buttons, unchanged analytic held-input filtering/caps/slew, and actual
Robot/MotorGate inhibition plus persistent Robot faults after fresh replacement.

Native tests use actual unmodified `power.cpp`, actual native owner binding and
actual owner against the existing installed-shaped deterministic fixture. They
cover pair setup, channel switching, raw identity, source times, shared native
faults, shutdown diagnostics and 100 acquisition/projection iterations without
allocation. Fresh boots remain separate processes. Counter/sequence tests use
only a dedicated test translation unit's approved private-state seam, explicitly
seeded near the limit; these are not billions of observed conversions.

Probe startup links actual native ADC/owner/core/Gate/recorder code. Its UnoQ motor
port is a counted public-callback substitute so any startup motor operation is
observable without mixing two native register fixtures. Real native motor backend
qualification remains with its established tests and root's target inspection.
The retained exercise is never invoked by this probe-startup test.

These synthetic calls prove software accounting and guarded composition. They
do not measure physical generation, analog accuracy, settling, clock calibration,
WCET, scheduler grants or motor behavior. The uint32 observation-gap precondition
and trusted-native-callback assumption remain explicit. Root owns full host/ASan,
actual target compile-only evidence and the separate fresh review. Tests frozen;
no further author changes planned.
