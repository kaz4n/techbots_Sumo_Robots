# D234 application session forwarding review

FINAL PASS for the scoped source change and saved host evidence. No open
material finding. Reviewed 2026-09-27 in the isolated app-session worktree.
The reviewer changed only this report and performed no tests or native action.

## Frozen scope

The contract is 1308 bytes / SHA-256
`fb9e68f053055578a6e7f66a921006be95c4ca185047734cf532688f9914a3e5`.
Validation is 2371 bytes /
`90219173b49bb284ea199d174f093d18d20413d9114258f2c523081b07101c79`.
The 8035-byte closure01.json is
`4aee26bc9c46c1349e145bf6a1ed3f62a0844948382e7fa91dec484bbb394bc2`;
all44 source, test, contract and receipt pins independently rehash exactly.

| Production file | Bytes | SHA-256 |
| --- | ---: | --- |
| `src/config.h` | 23335 | `de15b427732949adebb1a8450e2ec03bfa325a6bf925d8e09b5d593c15c5600e` |
| `src/app/configured_setup.h` | 2111 | `da0c65a75fe18308a55adf78649a1bad459fc2bf9a47bd082d49ee50ff598d8b` |
| `src/app/runtime_dump.cpp` | 2798 | `8bf657d0fb8450c7da181f5cadc9bd1b3a4f7b18166d0f6917a0bd8ac6abff7c` |
| `tools/deploy_commissioning_app.py` | 29175 | `9c88ecb293237918ed01fbda17e12dadc82db5df5cdfeb10fea16109e7989a10` |

## Source findings

The new receive-stream declaration is uint32, checked against the two declared
enum values before casting. The session declaration remains uint64 throughout
configuredSetupGrants, the copied Runtime grants and each dump Context.
Both defaults are zero. Runtime.begin already copies the grants; subsequent
caller mutation cannot alter the active Runtime identity. Existing Transfer
identity freezing/session-change handling and zero-session token fallback are
unchanged. No setup ownership grant, ready-pin rule, local service/IDLE gate,
MotorGate action, packet format or native HAL behavior changed.

The commissioning parser now protects both names from conditional declarations,
preprocessor use and source define/undef overrides. It requires one exact
uint32 stream literal and one exact uint64 session literal, preserves the
existing comment/string and unsupported-expression checks, and requires both
values to equal zero before continuing admission. Consequently neither a
nondefault stream nor a nonzero fixed session can be deployed through this
existing workflow. Existing source/Git/artifact, physical qualification and
specific motor-run authorization checks remain intact.

## Host evidence

Inspected the changed fixtures and the real host runner, not only the summary.
Seven selected configuration/entry methods cover real constexpr defaults and
mapping across build flags, stream/session combinations through UINT64_MAX,
exact uint64 type, and undefined stream values2/255/256/4294967295. Entry
fixtures explicitly model the two added SetupGrant fields; real Runtime
coverage supplies the separate integration evidence.

The new Runtime case passes sessions1, 2^32 and UINT64_MAX through begin into
the real dump service. It verifies every emitted envelope's identity, terminal
session, no cancellation, stored-grant immutability and motor inhibition.
The existing legacy scenarios remain. Saved UBSan builds cover default M0 and
configured M0/M1:5+22+22 cases and166+6196+6196 assertions, totaling49/12558.
All six compiler/execution receipts return zero with empty stderr. M1 here is
only a synthetic host model, never native firmware or motor permission.

Linux host02 passes28 Python methods (seven configuration/entry plus all21
deployment methods), with zero failures/errors/skips. Registry02 adds one
passing wrapper method that invokes all18 legacy checks and the expected
wrong-value refusal. Its fixture additions use the existing accepted motor
observation10000/10000000 constants and D229800us range; production values and
legacy assertions were not changed. Exact session type/default assertions
remain in the configuration tests.

Windows01 contains19 passing deployment methods and two unchanged metadata
guard refusals in temporary synthetic files. Windows02 repeats only those two
fixtures unchanged and both pass, giving21 unique passing Windows methods.
The new nondefault identity/preprocessor refusal method passes. No guard was
relaxed. Original Windows refusals, the host01 missing sparse tracked-fixture
dependency error, and registry01 missing fixture constants remain preserved.
The original metadata refusals do not themselves establish a production bug
or a particular host-filesystem cause.

Acceptance is source and host only. A configured fixed session is not a fresh
epoch across resets and does not prove physical origin or UART delivery.
Nondefault deployment stays refused pending its separate qualified receive
workflow. Native target compilation/delivery, hardware acceptance, human
phase gates and specific motor-run permission remain unprovided by D234.
