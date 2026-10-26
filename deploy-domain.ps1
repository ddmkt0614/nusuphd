# 누수박사 nusuphd.com 연결 배포. 새 계정에 도메인을 추가하고 Active 가 된 뒤 실행.
# 누수박사는 별도 Cloudflare 계정에 올린다. 다른 사이트 토큰(CLOUDFLARE_API_TOKEN)은 건드리지 않고 아래 전용 변수만 읽는다.
$token = [Environment]::GetEnvironmentVariable('NUSUPHD_CF_API_TOKEN', 'User')
$account = [Environment]::GetEnvironmentVariable('NUSUPHD_CF_ACCOUNT_ID', 'User')
if ([string]::IsNullOrWhiteSpace($token)) { throw 'NUSUPHD_CF_API_TOKEN was not found in the Windows user environment.' }
if ([string]::IsNullOrWhiteSpace($account)) { throw 'NUSUPHD_CF_ACCOUNT_ID was not found in the Windows user environment.' }
$env:CLOUDFLARE_API_TOKEN = $token
$env:CLOUDFLARE_ACCOUNT_ID = $account
$env:NODE_USE_SYSTEM_CA = '1'
Set-Location $PSScriptRoot
npx --yes wrangler deploy --env production
if ($LASTEXITCODE -ne 0) { throw "Cloudflare deployment failed. Exit code: $LASTEXITCODE" }
Write-Host 'Deployment completed: https://nusuphd.com' -ForegroundColor Green
