# Minimal guard for the existing static packet

25 September 2026. Advisory design only: no implementation or board action.
Use one small host coordinator and one bounded board-side capture composition,
with separate, fresh upload and capture claims. Production dynamic admission,
old helpers/tests and consumed D118/D144-D151 grants remain unchanged.

## Reuse and narrow gaps

| Reusable code | Use; boundary |
|---|---|
| `tools/board_tool.py:remote` | Explicit pinned ADB/serial transport. Wrap it with the new operation's exact command allowlist; the function itself is not an authority check. |
| `P7_default_qualification_raw/reuse_stage.py:verifiedStage` | Recheck103 current/102 existing staged sources without copying or compiling. |
| `P7_static_link_probe_raw/run_static_probe.py:verify_inputs`, `load_module`, `checked_files`, `Probe.source`, `installed_pins`, `remote_postcheck` | Hash-bound imports and existing source/artifact/boot/directory checks. Initialize the old D144 Claim/eight FileRecords from pinned receipts, as D148 `validate_native_actual.py:prepare` demonstrates. The Claim is object identity, not a reusable run grant. Do not invoke `prepare`, `claim_remote`, `run_probe` or any old top-level launcher. |
| `P7_static_link_probe_raw/static_remote.py:claimed`, `read_file`, `artifacts_action`, `postcheck_action` | Reuse frozen descriptor/path/hash checks for the original packet. Existing action names must remain read-only in this composition. |
| `tools/app_default_run.py:safe_path`, `write_exclusive`, `current_head` | Safe local paths, exclusive flushed/fsynced JSON claims and HEAD observation. Do not call its historical run/scope/upload functions. `run_static_probe.write_json` alone does not fsync a claim. |
| `tools/p0_capture.py:no_symlinks`, `file_hash`, `loader_image` | Small file/loader utilities only. Its `Capture.read` has16-read/whole-flash rules and cannot implement the18-block plan unchanged; D118 `Capture` includes dynamic ownership/heap state and is likewise unsuitable. |

The only new collection logic needed is exact-plan iteration, receipt/output
ownership, bounded subprocess/wait handling and reference binding around the new
pure `static_capture.read_plan/analyze_capture` interface. No generic address,
command, profile or transport options are needed.

## One execution sequence

1. Check Python-B, fixed repository/target, pinned host ADB, current reviewed
   HEAD and exact new source/test/review/run-record hashes. Revalidate source,
   retained D144 objects, upload dependencies and absent overrides/shadows.
   `upload_shadow_inventory.json` now confirms the two `/opt` candidates absent
   and current CLI1.5.1/01f3d4f2b; the earlier include gap is closed in evidence.
   Rechecks are still needed immediately before the authorized launch.
2. Exclusively create/fsync `upload_attempt.json` with the approved argv,
   source/packet/tool/review/HEAD/target identities. Then launch exactly the
   source-derived CLI argv in `P7_static_upload_route.md`, explicitly retaining
   cwd `/home/arduino`. Record exit/timeout/stdout/stderr in a separate outcome.
   Upload includes ordinary `/tmp/remoteocd` copies and the checked flash/reset/
   activation effects. It does not create another source/build tree.
3. Only known upload exit0 with intact postchecks admits the separately reviewed
   capture step. Exclusively create/fsync `capture_attempt.json`, linking the
   upload claim/outcome plus pure-plan/code/reference/config hashes, before its
   remote launch. Create one fresh capture-output directory; preserve its exact
   name and identity. Bind ELF-derived loader263680B/SHAe9322826 and flat93096B/
   SHA5f08afe0. The packaged loader BIN6b2ffd differs by one byte; see the separate
   P7_static_capture_reference_review.md. This corrects the initial advisory
   reference assumption, without changing the proposed collection scope.
4. Run exactly the18 requests from `P7_static_capture_contract.md`, total713656B.
   Use the already installed pinned passive config, not the upload configs.
   Each command has only `/opt/openocd/bin/openocd -f <fixed passive config>`
   plus its exact `dump_image {fixed fresh output} address size` and `shutdown`.
   Record a planned command before launch and actual result/read hash afterward.
   Require regular, previously absent, exact-length outputs. Compare complete
   before-flash images before any RAM sampling; mismatch terminates collection.
5. Freeze concrete limits in the new run contract: recommend18 read commands,
   30s per command,600s overall and one recorded2s monotonic interval between
   sample pairs. These are proposed bounds, not additions to the pure contract.
   No metadata executables, heap walk, new addresses or recovery probes follow.
   Only complete18-read data reaches `analyze_capture`; retain incomplete evidence
   without fabricating missing triples or an analysis verdict.

## Failure and durable evidence

Each claim remains consumed once its launch is attempted, including exceptions,
lost ADB, timeout or unknown completion. An upload failure never launches capture;
a capture failure never retries upload/capture, resets or restores. A lost host
transport is not proof that the board child stopped: the remote collector must
enforce its own deadline, and the outcome must retain UNKNOWN when appropriate.
Failure finalization runs independent local and Linux-file postchecks only; it
must not add MCU reads or erase the original error when a later check also fails.

Retain the two claims/outcomes, exact receipts/raw reads, bounded timing records,
reference hashes and separate analysis. A complete capture may report a sampled
fault or no progress; successful collection is not successful startup. Hash-bound
reuse of D148/D149/D151 evidence avoids rerunning structural/ABI audits. Runtime
progress still grants no live-memory/WCET/physical/motor or human-gate acceptance.
New command/claim/timeout/finalization glue needs focused independent failure
cases; the new pure oracle covers only planning/interpretation.
