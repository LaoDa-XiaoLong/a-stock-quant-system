#!/usr/bin/env bash

# 启动实时价格尾盘选股策略系统

echo "=================================================="
echo "🚀 启动实时价格尾盘选股策略系统"
echo "=================================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

# 检查依赖
echo "🔍 检查Python依赖..."
python3 -c "import requests, schedule" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 安装Python依赖..."
    pip3 install requests schedule --quiet
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
    echo "✅ 依赖安装完成"
fi

# 切换到工作目录
cd /Users/ago/.openclaw/workspace

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p data/tail_end_selection
mkdir -p reports
mkdir -p logs

# 更新尾盘选股法Skill配置
echo "🔧 更新尾盘选股法Skill配置..."
cat > skills/tail_end_selection/config.json << 'EOF'
{
  "skill_name": "尾盘选股法",
  "version": "1.0",
  "use_real_prices": true,
  "price_source": "sina_finance",
  "max_position_percent": 0.1,
  "stop_loss_percent": 0.05,
  "take_profit_percent": 0.08,
  "selection_time_window": "14:30-15:00",
  "monitoring_interval": 180,
  "report_time": "18:00",
  "last_updated": "$(date '+%Y-%m-%d %H:%M:%S')"
}
EOF

echo "✅ 尾盘选股法Skill配置已更新"

# 启动实时策略系统
echo "🚀 启动实时策略系统..."
echo "📋 系统日志将输出到终端"
echo "💡 按 Ctrl+C 停止系统"
echo "=================================================="

# 运行Python脚本
python3 scripts/real_time_tail_end_strategy.py