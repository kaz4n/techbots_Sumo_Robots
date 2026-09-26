# D214 native compile admission review

FINAL PASS, 2026-09-26. Independent same-model reused-context review of actual saved read-only evidence and the fixed native scope; not human or cross-model review. No subject import, test, compiler or device call was performed. Previous source/host and preparation reviews remain immutable. RAW means state/analysis/P7_b4_app_compile_raw.

| Checked RAW artifact | Bytes | SHA256 |
|---|---:|---|
| admission01.json | 64653 | 780a628f8f0ec8ba20e4c926fc83663b599bfd189764c76e25762633191086ea |
| admission_intent01.json | 738 | 21643a4fa79e506f75a93822fc4614591bc5f1d9e1025b9850cc78d2ff47fd75 |
| native_scope01.json | 7318 | 521c4b08549940aad5884ff90f52b89fe70f5a5ff11a5539f2f8254e1befe25e |
| native_scope_role_binding02.json | 2781 | bf85b1719bc033ec0f87aae3f9d7578a9dd93ab505460a4b6f966bf34294ca28 |
| native_driver01.py | 5099 | 029916bf63dc329323f11c7f8d0312711f860eb69e74a4315d37120cc42acb16 |
| inputs_static.json | 13493 | fc8e6fc1131c1952d5e1809f9dc6fb96763dd5e111749424e9ccfaec9b58d38c |

## Actual read-only admission

Both commands match the exact reviewed source bytes and complete ADB/Python argv, with 12765/2488 Windows UTF-16 units including NUL. They returned zero in 0.5880831/0.3533293 seconds, below their 75-second outer bounds, with empty stderr and no timeout/error. Independently decoded base64 streams agree exactly with saved text and observed JSON. First stdout is 11324 bytes / 70aca902c7accf559908e300dc5b1b9afd1b825cd584d385132f7e1aa6ff17c1; closing stdout is 301 bytes / 6fd3d5e2136d352d2e3f5b70e9cab9994127e89cbfac121d2e93a281fe8edad5. Preparation pin, initial intent and final local closure agree; first_error is null.

All 28 installed input names/hashes match the reviewed packet, with bounded regular-file sizes and matching recorded sizes/stamps. Initial and closing identity agree: Arduino UID/GID1000, Linux aarch64 6.16.7-g0dd6551ae96b, Python3.13.5, boot55c386b9-fe6d-4388-a7f4-1d91e0bb49d8. UID/GID four-tuples and saved triples are all1000; credentials are stable, and inherited file-size limits are unlimited. Neither observer sees the fresh remote owner, and neither process scan reports a conflict. The first bounded scan sees164 processes and no departed entries.

Observed free bytes are root2935209984, home13891117056 and temporary1921691648; available RAM3229184000 and free swap1924100096 are observations, not future guarantees. Root/home exceed the required1GiB. Independent closing repeats the home value, boot/CLI hash, absent owner, empty conflicts and UID/GID triples. Local free bytes before/after are6897881088/6897811456, above128MiB; both local owners remain absent and all224 checked pins close unchanged.

## Fixed scope and execution conditions

All current224 coordinator pins,17 scope-role file pins and130 manifest hashes match. The role map equals role_binding02 exactly: only the frozen interface's two obsolete freeze filenames are replaced by independent/coordinator03, with all17 role keys retained. Original interface and prior binding evidence remain untouched. Source/helper mapping is the already reviewed105 ordinary inputs to104 staged entries/764405 bytes with source identity9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a. No grant, firmware or source change occurred. The manifest's real helper/admission crosscheck and current byte checks remain applicable.

The admitted profile is solely app.ino, static/default startup, MATCH0, MOTORS_ALLOWED0, B4_STAND1 and all listed trial/diagnostic flags0. Attempt/local stage/remote owner are b4-app-m0-static01. Canonical source reuse requires exact full content/directory admission; no repair. The operation retains one60-second query, one jobs1 compiler with720-second deadline and5-second reap,1GiB board/128MiB local minima,30000-unit Windows limit including NUL, and all inherited source/tool/descriptor/intent/closing checks at use.

After checked successful compilation, only the two admitted source-payload chunks16384/11703 may populate the exclusive artifact-sources.zlib leaf (28087 bytes, SHA256901ff1d8657d74581f19543c87873402eccbc76867004b602f7b8755902d2f68). The32768 packed/262144 unpacked limits, complete source pins before execution, independent final read, partial-attempt observation and mandatory failure for uncertain completion remain as source/host-reviewed. No retry, upload, reset, MCU query, install, privilege escalation or cleanup is admitted.

The exact frozen native_driver01 retains isolated no-bytecode invocations and closed stdin. It checks prerequisite bytes and a clean40-hex Git HEAD before its sole local check-only (120-second outer bound); only a zero check result permits one execute (1800-second outer bound). Underlying caller saves its exclusive intent before dispatch. Outer outcomes preserve exact streams/base64/hashes and ordinary exceptions; failed check suppresses execute. After child exit, three independent checks retain input drift, prerequisite drift and HEAD drift while preserving the first error, then exclusively save native_invocations01.json. No outer receipt is created early enough to break the underlying clean-tree check.

Local stage, native_static01 and native_invocations01.json remain absent at this review. No native compile has happened. Accept exactly that one check/one conditional execute after root freezes the complete union of coordinator inputs, scope, role binding, actual admission/intent, driver and this final review into native_prerequisites01.json; verifies exact working/index/commit bytes; and reaches a clean committed reviewed HEAD. These are mandatory upcoming execution conditions, not claimed completed facts. Any prerequisite or check refusal stops the attempt; successful actual compile/artifacts/closure still require a separate result review. No firmware/runtime/physical acceptance or phase gate follows from this admission.
