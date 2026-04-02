#!/usr/bin/env python3
"""
测试数据分析
"""

import pandas as pd
import numpy as np
import os

# 加载示例数据
data_file = 'data/raw/stock_000001_20230101_20260327.csv'
df = pd.read_csv(data_file)

print(f"数据加载成功: {len(df)} 条记录")
print(f"数据列: {df.columns.tolist()}")

# 基本计算
df['daily_return'] = df['收盘'].pct_change()
total_return = (df['收盘'].iloc[-1] - df['收盘'].iloc[0]) / df['收盘'].iloc[0]

print(f"\n基本分析:")
print(f"数据期间: {df['日期'].iloc[0]} 到 {df['日期'].iloc[-1]}")
print(f"起始价格: {df['收盘'].iloc[0]:.2f}")
print(f"结束价格: {df['收盘'].iloc[-1]:.2f}")
print(f"总收益率: {total_return:.2%}")
print(f"平均日收益率: {df['daily_return'].mean():.4%}")
print(f"日收益率标准差: {df['daily_return'].std():.4%}")

# 创建处理后的数据
df_processed = df.copy()
df_processed.rename(columns={'日期': 'date'}, inplace=True)

# 保存处理后的数据
os.makedirs('data/processed', exist_ok=True)
processed_file = 'data/processed/stock_000001_processed.csv'
df_processed.to_csv(processed_file, index=False, encoding='utf-8-sig')
print(f"\n处理后的数据已保存到: {processed_file}")
