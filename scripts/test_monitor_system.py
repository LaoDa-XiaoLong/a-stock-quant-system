#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试监控系统功能
"""

import json
import time
from datetime import datetime
import os

def test_monitor_system():
    """测试监控系统"""
    print("🧪 测试实时股票监控系统")
    print("=" * 50)

    # 检查投资组合文件
    portfolio_file = 'data/investment_tracking/investment_portfolio.json'

    if not os.path.exists(portfolio_file):
        print("❌ 投资组合文件不存在")
        return

    with open(portfolio_file, 'r', encoding='utf-8') as f:
        portfolio = json.load(f)

    print(f"📊 投资组合信息:")
    print(f"   创建时间: {portfolio.get('created_date', 'N/A')}")
    print(f"   最后更新: {portfolio.get('last_updated', 'N/A')}")
    print(f"   股票数量: {len(portfolio['stocks'])}只")
    print()

    # 显示股票状态
    status_counts = {}
    for stock in portfolio['stocks']:
        status = stock['status']
        status_counts[status] = status_counts.get(status, 0) + 1

    print("📈 股票状态统计:")
    for status, count in status_counts.items():
        print(f"   {status}: {count}只")

    print()
    print("🎯 进场点位分析:")

    for stock in portfolio['stocks']:
        if stock['status'] == '待进场':
            print(f"\n{stock['code']} {stock['name']}:")
            print(f"   评分: {stock['score']}/100")
            print(f"   当前价格: {stock.get('current_price', 'N/A')}元")
            print(f"   进场策略:")
            print(f"     - 激进: {stock['entry_strategy']['激进进场']}元")
            print(f"     - 稳健: {stock['entry_strategy']['稳健进场']}元")
            print(f"     - 保守: {stock['entry_strategy']['保守进场']}元")
            print(f"   风险控制:")
            print(f"     - 止损: {stock['stop_loss']}元")
            print(f"     - 止盈: {stock['take_profit'][0]}元 / {stock['take_profit'][1]}元")

    # 模拟价格检查
    print()
    print("🔍 模拟价格检查:")

    # 模拟获取实时价格
    import random

    for stock in portfolio['stocks']:
        stock_code = stock['code']

        # 生成模拟价格
        base_price = 10.0
        code_suffix = int(stock_code[-2:]) if stock_code[-2:].isdigit() else 50
        variation = (code_suffix % 20) / 100.0
        random_change = random.uniform(-0.02, 0.03)
        current_price = base_price * (1 + variation + random_change)
        current_price = max(5.0, min(20.0, current_price))
        current_price = round(current_price, 2)

        print(f"\n{stock_code} {stock['name']}:")
        print(f"   模拟当前价格: {current_price}元")

        if stock['status'] == '待进场':
            # 检查进场条件
            entry_strategy = stock['entry_strategy']

            if current_price <= entry_strategy['激进进场']:
                print(f"   ✅ 达到激进进场条件! (需要: ≤{entry_strategy['激进进场']}元)")
            elif current_price <= entry_strategy['稳健进场']:
                print(f"   ✅ 达到稳健进场条件! (需要: ≤{entry_strategy['稳健进场']}元)")
            elif current_price <= entry_strategy['保守进场']:
                print(f"   ✅ 达到保守进场条件! (需要: ≤{entry_strategy['保守进场']}元)")
            else:
                print(f"   ⏳ 未达到进场条件")
                diff = current_price - entry_strategy['保守进场']
                print(f"     距离保守进场还需下跌: {diff:.2f}元 ({diff/current_price*100:.1f}%)")

        elif stock['status'] == '已进场':
            if 'entry_price' in stock:
                entry_price = stock['entry_price']
                profit_loss = (current_price - entry_price) * stock.get('current_position', 0)
                profit_loss_pct = (current_price - entry_price) / entry_price * 100

                print(f"   进场价格: {entry_price}元")
                print(f"   当前盈亏: {profit_loss:+.2f}元 ({profit_loss_pct:+.2f}%)")

                # 检查止损止盈
                if current_price <= stock['stop_loss']:
                    print(f"   ⚠️ 触发止损条件! (止损价: {stock['stop_loss']}元)")
                elif current_price >= stock['take_profit'][0]:
                    if current_price >= stock['take_profit'][1]:
                        print(f"   🎯 触发第二止盈条件! (止盈价: {stock['take_profit'][1]}元)")
                    else:
                        print(f"   🎯 触发第一止盈条件! (止盈价: {stock['take_profit'][0]}元)")

    # 检查定时任务
    print()
    print("📅 定时任务检查:")

    # 检查launchd任务
    import subprocess
    result = subprocess.run(['launchctl', 'list'], capture_output=True, text=True)

    if 'com.openclaw.trading_monitor' in result.stdout:
        print("✅ 交易监控定时任务已配置")
    else:
        print("❌ 交易监控定时任务未找到")

    if 'com.openclaw.daily_investment_report' in result.stdout:
        print("✅ 每日报告定时任务已配置")
    else:
        print("❌ 每日报告定时任务未找到")

    # 检查日志目录
    print()
    print("📁 文件系统检查:")

    required_dirs = [
        'data/investment_tracking',
        'logs'
    ]

    required_files = [
        'data/investment_tracking/investment_portfolio.json',
        'data/investment_tracking/操作指南.md',
        'scripts/real_time_stock_monitor.py',
        'scripts/start_trading_monitor.sh',
        'scripts/daily_investment_report.py'
    ]

    all_ok = True

    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ 目录存在: {dir_path}")
        else:
            print(f"❌ 目录缺失: {dir_path}")
            all_ok = False

    for file_path in required_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ 文件存在: {file_path} ({file_size}字节)")
        else:
            print(f"❌ 文件缺失: {file_path}")
            all_ok = False

    print()
    print("=" * 50)

    if all_ok:
        print("🎉 所有检查通过！系统准备就绪。")
        print()
        print("💡 使用说明:")
        print("   1. 交易时间自动启动: 系统会在09:29和12:59自动启动")
        print("   2. 手动启动监控: bash scripts/start_trading_monitor.sh")
        print("   3. 查看监控日志: tail -f logs/trading_monitor.log")
        print("   4. 查看交易记录: data/investment_tracking/trade_records_YYYYMMDD.json")
        print("   5. 查看每日报告: data/investment_tracking/daily_monitor_summary_YYYY-MM-DD.md")
    else:
        print("⚠️ 部分检查未通过，请修复缺失的文件或目录。")

    return all_ok

if __name__ == '__main__':
    test_monitor_system()
