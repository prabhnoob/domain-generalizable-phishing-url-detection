$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repoRoot '.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $python)) {
    py -3.12 -m venv (Join-Path $repoRoot '.venv')
}

& $python -m pip install --upgrade pip
& $python -m pip install -r (Join-Path $repoRoot 'requirements.txt')
& $python -m pip install -e $repoRoot
& $python -m pytest (Join-Path $repoRoot 'tests')
& $python -m phishing_url_detection evaluate `
    --data (Join-Path $repoRoot 'data\sample\urls.csv') `
    --model lexical `
    --split random `
    --test-size 0.25 `
    --seed 474 `
    --output (Join-Path $repoRoot 'output\quickstart')

Get-Content -Raw (Join-Path $repoRoot 'output\quickstart\metrics.json')
