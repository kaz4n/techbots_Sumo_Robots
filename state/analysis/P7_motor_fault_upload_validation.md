# D175 inert diagnostic uploader validation

IMPLEMENTED / HOST-TESTED only, 25 September 2026 Asia/Dubai.
Source and independent oracle frozen in commit67eccbc5; no upload, reset or MCU read.
Implementation e926b7ba5586475664b0541370e7cfb5c50e40d8dc8b47b18e35db3e0a0a25c1;
independent test bdc810cb1838692def32672f2777c27d9b27fa99823a331c945d7ca521fbc0fb.
The separate author used the public contract and frozen fixtures without reading
or executing implementation. Separate fresh-context same-model source review is
state/reviews/P7_motor_fault_upload_review.md, SHA1317cc4f; reviewer did not execute tests.

Exact commands, timestamps, output, exit statuses and12input pins are retained in
P7_motor_fault_raw/upload_freeze.json, upload_first.json, upload_legacy.json and
upload_file_limit_current.json. All scripts run under WSL Ubuntu Python3.12.3,
Python-B, TMPDIR=/dev/shm and PYTHONDONTWRITEBYTECODE=1. No board calls occurred.

| Suite | Actual result | unittest duration |
|---|---|---|
| New D175 contract |34/34PASS first execution|3.609s|
| Frozen upload_remote |55/55PASS|3.861s|
| Frozen upload_loader |59/59PASS|3.945s|
| Supplemental failure retention |3/3PASS|0.175s|
| Historical run02 ownership |19PASS/1FAIL|0.599s|
| Harmless inherited file-size copy boundary |4/4PASS|0.439s|

The one retained failure is test_run02_ownership.py:223: consumed run02 manifest
expects uploader23661c8a, while current D175 uploader ise926b7ba. Both old manifest
and assertion remain exact. Independent review confirms the actual old run is
consumed and the launcher still rejects changed source/existing ownership. This
is an expected historical snapshot mismatch, not an all-green suite. No test was
weakened, skipped or repinned; no fix/retry was attempted. This disposition does
not authorize the old run or waive acceptance of the new native caller.

New tests cover exact closed dynamic selection/raw ELF selector, schemas/source,
17file roles/three directories/14absences, detached bindings, nested static
instances, failure ownership, independent closing checks, timeouts/deadlines,
process-group reap and both stream boundaries. All12frozen pins remain exact.
No change to firmware, config, locked tests or historical run scopes.

Earlier read-only deployment_files01 observation confirms both deployment files
are29836B with distinct raw/packaged hashes. Six committed raw blobs match actual
bytes; the original CRLF raw stdout is intentionally preserved (diff --check
reports its carriage return as whitespace). Source diff itself is whitespace-clean.

Storage check upload_storage_check.json: zero owned RAM remnants; independent
bounded audit found zero new disposable candidates. Keep compact unique test and
file-observation evidence; no downloaded firmware, persistent build tree or new
package/cache. No previously denied removal was retried and no disk savings are
claimed. Next: the finite relocation/flash-bracketed capture profile described in
P7_motor_fault_capture_plan_notes.md, then independently reviewed native bindings
and one identified inert scope. D160 remains the last actual board upload.
