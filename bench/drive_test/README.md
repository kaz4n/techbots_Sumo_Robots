# P3 DRIVE_TEST

This separate firmware profile runs the existing SEARCH pattern and edge escape.
Openers, tracking, attack and re-flank are disabled. A normal local START/release
from the selected DRIVE_TEST service enters the complete countdown before motion
can be requested. Match selections do not start this profile.

Compile only with the configured UNO Q Linux transport:

```text
python tools/board_tool.py flash bench/drive_test --compile-only
```

The checked build has `MOTORS_ALLOWED=0`, empty hardware grants and no upload
allowlist entry. It is software preparation, not a runnable ring qualification.
The default app and B4 directional bench use their own unchanged profiles.

The existing menu enters services on a qualified long MODE press, then reaches
DRIVE_TEST after two short MODE presses (SENSOR_VIEW → QTR_CAL → DRIVE_TEST).
START must be newly pressed and released; holding it at boot does not start.
This profile displays D without the unavailable cross. STOP and faults still
inhibit; a post-STOP service-only session cannot restart motion.

Forward search starts with the existing 0.30 final electrical duty cap. Pivots
and edge escape keep their existing limits. Opponent readings remain recorded
but cannot interrupt SEARCH to engage a target. A successful escape brakes on
its exit tick and resumes a fresh SEARCH on the next eligible tick.

P3 3.1/3.5/3.6/3.7 physical trials remain unmeasured. Stopping-table trial duties
above 0.30 and isolated 90°/180° turn trials require separate bounded preparation;
this profile does not implement those tests or change the production search cap.
