# D160 actual run02: upload and capture complete, running not qualified

TARGET-UPLOADED / HARDWARE-OBSERVED; startup qualification remains OPEN.
One identified M0 static/default run used reviewed HEAD e852e2a5 and unchanged
source fcddbd8e. Invocation ran04:39:42–04:43:42 Dubai on25September2026, exit0.
No compile, extra reset/retry, motor-capable firmware or new hardware was used.

All14 numbered transport commands returned0 with empty transport stderr. The
upload report is UPLOADED (one child, exit0/reapedtrue/no timeout). Conditional
capture is COLLECTED:18 passive reads totaling713656B. Independent final local,
source/packet, installed and prerequisite checks pass; no query/compile attempt.
Both complete loader and sketch images match their references before and after
RAM observations. Exact originals remain in P7_static_startup_raw/native_run02,
plus native_run02_invocation.json; local packet333935B, raw capture stays on board.

The decoder observation is NO_RUNNING_PROGRESS, not running success:

- Both runtime samples: phase STOPPED(2), fault NONE(0), epochs3,
  initialization_complete0, next_release_us430099, maximum_execution_us790.
- Both transaction samples: phase IDLE(1), finished1, timing_valid1, faultNONE,
  started_us429103, decision_us429151, completed_us429598, execution_us495.
- The two observations are identical despite the required sample interval.

This establishes a flashed-image match and sampled stationary diagnostic state.
It does not by itself explain the stop, establish MCU/core global quiescence,
prove every intervening instant, or qualify full-loop timing/RAM/physical gates.
The sampled790us maximum over these few epochs is not the R4 worst-case test.
Source analysis and separate actual receipt review are the next steps. Do not
change firmware or perform an extra native read/reset under this consumed scope.
D156 original failed run and D159 exact temporary cleanup remain separate evidence.
