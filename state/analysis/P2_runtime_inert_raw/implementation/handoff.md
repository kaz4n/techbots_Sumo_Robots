# D104 inert Runtime implementation handoff

Objective: run one actual fixed Runtime with absent sources and all-false grants
for the unchanged 200 s MCU-clock window, then freeze truthful BOOT evidence.
Only the five files in source_freeze.json were implemented. Existing Runtime,
core, configuration, native owners, tools, tests and ledgers were not edited by
the implementation owner. No build, board operation or commit was performed by
this owner; target compilation and capture remain coordinator responsibilities.

The public Report/Diagnostics ABI and public method signatures are unchanged.
The pure port counts attempted callbacks, latches invalid or active requests,
and returns only real supplied clock readings. Runner checks actual completed
Transaction, receipt/token/chronology, absent inputs, EMPTY recorder, faults,
zero missed releases and exact setup/zero-write counts. A failure retains its
first cause and latest actual owner reports; a partial failed transaction is
not represented as a completed epoch. gate_fault prefers an actual fresh halt
report over the preceding application report. No abort or invented STOP is used.

The endpoint clock sample closes Runner timing after substantive checks/report
preparation. Endpoint validation/count/elapsed/duration bookkeeping and native
diagnostic publication are excluded. The native wrapper samples only real clock
callbacks, preserving D091's checked PSP/thread ABI and first metadata fault.
Initial and terminal diagnostics are the only publications. Stack invalidity
is a separate explicit diagnostic failure even when pure Runner is FROZEN.

Independent author reported the first normal and ASan/UBSan runs each passed
18 cases / 5,301,218 assertions, plus three compile flag refusals. A final rerun
was requested after the reviewed latest-halt diagnostic correction. Exact author
receipts are owned by the independent test author; source hashes are frozen in
source_freeze.json. Local git diff --check passed for the bench files.

Next action: coordinator compiles exact frozen sources using the checked probe
route; independent reviewer audits target constructors/imports/loader budget and
capture before upload. This implementation establishes no target fit, actual
load, physical inputs, full-app timing, historical stack watermark or phase gate.
