[CmdletBinding()]
param(
    [ValidateRange(1, 1000000)]
    [int]$EventsPerEnergy = 2000,

    [UInt64]$Seed = 20261115,

    [string]$OutputDir = (Join-Path $env:LOCALAPPDATA "LZ-3-body-for-hdm\nr_event_response")
)

$ErrorActionPreference = "Stop"

$NestCommit = "423b9745a5bfbb0402514f1d7955e67445de0810"
$NestUrl = "https://github.com/NESTCollaboration/nest.git"
$NestDir = Join-Path $PSScriptRoot ("_deps\nest-" + $NestCommit)
$BuildDir = Join-Path $PSScriptRoot "_build-nr-event-response"
$ParameterFile = Join-Path $PSScriptRoot "lz_2026_extended_nr\lz_2026_nr_yield_params_s5.txt"
$SummaryScript = Join-Path $PSScriptRoot "lz_2026_extended_nr\summarize_nr_event_response.py"
$TestsDir = Join-Path $PSScriptRoot "tests"

function Invoke-Checked {
    param([scriptblock]$Command, [string]$Description)
    Write-Host ("== " + $Description + " ==") -ForegroundColor Cyan
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Description failed with exit code $LASTEXITCODE"
    }
}

foreach ($tool in @("git", "cmake", "python")) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        throw "Required command '$tool' was not found in PATH."
    }
}

if (-not (Test-Path (Join-Path $NestDir ".git"))) {
    New-Item -ItemType Directory -Force -Path (Split-Path $NestDir) | Out-Null
    Invoke-Checked { git clone --filter=blob:none $NestUrl $NestDir } "Clone NEST source"
}

Invoke-Checked { git -C $NestDir fetch --depth 1 origin $NestCommit } "Fetch pinned NEST commit"
Invoke-Checked { git -C $NestDir checkout --detach $NestCommit } "Check out pinned NEST commit"

$actualCommit = (git -C $NestDir rev-parse HEAD).Trim()
if ($actualCommit -ne $NestCommit) {
    throw "NEST source pin mismatch: expected $NestCommit, got $actualCommit"
}

Invoke-Checked { python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" } "Check Python >= 3.10"

Invoke-Checked {
    python -m unittest discover -s $TestsDir -p "test_lz_2026_nr_*.py" -v
} "Run NR mean-yield and event-response configuration tests"

if (-not (Test-Path $ParameterFile)) {
    throw "Missing LZ 2026 Table S5 parameter file: $ParameterFile"
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

Invoke-Checked {
    cmake -S $PSScriptRoot -B $BuildDir "-DNEST_SOURCE_DIR=$NestDir" "-DCMAKE_BUILD_TYPE=Release"
} "Configure CMake project"

Invoke-Checked {
    cmake --build $BuildDir --config Release --target lz_2026_nr_event_response --parallel
} "Build NEST core and event-response driver"

$Executable = Get-ChildItem -Path $BuildDir -Recurse -File -Filter "lz_2026_nr_event_response.exe" |
    Select-Object -First 1
if (-not $Executable) {
    $Executable = Get-ChildItem -Path $BuildDir -Recurse -File -Filter "lz_2026_nr_event_response" |
        Select-Object -First 1
}
if (-not $Executable) {
    throw "Could not locate the compiled lz_2026_nr_event_response executable."
}

$Ws2024Csv = Join-Path $OutputDir "lz_2026_nr_response_ws2024.csv"
$GenericCsv = Join-Path $OutputDir "lz_2026_nr_response_generic.csv"
$SummaryJson = Join-Path $OutputDir "lz_2026_nr_response_summary.json"
$SummaryCsv = Join-Path $OutputDir "lz_2026_nr_response_summary.csv"
$RunMetadata = Join-Path $OutputDir "lz_2026_nr_response_run_metadata.json"

Invoke-Checked {
    & $Executable.FullName "ws2024" "$EventsPerEnergy" "$Seed" $Ws2024Csv $ParameterFile
} "Run LZ WS2024-tuned NR fluctuation baseline"

Invoke-Checked {
    & $Executable.FullName "generic" "$EventsPerEnergy" "$Seed" $GenericCsv $ParameterFile
} "Run generic NEST NR fluctuation comparison"

Invoke-Checked {
    python $SummaryScript --inputs $Ws2024Csv $GenericCsv --output-json $SummaryJson --output-csv $SummaryCsv
} "Summarize event-level distributions"

$metadata = [ordered]@{
    generated_utc = [DateTime]::UtcNow.ToString("o")
    repository_branch = "research/figure2-p0-4-mainline"
    nest_repository = $NestUrl
    nest_commit = $NestCommit
    events_per_energy_per_baseline = $EventsPerEnergy
    seed = $Seed
    energies_keV = @(5.4, 10.0, 50.0, 74.7, 100.0, 150.0, 200.0, 248.0, 269.9)
    baselines = @("ws2024", "generic")
    detector_class = "LZ_Detector_2024 from include/Detectors/LZ_WS2024.hh"
    nr_mean_yield = "LZ 2026 Supplemental Table S5, 15 parameters"
    s1_mode = "NEST::S1CalculationMode::Full"
    s2_mode = "NEST::S2CalculationMode::Full"
    position = "x=y=0; z=TopDrift-vD*dtCntr (NEST reference depth)"
    raw_outputs = @($Ws2024Csv, $GenericCsv)
    summaries = @($SummaryJson, $SummaryCsv)
}
$metadata | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 $RunMetadata

Write-Host "Completed local NEST NR event-response pilot." -ForegroundColor Green
Write-Host "Output directory: $OutputDir"
Write-Host "Summary JSON:     $SummaryJson"
Write-Host "Summary CSV:      $SummaryCsv"
Write-Host "Run metadata:     $RunMetadata"
