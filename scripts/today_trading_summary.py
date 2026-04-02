#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
今日交易与持仓情况综合报告
"""

import os
import sys
import json
from datetime import datetime

def load_simulated_trading_data():
    """加载模拟交易数据"""
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    portfolio_file = os.path.join(workspace_dir, "data", "simulated_trading", "simulated_portfolio.json")
    trades_file = os.path.join(workspace_dir, "data", "simulated_trading", "simulated_trades.json")

    try:
        with open(portfolio_file, 'r', encoding='utf-8') as f:
            portfolio = json.load(f)

        with open(trades_file, 'r', encoding='utf-8') as f:
            trades = json.load(f)

        return portfolio, trades
    except Exception as e:
        print(f"❌ 加载模拟交易数据失败: {e}")
        return None, None

def load_tail_end_selection_data():
    """加载尾盘选股数据"""
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    selection_file = os.path.join(workspace_dir, "data", "tail_end_selection", "tail_end_selection_20260401_144500.json")

    try:
        with open(selection_file, 'r', encoding='utf-8') as f:
            selection = json.load(f)
        return selection
    except Exception as e:
        print(f"⚠️ 加载尾盘选股数据失败: {e}")
        return None

def generate_today_summary(portfolio, trades, selection):
    """生成今日总结报告"""
    print(f"\n📊 今日交易与持仓情况综合报告")
    print(f"📅 报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # 今日交易情况
    print(f"🎯 今日交易情况:")
    print(f"  📅 日期: 2026年4月1日")

    if selection:
        print(f"  ⏰ 尾盘选股执行时间: {selection.get('selection_time', '14:45:00')}")
        print(f"  📈 选股数量: {selection.get('total_selected', 0)}只")
        print(f"  🎯 策略名称: {selection.get('strategy_name', '尾盘选股策略')}")
        print(f"  🔧 策略版本: {selection.get('strategy_version', 'v1.0')}")

        # 今日选出的股票
        stocks = selection.get('stocks', [])
        if stocks:
            print(f"\n  📋 今日选出的股票 ({len(stocks)}只):")
            for i, stock in enumerate(stocks, 1):
                code = stock.get('code', '')
                name = stock.get('name', '')
                price = stock.get('current_price', 0)
                change = stock.get('change_percent', 0)
                score = stock.get('score', 0)

                print(f"    {i}. {name} ({code})")
                print(f"       当前价格: {price:.2f}元")
                print(f"       今日涨跌: {change:.2f}%")
                print(f"       综合评分: {score}/100分")
    else:
        print(f"  ⚠️ 今日尾盘选股数据未找到")

    # 持仓情况
    print(f"\n💰 当前持仓情况:")
    positions = portfolio.get('positions', [])

    if positions:
        print(f"  📊 总持仓数量: {len(positions)}只股票")
        print(f"  💰 总持仓市值: {portfolio.get('total_value', 0):,.2f}元")
        print(f"  📉 总浮动盈亏: {sum(p.get('unrealized_pnl', 0) for p in positions):,.2f}元")

        # 持仓详情
        print(f"\n  📋 持仓详情:")
        for i, pos in enumerate(positions, 1):
            code = pos.get('stock_code', '')
            name = pos.get('stock_name', '')
            entry_price = pos.get('entry_price', 0)
            current_price = pos.get('current_price', 0)
            pnl = pos.get('unrealized_pnl', 0)
            pnl_percent = pos.get('unrealized_pnl_percent', 0)
            entry_date = pos.get('entry_date', '')

            pnl_emoji = "📈" if pnl > 0 else "📉"

            print(f"    {i}. {name} ({code})")
            print(f"       进场价格: {entry_price:.2f}元")
            print(f"       当前价格: {current_price:.2f}元")
            print(f"       浮动盈亏: {pnl_emoji} {pnl:,.2f}元 ({pnl_percent:.2f}%)")
            print(f"       进场日期: {entry_date}")
    else:
        print(f"  📭 当前无持仓")

    # 资金情况
    print(f"\n💵 资金情况:")
    print(f"  初始资金: {portfolio.get('total_capital', 0):,.2f}元")
    print(f"  当前总资产: {portfolio.get('total_value', 0):,.2f}元")
    print(f"  已投资金额: {portfolio.get('invested_capital', 0):,.2f}元")
    print(f"  可用资金: {portfolio.get('available_capital', 0):,.2f}元")

    total_return = ((portfolio.get('total_value', 0) - portfolio.get('total_capital', 0)) /
                   portfolio.get('total_capital', 1) * 100)
    print(f"  总收益率: {total_return:.2f}%")

    # 交易统计
    print(f"\n📈 交易统计:")
    print(f"  总交易笔数: {trades.get('total_trades', 0)}笔")
    print(f"  活跃交易: {trades.get('active_trades', 0)}笔")
    print(f"  已平仓交易: {trades.get('closed_trades', 0)}笔")

    # 今日是否执行交易
    today = datetime.now().strftime("%Y-%m-%d")
    active_trades = [t for t in trades.get('trades', []) if t.get('status') == 'ACTIVE']
    today_trades = [t for t in active_trades if t.get('trade_date') == today]

    if today_trades:
        print(f"\n✅ 今日已执行交易:")
        for trade in today_trades:
            print(f"  - {trade.get('stock_name', '')} ({trade.get('stock_code', '')})")
            print(f"    进场价格: {trade.get('entry_price', 0):.2f}元")
            print(f"    投资金额: {trade.get('investment', 0):,.2f}元")
    else:
        print(f"\n⚠️ 今日未执行新交易")
        if selection and selection.get('total_selected', 0) > 0:
            print(f"  💡 提示: 今日14:45选出了{selection.get('total_selected', 0)}只股票，但未记录交易")
            print(f"  💡 原因: 可能是仓位已满或资金不足")

    # 风险提示
    print(f"\n⚠️ 风险提示:")
    print(f"  1. 当前仓位比例: {portfolio.get('invested_capital', 0)/portfolio.get('total_capital', 1)*100:.1f}%")
    print(f"  2. 总浮动盈亏: {sum(p.get('unrealized_pnl', 0) for p in positions):,.2f}元")
    print(f"  3. 胜率: {sum(1 for p in positions if p.get('unrealized_pnl', 0) > 0)/len(positions)*100 if positions else 0:.1f}%")

    # 明日计划
    print(f"\n📅 明日执行计划:")
    print(f"  1. 09:30-15:00: 每3分钟获取实时价格")
    print(f"  2. 14:30: 执行尾盘选股")
    print(f"  3. 18:00: 生成每日报告")
    print(f"  4. 18:05: 发送报告到A股数据分析群")

def main():
    """主函数"""
    print("🔍 今日交易与持仓情况检查")
    print("=" * 70)

    # 加载数据
    portfolio, trades = load_simulated_trading_data()
    selection = load_tail_end_selection_data()

    if portfolio is None or trades is None:
        print("❌ 无法加载核心交易数据")
        return

    generate_today_summary(portfolio, trades, selection)

if __name__ == "__main__":
    main()
