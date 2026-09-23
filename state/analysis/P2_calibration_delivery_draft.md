# P2 calibration delivery: draft for the next software change

Prepared while D104 actual bare-board observation runs. This is not yet the
adopted D105 contract, interface freeze or a claimed implementation. Read
P2_next_software_inventory.md and D089/D090/D101/D103 before finalizing.

Proposed scope: explicit-default-off SetupGrants calibration export, non-MATCH
only. Share the single existing DumpPort with recorder Transfer; no native owner,
remote command, UART reinitialization, config change or additional sensor grant.
Keep the exact existing qtr_cal::formatConfig payload. Runtime alone binds a
new actual calibration.committed bank to the current actual inhibited receipt,
ordinary IDLE/QTR_CAL service, fresh result token and real S..C lifetime. A
retained SUCCESS report or D103 service-only reset must never replay the export.

Proposed writer state: fixed report phase/reason/request-token/bank-version/
acknowledged-byte count plus bounded clock/offset/progress fields. Consider
regenerating the <=80-byte canonical payload on the stack on each bounded write,
from the same unchanged actual owner bank, avoiding another persistent buffer.
No assumption this fits the full-app loader; verify actual default/MATCH targets
early. Reuse existing DUMP_PAYLOAD_BYTES/DUMP_STALL_MS/DUMP_TOTAL_MS bounds.
Do not enlarge recorder storage, reduce its capacity, weaken safety or use an
unsafe shared buffer lease merely to pass the memory model.

Each real newly committed version is consumed once, even if Linux is unavailable
or context rejects it; no delayed auto-retry or export merely on re-entering a
menu. Active output remains confined to fresh inhibited ordinary QTR_CAL epochs.
Any loss of context, token/time continuity, same-version bank consistency,
receipt, source validity, Linux readiness or transport progress cancels once.
Runtime failure/STOP/reset aborts any active export. Never clear native poison.
Recorder and calibration writes cannot occur on the same tick or interleave;
apply old owner's cancellation before considering the new owner, and recheck
current native readiness after cancellation. Exact arbitration to be frozen.

Small wire choice: one canonical complete config line on an exclusively selected
bench output. A bounded receive-only helper rejects incomplete/extra/malformed
bytes and never modifies config.h or sends a command. Host capture provenance
must say that the line carries no firmware/version/origin authentication; those
require separate evidence. No new MATCH traffic or relaxation of dump_match.py.

Tests must start from actual eight-request Runtime calibration, consume the real
commit pulse and inspect actual Gate receipt/output/S..C; no private-state seeding
or caller-forged export request. Cover default/MATCH silence, source and bank
rejection, replay, partial/zero/invalid writes, full configured timeout boundaries,
wrap/regression, readiness, STOP/START/service-reset/cancel-once and genuine
recorder stream mutual exclusion. Preserve old dump bytes and physical limits.
