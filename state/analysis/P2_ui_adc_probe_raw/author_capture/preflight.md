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

## Adopted final public preflight

The final proposal 7d18789b4a5210716d8ca84cab829efc53de9a27abf33ae419a62185a4879eb6
was adopted as P2_ui_adc_capture_contract.md SHA256
02b101fcd0246148c075a1594fcdee004295627d700fef83d82c15c9162c7ace.
The collector APIs, purpose labels, exact list/node offsets, pinned artifact input,
command limits, CLI output rules, and raw ET_REL st_value0 resolve the earlier
public gaps. No material decoder or collector result ambiguity remains. The
original preflight is preserved as preflight_initial.md.

The 21 pure decoder methods and literal fixtures froze before any implementation
execution; pure_freeze.json binds all bytes. Collector helper-fixture scope is
being confirmed independently before its executable freeze. No board action.
