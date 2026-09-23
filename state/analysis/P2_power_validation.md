# D078 native battery driver validation

2026-09-23 Asia/Dubai. Baseline64317be, contract/source commits a8e840d/fbd9d96.
Actual implementation commit e6b7060.
D051/D075 permit P2 software before physical acceptance. This increment supplies
the actual private native ADC1/PA4/channel9 implementation in power.cpp, with an
inert retained-method target probe. It does not integrate the application.

## Implementation

One fresh14-bit regular conversion per read,814-cycle sampling and required
LFTRIG. Setup performs bounded regulator/calibration/enable stages and a
completion-anchored2us minimum calibration gap. One100us runtime acceptance
deadline covers admission through final publication; separate100us fault cleanup
cannot convert an unacknowledged stop into success. Finite poll counts terminate
even if micros stops. Validity, raw value, timestamp interval, status and shutdown
acknowledgement remain distinct. No previous sample, healthy-voltage substitution
or second governor filter is returned.

Checks bind installed metadata, private ADC1 ownership, disabled idle ADC4,
inactive DAC1 channel1, pad/mode/IRQ consistency, nominal clock configuration,
ASV, Range1 and its EPOD booster. A boot-lifetime claim survives failed setup,
destruction and ignored first writes. No reader reset/retry API, shared-clock
change, stock blocking ADC call or constructor I/O is introduced.

Nominal3.3V and122/22 scaling, proposed A0 and all development bounds are recorded
in D078/TUNING_LOG. No existing B16 value, core/app or established locked test
changed. Hardware divider/reference accuracy is not implied by these constants.

## Actual validation

- Normal host CTest2/2 PASS4.37s, exit0. ASan+UBSan2/2 PASS19.21s, exit0:
 1030cases/20982541assertions and host-only enabled MotorGate37/3796846,
 no failures/skips. Receipts: power_host, power_sanitize_build/tests in
 P2_power_raw. Those suites exclude native target code, which is tested separately.
- Independent native author:9 Python methods PASS148.989s.51 binaries and104
 subprocess receipts:102 exits0 plus2 explicitly expected exits1 proving child
 assertion/crash propagation. Successful case executions include18 core,
 6 ownership,4 timing,1 ignored-write takeover,22 metadata,22 config and2 inert
 probe cases. Child assertions execute in fresh-boot forked processes; printed
 doctest assertion totals count parent status assertions and are not child totals.
- Final actual UNO Q Linux compile-only: source aggregate
 `a936d10d471c80c937bee3d312a99de40acfbc57fefced9fd51d409a097024dd`,
 MATCH0/MOTORS_ALLOWED0/default,81132B program/33476B compiler memory, exit0.
 Source CPP SHA256
 `505e008ea99f6e739968572ae5674a858fc646a81001f6e6af01e3117c60543d`.
 Exact40-file map,3 ELF artifacts,36 nonzero native exports, retained methods,
 direct register/NVIC/DMB paths and pointer-only setup were independently checked.
 This is an isolated probe, not full-application RAM or measured free memory.
- Broad existing tooling:411 tests PASS439.559s, exit0. New native9-method suite
 was run separately, so420 distinct tooling methods pass in total; no test was
 waived. Exact command/output/status: power_existing_tools.json/txt.
- Fresh separate same-model reviewer PASS/no open findings in this software
 scope. Independently replayed all9 native methods: PASS163.787s,75 positive
 native cases, no skips;104 subprocess receipts include102zero and the2 required
 negative isolation sentinels. The480 printed assertions are parent status
 checks, not every child assertion. Review: ../reviews/P2_power_review.md/raw.

The actual target collector is P2_power_target_audit.py. Source and ELF receipt
is P2_power_raw/target_a936d10d_bench-default.json. Initial f9a968c0 target also
compiled at80880/33316B; that earlier snapshot predates repairs and is not final
validation. Existing P2_motor_gate_record.py captured commands/output/status;
only uniquely named power_* receipts were relocated unchanged to this raw folder.

## Failures and corrections

Independent tests did not read production CPP. They caught two real defects:
an ADC write after readiness-triggered ownership loss, then new-reader recovery
after an ignored first configuration write left registers pristine. The first
was repaired with transition ownership/deadline checks; the second with the
irreversible claim. Original failed executions and source hashes are retained.
Each defect passed its repair; no existing locked assertion was changed.

Fixture compiler/extraction drafts, a dormant disabled-fraction expectation,
deadline-observation versus completion timing, the U585 SYSCFG address and
fresh-root stock-init coverage were corrected against the contract/sources.
These corrections did not relax production requirements. Explicit failure
sentinels ensure forked assertions/signals cannot silently pass. Test README and
author receipts preserve the distinction between real defects and harness errors.
All original author receipt bytes were moved after writers finished to
P2_power_raw/author_receipts/. Sealed manifests retain their original path prefix;
receipt_relocation.json supplies the mapping without rewriting historical bytes.

Five existing P0 inert source maps were recomputed and approved separately for
inertness, then checked file-for-file by root before adoption. No key/upload
allowlist expansion. Raw evidence is binary-exempt from Git newline conversion;
89 prerequisite receipts were independently checked byte-identical to fbd9d96.

## Fixture canonicalization after the reviewed implementation commit

Commit e6b7060 stores canonical LF. Original29worktree files were CRLF;
removing CRLF exactly reproduced those reviewed Git blobs. All original bytes
and Git blobs are archived in fixture_normalization.before.zip with per-file
hashes. A subsequent whitespace-only normalization changes five Git files:
trailing horizontal space/blank EOF removed, plus a two-line extractor output
formatter to preserve normalized regeneration. Original Python AST prefix,
C++ line content, backslash continuations, assertions and vendor notices remain
unchanged. Extractor syntax/regeneration and scoped diff-check pass. No broad
test rerun is claimed for this nonsemantic cleanup; the review addendum records
its equivalence check. Production source/target identity is unchanged.

## Acceptance limits and next work

HOST-TESTED and TARGET-COMPILED are software evidence only. No upload, reset,
MCU attachment, ADC/pin operation or motor run occurred. Last-known MCU image
remains inert QTR61d7a2d0. The probe never calls the driver at startup or in loop.
F091 inherited Bridge/loop-hook paths remain unqualified for runtime deployment.
SC-AJ's MSI automatic-calibration lock/history/frequency problem remains an open
GLOBAL runtime-integration blocker; source mode/readiness checks do not solve it.
Physical B5 accuracy within0.05V, supply/reference/pin verification, whole fault-
path tick WCET and all original human gates remain pending.

Next eligible software work is P2 B3's concrete bounded I2C4/MPU6050 transport.
P2_i2c_native_audit.md/raw provides actual register/ownership/error prerequisites.
Freeze its timing/filter calculation, finite transaction/fault budgets and
sensor setup/freshness policy before implementation. Do not invoke stock Wire's
unbounded path, count a repeated sample as fresh, or create a general bus system.
