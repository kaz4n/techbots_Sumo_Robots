# D150 native API observation composition review

25 September2026, Asia/Dubai. Separate same-model review reusing prior P7
review context; not fresh-context, cross-model, human or runtime review. Reviewer
owns only this file. No collector main, GDB, board command, compiler/upload/reset,
deletion, implementation/test edit or commit was performed. Previously consumed
observations were inspected as evidence, not rerun.

## Verdict and exact scope

**PASS for the final fixed one-shot file-only collection composition. No open
BLOCKER, MAJOR or MINOR findings.** This is permission-scope/source review, not
an API/ABI comparison result. Coordinator adoption and exact-source launcher
binding precede its sole execution.

| Input under state/analysis/ | SHA256 |
|---|---|
| P7_static_native_api_plan.md | a795f5feee63bb6632bf90d38e0e580b8954a49d351dd46be471ced3b7cf1caf |
| P7_static_link_probe_raw/read_native_api.py | 65cb7785234ac96d489a8f4439eabf1809745fba74eda1ab5a636cec0f7dd6c5 |
| P7_static_link_probe_raw/native_api_preflight.json | ff14e0df29bfe9602aead40bb6f412e6cca57085adf5a73818d00f604bed1d28 |

The final50-query version supersedes the unexecuted36-query draft b377966c.
The change adds five scalar-width queries to each image and four native GPIO
function-type queries, as required by the retained GPIO audit's explicit gap.
Final preparation/notes are frozen in coordinator commit4ced5cff. No original
test, production source or consumed receipt is altered by this composition.

## Command and provenance

The fixed command has215 arguments. It starts with pinned GDB, -nx -nh -batch
and `-iex "set auto-load no"` before the existing D144 debug ELF. Only one
later `file` command opens the exact pinned packaged loader; the auto-load
setting remains disabled. Neither filename is derived from untrusted command
output. The two setup commands select C++ language and the value-printing bound;
all observations use literal ptype, p/x, sizeof, whatis, disassemble and echo
strings. There is no inferior/target, evaluated function call, shell, script,
firmware operation or remote file write.

The count is13 APP observations plus37 LOADER observations: each image receives
six structure queries, two typedef queries and five scalar widths; loader-only
queries cover nine devices, three driver vectors, eleven signatures and one
device-init disassembly. The 50 labels are unique and ordered, followed by END.

Inspected `P7_static_native_dispatch_next.md`, `P7_static_gpio_dispatch_audit.md`
and `P7_static_pwm_dispatch_audit.md`, including their quoted original file
evidence and exact remaining query requests. The device ordinals, GPIO/PWM
driver symbols, setter/getter/init functions and GPIO function names agree.
The final scalar queries cover the GPIO note's int/pin/flags/port-value/pin-mask
widths. The PWM note supplies device_ops, pwm_driver_api, pwm_flags_t and named
init/set/get requests. Retained motor-clock and installed ADC source observations
also name stm32_pclken, clock_control_driver_api, clock_control_subsys_t and the
chosen RCC implementation symbols. Their actual DWARF availability and values
remain observations to collect, not assumed successful results.

GDB8e709e32 and loader39d4a4fd must exist among the26 installed hash pins before
dispatch. The chosen existing app ELF is bound by the original D144 FileRecord.
The final preflight records215 arguments,3561 UTF16 command units, four marker
parser cases passing and zero board dispatches. This reviewer inspected that
evidence without rerunning preparation or parser tests.

## Admission, response and failure behavior

The copied D148/D149 preparation path checks exact repo/-B, captured frozen
runner983e86d7, pinned ADB and17 local inputs. Frozen Probe initialization reuses
the103 current source/102 existing stage checks,26 installed dependencies and
three original D144 receipts to recover the exact boot identity, Claim and eight
FileRecords. It never invokes staging, compiler preparation or Claim creation.
The native_api output directory must be absent and is created exclusively.

The only five intended dispatches are frozen remote_postcheck, installed hashes,
one GDB observation, remote_postcheck and installed hashes. Frozen helper
postcheck independently inspects Claim, identity, resources, compiler candidates,
source and artifacts using the previously reviewed read-only contracts. Host
comparisons retain the original identity/Claim/FileRecords. No new remote helper
or mutation path is introduced.

Frozen dispatch enforces the30000-unit command bound and retains planned/final
command receipts, including unsuccessful stdout/stderr/status. The GDB command
has60s timeout; acceptance requires successful exit, empty stderr and at most
1MiB stdout. `blocks()` demands the complete ordered label list, rejects missing,
duplicate or reordered labels, and requires every result block to be nonempty.
It deliberately does not interpret ABI compatibility from generic nonempty text.
The original full response remains in command0003 rather than being duplicated.

Final remote, installed and local pin/stage checks run independently after a
captured failure. The first failure survives subsequent errors; later postcheck
failures are retained. Finalization checks five reads and zero compiler/property
queries before writing status. A result-write failure cannot replace an earlier
captured exception. Success is named NATIVE_API_QUERIES_COLLECTED, correctly
separate from a comparison pass. Coordinator's planned captured-source launcher
must preserve source hashes before/after; no collector self-retry exists.

## Required later interpretation

Actual output must still be checked field by field against the application call
instructions and retained native evidence. Missing debug types, incompatible
layouts/prototypes, unexpected device vectors or an unresolved init dispatcher
remain negative/incomplete evidence. Collection success cannot close those gaps.

The scope is the direct GPIO/PWM/RCC/device-init boundary. It does not claim an
exhaustive packaged-OS dependency audit, native loading/startup success, device
ownership, live RAM/stack/heap, timing/WCET, physical acceptance, static production
admission, specific motor-run authorization or any human gate.
