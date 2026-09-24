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
