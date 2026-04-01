#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析今日交易执行情况
"""

import os
import sys
import json
from datetime import datetime

def analyze_execution():
    """分析今日执行情况"""
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    print(f"🔍 今日交易执行情况分析")
    print(f"📅 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 1. 检查尾盘选股执行情况
    print(f"\n1. 📊 尾盘选股执行情况:")
    selection_file = os.path.join(workspace_dir, "data", "tail_end_selection", "tail_end_selection_20260401_144500.json")
    
    if os.path.exists(selection_file):
        with open(selection_file, 'r', encoding='utf-8') as f:
            selection = json.load(f)
        
        print(f"   ✅ 已执行尾盘选股")
        print(f"     执行时间: {selection.get('selection_time', '14:45:00')}")
        print(f"     策略名称: {selection.get('strategy_name', '尾盘选股策略')}")
        print(f"     选股数量: {selection.get('total_selected', 0)}只")
        
        stocks = selection.get('stocks', [])
        if stocks:
            print(f"     选出的股票:")
            for stock in stocks:
                print(f"       - {stock.get('name', '')} ({stock.get('code', '')})")
                print(f"         价格: {stock.get('current_price', 0):.2f}元")
                print(f"         涨跌: {stock.get('change_percent', 0):.2f}%")
                print(f"         评分: {stock.get('score', 0)}/100分")
    else:
        print(f"   ❌ 未找到尾盘选股执行记录")
    
    # 2. 检查模拟交易系统
    print(f"\n2. 💰 模拟交易系统状态:")
    portfolio_file = os.path.join(workspace_dir, "data", "simulated_trading", "simulated_portfolio.json")
    trades_file = os.path.join(workspace_dir, "data", "simulated_trading", "simulated_trades.json")
    
    if os.path.exists(portfolio_file) and os.path.exists(trades_file):
        with open(portfolio_file, 'r', encoding='utf-8') as f:
            portfolio = json.load(f)
        
        with open(trades_file, 'r', encoding='utf-8') as f:
            trades = json.load(f)
        
        print(f"   ✅ 模拟交易系统正常")
        print(f"     初始资金: {portfolio.get('total_capital', 0):,.2f}元")
        print(f"     当前总资产: {portfolio.get('total_value', 0):,.2f}元")
        print(f"     可用资金: {portfolio.get('available_capital', 0):,.2f}元")
        print(f"     总交易笔数: {trades.get('total_trades', 0)}笔")
        print(f"     活跃交易: {trades.get('active_trades', 0)}笔")
        
        # 检查今日交易
        active_trades = [t for t in trades.get('trades', []) if t.get('status') == 'ACTIVE']
        today = datetime.now().strftime("%Y-%m-%d")
        today_trades = [t for t in active_trades if t.get('trade_date') == today]
        
        if today_trades:
            print(f"   ✅ 今日已执行交易: {len(today_trades)}笔")
            for trade in today_trades:
                print(f"      - {trade.get('stock_name', '')} ({trade.get('stock_code', '')})")
        else:
            print(f"   ⚠️ 今日未执行新交易")
    else:
        print(f"   ❌ 模拟交易系统文件不存在")
    
    # 3. 检查资金情况
    print(f"\n3. 💵 资金情况分析:")
    if os.path.exists(portfolio_file):
        with open(portfolio_file, 'r', encoding='utf-8') as f:
            portfolio = json.load(f)
        
        available_capital = portfolio.get('available_capital', 0)
        invested_capital = portfolio.get('invested_capital', 0)
        total_capital = portfolio.get('total_capital', 1000000)
        
        print(f"   可用资金: {available_capital:,.2f}元")
        print(f"   已投资金额: {invested_capital:,.2f}元")
        print(f"   仓位比例: {invested_capital/total_capital*100:.1f}%")
        
        if available_capital < 0:
            print(f"   ⚠️ 可用资金为负数: {available_capital:,.2f}元")
            print(f"   💡 原因: 当前持仓市值超过初始资金")
        elif available_capital < total_capital * 0.1:
            print(f"   ⚠️ 可用资金不足: 仅剩{available_capital/total_capital*100:.1f}%")
        else:
            print(f"   ✅ 可用资金充足")
    
    # 4. 检查系统集成情况
    print(f"\n4. 🔧 系统集成情况:")
    
    # 检查Skill文件
    skill_dir = os.path.join(workspace_dir, "skills", "tail_end_selection")
    if os.path.exists(skill_dir):
        print(f"   ✅ 尾盘选股法Skill存在")
        
        init_file = os.path.join(skill_dir, "__init__.py")
        if os.path.exists(init_file):
            print(f"   ✅ Skill主文件存在")
        else:
            print(f"   ❌ Skill主文件不存在")
    else:
        print(f"   ❌ 尾盘选股法Skill目录不存在")
    
    # 检查调度系统
    scheduler_file = os.path.join(workspace_dir, "scripts", "daily_scheduler_fixed.py")
    if os.path.exists(scheduler_file):
        print(f"   ✅ 每日调度系统存在")
    else:
        print(f"   ❌ 每日调度系统不存在")
    
    # 5. 分析今日未执行交易的原因
    print(f"\n5. 🔍 今日未执行交易原因分析:")
    
    if os.path.exists(selection_file) and os.path.exists(portfolio_file):
        with open(selection_file, 'r', encoding='utf-8') as f:
            selection = json.load(f)
        
        with open(portfolio_file, 'r', encoding='utf-8') as f:
            portfolio = json.load(f)
        
        available_capital = portfolio.get('available_capital', 0)
        selected_count = selection.get('total_selected', 0)
        
        print(f"   今日选股数量: {selected_count}只")
        print(f"   当前可用资金: {available_capital:,.2f}元")
        
        if available_capital <= 0:
            print(f"   ❌ 主要原因: 可用资金不足 (当前: {available_capital:,.2f}元)")
            print(f"   💡 建议: 需要平仓部分持仓释放资金")
        elif selected_count == 0:
            print(f"   ❌ 主要原因: 未选出符合条件的股票")
            print(f"   💡 建议: 检查选股策略参数")
        else:
            print(f"   ⚠️ 可能原因: 系统集成问题")
            print(f"   💡 建议: 检查尾盘选股法Skill的交易记录功能")
    else:
        print(f"   ❌ 无法分析: 缺少必要数据文件")
    
    # 6. 明日改进建议
    print(f"\n6. 🎯 明日改进建议:")
    print(f"   1. 检查尾盘选股法Skill的交易记录功能")
    print(f"   2. 确保可用资金充足 (当前: {available_capital if 'available_capital' in locals() else 0:,.2f}元)")
    print(f"   3. 验证系统集成: Skill -> 交易记录 -> 投资组合")
    print(f"   4. 检查Cron任务执行情况")
    print(f"   5. 确保实时价格数据正常获取")
    
    # 7. 系统状态总结
    print(f"\n7. 📊 系统状态总结:")
    
    status_items = []
    
    # 尾盘选股执行
    if os.path.exists(selection_file):
        status_items.append("✅ 尾盘选股已执行")
    else:
        status_items.append("❌ 尾盘选股未执行")
    
    # 模拟交易系统
    if os.path.exists(portfolio_file) and os.path.exists(trades_file):
        status_items.append("✅ 模拟交易系统正常")
    else:
        status_items.append("❌ 模拟交易系统异常")
    
    # 资金情况
    if 'available_capital' in locals() and available_capital > 0:
        status_items.append("✅ 可用资金正常")
    else:
        status_items.append("❌ 可用资金不足")
    
    # Skill文件
    if os.path.exists(os.path.join(workspace_dir, "skills", "tail_end_selection", "__init__.py")):
        status_items.append("✅ Skill文件正常")
    else:
        status_items.append("❌ Skill文件异常")
    
    # 显示状态
    for status in status_items:
        print(f"   {status}")
    
    print(f"\n📅 明日执行计划:")
    print(f"   09:30-15:00: 每3分钟获取实时价格")
    print(f"   14:30: 执行尾盘选股")
    print(f"   18:00: 生成每日报告")
    print(f"   18:05: 发送报告到A股数据分析群")

def main():
    """主函数"""
    print("🔍 今日交易执行情况详细分析")
    print("=" * 70)
    
    analyze_execution()

if __name__ == "__main__":
    main()