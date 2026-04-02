#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票池筛选系统 - 第二部分
完成主函数和测试
"""

import pandas as pd
import numpy as np
import akshare as ak
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Tuple
import json
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """主函数：测试股票池筛选系统"""
    print("股票池筛选系统测试")
    print("=" * 50)

    # 导入筛选器类
    from stock_pool_filter import StockPoolFilter

    # 创建筛选器
    filter = StockPoolFilter()

    # 测试获取A股列表
    print("1. 获取A股列表...")
    all_stocks = filter.get_all_a_shares()
    print(f"   获取到 {len(all_stocks)} 只A股股票")

    # 测试筛选少量股票
    print("\n2. 测试筛选股票...")
    test_symbols = ['000001', '000002', '002352', '600580', '603728']

    for symbol in test_symbols:
        result = filter.filter_stock(symbol)
        status = "✅ 通过" if result['passed'] else "❌ 未通过"
        print(f"   {symbol}: {status} (分数: {result['weighted_score']:.1f})")

    # 生成股票池
    print("\n3. 生成股票池...")
    filtered_pool = filter.filter_stock_pool(symbols=test_symbols, max_stocks=10)

    if not filtered_pool.empty:
        print(f"   生成股票池: {len(filtered_pool)} 只股票")
        print("\n   前5名股票:")
        for i, (_, row) in enumerate(filtered_pool.head(5).iterrows(), 1):
            print(f"   {i}. {row['symbol']} {row['name']} - 分数: {row['weighted_score']:.1f}")

        # 生成报告
        report = filter.generate_report(filtered_pool)
        report_file = "data/stock_pool/filter_report.md"
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n   报告已保存: {report_file}")
    else:
        print("   未筛选出任何股票")

    print("\n" + "=" * 50)
    print("股票池筛选系统测试完成")
    print("下一步:")
    print("1. 调整筛选规则配置")
    print("2. 扩大测试范围")
    print("3. 集成到交易系统")


if __name__ == "__main__":
    main()
