$ErrorActionPreference = 'Stop'
$runRoot = [System.IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot)).TrimEnd('\')
$inspectionPath = Join-Path $runRoot 'outputs\_inspection'
$expectedPath = [System.IO.Path]::GetFullPath($inspectionPath)
if (Test-Path -LiteralPath $inspectionPath) {
    $actualPath = (Resolve-Path -LiteralPath $inspectionPath).Path
    if ($actualPath -ne $expectedPath -or -not $actualPath.StartsWith($runRoot + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing cleanup outside the intended run: $actualPath"
    }
    Remove-Item -LiteralPath $actualPath -Recurse -Force
}
Write-Output 'Temporary inspection files removed; scripts and final outputs retained.'

