#!/bin/bash
# 每日财报监控调度脚本
# 建议设置为每天21:30运行，22:00前完成

echo "📅 每日A股财报监控调度"
echo "⏰ 运行时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "🎯 目标: 22点前完成监控并生成报告"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到python3，请先安装Python"
    exit 1
fi

# 检查akshare
echo "🔍 检查akshare..."
python3 -c "import akshare" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  akshare未安装，尝试安装..."
    pip3 install akshare --quiet
fi

# 创建目录
mkdir -p data/daily_financial logs

# 显示监控配置
echo ""
echo "📋 今日监控配置:"
echo "   监控范围: 沪深300成分股 + 7只持仓股票"
echo "   超预期阈值: 30%"
echo "   重点关注行业:"
echo "     - 新能源汽车"
echo "     - 医药"
echo "     - 半导体"
echo "     - 白酒"
echo "     - 银行"

# 特别关注
echo ""
echo "⭐ 特别关注股票:"
echo "   1. 比亚迪(002594) - 2025年年报已发布"
echo "   2. 药明康德(603259) - 医药龙头"
echo "   3. 鸣志电器(603728) - 持仓股票"

# 运行监控
echo ""
echo "🚀 开始每日财报监控..."
echo "📝 日志: logs/daily_financial_monitor.log"
echo "📊 数据: data/daily_financial/"
echo "📄 报告: data/daily_financial/daily_report_$(date +%Y%m%d).txt"

cd /Users/ago/.openclaw/workspace
python3 scripts/daily_financial_monitor.py

echo ""
echo "✅ 每日监控完成!"
echo "📅 下次运行: 明天21:30"