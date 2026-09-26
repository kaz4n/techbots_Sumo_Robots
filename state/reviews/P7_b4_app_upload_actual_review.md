# D221 actual fixed inhibited B4 upload review

FINAL PASS for the exact returned uploader completion below, 2026-09-26.
Independent saved-evidence/data review by the same reviewer with reused context;
no subject imports/tests, native commands, credentials, cleanup, upload or MCU
reads were performed by this reviewer. Earlier source/host and native-admission
reviews remain unchanged. No open material actual-upload finding.

## Exact evidence and dispatch

Native HEAD:310f96066a0fb95c66d948e3128cd67c49c5f344.
RAW means state/analysis/P7_b4_app_upload_raw; OWNER means RAW/native_upload01.

- RAW/upload_native_invocations01.json:1900 bytes /
  3dfd848424b226f7156a35827a63b8c53c1ed5b78140bf8654b1e7de4a8c7981.
- OWNER/result.json:29965 bytes /
  6d5e7b106eff8013e65d7bbee521dd169bb39562915d975025d7e6546e0996c3.
- OWNER/final_checks.json:28880 bytes /
  fa80c347957b78fe8d033a3d0b2ff19b2e3781102dd501dbfb601c7305a69a95.
- OWNER/inputs.json:18247 bytes /
  6b10dc276c6b2b99ba6a0e06d834013b6781b8e6e901c1b59df85baaa8261187.
- RAW/upload_native_closing01.json:5427 bytes /
  f7b5967d9c8c71257321cb5b8c225187e9493352bff9645ec1f1231f766bbc1f.

The saved driver records one local check-only followed by one execute, both at
the admitted HEAD, returncode0, empty raw stdout/stderr and matching base64/hash
fields. Check-only elapsed2.2076556s; execution elapsed29.3924327s. The saved
120/900-second parent bounds and exact isolated argv match the admitted driver.
Driver first_error/closing_errors/changed_inputs are empty, prerequisite bytes
remain unchanged, and the closing HEAD equals the admitted HEAD.

All230 prerequisite files independently match current bytes and their blobs at
the native HEAD. The prerequisite file789bff40 and native-admission review
fab6302f also match their native-HEAD blobs. All161 runtime input hashes,
including the absolute pinned ADB executable, match current bytes. Concrete
scope9158547d and the accepted ten file roles remain exact.

Exactly nine numbered transport owners exist, in order: adapter-claim,
adapter-push, cli-initialization, cli-builtin-files, capabilities, upload,
cli-initialization, cli-builtin-files, capabilities. Every intent equals its
result apart from the added returncode0. All nine transport stderr files are
empty; each saved stdout/result pin matches the root closure. Independently
recomputed full Windows command lengths and both remote/native argv hashes
against OWNER/inputs.json and the durable action/staging command records.
The upload command is29529 UTF-16 units including NUL; all commands stay below
30000. Upload timeout195s and other transport timeouts60s are unchanged.
Upload intent has predecessor_sha256=null. No capture, retrieval or alternate
upload dispatch appears.

## Exact submitted profile and returned result

Data-only decoding of the actual saved upload argv recovers the exact reviewed
bootstrap and one canonical base85/BZ2 packet,102608 bytes / SHA256
ea73114e4c529a9716b8a7d73615e4a962a3f3555f226fd91bff0e2a9de1d13d.
The payload hash, canonical JSON, exact fixed B4 binding and staged adapter pin
match the reviewed source/plan. Each of the three inline dependency bodies
equals its current pinned source byte-for-byte. The profile therefore selects
the accepted B4 build raw82896/6fcad2f0, package82912/84667b0a, fixed loader and
installed files, static FQBN and unchanged source9044ebbb. The accepted compile
evidence binds MATCH=0, MOTORS_ALLOWED=0, SUMOX_B4_STAND=1, all other commissioning
profiles zero and all setup grants zero.

Adapter claim reports UID1000, expected user/boot/CLI hash, no conflicts and
13871132672 free bytes. Before/after CLI-initialization, builtin-file and
capability stdout pairs are byte-identical. Capability observations include
the exact adapter/source identity and104 staged source files. Saved native
admission and local/prerequisite checks are clean; all32 saved Git-check records
return zero with empty stderr, fixed HEAD and only the exclusive local attempt
owner permitted as untracked content.

The942-byte upload stdout is exactly the envelope retained in sequence result;
its SHA256 is00e08fafd67c07f46b5a74d3edd59de0504dd4b0101aa68d9eac1c9b4b8fa00f.
Its schema/action/run/source/path match the admitted upload. report_origin is
returned, not durable_unattributed. Both envelope and inner report have no
first_error or postcheck_errors. The inner report is UPLOADED, attempts1,
subprocess returncode0, timed_out=false and reaped=true. Monotonic duration is
12.001013612s, within180s; UTC bounds are17:51:09.538110 to17:51:21.538977 UTC.

The sequence reports COMPLETED/upload_attempts1. Its diagnostics exactly equal
the separately saved final_checks.json: commands=transport_calls=9; exact label
counts1,1,2,2,2,1; sole intended/dispatched action upload; complete staging
intent/claim/dispatch/ready state; and empty local, prerequisite, transport and
finish errors. This reconciles the successful returned path through the reviewed
uploader and independent adapter/root closing guards, rather than accepting a
durable status file without return attribution.

## Evidence boundary and next step

The envelope identifies a full canonical result of1793 bytes / SHA256
87bc88a9cd24e6b63c73275851f2930a4ce6605d0657270535c4c1ef1f97d2a3 at
/home/arduino/sumox26_codex_build/b4-app-m0-9044ebbb-load01-upload/upload_result.json.
That full durable report was NOT retrieved. This review does not independently
rehash its remote bytes or inspect the omitted uploader stdout/stderr. Accepted
evidence is the exact returned compact report from the pinned executed
bootstrap/uploader, its local transport bytes, and closing checks.

This accepts one fixed inhibited B4 upload completion as the D221 prerequisite
for a separately admitted D219 capture. It does not grant that capture itself.
D219 must independently verify complete flash before any SRAM evidence, and
must retain its own origin, lifecycle and recording-completion checks. There
has been no MCU flash readback, RAM capture, runtime/coherence/WCET qualification,
physical sensor or motor acceptance, motor-run permission or human phase gate
from D221. New /tmp/remoteocd upload scratch has not been inspected; consumed
D220 cleanup scope cannot be reused for it. All attempts/owners remain consumed.

Actual review sealed; writes stopped.
