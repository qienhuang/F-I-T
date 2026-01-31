param(
  [string]$Ms = "97,127",
  [string]$Seeds = "42,123,456",
  [string]$Ratios = "0.34,0.36,0.38,0.40,0.42,0.44,0.46,0.48",
  [string]$OutputRoot = "results/beta_multiseed_v4",
  [double]$BetaMinProb = 1.0,
  [int]$BetaMinPoints = 3,
  [double]$SpeedMinProb = 1.0,
  [int]$SpeedMinPoints = 3,
  [double]$SpeedMaxDeltaR = 0.0,
  [int]$PhasePlots = 4
)

$ErrorActionPreference = 'Stop'

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here

New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$logPath = Join-Path $OutputRoot ("_cross_m_3090_" + $timestamp + ".log.txt")

function Log([string]$msg) {
  $msg | Out-File -FilePath $logPath -Append -Encoding utf8
  Write-Host $msg
}

Log "=== Li2 cross-M run (GPU recommended) ==="
Log ("cwd: " + (Get-Location))
Log ("Ms: " + $Ms)
Log ("Seeds: " + $Seeds)
Log ("Ratios: " + $Ratios)
Log ("OutputRoot: " + $OutputRoot)
Log ""

# Prefer a user-supplied Python, otherwise fall back to whatever is on PATH.
# Example:
#   $env:FIT_PYTHON_EXE = ".venv\\Scripts\\python.exe"
$PythonExe = $env:FIT_PYTHON_EXE
if (-not $PythonExe) {
  $PythonExe = "python"
}

Log "Preflight: torch.cuda availability"
try {
  $code = "import torch; print('cuda_available=', torch.cuda.is_available()); print('device=', (torch.cuda.get_device_name(0) if torch.cuda.is_available() else None))"
  & $PythonExe -c $code 2>&1 | Out-File -FilePath $logPath -Append -Encoding utf8
} catch {
  Log "WARN: could not run torch preflight (python/torch may be missing)"
}
Log ""

$mList = $Ms.Split(",") | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }
foreach ($m in $mList) {
  $outDir = Join-Path $OutputRoot ("M" + $m)
  New-Item -ItemType Directory -Force -Path $outDir | Out-Null

  $cmd = @(
    "& `"$PythonExe`" run_fit_validation.py",
    "--M", $m,
    "--ratios", "`"$Ratios`"",
    "--seeds", "`"$Seeds`"",
    "--output_dir", "`"$outDir`"",
    "--beta_min_prob", $BetaMinProb,
    "--beta_min_points", $BetaMinPoints,
    "--speed_min_prob", $SpeedMinProb,
    "--speed_min_points", $SpeedMinPoints,
    "--speed_max_delta_r", $SpeedMaxDeltaR,
    "--phase_plots", $PhasePlots
  ) -join " "

  Log ("> " + $cmd)
  & powershell -NoProfile -Command $cmd 2>&1 | Out-File -FilePath $logPath -Append -Encoding utf8
  Log ("exit_code=" + $LASTEXITCODE)
  Log ""

  if ($LASTEXITCODE -ne 0) {
    throw "Command failed for M=$m. See log: $logPath"
  }
}

Log "DONE"
Log ("Log: " + $logPath)
