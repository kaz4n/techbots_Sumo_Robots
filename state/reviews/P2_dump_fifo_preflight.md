# D117 native FIFO preflight

2026-09-24. **PASS_FOR_NARROW_SOFTWARE_ADOPTION_AND_INDEPENDENT_TEST_AUTHORING**.
No material contract contradiction or missing public decision found. This is a
reused separate same-model source-aware review, not implementation acceptance,
cross-model review, a human gate or permission for a hardware run.

Reviewed final draft `state/analysis/P2_dump_fifo_contract.md` SHA256
`00a6c36c92c6b9f9eb5fd4b453de1ebe9a9e3a58fc28ab1907ca8328550f11f8`.
The earlier30e9b3d6 draft is superseded only by its accurate strong loop-hook /
potentially weak inherited empty initVariant wording. Supporting preflights:

- `P2_dump_fifo_source_preflight.md`:
  `f62f14e45b376d2c431f606d501bd28450d8670e51533a06fc8a2708cf6eca51`.
- `P2_dump_fifo_test_preflight.md`:
  `6aac9c4bea8f2cb78c638437fbf95391534180cdda733a8f1b892eb8a44c69b4`.

The current native header and implementation remain the pinned D090 baselines
`b7c654a990cd08ca7460fca6f472567e37a6ae0d90bc3ec1cb15fccf11c7f28e` and
`6dfaca493024d49d67497f2708ffb51e848447148423b82b4bbb3c10c250d2f3`.
No proposed production file is modified at this preflight. The reviewer read
these sources, the existing factory/caller interfaces, actual CSV formatter and
cached pinned register documentation. Only this review file was written.

## Compatibility and scope

The exact four-file scope is sufficient: the native header/implementation and the
two existing app/recorder sketches. Passive constructor-selected Buffering keeps
the existing begin/ready/port signatures, four setup predicates, factory symbol
definitions and runtime callback identities intact. It requires no new adapter,
translation unit, owner, config or service loop. Both sketches retain their
existing false/empty grants and disabled defaults. Selecting FIFO8 does not claim
physical UART ownership, receiver attachment or clean framing.

The const mode member intentionally deletes implicit assignment while retaining
copy/move construction. The inspected callers do not assign native owners or
depend on private layout. This is compatibility with the current repository,
not a promise of universal type-trait or ABI compatibility. The exact new size,
offsets and BSS still need target measurement. Existing pinned capture tools must
remain tied to their old exact artifacts rather than being silently repointed.

Default LEGACY_SINGLE must retain the old native expectations, including rejection
of installed fifo_enable metadata. New invalid-enum priority applies only before
the first existing grant check; reentry still follows old poison behavior. The
contract accurately separates pre-init DEVICE failures from the old post-init
combined OWNERSHIP gate at native lines157-161. No global status reclassification
or new AUTOCR requirement is imposed on legacy mode.

## Setup, cleanup and live ownership

The three FIFO setup writes are explicit and finite:0, TE|FIFOEN, UE|TE|FIFOEN,
each with DMB and immediate exact verification. Separate read-only ownership
observations are permitted without weakening that sequence. Current non-mode
identity/context/device/pad/IRQ/clock/baud/register facts must be established
before each mutation. No TDR write, ACK wait loop, retry or new timeout is added.
Missing immediate final TEACK may refuse otherwise supported hardware; this
conservative reliability limit is stated rather than hidden.

The setup-only cleanup exception is narrow enough: after a mutation, exactly one
disable/readback is required when all owned facts and the exact last verified or
just-attempted CR1 state remain recognizable. Omitting TEACK/initialized from
that setup predicate permits inhibition after an ACK failure. It does not permit
arbitrary CR1 subsets or foreign register writes. Cleanup readback failure stays
unverified, preserves the original failed-begin reason and cannot retry. Poison,
local buffer clearing and PRIMASK restoration are mandatory. Runtime abort keeps
its original strict live-ownership predicate and receives no setup exception.

The selected new-guard priority and immediate readback-failure priority are
observable without private state access. Existing earlier and legacy gates keep
their order. The first failed-begin return and immediately queried status agree;
later public calls may legitimately expose legacy poison semantics. This avoids
an impossible demand that status remain immutable across all subsequent calls.

AUTOCR==0 is required only for FIFO setup/live owned operation and cleanup
admission; the owner never repairs it. Cached RM0456 p2892 explicitly allows TC
with queued FIFO bytes when a smaller nonzero TDN is reached. Excluding all
AUTOCR autonomous/TDN configuration therefore supports the intended TC meaning.
TXFNF merely admits a TDR store; actual TC still controls payload acknowledgement.
The8-store/80us/100ms caps, packet identity, PENDING0, ERROR0, Transfer300s/2s limits
and one-step-per-decision cadence remain unchanged.

Pinned LL header SHA256
`6ef9bf504ddd453112b69b977fe3d6b0ae7e5be4638219e5f30a60e85cbc6247`
supports UE/FIFO control and puts TDN in AUTOCR. Device header
`8b66d5b9d1514f3ce0950b7a96402e7c026a0779e1cc36c3771be05432b68c06`
defines FIFOEN bit29, TXE/TXFNF bit7 aliases and AUTOCR TDN/TRIGEN fields.
Rehashed cached p2892 is
`a64b2691363c9b2bd6da2d66d6e6f3aaba110d88f71c593872ed0a7d7cff4309`.
RM p2876 requires32-bit register accesses; p2882/LL describe immediate operation
discard on UE0. Neither constitutes recovery of bytes already transmitted or of
the Linux streaming decoder. The draft correctly makes no framing-recovery claim
and does not assert that FIFOEN itself has a universal UE0-only restriction.

## Corrected capacity model and required evidence

The170-byte unrestricted FR bound is correct for the existing formatter. Its
known PackStatus test does not validate raw state/mode/mask bytes, which can each
print255. The17 decimal widths sum78; adding prefix24,17 commas,50 raw-hex digits
and LF gives170. Event73 and the six conservative1151-byte remaining lines are
consistent with the unchanged serializer/buffer limits. No formatter was executed
for this preflight; widths were checked directly against its field decodes.

Independent arithmetic recomputation gives23303 packets and1505629 wire bytes
for5001 FR/4096 ER/six other lines. With one separate TC observation per packet,
the declared model gives217659 calls at8 effective stores,288575 at6 and331091
at5. These match the final draft and public-author preflight. The earlier166-byte
semantic-valid bound is historical and must not substitute for this broader case.

The finite reference fixture must track eight queued entries plus the separate
in-flight character, rational3125/36us timing and completion of the final stop
bit. That is an explicit model assumption, not actual FIFO/baud/WCET evidence.
The deliberately invalid-raw maximum-width exercise cannot claim strict semantic
receiver success or a real Robot attempt. Replaying the unchanged actual D116
stream through the native owner supplies the separate valid receiver case.
The six-effective-store capacity calculation is likewise separate from the real
owner's8-store ceiling; it cannot force FIFO state to manufacture that rate.

Implementation and frozen additive tests remain pending. Preserve unchanged
D090 native tests and D101 factory probe, current Runtime/D116 regressions, and
first failures. Exact recorder-default and app-default/MATCH target audits remain
mandatory: the prior app-default model has only456 bytes of remaining span,
so fitting added code/data is a concrete unresolved acceptance condition. No
buffer reduction or timeout extension is authorized to conceal a failure.

No physical setup-ACK reliability, actual service rate, full native delivery,
whole-tick800us bound, framing/exclusivity grant, motor permission or phase gate
is established by this preflight. The proposal is sufficiently defined to adopt
for the narrow independent software work while retaining those limits.
