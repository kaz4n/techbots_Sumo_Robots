# D153 independent collector test freeze

Prepared 2026-09-25T03:23:13+04:00 by the separate spec-only test author.

`test_capture_remote.py` contains 46 unittest methods with additional parameter
matrices. It has **not been executed**, including no syntax/import smoke run.
The new `capture_remote.py` implementation was neither opened nor inspected.
The coordinator owns the first execution and its immutable result receipt.

Frozen inputs:

| Input | SHA256 |
|---|---|
| `test_capture_remote.py` | `2d9fe1697ebd0603508b1a36a08132ed3e000d3770e34e16df7e4854aff277dd` |
| `../P7_static_capture_remote_contract.md` | `0371739e93920fa24a18ed95eeb8eb6b117e4cf4e3f3b87f04ed38bc16ba227e` |
| `capture_bindings.json` | `c2c87df6165556602a5a79472caedf0755c070b2e2f3e0b834f17ab0de5c0d32` |
| `../P7_static_link_probe_raw/static_remote.py` | `8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8` |

Expectations come from D153's public contract, fixed bindings, the D152 public
18-read plan/result schema, and frozen helper interfaces. The p0 loader callback's
public raw-ELF-bytes to bytes interface was also inspected; no firmware `.cpp`
was read. The pre-freeze clarifications explicitly permit synthetic loader hashes,
specify shallow decoder admission, original-descriptor finalization after path
drift, literal Tcl path braces/eight lowercase hexadecimal digits, immediate
pre-Popen deadline checks, and clock-error evidence retention. The suite encodes
those clarified requirements rather than an implementation-specific fallback.

Coverage includes exact 18-command order/713656-byte extent/argv, durable receipts,
fixed environment/cwd/session/stdin/RLIMIT, admission and pin/identity failures,
existing output and no second attempt, subprocess exceptions/nonzero/timeout/
unreaped/malformed results, missing/short/oversized/symlink raw bytes, first-flash
mismatch suppressing RAM, two-second wait placement/failure and deadline bounds,
malformed decoder responses, honest fault/no-progress/late-flash observations,
independent postchecks, parent/output replacement, fsync failures, result collision,
stdout/stderr limits, timeout owned-group SIGKILL plus bounded reap, kill/spawn/reap
errors, and clock failure without replacing the primary error.

The suite uses real frozen descriptor traversal/read operations in small Linux
temporary trees, with synthetic identity/directory-owner results. References stay
at the exact 263680/93096-byte extents; tool/ELF files are tiny synthetic content.
An independent decoder substitute asserts exact triples and references. Popen and
killpg are guarded unless replaced by controlled test doubles. No tool binary,
compiler, board, upload, reset, MCU read, socket or real child process is requested.
TemporaryDirectory cleanups release each owned fixture after a method/matrix case.

Limitations: these controlled substitutes do not establish native process behavior,
kernel-wide process/filesystem exclusivity, real board ownership, actual RLIMIT
enforcement, MCU quiescence, runtime progress or physical qualification. The
4096-entry process-scan ceiling is not independently stress-tested here; exact
conflicts, similar names and disappearance/error distinctions are covered. Existing
helper correctness remains inherited from its prior frozen tests. This preparation
does not pass a hardware/phase gate or authorize a native capture.

Coordinator command after recording implementation/test freeze:

```sh
python3 -B -m unittest discover -s state/analysis/P7_static_startup_raw -p test_capture_remote.py -v
```

Run once under Linux/WSL with bytecode disabled, retain the complete first result,
and preserve these frozen bytes when investigating failures.
