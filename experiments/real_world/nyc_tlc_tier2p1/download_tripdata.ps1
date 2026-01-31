param(
  [Parameter(Mandatory=$true)]
  [ValidateSet("green","fhvhv")]
  [string]$Dataset,

  [int]$YearStart = 2019,
  [int]$YearEnd = 2023,

  [string]$OutDir = "data/raw",

  [int]$MaxFiles = 0
)

$ErrorActionPreference = "Stop"

$base = "https://d37ci6vzurychx.cloudfront.net/trip-data"
$OutDirPath = Resolve-Path -LiteralPath (Join-Path (Get-Location) $OutDir) -ErrorAction SilentlyContinue
if (-not $OutDirPath) {
  New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
  $OutDirPath = Resolve-Path -LiteralPath (Join-Path (Get-Location) $OutDir)
}

$count = 0
for ($y = $YearStart; $y -le $YearEnd; $y++) {
  for ($m = 1; $m -le 12; $m++) {
    $mm = "{0:D2}" -f $m
    $name = "${Dataset}_tripdata_${y}-${mm}.parquet"
    $url = "$base/$name"
    $dest = Join-Path $OutDirPath $name

    if (Test-Path $dest) {
      Write-Host "Skip (exists): $name"
      continue
    }

    Write-Host "Download: $url"
    try {
      Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing
    } catch {
      Write-Warning "Failed: $name ($($_.Exception.Message))"
      if (Test-Path $dest) { Remove-Item $dest -Force }
    }

    $count++
    if ($MaxFiles -gt 0 -and $count -ge $MaxFiles) {
      Write-Host "MaxFiles reached ($MaxFiles). Stopping."
      exit 0
    }
  }
}

