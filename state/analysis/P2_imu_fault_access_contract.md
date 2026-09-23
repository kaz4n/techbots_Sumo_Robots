# D097 passive IMU setup-fault evidence

2026-09-23 Asia/Dubai, baselinea93d536. Previous turn PROGRESS: actual native
runtime3be9669 is host-tested; exact full-app target fails RAM by14312B. D051/D075
permit this bounded P2 dependency correction, not a capacity or behavior change.

Add `Sample Acquirer::setupFailure() const`. If actual Setup is FAULT, return the
already latched setup-failure Sample by value, preserving every field, timestamp,
sequence, bus status, cleanup and error flag. Otherwise return canonical default
Sample (NOT_READY), including before setup, setup pending, profile-ready, runtime
observation/pending and runtime-only fault. Never expose stale motion as a setup
failure. No clock argument, bus operation, allocation, state change, completion
pulse, reset, retry, time admission or observer update. Repeated reads are passive.

Actual Acquirer start/advanceSetup already latch the failure. This accessor must
not synthesize a replacement from a partial SetupReport or call legacy read.
Leave legacy read, mixed-API cancellation, asynchronous acquisition and all setup
behavior unchanged. Use the accessor only in NativeSources::imuSetupFailure;
retain SourcePort's existing callback signature for compatibility and ignore its
time argument because retrieval does not observe a new time. Runtime still obtains
this evidence only after actual setup fault and observes it once, unchanged.

Independent public-spec tests must cover start and advanceSetup failure, all
Sample fields, repeated const reads/no bus calls, canonical absence outside setup
fault and unchanged legacy behavior. Add a native binding substitute test so the
actual callback cannot silently keep routing through legacy read. Preserve all
established/locked tests and config. Root owns public interface, implementation,
shared build/state; independent author owns new tests only; separate reviewer is
read-only. No hardware operation is needed to validate the getter contract.

Compile the same actual app on the pinned board-Linux toolchain without upload.
Compare exact source and all three linked images to D0964cb637f9. Confirm removal
of unintended Acquirer::read/Bus::acquireMotion app dependencies while preserving
48-step setup/native async paths, imports and startup. Measure net memory rather
than claim the estimated752B direct symbol saving. Remaining oversize is still a
failed target build; this small correction cannot alone close the recorded deficit.

Seven existing inert keys require exact independent source review before refresh;
no new key/app upload, setup grant, pin/capacity/tunable change, measured timing or
human gate. Larger inherited Bridge/serial dependency investigation is separate.
