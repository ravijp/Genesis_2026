# Get a working AWS session, then prove it works. Run this first, every session.
#
#   pwsh -File tools/aws-login.ps1          # login only if needed
#   pwsh -File tools/aws-login.ps1 -Force   # always re-login (picks up new IAM grants)
#   pwsh -File tools/aws-login.ps1 -Check   # run the full permission probe afterwards
#
# Why this script exists rather than "just run aws sso login":
#   * The CLI is not on PATH in shells opened before it was installed, so it resolves the
#     absolute path as a fallback.
#   * A token can be present but expired, and the failure ("Token has expired and refresh
#     failed") arrives later from an unrelated command. This checks up front.
#   * Re-login is also how you pick up a permission-set change: SSO bakes grants into the role
#     session, so a new IAM policy does nothing until the session is reissued. That is why
#     -Force exists and why it is the fix when IT says "done" but you still see AccessDenied.

param(
    [switch]$Force,   # re-login even if the current token is valid
    [switch]$Check,   # run tools/aws_probe.py after logging in
    [string]$Profile = 'genesis'
)

$ErrorActionPreference = 'Stop'

function Get-AwsCli {
    $onPath = Get-Command aws -ErrorAction SilentlyContinue
    if ($onPath) { return $onPath.Source }
    foreach ($p in @(
        "$env:ProgramFiles\Amazon\AWSCLIV2\aws.exe",
        "${env:ProgramFiles(x86)}\Amazon\AWSCLIV2\aws.exe",
        "$env:LOCALAPPDATA\Programs\AWSCLIV2\aws.exe"
    )) { if (Test-Path $p) { return $p } }
    throw "AWS CLI v2 not found. Install it, then re-run. Note v1 has no 'sso login'."
}

$aws = Get-AwsCli
$version = (& $aws --version 2>&1) -join ' '
Write-Host "CLI      $version"
if ($version -notmatch 'aws-cli/2\.') {
    throw "Need AWS CLI v2. Found: $version. v1 cannot do SSO login."
}

# A static key in the environment outranks the SSO profile in the credential chain, silently.
# Catch it here rather than three commands later when the token expires.
foreach ($v in 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN') {
    if (Test-Path "Env:$v") {
        Write-Warning "$v is set and OUTRANKS the '$Profile' profile. Clearing it for this session."
        Remove-Item "Env:$v"
    }
}

$env:AWS_PROFILE = $Profile

function Test-Session {
    try {
        $out = & $aws sts get-caller-identity --profile $Profile --output json 2>&1 | Out-String
        if ($LASTEXITCODE -ne 0 -or $out -notmatch '"Arn"') { return $null }
        return ($out | ConvertFrom-Json)
    } catch { return $null }
}

$who = if ($Force) { $null } else { Test-Session }

if ($null -eq $who) {
    if ($Force) { Write-Host "`n-Force given, re-logging in to pick up any new IAM grants..." }
    else        { Write-Host "`nNo valid session. Logging in..." }
    Write-Host "A browser will open. Approve the request there.`n"

    & $aws sso login --profile $Profile
    if ($LASTEXITCODE -ne 0) { throw "sso login failed. Check sso_start_url in ~/.aws/config." }

    $who = Test-Session
    if ($null -eq $who) { throw "Logged in, but credentials still do not resolve. Check the profile's sso_account_id / sso_role_name." }
}

Write-Host ""
Write-Host "Account  $($who.Account)"
Write-Host "Identity $($who.Arn)"
if ($who.Arn -notmatch 'assumed-role/AWSReservedSSO') {
    Write-Warning "Not an SSO role session. A static credential may still be winning."
}

# Region is a common silent misconfiguration: the console opens on ap-southeast-2 while every
# model ARN and price in our design is us-east-1.
$region = (& $aws configure get region --profile $Profile 2>&1 | Out-String).Trim()
Write-Host "Region   $region"
if ($region -ne 'us-east-1') { Write-Warning "Expected us-east-1. Model ARNs and published costs assume it." }

Write-Host "`nReady. AWS_PROFILE=$Profile is set for this shell."

if ($Check) {
    Write-Host "`nRunning the permission probe...`n"
    & uv run --with boto3 python tools/aws_probe.py
} else {
    Write-Host "Next: pwsh -File tools/aws-login.ps1 -Check   (verifies every permission the build needs)"
}
