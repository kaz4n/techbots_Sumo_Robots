# D237 missing opening envelope: bounded source analysis

2026-09-27. Read-only source/evidence investigation under D051; this file is the
only work product. No native command, firmware change, recovery action or test
run was performed by this investigation. Root subsequently reported D238 closed
PASS: Runner/Transfer SENT_UNCONFIRMED, failure NONE, native OK/inactive/unpoisoned,
first_failure NONE, 607508 submitted payload bytes, 5001 frames/eight events and
CRC2865663826. Recommendation: make one fresh attempt with a new owner/session and the accepted six-store
firmware, using the existing scoped scratch cleanup and receiver-before-upload
ordering. Leave the router running and retain the exact envelope checker. This
is an empirical delivery attempt, not an assertion of clean router framing.

## Observed failure and source boundary

[D237 actual review](../reviews/P7_recorder_six_delivery_actual_review.md) accepts
the failed-attempt evidence, not delivery. The original receive_2/stdout decodes
to 607448 bytes (SHA256
`2bac3f47d94bc8eadaa6619d81fc9f6dd122c73a0c45bf795e30ba4029b82e3d`):
SH, SR, FH, 5001 FR, EH, eight ER and END for session8582740024591403637.
The opening 60-byte envelope is absent. Only a diagnostic, in-memory insertion
of the source-implied envelope makes CRC2865663826 agree with END. That line was
not received, and the original BEGIN refusal remains correct. TCP connected
before upload; this alone does not prove monitor registration at the first write.

`src/hal/recorder_dump.cpp:181,216-224,269-316` starts at BEGIN, advances to SH only
after positive native payload completion, and includes BEGIN in CRC. A 60-byte
BEGIN fits in one64-byte payload. `src/hal/dump_uart_unoq.cpp:24-27,283-307,327-353`
wraps each payload as one MessagePack notification to mon/write, with a13-byte
prefix followed by D9,length,payload. Native progress requires all packet bytes
submitted and TC observed; it is not a Linux acknowledgement. END advances to
SENT_UNCONFIRMED. `bench/recorder/src/recorder_transport.cpp:22-25,101-102,155-161`
makes that terminal: later polls return without another dump write. The sketch
only invokes begin once and poll thereafter (`bench/recorder/recorder.ino`).

## Pinned router mechanism: plausible, not established cause

The historical installed binary is version0.10.0, SHA256
`3eacd38a9c813209f6985951869105600824e4f7c54a1111a8d48ef094cc1a19`.
The cached source receipt pins v0.10.0 to
`b92ba75a62781a7b79d4bc0429a499542f939233`. This is version/source evidence, not a
reproducible-build proof or a fresh observation of the running decoder.

Cached `P2_dump_raw/native/router/msgpackrpc/connection.go:162-261,292-320` creates
one decoder per connection and retains it after invalid-RPC errors. It has no
MCU-reflash boundary. It skips complete MessagePack values when rejecting a
malformed packet. The [pinned notification dispatcher](https://github.com/arduino/arduino-router/blob/b92ba75a62781a7b79d4bc0429a499542f939233/internal/msgpackrouter/router.go#L176-L214)
calls internal mon/write without returning an acknowledgement to the MCU.

Conditional byte walk for the previously recorded D233 offset7:

1. If exactly seven old bytes reached the continuous decoder, they are
   `93 02 a9 6d 6f 6e 2f`: array3, notification2, string9, `mon/`. The decoder
   still needs five method-name bytes.
2. The new BEGIN notification's first five bytes fill that old string. Its next
   byte, ASCII n, is not a parameter array and is skipped as an invalid RPC.
   The remaining ASCII /write bytes are skipped as non-array values.
3. The new parameter-array byte91 is rejected as an RPC array of length1;
   skipping its one element consumes D9,3c and the entire60-byte BEGIN string.
   The next notification, containing the start of SH, is at a valid boundary.

This yields exactly the observed first-envelope loss without a firmware omission.
It is not proof: the D233 offset counts TDR submissions, not bytes demonstrably
shifted into Linux; its cleanup readback failed. Actual prior decoder state,
buffered bytes and connection continuity were not captured. Other partial
prefixes and upstream loss remain possible.

Cached `router/internal/monitorapi/monitor-api.go:46-57,117-158` adds accepted
sockets to a map and writes each decoded payload to its current clients. No
client means silent loss; write errors close that client, and there is no replay.
There is no BEGIN-specific filtering. Missing registration at the first write
or an unobserved transport error are alternative boundaries, not proven causes.
`mon/reset` closes monitor clients; it does not reset the serial decoder.

The three cached files were rehashed against router_sources_receipt.json:
connection.go `e812eb4f2e7dd1f3ffeb55545096cfee3f0c04062c907290158267c5aa3282aa`;
monitor-api.go `23ed289c4a4e2ffe3d09ec88b0b9ef10bca390a6b5534dd2a9a95af56ba67663`;
main.go `a19b4188b6b1301385ac95dff269221ba18a19ba27795f49b933c03f1ec45ed8`.

## Minimal next action and limits

A complete received body through END supports the inference that the decoder
processed complete notifications after the lost BEGIN. If passive state also
shows Runner/Transfer SENT_UNCONFIRMED and native OK/inactive/unpoisoned, the
source has no subsequent write to create another partial packet. This supports
one fresh unchanged-six-store attempt without first disrupting the router. It
does not certify the decoder or input queues are clean; only the fresh, complete
received envelope/session/count/CRC validation can establish delivery success.
Root owns the new decision, exact scratch cleanup, fresh identity and execution.

Do not treat MCU reflash as parser recovery. The existing
[native audit](P2_recorder_bench_native_audit.md)
records service-stop GPIO actions that reset the MCU. Serial close/open creates
a new decoder, but main.go:180-269 acknowledges open before actual open succeeds,
and the pinned serial implementation does not prove flushed input or completed
RX-DMA. These actions therefore add work and unknowns without establishing a
cleaner admission here. No restart, close/open, padding, duplicate BEGIN,
receiver relaxation or repaired D237 capture is recommended by this analysis.
