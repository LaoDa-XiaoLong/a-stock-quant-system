#!/bin/bash
# 启动A股持仓盯盘系统

echo "🚀 启动A股持仓盯盘系统"
echo "📅 日期: $(date '+%Y-%m-%d %H:%M:%S')"
echo "📊 监控频率: 每3分钟一次"
echo "⏰ A股交易时间: 9:30-11:30, 13:00-15:00"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到python3，请先安装Python"
    exit 1
fi

# 检查依赖
echo "🔍 检查Python依赖..."
python3 -c "import akshare, pandas, logging" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  缺少部分依赖，尝试安装..."
    pip3 install akshare pandas --quiet
fi

# 创建必要目录
mkdir -p data/monitor logs

# 启动监控
echo "📈 开始监控持仓股票..."
echo "持仓股票列表:"
echo "1. 603728 鸣志电器 (成本: 68元)"
echo "2. 002594 比亚迪 (成本: 待确认)"
echo "3. 600580 卧龙电驱 (成本: 待确认)"
echo "4. 600183 生益科技 (成本: 待确认)"
echo "5. 603259 药明康德 (成本: 待确认)"
echo "6. 002352 顺丰控股 (成本: 待确认)"
echo "7. 600096 云天化 (成本: 待确认)"
echo ""
echo "📝 监控日志将保存到: logs/stock_monitor.log"
echo "📊 监控数据将保存到: data/monitor/"
echo ""
echo "按 Ctrl+C 停止监控"

# 运行Python监控脚本
cd /Users/ago/.openclaw/workspace
python3 scripts/stock_monitor.py