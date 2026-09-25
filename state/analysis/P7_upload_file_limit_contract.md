# Upload-specific file limit correction: host scope

D156 demonstrates that the1MiB capture-file limit cannot copy the pinned loader.
Four real Linux parent/descendant tests prove the minimum required ceiling is
2,303,728 bytes. Add a small explicit upload entry point; no new native run.

In upload_remote.py add `limit_upload_files()` setting RLIMIT_FSIZE soft and hard
to exactly2303728, plus `upload_loader(helper,support,*,fs_root=Path('/'),
executor=None,clock=None)`. It has the same bindings, report, claims, checks,
deadlines and failure semantics as existing upload(), except the default child
uses limit_upload_files rather than the frozen support.limit_child_output.
Use a per-instance callback and a small common runner, without global rebinding,
changing D153, duplicating the module or installing anything. No import-time I/O.

Keep legacy upload() behavior and all established tests unchanged. They remain
historical coverage of the original contract, whose1MiB policy is unsuitable for
the observed loader copy. The new API must be selected explicitly by a later
reviewed caller; D155's old source hash must reject the changed uploader. This
additive change does not revive D156 or permit reuse of consumed paths.

Diagnostic acceptance remains strictly below1048576 bytes for EACH stdout and
stderr stream. The new process file cap allows transient stream files as large
as2303728 bytes before failure; disclose this change. Do not claim the physical
1MiB write ceiling is retained. The cap remains finite and the smallest extent
shown sufficient for the three pinned copied inputs (loader2303728, sketch93096,
config680). No motor/firmware/pin/config/locked-test change.

Independent companion tests derive from this contract before seeing the new
implementation. Reuse the frozen fixture and assertions, replacing only the
fixture's dispatch choice and two preexec expectations for the NEW API. Keep
the old file byte-identical. Exercise every inherited case, new callback/limit
binding, both stream boundaries, frozen support's unchanged limit and source
pin sizes. The real OS copy proof remains separate from uploader validation.
Freeze before first execution; separate source/receipt review follows.

This explicitly permits an additive edit to the D154 uploader under a new
decision; original source81668c79 and all old oracles/receipts stay preserved in
Git. Every other D141-D155 source/binding remains unchanged. A future scope must
independently resolve fresh ownership and the known partial /tmp file before
any new upload. This contract grants no native action, cleanup or retry.
