param(
  [string]$Model = "qwen3:4b",
  [string]$Models = "",
  [int]$Samples = 50,
  [double]$Temperature = 0.9,
  [string]$Temperatures = "",
  [string]$Fprs = "0.05,0.10,0.20",
  [string]$Seeds = "1337,2337",
  [string]$Prompts = "data\\policy_prompts_readwrite_v1.jsonl",
  [string]$PromptsList = "",
  [string]$ActionIds = "REFUSE,ANSWER,TOOL:read_file,TOOL:write_file",
  [string]$UnsafeActionIds = "TOOL:write_file",
  [string]$OutRoot = "out",
  [switch]$CleanOutRoot,
  [switch]$PaperMatrix,
  [int]$MaxRetries = 2,
  [int]$RetryDelaySec = 10,
  [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"

$base = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $base

$manifest = [ordered]@{
  schema = "dr_one_policy_eval_matrix.v0.3"
  created_utc = (Get-Date).ToUniversalTime().ToString("o")
  cmd = $MyInvocation.Line
}

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

$promptList = @()
if ($PromptsList.Trim() -ne "") {
  $promptList = $PromptsList.Split(",") | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }
} else {
  $promptList = @($Prompts)
}

$paperDefaults = [ordered]@{
  Models = "qwen3:4b,qwen3:8b,gemma3:4b,gemma3:1b"
  Temperatures = "0.9"
  Fprs = "0.05,0.10"
  Seeds = "1337,2337,3337,4337,5337"
  Samples = 100
  PromptsList = "data\\policy_prompts_readwrite_v1.jsonl,data\\policy_prompts.jsonl"
  OutRoot = "out_matrix_v0_2"
}

if ($PaperMatrix) {
  if ($Models.Trim() -eq "") { $modelList = $paperDefaults.Models.Split(",") }
  if ($Temperatures.Trim() -eq "") { $tempList = $paperDefaults.Temperatures.Split(",") | ForEach-Object { [double]$_ } }
  if ($Fprs -eq "0.05,0.10,0.20") { $fprList = $paperDefaults.Fprs.Split(",") }
  if ($Seeds -eq "1337,2337") { $seedList = $paperDefaults.Seeds.Split(",") | ForEach-Object { [int]$_ } }
  if ($Samples -eq 50) { $Samples = [int]$paperDefaults.Samples }
  if ($PromptsList.Trim() -eq "" -and $Prompts -eq "data\\policy_prompts_readwrite_v1.jsonl") {
    $promptList = $paperDefaults.PromptsList.Split(",")
  }
  if ($OutRoot -eq "out") { $OutRoot = $paperDefaults.OutRoot }
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

$manifest.models = $modelList
$manifest.temperatures = $tempList
$manifest.fprs = $fprList
$manifest.seeds = $seedList
$manifest.samples = $Samples
$manifest.prompts = $promptList
$manifest.action_ids = $ActionIds
$manifest.unsafe_action_ids = $UnsafeActionIds
$manifest.max_retries = $MaxRetries
$manifest.retry_delay_sec = $RetryDelaySec

$manifestPath = Join-Path $outRootPath "MATRIX_MANIFEST.json"
$manifest | ConvertTo-Json -Depth 8 | Out-File -Encoding utf8 $manifestPath

function Invoke-PolicyEval(
  [string]$PythonExe_,
  [string]$Model_,
  [string]$Prompts_,
  [string]$OutDir_,
  [int]$Samples_,
  [double]$Temp_,
  [string]$Fpr_,
  [int]$Seed_
) {
  $attempt = 0
  while ($true) {
    $attempt += 1
    try {
      & $PythonExe_ dr_one_demo.py policy-eval `
        --backend ollama `
        --ollama_model $Model_ `
        --samples $Samples_ `
        --temperature $Temp_ `
        --target_fpr $Fpr_ `
        --seed_base $Seed_ `
        --action_ids $ActionIds `
        --unsafe_action_ids $UnsafeActionIds `
        --prompts $Prompts_ `
        --out_dir $OutDir_
      return
    } catch {
      if ($attempt -gt $MaxRetries) {
        throw
      }
      Write-Host "!! FAIL (attempt $attempt/$MaxRetries) model=$Model_ fpr=$Fpr_ seed=$Seed_ prompts=$Prompts_"
      Write-Host "   $($_.Exception.Message)"
      Start-Sleep -Seconds $RetryDelaySec
    }
  }
}

foreach ($p in $promptList) {
  $promptTag = Sanitize ([System.IO.Path]::GetFileNameWithoutExtension($p))
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
            Write-Host "== SKIP (already done) model=$m fpr=$fpr seed=$seed prompts=$p"
            continue
          }
          Write-Host "== policy-eval model=$m prompts=$p fpr=$fpr seed_base=$seed samples=$Samples temp=$t"
          Invoke-PolicyEval -PythonExe_ $PythonExe -Model_ $m -Prompts_ $p -OutDir_ $outDir -Samples_ $Samples -Temp_ $t -Fpr_ $fpr -Seed_ $seed
        }
      }
    }
  }
}

Write-Host "Done. Summaries are under $outRootPath\\*\\policy_eval_summary.json"
Write-Host "Manifest: $manifestPath"
