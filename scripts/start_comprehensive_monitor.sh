#!/bin/bash
# 启动全面分析版A股财报监控系统

echo "🚀 启动全面分析版A股财报监控系统"
echo "📅 日期: $(date '+%Y-%m-%d %H:%M:%S')"
echo "🎯 分析特性:"
echo "   1. 超预期阈值: 20%"
echo "   2. 全面财务指标分析"
echo "   3. 持仓股票优先深度分析"
echo "   4. 自动飞书推送"
echo "   5. 报告包含财报类型和发布日期"

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

# 显示分析维度
echo ""
echo "📊 全面分析维度:"
echo "   1. 营收分析: 增长率 vs 预期"
echo "   2. 利润分析: 净利润增长率 vs 预期"
echo "   3. 利润率分析: 毛利率、净利率变化"
echo "   4. 现金流分析: 经营现金流情况"
echo "   5. 负债分析: 资产负债率变化"
echo "   6. 成长性分析: 3年复合增长率"
echo "   7. 风险评估: 增收不增利、现金流为负等"

# 持仓股票信息
echo ""
echo "⭐ 你的持仓股票 (7只，优先深度分析):"
echo "   鸣志电器(603728) - 成本68元 - 电机"
echo "   比亚迪(002594)   - 成本99元 - 新能源汽车"
echo "   卧龙电驱(600580) - 成本42元 - 电气设备"
echo "   生益科技(600183) - 成本66元 - 电子元件"
echo "   药明康德(603259) - 成本101元 - 医药"
echo "   顺丰控股(002352) - 成本40元 - 物流"
echo "   云天化(600096)   - 成本37元 - 化工"

# 飞书配置
echo ""
echo "📱 飞书推送配置:"
echo "   ✅ 已启用"
echo "   📍 地址: https://open.feishu.cn/open-apis/bot/v2/hook/fb95ec56-6ad7-4830-99c7-0eaa287e67e7"
echo "   📋 内容: 每日监控摘要 + 持仓重点关注"

# 启动监控
echo ""
echo "🚀 开始全面分析监控..."
echo "📝 本地日志: logs/final_financial_monitor.log"
echo "📊 本地数据: data/final_financial/"
echo "📄 本地报告: data/final_financial/daily_report_$(date +%Y-%m-%d).txt"
echo "📱 飞书推送: 报告生成后自动发送"

cd /Users/ago/.openclaw/workspace
python3 scripts/final_financial_monitor.py

echo ""
echo "✅ 全面分析监控完成!"
echo "📅 建议设置定时任务: 每天21:30自动运行"
echo "📊 报告包含: 超预期指标 + 全面财务分析 + 交易建议"
echo "📱 请检查飞书群是否收到推送消息"