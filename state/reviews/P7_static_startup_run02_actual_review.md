# Run02 actual evidence review

25 September 2026, Asia/Dubai. Same-model review using prior design/source
context. Local receipt/hash audit only; no new board operation, source change,
capture, reset or cleanup by this reviewer. Root-cause diagnosis is separate.

**Evidence collection PASS; running-progress qualification NOT MET.**
D160 executed once at reviewed HEAD e852e2a5655051043c1c6b729f1776baa18ed655.
Invocation71d73a7b records UTC00:39:42.173818-00:43:42.258103, exit0/empty stderr,
launcher c9588835, explicit run02 and that exact HEAD. Result SHA256
`b0a31acce4f69a2c695d6649201bc30225dcf02cfa2b2a792f48ae83555417b6`
is COMPLETED with one UPLOADED and one COLLECTED attempt, no first/postcheck
errors. These labels describe the command/collection outcome, not healthy startup.

Inputs3906f3bb bind scope78bb3e56, current4 scope files,16 dependency/receipt
pins and17 runner pins; all rehashed against current bytes. Expected board
2629958581 and actual packet identity UID1000/aarch64/boot
6d4aca1b-ac1f-4caf-b1ef-e127ce3956f6 agree. D144 source fcddbd8e and artifact
run f0220228320c4b2aa20c3e5e8264c813 remain the retained M0 packet.

Audited all14 numbered receipts: exact sequence and six command forms, correct
timeouts/board, transport returncode0, empty stderr and no transport exception.
The three groups of four file checks retain matching installed/prerequisite
outputs and packet source/file/identity records; only packet RAM/root/tmp free
resource counters differ. Final checks03ab47aa report no local/prerequisite
errors, query_attempts=compile_attempts=0, exact clean HEAD/committed scope checks.

Upload0005 (748edad9) matches the result; child returncode0, reaped=true and
timed_out=false. Its12.637s remote interval and capture's215.994s are within the
fixed budgets. Actual compressed payload/module hashes, argv identities and
projected run02 bindings match the reviewed intent/inputs. Capture0010 (f28ad306)
also matches the result; its intent binds the exact successful upload report
SHA97b8ed6f. No retry or extra reset appears in the recorded dispatch sequence.

Collector records18 reads/713656B and all four loader/sketch byte comparisons
true against the pinned references. Paired before/after flash chunk hashes match.
The2s separation wait measures2.000400453s. The four retained diagnostic raw_hex
values independently reproduce their read-record lengths and SHA256 values.
Full raw flash files remain at the fixed remote run02-capture owner; this review
checks the pinned collector/report and local hashes, without fetching or
independently rehashing those remote files. Local run02 packet totals333935B.

Both runtime prefixes are byte-identical: phase2 STOPPED, fault0 NONE, epochs3,
initialization_complete0, fresh0, missed_releases0, service_passes0,
next_release_us430099 and maximum_execution_us790. Both transaction prefixes
are byte-identical: phase1 IDLE, fault0 NONE, decision_made=finished=timing_valid=1,
started429103, decision429151, completed429598 and execution495us.
The pinned decoder correctly returns NO_RUNNING_PROGRESS with no malformed
sample errors; epoch_delta remains null because its RUNNING-phase condition is
false (static_capture.py:81-92), not because samples were missing.

This is negative evidence for sustained running and completed initialization.
Fault NONE is not a healthy-runtime verdict. The observed790us maximum and495us
transaction are retained diagnostics, not whole-robot WCET/clock qualification.
These prefixes do not identify the stopping cause, physical inputs, MCU-wide
quiescence, live memory margin or sensor/pin/motor acceptance. Source diagnosis
may explain them but must remain distinct from additional target observation.

No open material collection/receipt finding. D160/upload/capture scopes are
consumed; original D156 failure remains evidence. Preserve the negative samples
and all logs. No automatic retry, recovery reset, firmware change, production
static admission or physical/human gate follows from collection completion.
