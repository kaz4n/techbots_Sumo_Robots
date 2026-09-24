<!-- Documents the D129 P4 timing-evidence build and event interpretation. -->
<!-- Separates observed source/application timing from physical acceptance. -->
<!-- Independent profile and build-policy tests verify the inert route. -->
# P4 reactive timing evidence

This opt-in build adds one target-loss timing candidate to each actual accepted
P4 attempt. It uses the unchanged reactive behavior: ordinary local match-menu
START, the full 5000+100 ms hold, SEARCH at non-edge GO, then current perception,
contact, Governor and edge authority. It adds no motion command or source grant.

Compile only through the configured UNO Q Linux transport:

```text
python tools/board_tool.py flash bench/reactive_timing --compile-only
```

The checked default-startup route requires exactly these C/C++ flags:

```text
-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_P4_REACTIVE=1 -DSUMOX_TIMING_EVIDENCE=1
```

The wrapper uses actual NativeSources, UnoQPort and Runtime with empty setup
grants. It cannot energize motors and has no upload allowlist key. MATCH and
Immediate-startup requests are rejected. Real M0 Gate receipts stay zero and
cannot arm a duty-drop trial. A synthetic host receipt can exercise arithmetic;
it is not evidence of applied hardware motion.

The trace arms only during ATTACK approach without contact, with current raw
and effective front detection and an immediately preceding valid ATTACK receipt
whose actual left/right duties are both positive. The first later fresh raw
all-front-clear consumes its sole candidate. The recorded source interval is
the actual seven-channel read start/end; Fusion retains its existing decision-
time debounce. The same prior-approach receipt conditions are checked again at
onset. A stale earlier nonzero report cannot qualify a later clear.

The actual normal loss-brake decision saves its full 64-bit request token. Only
that request's valid, enabled, exact-zero application receipt completes the
trace, using its actual application timestamp. Receipt arrival time and a later
request's zero are never substituted. No deadline is fabricated at 35 ms.

Transient raw reassertion, relevant stuck/phantom suppression, contact, unrelated
routes, edge, STOP, source faults and invalid receipts close the candidate with
explicit diagnostic events. Exclusions before onset may have no source pair.
An onset without the required immediately preceding approach receipt records
the pair and EXCLUDED_NO_APPROACH. A closed candidate never retries within the
attempt. Duplicates produce no fresh pulses; reset or missing tail evidence may
leave an incomplete trace rather than a synthetic completion.

Conditional event type 10 uses the exact metadata contract in
[P4_timing_evidence_contract.md](../../state/analysis/P4_timing_evidence_contract.md).
HEADER follows START_RELEASE; the source pair and decision diagnostics follow
ordinary current events. Matched receipt completion precedes the next current
observation's events. Keep ordinal order rather than sorting wrapped timestamps.
The existing eight-byte event format, CSV schema, 25 Hz frames and first4096
event retention remain unchanged, including all overflow/loss reporting.

For read interval [S,E] and matched zero receipt A, the observed delay lies in
[A-E,A-S]. With the current 35000 us inclusive limit, an upper bound at or below
the limit passes; a lower bound above it fails; an interval crossing the limit
is indeterminate. Missing or interrupted evidence cannot pass. A header without
a candidate means NOT_EXERCISED, and a missing header means NOT_RECORDED.

These timestamps do not measure physical box removal, the first GPIO/PWM edge,
mechanical rest, or a phase gate. Offline analysis is a separate task. Physical
P4 trials, identified motor-run authorization, live RAM/stack/WCET and P5 native
trace feasibility remain pending.
