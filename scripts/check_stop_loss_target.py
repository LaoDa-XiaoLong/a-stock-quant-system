#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查尾盘选股持仓的止损止盈情况
"""

import os
import sys
import json
from datetime import datetime

def load_trades_data():
    """加载交易数据"""
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    trades_file = os.path.join(workspace_dir, "data", "simulated_trading", "simulated_trades.json")
    
    try:
        with open(trades_file, 'r', encoding='utf-8') as f:
            trades = json.load(f)
        return trades
    except Exception as e:
        print(f"❌ 加载交易数据失败: {e}")
        return None

def check_stop_loss_target(trades):
    """检查止损止盈情况"""
    print(f"\n🛡️ 尾盘选股持仓止损止盈检查")
    print(f"📅 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    active_trades = [t for t in trades.get('trades', []) if t.get('status') == 'ACTIVE']
    
    if not active_trades:
        print("📭 当前无活跃持仓")
        return
    
    print(f"📊 共 {len(active_trades)} 笔活跃交易:")
    print("=" * 70)
    
    stop_loss_hit = 0
    target_hit = 0
    in_range = 0
    
    for i, trade in enumerate(active_trades, 1):
        stock_code = trade.get('stock_code', '')
        stock_name = trade.get('stock_name', '')
        entry_price = trade.get('entry_price', 0)
        current_price = trade.get('current_price', 0)
        stop_loss = trade.get('stop_loss', 0)
        target_price = trade.get('target_price', 0)
        
        # 计算价格关系
        stop_loss_distance = (current_price - stop_loss) / entry_price * 100
        target_distance = (target_price - current_price) / entry_price * 100
        current_return = (current_price - entry_price) / entry_price * 100
        
        # 判断状态
        if current_price <= stop_loss:
            status = "🔴 触发止损"
            stop_loss_hit += 1
        elif current_price >= target_price:
            status = "🟢 触发止盈"
            target_hit += 1
        else:
            status = "🟡 持仓中"
            in_range += 1
        
        print(f"{i}. {stock_name} ({stock_code})")
        print(f"   进场价格: {entry_price:.2f}元")
        print(f"   当前价格: {current_price:.2f}元")
        print(f"   止损价格: {stop_loss:.2f}元 (距离: {stop_loss_distance:.2f}%)")
        print(f"   目标价格: {target_price:.2f}元 (距离: {target_distance:.2f}%)")
        print(f"   当前盈亏: {current_return:.2f}%")
        print(f"   状态: {status}")
        print()
    
    print("=" * 70)
    print(f"📊 状态汇总:")
    print(f"  触发止损: {stop_loss_hit}笔")
    print(f"  触发止盈: {target_hit}笔")
    print(f"  持仓中: {in_range}笔")
    
    # 风险提示
    print(f"\n⚠️ 风险控制建议:")
    
    if stop_loss_hit > 0:
        print(f"  🔴 有 {stop_loss_hit} 笔交易触发止损，建议立即平仓")
    
    if target_hit > 0:
        print(f"  🟢 有 {target_hit} 笔交易触发止盈，建议分批止盈")
    
    if in_range > 0:
        print(f"  🟡 有 {in_range} 笔交易持仓中，继续监控")
    
    # 仓位管理检查
    total_investment = sum(t.get('investment', 0) for t in active_trades)
    initial_capital = 1000000  # 假设初始资金100万
    
    position_ratio = total_investment / initial_capital * 100
    
    print(f"\n💰 仓位管理检查:")
    print(f"  总投资额: {total_investment:,.2f}元")
    print(f"  初始资金: {initial_capital:,.2f}元")
    print(f"  仓位比例: {position_ratio:.1f}%")
    
    if position_ratio > 150:
        print(f"  🔴 仓位过重 ({position_ratio:.1f}%)，建议减仓")
    elif position_ratio > 100:
        print(f"  🟡 仓位较重 ({position_ratio:.1f}%)，注意风险")
    else:
        print(f"  🟢 仓位合理 ({position_ratio:.1f}%)")
    
    # 持仓建议
    print(f"\n🎯 持仓建议:")
    print(f"  1. 严格执行止损纪律")
    print(f"  2. 达到目标价格可分批止盈")
    print(f"  3. 控制单只股票仓位不超过30%")
    print(f"  4. 今日14:30将执行新一轮尾盘选股")

def main():
    """主函数"""
    print("🔍 检查尾盘选股持仓止损止盈情况")
    print("=" * 70)
    
    trades = load_trades_data()
    
    if trades is None:
        print("❌ 无法加载交易数据")
        return
    
    check_stop_loss_target(trades)

if __name__ == "__main__":
    main()