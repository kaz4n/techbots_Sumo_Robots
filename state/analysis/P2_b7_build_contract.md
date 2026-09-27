# D244 B7 compile-only selection

This extends preparation of the approved B7-only profile to target compilation.
There is no upload, motor operation, new source grant or physical acceptance.
The checked D222 caller, D214 primitives and their old policies remain unchanged.
The new caller privately configures the checked D222 module, with a separate
closed B7 policy and artifact adapter; all current source/helper bytes remain
bound to a clean reviewed Git HEAD before any board mutation.

Command: `python -I -B tools/compile_b7_app.py --check-only|--execute --profile
b7_brownout --motors-allowed 0|1 --attempt TOKEN --reviewed-head FULL_HEAD`.
Argument grammar, exact built-in type checks, fresh exclusive owners, source
mapping, jobs1 compiler, child reaping and nine closing checks are inherited
without change. The sole profile is `b7_brownout`; bool is not a motor integer.
The FQBN is `arduino:zephyr:unoq:link_mode=static`, default Linux startup.
Flags are MATCH=0, explicit MOTORS_ALLOWED, all eight D222 profile macros=0,
then SUMOX_B7_BROWNOUT=1. No arbitrary flags, paths, upload or reset option exists.

Owner is `commission-b7_brownout-mN-DIGEST_FIRST12`, using D222's SHA256 of
`source_digest + NUL + attempt`. Raw evidence is in
`state/analysis/P2_b7_build_raw/OWNER`; all other build/stage paths keep the D222
grammar. Input/check/result schemas remain commissioning-app-static-v1 variants
with mandatory exact B7 profile, motor, source, attempt and HEAD fields. The
artifact reply preserves the inherited profile/motor/source/attempt fields;
its HEAD linkage comes from the checked parent input manifest and owner, not a
standalone HEAD field in that artifact reply.
Existing owners cannot be reused. Preserved failure evidence is never overwritten.

The wrapper checks D222's exact size/hash before executing it in a private
namespace, and adds itself, its policy, remote adapter and this contract to the
checked input closure. The frozen D222 caller remains an explicit hard pin.
Local policy and remote adapter select the same exact flags. Full metadata,
ELF/TLS/layout/exported-package checks are inherited unchanged. All five policy
snapshot identities remain D222's originals; no dependency imports from ambient
Python paths are admitted. Distinct M0/M1 configurations do not share mutable
module state. Native boot identity must still match the caller's verified boot.

Before native use: targeted host policy/grammar/private-state and controlled
caller tests, independent source review, fresh board identity check, frozen
source and clean sparse checkout. Compile M0 and M1 serially, then compile the
ordinary production selection to check isolation. Compilation supplies no
waveform, uptime, half-charge, direction, sensor, RAM or WCET measurement.
The existing deployment tool intentionally does not accept B7. Any future B7
deployment must explicitly require STAND OK and the actual setup/qualification
gates; it must never fall through to another profile's RING authorization.
