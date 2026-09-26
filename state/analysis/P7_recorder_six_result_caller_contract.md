# D238 fixed passive result caller

tools/run_recorder_six_result_capture.py is an exact literal projection of the
accepted D233 caller. It binds the source/attempt/session/package and fresh ABI
specified in P7_recorder_six_result_contract.md. Current145 source inputs and
110 staged records are checked against historical compile HEAD1b2af246; the
reviewed collector HEAD remains separate. No source mapping, remote lifecycle,
descriptor, first/closing-error or transport guard changes.

The fresh ABI contains65 fields, including one4B `packet_started_us` window
for native_dump.started_us_. Its exact ELF-derived offset/width flows through
the existing range merge, bounded plan, count projection, retrieval and local
decode; no guessed address or separate read action is added. The accepted64-
field checkpoint is superseded. Clock-wrap, sample chronology and the shared
timeout predicate limit interpretation; the caller reports raw uint32 values
without automatically assigning a timeout cause.

Root first accepts the freshly executed ABI; old ABI addresses cannot be used.
With A equal to that exact abi.json SHA256, root runs offline:

    python -B tools/run_recorder_six_result_capture.py --prepare-bindings --abi-sha256 A

This writes exactly three absent-only local files beneath
state/analysis/P7_recorder_six_result_raw: capture_inputs01.json,
capture_scope01.json and capture_adapter01.py. The adapter is the fixed
reviewed helper plus the existing literal spec wrapper, at most1MiB. Pins bind
the four ABI records, four closed compile records, caller/helper/contracts and
canonical spec. No caller-supplied code or runtime address choice is admitted.
Root commits the accepted actual ABI evidence and all three bindings. With H
equal to the resulting clean collector HEAD, and only after delivery/receiver
closure if observation remains useful, root runs:

    python -B tools/run_recorder_six_result_capture.py --check-only --reviewed-head H
    python -B tools/run_recorder_six_result_capture.py --execute --reviewed-head H

The local owner is P7_recorder_six_result_raw/native_capture01. Fixed remote
staging is /home/arduino/sumox26_codex_build/recorder-771c04943d4c4a75-failure-capture01-adapter/remote.py;
the separate capture owner omits the -adapter suffix. Both are absent-only,
consumed after partial work, with no cleanup or retry branch.

The D219 CaptureRun/D212 owners and their reviewed D233 projections remain
unchanged. Retain the fixed ADB target/hash, ten-transport bound, seven-action
allowlist with no upload, durable intents, source/adapter capabilities before
and after, baseline prerequisites and exclusive descriptor/output identities.
Source capabilities still use the actual /recorder path. The installed
p0_capture bootstrap, adapter/parser closing checks and fixed-plan retrieval
remain identical after literal reversal. Retrieval returns the report and
every selected raw status file, with independent per-file closing reads and
1MiB reply limit; full flash images remain at their durable remote owner.

Successful export still requires exact envelope/report identities, counts,
monotonic timings and two-second separation, complete matching flash hashes,
raw hashes and identical local recomputed analysis. Before-flash mismatch
prevents SRAM access. Invalid bool/enum bytes fail decoding while preserving
raw data and attempting closing flash comparisons after successful reads.
An unsuccessful collection cannot be exported as successful. Every snapshot
is non-atomic with coherence UNPROVEN. Session equality is reported rather
than required because early setup failure may leave zero. First-record bytes
and status values create no causal, physical, delivery or gate claim.

Focused host checks use synthetic layouts only and execute no transport. They
prove complete reverse equality, absence of old executable identities, exact
field/enum/query inventory, invalid extent/width/value refusals, real145/110
file-owner composition and real fixed-adapter/action/full-flash composition.
Inherited lifecycle tests remain the accepted D230/D233 evidence. Root alone
owns native execution; a fully validated delivery may make capture unnecessary.
