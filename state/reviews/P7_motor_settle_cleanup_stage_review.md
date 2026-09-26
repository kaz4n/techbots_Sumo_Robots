# D200 independent stage verification

**Current disposition: PASS after separately authorized verification02.** The
original observation defect and failed verification01 remain preserved below
and in commit5cea956c. No production source, contract, staged file or pin was
changed. The completed correction and its evidence follow the historical
failure record.

## Preserved first attempt

26 September 2026, Asia/Dubai. **No staging-verification PASS.** The single
authorized nonprivileged verification call stopped on a defect in the
reviewer's observation program. This is not evidence of staged-source drift.
The separate same-model, reused-context reviewer `/root/fresh_review` made no
authentication, cleanup, firmware or MCU call and performed no board mutation.
The failed receipt was preserved; no retry was made.

The prior source/host review remains
`1ebd7342b31d3baa7bca04eb3c0d43123c5d4e3cac9f2400b6ca61ec2a7d2ea0`.
The coordinator's staging receipt is 2471 bytes, SHA-256
`5884a8d2f3189d42598f46e3aac4bf37f5dabeaaa3987a01a8948898768cd2e1`.
It records one successful creation of cleanup-app-settle-root04, directory
device66341/inode272573, mode0700, UID/GID1000, and exactly three sources
totaling 50664 bytes. Fresh absence receipt
`83913618afbb11a061c9d46e90402f58479808ea09ec354ff49d806b4b034a58`
preceded that staging call. These coordinator observations do not replace the
incomplete independent verification.

`state/analysis/P7_motor_settle_cleanup_raw/cleanup_stage_verification01.json`
is 30404 bytes, SHA-256
`f0ca0f685aeb77b9340d19c80e1242f073b824ff993200f3ff34f5b338b8e05b`.
It saves the exact argv, program hash, input provenance, stdout and stderr.
The one transport returned1 in 0.366 seconds, with empty stderr. Its 1037-byte
stdout reports `FAILED` and first error `KeyError: 'cleanup_remoteocd03.py'`.
The host envelope separately records its consequent nonzero-exit assertion.
The remote receipt confirms the expected full board identity/boot, initial
UID/GID triples1000 and successful root-directory descriptor closure. It has
no completed stage, scratch or original snapshot; local input closure was not
reached. Those incomplete checks must not be treated as PASS.

The observation program retained the checked D196 read-only template bootstrap
and current three pinned source definitions. Its requested additional stage
snapshot incorrectly called `recipe.inventory` with the staged source names.
Local inspection of cleanup_remoteocd03.py:81-91 confirms that the third
argument supplies only names: the function resolves each file's content pin
through the recipe's global scratch-only `PINS`. Thus the first sorted staged
source name raises KeyError before its content read. No wrapper or recipe
main, process scan, privilege transition, unlink or directory mutation was
called. The failure does not imply any product-source defect or require
changing the source, contract, staging owner or their pins.

The narrow repair is to restore the original D196 explicit staged-file read
loop, using the staged-source pin table and before/after full stamps, while
keeping recipe.inventory only for scratch names. Any subsequent verification
requires a separately scoped call and a new receipt; preserve verification01.
Complete independent stage/scratch/original close-and-reopen checks, exact
result_root04.json absence and final identity/credential closure remain
pending. Protected process-use clearance belongs to the later authenticated
cleanup scan. No authenticated invocation readiness or deletion conclusion
follows from this review.

## Separately authorized correction and actual closure

At 06:50:01 UTC, the reviewer performed exactly one additional nonprivileged
read-only call under a new explicit scope. The only remote-program change was
replacement of the incorrect staged-source inventory call with the D196
explicit source read/hash loop plus opening/closing full-stamp comparison.
The actual saved program comparison confirms all other bytes unchanged.
Scratch inventory continues to use the original recipe function. No wrapper
or recipe main, protected-process scan, credential change, cleanup or MCU call
was made; no automatic retry followed either call.

`state/analysis/P7_motor_settle_cleanup_raw/cleanup_stage_verification02.json`
is 39917 bytes, SHA-256
`2c7a1ad2955f4835c05f289ca63bba25a210772c51cd65750ada997c7d4699bb`.
It preserves exact argv and raw streams, the one-loop correction, predecessor
and input bindings, and before/after evidence. The 24340-byte remote program
hashes to `a074de232336de205452e94f8f3fd9369ce8d2d165dffd55c3677d42b469896f`;
the command has 27655 Windows units. Python -I -B, the 55-second alarm and
70-second transport bound remain unchanged.

The transport returned0 in 0.442 seconds, with empty stderr and no host or
remote first error. Its 8606-byte stdout hashes to
`afa7f16b79581f00d8bee98d12bab0c3ea99b5093138244080e7ef1daf88c45f`
and reports `STAGED_FILES_VERIFIED_NOT_EXECUTED`. All six closing checks PASS:
stage reopen, scratch reopen, retained-original reopen, full board identity,
credentials and root descriptor close. Local source/ADB input closure PASS.
The reviewer reread this receipt and independently compared each complete
before/after snapshot and its stream hash/length.

The stage's full stamp matches the actual creation receipt: device66341,
inode272573, directory0700, UID/GID1000, nlink2 and unchanged size/timestamps.
Exactly three regular0600, single-link, UID/GID1000 files total50664 bytes:
cleanup_root04.py inode272574/9603 bytes/`13f33327...`, cleanup_remoteocd03.py
inode272575/7740 bytes/`6afeea1b...`, and static_remote.py inode272576/33321
bytes/`8ba9b190...`. Their complete hashes match the prior reviewed pins.
Close-and-reopen file/directory stamps and bytes agree. Explicit no-follow
result_root04.json checks find it absent in both stage snapshots.

Scratch directory device34/inode1172 and all three child full stamps/hashes
match the prior admission and remain identical on reopen. Its payload total
is2399768 bytes: observer package95360/`85b05c56...`, flash configuration680/
`38706cee...`, and loader2303728/`39d4a4fd...`. Every retained original was
independently opened and checked twice, with matching full path stamps,
descriptor identities, lengths and complete hashes; all agree with the
admitted originals. Full board identity is unchanged, including boot
55c386b9-fe6d-4388-a7f4-1d91e0bb49d8. Real/effective/saved UID and GID triples
remain1000 before and after the entire observation.

This closes the independent staged-source/content verification prerequisite
for the fixed D200 cleanup. A separately admitted one-shot authenticated
invocation must still use the unchanged fixed root04 wrapper, exclusive
result_root04.json, 70-second outer bound and its runtime identity/content/
protected-process/credential guards. This read-only result supplies no current
protected process-use clearance, deletion or permanent-drop result; those
require the actual authenticated receipt and its separate review. No broader
privileged access, owner reuse, automatic retry, firmware operation, physical
acceptance or phase gate is implied.
