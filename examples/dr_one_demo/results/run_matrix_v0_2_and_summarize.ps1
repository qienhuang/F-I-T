param(
  [string]$PythonExe = "python",
  [switch]$Clean
)

$ErrorActionPreference = "Stop"

$base = Split-Path -Parent $MyInvocation.MyCommand.Path
$demo = Split-Path -Parent $base
Set-Location $demo

if ($Clean) {
  if (Test-Path "out_matrix_v0_2") { Remove-Item -Recurse -Force "out_matrix_v0_2" }
}

.\run_policy_eval_matrix.ps1 -PaperMatrix -PythonExe $PythonExe

& $PythonExe summarize_out.py --out_root out_matrix_v0_2 --write_md results/policy_eval_runs_matrix.md
& $PythonExe summarize_out.py --out_root out_matrix_v0_2 --aggregate --write_agg_md results/policy_eval_agg_matrix.md

Write-Host "Done. Paper-ready tables:"
Write-Host "  results\\policy_eval_runs_matrix.md"
Write-Host "  results\\policy_eval_agg_matrix.md"

