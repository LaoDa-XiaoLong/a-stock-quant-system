#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查尾盘选股策略持仓情况
"""

import os
import sys
import json
from datetime import datetime

def load_portfolio_data():
    """加载投资组合数据"""
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
        print(f"❌ 加载数据失败: {e}")
        return None, None

def generate_position_report(portfolio, trades):
    """生成持仓报告"""
    print(f"\n📊 尾盘选股策略持仓情况")
    print(f"📅 报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # 资金概览
    print(f"💰 资金概览:")
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

    # 持仓详情
    positions = portfolio.get('positions', [])
    if positions:
        print(f"\n📋 当前持仓 ({len(positions)} 只股票):")
        print("=" * 70)

        total_market_value = 0
        total_unrealized_pnl = 0
        total_investment = 0

        for i, pos in enumerate(positions, 1):
            pnl = pos.get('unrealized_pnl', 0)
            pnl_percent = pos.get('unrealized_pnl_percent', 0)
            pnl_emoji = "📈" if pnl > 0 else "📉"

            print(f"{i}. {pos.get('stock_name', '')} ({pos.get('stock_code', '')})")
            print(f"   持仓数量: {pos.get('shares', 0):,}股")
            print(f"   进场价格: {pos.get('entry_price', 0):.2f}元")
            print(f"   当前价格: {pos.get('current_price', 0):.2f}元")
            print(f"   浮动盈亏: {pnl_emoji} {pnl:,.2f}元 ({pnl_percent:.2f}%)")
            print(f"   持仓市值: {pos.get('market_value', 0):,.2f}元")
            print(f"   进场日期: {pos.get('entry_date', '')}")
            print()

            total_market_value += pos.get('market_value', 0)
            total_unrealized_pnl += pnl
            total_investment += pos.get('entry_price', 0) * pos.get('shares', 0)

        print("=" * 70)
        print(f"📊 持仓汇总:")
        print(f"  总持仓市值: {total_market_value:,.2f}元")
        print(f"  总投资金额: {total_investment:,.2f}元")
        print(f"  总浮动盈亏: {total_unrealized_pnl:,.2f}元")
        print(f"  持仓比例: {total_market_value/portfolio.get('total_capital', 1)*100:.1f}%")

        # 盈亏分析
        winning_positions = sum(1 for pos in positions if pos.get('unrealized_pnl', 0) > 0)
        losing_positions = sum(1 for pos in positions if pos.get('unrealized_pnl', 0) < 0)

        print(f"\n📊 盈亏分析:")
        print(f"  盈利持仓: {winning_positions}只")
        print(f"  亏损持仓: {losing_positions}只")
        print(f"  持平持仓: {len(positions) - winning_positions - losing_positions}只")
        print(f"  胜率: {winning_positions/len(positions)*100:.1f}%")
    else:
        print("\n📭 当前无持仓")

    # 策略信息
    print(f"\n🎯 策略信息:")
    print(f"  策略名称: {trades.get('strategy_name', '杨永兴隔夜套利战法')}")
    print(f"  系统名称: {trades.get('system_name', '尾盘选股策略模拟交易系统')}")
    print(f"  创建日期: {trades.get('created_date', '2026-04-01')}")
    print(f"  最后更新: {trades.get('last_updated', '')}")

    # 下次执行计划
    print(f"\n⏰ 下次执行计划:")
    print(f"  尾盘选股: 今日14:30 (基于真实价格)")
    print(f"  每日报告: 今日18:00")
    print(f"  报告发送: 今日18:05 (A股数据分析群)")

    # 风险提示
    print(f"\n⚠️ 风险提示:")
    print(f"  1. 当前为模拟交易，实际盈亏可能不同")
    print(f"  2. 股市有风险，投资需谨慎")
    print(f"  3. 严格执行止损纪律")
    print(f"  4. 控制单只股票仓位不超过30%")

def main():
    """主函数"""
    print("🔍 检查尾盘选股策略持仓情况")
    print("=" * 70)

    portfolio, trades = load_portfolio_data()

    if portfolio is None or trades is None:
        print("❌ 无法加载持仓数据")
        return

    generate_position_report(portfolio, trades)

if __name__ == "__main__":
    main()
