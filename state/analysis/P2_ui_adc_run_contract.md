# D114 single identified upload guard

Software contract selected under D051/D114 after the separate upload-route
preflight. No upload is authorized by this document alone. Existing generic
upload refusal and all old source keys/tests remain unchanged.

Add optional `--run-ui-adc-probe d114-ui-adc-01` to board_tool's flash command.
Before target lookup/staging/transport, reject any other identifier, sketch
other than `bench/ui_adc_probe`, MATCH, non-default startup, or compile-only
combined with this option. Ordinary compile-only stays unchanged. A missing
option preserves generic upload refusal. Direct fixtures without the new
Namespace member are equivalent to an absent option.

One passive module `tools/ui_adc_run.py` exposes:

```
validate_request(args, startup) -> bool
load_scope(root: Path, target: str, transport: str) -> dict
upload_once(board_module, target: str, artifact_folder: str,
            board_folder: str, scope: dict) -> None
```

`validate_request` returns false when the option is absent, true for the exact
valid combination, otherwise raises ValueError before any I/O. `load_scope`
performs local checks only. `upload_once` revalidates the same scope, verifies
both fresh checked artifacts, creates an exclusive attempt record and invokes
one upload. No function performs capture, monitor, reset, discovery or retries.
Imports are passive. Tests may use public filesystem/subprocess/board call
substitutes; no private state seeding is required.

Literal fixed identity values:

- run_id `d114-ui-adc-01`, target `2629958581`, transport `adb`;
- source `396bcc45fbaf30d38b170bf0c0063c555d5e88cdad512829b86a52ffede18642`;
- ELF `76e23fe03631d5cc2144578d35ca78b9bafd44158e0d18b2ab026922e4c9d05b`;
- ZSK `567fb90da6965cf74efc5ac2221e543d6d2150e3bf70ddae3e2346e6646c7fb9`;
- FQBN `arduino:zephyr:unoq`, MATCH0/MOTORS_ALLOWED0/default startup.

The fixed run record is `state/analysis/P2_ui_adc_probe_run01.json`.
It has exactly schema_version1, run_id, target, transport, source_sha256,
elf_sha256, binary_sha256, review_sha256, software_commit, setup, scope.
Identity/hash values above must match; software_commit is a lowercase40-hex
local revision, setup is exactly `human-reported bare UNO Q`, scope is exactly
`one inert ADC diagnostic upload; no motors; passive readout separately`.

The fixed approval is
`state/analysis/P2_ui_adc_probe_raw/reviewer/run01_approval.json`.
It has exactly schema_version1, run_id, verdict, source_sha256, elf_sha256,
binary_sha256, file_sha256. Verdict is
`PASS_EXACT_INERT_ADC_SOURCE_TARGET_CAPTURE_GUARD` and remaining identity fields
match above. file_sha256 has exactly these root-relative keys, each a lowercase
64-hex hash equal to the actual regular file bytes:

```
tools/board_tool.py
tools/app_build_policy.py
tools/app_build_pins.json
tools/app_build_commands.json
tools/ui_adc_run.py
tools/ui_adc_capture.py
tools/p0_capture.py
tools/p0_mem_read.cfg
tools/p0_inert_sources.json
state/analysis/P2_ui_adc_capture_contract.md
state/analysis/P2_ui_adc_run_contract.md
```

The run record's review_sha256 binds the approval's exact original bytes.
These are workspace review receipts, not signatures against a hostile editor.
Missing/unset/malformed/duplicate-key/nonfinite/oversized records or unequal
hashes fail closed. Bound each JSON receipt to65536bytes; both must be regular
files with no symlink ancestry below root. Root itself must be a real directory.
All pinned file ancestry below root is similarly checked. Reject an already
existing attempt path, including a dangling symlink, before remote access.

`load_scope` returns exactly root (absolute Path), run_record (decoded object),
approval (decoded object), run_record_sha256 and approval_sha256. Root/path/hash
revalidation inside upload_once must equal this initial returned scope. No
caller-supplied record path or uploaded image is accepted.

Only after independent capture/guard review may the coordinator add one manifest
key `bench/ui_adc_probe` with the fixed source hash; preserve the eight earlier
keys exactly. The explicit route still calls existing verify_inert_source after
staging, then the existing checked compile_app for ui_adc_probe.ino. Any source,
sync, preflight, compile or policy failure propagates without upload.

Returned artifact path must equal
`REMOTE_ROOT/_app_builds/native-app-v1/SOURCE/bench-default/UUID/artifacts`,
where REMOTE_ROOT is the existing validated dedicated SUMO_REMOTE_ROOT and UUID
is exactly32 lowercase hexadecimal characters. board_folder must equal
`REMOTE_ROOT/SOURCE/ui_adc_probe`. No cached passive-capture input is uploaded.
The normal compile_app generates the fresh UUID and checked receipt. Before
upload, call app_build_policy.verify_hashes using the board's existing remote
function for exactly the sibling `build/ui_adc_probe.ino.elf` and returned
`artifacts/ui_adc_probe.ino.elf-zsk.bin`, compared to fixed hashes above. The ELF
is in build; do not assume it exists in the CLI output artifact directory.

Revalidate local scope after remote artifact verification. Create
`state/analysis/P2_ui_adc_probe_raw/run01_upload_attempt.json` using exclusive
creation, after checking nonsymlink ancestry. This happens immediately before
launch and consumes the attempt even if the launch outcome is unknown. Store
schema_version1, run_id, target, source_sha256, elf_sha256, binary_sha256,
approval_sha256, started_utc, argv. Flush/fsync and close before remote launch.
The exact argv is `arduino-cli upload --fqbn arduino:zephyr:unoq --input-dir
ARTIFACT_FOLDER BOARD_FOLDER` using existing board.remote with capture=True
and a finite120s timeout. This is one upload, with its normal loader reset;
there is no separate reset. No retry or deletion of a claim is allowed.

On every returned outcome, retain a separate exclusive
`run01_upload_outcome.json` with schema_version1, run_id, finished_utc,
returncode (integer or null), stdout, stderr, timed_out(bool), error(string or
null). Nonzero, OSError, timeout and uncertain launch propagate as failure;
the consumed attempt remains. Failure to save outcome also fails without
another launch. A host interruption can leave the intent alone, which is an
unknown consumed attempt. A pre-existing outcome also refuses before launch.

The root-owned run record and reviewer approval remain absent until the exact
source/readout/guard reviews pass. Tests use synthetic fixtures clearly labelled
as such, cover refusal and error propagation, and do not write those live files.
The next actual run requires a new separately reviewed scope if this one fails;
no engineering recommendation manufactures measured ADC or human gate evidence.

Prefreeze field clarification: schema_version must be an actual integer1, not
a boolean. Outcome stdout/stderr are always strings (null becomes empty; timeout
bytes decode UTF-8 with replacement). Existing outcome includes dangling links.
The public board substitute exposes ROOT, setting, transport and remote.

Failure-type clarification before test freeze: semantic/request rejections use
ValueError; missing/unreadable local files may preserve OSError, including
FileNotFoundError. Actual remote exceptions propagate. A returned nonzero upload
status is raised as CalledProcessError with its original stdout/stderr.
