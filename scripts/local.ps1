param([ValidateSet('start','stop','status','logs')][string]$Action = 'status')
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$settings = Join-Path $root 'var/local/compose.env'
if (-not (Test-Path -LiteralPath $settings)) { throw 'Prepare private var/local settings using docs/local-development.md first.' }
$command = Get-Command docker -ErrorAction SilentlyContinue
$docker = if ($command) { $command.Source } else { Join-Path $env:LOCALAPPDATA 'Programs/DockerDesktop/resources/bin/docker.exe' }
if (-not (Test-Path -LiteralPath $docker)) { throw 'Docker CLI is unavailable. Start/configure Docker explicitly; this script does not restart Desktop or WSL.' }
$compose = @('compose','--env-file',$settings,'-f',(Join-Path $root 'deploy/compose.yaml'))
switch ($Action) {
    'start' { & $docker @compose up -d --wait db api edge }
    'stop' { & $docker @compose stop }
    'status' { & $docker @compose ps --all }
    'logs' { & $docker @compose logs --tail 100 --follow api edge }
}
exit $LASTEXITCODE
