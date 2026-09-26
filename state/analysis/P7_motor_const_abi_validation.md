# D204 constant metadata ABI reader host validation

The exact D204 reader passed its independent first host runs. No board ABI
observation or runtime acceptance follows from these fixtures.

The adopted contract is P7_motor_const_abi_contract.md, 15192 bytes / 55a9f10d.
After the independent author issued FINAL and stopped writing, root reconstructed
all 19 ordered substitutions (26 occurrences) from the pinned D199 predecessor.
Actual inspect_static_abi.py is 16087 bytes / f360a52d, exactly the reconstructed
bytes. The implementation receipt is 11477 bytes / 5fa25b24. The independent
oracle is 18621 bytes / ea268af8; fixture derivation is 18602 bytes / 9327acb3;
its 220-pin independent freeze is 48145 bytes / ec77deb0. The oracle author did
not inspect or execute the new subject before freezing expectations.

Root's abi_coordinator_freeze01.json (38881 bytes / 90499324) unites 238 exact
inputs, including historical failure provenance and accepted D203 compilation.
The source-reviewed host driver 682516a4 ran Linux then Windows serially with
360-second limits and separate exclusive owners; neither timed out or retried.
Windows used a dedicated TEMP/TMP/TMPDIR outside shared temporary ancestry.

| First run | Result | Elapsed outer | Saved stderr SHA256 |
|---|---|---:|---|
| abi_first_linux01 | 71 PASS | 34.602 s | d1a366bcde29cc15b67a4803ca2502548c23063dafd2f07e7d6e3004019e3afc |
| abi_first_windows01 | 69 PASS, 2 inherited skips | 8.790 s | 3dba30501c46899d52a3c79db63edd4eaa5122c6f94f080332a969824ada0982 |

All 66 retained historical methods and five new methods ran in identical order.
Windows skips are real symlink creation without privilege and a Linux FIFO
race fixture; both pass on Linux. All 238 inputs and the coordinator freeze
match before and after each run. No source, assertion or guard was changed.

abi_host_closing01.json (2260 bytes / bb30f2d6) independently verifies saved
stream hashes, method counts/order and current input bytes. Matched Linux RAM,
Windows shared temporary and dedicated Windows temporary inventories are empty.
C: free space was 8882872320 bytes at closing. Preserve both first result sets,
compact sources/freezes and historical failures for reproduction and review;
no duplicate ELF download or manual cleanup was performed.

The separate reviewer closes source, saved host evidence and fixed native scope
before one clean-HEAD check-only and file-only execution. The four child commands
and 13 remote closing checks remain unchanged. D201 remains the latest flashed
image. No compile, upload, reset, MCU read, motor operation, timing or gate is
part of D204. Future entry scope must use actual new symbol presence/absence.

Independent source/host review: reviews/P7_motor_const_abi_review.md,
16839 bytes / ae662c11ca21d5ebcbb2d0865d35ce8eb068a498e6107e18692d6273209120b4.
PASS, no open material finding; reviewer stopped writing. The separate fixed
scope is abi_native_scope01.json, 2758 bytes / 6b7fba9d, awaiting admission review.

Separate fixed-scope admission review: reviews/P7_motor_const_abi_admission_review.md,
5955 bytes / 763b0c8275ecb07015a3c01ca3d943076bf63e053d56d3de462d4ed307c73ea5.
PASS, no open finding; all writers stopped before committing the native inputs.
