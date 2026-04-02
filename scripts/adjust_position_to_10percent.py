#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调整每只股票仓位为10%
"""

import os
import sys
import json
from datetime import datetime

def adjust_positions():
    """调整仓位到10%"""
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 文件路径
    portfolio_file = os.path.join(workspace_dir, "data", "simulated_trading", "simulated_portfolio.json")
    trades_file = os.path.join(workspace_dir, "data", "simulated_trading", "simulated_trades.json")
    
    print(f"🔧 调整每只股票仓位为10%")
    print(f"📅 调整时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 加载数据
    try:
        with open(portfolio_file, 'r', encoding='utf-8') as f:
            portfolio = json.load(f)
        
        with open(trades_file, 'r', encoding='utf-8') as f:
            trades = json.load(f)
    except Exception as e:
        print(f"❌ 加载数据失败: {e}")
        return
    
    # 初始资金
    initial_capital = portfolio.get('total_capital', 1000000)
    target_position_percent = 0.10  # 10%
    
    print(f"💰 初始资金: {initial_capital:,.2f}元")
    print(f"🎯 目标仓位: {target_position_percent*100}%")
    print(f"🎯 单只股票目标投资额: {initial_capital * target_position_percent:,.2f}元")
    
    # 检查当前持仓
    positions = portfolio.get('positions', [])
    active_trades = [t for t in trades.get('trades', []) if t.get('status') == 'ACTIVE']
    
    if not positions:
        print(f"📭 当前无持仓，无需调整")
        return
    
    print(f"\n📊 当前持仓情况 ({len(positions)} 只股票):")
    print("=" * 70)
    
    total_adjustment_needed = 0
    adjustments = []
    
    for i, (pos, trade) in enumerate(zip(positions, active_trades), 1):
        stock_code = pos.get('stock_code', '')
        stock_name = pos.get('stock_name', '')
        current_shares = pos.get('shares', 0)
        current_price = pos.get('current_price', 0)
        entry_price = pos.get('entry_price', 0)
        
        # 当前持仓市值
        current_value = current_shares * current_price
        
        # 目标持仓市值 (10%仓位)
        target_value = initial_capital * target_position_percent
        
        # 目标股数
        target_shares = int(target_value / current_price)
        
        # 调整股数
        shares_adjustment = target_shares - current_shares
        
        # 调整金额
        adjustment_amount = shares_adjustment * current_price
        
        print(f"{i}. {stock_name} ({stock_code})")
        print(f"   当前持仓: {current_shares:,}股")
        print(f"   当前价格: {current_price:.2f}元")
        print(f"   当前市值: {current_value:,.2f}元")
        print(f"   目标持仓: {target_shares:,}股")
        print(f"   目标市值: {target_value:,.2f}元")
        print(f"   调整股数: {shares_adjustment:+,}股")
        print(f"   调整金额: {adjustment_amount:+,.2f}元")
        
        adjustments.append({
            'stock_code': stock_code,
            'stock_name': stock_name,
            'current_shares': current_shares,
            'target_shares': target_shares,
            'shares_adjustment': shares_adjustment,
            'adjustment_amount': adjustment_amount,
            'current_price': current_price
        })
        
        total_adjustment_needed += adjustment_amount
    
    print("=" * 70)
    print(f"📊 调整汇总:")
    print(f"   总调整金额: {total_adjustment_needed:+,.2f}元")
    
    if total_adjustment_needed > 0:
        print(f"   ⚠️ 需要增加投资: {total_adjustment_needed:,.2f}元")
    elif total_adjustment_needed < 0:
        print(f"   ✅ 需要减少投资: {abs(total_adjustment_needed):,.2f}元")
        print(f"   💡 调整后将释放资金: {abs(total_adjustment_needed):,.2f}元")
    else:
        print(f"   ✅ 仓位已符合10%要求")
    
    # 确认调整
    print(f"\n❓ 是否执行调整？ (y/n): ", end="")
    response = input().strip().lower()
    
    if response != 'y':
        print(f"❌ 用户取消调整")
        return
    
    # 执行调整
    print(f"\n🔄 执行仓位调整...")
    
    # 更新投资组合
    new_positions = []
    new_invested_capital = 0
    
    for adj in adjustments:
        if adj['shares_adjustment'] == 0:
            # 无需调整，保持原持仓
            new_shares = adj['current_shares']
        else:
            # 调整持仓
            new_shares = adj['target_shares']
        
        new_position = {
            'trade_id': f"TRADE_{datetime.now().strftime('%Y%m%d')}_{len(new_positions)+1:03d}",
            'stock_code': adj['stock_code'],
            'stock_name': adj['stock_name'],
            'shares': new_shares,
            'entry_price': adj['current_price'],  # 使用当前价格作为新的进场价格
            'current_price': adj['current_price'],
            'market_value': new_shares * adj['current_price'],
            'unrealized_pnl': 0,  # 调整后盈亏归零
            'unrealized_pnl_percent': 0,
            'entry_date': datetime.now().strftime("%Y-%m-%d")
        }
        
        new_positions.append(new_position)
        new_invested_capital += new_shares * adj['current_price']
    
    # 更新投资组合数据
    portfolio['positions'] = new_positions
    portfolio['invested_capital'] = new_invested_capital
    portfolio['available_capital'] = portfolio['total_capital'] - new_invested_capital
    portfolio['total_value'] = portfolio['available_capital'] + new_invested_capital
    
    # 计算总市值
    total_market_value = sum(pos['market_value'] for pos in new_positions)
    portfolio['total_value'] = portfolio['available_capital'] + total_market_value
    
    # 更新交易记录
    new_trades = []
    for i, pos in enumerate(new_positions, 1):
        trade = {
            'trade_id': pos['trade_id'],
            'stock_code': pos['stock_code'],
            'stock_name': pos['stock_name'],
            'trade_date': datetime.now().strftime("%Y-%m-%d"),
            'trade_type': 'BUY',
            'entry_price': pos['entry_price'],
            'target_price': round(pos['entry_price'] * 1.08, 2),  # 8%目标
            'stop_loss': round(pos['entry_price'] * 0.95, 2),     # 5%止损
            'shares': pos['shares'],
            'investment': pos['shares'] * pos['entry_price'],
            'position_percent': target_position_percent,
            'strategy_score': 100,
            'passed_steps': 6,
            'status': 'ACTIVE',
            'entry_time': datetime.now().strftime("%H:%M"),
            'holding_days': 0,
            'current_price': pos['current_price'],
            'current_value': pos['market_value'],
            'unrealized_pnl': 0,
            'unrealized_pnl_percent': 0,
            'exit_price': None,
            'exit_date': None,
            'exit_reason': None,
            'realized_pnl': 0,
            'trade_notes': f'仓位调整至10% - 原持仓调整'
        }
        new_trades.append(trade)
    
    trades['trades'] = new_trades
    trades['total_trades'] = len(new_trades)
    trades['active_trades'] = len(new_trades)
    trades['closed_trades'] = 0
    trades['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 保存数据
    try:
        with open(portfolio_file, 'w', encoding='utf-8') as f:
            json.dump(portfolio, f, ensure_ascii=False, indent=2)
        
        with open(trades_file, 'w', encoding='utf-8') as f:
            json.dump(trades, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 仓位调整完成!")
        print(f"   更新投资组合文件: {portfolio_file}")
        print(f"   更新交易记录文件: {trades_file}")
        
        # 显示调整结果
        print(f"\n📊 调整后持仓情况:")
        print("=" * 70)
        
        for i, pos in enumerate(new_positions, 1):
            print(f"{i}. {pos['stock_name']} ({pos['stock_code']})")
            print(f"   持仓数量: {pos['shares']:,}股")
            print(f"   持仓市值: {pos['market_value']:,.2f}元")
            print(f"   仓位比例: {pos['market_value']/initial_capital*100:.1f}%")
        
        print("=" * 70)
        print(f"💰 资金情况:")
        print(f"   初始资金: {portfolio['total_capital']:,.2f}元")
        print(f"   已投资金额: {portfolio['invested_capital']:,.2f}元")
        print(f"   可用资金: {portfolio['available_capital']:,.2f}元")
        print(f"   总资产: {portfolio['total_value']:,.2f}元")
        print(f"   仓位比例: {portfolio['invested_capital']/portfolio['total_capital']*100:.1f}%")
        
    except Exception as e:
        print(f"❌ 保存数据失败: {e}")

def main():
    """主函数"""
    print("🔧 调整每只股票仓位为10%")
    print("=" * 70)
    
    adjust_positions()

if __name__ == "__main__":
    main()