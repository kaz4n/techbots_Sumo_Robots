# P3 isolated turn accuracy

This profile prepares one P3 3.4 turn trial through the actual acquisition,
Robot, governor and MotorGate. `config::TURN_TRIAL_DEG` selects exactly +90,
-90, +180 or -180 degrees, with +90 as the development default. Positive turns
are rightward; negative turns reflect yaw coordinates and swap wheel requests
through the unchanged Turn controller. The real IMU availability is preserved.
Each future trial must identify its exact configuration and build.

Compile only with the configured UNO Q Linux transport:

```text
python tools/board_tool.py flash bench/turn_accuracy --compile-only
```

The checked route uses default startup and exactly these C/C++ build flags:

```text
-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_P3_TURN_TRIAL=1
```

The wrapper has empty hardware setup grants and no upload allowlist entry.
The checked build cannot energize motors. This preparation does not establish
physical accuracy, fallback timing, settling, electrical acceptance or a phase
gate. A later motor-capable run requires its own human authorization.

The local service menu enters on a qualified long MODE press. Two short MODE
presses reach DRIVE_TEST from SENSOR_VIEW through QTR_CAL. A newly pressed and
released START then enters the complete countdown. Holding START at boot or
selecting a match mode cannot start the trial. No remote angle selection exists.

At GO the profile requests the configured turn at the existing TURN_DUTY,
through the existing PIVOT governor. Completion or the unchanged turn timeout
starts a full 500 ms zero-duty brake interval at its actual observation. The
end of that interval inhibits EN/PWM immediately; the next distinct observation
establishes Lifecycle STOP. A timeout remains a distinct recorded outcome, not
a successful accuracy result.

An edge cancels the trial permanently and runs the existing complete edge
escape. If the edge is already present at GO, the trial stays NOT_STARTED.
Successful escape exit inhibits immediately and establishes STOP on the next
distinct observation. STOP, source faults and invalid application receipts also
inhibit. There is no automatic repeat or return to SEARCH or combat. The retained
report and recording distinguish trial completion, timeout and interruption.

A post-STOP service-only session remains inhibited and shows DRIVE_TEST as
unavailable. It reconstructs Robot and clears the trial report; the retained wire
recording contains frames/events, not the report. Capture a needed report before
that reset. It cannot authorize another trial. The requested brake interval is
software timing and does not measure physical settling or the final turn error.
