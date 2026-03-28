#!/bin/bash
# 启动A股持仓股票财报监控系统

echo "🚀 启动A股持仓股票财报监控系统"
echo "📅 日期: $(date '+%Y-%m-%d %H:%M:%S')"
echo "📊 监控股票: 7只持仓股票"
echo "🎯 重点关注: 比亚迪2025年年报"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到python3，请先安装Python"
    exit 1
fi

# 检查依赖
echo "🔍 检查Python依赖..."
python3 -c "import requests, pandas, logging, json, os" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  缺少部分依赖，尝试安装..."
    pip3 install requests pandas --quiet
fi

# 创建必要目录
mkdir -p data/financial_reports logs

# 启动监控
echo "📈 开始监控财报发布情况..."
echo "持仓股票列表:"
echo "1. 603728 鸣志电器"
echo "2. 002594 比亚迪 ⭐ (重点关注: 2025年年报预计3月27日发布)"
echo "3. 600580 卧龙电驱"
echo "4. 600183 生益科技"
echo "5. 603259 药明康德"
echo "6. 002352 顺丰控股"
echo "7. 600096 云天化"
echo ""
echo "📝 监控日志将保存到: logs/financial_report.log"
echo "📊 监控数据将保存到: data/financial_reports/"
echo ""
echo "比亚迪2025年年报关注要点:"
echo "1. 营收增长是否超预期"
echo "2. 净利润和毛利率变化"
echo "3. 海外业务增长情况"
echo "4. 研发投入和技术进展"
echo "5. 现金流和财务状况"
echo ""
echo "按 Ctrl+C 停止监控"

# 运行Python监控脚本
cd /Users/ago/.openclaw/workspace
python3 scripts/financial_report_monitor.py