# D203 constant-metadata diagnostic compile preparation

26 September 2026. The new launcher is the exact ten-substitution derivative
specified by [the adopted contract](P7_motor_const_compile_contract.md):
7557 bytes / `957666a83c6fa36408dd6616f93d9cdc583622b29a51a6f6c6e960dd4cd1f247`.
Its private caller and remote projections are `bda40e96` and `914d4d11`;
the adapter remains `e3d23d5c`. All inherited bootstrap, file identity,
resource, first-error, clean-HEAD and artifact guards remain unchanged.

## Host evidence and preserved first failure

Independent oracles were frozen before implementation inspection/execution.
They retain all 65 caller and 37 remote methods and add five owner/source
checks, yielding 69 caller and 38 remote methods. The coordinator initially
bound 185 inputs. First runs are preserved in commit `22c0750c`.

| Run | Passed | Skipped | Errors |
|---|---:|---:|---:|
| First Linux caller | 69 | 0 | 0 |
| First Linux remote | 38 | 0 | 0 |
| First Windows caller | 65 | 3 | 1 |
| First Windows remote | 19 | 19 | 0 |
| Separate isolated Windows caller | 66 | 3 | 0 |

The first Windows caller failure occurred at the final original-source stability
predicate while reading a temporary fixture copy, before private caller execution
in the affected test. The traceback does not identify the changed stamp; its
cause remains unknown. No production source, guard or assertion was changed.

A separately authored/reviewed, single unchanged-method trace diagnostic
(`windows_stamp_diagnostic01/observation.json`, SHA `96cde093`) passed with six
complete source reads and all original guard predicates true. This is only
non-reproduction. The original suite remains FAIL.

One separately frozen full Windows caller invocation used an exclusive
TEMP/TMP/TMPDIR outside shared Windows Temp ancestry. It executed the same 69
methods and assertions, passing 66 with the same three platform skips. Its
result is `5d63e13a`; all 196 frozen inputs and the freeze bytes remained exact,
and the dedicated temporary root was empty. This validates the unchanged suite
under the recorded environment; it does not explain or repair the first failure.

The [final host review](../reviews/P7_motor_const_compile_review.md), SHA
`c68852ff788e3c862e0d2c83cbbff23e9e53e69f77a4d3b4d7b3906619bcc9d1`, passes
with no open material source/host finding. All 22 Windows skips are individually
covered by Linux passes. [Closing evidence](P7_motor_const_compile_raw/host_closing01.json)
(`b36f777e`) verifies all 196 pins, exact result/stream hashes and absent fixture
remnants. Accepted coverage is 107 Linux passes and 85 Windows passes/22 covered
skips, with the original failure retained separately. This is not a claim that
broad historical tooling discovery passes; the D202-documented D197 failure remains.

## Fresh read-only board admission and source manifest

[Admission01](P7_motor_const_compile_raw/admission01.json), SHA `dc082eac`,
contains two successful read-only transports with empty stderr. Board serial
2629958581 and boot 55c386b9-fe6d-4388-a7f4-1d91e0bb49d8 match, all 28 installed
file hashes match, full UID/GID credentials remain 1000, and the new local/remote
owners are absent. No recognized compiler/debugger conflict was found. Observed
root free space was 2,935,283,712 bytes, home free 13,936,066,560 bytes and available
memory 3,227,119,616 bytes. No compiler, privileged action or MCU operation ran.

The reviewed launcher produced the fresh local [manifest](P7_motor_const_compile_raw/inputs_static.json),
SHA `1b847d96`, binding exactly 129 files. Its inventory has 110 files/782068 bytes;
108 mapped files/781200 bytes yield source
`4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2`.
Only the D202 motor cpp differs from the D198 source inventory. Local manifest
admission passed without preparing, claiming or staging an attempt.

[Scope01](P7_motor_const_compile_raw/native_scope01.json), SHA `c08195d7`, retains
the fixed static/default/MATCH0/MOTORS_ALLOWED0/probe1 profile and fresh
app-motor-const-static01 ownership. Independent admission review, clean committed
HEAD and check-only precede the single jobs1 compile. Upload, reset and MCU reads
are outside this scope. Actual artifacts, fresh ABI/instruction observations and
a later separately reviewed inhibited runtime attempt remain necessary; target
timing benefit, WCET, physical acceptance and human gates are not established.


Final admission/scope review: [separate review](../reviews/P7_motor_const_compile_admission_review.md), 8108B/SHA e85747afa928f58d0612b6b9409ccaf9247235ad6f8efbc8c41de4fd0e7cf267, PASS with no findings. All129manifest/10scope/196hostpins independently match; actualobserver andclosingcommands are exact, currentowners remain absent. This closes preparation only.
