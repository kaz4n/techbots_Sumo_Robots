# D190 human-invoked cleanup root02 contract

This replaces only the proposed separate-observer design, not cleanup01's
historical source/receipt. Current sudo-n visibility query failed; no agent may
invoke this wrapper as root. After independent tests/review and exact staging,
the human may run one fixed command with their existing sudo authentication.
No password is requested from the human in chat or read by tooling.

Fixed stage: `/home/arduino/sumox26_codex_build/cleanup-app-inert-root02`.
It contains `cleanup_root02.py`, unchanged `cleanup_remoteocd01.py`7873bytes/SHA
`23ef85ae3c386cc76751eea0fb18a90148a6fe513e3e8c753d527c06efcbbe95`, and unchanged
`static_remote.py`33321bytes/SHA
`8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8`.
No other dependency, new helper framework, arbitrary argument or path is allowed.
Preserve cleanup01's failed receipt and every old source/test.
The human command uses absolute `/usr/bin/python3 -I -B`; isolated mode prevents
user-writable stage files from shadowing standard-library imports. A parent-shell
noclobber redirection preserves the new stdout receipt and rejects reuse:
`( set -C; sudo -H /usr/bin/python3 -I -B /home/arduino/sumox26_codex_build/cleanup-app-inert-root02/cleanup_root02.py > /home/arduino/sumox26_codex_build/cleanup-app-inert-root02/result_root02.json )`.

## Minimal privilege arrangement

The original helper refuses root identity and requires Arduino ownership in its
home/build hierarchy. Do not modify or override those checks. The wrapper loads
the two exact dependencies without executing either main. Before loading the
cleanup module it projects exactly one original observer fragment
`                except FileNotFoundError:\n                    continue\n`
to `                except FileNotFoundError:\n                    raise\n`.
Require exactly one match and projected7870bytes/SHA
`51286ad414794e82f3161bed16cbb47dca421e831316e053a7eab967469f602e`.
All other original bytes remain unchanged. Missing cwd/FD now reaches the
inherited outer PID-existence recheck; any surviving PID fails, including the
conservative case of an FD closed during inspection. Original files stay intact.
The wrapper then starts cleanup main after real/effective UID and GID become1000, retaining
saved UID/GID0 temporarily. Clear supplementary groups to exactly[1000]. Only
the original module's `processes` callable is replaced by a wrapper: it changes
effective UID0 for that projected read-only function, then restores effective
UID1000 in a finally block and verifies the full UID/GID triples before return.
There is no child process and original self-exclusion remains exact.

Every original directory/file/hash/identity/original-retention, process bound,
native-name, open-FD/cwd use, deadline, failure and deletion guard remains.
Denied elevated inspection still fails; never exempt adbd or any other PID.
All original cleanup filesystem mutations run with effective UID/GID1000.
The wrapper finally drops real/effective/saved UID/GID permanently to1000; it
attempts both drops independently and records errors. If terminal drop fails,
the wrapper returns failure and exits without any further cleanup operation.

## Public isolated-test interface

The module is import-safe and imports only standard-library modules. No board
action, process credential change or deletion occurs during import. Functions:

- `require(condition, message)` raises ValueError on false.
- `credentials()` returns `{'uids': list(os.getresuid()), 'gids': list(os.getresgid())}`.
- `read_source(name)` reads only either fixed dependency basename from `STAGE`.
  Traversal uses directory FDs/O_NOFOLLOW; root/home ancestry and dependency
  records must be plain, required owned directories remain UID1000, dependency
  UID/GID1000/nlink1/size/hash and unchanged stat stamps are required. It returns
  bytes, attempting closure of every opened descriptor even after a close
  failure; preserve primary error, otherwise first close error. No
  path/symlink/size/hash substitution.
- `load_cleanup()` returns `(original_module, helper_bytes)`, from exact
  `read_source` inputs and the sole count/hash-checked projection above;
  original module name is not `__main__`. Public `PROJECTION_OLD`,
  `PROJECTION_NEW` are exact bytes and `PROJECTION_SHA` pins projected source.
- `enter_user()` requires UID and GID triples(0,0,0), clears groups[1000], sets
  GID then UID triples(1000,1000,0), and verifies both triples.
- `observe(original, records)` requires UID/GID triples(1000,1000,0); raises
  effective UID0, verifies UID(1000,0,0) and unchanged GID triple, calls original
  once, then always attempts EUID1000 restoration and verifies both triples.
  Each call appends a record with before/during/after credentials, result when
  available, and `errors` list of `{stage,type,message}`. It propagates the
  first error, preserving scan and restoration errors in that record.
- `drop_privilege()` independently attempts setresgid(1000,1000,1000) and
  setresuid(1000,1000,1000), verifies resulting triples, returns a list of
  `{stage,type,message}` errors. No saved0 survives a successful drop.
- `execute()` returns the wrapper result dict without printing. It requires
  exactly no extra argv, Python-I-B, and root UID/GID triples; loads dependencies,
  enters user state, replaces only `original_module.processes` with `observe`,
  and calls original main exactly once using the unchanged compressed helper
  argument. It captures original stdout as `cleanup_stdout` before attempting
  strict JSON decoding into `cleanup_result`. It restores sys.argv. Its finally
  always drops privilege after initial-root admission, including load/enter/main
  exceptions, while preserving original first error and any raw/partial output.
  It requires original return0 and status REMOVED_EXACT_STALE_COPIES, plus
  verified terminal UID/GID triples and no privilege errors, to report success.
- `main()` prints the execute result as compact JSON and returns0 only for
  wrapper status REMOVED_EXACT_STALE_COPIES; otherwise1.

Result schema: `d190-human-root-cleanup-v2`; fields `status` (FAILED initially),
`source_pins`, `source_projection` (`count:1`, `before`, `after`,
`projected_sha256`), `initial_credentials`, `final_credentials`, `observations`[],
`cleanup_stdout`string, `cleanup_result`dict-or-null, `cleanup_returncode`,
`first_error`dict-or-null, `privilege_drop_errors`[]. Original result remains
nested intact, including its schema, removed list and original first error.
Wrong initial root admission fails without invoking cleanup or changing IDs.
The wrapper's own credential/loading failures are distinct from cleanup errors.

## Required evidence and limitations

Independent controlled tests must cover credential entry/restore/permanent drop,
scan+restore dual failure, wrong identity/source/arguments, dependency load and
main errors, original failure/partial receipts, elevated denial/use rejection,
and that every original mutation occurs EUID1000. Check projection count/hash,
surviving missing-link rejection and departed-PID acceptance. Original functions
other than the projected and wrapped observation callable remain unchanged.
No actual root command is part of automated tests; injected credential/proc/file
fixtures provide host evidence only. Separate source and actual-staging review
precedes the human command. This does not prove access will succeed on the board.

Linux semantics: [setresuid(2)](https://www.man7.org/linux/man-pages/man2/setresuid.2.html)
sets real/effective/saved IDs and filesystem UID follows EUID;
[seteuid(2)](https://www.man7.org/linux/man-pages/man2/seteuid.2.html) allows a
switch to a saved UID. Python errors and post-call credentials must be checked.
Observations remain racy; this does not add locking, physical evidence or a gate.
