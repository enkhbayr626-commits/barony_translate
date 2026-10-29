# Integration tests use a fake game inside this workspace; no installed game is touched.
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..\scripts\Mongolian.Common.ps1')
$testRoot = Join-Path $PSScriptRoot ('tmp-install-' + [guid]::NewGuid().ToString('N'))
$game = Join-Path $testRoot 'game'
$pkg = Join-Path $testRoot 'package'
$null = New-Item -ItemType Directory -Path $game -Force
$null = New-Item -ItemType Directory -Path (Join-Path $pkg 'Barony-Mongolian\lang') -Force
$null = New-Item -ItemType Directory -Path (Join-Path $pkg 'Barony-Mongolian\data') -Force
$null = New-Item -ItemType Directory -Path (Join-Path $game 'lang') -Force
$null = New-Item -ItemType Directory -Path (Join-Path $game 'data') -Force
$null = New-Item -ItemType Directory -Path (Join-Path $game 'savegames') -Force
[IO.File]::WriteAllText((Join-Path $game 'barony.exe'),'fake executable - never launched')
[IO.File]::WriteAllText((Join-Path $game 'lang\en.txt'),'English original')
[IO.File]::WriteAllText((Join-Path $game 'data\sample.json'),'{"original":true}')
[IO.File]::WriteAllText((Join-Path $game 'savegames\save.json'),'precious saved game')
[IO.File]::WriteAllText((Join-Path $pkg 'Barony-Mongolian\lang\en.txt'),'Mongolian version 1')
[IO.File]::WriteAllText((Join-Path $pkg 'Barony-Mongolian\data\sample.json'),'{"translated":true}')
$enHash = Get-MnHash (Join-Path $game 'lang\en.txt')
$jsonHash = Get-MnHash (Join-Path $game 'data\sample.json')
$saveHash = Get-MnHash (Join-Path $game 'savegames\save.json')
$exeHash = Get-MnHash (Join-Path $game 'barony.exe')
$manifest = [pscustomobject]@{schemaVersion=1;version='test-1';files=@(
    [pscustomobject]@{path='lang/en.txt';sha256=(Get-MnHash (Join-Path $pkg 'Barony-Mongolian\lang\en.txt'));originalSha256=$enHash},
    [pscustomobject]@{path='data/sample.json';sha256=(Get-MnHash (Join-Path $pkg 'Barony-Mongolian\data\sample.json'));originalSha256=$jsonHash}
)}
Write-MnJson (Join-Path $pkg 'package-manifest.json') $manifest
function Assert-Equal($Actual, $Expected, [string]$Label) {
    if ($Actual -ne $Expected) { throw "FAIL: $Label ($Actual != $Expected)" }
}
function Assert-Fails([scriptblock]$Action, [string]$Pattern) {
    $caught = $false
    try { & $Action | Out-Null } catch {
        if ($_.Exception.Message -notlike $Pattern) { throw "Unexpected error: $($_.Exception.Message)" }
        $caught = $true
    }
    if (-not $caught) { throw "Expected refusal: $Pattern" }
}

try {
    # Registry and VDF commonly describe one Steam library with multiple casing
    # and slash variants. These must resolve to one candidate, not an ambiguity.
    $steamFixture = Join-Path $testRoot 'Steam'
    $steamGame = Join-Path $steamFixture 'steamapps\common\Barony'
    $null = New-Item -ItemType Directory -Path $steamGame -Force
    [IO.File]::WriteAllText((Join-Path $steamGame 'barony.exe'),'fake executable - never launched')
    $vdfPath = Join-Path $steamFixture 'steamapps\libraryfolders.vdf'
    [IO.File]::WriteAllText($vdfPath,('"libraryfolders" { "0" { "path" "' + $steamFixture.Replace('\','\\') + '" } }'))
    $detected = @(Get-MnSteamGameCandidates @($steamFixture,$steamFixture.ToLowerInvariant().Replace('\','/'),($steamFixture + '\')))
    Assert-Equal $detected.Count 1 'Autodetection deduplicates registry and VDF path aliases'
    Assert-Equal $detected[0].ToLowerInvariant() $steamGame.ToLowerInvariant() 'Autodetection chooses actual Steam game'

    # Invalid original or corrupt payload must be rejected before any game mutation.
    [IO.File]::WriteAllText((Join-Path $game 'data\sample.json'),'Steam updated this file')
    Assert-Fails { Install-MnPackage $game $pkg } '*Original file does not match*'
    Assert-Equal (Get-MnHash (Join-Path $game 'lang\en.txt')) $enHash 'No partial install after wrong-version refusal'
    [IO.File]::WriteAllText((Join-Path $game 'data\sample.json'),'{"original":true}')
    [IO.File]::AppendAllText((Join-Path $pkg 'Barony-Mongolian\lang\en.txt'),'corrupted')
    Assert-Fails { Install-MnPackage $game $pkg } '*Payload checksum failed*'
    [IO.File]::WriteAllText((Join-Path $pkg 'Barony-Mongolian\lang\en.txt'),'Mongolian version 1')

    # Force a mid-install I/O failure. Every changed game file must roll back.
    $script:injectCopyFailure = $true
    function Copy-Item {
        param([string]$LiteralPath,[string]$Destination,[switch]$Force)
        if ($script:injectCopyFailure -and $Destination -eq (Join-Path $game 'data\sample.json')) {
            $script:injectCopyFailure = $false
            throw 'Injected disk-write failure'
        }
        Microsoft.PowerShell.Management\Copy-Item -LiteralPath $LiteralPath -Destination $Destination -Force:$Force
    }
    Assert-Fails { Install-MnPackage $game $pkg } '*Injected disk-write failure*'
    Remove-Item Function:\Copy-Item
    Assert-Equal (Get-MnHash (Join-Path $game 'lang\en.txt')) $enHash 'Install failure restored first file'
    Assert-Equal (Get-MnHash (Join-Path $game 'data\sample.json')) $jsonHash 'Install failure restored second file'

    Install-MnPackage $game $pkg
    Install-MnPackage $game $pkg
    Assert-Equal (Get-MnHash (Join-Path $game 'lang\en.txt')) $manifest.files[0].sha256 'Repeated install is idempotent'
    Assert-Equal (Get-MnHash (Join-Path $game '.barony-mongolian-backup\originals\lang\en.txt')) $enHash 'English original retained'

    # A package for another game baseline must also be refused during an update.
    $beforeUpdate = Get-MnHash (Join-Path $game 'lang\en.txt')
    $beforeUpdateJson = Get-MnHash (Join-Path $game 'data\sample.json')
    $beforeUpdateManifest = Get-MnHash (Join-Path $game '.barony-mongolian-backup\manifest.json')
    $manifest.files[1].originalSha256 = ('0' * 64)
    Write-MnJson (Join-Path $pkg 'package-manifest.json') $manifest
    Assert-Fails { Install-MnPackage $game $pkg } '*Original file does not match this release*'
    Assert-Equal (Get-MnHash (Join-Path $game 'lang\en.txt')) $beforeUpdate 'Wrong-baseline update preserved first file'
    Assert-Equal (Get-MnHash (Join-Path $game 'data\sample.json')) $beforeUpdateJson 'Wrong-baseline update preserved second file'
    Assert-Equal (Get-MnHash (Join-Path $game '.barony-mongolian-backup\manifest.json')) $beforeUpdateManifest 'Wrong-baseline update preserved backup manifest'
    $manifest.files[1].originalSha256 = $jsonHash
    Write-MnJson (Join-Path $pkg 'package-manifest.json') $manifest

    # Update changed payload and retire a previous file. Original English stays intact.
    [IO.File]::WriteAllText((Join-Path $pkg 'Barony-Mongolian\lang\en.txt'),'Mongolian version 2')
    $manifest.version = 'test-2'
    $manifest.files = @([pscustomobject]@{path='lang/en.txt';sha256=(Get-MnHash (Join-Path $pkg 'Barony-Mongolian\lang\en.txt'));originalSha256=$enHash})
    Write-MnJson (Join-Path $pkg 'package-manifest.json') $manifest
    Install-MnPackage $game $pkg
    Assert-Equal ([IO.File]::ReadAllText((Join-Path $game 'lang\en.txt'))) 'Mongolian version 2' 'Update installed new content'
    Assert-Equal (Get-MnHash (Join-Path $game 'data\sample.json')) $jsonHash 'Retired payload restored English'

    [IO.File]::WriteAllText((Join-Path $game 'lang\en.txt'),'Other mod edits')
    Assert-Fails { Uninstall-MnPackage $game } '*Game file changed after installation*'
    Assert-Fails { Install-MnPackage $game $pkg } '*Game file changed after installation*'
    Assert-Equal ([IO.File]::ReadAllText((Join-Path $game 'lang\en.txt'))) 'Other mod edits' 'Unknown changes preserved'
    [IO.File]::WriteAllText((Join-Path $game 'lang\en.txt'),'Mongolian version 2')
    $backupFile = Join-Path $game '.barony-mongolian-backup\originals\lang\en.txt'
    [IO.File]::AppendAllText($backupFile,'damage')
    Assert-Fails { Uninstall-MnPackage $game } '*English backup is missing or damaged*'
    [IO.File]::WriteAllText($backupFile,'English original')
    Uninstall-MnPackage $game
    Uninstall-MnPackage $game
    Assert-Equal (Get-MnHash (Join-Path $game 'lang\en.txt')) $enHash 'Uninstall restored English byte for byte'
    Assert-Equal (Get-MnHash (Join-Path $game 'savegames\save.json')) $saveHash 'Savegames untouched'
    Assert-Equal (Get-MnHash (Join-Path $game 'barony.exe')) $exeHash 'Game executable untouched'
    Install-MnPackage $game $pkg
    Assert-Equal ([IO.File]::ReadAllText((Join-Path $game 'lang\en.txt'))) 'Mongolian version 2' 'Reinstall after uninstall works'

    foreach ($rel in @('../outside.txt','lang/../../outside.txt','C:\outside.txt','lang/stream:payload','lang//bad.txt','lang/.. /outside.txt','lang/NUL.txt','lang/bad?.txt')) {
        Assert-Fails { Get-MnChildPath $game $rel } '*Unsafe relative path*'
    }
    Write-Output 'PASS: preflight integrity, wrong-version refusal, rollback, idempotence, update, retirement, tamper protection, uninstall/reinstall, saves/exe, path confinement.'
} finally {
    # Verify absolute scope before recursive deletion of only this generated fixture.
    $resolved = [IO.Path]::GetFullPath($testRoot)
    $expectedRoot = [IO.Path]::GetFullPath($PSScriptRoot).TrimEnd('\','/') + [IO.Path]::DirectorySeparatorChar
    if (-not $resolved.StartsWith($expectedRoot,[StringComparison]::OrdinalIgnoreCase) -or [IO.Path]::GetFileName($resolved) -notlike 'tmp-install-*') { throw 'Unsafe test cleanup target' }
    Remove-Item -LiteralPath $resolved -Recurse -Force
}
