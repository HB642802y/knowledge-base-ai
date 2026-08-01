# Charge les variables depuis .env et lance Alembic
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

if (Test-Path "$root\.env") {
    Get-Content "$root\.env" | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith('#')) { return }
        $parts = $line -split('=',2)
        if ($parts.Length -eq 2) {
            $k = $parts[0].Trim()
            $v = $parts[1].Trim().Trim("'\"")
            Set-Item -Path env:$k -Value $v
         }
    }
}

Write-Host "Using DATABASE_URL =" $env:DATABASE_URL

alembic current
alembic upgrade head
