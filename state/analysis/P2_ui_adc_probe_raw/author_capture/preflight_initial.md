# D114 readout independent public preflight

The author read the worker's initial readout proposal and only the `abi` portion
of the enabled `target_396bcc45_bench-default_checked/audit.json`, together with
public UI/power/core declarations. No future capture implementation body was read.

Enabled GDB evidence confirms Runner9892, Report132 at16, Capture76 at148 with128
elements, and every proposed nested public field offset. This includes explicit
Capture member offsets, rather than relying on its earlier derived candidate.
The pure `decode_runner_pair(bytes, bytes)` interface supports independent literal
fixtures without importing implementation offsets, constants or a private state.

The coordinator resolved diagnostic determinism: errors are ordered but
non-exhaustive; identical(code,path) pairs are deduplicated. Tests must not assert
incidental exact error counts. Capture wrapper chronology is TIMING at
`captures[i]`; incorrect source_us is SOURCE at `captures[i].source_us`.
Unknown raw values remain visible. Full Runner-byte equality is required for a
frozen terminal label, including padding/private/unused bytes; typed interpretation
still ignores those bytes. Equal nonzero padding is therefore allowed, while a
changed padding byte means instability rather than malformed typed data.

Before collector executable expectations freeze, the proposal still needs its
final enabled artifact/section-relative symbol binding, public collector API and
CLI, exact node/list field offsets and pinned command/identity seams. The worker
is preparing these at the coordinator's request. An apparent nm/VMA address must
not become a guessed relocated Runner offset; use the final literal readelf and
section normalization specified in the adopted readout contract.

Pure fixtures should include full128 acquisition, truthful zero/partial FAULT,
historical decoder after rejected A, historical accepted flags after rejected S,
all nonterminal phases, raw endpoints/repeats and natural wrap, source/cadence/
timing boundaries, saturated counters, invalid enums/bool bytes/count, and byte
changes in both interpreted and ignored regions. Collector tests remain separate
from semantic decoding and must never promote failed collection identity into a
frozen result. This preflight authorizes no board operation or hardware claim.
