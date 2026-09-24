# D139 unchanged default/M0 full-app qualification plan

2026-09-24. **PREPARED ONLY; NO COMPILATION AUTHORIZED OR RUN BY THIS TASK.**
D138 closed in `e16e6a57`; D139 is scoped in `b5b9a9b3`. The coordinator will
authorize one actual compilation only after independent stage-adapter probes
and separate review pass. This task has not executed the adapter, wrapper,
prepared analysis scripts, tests or board commands.

## Purpose and immutable baseline

Qualify the current unchanged full default/M0 app, including its default native
owners, with the existing checked compiler, exact target layouts and ordered
loader model. This is a new production baseline measurement, not a third memory
optimization candidate. The historical candidate1/candidate2 deficits24/32 bytes
remain preserved and neither candidate is adopted or used as a source input.
The stopped loop in `P5_default_fit_experiment.md` remains stopped.

Current source is the first D138 production implementation `d19f8964`, unchanged
through closure. The new compact manifest rehashes 103 source files against
the final687-input host freeze `P7_readiness_raw/freeze_final.json`, SHA256
`0fe188b7f8d6d179c85d7beff1a152245ab2455ba015baea9d2a4b82d38ce839`.
It does not mislabel the older683-input configured-test snapshot as current.
Five current native tool/policy assets retain the exact D138 checked hashes.
No source snapshot, firmware/configuration edit, capacity cut, flag optimization,
library/core change, grant change or oracle amendment belongs to this task.

## Exact read-only stage reuse, pending independent acceptance

The existing `build/stage/app` is the 102-file,753087-byte exact D138 source stage.
Its deletion was policy-denied; no deletion or restaging retry is permitted.
The narrow proposed adapter returns this existing directory only after all
checks pass, with no original `stage()` call and no fallback:

- Preserve current app-source existence, source ancestry/symlink/containment and
  sketch-local reserved-source checks.
- Require exactly the current103 source file names and hashes, exactly102 stage
  file names and hashes, and a matching source origin for every stage file.
- Require declared and recomputed stage digests to equal the public fixed
  `AUTHORIZED_SOURCE_SHA256` literal
  `fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2`.
- Run the current read-only push-through and mode-availability config validators.
- Pin both actual manifest file hashes in the wrapper before parsing them:
  source `c106c0fb8baaf0a6f2536558da0084bd7d236c4ee8e77a4110b60107ad073391`;
  stage `56ab12b990ebe664941677e29dfef783197bc98c3a9de1985b54d57bb30da56a`.

Public independent-probe interface and required failure cases are in
`P7_default_qualification_raw/adapter_contract.md`. Tests must reject absent,
extra, changed and coherently replaced source/stage/manifests, trap source/stage
writes or deletion, and prove original staging/transport/compiler paths are not
called. The real fixed source constant remains literal; synthetic test fixtures
may substitute only their own fixed authorized digest in RAM. Current board-tool
failure is ValueError; a distinct controlled ReuseRejected callback is allowed.

The reviewer identified the first draft's coherent-manifest replacement gap
before any execution. Original adapter, wrapper, public contract and syntax
receipt remain in `draft_01/`. The bounded correction adds the fixed source
identity and manifest-file pins; it does not alter production tooling.

The corrected helper SHA256 is
`78e173296c1d4366e4866b947b017814d69be2055c739cf1d96d0980eb40900e`;
the corrected wrapper SHA256 is
`e23c2e5a0b6901cacc14bd3095540963d5e52dc7c26a5d3717f465f9b109f59e`.

The stage is profile-independent: existing `stage('app')` accepts no MATCH or
startup parameter. Build flags and FQBN are selected later by unchanged
`flash_profile`, `build_startup`, `build_flags` and `compile_app`. Reusing exact
source bytes therefore does not reuse the MATCH binary or its settings.

## One checked compilation after an explicit go

Proposed command, not executed:

```text
python -B state/analysis/P7_default_qualification_raw/compile_target.py
```

It invokes the unchanged board-tool entry point with the narrow read-only stage
adapter and existing one-job command recorder:

```text
tools/board_tool.py flash app --compile-only --startup default
```

Exact native properties are:

```text
arduino-cli compile --jobs 1 --json
--fqbn arduino:zephyr:unoq
--build-property compiler.cpp.extra_flags=-DMATCH=0 -DMOTORS_ALLOWED=0
--build-property compiler.c.extra_flags=-DMATCH=0 -DMOTORS_ALLOWED=0
--build-property build.library_discovery_phase_flag=-DARDUINO_LIBRARY_DISCOVERY_PHASE=0
```

Use verified ADB serial2629958581, existing ADB32.0.0 executable and dedicated
remote root `/home/arduino/sumox26_codex_build`. Do not use passwords. Current
compile policy must still verify CLI/core, installed hashes, overrides, expanded
properties, libraries, selected profile and generated artifacts. The source path
remains content-addressed; build/output/receipt paths get a new unique UUID under
`bench-default`. Existing MATCH and historical receipts are never overwritten.

Check current connectivity, resources and absence of another compiler before
starting. Run one native compiler and notify the coordinator when it ends, before
analysis continues. Keep the original first-failure output and actual exit codes.
No second compilation follows a build or fit failure automatically. A timeout
does not establish that a remote compiler ended; report its state without
starting another. No upload, reset, MCU/native I/O, matrix, Bridge/log dump or run.

## Required artifact accounting, including a negative result

After compiler/policy success, retain one exact final ELF locally plus compact
receipts and hashes of the checked debug/temp ELF and ZSK. Prove 103 current
source hashes,102 staged hashes/digest,102 remote staged hashes and the five
native tooling dependencies still match their bound identities.

Prepared analysis scripts, each to run with captured argv, source hash, output
and real exit code, are:

1. `account_target.py`: unchanged retained `elf_review.py` model; compare current
   payload, regions, global symbol count and modeled peak against historical
   D134 default and current D138 MATCH, never either optimization candidate.
2. `collect_source_binding.py`: recheck frozen/current/staged/remote bytes.
3. `collect_imports.py`: compare current relocation-used imports with freshly
   hashed packaged-loader exports through file-only GDB; no target/inferior.
4. `collect_abi.py`: hash and query current default, historical D134 default and
   current D138 MATCH debug ELFs. Capture16 sizeof/alignof pairs,72 common member
   offsets, the three current metadata fields and seven default-only Runtime
   fields where present. Report actual differences rather than asserting M0 and
   MATCH layouts must be identical.
5. `validate_account.py`: verify exact settings/source/import evidence and all
   allocations in loader order, aligned persistent peeks and the first failing
   allocation if any. Save the full ordered account before returning nonzero for
   failed conditional fit; report largest possible payload only when it fits.

| Comparison baseline | Compiler payload | Conditional peak / remaining span |
|---|---:|---:|
| Historical D134 default, unchanged production | 257320 B | 262176 B / deficit32 B |
| Current D138 MATCH/Immediate | 256440 B | 261280 B / 864 B |
| Current default/M0 | **Unmeasured** | **Unmeasured** |

Model pool is262144 bytes. Preserve the distinction between compiler nominal
remainder, hypothetical ordered peak/deficit, first failing allocation, and
actual runtime memory. If fit fails, still archive source/import/layout results
and a final negative report, then stop for review. Do not repair source or rerun
the compiler as part of this baseline qualification.

## Storage and present readiness

Use only these new raw files and the planned default qualification report.
C: had692170752 bytes free at preparation; recheck before artifacts. The plan
adds small scripts/manifests, not a duplicate checkout. Keep one final ELF and
required receipts; preserve checked remote artifacts and unique failures. Any
later disposable-object cleanup must concern only the new unique run and retain
a receipt. Do not retry local stage deletion or either older denied cleanup.
The coordinator owns ledgers, acceptance and commits.

Preparation performed local source/hash reads and AST syntax inspection only.
Independent controlled probes and scoped adapter review are pending; no native
fit, actual loading, live RAM/stack/WCET, physical acceptance or phase gate is
claimed. Wait for their results and the coordinator's explicit compile go.
