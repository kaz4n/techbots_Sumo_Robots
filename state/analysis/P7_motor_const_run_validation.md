# D207 inhibited diagnostic preparation and host validation

26 September 2026. The current source and packaged diagnostic are those accepted
by D203, D204 and D205. The source digest is
`4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2`.
The profile is static/default startup, MATCH=0, MOTORS_ALLOWED=0 and
SUMOX_MOTOR_FAULT_PROBE=1. Setup grants, pins, 150 us SETTLE deadline and
4096-poll limit remain unchanged. This document does not report a new runtime
outcome; D201 is still the latest flashed image at this preparation point.

## Source and host evidence

The independent oracle freezes preceded inspection or execution of the new
implementations. Exact derivations retain all 99 historical native methods and
all 67 corrected decoder methods, with seven native and three decoder additions.
The four implemented modules, current ABI map and preparation match their
prospectively recorded hashes. Preparation review `e06f3b73`, caller/actions
review `74083d6e`, remote review `316fec95` and interpreter/map review `f4fd1bc8`
are final PASS within their stated scopes.

All eight first host invocations ran serially under Python -I -B:

| Suite | Linux | Windows |
|---|---:|---:|
| Remote capture | 47 pass | 29 pass, 18 Linux-covered skips |
| Action sequencing | 29 pass | 24 pass, 5 Linux-covered skips |
| Caller | 30 pass | 9 pass, 21 Linux-covered skips |
| Offline interpreter | 70 pass | 70 pass |

No suite failed, timed out or required a retry. The Linux caller took 303.659
seconds including outer orchestration, within its declared 600-second bound.
Saved method streams, hashes and serial intervals are retained. All 302 native
and 184 interpreter coordinator pins, and all 290/177 independent pins, remained
unchanged. Scoped Linux fixture prefixes and Windows temporary directories were
empty after execution.

`native_host_closing01.json` is 52838 bytes, SHA256
`eeccfad26bc2e9e89b7e79d3355a38d7e486b2ac7c250ede01c787b71021b0ed`.
`interpreter_host_closing01.json` is 30769 bytes, SHA256
`d331a41bf4304e3cde7c6c95778902ba8721c68b1be70af57a112319326f81b5`.
The native summary retains a leading apostrophe from unittest quoting in its
44 skip-reason strings. The independent caller review records this clerical
issue; raw logs, method identities, outcomes and historical skip coverage are
correct. The immutable summary and original evidence remain preserved.

Two local preparation errors remain recorded: the first preparation object
used digest-only values and failed its expected hash before writing, and a
coordinator builder used the wrong freeze key before the unchanged test driver
refused a missing coordinator file. Corrections restored the declared schemas;
neither changed expected source/oracle hashes, consumed a test owner or invoked
the board. They are not erased or relabeled as successful attempts.

## Fresh board admission

Accepted D206 cleanup removed exactly the three stale D201 scratch copies.
At 14:29:32 Dubai, the separately reviewed read-only admission ran once in
0.932 seconds, returned zero and had empty stderr. Its raw stdout is 12681 bytes,
SHA256 `9a84758f0c6294fbb591626a7bec3ab591ebdbe44505deb5479ba9e20b239b6c`.
It verified the expected Arduino identity and boot, all 19 required files,
accepted cleanup result and staged sources, four required absences and no
recognized process conflicts. Board root available space was 13914370048 bytes.
All 13 local admission bindings remained unchanged.

The exact eleven-role scope is 1875 bytes, SHA256
`23c1fcf6ddb371d5e7c641bab67b78c927ac541b4090cc390942de90bd86f700`.
Its caller and remote review roles are final; decoder/map acceptance remains an
additional coordinator gate. Final independent native admission, a clean
committed HEAD and local check-only still precede one upload and conditional
capture. These checks neither reserve remote resources nor replace the native
caller's repeated identity, source, process and closing guards.

The later actual report must distinguish collection integrity, setup outcome,
any later callback or timing failure, current versus lifetime SETTLE reports,
and all loss/inhibition fields. Equal samples do not prove coherence. Host
success is not hardware acceptance, a timing remedy, WCET or a phase gate.


Final admission addendum: independent review `3f0357cd3e8bd5d00edd29200e75875d0f8cc2f81391fcda8bf276277d3053e2` (9553 bytes) accepts the actual read-only board evidence and exact scope. All reviewers have stopped writes. A clean committed HEAD and successful local check-only remain required before the one inhibited execution.
