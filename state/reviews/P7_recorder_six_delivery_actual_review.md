# D237 actual six-store delivery review

**ACCEPTED FAILED-ATTEMPT EVIDENCE; DELIVERY FAILED.** The transport retained a
complete-looking record body through END, but its required opening envelope is
absent. The unchanged receiver correctly refuses the stream. No repaired capture
or full-delivery acceptance is produced by this review.

Evidence owner is
`C:/Users/narut/AppData/Local/Temp/sumox-recorder-six-native-20260927/state/analysis/P7_recorder_delivery_raw/recorder-771c04943d4c4a75`.
Its durable MAIN copy is the same relative state/analysis owner; all 266 copied
files (2514245 bytes) independently compare byte-for-byte to that closed source.
Native HEAD `1b2af246cd88e6207e846ee340f8c4e46a5bb980`, attempt
`771c04943d4c4a759055d794fa4b706e`, session `8582740024591403637`, source
`289300a4be9547cd294dc1f753bbe17a429d16776c46467fec5417b1290f4ffc`.
The static/default recorder.ino has MATCH=0/MOTORS_ALLOWED=0; its checked
55376-byte package SHA256 is
`3b4812a7a57ec964437d6d1048f96724e3fed5d0a3f9419acd26adbcd5e70a5d`.

The separately accepted compile review reconciled all 145 input pins to native
Git/current bytes and all 110 staged files to this source digest. In the saved
run, pre-upload and closing source maps still exactly match the staged map, and
both artifact replies exactly match the accepted compile packet. The native
worktree and historical image identity remain distinct from later MAIN commits.

## Actual ordering and closure

The fixed ADB target is 2629958581, boot
`55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`. The fresh ticket equals the attempt.
Receiver TCP connection was observed at monotonic 123193.417953255 s, before
the one upload started at 123195.586211294 s. The upload finished at
123205.779197306 s, status UPLOADED, attempts=1, child reaped with returncode=0
and timed_out=false. Its first error is null and postcheck errors are empty.
TCP connection alone does not establish router registration or route readiness.

All 45 main transport receipts return zero with empty stderr. All four receiver
command outcomes have returncode=0, reaped=true, no first/secondary error and
empty stderr. Closing identity, source, installed-input and artifact operations
complete; the two closing checked children are reaped with returncode=0 and no
timeout. The run preserves empty closing_errors and receiver_cleanup_errors.

The receiver starts at monotonic 123193382203601 ns with a 900 s deadline.
Its terminal record closes at 123550131481081 ns, after 356.749277480 s,
reason END_OBSERVED, observed_byte_count=607448. The claim, connection and
terminal identities agree. This is not the earlier empty-stream timeout. Root
reported the outer run closed with exit 1 after approximately 375 s.

The host first error is CaptureError/BEGIN, `Missing exact version-1 envelope.`
Capture and capture_acceptance are null; framing_clean remains UNKNOWN.
The partial error preserves expected_session=8582740024591403637 and
observed_session/rejected_session=null: the parser refuses the first line before
admitting any opening-envelope session. Later matching body sessions do not
retroactively satisfy that admission.

## Entire retained wire, independently examined

The parser's partial wire.txt contains 578 bytes, exactly the first line of the
larger retained stream. receive_2/stdout contains 10028 strictly decodable base64
lines. Concatenating their decoded bytes in memory gives 607448 printable-ASCII/LF
bytes, SHA256
`2bac3f47d94bc8eadaa6619d81fc9f6dd122c73a0c45bf795e30ba4029b82e3d`.
That length agrees with the receiver terminal; it ends in LF. No original evidence
was modified and no decoded or repaired capture was published.

The received sequence is SH, SR, FH, 5001 FR, EH, eight ER, END. There is no
SUMOX26_DUMP occurrence anywhere. All received records identify the expected
session. Exact CSV headers and every numeric/raw-hex row parse under the existing
row validator. Frame and event ordinals are contiguous. END declares 5001 frames,
eight events and CRC 2865663826.

The retained summary reports epoch 70, SEALED phase 3, mode 1, go_seen=1,
incomplete=0, all declared loss fields zero, 194901 ticks, zero overruns and
tick_max_us=315. All frames have valid packing, mode 1, zero duty and their
expected 40 ms ordinal coverage through 200000 ms, within the caller's existing
2 ms allowance; maximum frame tick value is 315 us. The eight event
type/detail/value tuples and modular times match the declared synthetic scenario,
including the 5.1 s GO and 200 s terminal recording event. These facts describe
the received body; the missing envelope still prevents accepted stream integrity
and provenance. They are not physical sensor or WCET qualification.

CRC of the received body before END alone is 1211688594, which differs from END.
For diagnosis only, the source/config and retained summary imply this missing
60-byte opening line:

```text
SUMOX26_DUMP,1,8582740024591403637,70,1,25,5001,4096,5001,8
```

Its final LF is part of those 60 bytes. An in-memory counterfactual calculation
over that prefix followed by the unchanged received body produces CRC 2865663826,
exactly the retained END value. This supports a missing initial envelope with an
otherwise internally consistent body. CRC agreement is not proof of where the
loss occurred, MCU transmission completion, router readiness or successful
end-to-end delivery. The prefix was not received and cannot be promoted to
observed evidence. No retry or parser relaxation follows from this review.

## Principal receipt pins

- run/result.json, 22198 bytes:
  `1e4039ad8b74cd6d6cf18c12b3c34ea3bbdf2fc69233867f7c638a7aed998cc7`.
- run/receive_2/stdout, 851624 bytes:
  `b87552c4447db72937b947c41a16995427272ab77a291e38af1efdeb8010c55b`.
- run/receive_4/stdout, 1844 bytes:
  `1062492518b51d37198d16077092efbd90bb63429635b56226bfa525ec44f0c5`.
- Partial error.json, 41033 bytes:
  `2c8b5a492c31983d1b60372772beb178232cda6598b9d60bfb4a34030c135079`.
- Partial wire.txt, 578 bytes:
  `d5c255a0008b9cefe9ae5f01d3e6a8b4dfa5c24ae9a801d65444d9d80cdee42d`.

Fresh passive status observation can distinguish the MCU's retained terminal
state without altering this failed capture verdict. No original native failure
or cleanup cause is inferred here. Reviewer performed only local evidence reads,
hashing, base64/CSV decoding and CRC calculations; no test rerun, native command,
source change or wire repair. Only this actual-review report was written.
