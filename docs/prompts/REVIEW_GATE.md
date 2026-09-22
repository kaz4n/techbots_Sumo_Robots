# Gate review (Codex)

Independent review of the SumoX-26 firmware. You review only: do not edit any file. Read AGENTS.md first.

Phase under review: <Pn>
Commit range: <base>..<head>   (inspect with git diff and git log)
Spec sections to check against: <from the phase file>
Exit criteria claimed as met: <copy from state/PROGRESS.md>

Check in this order:
1. Rules R1 to R6 in AGENTS.md section 4. Trace every write to a motor PWM pin and to MOTOR_EN back to its source.
2. Spec conformance: does the code do what the named BEHAVIOR.md and HARDWARE.md sections say? List every mismatch.
3. Tests: does every new behavior have a test that names its spec section? Do any tests assert the implementation instead of the spec? Did anything under tests/locked/ change?
4. Real time: any blocking or unbounded work inside the 1 kHz tick? Any micros() wrap bug? Any path to NaN in a duty?
5. Explainability: anything a student team could not explain to a judge in two sentences?
6. Evidence: are the claimed measurements present in state/TUNING_LOG.md or state/FACTS.md, with numbers?

Output format:

## Findings
- [BLOCKER|MAJOR|MINOR] path:line: problem. Suggested fix.

## Verdict
PASS or FAIL (FAIL if any BLOCKER).
