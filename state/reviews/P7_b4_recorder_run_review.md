# D219 capture-only caller source and host review

FINAL PASS, 2026-09-26. Separate implementation/oracle review using the same model and reused reviewer context; this is not fresh-context, cross-model or human approval. I inspected saved source/data and receipts only, with no subject import, test execution or native call. This review does not admit a native capture.

## Exact accepted inputs

Paths below use RAW = state/analysis/P7_b4_recorder_run_raw.

- Contract: 13808 bytes / b205280afdc8b4ce4be2b6dea498e1494b50d698bf4bea266cafa4199a716590; plan02.json: 11356 / d48af05673d47d787b4eeaa3f1301f2dbc8b7e6ed9a3555401ade30d21f39604.
- tools/capture_b4_recorder.py: 22155 / d5042c4d13337b2cd2c4599b88af92fbb15c566601750ca82ca07b8f1ae50349; RAW/actions.py: 25620 / 59f1b3ba14e87796f5eafaa79f4da60e88c0d52560d8ba334ffb92fd7d18c336; derivation01.json: 35906 / 7e28d76665a56c60f31f68f7b2eed6b2943339af3f58cd26a130659629054512.
- Corrected tests/tooling/test_b4_recorder_run.py: 33384 / 145395a57cba25e557b013ad955b8099eb6d122395ed9ff6c71dfbabfb5a486f; run_oracle02.json: 12863 / f7cb7b94863b4240ba2b3fb60bac49a39033e805974a425fd17ad99caa7c921e; run_oracle_repair02.json: 3286 / c2d02c033ead8404543d36c787a4d90ebfeba456907d39f7409efcb710a58158.
- run_coordinator_freeze02.json: 28864 / 664728b08215130945ba41e0a5ecd68ade8fc0d70c3dacb98f36f50b4004424c; run_host_closing01.json: 5657 / 3553f619bcbdf692a1d2c0c5c046bd039bbed5e680920e726ec4910165d5f3b5.

## Source and oracle findings

No material source finding remains. All 164 derivation inputs and both subject identities matched. The single import substitution reconstructs the complete 24795-byte D212 private projection, retaining all named 23 inherited method spans; all ten bootstrap helper functions equal their accepted literal ancestor. Checked local ownership, clean HEAD, fixed scope/input hashes, checked ADB, dispatch intents, bounded transport, independent closing and earliest-error machinery remain in force. The reviewer initially attempted literal_eval on D212's computed bootstrap assignment; that data-only extraction refused. Following its source-declared literal D195 ancestor verified the exact unchanged functions without execution.

The current binding is the fixed B4 source/130-input manifest with ordinary 104-file mapping, current artifacts/ABI/entry, accepted D216 layout and D218 capture/decoder. It stages only the pinned adapter under the fresh capture-specific owner. Capture framing has only helper/support roles; the installed p0 source is descriptor-read with its exact pin. Complete snapshots precede private execution. Bootstrap adapter/parser closing checks and root closure retain failures; durable-only evidence never becomes a returned successful capture.

Success requires exactly ten dispatches: claim/push, three initial prerequisites, capture, retrieval and three final prerequisites. Limits remain capture630s, other60s and 30000 Windows UTF-16 units including NUL; measured data-only command sizes are 25672 and 14427. Capture/retrieval intents are consumed once. No upload predecessor, firmware write, reset, halt, privileged action or retry was added.

Retrieval is restricted to capture_result.json and twelve fixed SRAM leaves. Its pinned helper performs 27 logical reads and two identity observations, including all thirteen closing reads. Local packet validation enforces exact keys, order, typed identities/sizes, canonical base64 and actual hashes before unchanged D218 decoding. Failed capture, retrieval or caller closing cannot reach export. Raw leaves and the canonical returned envelope are saved exclusively; export references avoid duplicating the assembled owner. D216 refusal remains distinct and suppresses CSV; D218 bundle refusal fails the sequence. All unknown-origin/coherence/common-attempt/transport/hardware flags remain conservative.

The ten focused methods exercise current/stale source and scope admission, exact framing and inherited bodies, at-most-once intents, order/first errors/closing, changed retrieval paths/bytes/identity, returned versus partial/unattributed reports, exact CSV/raw preservation and exclusive local output. Controlled endpoints are host fixtures, not real board observations. Original Linux01 had nine passing methods and one sequence failure: its fake successful export omitted required bundle_status. The caller correctly refused. Original test/oracle/receipt remain preserved; only that fixture method changed, with all outside bytes identical. The corrected positive supplies PASS and the new REFUSED case requires FAILED, retained export, first/postcheck errors and one export/finish. No product bytes or rejection rule were weakened.

## Host evidence and remaining boundary

Independently reconciled all twelve saved original/corrected receipt/stream identities, twenty corrected ordered outcomes and all 184 current coordinator pins. Linux02: ten PASS, 12.856s inner / 24.3506005s outer. Windows02: ten PASS, 2.8092686s outer. Both returned zero with empty stdout, no skips/timeouts and unchanged freeze/inputs. Windows fixture temporary directory is actually empty; no independent Linux remnant inventory is claimed.

Accepted source/host preparation only. Before any native use, the separately reviewed committed scope/prerequisite union must bind this final review, corrected test, oracle02, repair and host closure; the retained oracle01 scope role alone is not the corrected host proof. Native execution, actual retrieval, physical inhibition, firmware commissioning, atomic coherence, lifecycle completion, WCET and phase acceptance remain separate. All writes to this review stop at seal.
