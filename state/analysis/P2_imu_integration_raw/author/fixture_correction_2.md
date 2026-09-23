# D084 independent coverage enhancement after passing second run

Second run passed all5tooling methods, including both27case/158255assertion
normal and ASan/UBSan executions. Before the final snapshot, allocation guarding
was constant-initialized true and the probe now checks allocation count before
setup, so static constructors are observed as well as setup/runtime/destruction.
This follows a reviewer coverage finding; no production behavior/assertion changed.

The existing seeded actual Estimator-to-Robot stream now uses nonzero gyro,
verifies accepted raw bias1, preservation of old numeric report at applyBias,
and occasional synthetic horizontal rail flags. Explicit checks require VALID
gyro and separate INVALID acceleration on those source observations; the full
hold, edge, governor bounds, STOP, matched receipts and retained-heading checks
remain. Sensor metadata is synthetic software input, not physical evidence.
The next invocation writes a fresh immutable pre-execution freeze manifest.
