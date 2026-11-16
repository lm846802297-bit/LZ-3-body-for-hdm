[CmdletBinding()]
param(
    [string]$OutputDirectory = (Join-Path $env:TEMP "lz-xe131-full-dsigma"),
    [int]$NW = 16,
    [int]$NZ = 16,
    [int]$NPhi = 8,
    [double]$RelativeTolerance = 2e-7,
    [double]$ResponseTolerance = 2e-10,
    [string]$Benchmark = "all",
    [string]$ERListKeV = "",
    [bool]$RequireFullGrid = $true
)

$ErrorActionPreference = "Stop"

$Benchmark = $Benchmark.ToLowerInvariant()
$allowedBenchmarks = @("all", "red_ms200_dm1", "green_ms300_dm1", "black_ms360_dm1", "blue_ms300_dm10")
if ($allowedBenchmarks -notcontains $Benchmark) {
    throw "Unknown benchmark: $Benchmark"
}
if ($NW -lt 1 -or $NZ -lt 1 -or $NPhi -lt 1 -or $RelativeTolerance -le 0 -or $ResponseTolerance -le 0) {
    throw "Quadrature orders and comparison tolerances must be positive."
}

if ($RequireFullGrid -and $Benchmark -ne "all") {
    throw "RequireFullGrid needs -Benchmark all. For a single-benchmark pilot, pass -RequireFullGrid `$false."
}

$studyDir = $PSScriptRoot
$wolframFile = Join-Path $studyDir "run_afh_eq6_full_dsigma.wls"
$pythonComparator = Join-Path $studyDir "compare_full_dsigma_mathematica.py"
$nativeAfhTable = Join-Path $studyDir "output\native_exports\afh_default_xe131_WM00_mathematica.csv"
$eq6Kernel = Join-Path $studyDir "..\figure2_full_reproduction\eq6_kernel.py"
$phaseSpace = Join-Path $studyDir "..\figure2_full_reproduction\phase_space_convergence.py"
$requirements = Join-Path $studyDir "requirements.txt"
$nativeAfhGenerator = Join-Path $studyDir "run_afh_default_xe131.wls"
$nativeAfhComparator = Join-Path $studyDir "compare_afh_mathematica_python.py"
$nativeAfhManifest = Join-Path $studyDir "output\native_audit\afh_native_audit_manifest.json"

if (-not (Test-Path $wolframFile)) { throw "Missing Wolfram script: $wolframFile" }
if (-not (Test-Path $pythonComparator)) { throw "Missing Python comparator: $pythonComparator" }
if (-not (Test-Path $nativeAfhTable)) { throw "Missing native Mathematica AFH response table: $nativeAfhTable" }
foreach ($requiredFile in @($eq6Kernel, $phaseSpace, $requirements, $nativeAfhGenerator, $nativeAfhComparator, $nativeAfhManifest)) {
    if (-not (Test-Path -LiteralPath $requiredFile)) { throw "Missing provenance/source file: $requiredFile" }
}

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
Remove-Item -LiteralPath $mathematicaCsv, $mathematicaMetadata -Force -ErrorAction SilentlyContinue

Write-Host "Running native Wolfram Language Eq. (6) integration..."
$wolframArgs = @(
    "-script", "run_afh_eq6_full_dsigma.wls",
    "--nw", "$NW",
    "--nz", "$NZ",
    "--nphi", "$NPhi",
    "--width-scheme", "pole",
    "--w2-mapping", "threshold_u2",
    "--er-start-kev", "5",
    "--er-stop-kev", "800",
    "--er-step-kev", "5",
    "--benchmark", $Benchmark,
    "--out-csv", $mathematicaCsv,
    "--metadata", $mathematicaMetadata
)
if (-not [string]::IsNullOrWhiteSpace($ERListKeV)) {
    $wolframArgs += @("--er-list-kev", $ERListKeV)
}
$previousLocation = Get-Location
try {
    Set-Location -LiteralPath $studyDir
    & $wolfram.Source @wolframArgs
    $wolframExitCode = $LASTEXITCODE
}
finally {
    Set-Location -LiteralPath $previousLocation
}
if ($wolframExitCode -ne 0) {
    throw "Native Wolfram calculation failed with exit code $wolframExitCode."
}
if (-not (Test-Path $mathematicaCsv) -or -not (Test-Path $mathematicaMetadata)) {
    throw "Wolfram returned success but its CSV/metadata outputs are missing."
}

Write-Host "Comparing Mathematica against the independent Python recomputation..."
$compareArgs = @(
    "compare_full_dsigma_mathematica.py",
    "--mathematica-csv", $mathematicaCsv,
    "--afh-response-csv", "output\native_exports\afh_default_xe131_WM00_mathematica.csv",
    "--out-csv", $comparisonCsv,
    "--metadata", $comparisonMetadata,
    "--rtol", "$RelativeTolerance",
    "--response-rtol", "$ResponseTolerance"
)
if ($RequireFullGrid) {
    $compareArgs += "--require-full-grid"
}
$previousLocation = Get-Location
try {
    Set-Location -LiteralPath $studyDir
    & $python.Source @compareArgs
    $pythonExitCode = $LASTEXITCODE
}
finally {
    Set-Location -LiteralPath $previousLocation
}
if ($pythonExitCode -ne 0) {
    throw "Mathematica/Python pointwise comparison failed with exit code $pythonExitCode."
}

$comparison = Get-Content -Raw -Path $comparisonMetadata | ConvertFrom-Json
$nativeMeta = Get-Content -Raw -Path $mathematicaMetadata | ConvertFrom-Json
if ($comparison.status -ne "PASS") {
    throw "Comparison metadata did not report PASS."
}
if ([int]$nativeMeta.output.rows -ne [int]$comparison.rows) {
    throw "Mathematica metadata row count does not match the Python comparison."
}
if ([double]$nativeMeta.particle_inputs.speed_km_s -ne 800.0) {
    throw "Unexpected fixed speed in Mathematica metadata; expected 800 km/s."
}
if ($nativeMeta.integration.width_scheme -ne "pole" -or $nativeMeta.integration.W2_mapping -ne "threshold_u2") {
    throw "Unexpected width or W2-mapping convention in Mathematica metadata."
}
if ([int]$nativeMeta.integration.quadrature.nW -ne $NW -or [int]$nativeMeta.integration.quadrature.nz -ne $NZ -or [int]$nativeMeta.integration.quadrature.nphi -ne $NPhi) {
    throw "Mathematica metadata quadrature orders do not match the requested orders."
}
if ($RequireFullGrid -and (-not [bool]$comparison.full_grid_required -or [int]$comparison.rows -ne 652 -or [int]$comparison.open_phase_space_rows -ne 500)) {
    throw "Full-grid acceptance requires full_grid_required=true, 652 rows and 500 open phase-space rows."
}

$filesToHash = @(
    $wolframFile, $pythonComparator, $PSCommandPath, $eq6Kernel, $phaseSpace,
    $nativeAfhGenerator, $nativeAfhComparator, $nativeAfhManifest,
    $requirements, $nativeAfhTable,
    $mathematicaCsv, $mathematicaMetadata, $comparisonCsv, $comparisonMetadata
)
$hashEntries = @()
foreach ($file in $filesToHash) {
    if (-not (Test-Path -LiteralPath $file)) {
        throw "Cannot create a complete provenance manifest; missing file: $file"
    }
    $hash = Get-FileHash -LiteralPath $file -Algorithm SHA256
    $hashEntries += [pscustomobject]@{
        file = (Split-Path -Leaf $file)
        sha256 = $hash.Hash.ToLowerInvariant()
    }
}
$manifest = [ordered]@{
    schema_version = 1
    generated_utc = [DateTime]::UtcNow.ToString("o")
    status = $comparison.status
    benchmark = $Benchmark
    speed_km_s = [double]$nativeMeta.particle_inputs.speed_km_s
    require_full_grid = $RequireFullGrid
    rows = [int]$comparison.rows
    benchmarks = $comparison.benchmarks
    recoil_energies_keV = $comparison.recoil_energies_keV
    open_phase_space_rows = [int]$comparison.open_phase_space_rows
    quadrature = [ordered]@{ nW = $NW; nz = $NZ; nphi = $NPhi }
    width_scheme = $nativeMeta.integration.width_scheme
    W2_mapping = $nativeMeta.integration.W2_mapping
    max_relative_differences = $comparison.max_relative_differences
    wolfram_environment = $nativeMeta.environment
    python_environment = $comparison.python_environment
    files = $hashEntries
}
$manifestPath = Join-Path $OutputDirectory "full_dsigma_sha256_manifest.json"
$manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $manifestPath -Encoding UTF8
$hashLines = $hashEntries | ForEach-Object { "$($_.sha256)  $($_.file)" }
$hashLines | Set-Content -LiteralPath (Join-Path $OutputDirectory "SHA256SUMS.txt") -Encoding ASCII

Write-Host ""
Write-Host "PASS: full Xe-131 Mathematica/Python dSigma/dER comparison completed."
Write-Host ("Compared rows: {0}; open phase-space rows: {1}" -f $comparison.rows, $comparison.open_phase_space_rows)
Write-Host ("Maximum I6 relative difference: {0:E6}" -f $comparison.max_relative_differences.I6)
Write-Host ("Maximum dSigma relative difference: {0:E6}" -f $comparison.max_relative_differences.dsigma)
Write-Host ("Maximum AFH response relative difference: {0:E6}" -f $comparison.max_relative_differences.R_A_physical)
Write-Host ("Factor-four mapping residual: {0:E6}" -f $comparison.max_relative_differences.factor4_mapping)
Write-Host ("Comparison archive: {0}" -f $OutputDirectory)
Write-Host ("SHA-256 manifest: {0}" -f $manifestPath)
