#!/bin/bash
# 启动最终版A股财报监控系统

echo "🚀 启动最终版A股财报监控系统"
echo "📅 日期: $(date '+%Y-%m-%d %H:%M:%S')"
echo "🎯 基于老大要求的调整:"
echo "   1. 超预期阈值: 20% (从30%下调)"
echo "   2. 持仓股票优先分析"
echo "   3. 及时提供交易建议"
echo "   4. 307只股票去重监控"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到python3，请先安装Python"
    exit 1
fi

# 检查依赖
echo "🔍 检查Python依赖..."
python3 -c "import requests, pandas, sqlite3, logging, json, os" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  缺少部分依赖，尝试安装..."
    pip3 install requests pandas --quiet
fi

# 创建目录
mkdir -p data/final_financial logs

# 显示监控配置
echo ""
echo "📋 监控配置详情:"
echo "   超预期阈值: 20% (不足或超出预期20%即触发)"
echo "   高警报阈值: 50%"
echo "   监控范围: 沪深300成分股 + 7只持仓股票 (去重)"
echo "   优先级: 持仓股票优先分析"
echo "   报告时间: 每天22点前完成"

# 持仓股票信息
echo ""
echo "⭐ 你的持仓股票 (优先监控):"
echo "   1. 鸣志电器(603728) - 成本68元 - 优先级: 最高"
echo "   2. 比亚迪(002594)   - 成本99元 - 优先级: 最高"
echo "   3. 卧龙电驱(600580) - 成本42元 - 优先级: 高"
echo "   4. 生益科技(600183) - 成本66元 - 优先级: 高"
echo "   5. 药明康德(603259) - 成本101元 - 优先级: 高"
echo "   6. 顺丰控股(002352) - 成本40元 - 优先级: 中"
echo "   7. 云天化(600096)   - 成本37元 - 优先级: 中"

# 重点关注行业
echo ""
echo "🎯 重点关注行业:"
echo "   新能源汽车、医药、半导体、白酒、银行、券商、化工、物流"

# 启动监控
echo ""
echo "🚀 开始每日监控..."
echo "📝 日志文件: logs/final_financial_monitor.log"
echo "📊 数据目录: data/final_financial/"
echo "📄 报告文件: data/final_financial/daily_report_$(date +%Y-%m-%d).txt"
echo "💾 数据库: data/final_financial/final_reports.db"

cd /Users/ago/.openclaw/workspace
python3 scripts/final_financial_monitor.py

echo ""
echo "✅ 监控完成!"
echo "📅 建议设置定时任务: 每天21:30自动运行此脚本"