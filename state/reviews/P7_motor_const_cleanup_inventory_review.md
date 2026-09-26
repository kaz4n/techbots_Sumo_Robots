# D201 scratch inventory observer source review

26 September 2026, Asia/Dubai. Separate same-model reviewer. This new file is
the only owned output; all D204 reviews and prior sources remain unchanged.
Inspection was limited to source/data reads, AST inspection, hashing and
literal byte comparison. No subject, test, compiler, device transport, inventory
or cleanup was executed by this reviewer.

**FINAL PASS for one nonprivileged read-only inventory using the fixed new
observer. No open material source finding.** This accepts observation only.
It establishes no current scratch contents, process-use clearance, cleanup
permission, privileged capability or reclaimed storage.

## Exact derivative and package identity

The subject is
`analysis/P7_motor_const_cleanup_raw/observe_admission01.py`, 9769 bytes,
SHA256 `462c0534826b19d0722f86c69444a61bc55309514d7741ce196f40292a85ecd8`.
Its derivation receipt is 3615 bytes,
`d2537c7470b2dfc80d65d4aee1c656a17edecacf5aeb1b0e56991dcb9e4f97df`.

Independent reconstruction confirms exactly five ordered, single-occurrence
literal substitutions from the 9770-byte approved D200 observer,
`e4db653bf71bb2201549ea0ade3d637521520d6e2e9747473cf52fd6688aaa83`.
Every intermediate byte count/hash agrees with the receipt, and the complete
result exactly equals the actual new source. The changes are the D201 scope
label, package size, package digest, retained build owner and matching-result
key. No operational function, branch, command, bound or file-reader guard is
otherwise changed.

All five derivation input pins independently rehash unchanged: predecessor,
D198 artifact packet, accepted D201 actual review, fixed descriptor helper and
upload source. The accepted D198 artifact packet identifies the D201 flashed
package as 95520 bytes,
`e400078166394d0f8ea44b601e9ba2948992c4f263c5c7ee5fb3942433c143d0`,
at
`/home/arduino/sumox26_codex_build/app-motor-settle-static01/build/app_motor_observe.ino.bin-zsk.bin`.
The accepted D201 review records the corresponding completed inhibited upload
and full packaged-sketch flash comparison. D204 did not upload a new image.
The retained basename is correctly **app_motor_observe.ino.bin-zsk.bin**;
the build-owner name changes to settle without changing that basename.
The unflashed D203 package is not the inventory's matching target.

## Bounded read-only operation

The fixed output owner
`analysis/P7_motor_const_cleanup_raw/admission01.json` is currently absent,
independently checked with lexists semantics. The observer refuses an existing
owner, requires Python-B and no CLI arguments, and writes its new evidence
file exclusively. It checks the pinned helper and ADB before dispatch and
again after a successful observation. Local free space must be at least
128 MiB and the submitted command at most 30000 UTF-16 units.

There is exactly one fixed ADB transport to serial2629958581 under a minimal
environment and remote Python-I-B. stdin is DEVNULL. The outer timeout is
60 seconds and remote alarm 45 seconds. No password, authentication prompt,
sudo, credential mutation, compiler, upload, reset, MCU operation, unlink,
rename or deletion command occurs in the observer's reachable path.

The remote helper is length/hash checked before private definition loading.
Its invoked directory/file routines use descriptor-relative reads, plain
directory traversal, O_NOFOLLOW and nonblocking file opens with identity
checks. The helper's broader functions are definitions only; its main dispatcher
is not invoked by this private loading or the observer.

The observer reads the three fixed retained originals and `/tmp/remoteocd`.
Scratch observation allows at most eight names and requires regular, single-link,
positive-sized files no larger than 4 MiB. It rechecks full directory/file
identities, descriptor identities, byte counts and hashes. All three originals
are independently reread for closing equality. No historical inode is embedded:
device/inode/mode/uid/gid/link/size/mtime/ctime values are freshly collected.

Expected identity is the pinned nonroot arduino account, kernel, architecture,
boot and Python tuple; real/effective/saved UID/GID must each remain1000 at
admission. The final identity must equal its opening observation. Process
inspection is limited to at most4096 PIDs and bounded status/cmdline/comm reads;
it does not inspect protected cwd/fd handles or establish process-use clearance.
Process-inspection errors remain visible in the result. The remote JSON reply
and accepted outer streams are bounded at65536 bytes, with raw streams and
first error retained in the fresh local receipt.

## Required interpretation after observation

`OBSERVED` means the read-only observation completed. It is intentionally not
proof that the originals match or that scratch contains exactly the three
expected D201 copies. Those facts are separate booleans:
`expected_originals_match` and `exact_three_d201_copies`. An absent scratch
directory or different regular files may therefore produce OBSERVED with a
false matching result; that is useful evidence, not cleanup admission.

The coordinator must independently inspect both booleans, their exact file
bytes/hashes, full identity closure, first errors and process-visibility limits
before proposing any subsequent action. Even both true booleans do not grant
privileged process-use inspection or deletion authorization. Any later cleanup
requires its own fresh exact scope and review; no old cleanup owner, inode or
permission is reused here.

Preserve the one inventory's raw receipt and any failure; do not silently rerun
or convert read-only success into cleanup. This reviewer has stopped writes.
