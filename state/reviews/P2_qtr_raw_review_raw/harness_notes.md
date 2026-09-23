# D109 reviewer harness notes

The first private firmware run passed tools/test_host.sh and every C++ profile,
but its separately invoked inherited D106 registry fixture could not hash the
omitted P2_app_runtime_contract.md. The execution and nested traces remain in
firmware_1790195019448979762.json and its cases directory. The reviewer copied
that exact historical contract and reran only the registry method; no production
file, author oracle or registry assertion was edited. Passing C++ suites were
not repeated for this missing-fixture correction.

The initial exact registry-byte check also failed: besides the approved literal
entry, the immediately preceding `BEHAVIOR_EXTRA_DEFAULTS = {` terminator changed
from CRLF to LF. The corrected reviewer assertion permits only those two exact
changes and restores every other original byte; no assertion or executable test
token changed. This is an evidence-wording correction, not a test or product fix.
