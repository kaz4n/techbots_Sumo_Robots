# D169 explicit inert diagnostic activation

The D168 image compiles but its default grant is false. Add one build selector,
SUMOX_MOTOR_FAULT_PROBE, default0 in src/config.h. Accept values0/1 only. When1,
require MATCH=0, MOTORS_ALLOWED=0 and every other SUMOX profile selector0.
No existing value, pin, safety bound or default changes.

The same bench/motor_fault sketch passes Grants{true} to its existing Runner only
when this selector is1; otherwise preserve Grants{} behavior. Construction, loop
gating and all Trace/Runner/native MotorGate implementations remain unchanged.
There is no serial/Bridge/network activation path. The selector is a build choice,
not an upload/run authorization or evidence of exclusive pad ownership.

Checked build policy admits exactly these two motor_fault.ino flag strings:
- -DMATCH=0 -DMOTORS_ALLOWED=0
- -DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1
Both require the exact base FQBN/default startup and dynamic linking. Preserve
the existing property/recipe/dependency/artifact checks, and the C/C++ flag match.
Other projects gain no admission for the new flag. Explicit0, reordered/extra/
duplicate flags and alternate FQBNs remain rejected by checked motor-fault builds.
No CLI upload allowlist, consumed caller/manifest or staging helper changes.

Independent companion tests derive from this contract and public headers, not
implementation bodies. Cover default/0/1 config, invalid numeric values, each
unsafe/exclusive profile, actual sketch setup and loop selection using controlled
header/Arduino substitutes, and exact policy/property admission/refusal. Copy only
the opaque sketch into owned RAM if include resolution needs it; preserve its bytes.
Test the real config and policy. Add no weakened/skipped legacy assertions.
Run unchanged existing diagnostic normal/sanitized and macro regressions plus
relevant policy tests. Freeze new expectations before implementation validation.

Host-only scope: no board, new target build, upload/reset or passive capture.
The policy-denied existing stage remains untouched, including by helper cleanup.
An active image still needs fresh artifact binding and a separately identified
inert run/capture. Instrumentation may change timing; the original D160 fault,
physical acceptance, WCET, motor permission and human gates remain unproved.
