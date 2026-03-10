# run_phase2_v1.ps1 - Phase-II v1.0 Conclusive-First Protocol launcher
#
# Usage:
#   .\run_phase2_v1.ps1
#   .\run_phase2_v1.ps1 -PrimaryMatrixOnly
#   .\run_phase2_v1.ps1 -SeedOverride "141 142 143"

param(
    [string]$GrokkingRoot = "D:\FIT Lab\grokking",
    [string]$RunsRoot     = "D:\FIT Lab\grokking\runs_v0_6_structural_phase2",
    [string]$PythonExe    = "python",
    [switch]$PrimaryMatrixOnly,
    [string]$SeedOverride = ""
)

$ErrorActionPreference = "Stop"

$ScriptDir = $PSScriptRoot
$PhaseIIDir = Split-Path $ScriptDir -Parent
$PreregPath = Join-Path $PhaseIIDir "EST_PREREG.phase_ii.v1_0.yaml"
$OutDir     = Join-Path $PhaseIIDir "results\main_v1_0"
$LogFile    = Join-Path $PhaseIIDir "results\phase2_v1_0_run.log"

Write-Host "== Phase-II v1.0 Attractor Stability (Conclusive-First) =="
Write-Host "Prereg : $PreregPath"
Write-Host "Runs   : $RunsRoot"
Write-Host "Out    : $OutDir"
Write-Host ""

# GPU check
try { nvidia-smi | Out-Host } catch { Write-Warning "nvidia-smi unavailable." }

# Build argument list
$cmdArgs = @(
    "`"$ScriptDir\run_phase2_v1.py`"",
    "--prereg", "`"$PreregPath`"",
    "--grokking-root", "`"$GrokkingRoot`"",
    "--runs-root", "`"$RunsRoot`"",
    "--out-dir", "`"$OutDir`""
)

if ($PrimaryMatrixOnly) {
    $cmdArgs += "--primary-matrix-only"
}

if ($SeedOverride -ne "") {
    $seedList = $SeedOverride.Trim() -split '\s+'
    $cmdArgs += "--seed-override"
    $cmdArgs += $seedList
}

$cmdLine = "$PythonExe " + ($cmdArgs -join " ")
Write-Host "Running: $cmdLine"
Write-Host ""

New-Item -ItemType Directory -Path (Split-Path $LogFile -Parent) -Force | Out-Null

# Run and tee output to log
& $PythonExe @($cmdArgs | ForEach-Object { $_ -replace '^"|"$', '' }) 2>&1 |
    Tee-Object -FilePath $LogFile

Write-Host ""
Write-Host "== Done. Log: $LogFile =="
Write-Host "Check results at: $OutDir\summary.json"
