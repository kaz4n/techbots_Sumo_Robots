# D211 actual staged-source verification and cleanup admission

Verdict: PASS for the actual nonprivileged staged-source verification and admission of one exact authenticated cleanup invocation under the existing user authorization recorded in D211. This review is not a cleanup-success receipt. Separate same-model reviewer with reused project context; reviewed local saved bytes and source only. No test, device command, credential access, authentication or cleanup execution by the reviewer. Date: 2026-09-26.

## Actual verification

`cleanup_stage_verification01.json` is 10,044 bytes, SHA-256 `38a7b718ecbd87a8faa19f898abb6864a8f9d1ed3b7ec236a20aa3063e6397dc`. It binds the reviewed intent `9701e74de3f2e052b7a68ce33de46b255f2a5b00996da61bee58da0156637b5e`; return 0, elapsed 0.4919313 s, null first error, empty stderr, and local input closure PASS. Recomputed stdout SHA-256 is `c9170d942f921f3b87a3f94f7695c09f5875b1de00c5f8b92ef94a3fb8aca3b8`; the empty stderr digest also matches.

The nested schema is exactly `d211-independent-stage-verification-v1`, status `STAGED_FILES_VERIFIED_NOT_EXECUTED`, first error null. All six named closing checks pass: stage reopen, scratch reopen, originals reopen, board identity, credentials and root descriptor close. I independently compared complete opening/closing records and the expected values embedded in the reviewed intent, rather than relying only on the status.

The exact stage `/home/arduino/sumox26_codex_build/cleanup-ordinary-app-root06` remains device 66341/inode 273931, mode 0700, UID/GID 1000, nlink 2, size 4096, ctime/mtime 1790431982620557031 ns. Its only three files remain regular, mode 0600, single-link, UID/GID 1000, with unchanged full stamps, exact sizes and source hashes:

- root06: 9,607 bytes, `290a7236dc7cc5c6b679a72d5864fb99408dd21bbd30b7b8f3edf74c0fe10aa3`, inode 273932.
- recipe05: 7,740 bytes, `1a59d4b2fc12a0b74a81f65847d7384002423882bd42f5242a98774c8bc02958`, inode 273933.
- helper: 33,321 bytes, `8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8`, inode 273934.

`result_root06.json` is absent on both reads. Full board identity is unchanged, including boot `55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`; real/effective/saved UID and GID triples are all 1000 before and after. Scratch `/tmp/remoteocd` remains device 34/inode 1732 with exact directory stamp and precisely these three copies: current D207 package 95,368 bytes (`f15c7ce1f0ff5fea2d44d0b60f0607f9adae22b83ba5043fe4de5e2b21fa26f7`), configuration 680 bytes and loader ELF 2,303,728 bytes. Total eligible scratch content is 2,399,776 bytes. Both complete scratch inventories and all retained original path/descriptor/content/full-stamp records equal the preceding admission evidence. All 69 coordinator-frozen local files were rehashed again and remain exact.

The explicit `process_use_clearance: false` is correct. These file observations do not replace the protected process scans at deletion time, nor guarantee an absence of concurrent changes after observation.

## Exact invocation admitted

`cleanup_authenticated_intent01.json` is 1,413 bytes, SHA-256 `8be7c55962424322e4c9729a2cb9f554e80b8d93b2b59903155974646c81b003`. Its predecessor intent is the unchanged D206 1,406-byte file `cee3ab13e599bddf33e9f8d0f945dd1f242910c03272d77e03b638413204bda1`. I compared the full argv: only the stage, wrapper basename and result basename metadata change. Fixed ADB serial 2629958581, `shell -T`, 70-second outer timeout, and credential handling remain unchanged.

The remote shell command is exactly:

```sh
set -C; sudo -S -p "" -H /usr/bin/python3 -I -B /home/arduino/sumox26_codex_build/cleanup-ordinary-app-root06/cleanup_root06.py > /home/arduino/sumox26_codex_build/cleanup-ordinary-app-root06/result_root06.json
```

The result is created by the nonprivileged shell with no-clobber behavior before sudo starts. An existing result prevents the invocation; it must not be overwritten. The stated credential route is a Windows no-echo console to native stdin only, never an argv, stored receipt or source field. No credential was inspected for this review. The intent binds the exact wrapper, source/host review, verifier preparation review and completed staged verification. It specifies one invocation, no additional elevated command and no retry. This is a concrete admission within the parent's recorded existing user authorization, not a grant of general privileged access.

## Retained runtime conditions and acceptance limits

The source/host review `f033655ea6d72c14b092958e73b885887e56d3b57ad1f4fcb198365103dc1713` remains applicable. I reread the current invocation, private recipe loading, credential observer and deletion sequence. The root wrapper verifies staged recipe/helper through the unchanged descriptor/source guards; it applies exactly the pinned count-one missing-readlink `continue` to `raise` correction before loading the recipe privately. The outer surviving-PID check therefore remains fail-closed for still-existing processes.

Initial UID/GID triples must be root. The wrapper sets supplementary groups to [1000], real/effective GID and UID to 1000 while retaining saved root. Each of the three protected process scans temporarily elevates only effective UID; its finally block must restore the full Arduino user credential state before deletion proceeds. All unlinks and the final empty-directory removal execute in that user state. Per-file fresh process/identity/inventory checks, the exact scratch directory identity, original hashes, directory replacement checks and fsync behavior are unchanged. Failure retains partial evidence and the original error; admitted root execution independently attempts permanent GID/UID drops in finally and records drop errors. The original recipe's 55-second alarm and outer 70-second bound remain.

The next eligible operation is this single saved authenticated intent. Even transport exit 0 will require a separate read-only retrieval and independent actual review. That review must inspect both outer and nested schemas, the exact three removed content pins, all three protected scan observations and restorations, retained originals and board identity, no first/close/drop errors, final UID/GID triples all 1000, and `/tmp/remoteocd` absence. `run_original` itself checks a dictionary, return code and success status; it does not perform the complete nested schema validation, so coordinator acceptance must do so. No deletion or firmware change is claimed here.
