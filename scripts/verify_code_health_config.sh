#!/bin/bash
# 代码健康度检查任务验证脚本

echo "🔍 验证代码健康度检查任务配置"
echo "================================"

echo ""
echo "1. 检查飞书配置文件:"
if [ -f ~/.openclaw/feishu_config.json ]; then
    echo "   ✅ 配置文件存在"
    cat ~/.openclaw/feishu_config.json | python3 -m json.tool | head -20
else
    echo "   ❌ 配置文件不存在"
fi

echo ""
echo "2. 检查任务状态:"
openclaw cron list --all | grep -A5 -B5 "代码健康度检查"

echo ""
echo "3. 手动测试任务:"
echo "   openclaw cron run 17da0ef4-47a1-47c2-b925-365131db70a7"

echo ""
echo "4. 查看调度任务完整列表:"
echo "   openclaw cron list --all"

echo ""
echo "🎯 配置完成！任务将在明天15:00自动执行"
