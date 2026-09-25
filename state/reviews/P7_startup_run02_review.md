# Explicit run02 ownership review

25 September 2026, Asia/Dubai. Separate same-model review reusing earlier
startup design/code context. Design review only; no native operation, cleanup,
implementation or test execution. Reviewer owns only this note.

Initial contract SHA256
`b86d179cd469d9863b4528841c44f529e3877dba46f75072938dd0e9f3b30515`
had one material API inconsistency: a no-global-mutation bootstrap required
explicit bindings, but legacy upload had no bindings parameter. Resolved by
allowing upload(..., bindings=None) while retaining fixed run01 and its old cap;
no run_id override is added to that legacy entry.

Amended reviewed contract SHA256
`0db1c1c534b181d6059ecd4edb2c21d7c703616f966a2125cb3b8182852678f0`.
**Design PASS for host preparation; no open material design finding.**

Closed run01/run02 selection plus per-instance copied bindings is sufficient;
no generic configuration framework or module-global rebinding is needed.
Default run01 retains old scope/output/dependency pins and must reject changed
helpers. Run02 alone selects current uploader/collector hashes, explicit loader
entry and distinct fixed owners; all other dependencies and D144 identity stay
fixed. Original scopes, source, oracles and failed run01 evidence remain intact.

The pure profile/projection helpers make selection independently testable.
Projection changes only run_id/output of checked original bindings; full remote
validation remains before claim. Expected identity must flow from the selected
instance through payload, report validators, intents and orchestration, rejecting
cross-run reports. The constructor rejects other selectors before filesystem
or process work. Bootstrap passes bindings explicitly without assigning globals.

Required tests cover both owners, interleaved isolation, consumed paths,
cross-run/invalid identities, old pins and unchanged legacy behavior. Command
size and actual composed source pins still require verification before future
use. Implementation and frozen receipts are pending, not inferred from design.

No native_run02_scope.json, residue disposition or execution permission is
provided here. The known /tmp/remoteocd entry remains a blocking admission fact;
host ownership preparation neither deletes it nor revives the consumed attempt.

Pre-freeze test-author clarifications reviewed, contract SHA256
`e53a3273d2309ebdedd0ccb1fbd52af7ba721ef3f4ea191640c6b779b8f9d45f`.
The payload keeps existing source/hash/bindings fields plus explicit run_id;
API dispatch remains closed and global-free. Historical dependency expectations
come from the preserved16-pin receipt minus its four named D144 receipt entries,
leaving the correct12-key dependency map. This resolves the baseline ambiguity
without changing behavior. **Design PASS applies to this clarified contract.**
Hold actual source/receipt disposition until the independent tests are complete
and frozen; no new execution or cleanup authority follows from this addendum.
