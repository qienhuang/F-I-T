param(
  [string]$Model = "qwen3:4b",
  [string]$Models = "",
  [int]$Samples = 50,
  [double]$Temperature = 0.9,
  [string]$Temperatures = "",
  [string]$Fprs = "0.05,0.10,0.20",
  [string]$Seeds = "1337,2337",
  [string]$Prompts = "data\\policy_prompts_readwrite_v1.jsonl",
  [string]$ActionIds = "REFUSE,ANSWER,TOOL:read_file,TOOL:write_file",
  [string]$UnsafeActionIds = "TOOL:write_file",
  [string]$OutRoot = "out",
  [switch]$CleanOutRoot,
  [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"

$base = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $base

$fprList = $Fprs.Split(",") | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }
$seedList = $Seeds.Split(",") | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" } | ForEach-Object { [int]$_ }
$modelList = @()
if ($Models.Trim() -ne "") {
  $modelList = $Models.Split(",") | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }
} else {
  $modelList = @($Model)
}

$tempList = @()
if ($Temperatures.Trim() -ne "") {
  $tempList = $Temperatures.Split(",") | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" } | ForEach-Object { [double]$_ }
} else {
  $tempList = @([double]$Temperature)
}

$outRootPath = $OutRoot.Trim()
if ($outRootPath -eq "") { $outRootPath = "out" }

if ($CleanOutRoot -and (Test-Path $outRootPath)) {
  Remove-Item -Recurse -Force $outRootPath
}

New-Item -ItemType Directory -Force -Path $outRootPath | Out-Null

function Sanitize([string]$s) {
  return ($s -replace "[:/\\\\]", "_")
}

$promptTag = Sanitize ([System.IO.Path]::GetFileNameWithoutExtension($Prompts))

foreach ($m in $modelList) {
  foreach ($t in $tempList) {
    foreach ($fpr in $fprList) {
      foreach ($seed in $seedList) {
        $safeModel = Sanitize $m
        $tag = "{0}_{1}_fpr{2}_seed{3}_s{4}_t{5}" -f $safeModel, $promptTag, ($fpr -replace "\\.",""), $seed, $Samples, ($t.ToString().Replace(".","p"))
        $outDir = Join-Path $outRootPath $tag
        # Skip if summary already exists (resume support)
        $summaryPath = Join-Path $outDir "policy_eval_summary.json"
        if (Test-Path $summaryPath) {
          Write-Host "== SKIP (already done) model=$m fpr=$fpr seed=$seed"
          continue
        }
        Write-Host "== policy-eval model=$m prompts=$Prompts fpr=$fpr seed_base=$seed samples=$Samples temp=$t"
        & $PythonExe dr_one_demo.py policy-eval `
          --backend ollama `
          --ollama_model $m `
          --samples $Samples `
          --temperature $t `
          --target_fpr $fpr `
          --seed_base $seed `
          --action_ids $ActionIds `
          --unsafe_action_ids $UnsafeActionIds `
          --prompts $Prompts `
          --out_dir $outDir
      }
    }
  }
}

Write-Host "Done. Summaries are under $outRootPath\\*\\policy_eval_summary.json"
