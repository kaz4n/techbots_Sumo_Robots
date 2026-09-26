# D240 source and focused host validation

2026-09-27 Dubai. Implemented the additive paired application delivery caller
and private D227 opt-in. No firmware/config/locked-test change or native action.
The ordinary D227 CLI still refuses identified settings; existing M0 grant
refusal and all M1 source/artifact/physical/specific authorization checks remain.

Windows command: `python -I -B tests/test_app_identified_delivery.py -v`.
Final host02: nine methods PASS, zero failures/errors/skips, 28.172 seconds
unittest time and 28.410 seconds process time. All four recorded source/contract
input hashes remained unchanged. Raw stdout/stderr, command/closure receipt and
input pins are retained in P7_app_identified_delivery_raw/host02.*.

Five cases use the existing D227 fixture with actual temporary Git objects,
complete synthetic compiler/artifact validators and synthetic qualification
records. The default disabled baseline is admitted before every mutation.
Coverage includes qualified paired admission, unchanged standalone refusal,
exact receiver two-command composition, decoded real upload payload bindings,
missing specific permission/UART qualification, M0 refusal, one-use session
prefix collision, changed claim refusal, and actual D227 five-operation upload
closure under the new nested owner without retry. No fixture grants are facts.

Real receiver/CSV fixtures use a two-frame/one-event wire, including an
interrupted recording; no recorder-specific 5001/8 oracle is imposed. The actual
inherited close_receiver invokes the new application validator and preserves
an original receiver error when closing also fails. Wrong-session, missing-BEGIN
and changed-CSV inputs remain rejected. Controlled full caller sequencing covers
success, failed upload, failed connection, post-connection claim revalidation
failure before upload, and original upload failure followed by failed final
journal write. Every attempted upload is single; available receiver/secondary
errors and the original primary remain in the returned exception outcome.

Initial host01 is preserved: six methods passed, one fixture asserted an owner
string against compressed data instead of its decoded payload, and one fresh
fixture hit the unchanged descriptor metadata-stability guard before its M0
case. The assertion now checks the decoded actual selection/bindings. No metadata
guard was relaxed; a fresh final fixture passed. Exact initial caller/test source
bytes are retained and reconcile to host01 input hashes.

Source review also identified the final-journal failure seam, independently
noticed during implementation. The fix retains the original first error,
records result_write as secondary, attaches the in-memory outcome, and treats
missing capture/closing evidence as FAILED. The final focused tests include
that failure combination. No broad inherited-suite rerun was performed.

Temporary host Git fixtures were removed by their existing harness after test
closure. No compiler products, large snapshots, credentials or board artifacts
were created. Native deployment remains separately qualified and authorized;
this preparation neither enables a bare-board operational app dump nor makes
a fixed session fresh after reset.

Final convention-only adjustment joins two continuation lines in run(), bringing
its span to 59 lines. ASTs without source locations are exactly equal. The
tested host02 caller and original review are retained; line_wrap01.json records
the old/new hashes. No semantic change or redundant test rerun.
