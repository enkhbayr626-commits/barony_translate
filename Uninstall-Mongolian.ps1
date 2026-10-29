param([string]$GamePath)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'scripts\Mongolian.Common.ps1')
Uninstall-MnPackage -GamePath $GamePath
