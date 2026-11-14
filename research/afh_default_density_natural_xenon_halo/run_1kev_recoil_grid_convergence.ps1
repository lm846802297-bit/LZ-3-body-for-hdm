$ErrorActionPreference = "Stop"

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $here "..\..")).Path
$script = Join-Path $here "run_afh7_hybrid9_continuous_spectrum.py"
$compare = Join-Path $here "compare_5kev_1kev_recoil_grid.py"
$requirements = Join-Path $repoRoot "research\afh_default_density_xe131\requirements.txt"

$fiveDir = Join-Path $here "results\afh7_hybrid9_continuous_2026-11-14"
$oneDir = Join-Path $here "results\afh7_hybrid9_continuous_1keV_2026-11-15"
$summaryDir = Join-Path $here "results\recoil_grid_convergence_2026-11-15"

$fiveCsv = Join-Path $fiveDir "afh_hybrid9_natural_xenon_spectrum.csv"
$fiveMeta = Join-Path $fiveDir "metadata.json"
$oneCsv = Join-Path $oneDir "afh_hybrid9_natural_xenon_spectrum.csv"
$oneMeta = Join-Path $oneDir "metadata.json"
$efficiency = Join-Path $repoRoot "research\lz_detector_response\lz_2026_extended_nr\lz_2026_nr_efficiency_digitized.csv"

foreach ($inputPath in @($fiveCsv, $fiveMeta, $requirements, $efficiency)) {
    if (-not (Test-Path $inputPath)) { throw "Required input is missing: $inputPath" }
}

Push-Location $repoRoot
try {
    Write-Host "=== Verify Python numerical dependencies ==="
    & python -c "import numpy, scipy; print('numpy', numpy.__version__, 'scipy', scipy.__version__)"
    if ($LASTEXITCODE -ne 0) { throw "Python numerical dependencies are unavailable" }

    Write-Host "=== Run natural-xenon 1-keV recoil grid ==="
    $runArgs = @(
        $script,
        "--outdir", $oneDir,
        "--benchmarks", "red_ms200_dm1", "green_ms300_dm1", "black_ms360_dm1", "blue_ms300_dm10",
        "--er-min-keV", "5",
        "--er-max-keV", "800",
        "--er-step-keV", "1",
        "--fine-er-max-keV", "270",
        "--high-er-step-keV", "20",
        "--mchi-GeV", "1000",
        "--mV-GeV", "10",
        "--coupling-product-sq", "1e-8",
        "--rhoDM-GeV-cm3", "0.3",
        "--g2", "1",
        "--v0-km-s", "220",
        "--ve-km-s", "232",
        "--vesc-km-s", "544",
        "--nv", "24",
        "--nw", "6",
        "--nz", "6",
        "--nphi", "3",
        "--nv-low", "16",
        "--nw-high", "12",
        "--nz-high", "12",
        "--nphi-high", "6",
        "--max-relative-check", "0.005"
    )
    & python @runArgs
    if ($LASTEXITCODE -ne 0) { throw "Natural-xenon 1-keV spectrum run failed" }

    Write-Host "=== Compare archived 5-keV and new 1-keV grids ==="
    $compareArgs = @(
        $compare,
        "--five-kev-csv", $fiveCsv,
        "--five-kev-metadata", $fiveMeta,
        "--one-kev-csv", $oneCsv,
        "--one-kev-metadata", $oneMeta,
        "--efficiency-csv", $efficiency,
        "--out-dir", $summaryDir
    )
    & python @compareArgs
    if ($LASTEXITCODE -ne 0) { throw "5-keV versus 1-keV convergence comparison failed" }

    Write-Host "PASS: 1-keV calculation and grid comparison completed."
    Write-Host "1-keV outputs: $oneDir"
    Write-Host "Grid comparison: $summaryDir"
}
finally {
    Pop-Location
}
