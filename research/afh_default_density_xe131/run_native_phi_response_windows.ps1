param(
    [string]$WolframScript = "wolframscript",
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$wlsPath = Join-Path $scriptDir "run_afh_phi_response_xe131.wls"
$validatorPath = Join-Path $scriptDir "validate_afh_phi_response.py"
$outputDir = Join-Path (Join-Path $scriptDir "output") "phi_response_native"

$wolframCommand = Get-Command $WolframScript -ErrorAction Stop
$pythonCommand = Get-Command $Python -ErrorAction Stop
if (-not (Test-Path -LiteralPath $wlsPath -PathType Leaf)) {
    throw "Native Wolfram runner not found: $wlsPath"
}
if (-not (Test-Path -LiteralPath $validatorPath -PathType Leaf)) {
    throw "Python validator not found: $validatorPath"
}

Write-Host "[1/3] Run native AFH v6.0 Xe-131 M/Phi'' response export..."
& $wolframCommand.Source -file $wlsPath
if ($LASTEXITCODE -ne 0) {
    throw "wolframscript failed with exit code $LASTEXITCODE"
}

$csvPath = Join-Path $outputDir "afh_default_xe131_M_PhiPP_native.csv"
$metadataPath = Join-Path $outputDir "afh_default_xe131_M_PhiPP_metadata.json"
$summaryPath = Join-Path $outputDir "afh_default_xe131_M_PhiPP_validation.json"
foreach ($path in @($csvPath, $metadataPath)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Expected native output is missing: $path"
    }
}

Write-Host "[2/3] Validate response normalization, Cauchy-Schwarz, grid, and provenance..."
& $pythonCommand.Source $validatorPath --csv $csvPath --metadata $metadataPath --summary $summaryPath
if ($LASTEXITCODE -ne 0) {
    throw "AFH Phi'' response validation failed with exit code $LASTEXITCODE"
}

Write-Host "[3/3] Write local SHA-256 provenance manifest..."
$metadata = Get-Content -LiteralPath $metadataPath -Raw | ConvertFrom-Json
$manifest = [ordered]@{
    status = "COMPLETED"
    files = [ordered]@{
        "afh_default_xe131_M_PhiPP_native.csv" = (Get-FileHash -LiteralPath $csvPath -Algorithm SHA256).Hash.ToLowerInvariant()
        "afh_default_xe131_M_PhiPP_metadata.json" = (Get-FileHash -LiteralPath $metadataPath -Algorithm SHA256).Hash.ToLowerInvariant()
        "afh_default_xe131_M_PhiPP_validation.json" = (Get-FileHash -LiteralPath $summaryPath -Algorithm SHA256).Hash.ToLowerInvariant()
    }
}
$manifestPath = Join-Path $outputDir "sha256_manifest.json"
$manifest | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $manifestPath -Encoding UTF8

Write-Host "PASS: Xe-131 M/Phi'' native AFH response export and validator."
Write-Host "CSV: $csvPath"
Write-Host "Metadata: $metadataPath"
Write-Host "Validation: $summaryPath"
Write-Host "Manifest: $manifestPath"
