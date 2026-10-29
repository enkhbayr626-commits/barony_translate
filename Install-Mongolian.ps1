param(
    [string]$GamePath,
    [string]$PackageRoot = $PSScriptRoot
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'scripts\Mongolian.Common.ps1')
Install-MnPackage -GamePath $GamePath -PackageRoot $PackageRoot
