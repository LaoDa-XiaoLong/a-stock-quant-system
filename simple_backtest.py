#!/usr/bin/env python3
"""
简化的回测试验
"""

import pandas as pd
import numpy as np
from datetime import datetime

# 加载处理后的数据
df = pd.read_csv('data/processed/stock_000001_processed.csv')
df['date'] = pd.to_datetime(df['date'])

print(f"数据加载成功: {len(df)} 条记录")
print(f"数据期间: {df['date'].min()} 到 {df['date'].max()}")

# 简单的MACD策略模拟
def simulate_macd_strategy(df, initial_cash=100000):
    """模拟MACD策略"""
    cash = initial_cash
    position = 0
    trades = []
    
    # 计算MACD指标
    exp1 = df['收盘'].ewm(span=12, adjust=False).mean()
    exp2 = df['收盘'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    
    for i in range(1, len(df)):
        # 检查交易信号
        prev_macd = macd.iloc[i-1]
        prev_signal = signal.iloc[i-1]
        curr_macd = macd.iloc[i]
        curr_signal = signal.iloc[i]
        
        # 买入信号：MACD上穿信号线
        if prev_macd <= prev_signal and curr_macd > curr_signal and position == 0:
            # 买入
            price = df['收盘'].iloc[i]
            shares = int(cash * 0.95 / price)
            if shares > 0:
                cost = shares * price
                cash -= cost
                position = shares
                trades.append({
                    'date': df['date'].iloc[i],
                    'action': 'BUY',
                    'price': price,
                    'shares': shares,
                    'cash': cash,
                    'position': position
                })
        
        # 卖出信号：MACD下穿信号线
        elif prev_macd >= prev_signal and curr_macd < curr_signal and position > 0:
            # 卖出
            price = df['收盘'].iloc[i]
            proceeds = position * price
            cash += proceeds
            trades.append({
                'date': df['date'].iloc[i],
                'action': 'SELL',
                'price': price,
                'shares': position,
                'cash': cash,
                'position': 0
            })
            position = 0
    
    # 最后一天清仓
    if position > 0:
        price = df['收盘'].iloc[-1]
        proceeds = position * price
        cash += proceeds
        trades.append({
            'date': df['date'].iloc[-1],
            'action': 'SELL',
            'price': price,
            'shares': position,
            'cash': cash,
            'position': 0
        })
        position = 0
    
    return cash, trades

# 运行模拟
final_cash, trades = simulate_macd_strategy(df)
initial_cash = 100000
total_return = (final_cash - initial_cash) / initial_cash

print(f"\n策略回测结果:")
print(f"初始资金: {initial_cash:.2f}")
print(f"最终资金: {final_cash:.2f}")
print(f"总收益率: {total_return:.2%}")
print(f"交易次数: {len(trades)}")

if trades:
    print(f"\n交易记录:")
    for trade in trades:
        print(f"  {trade['date'].date()} {trade['action']} {trade['shares']}股 @ {trade['price']:.2f}")

# 对比买入持有策略
buy_hold_return = (df['收盘'].iloc[-1] - df['收盘'].iloc[0]) / df['收盘'].iloc[0]
print(f"\n策略对比:")
print(f"MACD策略收益率: {total_return:.2%}")
print(f"买入持有收益率: {buy_hold_return:.2%}")

# 保存结果
import os
os.makedirs('reports', exist_ok=True)

# 保存交易记录
if trades:
    trades_df = pd.DataFrame(trades)
    trades_df.to_csv('reports/simple_trade_records.csv', index=False, encoding='utf-8-sig')
    print(f"\n交易记录已保存到: reports/simple_trade_records.csv")

# 生成简单报告
report = f"""
# 简化MACD策略回测报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 回测参数
- 初始资金: {initial_cash:.2f}
- 数据期间: {df['date'].min().date()} 到 {df['date'].max().date()}
- 数据条数: {len(df)}
- 交易股票: 000001 (示例数据)

## 策略规则
1. 买入信号: MACD线上穿信号线
2. 卖出信号: MACD线下穿信号线
3. 仓位: 95%资金投入
4. 佣金: 0% (简化模型)

## 回测结果
- 最终资金: {final_cash:.2f}
- 总收益率: {total_return:.2%}
- 交易次数: {len(trades)}
- 买入持有收益率: {buy_hold_return:.2%}

## 性能对比
- MACD策略超额收益: {(total_return - buy_hold_return):.2%}

## 结论
这是一个简化的MACD策略演示。实际应用中需要：
1. 使用真实市场数据
2. 考虑交易成本和滑点
3. 添加风险控制措施
4. 进行更长时间的回测
"""

with open('reports/simple_backtest_report.md', 'w', encoding='utf-8') as f:
    f.write(report)

print(f"\n回测报告已生成: reports/simple_backtest_report.md")
print("\n报告摘要:")
print("-" * 40)
print(report[:500] + "...")
print("-" * 40)