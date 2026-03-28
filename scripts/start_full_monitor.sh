#!/bin/bash
# 启动全A股财报监控系统

echo "🚀 启动全A股上市公司财报监控系统"
echo "📅 日期: $(date '+%Y-%m-%d %H:%M:%S')"
echo "📊 监控范围: 全A股上市公司"
echo "🎯 目标: 发现财报超预期投资机会"
echo "⏰ 检查频率: 每小时一次"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到python3，请先安装Python"
    exit 1
fi

# 检查依赖
echo "🔍 检查Python依赖..."
python3 -c "import requests, pandas, numpy, sqlite3, logging, json, os, threading" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  缺少部分依赖，尝试安装..."
    pip3 install requests pandas numpy --quiet
fi

# 创建必要目录
mkdir -p data/full_a_stock logs

# 显示配置
echo ""
echo "📋 监控配置:"
echo "   超预期阈值: 30%"
echo "   并发线程数: 10"
echo "   重点关注行业:"
echo "     - 新能源汽车"
echo "     - 锂电池/光伏"
echo "     - 半导体"
echo "     - 医药"
echo "     - 人工智能/云计算"

# 特别关注比亚迪
echo ""
echo "⭐ 特别关注: 比亚迪(002594)"
echo "   预计2025年年报已发布"
echo "   关注要点:"
echo "     1. 营收是否超预期"
echo "     2. 净利润变化"
echo "     3. 海外业务增长"
echo "     4. 研发投入情况"

# 启动监控
echo ""
echo "📝 监控日志将保存到: logs/full_a_stock_monitor.log"
echo "📊 监控数据将保存到: data/full_a_stock/"
echo "💾 数据库文件: data/full_a_stock/a_stock_reports.db"
echo ""
echo "按 Ctrl+C 停止监控"

# 运行Python监控脚本
cd /Users/ago/.openclaw/workspace
python3 scripts/full_a_stock_monitor.py