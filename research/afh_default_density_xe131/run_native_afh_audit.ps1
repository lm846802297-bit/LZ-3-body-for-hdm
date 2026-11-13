[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$AfhSource
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$tempExtract = $null
Push-Location $scriptDir

try {
    $sourceInput = (Resolve-Path -LiteralPath $AfhSource).Path
    if (-not (Test-Path -LiteralPath $sourceInput -PathType Leaf)) {
        throw "AfhSource must be a .m file or the original AFH v6.0 ZIP archive."
    }

    $expectedArchiveSha = "4e0f70e6e780f3f4a40faa14792cae239d1989cf15d1e211b4fd7389b0460727"
    $expectedSourceSha = "dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372"
    $expectedMatrixSha = "f656145ba2fb9da741b77faed4c01d0dc457c955fa340928b5dbf9cee9bc5d45"
    $archiveSha = $null

    if ([IO.Path]::GetExtension($sourceInput).ToLowerInvariant() -eq ".zip") {
        $archiveSha = (Get-FileHash -LiteralPath $sourceInput -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($archiveSha -ne $expectedArchiveSha) {
            throw "AFH ZIP SHA-256 mismatch. Expected $expectedArchiveSha, got $archiveSha."
        }
        $tempExtract = Join-Path $env:TEMP ("afh-v6-native-" + [Guid]::NewGuid().ToString("N"))
        New-Item -ItemType Directory -Force -Path $tempExtract | Out-Null
        Expand-Archive -LiteralPath $sourceInput -DestinationPath $tempExtract -Force
        $matches = @(Get-ChildItem -LiteralPath $tempExtract -Filter "dmformfactor-V6.m" -File -Recurse)
        if ($matches.Count -ne 1) {
            throw "Expected exactly one dmformfactor-V6.m in the AFH ZIP; found $($matches.Count)."
        }
        $packagePath = $matches[0].FullName
    }
    else {
        if ([IO.Path]::GetFileName($sourceInput) -ne "dmformfactor-V6.m") {
            throw "The source file must be named dmformfactor-V6.m."
        }
        $packagePath = $sourceInput
    }

    $sourceSha = (Get-FileHash -LiteralPath $packagePath -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($sourceSha -ne $expectedSourceSha) {
        throw "AFH source SHA-256 mismatch. Expected $expectedSourceSha, got $sourceSha."
    }

    $matrixPath = Join-Path $scriptDir "afh_default_xe131_density_matrix.csv"
    $matrixSha = (Get-FileHash -LiteralPath $matrixPath -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($matrixSha -ne $expectedMatrixSha) {
        throw "Archived 67-entry Xe-131 density-matrix SHA-256 mismatch. Expected $expectedMatrixSha, got $matrixSha."
    }

    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        throw "Python was not found on PATH."
    }
    if (-not (Get-Command wolframscript -ErrorAction SilentlyContinue)) {
        throw "wolframscript was not found on PATH. Install/activate Wolfram Engine or Mathematica first."
    }

    $outputDir = Join-Path $scriptDir "output"
    $auditDir = Join-Path $outputDir "native_audit"
    New-Item -ItemType Directory -Force -Path $outputDir, $auditDir | Out-Null

    $env:DMFormFactorPath = $packagePath
    $env:AFHPythonCSV = Join-Path $outputDir "afh_default_xe131_WM00.csv"
    $env:AFHAuditDir = $auditDir

    Write-Host "[1/4] Rebuild Python reference and verify all 67 matrix entries against the official AFH source..."
    & python ".\run_afh_default_xe131.py" --afh-package $packagePath --density-matrix-csv $matrixPath --outdir $outputDir
    if ($LASTEXITCODE -ne 0) { throw "Python AFH reference generation failed with exit code $LASTEXITCODE." }

    Write-Host "[2/4] Run the AFH v6.0 package natively in Wolfram..."
    & wolframscript -file ".\run_afh_default_xe131.wls"
    if ($LASTEXITCODE -ne 0) { throw "Native AFH Mathematica calculation failed with exit code $LASTEXITCODE." }

    Write-Host "[3/4] Independently evaluate the same 2401 q nodes in Wolfram and compare against Python..."
    & wolframscript -file ".\verify_afh_xe131_native.wls"
    if ($LASTEXITCODE -ne 0) { throw "Native Wolfram/Python pointwise verifier failed with exit code $LASTEXITCODE." }

    Write-Host "[4/4] Produce the machine-readable comparison and SHA-256 manifest..."
    $pythonCsv = Join-Path $outputDir "afh_default_xe131_WM00.csv"
    $mathematicaCsv = Join-Path $scriptDir "afh_default_xe131_WM00_mathematica.csv"
    $comparisonJson = Join-Path $auditDir "afh_mathematica_python_comparison.json"
    & python ".\compare_afh_mathematica_python.py" --python-csv $pythonCsv --mathematica-csv $mathematicaCsv --output $comparisonJson
    if ($LASTEXITCODE -ne 0) { throw "Final Python/MMA comparison failed with exit code $LASTEXITCODE." }

    $nativeMetadata = Join-Path $auditDir "afh_native_audit_metadata.txt"
    $metadataLines = Get-Content -LiteralPath $nativeMetadata
    $wolframVersionLine = $metadataLines | Where-Object { $_ -like "WolframVersion = *" } | Select-Object -First 1
    $hashFiles = @(
        $pythonCsv,
        $mathematicaCsv,
        $comparisonJson,
        (Join-Path $auditDir "afh_native_audit_grid.csv"),
        (Join-Path $auditDir "afh_native_audit_comparison.csv"),
        (Join-Path $auditDir "afh_native_audit_minima.csv"),
        $nativeMetadata
    )
    foreach ($file in $hashFiles) {
        if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
            throw "Expected audit output was not produced: $file"
        }
    }

    $manifest = [ordered]@{
        status = "PASS"
        afHArchiveSha256 = $archiveSha
        afhSourceFileSha256 = $sourceSha
        densityMatrixCsvSha256 = $matrixSha
        wolframVersion = if ($wolframVersionLine) { $wolframVersionLine -replace "^WolframVersion = ", "" } else { "not recorded" }
        pythonReferenceCsvSha256 = (Get-FileHash -LiteralPath $pythonCsv -Algorithm SHA256).Hash.ToLowerInvariant()
        mathematicaNativeCsvSha256 = (Get-FileHash -LiteralPath $mathematicaCsv -Algorithm SHA256).Hash.ToLowerInvariant()
        comparisonJsonSha256 = (Get-FileHash -LiteralPath $comparisonJson -Algorithm SHA256).Hash.ToLowerInvariant()
        nativeGridCsvSha256 = (Get-FileHash -LiteralPath (Join-Path $auditDir "afh_native_audit_grid.csv") -Algorithm SHA256).Hash.ToLowerInvariant()
        nativeComparisonCsvSha256 = (Get-FileHash -LiteralPath (Join-Path $auditDir "afh_native_audit_comparison.csv") -Algorithm SHA256).Hash.ToLowerInvariant()
        nativeMinimaCsvSha256 = (Get-FileHash -LiteralPath (Join-Path $auditDir "afh_native_audit_minima.csv") -Algorithm SHA256).Hash.ToLowerInvariant()
        nativeMetadataSha256 = (Get-FileHash -LiteralPath $nativeMetadata -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    $manifestPath = Join-Path $auditDir "afh_native_audit_manifest.json"
    $manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $manifestPath -Encoding UTF8

    Write-Host ""
    Write-Host "PASS: AFH native Mathematica/Python audit completed."
    Write-Host "Manifest: $manifestPath"
    Write-Host "Artifacts: $auditDir"
}
finally {
    Pop-Location
    if ($tempExtract -and (Test-Path -LiteralPath $tempExtract)) {
        Remove-Item -LiteralPath $tempExtract -Recurse -Force
    }
}
