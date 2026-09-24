# P3 finite stopping trial

This separate profile prepares one P3 3.3 straight approach through the actual
acquisition, Robot, governor and MotorGate. `config::STOP_TRIAL_DUTY` selects
exactly 0.30, 0.40, 0.50, 0.60 or 0.70, with 0.30 as the development default.
The production `SEARCH_DUTY_MAX` remains 0.30. Duty selection requires an
identified configuration and build; there is no runtime duty command.

Compile only with the configured UNO Q Linux transport:

```text
python tools/board_tool.py flash bench/stopping_distance --compile-only
```

The checked route uses default startup and exactly these C/C++ build flags:

```text
-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_P3_STOP_TRIAL=1
```

The actual native Runtime receives empty setup grants. The checked build cannot
energize motors and has no upload allowlist entry. A later motor-capable run
needs its own human authorization; this preparation provides no physical
distance, electrical acceptance, settling, WCET or phase-gate evidence.

Enter the local service menu with a qualified long MODE press, then use two
short MODE presses to reach DRIVE_TEST from SENSOR_VIEW through QTR_CAL. A new
START press and release enters the complete countdown. A boot-held START,
selection alone or a match-mode selection cannot start this profile.

At GO, the existing Straight primitive captures the actual match heading and
requests the selected positive base duty for at most 1000 ms. Healthy IMU
observations provide the existing bounded heading correction; actual IMU loss
uses equal requests, and recovery resumes the captured heading reference.
The profile's governor caps each final electrical duty at the selected value
after voltage compensation and before the existing acceleration slew.

The report's duty fields describe pre-governor trial requests. Corrected requests
can exceed the selected base, while the final governed outputs remain capped.
Actual applied left/right duties come from MotorGate receipts and can differ
from the selected value during compensation, correction and slew. Record these
separately from the configuration and battery voltage.

An edge wins immediately, including at the approach or brake deadline. It
permanently cancels the trial and runs the complete existing edge escape. An
edge already present at GO leaves the report NOT_STARTED. Successful escape
exit inhibits EN/PWM immediately, then Lifecycle STOP follows on the next
distinct observation. All-white and recovery faults retain their existing
inhibited behavior. Opponent detections cannot select combat or restart travel.

If no edge occurs, observed Straight completion enters a full 500 ms zero-duty
Brake interval labeled NO_EDGE_TIMEOUT. Its end inhibits immediately and leads
to Lifecycle STOP. A delayed observation cannot backdate or skip braking. This
timeout is excluded from stopping-distance evidence. The fixed deadline does
not establish a safe starting position or protect against every failed sensor.

STOP, source faults and invalid application receipts also inhibit. There is no
automatic repetition. The report's finished flag ends the trial request; an
edge escape may still be moving afterward. A post-STOP service-only session can
clear that report while preserving the recording, but cannot enable another
trial. The existing recorder format does not serialize the trial report.

For later physical measurements, retain the original distance from the white
border's inner edge to the robot front at rest, identifying its orientation and
which rest observation was measured. Separately measure maximum outward
excursion from the same first-white reference and direction used for R_room.
The final rest position after reverse/pivot escape is not the maximum excursion.
Only compatible measured excursion and R_room values support the 70 percent
comparison. No duty-to-distance estimate or unmeasured reference offset is valid.
Three physical runs per duty, voltage, build/run identity and evidence-backed
approval of any production search-cap change remain pending.
