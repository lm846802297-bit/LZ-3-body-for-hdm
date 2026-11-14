[CmdletBinding()]
param(
    [string]$OutputDirectory = (Join-Path $env:TEMP "lz-xe131-full-dsigma"),
    [int]$NW = 16,
    [int]$NZ = 16,
    [int]$NPhi = 8,
    [double]$RelativeTolerance = 2e-7,
    [double]$ResponseTolerance = 2e-8
)

$ErrorActionPreference = "Stop"

$studyDir = $PSScriptRoot
$wolframFile = Join-Path $studyDir "run_afh_eq6_full_dsigma.wls"
$pythonComparator = Join-Path $studyDir "compare_full_dsigma_mathematica.py"
$pythonAfhTable = Join-Path $studyDir "output\afh_default_xe131_WM00.csv"
$nativeAfhTable = Join-Path $studyDir "output\native_exports\afh_default_xe131_WM00_mathematica.csv"

if (-not (Test-Path $wolframFile)) { throw "Missing Wolfram script: $wolframFile" }
if (-not (Test-Path $pythonComparator)) { throw "Missing Python comparator: $pythonComparator" }
if (-not (Test-Path $pythonAfhTable)) { throw "Missing Python AFH response table: $pythonAfhTable" }
if (-not (Test-Path $nativeAfhTable)) { throw "Missing native Mathematica AFH response table: $nativeAfhTable" }

$wolfram = Get-Command "wolframscript" -ErrorAction SilentlyContinue
if (-not $wolfram) {
    throw "wolframscript was not found on PATH. Install/activate Mathematica or Wolfram Engine and verify wolframscript -version."
}
$python = Get-Command "python" -ErrorAction SilentlyContinue
if (-not $python) { throw "python was not found on PATH." }

& $python.Source -c "import numpy, pandas, scipy"
if ($LASTEXITCODE -ne 0) {
    throw "Python dependencies missing. Install research/afh_default_density_xe131/requirements.txt first."
}

New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$mathematicaCsv = Join-Path $OutputDirectory "mathematica_full_dsigma_xe131.csv"
$mathematicaMetadata = Join-Path $OutputDirectory "mathematica_full_dsigma_xe131_metadata.json"
$comparisonCsv = Join-Path $OutputDirectory "mathematica_python_full_dsigma_comparison.csv"
$comparisonMetadata = Join-Path $OutputDirectory "mathematica_python_full_dsigma_comparison.json"

Write-Host "Running native Wolfram Language Eq. (6) integration..."
$wolframArgs = @(
    "-file", $wolframFile,
    "--nw", "$NW",
    "--nz", "$NZ",
    "--nphi", "$NPhi",
    "--width-scheme", "pole",
    "--w2-mapping", "threshold_u2",
    "--er-start-kev", "5",
    "--er-stop-kev", "800",
    "--er-step-kev", "5",
    "--out-csv", $mathematicaCsv,
    "--metadata", $mathematicaMetadata
)
& $wolfram.Source @wolframArgs
if ($LASTEXITCODE -ne 0) {
    throw "Native Wolfram calculation failed with exit code $LASTEXITCODE."
}
if (-not (Test-Path $mathematicaCsv) -or -not (Test-Path $mathematicaMetadata)) {
    throw "Wolfram returned success but its CSV/metadata outputs are missing."
}

Write-Host "Comparing Mathematica against the independent Python recomputation..."
$compareArgs = @(
    $pythonComparator,
    "--mathematica-csv", $mathematicaCsv,
    "--afh-response-csv", $pythonAfhTable,
    "--out-csv", $comparisonCsv,
    "--metadata", $comparisonMetadata,
    "--rtol", "$RelativeTolerance",
    "--response-rtol", "$ResponseTolerance"
)
& $python.Source @compareArgs
if ($LASTEXITCODE -ne 0) {
    throw "Mathematica/Python pointwise comparison failed with exit code $LASTEXITCODE."
}

$comparison = Get-Content -Raw -Path $comparisonMetadata | ConvertFrom-Json
if ($comparison.status -ne "PASS") {
    throw "Comparison metadata did not report PASS."
}

Write-Host ""
Write-Host "PASS: full Xe-131 Mathematica/Python dSigma/dER comparison completed."
Write-Host ("Compared rows: {0}; open phase-space rows: {1}" -f $comparison.rows, $comparison.open_phase_space_rows)
Write-Host ("Maximum I6 relative difference: {0:E6}" -f $comparison.max_relative_differences.I6)
Write-Host ("Maximum dSigma relative difference: {0:E6}" -f $comparison.max_relative_differences.dsigma)
Write-Host ("Maximum AFH response relative difference: {0:E6}" -f $comparison.max_relative_differences.R_A_physical)
Write-Host ("Factor-four mapping residual: {0:E6}" -f $comparison.max_relative_differences.factor4_mapping)
Write-Host ("Comparison archive: {0}" -f $OutputDirectory)
