<!-- Documents the D128 reactive profile and its checked inert build route. -->
<!-- Separates software preparation from physical trials and motor permission. -->
<!-- Independent profile and tooling tests verify the behavior and build policy. -->
# P4 reactive profile

This separate build uses the actual acquisition, Robot, Governor and MotorGate
for SEARCH, TRACK, ATTACK, DEFEND_TURN and stall/re-flank behavior. Openers never
start or run in this profile. All six local match-mode selections use the same
reactive behavior; the selected mode remains recording metadata.

Compile only with the configured UNO Q Linux transport:

```text
python tools/board_tool.py flash bench/reactive_test --compile-only
```

The checked route requires default startup and exactly these C/C++ flags:

```text
-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_P4_REACTIVE=1
```

The wrapper uses actual NativeSources, UnoQPort and Runtime with empty setup
grants. Electrical outputs remain inhibited. There is no upload allowlist key;
the tool rejects upload, MATCH and Immediate-startup requests for this sketch.
This build supplies no sensor readiness, wiring acceptance, motor-run permission
or physical timing evidence.

Admission uses the ordinary local match menu. After actual initialization and
source readiness, a new qualified START press and release enters the complete
5000+100 ms hold. Service-menu selections cannot start this profile. Boot-held
START, MODE cancellation, STOP, source and application-receipt checks retain
their existing behavior. A service-only session cannot authorize motion.

At a permitted GO without an edge, the visible state is SEARCH for that
observation. Actual Search receives the current effective opponent mask: an
already confirmed target produces its zero-duty PERCEPTION exit at GO, while
an empty mask starts genuine Search with its captured timer and heading. A new
raw assertion alone does not establish an effective target. Zero duty after the
full hold does not require EN low in a separately authorized motor-capable build.

The next distinct eligible observation uses ordinary perception arbitration.
It counts as the first centered observation; ATTACK requires the third centered
post-GO observation. Existing steering, bearing memory, contact qualification,
Governor caps and slew, lost-target braking, DEFEND and stall/re-flank remain in
force. Duplicate calls cannot restart or advance motion.

Edges retain full priority and the complete escape behavior, including at GO.
A successful escape exit selects from current perception and brakes for that
observation; its selected executor runs no earlier than the next tick. STOP,
faults and lost permission continue to inhibit. Push-through remains disabled
at its existing development default.

Host tests and compile-only receipts do not establish P4.1-4.7 physical results
or a phase gate. The existing 25 Hz frames cannot prove the P4.2 duty-drop limit
or P5's one-tick abort timing; exact condition/decision/application evidence is
a separate task. Later physical trials need their own identified build, actual
readiness, human run authorization and recorded measurements.
