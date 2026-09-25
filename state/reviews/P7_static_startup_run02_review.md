# Run02 inert startup: pre-action review

25 September 2026, Asia/Dubai. Bounded same-model review reusing D155-D159
design, source and evidence context. Local read-only inspection; no test,
native execution, cleanup or new board measurement by this reviewer.

Reviewed plan SHA256
`c464f8a18ff7d9e9aede4cd189c1f10ca326dd0b2195778d8888c3df17690f0c`
and native_run02_scope.json SHA256
`78bb3e564476d91f238f4ff6ecb431e70ac33bb265c7480326ae8481bf555b77`.
All four scope digests match the exact launcher, ownership tests, contract and
D158 review; launcher c9588835, tests84503c31, contracte53a3273, reviewbda4208e.
Their closed run02 profile is consistent with the scope schema and file set.

**PASS for this single inert run02 scope; no open material finding.**
The coordinator must record D160 and commit this concrete scope before launch;
--reviewed-head must equal that actual clean scope-containing HEAD. All normal
fresh local/source/packet/installed/F166/identity checks remain mandatory.
This review neither bypasses admission nor asserts a currently observed boot.

Target ADB2629958581, UID1000/aarch64, expected boot
6d4aca1b-ac1f-4caf-b1ef-e127ce3956f6. Operation static-fcddbd8e-run02 retains
D144 artifact run f0220228320c4b2aa20c3e5e8264c813 and source
fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2.
Rehashed receipt0017 (3c8cc9df): successful static compile, exact source/build
paths, C and C++ flags -DMATCH=0 -DMOTORS_ALLOWED=0. The unchanged raw selector
93080B/bd03c2e7, flat sketch93096B/5f08afe0, packaged loader2303728B/39d4a4fd
and ELF-derived reference263680B/e9322826 agree across retained bindings.

D158 review retains original failures and verifies227 aggregate host tests.
Composition8bc2abe2 uses exact final source,16 dependency/receipt pins plus17
runner pins, rechecked here; six allowed forms and zero native dispatches.
Upload28751/capture25436 UTF16 units remain below30000. Its null optional
source_manifest projection is not a new manifest/count or target measurement.

Clean-path sequence remains four file checks, upload, four checks, capture,
four final checks:14 dispatches. Upload includes the fixed recipe's intrinsic
loader/sketch programming, resets,100ms wait and0xCAFFEEEE activation write at
0x40036400; no separate reset/recovery/rebuild/install is introduced. Remote
upload180s/child120s/+5s reap, host195s; capture600s/read30s/+5s reap, host630s.
The upload-only file cap2303728 permits the retained loader; each accepted
stdout/stderr remains below1048576. Passive capture stays18 reads/713656B,
full flash brackets and >=2s sample separation, with no halt/reset/write.

D159 resultfb99a50a records removal of the exact reproducible1MiB fragment and
empty parent, and its scope is consumed. Uploader:266-270 still freshly checks
/tmp/remoteocd absence and conflicting processes; cleanup is no admission bypass.
Run01 scope c7447815 and failed resultfff23bd0 remain unchanged and consumed.
The exclusive local native_run02 path was absent at review; remote owners are
the fixed run02-upload/run02-capture paths, subject to their fresh claims.

Only strict known upload success plus clean intermediate checks admits capture;
failure/uncertainty suppresses it, preserves evidence and ends this scope.
Independent permitted final checks remain. Existing user-reported bare-board
permission and D051 cover this inhibited packet only. No motor-capable run,
sensor/pin acceptance, production static admission or physical/human gate is
granted here. Collection status remains separate from decoder progress/fault,
live memory/WCET and startup qualification. Actual results need separate review.
