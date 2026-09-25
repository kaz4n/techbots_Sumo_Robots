# D177 inert actions actual review

2026-09-25 11:06 Asia/Dubai. Separate-context, same-model read-only reviewer; reused for repairs, not a cross-model or human gate.
Scope: frozen contract, D175/D176 public APIs, offline input provenance, actual source, independent oracles and retained root-run host receipts. No reviewer test, build, native or device execution.
Source: 58d32dda, inert_actions.py SHA256 8ffb65c0f1284f261ae1237bcf260e866176e83433a3538908780962513f1104.
Oracles: test_inert_actions.py bfffda215aaa04e45ec6b653f048ac9f6ca2c8dd95f2c83c9bb84e16b6d0492f; test_inert_actions_encoding.py 4a907281df3a6b4573c448a1ecd106804efde616aeb14a1ee1e25bde7d73c727.

- MAJOR (closed): original 9917fbf1 admitted contradictory capture read digests; contract1933c59c and inert_actions.py:304 enforce matching flash/relocation brackets and list confirmations. Snapshot digests may differ. Independent negative: test_inert_actions.py:730.
- MINOR (closed): first frozen source checked startup -B alone; action_first.json preserves 45 PASS/1 FAIL. inert_actions.py:83 now also requires current sys.dont_write_bytecode is True; the original assertion at test_inert_actions.py:442 is unchanged.
- MAJOR (closed): original production upload composition exceeded30000 UTF16 units (30598); action_composition_first.json preserves rejection. Contract2ac0f702 and inert_actions.py:180 add canonical Base85 fallback only after actual Base64 overflow, retaining identical BZ2 payload/source hashes and rechecking the unchanged ceiling.
- No open BLOCKER, MAJOR or MINOR findings in this scope.

Reviewed bounded canonical framing, all inline hashes before source execution, fixed identities/module registration, installed dependency read/import/recheck order, public dispatch, compact result binding and error retention.
Reviewed exact successful report shapes/counts/addresses/times, conditional capture only after checked upload, no retry, independent final checks, and finish failure precedence.
Verified six offline provenance files by bytes/hash,19 unchanged shared upload/capture pin records, and all three installed-module pins against retained observations and local source bytes. Historical observations remain preparation inputs only.
Verified all11 action_repair1_freeze.json source/oracle/input/dependency sizes and hashes against current files; original46-test oracle is unchanged.

Evidence b7736483: action_repair1.json records original46/46 PASS (0.320s) and additive encoding16/16 PASS (0.337s), both exit0, all11 pins unchanged, native_calls0. Root executed; reviewer inspected source and receipts only.
action_composition_repair1.json records Windows Python3.13.11 production upload28989 UTF16 units/Base85 and capture25231/Base64, both below30000, shell roundtrips true; source/input hashes match reviewed files.
Independent additive checks cover fallback threshold/quoting, identical payloads, both-too-large rejection, canonical aliases, bounded BZ2 framing, hash/order failures and unchanged dispatch/postchecks.
Original source9917fbf1, first frozen sourcee9481f5c, failure receipts838fa1f1 and first tested-source repair58d32dda remain retained; no oracle weakening or historical-scope repinning.

Limitations: host preparation only; current target bz2/Base85 availability, board identity, actual artifact admission, fresh native scope and motor-run authorization remain unprovided. No upload, reset, capture, physical qualification or phase gate follows.
Next: separately review fresh native caller/ownership/dependency pins and current prerequisites when the board is available; do not reuse consumed scopes.
Verdict: PASS for D177 host preparation.
