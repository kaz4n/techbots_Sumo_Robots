# D240 qualified application identified delivery

Host/tooling preparation only. No native app operation is authorized by this
contract. Firmware, default config, D103 inhibition and all locked tests remain
unchanged. After a successful export, ordinary reset/start is the existing
next-round path; reset never preserves RAM evidence or renews an image/session.

The additive CLI is `python -I -B tools/run_app_identified_delivery.py
--check-only|--execute --scope RELATIVE_JSON --reviewed-head FULL_HEAD`.
The input is the existing exact D227 scope, compile receipts, image bindings,
physical qualification and specific fresh STAND OK/RING OK authorization.
The initial route is the fixed identified ADB target 2629958581 with the existing
pinned Windows ADB executable and boot identity. No ambient route substitution.

The exact compiled config must have APP_DUMP_RECEIVE_STREAM_ID=1 and a positive
uint64 APP_DUMP_SESSION_ID equal to the first 16 hex digits of request.run_id.
DUMP_ENABLED, DUMP_SETUP_PHASE, DUMP_EXCLUSIVE_UART and DUMP_READY_PIN_OWNED must
be enabled and individually qualified by the unchanged D227 checks. Unknown
framing is allowed only through the existing identified receive mode. M0 still
requires all grants absent and therefore cannot admit this operational dump.
The ordinary D227 CLI retains its nondefault-session refusal. Its private
paired-caller opt-in adds no motor, physical, source or artifact exception.

Check-only performs local admission and reserves nothing. Execute exclusively
creates `state/analysis/app_identified_delivery_<16hex-session>`, writes a claim
binding the complete qualified request, scope hash and reviewed tool HEAD, then
creates run/. Session-prefix collisions share this owner. Every attempted
execution consumes the image/session, including failures before upload. There
is no resume, retry, reset or removal of consumed evidence. The compiled source
HEAD remains distinct from the reviewed delivery-tool HEAD.

The caller loads exact reviewed Git/current bytes for its code, this contract,
the D227 deployment modules, and the existing recorder receiver/dump/CSV modules.
It reuses ReceiverCommands, receiver_modules, arm_receiver, await_connection and
close_receiver from run_recorder_delivery.py. Only the private module's final
capture validator is replaced with the bounded application validator; no
recorder synthetic frame/event/timing assertions apply. The existing 900-second
receiver, two-command allowlist, bounded child/reap lifecycle, raw evidence and
independent closing behavior are retained. Connection observation precedes the
single existing qualified upload; CONNECTED is not a router acknowledgement.
Local claims/source/authorization are rechecked before upload and at closure.
D227's complete upload/prerequisite/owner/closing checks run unchanged, with its
upload evidence nested under the reserved delivery owner.

Successful delivery requires the original complete version-1 envelope, exact
session in every record, END counts/CRC and independent CSV validation. Reparse
the retained wire, compare every published CSV byte, verify source/config/target
declarations, and retain loss/interruption status without converting it into a
clean recording. SENT_UNCONFIRMED, upload success, reconstructed BEGIN, observed
END alone or a later reset cannot satisfy delivery. Published metadata always
keeps hardware_acceptance false and origin as a caller declaration.

Upload/receiver/local failures retain the first error and all available closing
evidence. The receiver still closes under its original bounded lifecycle after
upload failure. No new UART write, service reset, router restart, motion command,
automatic local gesture or compiler invocation is introduced. Actual local
service activation remains an operator/physical qualification boundary. The
host tests use synthetic authority records solely as fixtures.
