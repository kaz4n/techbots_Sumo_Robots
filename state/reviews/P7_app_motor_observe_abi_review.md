# D194 file-only ABI projection: source and host review

26 September 2026, Asia/Dubai. **PASS for SOURCE / HOST scope; no open material
finding.** Native ABI observation has not occurred. Reviewer `/root/fresh_review`
is a separate same-model reused context, not a fresh whole-project reviewer.

The reviewer read the contract, wrapper, preserved reader/normalizer/launcher,
the complete independent oracle, first failure, corrected freeze and actual
Linux/Windows receipts. Independent local hashing, AST/data inspection and Git
blob comparison were used; no subject import, test execution or device call was
performed. Only this review document was written.

## Source and binding

| Item | Bytes | SHA-256 |
|---|---:|---|
| Contract | 11496 | `889d6a7697f2ddc0051ef73f52f82c1dd43f35fa45af9fc2d4958f44441bf8ff` |
| New wrapper | 8831 | `297eac8b2c9878b8c8e5480053e5541dfc48e9bd35c1a99a924eadc9374d632d` |
| Private projected reader | 16833 | `f359bebbbba176036891027412327b6b59e47d849e46c37cfe3363cd70a95c14` |
| Corrected independent oracle | 46134 | `ac571bd4a1e4eeba9516795236c9d79329a0d2967999c22f81a953f7aa957cb2` |

The [contract](../analysis/P7_app_motor_observe_abi_contract.md) and
[wrapper](../analysis/P7_app_motor_observe_compile_raw/inspect_static_abi.py)
match these pins. All three original source lengths/hashes match. The reviewer
reproduced all 14 ordered byte substitutions and the exact projected hash
without executing the source. The resulting diff changes only declared names,
scope/receipt/source pins, compiler-loader integration and member queries.
Historical source files and consumed owners remain unchanged.

Private definitions retain the correct repository root through original
absolute __file__ paths, never run as __main__, and are not registered in
sys.modules. All original snapshots, contract and projection are checked before
execution. The reader receives the stronger bounded pinned function and retains
all inherited hard pins, adding the original reader, normalizer and contract.
Its own wrapper remains bound through SELF and reviewed Git/manifest checks.

The compiler lookup correctly calls the D193 launcher's load_caller(root=ROOT),
so the reused CompileDiagnostic methods enforce the new source inventory,
manifest schema and actual compile/artifact bindings. Source3a08ddeb, manifest
aa350c65, compile result24d12778 and artifacts5ceba77d are the completed D193
inputs; the old D188 artifacts/layout are not substituted for them. The boot
literal is unchanged because D193 freshly observed the same boot, with future
live identity checks still required.

Strong pinned reads reject nonordinary/multiple-link/reparse inputs, validate
the descriptor before reading, use nonblocking/no-follow flags where supported,
bound reads, compare ancestry/path/descriptor identities and preserve primary
errors over closure errors. The Windows cross-API ctime exception still requires
stability within each API. No material bootstrap defect was found.

The summary adapter deep-copies result rows and layout. Only the private readelf
stdout representation changes. It uses the unchanged normalizer.normalize;
neither historical interpret nor main executes. Original command/stream checks
precede normalization, original result.json is retained first, and projected
stdout hashes/size-token metadata accompany the parsed ABI. Decimal/hexadecimal
spelling does not weaken unique-symbol, ET_EXEC, BSS, alignment or window checks.

Four file commands now describe 20 SIZE/ALIGN/LAYOUT groups and 11 member
windows. report_.polls is queried through its actual member expression, including
size, alignment, type and offset. No field offset, Report/Runner size, padding
or address is assumed from D188. New readelf/debug filenames remain bound to
the same checked D193 artifact packet. The unchanged reader retains fresh
exclusive local ownership, absent-only remote scope, 12 remote file pins,
bounded/reaped children, original stream accounting and independent closure.

## Independent oracle and actual host evidence

The original oracle was frozen before its author read/executed the new wrapper.
It exercises exact projections, passive private loading, CLI rejection, real
D193 admission and artifact-receipt validation, strong bootstrap reads, synthetic
ABI/parser packets, original receipt validation and controlled prepare/execute
paths. Subprocess/socket endpoints are blocked. Prepare composition uses an
explicit controlled space/local fixture; execution uses synthetic transport and
writer seams. These are host checks, not actual admission or native observations.

Material coverage includes real hardlinks and Linux file/parent symlinks, a
nonblocking regular-file-to-FIFO swap, simulated reparse rejection, descriptor
and ancestor drift, Windows ctime handling, bounded reads and close errors;
20 query groups/11 windows and variable polls size/offset; strict symbol/tag/
Base64/UTF8/BSS/alignment bounds; raw retention, wrong scope/commands/deadlines/
closure rejection, consumed-owner refusal, command-length/space limits and
primary-error preservation. Controlled composition checks four file tools and
the Windows 30,000-unit limit without dispatch. No material remaining host
coverage gap was identified for this narrow change.

The first Linux run is preserved: 44 methods, 43 PASS and one FAIL, with all
134 pins unchanged. Its sole failure required parser-layout object identity,
which the contract does not require. A defensive copy with unchanged contents
is compliant. The reviewer independently confirmed that commit974de230 retains
the exact 46,030-byte original oracle SHA-256
`fcbb950ef27825664b5b734e25d68083d967f8b8c05609aa238f6026bdff963a`.

The corrected diff only snapshots layout, replaces that identity assertion with
content equality, and checks the original layout afterward. All other assertions
remain. Source and contract did not change. The corrected oracle was refrozen
before rerun; the unsupported fixture assumption is CLOSED without weakening
the contractual preservation check.

| Actual receipt | Result | Unittest duration |
|---|---|---:|
| [linux_test01.json](../analysis/P7_app_motor_observe_abi_raw/linux_test01.json) | 43 PASS / 1 fixture FAIL | 9.673 s |
| [linux_test02.json](../analysis/P7_app_motor_observe_abi_raw/linux_test02.json) | 44 PASS, no skips, exit0 | 12.988 s |
| [windows_test01.json](../analysis/P7_app_motor_observe_abi_raw/windows_test01.json) | 42 PASS / 2 platform skips, exit0 | 1.518 s |

Windows skips unavailable symlink creation (WinError1314) and the Linux FIFO
fixture; Linux executes both. Windows hardlink and simulated reparse/ctime checks
pass. Actual Windows symlink creation remains unexercised. Both final receipts
record all 135 coordinator pins unchanged; the reviewer independently rehashed
every current pin and found no drift.

| Evidence | SHA-256 |
|---|---|
| Corrected independent freeze | `ec6cf28db266da81bddc7b75182c05f19c2d752c207e8838c2acc1dd54953704` |
| Coordinator freeze02 | `02e7200c6db154337dadefc2445c952b3481e60139040dfc2824006b5c358f07` |
| First Linux receipt | `bab9f7dbd312aa21fba7742e16dc293c19e897030e088e93b015f8e930d351f0` |
| Corrected Linux receipt | `d46d17912609f771aacf810622301f1278e0d56d0b8a134749a17d6e5cecfbbd` |
| Windows receipt | `f0bf9a5f456cbec025b1b59c2af72ca2e9b0771c44accc537af0ad900395a21d` |

## Native boundary

At final review the local native_abi_static01 owner is absent. Observed local
free space was 9,023,488 bytes, below the unchanged 134,217,728-byte guard.
No actual check-only or file-tool invocation is approved by this host verdict;
space recovery, a clean reviewed HEAD and successful existing admission remain
required. The guard must not be bypassed.

The new member-expression GDB syntax and actual sizes/addresses remain
unobserved. An unsupported expression must fail and preserve that consumed
attempt, not trigger a guessed layout. A later file observation still needs
independent ABI/field and initialization interpretation before a separately
scoped inert run. No upload, reset, MCU read, binary transfer, firmware execution,
fault reproduction/repair, live RAM/stack/WCET measurement, physical acceptance
or human gate follows from this source/host review.
