#!/bin/bash
# 双仓库推送脚本

echo "🔄 开始向双仓库推送..."

# 推送到gitee
echo "📤 正在推送到gitee..."
git push gitee main

# 推送到github
echo "📤 正在推送到github..."
git push origin main

echo "✅ 双仓库推送完成！"