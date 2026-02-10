# 双仓库推送脚本 (PowerShell版本)

Write-Host "🔄 开始向双仓库推送..." -ForegroundColor Yellow

# 推送到gitee
Write-Host "📤 正在推送到gitee..." -ForegroundColor Cyan
git push gitee main

# 检查推送是否成功
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ gitee推送成功" -ForegroundColor Green
} else {
    Write-Host "❌ gitee推送失败" -ForegroundColor Red
    exit 1
}

# 推送到github
Write-Host "📤 正在推送到github..." -ForegroundColor Cyan
git push origin main

# 检查推送是否成功
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ github推送成功" -ForegroundColor Green
} else {
    Write-Host "❌ github推送失败" -ForegroundColor Red
    exit 1
}

Write-Host "🎉 双仓库推送全部完成！" -ForegroundColor Green