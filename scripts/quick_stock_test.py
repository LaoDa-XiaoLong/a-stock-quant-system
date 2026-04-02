#!/usr/bin/env python3
"""
快速股票数据测试
"""

import akshare as ak
import pandas as pd
from datetime import datetime

def main():
    print("快速测试akshare股票数据...")

    # 测试1: 获取股票列表
    print("\n1. 测试股票列表获取...")
    try:
        stock_list = ak.stock_info_a_code_name()
        print(f"   成功获取 {len(stock_list)} 只股票")
        print(f"   前3只股票: {stock_list.head(3).to_dict('records')}")
    except Exception as e:
        print(f"   失败: {e}")

    # 测试2: 获取指数数据
    print("\n2. 测试指数数据获取...")
    try:
        index_data = ak.stock_zh_index_daily(symbol="sh000001")
        print(f"   成功获取上证指数 {len(index_data)} 条记录")
        print(f"   最新日期: {index_data.iloc[-1]['date'] if 'date' in index_data.columns else 'N/A'}")
    except Exception as e:
        print(f"   失败: {e}")

    # 测试3: 获取单只股票历史数据
    print("\n3. 测试单只股票历史数据...")
    try:
        stock_data = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20250101", end_date="20250331", adjust="qfq")
        print(f"   成功获取平安银行 {len(stock_data)} 条记录")
        print(f"   列名: {stock_data.columns.tolist()}")
    except Exception as e:
        print(f"   失败: {e}")

    print("\n测试完成!")

if __name__ == "__main__":
    main()
