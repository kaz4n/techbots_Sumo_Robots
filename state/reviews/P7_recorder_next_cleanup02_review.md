# D232 corrected fresh-owner cleanup review

FINAL conditional PASS for the corrected root02 package and the fixed sequence
below. The prior root01 package is consumed and is not accepted for execution.
No open material finding remains in this correction. Reviewed 2026-09-27;
the reviewer wrote only this report and ran no tests or native actions.

## Prior finding and correction

The earlier review `P7_recorder_next_cleanup_review.md`, SHA-256
`c75a9ead9c786a15b5d67490a40c00bcadde7f6d5ebca8df1f2df4852d63a71d`,
incorrectly accepted preparation containing stale inode 2281 checks in both
`absence_program01.py:17` and `stage_program01.py:17`. The reviewer missed these
executable guards: exact reversal of selected substitutions and correct embedded
recipe data did not establish that every necessary substitution had occurred.
That acceptance is superseded by this report and remains preserved unchanged.

Actual root01 absence receipt SHA-256
`2c38a1366cf3c864ed10b4a3cfc9ebc49bd84e14283f74682824c3b47f963cf7`
records exit1, empty stdout, the line17 assertion traceback, no closing errors
and successful local input closure. Inspection confirms this was before any
stage creation, authentication or deletion. The old source, review, intents and
failure evidence remain intact; root01 is not retried.

The new package at `state/analysis/P7_recorder_next_cleanup02_raw` corrects both
checks to the observed inode6292. It uses fresh remote owner
`/home/arduino/sumox26_codex_build/cleanup-recorder-next-root02`, regenerates the
four embedded source packets and five intents, and retains the same bounded
cleanup implementation. Recipe/projection behavior and source originals have
not changed.

## Verified preparation

Contract: 5041 bytes / SHA-256
`b8131b54994a1a309194d13af008148523b2b1ba6437ce6890620af40f9b41dc`.
Flat preparation manifest: 10219 bytes / SHA-256
`a6524df882d2d99aff1b57a17ba9e2fdbbb357962e68e457ab622d34df0e04a7`.
Independently recomputed all 51 pinned sizes/hashes with zero differences.

| Component | Bytes | SHA-256 |
| --- | ---: | --- |
| Recipe | 7723 | `4c6e8bbfecb10a42d9963a0159a3f3e869bbf9db5e9b13b4f09a099991f39059` |
| Wrapper | 9616 | `8090a0e47b8a2e7bb4ee0342bad63b84be7e9f892c57350c3a3aaec861085974` |
| Projected recipe | 7720 | `d002e6ad16e202c49c1cb3ef4b22f01bc4da3c0674f1dccfb155eb22d7d66755` |
| Dispatcher template | 6481 | `c07a59dafc5f6ff604bf483acb3f0a02cc4a08f711cb5f349fdfa3eb06d95742` |

Checked the executable bodies in all four programs and recipe/wrapper, rather
than relying only on derivation proofs. Both actual absence/stage inode
comparisons now equal admission `/directory_before/ino`; verification's complete
scratch stamp and all copy identities/hashes match that admission. Verification
and retrieval retain the exact observed originals. No stale operational D221
inode, old package, original path or old stage was found. Recipe device/owner
checks remain device34, UID/GID1000. Old literals retained in derivation history
are evidence, not executable target identities.

Also recomputed all seven complete reverse proofs to the accepted D226 source;
the corrected absence/stage derivations now include their missing count-one
inode replacements. All four packets decode to the exact current source bytes,
and source pins agree. Absence/stage intent argv contain those exact program
bodies, at 19104/19606 Windows UTF-16 units including NUL. Verify/retrieve remain
unbound templates. The fixed target remains exactly three D228 copies totaling
2359512 bytes in `/tmp/remoteocd` device34/inode6292, with admission hash
`17cfc318c40cbe01b95f824bea001a7aa03359b94bbae54119fa21830f627b99`.

Inspected eight passing saved local test methods. New coverage executes each
real complete pre-mutation scratch With block with substituted descriptor
results: inode6292 reaches inventory; inode2281 and inode6293 raise before
inventory. This is real guard execution with controlled dependencies, not a
claim that the full remote workflow ran. The additional AST audit covers all
programs, embedded sources and intent equality. Existing projection, corruption,
active-process and disappearing-handle refusal checks pass. No native call was
made by these fixtures. Reverse proofs alone are expressly insufficient.

## Conditional execution and evidence boundary

The accepted D226 implementation remains the guard basis: descriptor-relative
no-follow identity/content checks, retained originals, protected process scans
before each unlink, credential restoration before Arduino-owned deletion,
permanent drops, empty-directory-only removal and closing evidence. This delta
does not weaken or broaden any of them.

Root may bind exactly the two manifest/review hash placeholders, exclusively
save `native_dispatch01.py`, and verify reversal to the pinned template. Keep
ROOT at the isolated worktree; MAIN stays frozen. This mechanical binding and
the later stage/source stamp bindings require no additional review chain.

After all native jobs have closed, run the fixed actions once each, in order:
absence, stage, verify, authenticated, retrieve. Require each expected status,
exact sources/ADB/boot/scratch/original identity and every closing check before
the dependent action. Use only the fresh root02 stage/result owner and existing
no-clobber receipts, 70-second host/55-second remote bounds and 65536-byte reply
limits. Credentials enter protected no-echo stdin only, never files, argv or
environment. Preserve errors and consume any failed owner without retry.

Actual acceptance still requires strict reconciliation of original result
bytes, exact three removals, successful process/restoration checks, permanent
UID/GID drops, retained originals, independent scratch absence and closure.
This review proves corrected preparation only, not deletion or current process
clearance. No upload, MCU change, UART cause/delivery, motor authority, physical
acceptance or phase gate follows.
