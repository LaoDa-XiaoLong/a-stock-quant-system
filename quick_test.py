#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试股票数据更新
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import json
import os

print("快速测试股票数据获取")
print("=" * 50)

# 测试1: 获取A股列表
print("1. 测试获取A股列表...")
try:
    stock_info = ak.stock_info_a_code_name()
    print(f"   成功获取 {len(stock_info)} 只A股股票")
    print(f"   前5只股票:")
    for i, (_, row) in enumerate(stock_info.head(5).iterrows(), 1):
        print(f"     {i}. {row['code']} {row['name']}")
except Exception as e:
    print(f"   获取失败: {e}")

print("\n2. 测试获取实时行情...")
try:
    # 获取实时行情
    spot_data = ak.stock_zh_a_spot()
    print(f"   获取到 {len(spot_data)} 只股票的实时数据")
    
    if not spot_data.empty:
        # 显示前3只股票
        print(f"   实时行情示例:")
        for i in range(min(3, len(spot_data))):
            row = spot_data.iloc[i]
            print(f"     {row['代码']} {row['名称']}: {row['最新价']}元 "
                  f"({row['涨跌幅']}%) 成交额:{float(row['成交额'])/1e8:.2f}亿")
except Exception as e:
    print(f"   获取失败: {e}")

print("\n3. 测试获取单只股票信息...")
test_symbol = '000001'  # 平安银行
try:
    stock_individual = ak.stock_individual_info_em(symbol=test_symbol)
    print(f"   股票 {test_symbol} 基本信息:")
    if not stock_individual.empty:
        for _, row in stock_individual.iterrows():
            print(f"     {row['item']}: {row['value']}")
except Exception as e:
    print(f"   获取失败: {e}")

print("\n4. 检查数据目录...")
data_dir = "data"
stock_pool_dir = os.path.join(data_dir, "stock_pool")
os.makedirs(stock_pool_dir, exist_ok=True)
print(f"   数据目录: {data_dir}")
print(f"   股票池目录: {stock_pool_dir}")

# 创建简单的配置文件
config = {
    "update": {
        "max_retries": 3,
        "retry_delay": 2
    },
    "data_sources": {
        "use_cache": True,
        "cache_expiry_hours": 24
    }
}

config_file = "config/quick_test_config.json"
os.makedirs(os.path.dirname(config_file), exist_ok=True)
with open(config_file, 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)
print(f"   配置文件已创建: {config_file}")

print("\n" + "=" * 50)
print("快速测试完成")
print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")