# D200 exact upload scratch cleanup

26 September 2026. **Complete and independently reviewed PASS.** One authenticated
invocation removed exactly three stale D195 upload copies (2,399,768 bytes) and
their empty `/tmp/remoteocd` directory. Retained originals and staged source files
were independently reopened and verified unchanged. No firmware operation occurred.

The adopted contract6cb02590 binds recipe6afeea1b and wrapper13f33327 to the
observed directory device34/inode1172. Independent tests froze before implementation
inspection: all49 Linux methods passed; Windows passed12 and explicitly skipped37
Linux credential/process cases, all covered on Linux. All22 host input pins stayed
exact. Source/host review1ebd7342 confirms preserved content, process, descriptor,
credential, first-error and exact user-owned deletion guards.

Fresh absence83913618 preceded one staging operation5884a8d2. Three pinned sources
totaling50,664 bytes were staged in cleanup-app-settle-root04, device66341/inode272573.
First independent verifierf0ca0f68 failed because its staged-file observer used a
scratch-only pin table. The failed program and receipt remain preserved. Separately
authorized verification02 used the original explicit source read/hash/stamp loop;
receipt2c7a1ad2 and review7e0181e5 confirm complete source, scratch, original and
identity closure with result_root04.json absent. No source or cleanup guard changed.

The first local authentication launcher received EOF before any credential or
subprocess invocation. That failure is preserved separately. The successful
launcher used no-echo console input and passed authentication solely through native
stdin; no credential was saved in files or command arguments.

The single native invocation ran06:52:01.922913–06:52:02.850410UTC, exit0 with empty
stdout/stderr. Intent5f78e1dc fixes the exact root04 wrapper and exclusive result.
The original saved result is6,370 bytes, SHA256
`05507941ebbc8f9ba88c366dbf3c762e80042654a7c8de9166637ecc4e7c7ebd`.
Both the coordinator and independent reviewer checked the complete outer/nested
D200 schemas, equality with the raw nested JSON, exact removed names/stamps/hashes,
zero cleanup return code, no first errors and no privilege-drop errors.

Three protected scans each checked167 process names and3 same-user handle sets.
Each elevated only effective UID for read-only observation and restored effective
UID1000 before mutation. Initial UID/GID triples0 became permanently1000 on exit.
The inherited other-user-handle and concurrent-change limitations remain explicit.

Independent nonprivileged retrievalb7b776c9 preserves raw bytes and confirms six
remote closing checks plus local closure, exact retained-original/staged-source
full stamps and hashes, scratch absence twice, and unchanged board boot/identity.
Actual review5bc9d56d is PASS. Root04 and its result owner are consumed; no retry.
Sources, unique failures and compact receipts remain useful reproduction evidence.
Prior denied cleanup paths were not touched.

D195 remains the flashed image. Its SETTLE failure is unresolved; D198 compile and
D199 report ABI concern a later diagnostic image. This cleanup establishes no
runtime repair, physical acceptance, motor-run authorization or phase gate.
