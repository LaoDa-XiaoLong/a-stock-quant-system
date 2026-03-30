#!/bin/bash
# 工作群通知启动脚本
# 自动启动定时任务

echo "🚀 启动工作群通知服务"
echo "=========================="

# 设置环境变量
export WORKSPACE="/Users/ago/.openclaw/workspace"
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

# 检查Python环境
python3 --version

# 启动健康检查报告发送（立即测试）
echo "📊 测试系统健康检查报告发送..."
cd "$WORKSPACE" && python3 scripts/send_health_check_to_group.py

# 启动GitHub同步状态发送（立即测试）
echo "🔄 测试GitHub同步状态发送..."
cd "$WORKSPACE" && python3 scripts/send_github_sync_status.py

echo "✅ 工作群通知服务启动完成"
echo "定时任务配置:"
echo "  1. 系统健康检查报告发送: 每天10:00"
echo "  2. GitHub同步状态发送: 每天12:10"
