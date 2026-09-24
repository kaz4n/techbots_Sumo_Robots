# D151 exact native device-init range collection review

25 September 2026, Asia/Dubai. Separate same-model reviewer using prior P7
review context; not fresh-context, cross-model, human or runtime review. This
review owns only this new file; the separately assigned D150 receipt review is
recorded in P7_static_native_api_review.md. No collector main, board command,
GDB, build/upload/reset, deletion, implementation/test edit or commit was run.

**PASS for the fixed one-shot file-only composition. No open BLOCKER, MAJOR or
MINOR findings.** This is source/scope review before execution, not evidence of
the missing instructions or a native ABI/runtime pass.

| Input under state/analysis/ | SHA256 |
|---|---|
| P7_static_native_init_plan.md | fb7043e628a912e4c99d7fa00f55cc8df1c6bcf9900494adda6516fe7bff9e30 |
| P7_static_link_probe_raw/read_native_init.py | 4c39fafc2efe646f53020ff121cd4441956c71b95c9ae1cb245454f9209da415 |
| P7_static_link_probe_raw/native_init_preflight.json | bd701cb0ee2137dd4b701418496d9b776de14ce49264046d8ee7e1cb3f3955a9 |
| P2_adc_ownership_raw/installed_02.json | ed8b6c0fd2156483f1157fe3056ee5045ac7a38bb8c69117530e58dcc5b202f3 |
| P2_dump_raw/native/native_symbols.txt | 7ee12bec79896ea4aaddc1b9492d92d9d2f6a8e33af74bb03f7b7a8bb107a5b1 |
| P2_dump_raw/native/native_receipt.json | 9f92630b2bdc89840bc3fda4b9e583e4de65de486665ee0bdee8502e7128e444 |

The exact address provenance is supported. installed_02.json records[12]
preserves the earlier failed by-name query; records[13] disassembles the helper
at08019e2c but ends before the missing wrapper. native_symbols.txt:1712-1714
lists do_device_init08019e2c, z_impl_device_init08019e5c and next symbol
z_impl_device_is_ready08019e6e. The companion successful nm receipt identifies
loader39d4a4fd; the retained SHA256 index binds the symbol text and receipt.
The P0 PWM export independently gives Thumb pointer08019e5d. This supports
the requested half-open18-byte range, not its yet-unobserved control flow.

read_native_init.py:64 constructs13 fixed arguments: pinned GDB, -nx -nh
-batch, `-iex "set auto-load no"` before the pinned packaged ELF, one opening
marker, `disassemble /r 0x08019e5c,0x08019e6e`, and END. No symbol-name lookup,
inferior/target, evaluated function call, shell, script or remote mutation is
present. The preflight records335 UTF16 units, one query, four marker cases and
zero dispatches. The exclusive native_init output directory was absent during
review. Coordinator source capture/hash binding must precede the sole execution.

Compared the entire collector with frozen D15065cb7785: differences are the
new explicit command/range, output directory, marker/status/phase names and
description. Preparation still hash-loads runner983e86d7 and retains exact
D144 identity/Claim/eight FileRecords,17 local pins,103 source/102 stage files
and26 installed dependencies. No frozen runner/helper implementation changed.
The unchanged remote_postcheck()/installed_pins()/postchecks(local_only=True)
contracts remain the reviewed read-only APIs; no Probe.prepare(), staging,
compiler/property query or Claim creation path is called.

The five dispatches remain remote postcheck, installed hashes, one GDB query,
remote postcheck and installed hashes. GDB timeout60s, successful exit, empty
stderr, at most1MiB stdout, exact ordered unique markers and a nonempty block
are required. The block parser is a collection check; later review must confirm
the actual decoded instructions cover the intended range. Final remote,
installed and local checks run independently after capture failure. The first
failure and later postcheck errors are retained; final counts precede status
writing and a write error cannot replace the first failure.

Success is only NATIVE_INIT_QUERIES_COLLECTED. D150's failed collector, raw
negative evidence and partial observations remain unchanged. Any actual branch
to the retained helper must be established from the new receipt, not inferred
from the range or expected behavior. This scope cannot establish native startup,
full dependency coverage, live RAM/stack/heap, timing, physical acceptance,
production admission, motor-run authorization or a human phase gate.
