# D195 observer remote adapter review

26 September 2026, Asia/Dubai. **PASS for source and host preparation; no open
material finding.** Reviewer `/root/fresh_review` is a separate same-model
reused context. Review used local source/contract/fixture/receipt reads, hashes
and static comparisons. No subject import, test execution or board/native call
was performed by the reviewer. Only this review was written.

| Input | Bytes | SHA-256 |
|---|---:|---|
| P7_app_motor_observe_remote_contract.md | 11937 | `c2563449091f44ccd827b8cbc1173dc3e655614f6bb8d01c091540b99958d9c7` |
| P7_app_motor_observe_run_raw/remote.py | 11357 | `98b0f5394d64f61178277f701adb81eece3d5f136ea84a8c5fb30534a5b241db` |
| tests/tooling/test_app_motor_observe_remote.py | 20956 | `f45218ea3d9fb118adfe796c12fc5f4bab654c843cf33cc531e81d99a3f41fc6` |

Independently reproduced all ten ordered/count-checked metadata substitutions
from the preserved 10518-byte original `a77fb7d4...`. The result is exactly the
10548-byte baseline `e0bb7868e54a640499718d5c0d3df4ce6c6b4ef72a49f0bda9df64bbb60530f5`.
The new source differs only by initializing analysis.pre_sample_wait, adding
pre_sample_pause, invoking it at index7, and requiring completed wait evidence.
All other module-level function bodies are structurally identical to that
baseline. The three upload/capture/helper dependency bytes and hashes match
the contract. Private selection/hash checks precede private execution; import
defines the adapter without loading dependencies or calling a device.

Fixed source/build/artifact identities agree with D193 and current ABI02: raw
95344 bytes, package95360, unchanged loader image263680, and the same six
observed SRAM windows. The plan remains 26 reads requesting727152 bytes, with
12 SRAM snapshots. Initial loader/sketch comparisons occur after indices4/6;
final sketch/loader comparisons occur after20/25. The index13 two-second pause
and existing report.wait are unchanged. Upload, exclusive owners, strict
bindings, process/file checks and mandatory /tmp/remoteocd absence are retained.
No cleanup, arbitrary profile, new transport or extra memory query is added.

The one new sleep is after both initial flash comparisons and before read7.
It requires more than30 seconds remaining, records a checked monotonic before,
requests the integer30 once, records a checked after, verifies at least30 elapsed
and rechecks the original600-second budget. The capture origin is never reset.
Equal/insufficient budget fails without recording a wait; later failures retain
before and any validly obtained after. A throwing/short sleep, invalid or
reversing clock, or expired final budget prevents the first SRAM read. Existing
children still use min(30,budget()), original stream/reap bounds, and upload's
180-second budget is unchanged. Thirty seconds is an observation delay, not
evidence of FROZEN state, epoch progress or successful MCU execution.

The inherited collection/finalization path retains first_error, partial reads,
flash flags and independent final postcheck errors. COLLECTED additionally
requires the original complete counts/snapshots/flash checks and no first error.
Precise inherited limit: an FD-close exception from _collect's final close may
propagate separately after capture_result.json is saved; the saved first_error
is preserved, but that descriptor-close exception is not added retroactively
to the inner receipt. The existing outer action envelope must retain the outward
failure and treat durable fallback as unattributed failure. No stronger inner
close-evidence claim is made here.

The independent oracle froze before its author read/imported the new source.
It retains all26 historical methods through checked metadata/fixture projection
and adds16 focused methods. Fixture changes account for30-at-read7 then2-at-read13,
preserve the old short-gap failure injection, and restore only their own platform
module aliases. New coverage includes exact baseline/delta, complete read/wait
ordering, clock type/finite/order failures, equal-budget refusal, short/throwing/
oversleep failure, partial wait persistence, no SRAM after wait failure,
completion predicates and first error through closing failures. Public collect
descriptor fixtures run on Linux; controlled class seams also run on Windows.
The close-exception fixture explicitly checks the inherited limit above.
No material fixture defect was found.

| First receipt in P7_app_motor_observe_run_raw | Actual result | SHA-256 |
|---|---|---|
| test_remote_windows01.json | 24 PASS,18 explicit Linux-only skips; exit0, unittest0.584s | `82b7625bd36ebeb12ac940540c5a682b79a94117ff2964a8721a39278f18239b` |
| test_remote_wsl01.json | 42 PASS,no skips; exit0, unittest4.533s | `c15d7ce336e79354d6ac8b3b2f354ce6b69cbc2d80142327c2f032bc80700d8a` |

Both commands use Python -I -B; WSL uses TMPDIR=/dev/shm. These are42 discovered
methods per platform, not42 passes plus18 skips on Windows. Independent freeze
is `b268b83863618cf9fc8ce21412688b139dc1e937f708c1ecb6ebb7e8f5f664bd`.
The reviewer independently hashed its nine oracle inputs and exact expected
subject against current files: all match. Both first receipts bind the same
source/oracle; no failure-driven repair occurred.

This PASS supports only the fixed remote-adapter preparation. Caller/actions
review, strict validation of the new wait field, exact provenance/scope and
separate fresh native admission remain distinct. Capture coherence stays
UNPROVEN. No complete callback history, runtime success, live RAM/WCET,
electrical safety, motor permission or human gate is established by these tests.
