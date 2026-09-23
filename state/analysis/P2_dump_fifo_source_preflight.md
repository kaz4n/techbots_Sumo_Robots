# D117 source/public compatibility preflight

2026-09-24. Implementation-author source preflight, not independent final review.
No production edits, compilation, tests, test-body reads or board action.

## Current owner compatibility

Only three actual owners occur in src/bench: `src/app/app.ino:13`,
`bench/recorder/recorder.ino:11`, and `bench/p2_dump_compile/src/dump_probe.cpp:8`.
All are fixed-lifetime default-constructed objects. The first two will receive
explicit FIFO8 construction; the compile-only link probe keeps legacy default.
No actual owner copy/move, assignment, aggregate initialization, byte serialization,
memcpy/memset, sizeof/offsetof assumption, inheritance or container use was found.

`src/app/dump_port_unoq.cpp:9-19` uses an owner reference/address and calls the
unchanged begin/ready/port signatures. `src/app/runtime.cpp:17-19` copies DumpPort
callbacks/context and constructs Transfer from its Port; it never copies the
native object. Runner has the same callback ownership model. Adding a private
selection cannot change these callback function signatures or context identity.

The const enum changes C++ type traits: implicit copy/move assignment becomes
deleted. It does not delete copy/move construction; moving a const enum copies
that scalar. This is compatible with the current actual callers, not a claim of
universal source/ABI compatibility. The old class is already non-aggregate due to
private data. Both proposed constexpr constructors can initialize all fields from
existing constant member initializers, with no hardware/reference dependency.
No out-of-line constructor symbol or new factory thunk is required. Do not add
other copy/move API changes in this task.

Native private offsets/sizeof and global BSS may change. Nothing inspected exposes
that object's fields as a wire ABI. Existing `tools/runtime_capture.py:304,408` and
`tools/ui_adc_capture.py:550,582` bind old exact ELF hashes/layouts; they are not
automatically applicable to new builds. Fresh target inspection remains required
for all three adopted build configurations. No old capture pin is to be relaxed.

## Existing first-failure status order

Exact source baseline: dump_uart_unoq.cpp
6dfaca493024d49d67497f2708ffb51e848447148423b82b4bbb3c10c250d2f3.
The new enum test goes after attempted latch and before existing first grant check;
legacy valid-mode checks below keep their order, short-circuit behavior and statuses.

| Existing site | First failing condition/result |
|---|---|
|138-150|Reentry/poison invokes abort, returns POISONED; first missing grant OWNERSHIP; context CONTEXT; existing singleton OWNERSHIP; metadata/ready-device/RCC DEVICE; already initialized/init_res/nonidle IRQ OWNERSHIP.|
|151-156|Claim lifetime singleton; ready-pad configure error READY_ERROR; device_init error or not-ready DEVICE. These cannot retry and never release the singleton.|
|157-161|After init, combined context/metadata/clock/nominal/IRQ-active/pending rejection returns OWNERSHIP, including metadata rejection here.|
|162-166|Unexpected installed CR1/CR2/CR3/PRESC/BRR returns REGISTER. FIFO adds AUTOCR zero at this register gate.|
|174-179|Post-mode ownership returns its actual first cause; abort/cleanup does not replace that immediate begin result.|
|181-184|Ready ERROR terminates as READY_ERROR; ready LOW is accepted setup and returns OK.|

Live `ownership()` at186-198 orders CONTEXT, NOT_INITIALIZED, lifetime OWNERSHIP,
metadata/not-ready DEVICE, clock/pad/IRQ OWNERSHIP, saved-clock OWNERSHIP, then
register/TEACK REGISTER. FIFO AUTOCR mismatch joins only the last register group.
`ready()` prioritizes existing POISONED and CONTEXT before ownership/ready. Native
advance checks POISONED then CONTEXT, takes its actual clock/interrupt mask,
checks ownership before payload validity, then each store admission checks owner,
ready, deadline, room and deadline. D117 must not globally reorder these paths.

## FIFO transition cleanup coverage

The existing abort relies on initialized live ownership, including TEACK, so it
cannot alone implement required cleanup for a partially initialized FIFO state.
A separate setup-only owned-state cleanup check is required; no public helper or
new owner is needed. Retain lifetime, metadata/device, clock/pad/IRQ, saved snapshot,
register and exact known-CR1 checks; omit only live TEACK/initialized eligibility.

| Failure point after first new CR1 write | Status and cleanup obligation |
|---|---|
|First CR1=0 readback mismatch|REGISTER; if still exactly prior verified installed state or attempted0 and other facts hold, one cleanup0 write/readback; otherwise no foreign write.|
|Owned-facts guard before disabled-mode or final-enable write|Preserve guard's first CONTEXT/OWNERSHIP/DEVICE/REGISTER cause; poison. It normally also defeats cleanup; re-evaluate exact facts without claiming recovery or another setup attempt.|
|TE+FIFOEN readback mismatch|REGISTER; same one conditional cleanup using last verified0 or just-attempted disabled mode.|
|UE+TE+FIFOEN readback mismatch|REGISTER; same conditional cleanup using last verified disabled mode or just-attempted enabled mode.|
|Final ownership fails, including TEACK low|Preserve actual ownership cause; missing TEACK alone must still perform cleanup0 because it does not disprove setup ownership. Clock/pad/IRQ/AUTOCR/foreign CR1 loss forbids the write.|
|Final ready sampling returns error|READY_ERROR; perform setup cleanup if the now-current facts still prove ownership, then poison. Ready LOW is successful setup, no cleanup.|
|Cleanup readback itself fails|Keep the original begin cause, cleanup unverified, permanently poisoned; no second cleanup write or polling.|

Every listed failure clears local pending state and permanently poisons after the
first direct FIFO mutation. There are no TDR writes during setup. A later repeated
begin/ready/write can return POISONED under existing semantics; the contract's
first-reason guarantee applies to the original failed begin return/status, not
an immutable status across all subsequent public calls. Runtime cancel remains
strict D090 live ownership and must not inherit the setup-only TEACK exception.

For new FIFO-only guard calls, adopt ordinary ownership cause order without its
NOT_INITIALIZED gate: context, lifetime identity, metadata/device, clocks/pads/IRQ,
saved clocks, then register invariants. New CR1 readback mismatch is REGISTER;
AUTOCR mismatch is REGISTER. Readback follows the attempted write immediately;
its failure is not replaced by a later cleanup failure. Earlier existing gates
still win before any new guard is reached. No new NativeStatus enum is needed.

## Concrete draft corrections and limits

Qualified the metadata DEVICE statement to the pre-init gate, preserving the
actual existing post-init OWNERSHIP grouping. Changed conditional setup cleanup
from permissive 'may' to mandatory 'must issue exactly one' when its predicate
holds, matching root's selected inhibition requirement. No other contract or
production change. Root/public-oracle review should freeze the exact new-guard
precedence above before implementation. Immediate TEACK reliability and complete
physical FIFO service remain explicitly unproved; no timing/poll constant is added.

## Conditional target memory risk

Verified state/FACTS.md:491,499 (F130/F132) gives app default ordered peak261688 with only456
bytes of modeled span remaining; MATCH peak260056 leaves2088. Therefore neither
the mode byte nor added setup/cleanup code is assumed to fit. Fresh exact app
default/MATCH and recorder target/ABI/ordered-allocation evidence is mandatory.
Retain any initial fit failure. Common native ownership checks may be factored
within the same four-file scope only with preserved legacy callback/read/status
order; no unrelated optimization, reduced buffers or weakened config/grants.
These are conditional loader-model spans, not measured free RAM or WCET.
