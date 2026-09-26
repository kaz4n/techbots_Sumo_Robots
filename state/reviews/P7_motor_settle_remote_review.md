# D201 fixed remote adapter fresh-context review

26 September 2026, Asia/Dubai. PASS for source and host preparation; no open
material finding in the remote adapter. Reviewer `/root/settle_run_review`
read source, contracts, independent oracles and saved coordinator receipts,
and performed local static/data comparisons only. No subject import, test
execution, device call or native action was performed by this reviewer.

| Input | Bytes | SHA256 |
|---|---:|---|
| P7_motor_settle_remote_contract.md | 10744 | 6d245a4e1f0426d5ed54b1ca47d124643ba9b2e3b6c86975294ba6efcd641dd3 |
| P7_motor_settle_run_raw/remote.py | 11343 | 577f2f17ae532db1e21644868b624d0d8a903771309a39b0b3488f8ae4f98cb0 |
| test_motor_settle_remote.py | 7444 | 0b1977444737694e8b39e5d712bd7766bd1db4d6073bf582cbed9e960b4f38b5 |
| capture_binding01.json | 24233 | 0a9d4a6af736ff96efa3b9213696f4369cb861e07996e594ebce00c996e39619 |

The reviewer independently reproduced all eleven ordered, count-checked byte
substitutions from original D195 remote.py (11357 bytes, 98b0f5394d64f61178277f701adb81eece3d5f136ea84a8c5fb30534a5b241db).
The resulting bytes equal the current source exactly. No lifecycle, predicate,
native dispatch, error handling or dependency guard differs beyond the fixed
metadata, single window tuple and byte accounting authorized by the contract.

The unchanged checked upload/capture/helper dependencies retain private module
loading after fixed-role and hash checks. Adapter import defines constants and
functions only. The static/default image is bound to source117cc0e7, raw95504
and package95520 bytes; the installed loader and capture configuration pins
remain unchanged. The fixed profile preserves mandatory /tmp/remoteocd absence,
UID/boot checks, every installed-file and excluded-override check, exclusive
output ownership and Python-B. There is no cleanup, sudo, retry, reset option or
arbitrary source/profile/address facility.

The six windows agree with current observed ABI: trace2128, report1168,
runtime600, transaction504, settle28 and gate88, in that order. The separate
settle report is at537121768. Only the prior live PreviousTick48 window is
replaced; Report.before_abort.previous remains within the1168-byte report.
Both samples total4516 bytes. The26-entry plan requests727432 bytes with five
loader chunks and two sketch chunks on each side, twelve SRAM snapshots and
four complete flash comparisons at4,6,20,25. The new sketch tail is29984 bytes.
Remote/action layers retain bytes and do not infer typed state or atomicity.

The inherited30-second pause occurs once after initial flash comparisons and
before read7; the two-second pause occurs once before read13. Their checked
clock, strictly sufficient budget, short/throwing wait, partial evidence and
unchanged600-second origin behavior remain intact. No SRAM read follows an
unsuccessful initial pause. Success still requires both waits, all flash flags,
twelve snapshots,26 reads/commands, exact byte accounting and no first error.
Child caps/reaping, stream bounds,180-second upload budget and closing checks
are unchanged. A final descriptor-close exception can propagate after the
inner durable result has been saved; the outer caller must retain failure and
never upgrade an unattributed durable result. The historical limitation is not
silently strengthened by this review.

## Independent first host evidence

The oracle preserves all42 D195 methods through explicit, checked fixture
metadata projection and adds three current-source/plan/stale-binding methods.
All historical assertion bodies remain, including clock and sleep failures,
flash mismatch, process/file/owner refusal, child deadline/reap/stream checks,
partial reads and first-error persistence through closing failures. The new
cases compare the exact eleven-step source derivative, current window order
and accounting, and refuse stale source/package bindings without mutation.

Native independent freeze67948 bytes / 2d636ae45fb949c78df7fe9dda2259342e70909258e60e3661cb83d0a086af00
records pre-implementation author isolation. The reviewer independently read
and hashed all251 frozen inputs and all256 coordinator inputs; all matched.

| First receipt under P7_motor_settle_run_raw | Observed result | Result SHA256 |
|---|---|---|
| first_remote_linux01/result.json | 45 PASS, no skips, exit0 | 385a07d5318671ce7af8b2325a8b53b912ec3d89d2a149c55eb62086800635a9 |
| first_remote_windows01/result.json | 27 PASS,18 explicit Linux skips,45 discovered, exit0 | e0a3e0ebc037ecf790f9d429684f2262758bff9385c0dc294cf74a421152fc73 |

Both first invocations used Python-I-B; Linux uses TMPDIR=/dev/shm. Each receipt
reports no changed coordinator input. Stderr hashes are respectively
2f0df27aeac30b5e4a4c29be2b4e912bd59a47a41659c72f74439dbabe562657 and
b24b0b6b07607ef7b673590b2b5e2c47622242cace4c2367790d9a7d5f6fde90.
The freeze's predicted Windows16 PASS/29 skips is a bookkeeping error,
preserved without editing the oracle or its guards. D195 already makes its11
descriptor-free Contract cases portable; only15 Lifecycle and3
PublicWaitLifecycle cases skip on Windows. Thus11+13+3=27 portable current
cases, with all18 skipped cases exercised on Linux. No production or test
repair occurred for this discrepancy.

This PASS supports only source/host preparation. Final preparation/scope,
clean reviewed HEAD and fresh native admission remain separate. No native
upload/capture has been established by these host receipts. Decoder findings
are tracked separately and cannot be converted into native acceptance.
Coherence remains UNPROVEN; runtime cause, timing repair, live RAM/WCET,
electrical acceptance, motor-run permission and human gates remain unproved.
