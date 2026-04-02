#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
立即测试真实价格监控
"""

import json
from datetime import datetime
import os

print("🔍 立即检查真实价格和持仓情况")
print("=" * 60)

# 加载最新投资组合
portfolio_file = 'data/investment_tracking/investment_portfolio.json'

if not os.path.exists(portfolio_file):
    print("❌ 投资组合文件不存在")
    exit(1)

with open(portfolio_file, 'r', encoding='utf-8') as f:
    portfolio = json.load(f)

print(f"📊 投资组合信息:")
print(f"   创建时间: {portfolio.get('created_date', 'N/A')}")
print(f"   最后更新: {portfolio.get('last_updated', 'N/A')}")
print(f"   数据来源: {portfolio.get('data_source', 'N/A')}")
print(f"   更新类型: {portfolio.get('update_type', 'N/A')}")
print()

# 统计状态
status_counts = {}
for stock in portfolio['stocks']:
    status = stock['status']
    status_counts[status] = status_counts.get(status, 0) + 1

print("📈 股票状态统计:")
for status, count in status_counts.items():
    print(f"   {status}: {count}只")

print()
print("💰 投资概况:")
print(f"   总投资: {portfolio.get('total_investment', 0):.2f}元")
print(f"   当前市值: {portfolio.get('current_value', 0):.2f}元")
print(f"   总盈亏: {portfolio.get('total_profit_loss', 0):+.2f}元")
print(f"   盈亏比例: {portfolio.get('total_profit_loss_pct', 0):+.2f}%")

print()
print("🎯 详细持仓分析:")
print("=" * 50)

for stock in portfolio['stocks']:
    stock_code = stock['code']
    stock_name = stock['name']
    status = stock['status']

    print(f"\n{stock_code} {stock_name} - {status}")
    print("-" * 30)

    if 'current_price' in stock:
        current_price = stock['current_price']
        current_change = stock.get('current_change', 0)
        price_source = stock.get('price_source', '未知')
        price_time = stock.get('price_timestamp', '未知')

        print(f"📊 实时价格: {current_price}元 ({current_change:+.2f}%)")
        print(f"📡 数据源: {price_source} | 时间: {price_time}")

        # 进场条件分析
        entry_strategy = stock['entry_strategy']

        print("🎯 进场条件检查:")

        if current_price <= entry_strategy['激进进场']:
            print(f"   ✅ 已达到激进进场条件! (≤{entry_strategy['激进进场']}元)")
            print(f"      建议: 使用60%仓位，立即进场")
        elif current_price <= entry_strategy['稳健进场']:
            print(f"   ✅ 已达到稳健进场条件! (≤{entry_strategy['稳健进场']}元)")
            print(f"      建议: 使用80%仓位，可以进场")
        elif current_price <= entry_strategy['保守进场']:
            print(f"   ✅ 已达到保守进场条件! (≤{entry_strategy['保守进场']}元)")
            print(f"      建议: 使用100%仓位，安全进场")
        else:
            diff = current_price - entry_strategy['保守进场']
            diff_pct = diff / current_price * 100
            print(f"   ⏳ 未达到进场条件")
            print(f"      距离保守进场还需下跌: {diff:.2f}元 ({diff_pct:.1f}%)")

        # 风险控制分析
        print("🛡️ 风险控制分析:")
        print(f"   止损点位: {stock['stop_loss']}元 (距离: {current_price - stock['stop_loss']:.2f}元)")
        print(f"   第一止盈: {stock['take_profit'][0]}元 (距离: {stock['take_profit'][0] - current_price:.2f}元)")
        print(f"   第二止盈: {stock['take_profit'][1]}元 (距离: {stock['take_profit'][1] - current_price:.2f}元)")

        # 如果已进场，显示盈亏
        if status == '已进场' and 'entry_price' in stock:
            entry_price = stock['entry_price']
            position = stock.get('current_position', 0)
            profit_loss = stock.get('profit_loss', 0)
            profit_loss_pct = stock.get('profit_loss_pct', 0)

            print("💰 持仓盈亏:")
            print(f"   进场价格: {entry_price}元")
            print(f"   持仓数量: {position}股")
            print(f"   投资金额: {stock.get('total_investment', 0):.2f}元")
            print(f"   当前盈亏: {profit_loss:+.2f}元 ({profit_loss_pct:+.2f}%)")

    else:
        print("❌ 未获取到价格数据")
        print(f"   进场策略: 激进≤{stock['entry_strategy']['激进进场']}元, 稳健≤{stock['entry_strategy']['稳健进场']}元, 保守≤{stock['entry_strategy']['保守进场']}元")

print()
print("=" * 60)
print("📅 系统状态总结")

# 检查定时任务
import subprocess
result = subprocess.run(['launchctl', 'list'], capture_output=True, text=True)

tasks = {
    '交易监控': 'com.openclaw.trading_monitor',
    '每日报告': 'com.openclaw.daily_investment_report'
}

print("\n⏰ 定时任务状态:")
for name, task_id in tasks.items():
    if task_id in result.stdout:
        print(f"   ✅ {name}: 已配置")
    else:
        print(f"   ❌ {name}: 未配置")

print("\n📁 文件系统状态:")
required_files = [
    'data/investment_tracking/investment_portfolio.json',
    'data/investment_tracking/real_price_report_2026-03-31.md',
    'scripts/update_real_prices_simple.py',
    'scripts/start_trading_monitor.sh'
]

for file_path in required_files:
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path)
        print(f"   ✅ {file_path} ({file_size}字节)")
    else:
        print(f"   ❌ {file_path} (缺失)")

print()
print("💡 操作建议:")

# 检查是否有达到进场条件的股票
entered_stocks = []
for stock in portfolio['stocks']:
    if 'current_price' in stock and stock['status'] == '待进场':
        current_price = stock['current_price']
        entry_strategy = stock['entry_strategy']

        if current_price <= entry_strategy['激进进场']:
            entered_stocks.append((stock, '激进进场'))
        elif current_price <= entry_strategy['稳健进场']:
            entered_stocks.append((stock, '稳健进场'))
        elif current_price <= entry_strategy['保守进场']:
            entered_stocks.append((stock, '保守进场'))

if entered_stocks:
    print(f"\n🎯 发现{len(entered_stocks)}只股票达到进场条件:")
    for stock, entry_type in entered_stocks:
        print(f"   {stock['code']} {stock['name']}: {stock['current_price']}元 ({entry_type})")

    print("\n   建议操作:")
    print("   1. 立即手动记录交易:")
    print("      cd /Users/ago/.openclaw/workspace")
    print("      python3 data/investment_tracking/update_tracking.py buy 股票代码 价格 数量")
    print("   2. 或等待明天系统自动执行")
else:
    print("\n⏳ 暂无股票达到进场条件，继续监控")

print()
print("🔄 立即刷新价格:")
print("   cd /Users/ago/.openclaw/workspace")
print("   python3 scripts/update_real_prices_simple.py")

print()
print("🚀 明天自动执行:")
print("   09:29 - 交易监控系统自动启动")
print("   09:30-11:30 - 每3分钟获取真实价格")
print("   12:59 - 下午监控系统自动启动")
print("   13:00-15:00 - 每3分钟获取真实价格")
print("   16:00 - 自动生成详细报告")
