# D184 actual inert diagnostic review

25 September 2026, Asia/Dubai. Separate same-model Codex reviewer continuing the
earlier read-only D179 admission inspection; this is not a fresh-context or
cross-model review. The reviewer did not implement or execute the diagnostic,
decoder, tests, transport or device operations. This new review is the only edit.

## Findings and verdict

PASS for consistency of the actual D184 execution, retrieved evidence and bounded
diagnostic interpretation. No open BLOCKER or MAJOR finding in this scope.

One interpretation correction: numeric motors::Fault6 is STOPPED, not HALTED.
The decoded gate separately has halted_=true. STOPPED is the expected successful
terminal result of MotorGate::halt(), not an observed callback failure.

This verdict does not resolve the earlier static full-app I/O fault. It does not
qualify the current main app, physical motor outputs, continuous operation, WCET,
free RAM, motor permission or any human phase gate.

## Scope, ownership and identities

The owner inputs bind reviewed HEAD133f77bc0f0539c24a2bf23b44f935687d08ff01,
scope e9fb5248b1e9719c6a5382704614fb8c4457c2ac8f2268207166c46bae425827,
ADB2629958581, boot55c386b9-fe6d-4388-a7f4-1d91e0bb49d8 and source
8f592937961a0c95b7cc4db88617169fcc9504644aa8b8b7dcf62f83c4c33f36.
Run identity is motor-fault-8f592937-run01. The existing D172 artifact uses dynamic
linking/default wait startup, MATCH0/MOTORS_ALLOWED0/SUMOX_MOTOR_FAULT_PROBE1.

All21 owner input hashes were independently rechecked against local files:
four scope files, nine frozen module/input pins, six preparation provenance files,
the committed scope and Windows ADB. No mismatch. This includes caller8b47b1d6,
uploader e926b7ba, capture support95b0344d and descriptor helper8ba9b190.

The six inspected diagnostic/MotorGate/native-port source files also match the
D172 compile_inputs_active01.json pins. Current decoder SHA256 is
f6e2fd36ee1db2a2079a75526072f45de3d6fceeccdfa18a641c62a720040dbe;
its required observed ABI is
822c917d32d5bbbcb209ebfad88fd347b516141f85351b84058b3a5ac4ab77a4.
That ABI binds the same source and raw ELFf9460a16, Runner2592B at BSS offset0,
BSS2632B/alignment8 and little-endian ARM32 scalar representation.

## Terminal execution evidence

native_inert_run01/result.json actually reports COMPLETED, one upload attempt and
one capture attempt. Its diagnostics match final_checks.json. All error arrays
are empty;27 recorded Git checks return0 and preserve the reviewed HEAD.

All11 distinct transport receipts return0 with zero-byte stderr. Their order is
three prerequisites, upload, three prerequisites, capture, three final
prerequisites. All six inventory identities match the scope field by field;
all three capability replies bind the same boot/UID1000 and true -B/bz2/Base85
checks. The stored upload/capture envelopes match their raw transport replies.
The durable capture intent's predecessor hash matches the actual upload envelope.

Upload reports UPLOADED, attempts1, child return0/reapedtrue/timed_outfalse and no
errors. Monotonic elapsed time is8.852545309s. Its Windows command is28984 units.
Capture reports COLLECTED and no errors, with20 listed reads totaling592640B.
Both numbers agree with the single-node plan18+2N and592248+392N. Monotonic elapsed
time is180.036757431s; the requested two-second gap measures2.000404374s.
Its Windows command is25236 units. Both commands remain below30000 units.

All four before/after loader/sketch comparison results are true. Relocation
before and after is identical: node536951012, BSS536959144 of2632B, one visited
node. Capture explicitly retains coherence=UNPROVEN; matching brackets and two
snapshots do not establish atomicity or continuous identity between reads.

Board wallclock values are unsynchronized with host time. Upload UTC and capture
UTC+04 timestamps are internally compatible after timezone conversion; this
review uses scoped boot identity, board monotonic times and host receipts, without
inferring an accurate host-to-board wallclock offset or changing any clock.

## Retrieved raw bytes and independent ABI interpretation

The file-only retrieval packet at
retrieved_inert_run01/0001-read-saved-results/stdout contains exact Base64 bytes.
Its before/after identities match the scope. Independently decoding Base64 and
hashing all four byte arrays gives these exact envelope/capture references:

| Saved object | Bytes | SHA256 |
|---|---:|---|
| upload_result.json |1887|df45977212a986465ecf660218ea91cec83fba3c41471e577c221fdbb498464c|
| capture_result.json |4674|5fa054e9ff681d4a79ba89c6b402d6563b9451d9994652efb8ca73cf1c9579bf|
|09-first.diagnostic.bin|2592|8805ee82be780f1d2b55acac0f9c21ae8c5fd313f2fb20ba48a1bc74b3665548|
|10-second.diagnostic.bin|2592|8805ee82be780f1d2b55acac0f9c21ae8c5fd313f2fb20ba48a1bc74b3665548|

Every field shared by each full report and its transport-envelope report agrees.
The saved upload/capture reports contain no standalone boot_id field; boot binding
comes from the reviewed owner scope, repeated prerequisites and retrieval
identities, not an invented report field. Other capture blobs remain on board
with their original names and hash references; they were not independently
downloaded/rehashed by this reviewer.

Selected fields were reconstructed directly from the literal ABI byte offsets
using little-endian scalar reads, independently of executing motor_fault_decode:

- Runner report at2312: phase3=COMPLETE, failure0=NONE, begin_called/begin_ok1,
  begin_fault0, halt_called1, applications4.
- Four result records at2336+56i: consumed/applied_valid1, tokens1..4, fault0,
  motors_enabled0, both duties0. All duration_valid flags are0; these are not
  measured application-duration or full-loop timing receipts.
- Trace report at44: count41, rejected0, clock_reads89, overflow0, timing_fault0,
  has_failure0. All41 stored calls have invoked/completed/returned/timing_valid1,
  requested_high0 and pulse_cycles0.
- Gate at2224: armed0, last_token4, halted1, fault6=STOPPED. Report halt at2560:
  fresh/attempted/inhibition_confirmed/timing_valid1, started416441us,
  completed416707us, fault6. This266us halt interval is diagnostic callback timing,
  not a physical-pin measurement or worst-case control-loop bound.

Both snapshots yield the same values and agree with decoded.json. Public source
motor_fault::Runner::stop explicitly requires the successful STOPPED halt before
setting COMPLETE; MotorGate::halt sets STOPPED when no earlier fault exists.
Inhibition confirmation records callback acknowledgement, as documented by
motors::HaltResult, rather than independently measured voltage or wheel motion.

## Evidence identifiers and consequence

- Native result: e462f2295535e06772559cb8c2c766c8655313ffde022100c82b8ffea956b248.
- Final checks: cc5997e222f61d0b7fd8e194141037c94b77ac47a944951909c1ae03d7d4dc74.
- Retrieval raw stdout:20973d6d1e54b4d5710a588122db4b2b684e2bc1b3ca00b449dc1b5379431d7b.
- Decoded artifact:a730691b79e991c794e276367a33943237b661ec9ab9a194e2f4ed157bbfdb6f.

The isolated dynamic M0 diagnostic completed four zero-output transactions and
terminal inhibition without an observed callback failure in its retained trace.
That narrows the investigation; it does not identify or repair the earlier static
full-app fault, nor compare identical whole-app startup/load conditions. Preserve
this consumed local/remote attempt, original failures and historical source pins.
Further native work requires its own bounded, reviewed scope.
