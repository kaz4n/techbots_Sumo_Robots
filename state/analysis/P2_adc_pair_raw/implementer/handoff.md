# D086 implementer handoff

2026-09-23. Objective: implement the frozen fixed A0/A1 native ADC contract using
the existing single owner and preserving the battery API. This directory records
only implementer evidence; independent pair tests, actual target compilation,
review, decisions and final closure are coordinator-owned.

Changed production scope: src/hal/power.cpp, private declarations/state only in
src/hal/power.h, and bench/p2_adc_pair_compile/{p2_adc_pair_compile.ino,
src/adc_pair_probe.cpp,src/adc_pair_probe.h}. Public API and config are coordinator
inputs. No tests, shared ledgers, application or decoder were edited here.

The opt-in profile guards PA5/DAC2 while the default remains battery-only. Setup
tracks five exact stages; an in-progress setup write admits only its old or
requested complete state for cleanup. Runtime tracks the selected single rank
and, only during its own write verification, the old/requested pair. Both reads
share one native conversion path, total100us acceptance,4096 polling bound and
the separate D078 bounded shutdown. Successful A1 reads alone increment the raw
result sequence. No PA5 write, rank restoration, reset or recurring calibration
was added. The probe only publishes a never-called exercise address in setup.

Checks: initial strict native compilation passed. Full original battery tooling
passed9 groups; its output was not redirected and execution overlapped development,
so historical_runs.json explicitly avoids claiming a final-source binding.
After ADRDY persistence was added, the three relevant native regression groups
passed28 cases/280 assertions against the final source. The historical observed
output copies are labeled reconstructions, not original raw process logs.
An additional fresh strict compilation of the final source is directly captured
in strict_compile_final.receipt.json and its empty stdout/stderr files.
No battery suite assertions were read or modified. git diff --check was clean.

Final implementer SHA256:

| File | SHA256 |
|---|---|
| src/hal/power.cpp | ee5022da57eabeacee174ceae5f299d5955604abc4d2196edf42a4c62adc3f87 |
| src/hal/power.h | 22dfc8aad43c164fbd1f078b2aa3f3e5377e8a314aede60ce19172b7f51fb94d |
| bench/p2_adc_pair_compile/p2_adc_pair_compile.ino | f7304fbd1b5e7cd7bb8228dbcbad36a96361571645d74de4256f0f0a2957af08 |
| bench/p2_adc_pair_compile/src/adc_pair_probe.cpp | 60bc43ddeea18bc2082c457fd95d8202ae08d861cf68af5d2dc95cdd761ffdc2 |
| bench/p2_adc_pair_compile/src/adc_pair_probe.h | e34a918e1e402bacb4be3b981e5636c1147319ce14431cfc46da078802f396f9 |

Limits: no board mutation, upload, physical ADC accuracy/settling measurement,
ownership-race proof, clock qualification, whole-tick timing, button decoding,
START/BOTH distinction or human gate. Next action: coordinator collects the
independent pair tests and fresh review, compiles the final source snapshot and
records accepted software evidence with those physical/integration limits intact.
