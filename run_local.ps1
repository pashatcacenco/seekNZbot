$ErrorActionPreference = 'Stop'
$repoDir = $PSScriptRoot
Set-Location $repoDir

$logFile = Join-Path $repoDir 'run_local.log'
function Log($msg) {
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $msg"
    Write-Output $line
    Add-Content -Path $logFile -Value $line
}

try {
    Log "=== run_local.ps1 starting ==="

    git pull --quiet 2>&1 | ForEach-Object { Log "git pull: $_" }

    $env:RUN_SOURCE = 'local'
    & 'C:\Python313\python.exe' main.py 2>&1 | ForEach-Object { Log $_ }

    git add data/seen_jobs.json data/last_run.json 2>&1 | Out-Null

    git diff --cached --quiet
    if ($LASTEXITCODE -ne 0) {
        git commit -m "Update job state [skip ci] (local)" --quiet
        git push --quiet
        Log "Pushed updated state to GitHub."
    } else {
        Log "No state changes to commit."
    }

    Log "=== run_local.ps1 finished ==="
}
catch {
    Log "ERROR: $_"
}
