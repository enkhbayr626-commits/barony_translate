Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'

function Get-MnHash([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Get-MnChildPath([string]$Root, [string]$Relative) {
    if ([string]::IsNullOrWhiteSpace($Relative) -or [IO.Path]::IsPathRooted($Relative) -or $Relative.Contains(':')) {
        throw "Unsafe relative path: $Relative"
    }
    $parts = $Relative.Replace('\','/').Split('/')
    if (@($parts | Where-Object { $_ -eq '..' -or $_ -eq '.' -or $_ -eq '' }).Count -gt 0) {
        throw "Unsafe relative path: $Relative"
    }
    foreach ($part in $parts) {
        if ($part.TrimEnd(' ','.') -ne $part -or $part.IndexOfAny([IO.Path]::GetInvalidFileNameChars()) -ge 0 -or $part -match '^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(\..*)?$') {
            throw "Unsafe relative path: $Relative"
        }
    }
    $rootFull = [IO.Path]::GetFullPath($Root).TrimEnd('\','/')
    $full = [IO.Path]::GetFullPath((Join-Path $rootFull ($parts -join [IO.Path]::DirectorySeparatorChar)))
    if (-not $full.StartsWith($rootFull + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Path escapes its root: $Relative"
    }
    # Never follow a directory junction or file symlink while installing/restoring.
    $cursor = $full
    while ($cursor -and $cursor.Length -ge $rootFull.Length) {
        if (Test-Path -LiteralPath $cursor) {
            $item = Get-Item -LiteralPath $cursor -Force
            if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Symlink/junction is not supported: $cursor" }
        }
        if ($cursor -eq $rootFull) { break }
        $cursor = [IO.Path]::GetDirectoryName($cursor)
    }
    return $full
}

function Get-MnUniquePaths([string[]]$Paths) {
    # Steam stores the same path with different slash direction and casing in
    # HKCU, HKLM and its VDF. Select-Object -Unique is case-sensitive in PS 5.1.
    $seen = @{}
    foreach ($path in $Paths) {
        if ([string]::IsNullOrWhiteSpace($path)) { continue }
        $normalized = [IO.Path]::GetFullPath($path.Replace('/','\')).TrimEnd('\','/')
        if (-not $seen.ContainsKey($normalized)) {
            $seen[$normalized] = $true
            Write-Output $normalized
        }
    }
}

function Get-MnSteamGameCandidates([string[]]$SteamRoots) {
    $roots = @(Get-MnUniquePaths $SteamRoots)
    $libraries = @($roots)
    foreach ($steamRoot in $roots) {
        $vdf = Join-Path $steamRoot 'steamapps\libraryfolders.vdf'
        if (Test-Path -LiteralPath $vdf) {
            try {
                $content = [IO.File]::ReadAllText($vdf)
                foreach ($match in [regex]::Matches($content, '"path"\s+"([^"]+)"')) {
                    $libraries += $match.Groups[1].Value.Replace('\\','\')
                }
            } catch {
                # An inaccessible library registry does not invalidate a known
                # install in the main Steam directory or another readable VDF.
            }
        }
    }
    $candidates = @()
    foreach ($library in @(Get-MnUniquePaths $libraries)) {
        $candidate = Join-Path $library 'steamapps\common\Barony'
        if (Test-Path -LiteralPath (Join-Path $candidate 'barony.exe') -PathType Leaf) {
            $candidates += (Resolve-Path -LiteralPath $candidate).Path
        }
    }
    Get-MnUniquePaths $candidates
}

function Get-MnGamePath([string]$GamePath) {
    if ($GamePath) {
        $resolved = (Resolve-Path -LiteralPath $GamePath).Path
        if (-not (Test-Path -LiteralPath (Join-Path $resolved 'barony.exe') -PathType Leaf)) {
            throw "barony.exe was not found in: $resolved"
        }
        return $resolved.TrimEnd('\','/')
    }
    $steamRoots = @()
    foreach ($key in @('HKCU:\Software\Valve\Steam','HKLM:\SOFTWARE\WOW6432Node\Valve\Steam')) {
        try {
            if (Test-Path $key) {
                $reg = Get-ItemProperty $key
                foreach ($field in @('SteamPath','InstallPath')) {
                    if ($reg.PSObject.Properties.Name -contains $field) { $steamRoots += $reg.$field }
                }
            }
        } catch {
            # Registry access can be denied in restricted shells. Continue with
            # the other registry view and the usual Steam installation path.
        }
    }
    if (${env:ProgramFiles(x86)}) { $steamRoots += Join-Path ${env:ProgramFiles(x86)} 'Steam' }
    $candidates = @(Get-MnSteamGameCandidates $steamRoots)
    if ($candidates.Count -ne 1) { throw 'Cannot choose a unique Barony installation. Pass -GamePath "D:\SteamLibrary\steamapps\common\Barony".' }
    return $candidates[0].TrimEnd('\','/')
}

function Assert-MnGameClosed([string]$GamePath) {
    foreach ($process in @(Get-Process -Name barony -ErrorAction SilentlyContinue)) {
        if (-not $process.Path -or $process.Path.StartsWith($GamePath + '\', [StringComparison]::OrdinalIgnoreCase)) {
            throw 'Close Barony before installing or uninstalling Mongolian.'
        }
    }
}

function Write-MnJson([string]$Path, $Value) {
    $json = $Value | ConvertTo-Json -Depth 20
    [IO.File]::WriteAllText($Path + '.tmp', $json, (New-Object Text.UTF8Encoding($false)))
    Move-Item -LiteralPath ($Path + '.tmp') -Destination $Path -Force
}

function Read-MnState([string]$BackupRoot, [string]$GamePath) {
    $manifestPath = Get-MnChildPath $BackupRoot 'manifest.json'
    if (-not (Test-Path -LiteralPath $manifestPath)) {
        if (Test-Path -LiteralPath $BackupRoot) { throw "Backup folder exists without a manifest: $BackupRoot. Keep it safe and inspect it before continuing." }
        return $null
    }
    $state = [IO.File]::ReadAllText($manifestPath) | ConvertFrom-Json
    if ($state.schemaVersion -ne 1 -or $state.gamePath -ne $GamePath) { throw 'Backup manifest belongs to a different game installation or format.' }
    $seen = @{}
    foreach ($entry in $state.files) {
        if ($seen.ContainsKey($entry.path)) { throw 'Duplicate backup manifest path.' }
        $seen[$entry.path] = $true
        $null = Get-MnChildPath $GamePath $entry.path
        $backup = Get-MnChildPath $BackupRoot ('originals/' + $entry.path)
        if (-not (Test-Path -LiteralPath $backup -PathType Leaf) -or (Get-MnHash $backup) -ne $entry.originalSha256) {
            throw "English backup is missing or damaged: $($entry.path)"
        }
    }
    return $state
}

function Assert-MnCurrentFiles($State, [string]$GamePath) {
    foreach ($entry in $State.files) {
        $current = Get-MnChildPath $GamePath $entry.path
        $accepted = @($entry.originalSha256, $entry.installedSha256)
        if ($entry.PSObject.Properties.Name -contains 'previousSha256') { $accepted += $entry.previousSha256 }
        if (-not (Test-Path -LiteralPath $current -PathType Leaf) -or $accepted -notcontains (Get-MnHash $current)) {
            throw "Game file changed after installation: $($entry.path). Nothing was overwritten; inspect the Steam update or other mod first."
        }
    }
}

function Install-MnPackage([string]$GamePath, [string]$PackageRoot) {
    $GamePath = Get-MnGamePath $GamePath
    Assert-MnGameClosed $GamePath
    $payloadRoot = Join-Path $PackageRoot 'Barony-Mongolian'
    $packageFile = Join-Path $PackageRoot 'package-manifest.json'
    if (-not (Test-Path -LiteralPath $packageFile -PathType Leaf)) { throw 'package-manifest.json is missing. Download and extract the complete release ZIP.' }
    $package = [IO.File]::ReadAllText($packageFile) | ConvertFrom-Json
    if ($package.schemaVersion -ne 1 -or @($package.files).Count -eq 0) { throw 'Unsupported or empty package manifest.' }
    $backupRoot = Get-MnChildPath $GamePath '.barony-mongolian-backup'
    $state = Read-MnState $backupRoot $GamePath
    if ($state) { Assert-MnCurrentFiles $state $GamePath }
    $old = @{}
    if ($state) { foreach ($entry in $state.files) { $old[$entry.path] = $entry } }
    $seen = @{}
    $records = @()
    # Validate the entire payload, destinations and originals before a single game write.
    foreach ($file in $package.files) {
        $rel = [string]$file.path
        if ($seen.ContainsKey($rel)) { throw "Duplicate package path: $rel" }
        $seen[$rel] = $true
        if ($rel -notmatch '^(lang|fonts|data|items|books|themes)/.+\.(json|txt|ttf)$') { throw "Unsupported payload path: $rel" }
        $source = Get-MnChildPath $payloadRoot $rel
        $target = Get-MnChildPath $GamePath $rel
        if (-not (Test-Path -LiteralPath $source -PathType Leaf) -or (Get-MnHash $source) -ne $file.sha256) { throw "Payload checksum failed: $rel" }
        if (-not (Test-Path -LiteralPath $target -PathType Leaf)) { throw "Expected original game file missing: $rel" }
        $currentHash = Get-MnHash $target
        $originalHash = $currentHash
        if ($old.ContainsKey($rel)) {
            $originalHash = $old[$rel].originalSha256
            if (($file.PSObject.Properties.Name -contains 'originalSha256') -and $file.originalSha256 -and $originalHash -ne $file.originalSha256) {
                throw "Original file does not match this release: $rel. The new package requires a different Barony baseline; the existing installation was not changed."
            }
        } elseif (($file.PSObject.Properties.Name -contains 'originalSha256') -and $file.originalSha256 -and $currentHash -ne $file.originalSha256) {
            throw "Original file does not match this release: $rel. Use a clean supported Barony installation or the existing English backup."
        }
        $records += [pscustomobject]@{path=$rel;originalSha256=$originalHash;installedSha256=[string]$file.sha256;previousSha256=$currentHash}
    }
    # Retired payload files return to English; retain their verified originals.
    foreach ($entry in $old.Values) {
        if (-not $seen.ContainsKey($entry.path)) {
            $records += [pscustomobject]@{path=$entry.path;originalSha256=$entry.originalSha256;installedSha256=$entry.originalSha256;previousSha256=(Get-MnHash (Get-MnChildPath $GamePath $entry.path))}
        }
    }
    $manifestPath = Get-MnChildPath $backupRoot 'manifest.json'
    $null = New-Item -ItemType Directory -Path $backupRoot -Force
    foreach ($entry in $records) {
        $backup = Get-MnChildPath $backupRoot ('originals/' + $entry.path)
        if (-not (Test-Path -LiteralPath $backup)) {
            $null = New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($backup)) -Force
            Copy-Item -LiteralPath (Get-MnChildPath $GamePath $entry.path) -Destination $backup
        }
        if ((Get-MnHash $backup) -ne $entry.originalSha256) { throw "Backup verification failed: $($entry.path)" }
    }
    $journal = [pscustomobject]@{schemaVersion=1;gamePath=$GamePath;state='installing';packageVersion=$package.version;files=@($records)}
    Write-MnJson $manifestPath $journal
    $rollbackRoot = Get-MnChildPath $backupRoot ('transaction-' + [guid]::NewGuid().ToString('N'))
    # Snapshot the exact current state so a failed update restores the previous version.
    foreach ($entry in $records) {
        $rollback = Get-MnChildPath $rollbackRoot $entry.path
        $null = New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($rollback)) -Force
        Copy-Item -LiteralPath (Get-MnChildPath $GamePath $entry.path) -Destination $rollback
    }
    try {
        foreach ($entry in $records) {
            $from = if ($seen.ContainsKey($entry.path)) { Get-MnChildPath $payloadRoot $entry.path } else { Get-MnChildPath $backupRoot ('originals/' + $entry.path) }
            $to = Get-MnChildPath $GamePath $entry.path
            Copy-Item -LiteralPath $from -Destination $to -Force
            if ((Get-MnHash $to) -ne $entry.installedSha256) { throw "Installed checksum failed: $($entry.path)" }
        }
        $journal.state = 'active'
        $journal.files = @($records | Select-Object path,originalSha256,installedSha256)
        Write-MnJson $manifestPath $journal
    } catch {
        $failure = $_
        foreach ($entry in $records) {
            Copy-Item -LiteralPath (Get-MnChildPath $rollbackRoot $entry.path) -Destination (Get-MnChildPath $GamePath $entry.path) -Force
        }
        if ($state) { Write-MnJson $manifestPath $state } else {
            $journal.state = 'restored'
            $journal.files = @($records | ForEach-Object { [pscustomobject]@{path=$_.path;originalSha256=$_.originalSha256;installedSha256=$_.originalSha256} })
            Write-MnJson $manifestPath $journal
        }
        throw $failure
    } finally {
        # Delete only individually verified transaction files, then empty directories.
        foreach ($entry in $records) {
            $rollback = Get-MnChildPath $rollbackRoot $entry.path
            if (Test-Path -LiteralPath $rollback -PathType Leaf) { Remove-Item -LiteralPath $rollback -Force }
        }
        Get-ChildItem -LiteralPath $rollbackRoot -Directory -Recurse | Sort-Object { $_.FullName.Length } -Descending | ForEach-Object {
            if (@(Get-ChildItem -LiteralPath $_.FullName -Force).Count -eq 0) { Remove-Item -LiteralPath $_.FullName -Force }
        }
        if (@(Get-ChildItem -LiteralPath $rollbackRoot -Force).Count -eq 0) { Remove-Item -LiteralPath $rollbackRoot -Force }
    }
    Write-Output "Mongolian installed ($($records.Count) files). Start Barony normally from Steam."
    Write-Output "English backup: $backupRoot"
}

function Uninstall-MnPackage([string]$GamePath) {
    $GamePath = Get-MnGamePath $GamePath
    Assert-MnGameClosed $GamePath
    $backupRoot = Get-MnChildPath $GamePath '.barony-mongolian-backup'
    $state = Read-MnState $backupRoot $GamePath
    if (-not $state) { throw 'No installer backup found. Do not remove game files manually; restore using your original installation method.' }
    Assert-MnCurrentFiles $state $GamePath
    foreach ($entry in $state.files) {
        $from = Get-MnChildPath $backupRoot ('originals/' + $entry.path)
        $to = Get-MnChildPath $GamePath $entry.path
        Copy-Item -LiteralPath $from -Destination $to -Force
        if ((Get-MnHash $to) -ne $entry.originalSha256) { throw "English restore checksum failed: $($entry.path)" }
    }
    $state.state = 'restored'
    Write-MnJson (Get-MnChildPath $backupRoot 'manifest.json') $state
    Write-Output 'English restored. Game saves were not changed. Verified backups are retained for safe reinstallation.'
}
