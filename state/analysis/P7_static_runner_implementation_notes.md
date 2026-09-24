# D143 implementation clarifications before independent test freeze

These clarify the adopted interfaces; frozen contracts, production policy and
prior tests remain unchanged. Reviewed code and host tests are still required.

- `main` returns1 with concise stderr for a valid CLI invocation whose runtime,
  configuration or admission fails. `parse_request` retains argparse help0/error2;
  public `run_probe` propagates original command exceptions or admission ValueError.
- A process-record ENOENT is a normal race only when that PID directory is
  confirmed absent. A surviving PID with missing comm/cmdline/status is incomplete
  and fails PROCESS_INSPECTION. ESRCH indicates the departed process.
- Literal local code binding uses captured hash-verified source for direct module
  loads. The unchanged D141 nested common-policy loader must see no current-
  interpreter bytecode cache before/after import, with source/hash/ancestry
  rechecks. Invoke this scoped runner using python -B; no loader callback or
  frozen source is replaced. This detects ordinary drift, not an adversarial
  swap-and-restore entirely between observations.
- Malformed nonserializable callback output is represented explicitly as
  {encoding:python-type,type:<name>} in the receipt, never invented process text;
  the operation raises ValueError. Normal text/null and exception bytes keep
  their existing representations. A well-formed zero compile result establishes
  terminal state before receipt persistence, so a later receipt error still
  permits the five independent terminal postchecks and cannot claim success.

Reviewed first helper source fa209bee is preserved before the two inspection
repairs for surviving-PID ENOENT and partial-claim observations. No new helper or
runner has yet executed; independent tests will exercise both boundaries.

## First host results and bounded adjudication

First source006fdb70/helper521773e5 executes22 runner methods (21pass),23 bootstrap
methods (allpass),28 Linux helper methods (27pass). Original sources and freezes
remain in e64c61f9/047d6576, with complete first receipts. The two mismatches are
new-oracle assumptions, not evidence of accepting unsafe input.

The runner contract requires recording its own hash and does not close the whole
receipt directory. The independent author and separate reviewer confirm that
excluding compact inputs.json was an overconstraint. Its schema is exactly
{pins,stage,runner_sha256}: pins maps the17 reviewed relative input paths to their
SHA256s; stage is {source_files:103,stage_files:102,source_sha256:<fixed SOURCE>,
read_only_reuse:true}; runner_sha256 is SHA256 of the runner source bytes. Preserve
exact directory equality with this one addition and add exact metadata checks.
Only this unaccepted new draft assertion may be corrected and independently
refrozen; all existing command/result assertions and production tests stay intact.

The helper contract permits both FILE_READ and SOURCE_DRIFT without mapping all
source read races. The first run rejected inode replacement with exit2/FILE_READ.
Coordinator selects the reviewer's more precise SOURCE_DRIFT diagnostic for
positively detected source identity/content changes while opening/reading, keeping
FILE_READ for unreadability/bounds/special-file failures and PATH for ancestry.
An internal optional drift-code argument applies only to those two checks; source
reads select SOURCE_DRIFT. The original helper oracle remains unchanged. This is
diagnostic refinement, not a repaired admission or motor-safety failure.
