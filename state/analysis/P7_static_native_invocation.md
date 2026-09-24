# D143 future native invocation

Preparation only, 25 September 2026. **No native GO has been issued.** All80 host
methods pass (runner22+2, helper28+5, bootstrap23); separate scoped source/receipt
reviews close all findings. Follow the frozen
[runner contract](P7_static_runner_contract.md),
[remote contract](P7_static_remote_contract_draft.md),
[implementation notes](P7_static_runner_implementation_notes.md) and separate
[runner](../reviews/P7_static_runner_code_review.md)/
[helper](../reviews/P7_static_remote_code_review.md) reviews. This plan adds no
runner/helper code and changes no admission rule.

## Exact inputs and local prerequisites

| Input | SHA256 |
|---|---|
| `P7_static_link_probe_raw/run_static_probe.py` | `983e86d7eb68f437c50b4b790e96ca4520e092abe53e4d29e8ffe1a97502b208` |
| `P7_static_link_probe_raw/static_remote.py` | `8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8` |
| `P7_static_runner_contract.md` | `35473ed0eb59b9d7fd097cb25554b591ec6bd470703504e1a525219b2fdba7e7` |
| `P7_static_remote_contract_draft.md` | `a4be3733d40632b4ae79e3bbbab3300f720b8f7f13f3337d35d96dfc90373b39` |

Paths in the table start at `state/analysis/`. The runner retains its own complete
17-input pin map, source digest
`fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2`,
D139 read-only103/102 source/stage verification, all26 installed dependency pins,
CLI/core/override checks, exact D141 properties, D142 validation, fresh-directory
claims, command-size limits, and the complete failure/postcheck rules.

Read-only local observations at approximately01:24 Dubai:

- PowerShell7.6.6; Python executable is
  `C:/Users/narut/AppData/Local/Programs/Python/Python313/python.exe`.
- The configured ADB executable exists as a regular, non-reparse file; its hash
  is `e79dc8fc3c6385192bdccd7ff7eabe3d5c1ec292475a06b04d82759f07655982`.
- `P7_static_link_probe_raw/runs/` **does not exist**. The coordinator must create
  this exact nonsymlink parent before the authorized invocation; do not precreate
  `runs/<run_id>`, which the runner exclusively claims itself.
- The three SUMO variables are unset. The command below supplies only those three
  transient process values and restores their previous values, including absence.
- Current-interpreter `tools/__pycache__/app_build_policy.cpython-313.pyc` is absent.
  The runner rechecks its actual interpreter cache path; do not disable that guard.
- C: had747,077,632 free bytes. Recheck space and coordinator compiler exclusivity
  just before GO; this historical observation is not a reservation.

No ADB/device query, remote helper, compiler or test was executed for this plan.
Actual Linux identity/resources/process/source checks remain the runner's first
authorized observations. A failed prerequisite is a retained negative outcome.

## Literal Windows command, only after source-bound GO

Run in PowerShell7 from the repository. The source hashes below must still match
the reviewed release of this plan. Do not substitute a newly changed runner or
helper without review. This uses the unchanged script `main()` and consequently
the unchanged `board_tool.remote`; no callback or validator is replaced.

```powershell
$ErrorActionPreference = 'Stop'
$repo = 'C:\Users\narut\OneDrive\Desktop\Project\techbots_Sumo_Robots'
$python = 'C:\Users\narut\AppData\Local\Programs\Python\Python313\python.exe'
$raw = Join-Path $repo 'state\analysis\P7_static_link_probe_raw'
$runner = Join-Path $raw 'run_static_probe.py'
$helper = Join-Path $raw 'static_remote.py'
$runnerHash = '983e86d7eb68f437c50b4b790e96ca4520e092abe53e4d29e8ffe1a97502b208'
$helperHash = '8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8'
if ((Get-FileHash -LiteralPath $runner).Hash -ine $runnerHash) { throw 'Runner drift' }
if ((Get-FileHash -LiteralPath $helper).Hash -ine $helperHash) { throw 'Helper drift' }
$runs = Join-Path $raw 'runs'
if (-not (Test-Path -LiteralPath $runs -PathType Container)) { throw 'Missing coordinator-created runs parent' }
$runId = [Guid]::NewGuid().ToString('N')
if (Test-Path -LiteralPath (Join-Path $runs $runId)) { throw 'Run ID already exists' }
$capture = Join-Path $runs ($runId + '.launcher')
$null = New-Item -ItemType Directory -Path $capture -ErrorAction Stop
$values = @{
    SUMO_TRANSPORT = 'adb'
    SUMO_ADB_SERIAL = '2629958581'
    SUMO_ADB_EXECUTABLE = 'C:/Users/narut/AppData/Local/Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe'
}
$previous = @{}
foreach ($name in $values.Keys) { $previous[$name] = [Environment]::GetEnvironmentVariable($name, 'Process') }
$nativeErrorPreference = $PSNativeCommandUseErrorActionPreference
$exitCode = $null
$launchError = $null
$start = [DateTime]::UtcNow.ToString('o')
@{run_id=$runId; runner_sha256=$runnerHash; helper_sha256=$helperHash;
  executable=$python; argv=@('-B',$runner,'--compile-only','--run-id',$runId);
  start_utc=$start} | ConvertTo-Json -Depth 4 |
    Set-Content -LiteralPath (Join-Path $capture 'planned.json') -Encoding utf8NoBOM
try {
    foreach ($name in $values.Keys) { [Environment]::SetEnvironmentVariable($name, $values[$name], 'Process') }
    $PSNativeCommandUseErrorActionPreference = $false
    & $python -B $runner --compile-only --run-id $runId 1> (Join-Path $capture 'stdout.txt') 2> (Join-Path $capture 'stderr.txt')
    $exitCode = $LASTEXITCODE
} catch {
    $launchError = $_.Exception.ToString()
} finally {
    foreach ($name in $previous.Keys) { [Environment]::SetEnvironmentVariable($name, $previous[$name], 'Process') }
    $PSNativeCommandUseErrorActionPreference = $nativeErrorPreference
    $afterHashes = @{}
    $afterHashErrors = @{}
    foreach ($item in @(@{name='runner';path=$runner}, @{name='helper';path=$helper})) {
        try { $afterHashes[$item.name] = (Get-FileHash -LiteralPath $item.path).Hash.ToLowerInvariant() }
        catch {
            $afterHashes[$item.name] = $null
            $afterHashErrors[$item.name] = $_.Exception.ToString()
        }
    }
    @{run_id=$runId; returncode=$exitCode; error=$launchError; start_utc=$start;
      end_utc=[DateTime]::UtcNow.ToString('o');
      runner_sha256_after=$afterHashes.runner; helper_sha256_after=$afterHashes.helper;
      post_hash_errors=$afterHashErrors} |
        ConvertTo-Json -Depth 4 |
        Set-Content -LiteralPath (Join-Path $capture 'completed.json') -Encoding utf8NoBOM
}
if ($null -ne $launchError -or $exitCode -ne 0 -or $afterHashErrors.Count -ne 0 -or
    $afterHashes.runner -ne $runnerHash -or $afterHashes.helper -ne $helperHash) {
    throw "Static probe launcher failed or source drifted; retain $capture"
}
```

The fresh `<run_id>.launcher` sibling retains launcher stdout/stderr as captured
by PowerShell, exact planned argv, actual launcher exit code (null if unavailable)
and exception text. It never preclaims the runner's `<run_id>` directory. No old
receipt or output is overwritten; stop if either destination exists. Coordinator
checks the parent ancestry before creating the launcher sibling; runner checks
its full ancestry again before any transport. Source hashes are ordinary
before/after drift checks, not adversarial swap-and-restore attestation.

The tool session may yield while this one process runs. Observe its existing
session and newly written numbered command receipts; do not launch a second
process, insert another board inventory, sleep/retry loop or impose an outer
timeout that kills the launcher. The runner already has explicit command timeouts.
Retain launcher interruption as unknown and stop for coordinator review.

## Result and stop boundary

Inspect `<run_id>/result.json` and original numbered receipts even when the launcher
returns nonzero. No query or compile follows a failed check automatically; maximum
one expanded-properties query and one actual `--jobs 1` compile. Nonzero/malformed
compile transport or timeout means `COMPILE_OUTCOME_UNKNOWN`, with local checks
only. A known terminal compiler/policy/artifact failure remains `FAILED`; its
required independent postchecks preserve evidence and do not authorize repair.
No retry, cleanup, upload/reset or source/config change follows either outcome.

Even exit0 is accepted only when source hashes remain exact, result status is
`STATIC_COMPILE_COLLECTED`, the single-attempt counts and captured identities
agree, and retained artifacts pass separate review. This includes the complete
`STATIC_LAYOUT_PACKAGE_PASS` structural report and one checked local final ELF;
all seven complete artifacts and selected exported copy remain at the claimed
remote paths. Do not transfer additional multi-MiB artifacts by default.

Full native entry/instruction and copy/zero/constructor order, strong app main,
used external/wrapper/heap/native-HAL bindings, weak-reference classification and
D139 ABI size/offset comparison are subsequent read-only artifact audits under
the parent contract. Compilation/collection is not full-probe acceptance, an
upload/run authorization, live-memory/WCET evidence, release adoption or a phase
gate. D139's dynamic592-byte deficit remains unchanged.
