param(
    [Parameter(Mandatory=$true, Position=0)]
    [ValidateSet('prepare','start','update','stop')][string]$Action,
    [string]$SchemaDigest,
    [string]$ContentDigest,
    [switch]$NonInteractive,
    [ValidateRange(1024,65535)][int]$PublicPort = 8131
)
$ErrorActionPreference = 'Stop'
$taskRoot = $PSScriptRoot
$taskLocal = Join-Path $taskRoot 'var/compose'
$taskProfilePath = Join-Path $taskLocal 'checkout.json'
$taskCompose = Join-Path $taskRoot 'deploy/compose.dev.yaml'

function Write-LocalJson($Path, $Value) {
    $json = $Value | ConvertTo-Json -Depth 12
    [IO.File]::WriteAllText($Path, $json + "`n", [Text.UTF8Encoding]::new($false))
}
function Get-ComposeFiles {
    $paths = @(& git -C $taskRoot rev-parse --path-format=absolute --show-toplevel --git-dir --git-common-dir)
    if ($LASTEXITCODE -ne 0 -or $paths.Count -ne 3) { throw 'Cannot resolve checkout Git metadata.' }
    $root, $gitDir, $commonDir = $paths | ForEach-Object { (Resolve-Path -LiteralPath $_).ProviderPath }
    if ($root -ne $taskRoot -or -not (Test-Path -LiteralPath $gitDir -PathType Container) -or
        -not (Test-Path -LiteralPath $commonDir -PathType Container)) { throw 'Git metadata does not belong to this checkout.' }
    '-f'
    $taskCompose
    if ($gitDir -eq $commonDir -and $gitDir -eq (Join-Path $root '.git')) { return }

    $worktrees = Join-Path $commonDir 'worktrees'
    if ((Split-Path $gitDir -Parent) -ne $worktrees) { throw 'Unsupported Git metadata layout.' }
    $backlink = (Get-Content -LiteralPath (Join-Path $gitDir 'gitdir') -Raw).Trim()
    $relativeCommon = (Get-Content -LiteralPath (Join-Path $gitDir 'commondir') -Raw).Trim()
    if ((Resolve-Path -LiteralPath $backlink).ProviderPath -ne (Join-Path $root '.git') -or
        $relativeCommon -ne '../..') { throw 'Linked worktree Git metadata does not match this checkout.' }
    $env:MATHSTART_DEV_GIT_COMMON = $commonDir
    $env:MATHSTART_DEV_GIT_DIR = '/git-common/worktrees/' + (Split-Path $gitDir -Leaf)
    '-f'
    Join-Path $taskRoot 'deploy/compose.dev.worktree.yaml'
}

function Invoke-Compose([string[]]$Arguments) {
    $stageTimer = [Diagnostics.Stopwatch]::StartNew()
    & docker compose --project-name $script:taskProfile.project --project-directory $taskRoot @taskComposeFiles @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Docker Compose failed (exit $LASTEXITCODE). State and data retained." }
    Write-Output ('TIMING compose {0}: {1:N3}s' -f ($Arguments -join ' '), $stageTimer.Elapsed.TotalSeconds)
}
function Get-ImageFingerprint {
    $paths = @('deploy/Dockerfile', '.dockerignore')
    $paths += & git -C $taskRoot ls-files -- backend specs
    if ($LASTEXITCODE -ne 0) { throw 'Git checkout required' }
    $sha = [Security.Cryptography.SHA256]::Create()
    $rows = foreach ($path in ($paths | Sort-Object -Unique)) {
        $raw = [IO.File]::ReadAllBytes((Join-Path $taskRoot $path))
        $hex = ([BitConverter]::ToString($sha.ComputeHash($raw))).Replace('-','').ToLowerInvariant()
        "$path $hex"
    }
    $result = ([BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes(($rows -join "`n"))))).Replace('-','').ToLowerInvariant()
    $sha.Dispose()
    return $result
}

try {
    Set-Location -LiteralPath $taskRoot
    if ($PublicPort -eq 8132) { throw 'Public port 8132 is reserved for internal FastAPI.' }
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { throw 'Install Docker Desktop with Linux engine and Compose.' }
    $taskComposeFiles = @(Get-ComposeFiles)
    if (-not (Test-Path -LiteralPath $taskProfilePath)) {
        if ($Action -ne 'prepare') { throw 'Run .\dev.cmd prepare first.' }
        if (Test-Path -LiteralPath $taskLocal) { throw 'Partial local setup exists. Inspect var/compose; configuration will not be replaced.' }
        New-Item -ItemType Directory -Path $taskLocal | Out-Null
        $taskId = [Guid]::NewGuid().ToString('N')
        $taskRandom = New-Object byte[] 36
        $taskRng = [Security.Cryptography.RandomNumberGenerator]::Create()
        $taskRng.GetBytes($taskRandom)
        $taskRng.Dispose()
        $taskPassword = [Convert]::ToBase64String($taskRandom).TrimEnd('=').Replace('+','-').Replace('/','_')
        [IO.File]::WriteAllText((Join-Path $taskLocal 'postgres.env'), "POSTGRES_USER=local_admin`nPOSTGRES_DB=mathstart_dev`nPOSTGRES_PASSWORD=$taskPassword`n", [Text.UTF8Encoding]::new($false))
        $taskPassword = $null
        Write-LocalJson $taskProfilePath @{version=1; owner=$taskRoot; project=('msdev-' + $taskId.Substring(0,12)); id=$taskId; public_port=$PublicPort}
    }
    $script:taskProfile = Get-Content -LiteralPath $taskProfilePath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($taskProfile.version -ne 1 -or $taskProfile.owner -ne $taskRoot -or $taskProfile.project -notmatch '^msdev-[a-f0-9]{12}$') {
        throw 'Local setup belongs to another checkout or has an unsupported format. Do not copy var/.'
    }
    $savedPort = 8131
    if ($taskProfile.PSObject.Properties['public_port']) {
        $savedPort = $taskProfile.public_port
        if (($savedPort -isnot [int] -and $savedPort -isnot [long]) -or $savedPort -lt 1024 -or $savedPort -gt 65535 -or $savedPort -eq 8132) {
            throw 'Invalid public port in checkout profile.'
        }
    }
    if ($PSBoundParameters.ContainsKey('PublicPort') -and $PublicPort -ne $savedPort) {
        throw "This checkout is bound to public port $savedPort. Omit -PublicPort or use the saved port."
    }
    $env:MATHSTART_DEV_PUBLIC_PORT = [string]$savedPort
    $env:MATHSTART_DEV_PROJECT = $taskProfile.project
    $env:MATHSTART_DEV_CHECKOUT = $taskRoot
    $taskImageRecord = Join-Path $taskLocal 'image.json'
    $taskFingerprint = if ($Action -ne 'stop') { Get-ImageFingerprint } else { '' }
    $taskImage = $null
    if (Test-Path -LiteralPath $taskImageRecord) { $taskImage = Get-Content -LiteralPath $taskImageRecord -Raw -Encoding UTF8 | ConvertFrom-Json }
    $env:MATHSTART_DEV_IMAGE = if ($taskImage) { $taskImage.image } elseif ($taskFingerprint.Length -ge 16) {
        $taskProfile.project + '-dev:' + $taskFingerprint.Substring(0,16)
    } else { $taskProfile.project + '-dev:unprepared' }
    if ($Action -eq 'stop') {
        Invoke-Compose @('stop')
        Write-Output 'Stopped this checkout only. Database, credentials and volumes retained.'
        exit 0
    }
    $taskEngineType = & docker info --format '{{.OSType}}'
    if ($LASTEXITCODE -ne 0 -or $taskEngineType -ne 'linux') { throw 'Start Docker Desktop Linux engine, then repeat the command.' }
    if ($Action -in @('prepare','update')) {
        Invoke-Compose @('stop','app')
        $taskImageExists = $false
        if ($taskImage) {
            & docker image inspect $taskImage.image --format '{{.Id}}' 2>$null | Out-Null
            $taskImageExists = $LASTEXITCODE -eq 0
        }
        if (-not $taskImage -or $taskImage.fingerprint -ne $taskFingerprint -or -not $taskImageExists) {
            $env:MATHSTART_DEV_IMAGE = $taskProfile.project + '-dev:' + $taskFingerprint.Substring(0,16)
            Invoke-Compose @('build','app')
            Write-LocalJson $taskImageRecord @{fingerprint=$taskFingerprint; image=$env:MATHSTART_DEV_IMAGE}
        } else { Write-Output 'Image inputs unchanged; build skipped.' }
        Invoke-Compose @('up','-d','--wait','--wait-timeout','90','db')
        while ($true) {
            $taskArgs = @('run','--rm','--no-deps','tools','prepare')
            if ($SchemaDigest) { $taskArgs += @('--schema-digest', $SchemaDigest) }
            if ($ContentDigest) { $taskArgs += @('--content-digest', $ContentDigest) }
            & docker compose --project-name $taskProfile.project --project-directory $taskRoot @taskComposeFiles @taskArgs
            $taskExit = $LASTEXITCODE
            if ($taskExit -eq 0) { break }
            if ($taskExit -ne 42) { throw "Preparation stopped (exit $taskExit). Inspect ignored var/compose/logs; do not blindly repeat an uncertain write." }
            $taskReview = Get-Content -LiteralPath (Join-Path $taskLocal 'review.json') -Raw -Encoding UTF8 | ConvertFrom-Json
            Write-Output ($taskReview | ConvertTo-Json -Depth 8)
            if ($NonInteractive) { Write-Output 'Review the concrete plan and repeat with -SchemaDigest or -ContentDigest. Nothing was implicitly approved.'; exit 42 }
            $taskApproval = Read-Host 'Review the saved plan, then enter its complete SHA256 (Enter to leave it pending)'
            if (-not $taskApproval) { exit 42 }
            if ($taskApproval -cne $taskReview.digest) { throw 'Digest does not match the pending plan; nothing approved.' }
            if ($taskReview.kind -eq 'schema') { $SchemaDigest = $taskApproval } else { $ContentDigest = $taskApproval }
        }
        Write-Output 'Prepared. Run .\dev.cmd start. No Git pull/reset/checkout was performed.'
    } else {
        if (-not $taskImage) { throw 'Run .\dev.cmd prepare first.' }
        if ($taskImage.fingerprint -ne $taskFingerprint) { throw 'Image inputs changed. Run .\dev.cmd update; start never rebuilds or migrates.' }
        $app = & docker compose --project-name $taskProfile.project --project-directory $taskRoot @taskComposeFiles ps --status running -q app
        if ($LASTEXITCODE -ne 0) { throw 'Could not check the current app container.' }
        if ($app) {
            $binding = & docker port $app "$savedPort/tcp"
            if ($LASTEXITCODE -ne 0 -or $binding -cne "127.0.0.1:${savedPort}") {
                throw 'Running app does not match the saved loopback port.'
            }
        } else {
            $listener = [Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback, $savedPort)
            try {
                $listener.ExclusiveAddressUse = $true
                $listener.Start()
            } catch [Net.Sockets.SocketException] {
                throw "Cannot bind 127.0.0.1:${savedPort}. Check the port owner before starting."
            } finally { $listener.Stop() }
        }
        Invoke-Compose @('up','-d','--wait','--wait-timeout','90','db')
        Invoke-Compose @('run','--rm','--no-deps','tools','ready')
        Invoke-Compose @('up','-d','--no-build','--wait','--wait-timeout','300','app')
        Write-Output "Dev: http://127.0.0.1:$savedPort ; logs: docker compose via this checkout configuration. Stop: .\dev.cmd stop"
    }
} catch {
    Write-Error $_.Exception.Message
    exit 1
}
