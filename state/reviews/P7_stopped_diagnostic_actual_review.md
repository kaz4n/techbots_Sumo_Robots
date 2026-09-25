# D161 stopped-state diagnostic: actual review

25 September 2026, Asia/Dubai. Same-model review reusing D149/D160 source context.
Independent local parse of invocation raw output, without using the coordinator's
parsed artifact. No native command, source edit or additional capture by reviewer.

**Scoped collection/interpretation PASS; observed runtime qualification remains
negative.** One invocation at HEAD1d455be7dcd86d7946afd29567bc4b1835409d72,
UTC01:00:54.451403-01:00:56.467693, outer returncode0/empty stderr/no exception.
Intent SHA256
`ed5db4039ec817a0a79be75332aa326b75da63f469b3fba824ae22fbcfead2e6`;
invocation SHA256
`de7ac9b4ae0f1bbd31007d4e0b933f9cfd5fbeef408e9c226682bdd5f24a7372`.

Independently rehashed all eight named local pins, including source71507fd8,
planbf992388, review71305a36 and ADB. Parsed the shell-quoted remote argv without
execution: exact source bytes, three pinned payload members,60367B/payload
SHA1e2439f9 and27577 Windows UTF16 units match intent. The intent separately
records17 runner pins/103 source/102 stage admission. Actual remote argv is
exactly the four approved labelled mdw phys windows, END and shutdown.

Remote report is COLLECTED, commands1, child returncode0/reapedtrue/timed_outfalse,
no first/postcheck errors. Actual identity retains UID1000/aarch64 and expected
boot6d4aca1b-ac1f-4caf-b1ef-e127ce3956f6. Outer local postcheck_errors is empty.
Pinned code checks identity and all five files before/after. OpenOCD stdout is
empty; its stderr retains banners/deprecation notices and all labelled words.
Those normal diagnostic/data lines must not be confused with outer stderr.

Parsed BEFORE/TRANSACTION/INPUT/AFTER/END exactly once and in order. Every data
line has the expected contiguous address and exact eight-digit hexadecimal words;
counts7/126/48/7 reconstruct28/504/192/28 little-endian bytes,752B total.
Reconstructed hashes: both Runtime brackets
ada6d02f79a58797868af0a62d253c1ecdb487c35dce64db0f14f396c412fd34;
Transaction4f30f4a97de8a6d24377d77b51681d83ca024ace0d5d89d50bd6c8dbeb8c31f8;
Inputd63823a03ef0d00224fc5511e90d54ab15f5ba38b8c92451f3171e319bc0730c.
Both Runtime28B and Transaction's first24B exactly match both D160 samples:
STOPPED/epoch3/initfalse, transaction IDLE/finished/timing_valid and495us.

D149 receipt a7c0c479 supplies the exact layouts. Transaction+112(u16) is0x0110:
APPLICATION_CONTRACT16 and LINE_CONTRACT256 (src/core/fsm.h:395-400), no unknown
bits in that field. Escape fault+114 is0. Robot token3, ui_state10 STOPPED,
motors_enabled0. MotorGate fault+472 is3 IO (src/hal/motors.h:10), consumed+473=1.
Current applied feedback at+424: applied_valid0, token3, applied_us429580,
motors_enabled0, both duties0, duration_valid0, completed_us/execution_us0.

Input t_us429151/init_complete0; PreviousTick at+64 has applied_valid0, token2,
applied_us428628, motors_enabled0/zero duties, duration_valid1,
completed_us428647 and execution_us546. These are distinct prior/current receipt
fields; transaction timing_valid1 does not establish a valid motor application.
The invalid prior receipt is consistent with APPLICATION_CONTRACT admission
(fsm_robot.cpp:186-195). The bitmap and IO enum are observed stored facts;
the first failing callback, first-fault time and precise original cause are not.

Equal prefixes show sampled stability across D160/D161 only. No atomic nested
snapshot, uninterrupted image/MCU continuity or current full-flash recheck is
claimed; D160 flash provenance is inherited. No measured physical motor/pin,
sensor, timing/WCET, free-memory, production-static or human-gate acceptance.
All original raw output remains evidence. D161 is consumed; no automatic retry,
reset, upload or firmware change follows. No open material collection finding.
