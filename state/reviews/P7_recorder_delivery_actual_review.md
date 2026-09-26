# D228 independent actual recorder review

Reviewed 2026-09-27. Verdict: **ACCEPTED FAILED-ATTEMPT EVIDENCE; DELIVERY FAILED**.
No open evidence-reconciliation blocker was found. This is not recorder delivery
acceptance, a physical qualification, a motor authorization, or a phase pass.
The reviewer read local retained evidence only and performed no native action.

The attempt is `377911abefabd094971ee6d089326604`, session
`3997245574426120340`, native HEAD
`004dc7cff534896a851901f9d7d0ba6066cae060`, source
`702ad99ee4f888c58de1715cb91512cb0a174a646d914db6ce9155489ffa63e8`.
It targets ADB serial `2629958581`, boot
`55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`, UID1000, static/default
`recorder.ino`, MATCH0/MOTORS_ALLOWED0. The owner is
`state/analysis/P7_recorder_delivery_raw/recorder-377911abefabd094/`.

The closed compile review checked all144 input bytes against the recorded native
HEAD's Git blobs and all109 staged entries, including the staged-only positive
session header. The source digest was recomputed. The compile used one query
and one compiler, finished in278.151 seconds, and passed all9 closing checks.
Native TLS, ELF initialization/layout, package and artifact identities passed.
The55,104-byte package SHA256 is
`91b6042a3f13e3650fc4b23892f88e69d4c0c56edebd6514662fa2d8cd8208c6`;
the101,736-byte ELF is
`a70f2e16187ff0bd30277f9bf9d1674ef53227ba3a7e791329cf7a9ddba1bfab`.
The checked `.data` copy and initialized BSS interval are retained in artifacts;
neither historical B4 addresses nor the entire larger BSS section establish
the current recorder's status addresses.

The run reached the matching fresh ticket's loopback TCP connection before its
single upload. Board monotonic connection time116607.289467084 precedes upload
start116610.350891329; uploader completion was116620.526903749. The uploader
reported UPLOADED, one attempt, a reaped child with returncode0, no timeout,
no first error and no postcheck errors. This establishes uploader success, not
MCU execution or router registration. Host and board wall clocks are not used
as a synchronized timing reference.

The native receive deadline was exactly900 seconds after its recorded start.
The terminal closed at117507350969483ns with reason TIMEOUT and
observed_byte_count0. The retained receive stdout and partial wire are empty.
The original remote TimeoutError remains in stderr, the child was reaped with
returncode1, and the host retained its CaptureError and partial error record.
Expected session is preserved; observed and rejected session are null. There
is no BEGIN, frame, event or END evidence, and no accepted capture. The
CONNECTION_METADATA error explicitly preserves the lack of END_OBSERVED.

All45 main transport receipts returned0. The4 separately owned receiver
children were all reaped: the receive child returned1 and the other3 returned0;
all secondary error lists are empty. Run closing_errors and
receiver_cleanup_errors are empty. The final artifact reply exactly matches
the original packet. This review also reconciled the principal hashes in
root_actual_closure02.json against the files and the recorded result fields.
The older36370b3b pre-upload failure remains a separate consumed attempt.

Principal evidence pins (SHA256):

- Compile result: `86168b9c0ce06b4a75e4c0df014f3b0a8081348576c294bc9302f5c8d4de0b3c`.
- Artifacts: `14bb6445447a6e2482b167e0dcca5090d92774589f6e26ae2e9a98aae538dc31`.
- Run result: `3165f29720060c545b6579326bb77118af9d34441fdcb8dba3dd20193a9876f6`.
- Partial error: `9753c16f74e3ccbc3963a0da3a6f90b2470c88f56eada68ef300ca6adf89d168`.
- Receive stderr: `0c29dd39584457b842dfc6b5a8b9633e0c43558d4a9dc305b91250acbc6388bc`.
- Receive outcome: `7e8a03e02754b613479a9d1e8c9e888990af208915b4f902cb1ec619a6196c2e`.
- Root closure02: `c953275f7240c1f1ada4ed605692493cdf17dfaa1ae2cfe7c096e87d3072d311`.
- Actual validation: `3374e89a735d5ae77a235da28b9e3bc9c621875c860afaf6248df9e8345596bb`.

The failure cause remains unknown. In particular, an established TCP socket
does not prove native UART registration/readiness, and an empty capture does
not identify a runner, scheduler or transport failure. The runner's possible
recording-plus-dump duration is about503 seconds, so the earlier240-second
no-data observation was not a terminal result. Preserve this current image
for D230's fresh file-only ABI and bounded passive status observation after
that source/host scope is accepted. No delivery retry, reset, upload, grant
change or PG13 change follows from this review. Physical hardware, timing/RAM,
sensor/motor performance and human gates remain unqualified.
