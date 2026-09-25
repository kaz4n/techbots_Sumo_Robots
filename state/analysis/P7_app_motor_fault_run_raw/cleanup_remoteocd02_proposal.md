# D190 cleanup visibility failure and bounded correction proposal

Status: PROPOSAL ONLY. No new cleanup executable, board operation or deletion
is authorized by this document. Preserve cleanup01 and its original review.

## Observed failure

The original source SHA256 is
`23ef85ae3c386cc76751eea0fb18a90148a6fe513e3e8c753d527c06efcbbe95`.
The result receipt SHA256 is
`e382b267a1cf9af53f6bd8ec17b15d3c75d20270b70bab809179bee7898f5a3f`.
It returned 1 with `PermissionError: /proc/637/fd`, `removed=[]`,
`directory_removed=false`, and `use_checks=[]`. Original file verification and
the full initial scratch inventory succeeded before the first process-use
check; closing identity and original-file verification were not reached.

Root's separate read-only reconnect receipt
`reconnect_20260925_2035.json`, SHA256
`740208fad419cd00a2c57e44811845b7f1a8ea7876b1ad38303e7de8580ec95b`,
reports PID637 `adbd`, all real/effective/saved/filesystem UIDs and GIDs1000,
readable comm/status, and denied fd/cwd access. Identity/boot remains the pinned
board. No recognized native uploader/debugger name was present in that
observation. This is not an absence-of-use proof for adbd.

The immediate cause is an unfulfilled process-visibility precondition. It is
not evidence of incorrect scratch content. Linux applies a ptrace access check
to proc FD and cwd symlink reads, so matching UID alone does not prove access.
Dumpability or an LSM rule can deny access; the exact kernel reason on this
board has not been measured. Primary references:
[proc_pid_fd(5)](https://www.man7.org/linux/man-pages/man5/proc_pid_fd.5.html),
[proc_pid_cwd(5)](https://www.man7.org/linux/man-pages/man5/proc_pid_cwd.5.html),
[ptrace(2)](https://www.man7.org/linux/man-pages/man2/ptrace.2.html).

Historical read-only evidence in
`../P2_native_dump_bare_feasibility.md` records `sudo -n` refusing a proc-FD
query because a password was required. That earlier refusal is not assumed to
describe current sudo configuration. No password search, prompting, permission
change, daemon restart or alternative privilege bypass is proposed.

## Required safe outcome

Keep cleanup01's fail-closed behavior. Do not skip PID637/adbd, skip any
same-UID denial, infer absence from comm/status, or convert failed inspection
into success. Do not rerun cleanup01: its historical failure remains consumed.
Run02 upload remains blocked until a newly reviewed exact cleanup succeeds and
the unchanged uploader absence check passes.

If an already authorized noninteractive read-only observer can inspect every
required process, a new helper may retain all original deletion, identity,
content, directory, deadline and receipt guards and replace only the process
observer. A separate observer should:

1. Be fixed-source/hash-pinned and read-only: proc metadata/readlink only; no
   signal, process attach, service change, sysctl, credential/config mutation,
   scratch write, file deletion, open of an FD referent or device access.
2. Execute through the existing authorized noninteractive privilege mechanism
   with a bounded child deadline and bounded output. A denial, timeout,
   malformed result, unreadable surviving PID, bound excess, native process,
   UID/boot mismatch or scratch use fails the enclosing cleanup.
3. Check every readable native process name and every required same-UID cwd/FD
   under the same4096PID/4096FD bounds. Preserve exiting-PID verification;
   never treat missing metadata in a surviving PID as process disappearance.
4. Exclude only its own PID and the active cleanup caller whose open scratch
   directory descriptors are necessary for descriptor-bound deletion. Bind
   that caller to verified parent relationship and PID/start-time; never take
   an arbitrary exemption list or exempt the transport daemon. A PID reuse or
   parent mismatch is a failure. Document observations remain racy, not a lock.
5. Return complete current coverage and errors to the UID1000 cleaner. Verify
   observer source, current boot and identity on every call; invoke it again
   before every unlink, with the unchanged identity/inventory/directory checks
   following it. Keep all deletion operations unprivileged and unchanged.

If no authorized observer has sufficient access, do not generate or execute a
replacement that pretends to close the gap. Record the limitation and request
the narrowly necessary human/environment action through the repository's
existing workflow. No stop/restart of adbd, debugger or router is in this scope.

## Required independent controlled checks before adopting a helper

Freeze the new source and observer, contract and independently authored oracle;
retain original source/receipt hashes and every first failure. Controlled tests
must demonstrate at least: denied fd and denied cwd each prevent the first
unlink; surviving-PID missing metadata fails; a departed PID is accepted only
after recheck; direct/descendant/deleted target references reject; native names
reject; foreign names do not bypass same-UID inspection; bounds and identity
drift reject; observer privilege denial/timeout/nonzero/malformed/truncated
results reject; cleaner exemption requires exact parent and start-time; repeated
checks reject a change before each deletion; and all original file/content,
directory replacement, retained-original and partial-deletion guarantees hold.
Separate review must close material findings before any native use.

This proposal alone does not resolve the process visibility prerequisite,
authorize new privileges or establish a phase, physical, motor or MCU result.
