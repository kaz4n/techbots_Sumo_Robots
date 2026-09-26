# D223 UART holder observer: source, host and native admission

Date: 2026-09-26. Independent fresh-context review. The reviewer read source and
saved host evidence only; no observer import/execution, authentication, board
command, UART open or MCU operation was performed by the reviewer.

## Findings

No open BLOCKER or MAJOR finding in the reviewed scope. Pre-test findings were
closed before the accepted runs:

- Output-limit fallback now counts its cap and retains per-sweep aggregate
  counts, observed completeness and explicit omitted-detail/holder counts.
- Reaching the global FD budget before remaining tasks now records the
  unvisited tasks and makes that sweep incomplete.
- The alarm explicitly restores SIGALRM's default disposition. Executable
  command paths are absolute. Authentication fails closed on GetPassWarning,
  so the fallback cannot request an echoed password.
- Launcher closing checks retain individual pin failures instead of losing the
  transport record at the first missing or changed input.

## Reviewed inputs

Paths are relative to the repository. SHA-256 values identify the accepted
current files, also recorded in `state/analysis/P7_uart_holder_raw/host_inputs02.json`.

| Input | Bytes | SHA-256 |
|---|---:|---|
| `tools/observe_uart_holders.py` | 14011 | `f2d8e4e7bf3a128350f17337decb352b1cb18de94c7d36e8557aaa76031502fb` |
| `state/analysis/P7_uart_holder_contract.md` | 3184 | `b2c058f04ae5c595662522dc2edbb6a803b626ea2188f0ad15ad9b99b9a93d01` |
| `tests/tooling/test_uart_holder_observer.py` | 13888 | `1ea6116205f1ddabfbcb32f1c46a03236f10dcfb78918309c30310a389336566` |
| `state/analysis/P7_uart_holder_raw/authenticate_observation01.py` | 5807 | `39a03613fb42c9f3a4dc16e1b6fcf04690bdb48f3b3b377a2b26bdb321e677cc` |

## Source and host evidence

The operation set is restricted to small fixed proc metadata, stat metadata,
executable identity metadata, the identified router's bounded regular-file
executable hash, and fixed `/usr/bin/systemctl show arduino-router.service
--property=MainPID --value`. It never opens the UART, reads FD payloads, reads
other executables' bytes, reads cmdline/environment, changes services, sends
router RPC or touches MCU state.

Both sweeps enumerate process and task FD tables, including private thread
tables, and bracket process/task start times and name lists. Denied, vanished,
replaced, capped and expired observations become incomplete. Numeric directory
enumeration is bounded while iterating. Only the observer's own proven directory
handles matching the enumerated FD directory's device/inode are excluded; those
handles cannot be UART holders. Their stat calls consume the same actual FD-stat
budget. The per-sweep limits and the whole-process 45-second alarm are explicit;
absent output or abnormal termination remains indeterminate.

The independent oracle checks private-thread holders and stable absence;
permission/disappearance at each metadata layer; PID/TID, name-set, holder and
boundary changes; enumeration caps; the exact global FD-budget seam; deadlines;
error-detail and holder bounds; serialized-output loss; and nonroot/extra-argument
refusal before metadata construction. Static source inspection additionally
checked real enumeration and self-directory exclusion. These are synthetic host
checks, not evidence of actual protected board descriptor visibility.

Saved results under `state/analysis/P7_uart_holder_raw/`:

- `first_windows01`: original 16-method run had 15 passes and one fixture error.
  The changed-set fixture announced FD 9 without metadata and raised KeyError.
  The narrow correction supplies a non-UART FD and avoids duplicate names; the
  changed-set rejection assertion is preserved. Production files did not change.
- `first_windows02`: 16 passes, no skips, return code 0; 0.897415 seconds outer.
- `first_linux01`: 16 passes, no skips, return code 0; 21.131976 seconds outer,
  1.912 seconds reported by unittest.

Both accepted receipts report no changed inputs. The reviewer read the test
source and saved outputs, independently checked current source/test/launcher
hashes, and reconciled saved stdout/stderr hashes with both accepted receipts.
Empty stdout and stderr hashes `3750a7ff...` (Windows) / `89789af9...` (Linux)
match. No reviewer rerun or extra board observation was needed.

## Native admission and evidence boundary

PASS for one fresh D223 invocation through the reviewed launcher, conditional on
its existing checks: the intent must contain exactly these four file pins plus
this sealed review's pin, reproduce `command(SOURCE.read_bytes())` exactly, bind
ADB serial `2629958581`, and retain the fixed 65-second timeout. All invocation
owner/output paths must be unused. The launcher also verifies its fixed local
ADB binary hash and rejects changed inputs before use.

The admitted argv is the fixed ADB `shell -T` command carrying
`/usr/bin/sudo -k -S -p '' -H -- /usr/bin/python3 -I -B -c` and only the compressed
reviewed observer source. Password input is obtained with no echo, passed only
through native stdin and omitted from files, argv and logs. There is no reused
cleanup session or generic root operation. A create-exclusive invocation marker
consumes the owner before authentication. Timeout records remote completion as
indeterminate and provides no retry path. Later interpretation must inspect the
actual receipt and transport outcome separately.

`SAMPLED_COMPLETE` requires complete/stable boundaries and both sweeps with equal
sampled holder sets. Same-number FD reuse or transient changes between reads,
including process exec without PID/start-time change, remain outside continuous
proof. `continuous_exclusivity`, `framing_clean` and `receiver_ready` remain
`UNKNOWN`, even for complete scans or no observed holder. No UART setup grant,
last-close/DMA completion, reopen/delivery proof, motor authorization, physical
acceptance or human phase gate follows. Mandatory motor inhibition is unchanged.

## Verdict

FINAL PASS for the source/host scope and the single conditional native admission
above. Actual board visibility is not yet observed by this review. The next
action is the exact one-time observation and separate interpretation of its
receipt, without expanding readiness or exclusivity claims.
