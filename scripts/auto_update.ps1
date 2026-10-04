param(
    [Parameter(Mandatory = $true)][string]$Config,
    [string]$Python = 'C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe',
    [switch]$Publish,
    [switch]$Scheduled
)
$ErrorActionPreference = 'Stop'
$ghprConfig = Get-Content -LiteralPath $Config -Raw | ConvertFrom-Json
$ghprRuntime = [System.IO.Path]::GetFullPath($ghprConfig.runtime_root)
if (-not $ghprRuntime.StartsWith('D:\', [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'GHPR runtime must be on D:'
}
$ghprTmp = Join-Path $ghprRuntime 'wrapper-tmp'
New-Item -ItemType Directory -Path $ghprTmp -Force | Out-Null
# Process-local only. Do not alter Windows global environment or other projects.
$env:TMP = $ghprTmp
$env:TEMP = $ghprTmp
$env:TMPDIR = $ghprTmp
$env:PYTHONUTF8 = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:GIT_TERMINAL_PROMPT = '0'
$env:GCM_INTERACTIVE = 'Never'
$ghprArgs = @('-B', (Join-Path $PSScriptRoot 'auto_update.py'), '--config', $Config)
if ($Publish) { $ghprArgs += '--publish' }
if ($Scheduled) { $ghprArgs += '--scheduled' }
& $Python @ghprArgs
exit $LASTEXITCODE
