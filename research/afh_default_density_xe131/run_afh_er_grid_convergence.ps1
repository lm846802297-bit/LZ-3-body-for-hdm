$ErrorActionPreference = "Stop"

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $here "..\..")).Path
$outDir = Join-Path $here "output\er_grid_convergence_2026-11-15"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$wls = Join-Path $here "run_afh_eq6_full_dsigma.wls"
$fullCompare = Join-Path $here "compare_full_dsigma_mathematica.py"
$gridCompare = Join-Path $here "compare_er_grid_convergence.py"

$fiveCsv = Join-Path $outDir "mathematica_full_dsigma_xe131_5keV.csv"
$fiveMeta = Join-Path $outDir "mathematica_full_dsigma_xe131_5keV_metadata.json"
$fivePointwise = Join-Path $outDir "pointwise_comparison_5keV.csv"
$fivePointwiseMeta = Join-Path $outDir "pointwise_comparison_5keV_metadata.json"

$oneCsv = Join-Path $outDir "mathematica_full_dsigma_xe131_1keV.csv"
$oneMeta = Join-Path $outDir "mathematica_full_dsigma_xe131_1keV_metadata.json"
$onePointwise = Join-Path $outDir "pointwise_comparison_1keV.csv"
$onePointwiseMeta = Join-Path $outDir "pointwise_comparison_1keV_metadata.json"

$summaryCsv = Join-Path $outDir "er_grid_convergence_5keV_vs_1keV.csv"
$summaryJson = Join-Path $outDir "er_grid_convergence_5keV_vs_1keV.json"

$common = @(
    "--nw", "16",
    "--nz", "16",
    "--nphi", "8",
    "--w2-mapping", "threshold_u2",
    "--width-scheme", "pole",
    "--er-start-kev", "5",
    "--er-stop-kev", "800"
)

Push-Location $repoRoot
try {
    Write-Host "=== Native Mathematica: 5-keV recoil grid ==="
    & wolframscript -file $wls @common --er-step-kev 5 --out-csv $fiveCsv --metadata $fiveMeta
    if ($LASTEXITCODE -ne 0) { throw "Mathematica 5-keV run failed with exit code $LASTEXITCODE" }

    Write-Host "=== Independent Python comparison: 5-keV grid ==="
    & python $fullCompare --mathematica-csv $fiveCsv --out-csv $fivePointwise --metadata $fivePointwiseMeta
    if ($LASTEXITCODE -ne 0) { throw "Python 5-keV comparison failed with exit code $LASTEXITCODE" }

    Write-Host "=== Native Mathematica: 1-keV recoil grid ==="
    & wolframscript -file $wls @common --er-step-kev 1 --out-csv $oneCsv --metadata $oneMeta
    if ($LASTEXITCODE -ne 0) { throw "Mathematica 1-keV run failed with exit code $LASTEXITCODE" }

    Write-Host "=== Independent Python comparison: 1-keV grid ==="
    & python $fullCompare --mathematica-csv $oneCsv --out-csv $onePointwise --metadata $onePointwiseMeta
    if ($LASTEXITCODE -ne 0) { throw "Python 1-keV comparison failed with exit code $LASTEXITCODE" }

    Write-Host "=== 5-keV versus 1-keV ER-grid convergence ==="
    & python $gridCompare --five-kev-csv $fiveCsv --one-kev-csv $oneCsv --output-csv $summaryCsv --output-json $summaryJson
    if ($LASTEXITCODE -ne 0) { throw "ER-grid convergence comparison failed with exit code $LASTEXITCODE" }

    Write-Host "PASS: both native grids, both independent pointwise comparisons, and ER-grid summary completed."
    Write-Host "Outputs: $outDir"
}
finally {
    Pop-Location
}
