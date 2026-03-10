param(
    [string]$GrokkingRoot = "D:\FIT Lab\grokking",
    [string]$PythonExe = "python",
    [int]$WaitForPid = 24612
)

$ErrorActionPreference = "Continue"

$ScriptDir = $PSScriptRoot
$PhaseIIDir = Split-Path $ScriptDir -Parent
$SpecPath = Join-Path $PhaseIIDir "results\specs\estimator_spec.phase2_v1_0_40_checkpoints.yaml"
$PreregPath = Join-Path $PhaseIIDir "EST_PREREG.phase_ii.v1_0.yaml"
$RunsRoot = "D:\FIT Lab\grokking\runs_v0_6_structural_phase2"
$OutDir = Join-Path $PhaseIIDir "results\final_v1_0_40"
$SweepLog = Join-Path $PhaseIIDir "results\phase2_v1_0_40_checkpoint_sweep.log"
$EvalLog = Join-Path $PhaseIIDir "results\phase2_v1_0_40_eval.log"

if (-not (Test-Path $SpecPath)) {
    throw "Missing spec: $SpecPath"
}

New-Item -ItemType Directory -Path (Split-Path $SweepLog -Parent) -Force | Out-Null
New-Item -ItemType Directory -Path $OutDir -Force | Out-Null

if ($WaitForPid -gt 0) {
    try {
        $p = Get-Process -Id $WaitForPid -ErrorAction Stop
        Write-Host "Waiting for PID $WaitForPid ($($p.ProcessName)) to finish before starting Phase-II final..."
        while ($true) {
            Start-Sleep -Seconds 60
            $alive = Get-Process -Id $WaitForPid -ErrorAction SilentlyContinue
            if (-not $alive) { break }
        }
        Write-Host "PID $WaitForPid finished. Continuing."
    } catch {
        Write-Host "PID $WaitForPid not running. Starting immediately."
    }
}

Write-Host "== Phase-II v1.0 final 40-seed: checkpoint sweep =="
Write-Host "Spec: $SpecPath"
Write-Host "Out : $RunsRoot"

Set-Location $GrokkingRoot
$env:PYTHONUTF8 = "1"
& $PythonExe -m grokking.runner.sweep `
    --spec $SpecPath `
    --out $RunsRoot `
    --phase eval 2>&1 | Tee-Object -FilePath $SweepLog
if ($LASTEXITCODE -ne 0) { throw "Checkpoint sweep failed with exit code $LASTEXITCODE" }

$seedList = @()
for ($s = 140; $s -le 179; $s++) {
    $seedList += "$s"
}

Write-Host "== Phase-II v1.0 final 40-seed: recovery eval =="
Write-Host "Prereg: $PreregPath"
Write-Host "Runs  : $RunsRoot"
Write-Host "Out   : $OutDir"

& $PythonExe (Join-Path $ScriptDir "run_phase2_v1.py") `
    --prereg $PreregPath `
    --grokking-root $GrokkingRoot `
    --runs-root $RunsRoot `
    --out-dir $OutDir `
    --primary-matrix-only `
    --seed-override $seedList 2>&1 | Tee-Object -FilePath $EvalLog
if ($LASTEXITCODE -ne 0) { throw "Phase-II eval failed with exit code $LASTEXITCODE" }

Write-Host ""
Write-Host "== Phase-II final run complete =="
Write-Host "Checkpoint sweep log: $SweepLog"
Write-Host "Evaluation log      : $EvalLog"
Write-Host "Summary             : $OutDir\summary.json"
