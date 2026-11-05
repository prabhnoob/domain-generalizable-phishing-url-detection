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

foreach ($model in @('lexical', 'char')) {
    $output = Join-Path $repoRoot "output\quickstart\$model"
    & $python -m phishing_url_detection evaluate `
        --data (Join-Path $repoRoot 'data\sample\urls.csv') `
        --model $model `
        --split domain `
        --test-size 0.25 `
        --seed 474 `
        --output $output | Out-Null
    Write-Output "== ${model}: output\quickstart\$model\metrics.json"
    Get-Content -Raw (Join-Path $output 'metrics.json')
}

Write-Output '== Running example from the report (character model)'
& $python -m phishing_url_detection predict `
    --model-dir (Join-Path $repoRoot 'output\quickstart\char') `
    --url 'https://paypal.login-fraud.top/verify'
