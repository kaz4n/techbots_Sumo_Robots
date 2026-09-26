# D230 scoped recorder failure software validation

Objective: prepare fresh file-only ABI observation and small passive failure
status snapshots of D228 recorder377911abefabd094. Implementation is additive:
tools/recorder_failure_abi.py, tools/recorder_failure_capture.py and
tests/test_recorder_failure.py. No firmware, config, locked test or main-worktree
file changed; no native/ADB command, upload, reset or UART operation occurred.

The ABI helper fixes435 offline GDB expressions,8 complete type layouts,
10 windows and56 decoded scalar fields. Runner and native_dump are checked
against the corresponding initialized RAM intervals. The capture takes two
small snapshots with full loader/sketch comparisons before and afterward;
all raw observations remain non-atomic with coherence UNPROVEN.

The existing D209 four descriptor bodies are byte-for-byte equal. Strict
result/marker/layout/number/symbol parsing is reused from that pinned module.
D188 execute/finally is inherited after changing only its scope label; the
new class overrides construction, local source admission and prepare. D173's
offline GDB builder and remote12-file/board closing lifecycle remain unchanged.
Pinned dependencies and exact compile records are in plan.json and source.

Serial host results:

- Initial15 focused methods passed in the console before integration fixtures.
- host_windows01 retained17 passes and one fixture error: a mocked prepare
  omitted bootstrap. Adding that fixture value preserved every assertion.
- host_windows02:18/18 PASS,1.681s; production composition yields four children,
  twelve remote file pins and7913 Windows UTF16 command units. The controlled
  fixture substitutes the live clean-HEAD/ADB gate and forbids transport calls;
  this is composition evidence only, not actual check-only/native admission.
- host_linux01:17/18 PASS, one unchanged strict descriptor refusal while
  reading a pinned dependency through DrvFS. Its original output is retained.
  The exact cause of changing filesystem metadata was not established.
- host_linux02:18/18 PASS,5.322s, exact-byte minimal /dev/shm fixture mirror,
  explicit Linux Git directory/worktree environment. No guard was relaxed.

integration_precheck01 also preserves an earlier preparation refusal caused
by core.autocrlf expanding two existing JSON files in the new worktree. They
were restored there to their exact historical Git bytes. The actual compiled
144 inputs/109 staged sources then passed historical admission. These two
original files are not part of the change or isolated commit.

host_closure.json binds final production, contract, plan, fixtures and all
retained test/error receipts. No C++ or target build was needed. Actual ABI
answers, passive MCU data and a cause for the zero-byte delivery remain absent.
Next action: independent review, root integration/exact reviewed collector
HEAD and one file-only check/execute. Later capture spec addresses derive only
from the accepted fresh ABI. The original failed receiver owner is never reused.

Storage: the worktree is sparse; only required dependencies and four compact
compile JSON records were copied for host composition. No full image/build
snapshot was made. Linux mirror and unittest temporary directories were
removed by their scoped TemporaryDirectory owners after completion. Python -B
prevented bytecode generation. Retained source, failures and compact receipts
are needed for review/reproduction; root can append this batch to STORAGE_LOG.

Root action sequence after independent acceptance:

1. Commit/integrate the reviewed additive files and all four original compile
   records already retained on main. Keep the144 historical source bytes fixed.
2. At the exact clean collector HEAD run
   `python -B tools/recorder_failure_abi.py --check-only --reviewed-head <HEAD>`,
   then exactly one same-HEAD `--execute` invocation. There is no retry. The
   consumed local output is state/analysis/P7_recorder_failure_raw/native_abi01.
3. Reconcile its four command results, twelve file checks, board identity,
   local closure and fresh ABI.json. Freeze the accepted ABI bytes/SHA256.
4. Mechanically call capture.build_spec(abi_raw, accepted_sha256, abi_module),
   save capture.canonical(spec) and freeze its SHA256. The four-hook remote
   adapter loads only the three dependencies listed in DEPENDENCIES and calls
   capture.collect(deps, spec=spec, spec_sha256=frozen_sha,
   input_bindings=capture.bindings()). This step supplies data, not new code.
5. Root stages/invokes/retrieves that exact adapter through the existing reviewed
   lifecycle. There is no added local native capture CLI in this change. Preserve
   its raw files and first/closing errors; reconcile both flash brackets and
   decoded snapshots before interpreting an observed failure status.
