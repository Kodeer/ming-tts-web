# Creates a PRIVATE GitHub repo and pushes the current project.
# Usage:  copy your PAT to the clipboard, then run:
#   powershell -ExecutionPolicy Bypass -File _push.ps1
# The token is read from the clipboard (so no interactive typing needed).

$ErrorActionPreference = "Stop"
$repoName = "ming-tts-web"
$repoDesc = "Web UI for Ming-3.0-tts (local GPU TTS) with voice cloning"
$remoteUrl = "https://github.com/Kodeer/$repoName.git"

Write-Host "Reading PAT from clipboard..." -ForegroundColor Cyan
try {
    $token = Get-Clipboard -Raw
} catch {
    $token = (Get-Clipboard)
}
$token = ($token -split "`n" | Select-Object -First 1).Trim()
if (-not $token) {
    Write-Host "Clipboard is empty. Copy your GitHub PAT first, then re-run." -ForegroundColor Red
    exit 1
}
Write-Host "Token read from clipboard (length $($token.Length))." -ForegroundColor Green

$base64 = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("Kodeer:$token"))
$headers = @{ Authorization = "Basic $base64"; "User-Agent" = "git-push-script" }
$body = @{ name = $repoName; description = $repoDesc; private = $true; auto_init = $false } | ConvertTo-Json

Write-Host "Creating private repo '$repoName' ..." -ForegroundColor Cyan
try {
    $resp = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method Post -Headers $headers -Body $body -ContentType "application/json"
    Write-Host "Repo created: $($resp.html_url)" -ForegroundColor Green
} catch {
    $msg = $_.ErrorDetails.Message
    if ($msg -match 'already exists') {
        Write-Host "Repo already exists; continuing to push." -ForegroundColor Yellow
    } else {
        Write-Host "Failed to create repo: $msg" -ForegroundColor Red
        exit 1
    }
}

Set-Location d:\AI\TTS

if (-not (Test-Path .git)) { git init; git branch -M main }
$existing = $null
try { $existing = git remote get-url origin 2>$null } catch { }
if ($existing) { git remote set-url origin "https://Kodeer:$token@github.com/Kodeer/$repoName.git" }
else { git remote add origin "https://Kodeer:$token@github.com/Kodeer/$repoName.git" }

git add -A
git commit -q -m "Initial commit: Ming-3.0-tts web UI with GPU inference and voice cloning" 2>&1 | Out-Null
git push -u origin main

# Scrub the token from the stored remote URL.
git remote set-url origin $remoteUrl
Write-Host "Pushed to $remoteUrl" -ForegroundColor Green
