# D114 one bare-board ADC observation: d114-ui-adc-01

Scope: one reviewed default-startup MATCH0/MOTORS_ALLOWED0 diagnostic upload to
ADB serial2629958581, then one passive readout. User freshly reported the UNO Q
connected alone and explicitly permitted testing. This is human-reported setup,
not independently verified wiring. No sensors, motors or other parts requested.
No STAND/RING permission, physical gate or calibrated ADC claim follows.

The exact96-file staged source is
`396bcc45fbaf30d38b170bf0c0063c555d5e88cdad512829b86a52ffede18642`.
Firmware sources committedbfd4f25; the upcoming software commit supplies the
reviewed capture/guard/manifest. ELF is
`76e23fe03631d5cc2144578d35ca78b9bafd44158e0d18b2ab026922e4c9d05b`,
ZSK is `567fb90da6965cf74efc5ac2221e543d6d2150e3bf70ddae3e2346e6646c7fb9`.
The guard requires a fresh checked compilation and these exact artifact hashes;
cached passive-readout inputs cannot serve as the uploaded image.

Reviewed capture sourcef4b3db26 uses unchanged helper885c4e42/config89d16a28.
Guard1aa109a2 and boardd1fda964 bind an exclusive one-attempt record. Independent
capture42 and guard22 suites pass; prior145 policy regression also passes.
Capture/guard reviews are separate reused same-model contexts, not human gates
or cross-model reviews. Exact pins and limitations are in their review reports.

Before any upload, transfer only those three capture files to exclusive board
Linux folder `/home/arduino/sumox26-capture-tools/ui_adc_d114_run01`, retaining
argv/status/hash receipts. The already prepared input folder is
`/home/arduino/sumox26-capture-input/ui_adc_probe_396bcc45fbaf30d38b170bf0c0063c555d5e88cdad512829b86a52ffede18642`.
Its exact two files were copied/hash-checked from the earlier checked compilation
without MCU operations. The reviewer then binds all eleven run-contract files,
and the root records that approval hash plus completed software commit.

Execute once, with fixed ADB transport/serial/dedicated remote root:

```
python tools/board_tool.py flash bench/ui_adc_probe --run-ui-adc-probe d114-ui-adc-01
```

Any staging/compile/identity failure prevents upload. Once the exclusive upload
attempt exists, no second upload, reset or retry is permitted under this run.
The one upload includes its normal loader reset; no independent reset is issued.
Return/timeout/error receipts remain actual. A failed or uncertain upload stops
this plan; later work requires a new reviewed scope rather than deleting claims.

After a successful upload only, invoke the staged capture once with the exact
artifact folder and output `/home/arduino/sumox26-capture/ui-adc-d114-run01`.
Record the outer command, status and all original output. The finite read sequence
has at most22reads/588016bytes/26commands, with30s/command and600s overall; use
a620s outer process bound. This only uses the pinned nonhalting MEM-AP config:
no MCU halt, reset, function call, memory write, peripheral query or UART command.
The full deployed loader/sketch and descriptor mapping bracket both Runner reads.
Pull original capture files once, retaining byte hashes and exact board report.
On failure retain partials and stop; do not retry the collector.

Interpretation: VERIFIED collection plus COMPLETE128 means the finite diagnostic
was collected consistently. Frozen FAULT is a collected failure. NONTERMINAL or
unequal/invalid bytes remain explicit unsuccessful diagnostics. Unconfigured A1
windows stay UNCONFIGURED; floating bare A1 values are not button voltages or
electrical accuracy evidence. SC-A/SC-AJ, calibrated time, physical buttons/STOP,
full-app RAM/WCET, other P2 hardware and all human gates remain open. Separate
post-run review and immutable raw evidence precede the measured-fact ledger.
