# B7 brownout software preparation

The D244 profile implements P2 B7's original twenty full-forward/full-reverse
cycles. It uses forty confirmed full-electrical-duty dwells of 500 ms each,
with a 1000 ms reach deadline, normal slew/reversal braking and existing safety
arbitration. Inhibited M0 receives no credit and reaches timeout.

This wrapper requires compiler-wide `SUMOX_B7_BROWNOUT=1`, `MATCH=0` and
`MOTORS_ALLOWED=0`; all setup grants remain absent. It is not a qualified robot
configuration. Use the separate app compile-only command documented in
`state/analysis/P2_b7_build_contract.md` for M0/M1 toolchain checks. Do not use
another bench profile's upload route or motor authorization for B7.

Actual acceptance still needs verified wiring/setup, a half-charged pack,
fresh run-specific STAND OK, observed direction, and independent continuous
uptime/boot evidence before START through final STOP. A report in volatile RAM
cannot prove that a reboot never occurred. Acknowledged full PWM settings do
not prove continuous EN, waveform or delivered motor power. Stop, edge, fault
and in-process reset consume the attempt; a restarted board is a new attempt,
not continuation of a passing test.

Evidence: `state/analysis/P2_b7_brownout_validation.md` and its independent review.
