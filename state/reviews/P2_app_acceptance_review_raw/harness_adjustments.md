# Reviewer harness corrections

Initial receipt comparison asserted equality of all preflight and real-build
properties. It stopped at `assert props == preflight`. Inspection found only
`extra.time.utc` and `extra.time.local` differ (1790183752 to 1790183754 in the
default run), as expected for separate CLI invocations. The comparison now
excludes exactly those two timestamp fields, after both public validators check
all required effective command properties. No production change was requested.

The first MATCH comparison expected only MotorGate::transact to change. Actual
objects additionally changed UnoQPort::writeEnable and writePwm; both contain
existing MOTORS_ALLOWED branches (native EN admission and nonzero PWM rejection).
Source lines 289-327 confirm this is the expected motor-capable mode distinction.
The final assertion permits exactly these three sections in two objects, requires
the same relocation-change set, and rejects any added/removed allocated section.
No firmware difference or weakened safety check was requested.

The optional disassembly excerpt helper needed three local-only corrections:
the collected disassembly field is a string (not a stdout dictionary), labels
are demangled, and re.split produces an empty first chunk. The initial helper
attempts raised TypeError, AttributeError and IndexError respectively. Filtering
the nonempty demangled sections produced match_motor_functions.txt. No receipt,
firmware, test or binary was changed.

The fixture verifier initially accepted relative folder arguments but attempted
to report them relative to absolute ROOT, raising ValueError. Resolving its two
input paths before reading fixes that local reporting mismatch. Fixture receipts
and acceptance assertions were unchanged.
