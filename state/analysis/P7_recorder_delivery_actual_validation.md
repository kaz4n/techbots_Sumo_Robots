# Identified recorder native attempt: upload passed, delivery failed

At native source HEAD `004dc7cff534896a851901f9d7d0ba6066cae060`, attempt
`377911abefabd094971ee6d089326604` compiled the motor-disabled static/default
recorder and made one upload. The source hash is
`702ad99ee4f888c58de1715cb91512cb0a174a646d914db6ce9155489ffa63e8`;
expected session is `3997245574426120340`.

Compilation passed in 278.151 seconds: one query, one compiler, 28 transports,
and all nine closing checks. The checked package is 55,104 bytes. One upload
returned UPLOADED with a reaped successful child, no postcheck errors and no retry.
The receiver observed its matching board boot/ticket TCP connection before upload.

The run then FAILED after 927.365 seconds. Its native receiver closed with
TIMEOUT after the 900-second deadline, reporting **zero observed bytes**. The
retained wire is empty; no session, BEGIN, frames or END were observed. Expected
session remains recorded; observed/rejected identities are null. The receiver's
original TimeoutError, host CaptureError, partial metadata and all raw streams
are retained. No loss-free recording or successful UART delivery is established.

All 45 main native transports returned zero; the separately owned receiver
preserves its failed exit. Final source/dependency/artifact checks closed with
no closing errors. This is a failed delivery with preserved evidence, not a
passed recorder test. The corrected D228 fixed-ADB path did reach receiver/upload;
the older 36370b3b attempt remains a distinct consumed pre-upload failure.

The latest uploader-reported firmware is this inhibited recorder, replacing
D221 B4. Actual runner phase, native UART status and root cause are unknown.
Retain the image for a fresh source-bound file-only ABI and minimal passive
status read (D230); no reset, upload, receiver retry or grant change is justified
by an empty capture alone. New upload scratch remains retained. BOARD ONLY
provides no motor/sensor qualification, physical timing/RAM or human phase gate.

Evidence: `P7_recorder_delivery_raw/recorder-377911abefabd094/`, including
`root_actual_closure02.json`, compile `result.json`, `run/result.json`, receiver
streams and the `.partial` capture. Independent actual review is pending.
