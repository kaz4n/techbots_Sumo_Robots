# D214 B4 M0 compile actual review

FINAL PASS, 2026-09-26: the single admitted B4 M0 static/default compile and its file-artifact closure are accepted. This is a same-model reused-context independent review, not human or cross-model review. I read saved evidence, source and Git blobs only; no subject import, test, compiler, board call or retry was performed. The separate fresh_review agent cross-checked saved compiler/artifact metadata read-only without writes. RAW means state/analysis/P7_b4_app_compile_raw.

## Exact result/provenance

| Artifact | Bytes | SHA256 |
|---|---:|---|
| RAW/native_invocations01.json | 9114 | c2c5dfba3315f6ee79067baa31a6a9b014961ac4e2173974dfcb2df284761bd4 |
| RAW/native_static01/intent.json | 1004 | 469ec2ea0c9e6367e300a0c37e27583cca0e874b15f0ff805379df082a65012f |
| RAW/native_static01/result.json | 1829 | b722db17adabafc03f6ad8583bcef9b0f6b7d1def4d3e54962508aad4039567a |
| RAW/native_static01/artifacts.json | 9484 | 0acaa30a4ba01ac5c9ff8c8fddc66c4bec94e033b1194ec63271f12affb6c085 |
| RAW/native_closing01.json | 34317 | 7a43d0be1d4f51f11d198c431b11cc7c0a277735fc897bf49c6e2d238e14eb17 |

The reviewed execution HEAD is34c1b965f4ed2a9332c4f890ee2a4a27d89a7ba0. All244 prerequisite files independently match both current bytes and that commit's Git blobs; prerequisite identity is2365bc036baf286bca651a2a682eb892e321b60f1dd25aa478242837a941c3d9. Scope17, coordinator224 and manifest130 subsets remain exact. The scope, manifest, role-binding02/current freezes03 and sealed source/host/native-admission reviews reconcile with the exclusive native intent. Source identity remains9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a.

The one local check returned0 in0.7057413 seconds; the one execute returned0 in274.6018024 seconds, within120/1800-second bounds. Both exact isolated/no-bytecode argv and outer base64/text/hash streams reconcile, with empty stderr. The execute uses the admitted output-specific pycache prefix. Outer first_error is null; all three independent closing checks pass, prerequisite bytes are unchanged and HEAD closes unchanged. Clean admission was enforced by the checked driver/caller; no later dirty output is mistaken for a pre-execution dirty tree.

## Native work and closure

Exactly25 ordered transport owners are present. Every intent equals its result apart from returncode0; every raw stderr is empty, every saved argv uses the fixed ADB/serial route, and every complete Windows command length independently matches the recorded value including NUL and remains below30000. The maximum actual value is29352. All nine checked children have matching raw JSON/base64/child streams, COMPLETED status, returncode0, reaped=true, timed_out=false and5-second reap. The expanded-properties query runs once with60-second deadline (1.6506011 seconds); the one compiler runs --jobs1 with720-second deadline (226.7490315 seconds). Compiler transport outer timeout is810 seconds. Version/config, installed-pin and override checks are separately identifiable preflight/closing children, not additional compiles.

The actual query/compiler argv carries app.ino, arduino:zephyr:unoq:link_mode=static, default startup, MATCH0, MOTORS_ALLOWED0, B4_STAND1 and all remaining declared diagnostic/trial flags0 in both C and C++. Their318-property maps agree except recorded extra.time.utc/local values. Real full metadata validators accepted them. Compiler success is true, compiler_err is empty and upload_result is empty.

The stage contains exactly104 admitted files/764405 bytes, each matching staged_files.json and the current manifest mapping. The105-source inventory includes the intentionally unmapped app .gitkeep. Remote canonical source admission reports reused=true after exact content/directory checking; source sets before/after are byte-identical. Thus this attempt reused the checked canonical source instead of issuing source-file uploads. Initialization/builtin inventories before/after also match byte-for-byte. Identity fields remain unchanged; the permitted home free-space observation decreases13891100672 to13871235072 bytes and stays above1GiB.

Result status is COMPILE_CHECKED with query_calls1, compiler_calls1, transport_calls25 and null first_error. All nine final checks are PASS with null errors: local, identity, initialization, builtins, remote_sources, installed_pins, overrides, artifacts and artifact_sources. The152 retained native files total1006951 bytes. All transport receipt/stream pins and reported child timing/argv in native_closing01 reconcile independently.

## Actual source transfer and artifact evidence

Postcompile transport15 writes exactly16384 bytes; transport16 appends11703 bytes. Decoding the actual transported tokens reconstructs28087 compressed bytes with SHA256901ff1d8657d74581f19543c87873402eccbc76867004b602f7b8755902d2f68. Bounded decompression yields116347 bytes /834853a8e8946fce5a301e3eb4975fab0cbae59fe73da6c2eba551a44bef7549, with EOF and no tail. The reconstructed remote source and every one of the eight bundle members equal the pinned current source bytes, including their original newlines.

The exact corrected ARTIFACT_SOURCE_IO body appears in both writes, initial/final artifact programs and final payload read. This retains anchored dir_fd ancestry opens, no-follow/type/link/owner/mode/size/stability guards, exclusive first creation, exact previous record, first-error priority and descriptor closure. The second command embeds the first actual record. Both use device66341/inode274493, regular0600, nlink1, UID/GID1000. Size changes16384 to28087; second mtime/ctime are1790439044535638931. The final read returns the complete second identity/hash unchanged, and artifact readers use that exact previous record. The actual successful path does not exercise partial-failure behavior; that remains explicitly host-tested evidence.

Both artifact programs and their6471-byte stdout streams are identical; stdout SHA256094d3629fe48f74a425ba275313a21859d97de58ac391d8f2973d789fd241360. Both parse exactly to artifacts.json. All eight file records, loader/TLS identities and three independent remote postchecks close unchanged, with no first error. Seven nested artifact size/hash/identity-alias records agree. The retained guarded validator reports STATIC_B4_APP_LAYOUT_PACKAGE_PASS and exact integer motors_allowed0.

Key checked target artifacts:

- Exported/build flat package:82912 bytes,84667b0a22ff7701059a266b6c82bb61de1f7ccec96280e4f13b5692bf785a28; both copies agree.
- Raw binary:82896 bytes,6fcad2f09c90bbc7dd72760e7a794305811d042a9d2e578e03d5154cc368a471.
- Stripped ELF:152780 bytes,12a24abfb96e89863c46f2475d05fb44a549db95cb157411cd794657f15fd422.
- Debug/temporary ELF:1779680 bytes,4c0fc8e2d3881019aaef222d7a9ab77779da7ca116bca49d1c6badeefeb83f7d; both copies agree.

These are saved outputs of the exact transported, source/host-reviewed validators; this review did not separately retrieve or reparse full raw ELF files. Structural data208+BSS167584=167792 bytes leaves94352 bytes in the admitted RAM region. CLI independently reports167796 globals and94348 remaining. The four-byte accounting difference is retained without inventing a cause. The startup-zero span167352 excludes232 bytes of the BSS section tail. Neither static remainder is measured live free RAM or a stack/WCET bound.

## Acceptance limits

No actual-result blocker remains. Earlier Linux product/fixture failures and the Windows pwd fixture failure remain preserved; host coverage is still the explicitly reviewed86+5 composition, not retrospectively relabeled. Two reviewer-only read-audit assertions were corrected before writing this report: actual transports have the inherited env preamble, and free_bytes is a changing resource observation rather than an invariant identity field. Neither correction changed evidence, source or tests or caused native work.

This closes only the admitted compile and stable file-artifact observations. There was no B4 upload, reset, MCU read, ABI/disassembly observation, runtime execution, live timing/RAM measurement or physical test. The previously flashed D212 firmware was not replaced by this compile. Static M0 metadata/package validation is not physical inhibition evidence, motor-run permission, strategy qualification, a phase gate or competition readiness. Any downstream file-only ABI/entry work requires its own actual-artifact bindings and guarded admission; any firmware run remains separate.
