# D212 read-only admission preparation review

Verdict: PASS as preparation for one nonprivileged read-only admission observation, conditional on the separately required source/host acceptance. This review neither executes the query nor admits the later firmware upload/capture. Separate same-model reviewer with reused context, 2026-09-26. Only local source, AST/literals and saved evidence were inspected; no subject import, test, device command, compiler or credential access occurred.

## Exact construction and bindings

The prepared program `admission01_readonly.py` is 23,798 bytes, SHA-256 `c00a07512417508cc32566aa7469ba8ec22aceab90ed3faa060fb94c241d3c27`. `admission01_derivation.json` is 6,115 bytes, `7cb3e5ce9c225977f4a7ea72fc338080a6cf10964d3b2dcc71eea3619da9a827`. The saved intent is 34,188 bytes, `d51f1ff13e2141f6241bc63e3e920b265eabb8c96ec75605b8d4eddc8e19163a`.

I independently reconstructed the program from the accepted D207 admission program (23,886 bytes, `769933e9baa0c0b9fa61dc72017bd3585a8680f9e3238fe65b362a60fb2fc198`). All ten counted metadata steps and every intermediate whole-program size/hash match: two decision labels, complete source pins/packet/file-table assignments, recipe name, stage path, result name, exact completed cleanup result size/hash and the fresh run owner prefix. The three assignment replacement substrings were separately size/hash checked. Final reconstructed bytes equal both the saved program and the command's embedded Python text. Operational statements and guards are otherwise unchanged.

All eight intent input pins match current files. The source packet was decompressed as data and its three complete byte strings match the accepted D211 root06 wrapper, recipe05 and static helper. The expected cleanup result is the exact accepted 6,376-byte raw receipt `0930bc902f92c1eb7e03084abbb045c57690388949b98f62bb49d7b720d1c710`; its actual review `467923541391dbbeca61c063b5315fc640760701effaee6289b9ac7c58206fd5` is pinned. No pending or invented cleanup result is used.

The fixed file table contains exactly 19 entries. Eighteen are the deduplicated union of the exact upload/capture file bindings in preparation `3f65a84a5cd856b021357e16e601c7bed27afaecead6e21e0558a2ce0ca3384e`; duplicate paths have identical metadata. The nineteenth is the unchanged historical `p0_capture.py` file pin. In particular the ordinary raw image is 92,928 bytes, `6f5f531b114219d712d857b4ac89ad161ceb217211207788a27443b7d4ab6db7`, and the ordinary packaged image is 92,944 bytes, `7fa9d41da043931e1237712e1e88bda4151c82933af2ecec97ce3a02184d23ad`, under `/home/arduino/sumox26_codex_build/ordinary-app-static01/build/`. Installed loader, tools and configuration pins are retained; diagnostic firmware paths are not substituted as the ordinary image.

## Read-only behavior and limits

The fixed ADB command uses the reviewed board serial, isolated `/usr/bin/env -i` arduino environment and `/usr/bin/python3 -I -B`. Its independently computed size is 26,057 UTF-16 units including the terminator, below the unchanged 30,000 ceiling. The outer bound is 70 seconds and the remote alarm 55 seconds.

The future program validates every packet size/hash before privately loading the helper and recipe under non-main module names. The root06 wrapper remains data. It reads the saved result through the retained descriptor-relative helper and checks exact bytes/hash before its status/error check. Thus that small status check does not substitute for the already completed strict cleanup review. It checks `/tmp/remoteocd` absence, rereads all three staged sources and every retained original, and reads/hashes each of the 19 fixed board files without executing any of them.

Four absence paths are checked: `/tmp/remoteocd` and the fresh `ordinary-app-9044ebbb-run01-` adapter, upload and capture directories. This is four paths, not four new native owners. It does not remove or claim an owner. The later native profile's complete 14-item absence list is unchanged and remains the native caller's separate responsibility.

The helper's unchanged bounded process inspection must return an empty conflict list. It enumerates at most 4,096 PIDs and distinguishes a departed process from inspection failure for a still-existing process. No privileged scan is requested. Resource inspection records available RAM plus root and temporary-filesystem space; this preliminary query explicitly requires only root available space of at least 1,073,741,824 bytes. It does not by itself establish every later native resource predicate.

The full board identity must match the pinned recipe identity, and is checked again before output. Existing checked-directory traversal and bounded no-follow file reads preserve their opening/closing descriptor checks; the root descriptor closes in finally. There is no compiler invocation, upload, reset, capture, MCU access, cleanup main, authentication, write, unlink or owner creation in the program.

## Evidence boundary and next step

No material preparation finding remains. This program supplies fresh board-file, identity, conflict, resource and four-path absence observations only. It neither replaces the native caller's clean-head/source/scope/owner admission nor proves the target is running the ordinary image. It does not implement a second full-file reread at the end, atomic multi-file observation, protected-process clearance, or a guarantee against subsequent changes; the retained native lifecycle must recheck its own requirements.

After source/host acceptance and unchanged-input validation, the coordinator may perform the single saved read-only admission query and preserve its exact argv, streams, outcome and local closing pins. A failed or interrupted query remains evidence and does not authorize a retry, firmware operation or a weakened guard. Fresh successful admission must be reviewed separately before freezing the later runtime scope.
