# D113 executable author freeze

The new `test_dump_connection.py` was authored from adopted contract e4854815
and public D090 API/test fixtures, without production-body reads or implementation
execution. This reused author context is separate from the implementer but not
fresh to the repository or another model. No old assertion or test was edited.
The only fixture imported from D090 is its independent literal `wire()` generator.

The frozen cases exercise strict host schema and record keys, malformed JSON,
types, bounds, request/record identity, source chronology, exact public outcomes,
passive construction, invalid CLI/API combinations, all observation states,
transport/metadata/Parser precedence, final retrieval before first yielded byte,
partial wire preservation, and final success requiring three terminal records.

Actual generated remote Python bodies are obtained only through captured public
board.remote calls and executed under a confined Linux fixture. Socket operations
are counted and cannot send; /tmp and /proc resolve to unique test-owned paths;
real directory/file descriptors and the platform's no-replace rename still operate
on those temporary files. A synthetic root-owned sticky /tmp stat is needed because
the isolated WSL test user is uid1000. All actual capture files belong to that user.
No board, network connection, child remote process, signal, or service is used.

Remote cases cover claim/connect/connected/recv/close order and actual immutable
records; collisions, failed connect, close/publication failures; exact original
chunks; late END/deadline equality; literal raw END versus Parser validity; EOF,
socket timeout, exact line bound, line failure, and MAX_BYTES+1 observation; missing
claim and ignored publication temporaries; terminal/expiry priority over dead PID;
PID/fd reuse, zombie/TCP state, absent/malformed/oversized process evidence; unsafe
file mode/link/symlink and malformed identity; mutation during file read; process,
fd and directory replacement during observation; future event versus live deadline.

Linux execution is required for the complete remote-body class. No private
production state is seeded. Functions/scripts are invoked through public APIs;
fixtures mutate only their own synthetic Linux state. Tests do not prove continuous
atomic connection, router client registration, UART framing or exclusivity, board
transport behavior, remote-process termination, OS WCET, hardware readiness, or
motor authority. Schema/receipt success cannot manufacture those facts.

The untouched D090 suite will run alongside the new suite. Its additive registry
case may require the already approved current registry invocation wrapper; any
stale-context result must be retained rather than assertions changed. Initial
execution failures are preserved, and any fixture/oracle amendment requires a
recorded independent review before rerun. The task permits at most two repair
attempts before escalation to the coordinator.
