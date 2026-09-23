# Next P2 software task after D089 - read-only inventory

Implement the actual bounded IDLE log-dump owner/transport for P2 B8/B13/B15,
starting with source/API and lifecycle reconciliation, not another CSV formatter.
Read AGENTS,R2/R3/R4,BEHAVIOR B13/B15,active P2 prompt,D070/D073/D074,
recorder/recorder_csv APIs,existing tools,FACTS F091 and open SC-AJ.

Existing fixed RAM storage, attempt owner and CSV formatter are tested. Their
SEALED status does not prove current Robot IDLE. tools/dump_match.sh is absent.
MATCH permits only log dump while IDLE and control may not depend on Linux;
existing inherited Bridge hooks and native boundedness require actual installed
source verification. Do not treat an API's asynchronous name as a timeout proof.

Resolve how a final STOPPED attempt becomes legally dumpable without erasing RAM
or bypassing reset-only STOP. recorder interrupt/reset preservation is an object
lifetime policy, not physical MCU reset persistence. Preserve final receipts and
incomplete/loss fields; bind current state, fresh service intent, retained attempt
and transport session explicitly. No transport request may become a motion path.

Freeze precise bounded transfer/backpressure/cancellation/identity choices under
D051, then independently derive tests and implement the real path. Native API
unknowns block dependent calls, not safe host protocol work. No sensor request,
MCU upload or motor permission is implied. App scheduler, physical acceptance and
all human gates remain separate. This inventory is not a new decision or approval.
