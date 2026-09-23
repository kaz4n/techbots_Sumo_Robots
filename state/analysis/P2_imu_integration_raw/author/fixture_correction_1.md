# D084 independent fixture correction

Initial freeze1790156647495225601 preceded all execution. Both inert probe modes
and all eight upload refusals passed. Both normal and ASan/UBSan test executables
compiled; each reported27cases,26pass,1fail. The only failing case was the actual
Estimator stream; allocation execution also failed on the first NO_NEW report.
Every command/exit/full output and opaque source hash remains in command JSONs.

The reviewer identified that independently authored NO_NEW fixtures omitted
BusStatus::OK and unchanged accepted sequence. The author then checked
P2_imu_heading_contract.md ordered admission paragraphs3 and5, which explicitly
require both. The D084 normal integration stream and allocation harness now set
those fields. No assertion was weakened and no production CPP was read.
The next runner invocation writes a fresh pre-execution manifest.
