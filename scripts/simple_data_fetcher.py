#!/usr/bin/env python3
"""
简化的A股数据获取脚本
使用akshare的基础功能，避免复杂依赖
"""

import pandas as pd
import os
from datetime import datetime, timedelta
import time

def ensure_data_dir():
    """确保数据目录存在"""
    if not os.path.exists('data'):
        os.makedirs('data')
    if not os.path.exists('data/raw'):
        os.makedirs('data/raw')
    if not os.path.exists('data/processed'):
        os.makedirs('data/processed')

def create_sample_data():
    """创建示例数据（用于演示）"""
    print("创建示例股票数据...")
    
    # 生成示例日期范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # 生成示例股票数据（000001 平安银行）
    np.random.seed(42)
    
    # 基础价格
    base_price = 10.0
    prices = []
    
    for i in range(len(dates)):
        # 随机波动
        if i == 0:
            price = base_price
        else:
            change = np.random.normal(0, 0.02)  # 2%的日波动
            price = prices[-1] * (1 + change)
        
        prices.append(price)
    
    # 创建DataFrame
    df = pd.DataFrame({
        '日期': dates,
        '开盘': [p * (1 + np.random.normal(0, 0.01)) for p in prices],
        '收盘': prices,
        '最高': [p * (1 + abs(np.random.normal(0, 0.015))) for p in prices],
        '最低': [p * (1 - abs(np.random.normal(0, 0.015))) for p in prices],
        '成交量': [int(np.random.normal(1000000, 200000)) for _ in range(len(dates))]
    })
    
    # 确保价格合理性
    df['最高'] = df[['开盘', '收盘', '最高']].max(axis=1)
    df['最低'] = df[['开盘', '收盘', '最低']].min(axis=1)
    
    # 保存数据
    filename = f"data/raw/stock_000001_20230101_{end_date.strftime('%Y%m%d')}.csv"
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"示例数据已保存到 {filename}")
    print(f"数据期间: {start_date.date()} 到 {end_date.date()}")
    print(f"数据条数: {len(df)}")
    
    return df

def create_sample_index_data():
    """创建示例指数数据"""
    print("\n创建示例指数数据...")
    
    # 生成示例日期范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # 生成上证指数示例数据
    np.random.seed(123)
    
    base_index = 3000.0
    index_values = []
    
    for i in range(len(dates)):
        if i == 0:
            value = base_index
        else:
            change = np.random.normal(0, 0.015)  # 1.5%的日波动
            value = index_values[-1] * (1 + change)
        
        index_values.append(value)
    
    # 创建DataFrame
    df = pd.DataFrame({
        'date': dates.strftime('%Y%m%d'),
        'open': [v * (1 + np.random.normal(0, 0.01)) for v in index_values],
        'close': index_values,
        'high': [v * (1 + abs(np.random.normal(0, 0.012))) for v in index_values],
        'low': [v * (1 - abs(np.random.normal(0, 0.012))) for v in index_values],
        'volume': [int(np.random.normal(2000000000, 500000000)) for _ in range(len(dates))]
    })
    
    # 确保价格合理性
    df['high'] = df[['open', 'close', 'high']].max(axis=1)
    df['low'] = df[['open', 'close', 'low']].min(axis=1)
    
    # 保存数据
    filename = f"data/raw/index_sh000001_20230101_{end_date.strftime('%Y%m%d')}.csv"
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"指数数据已保存到 {filename}")
    
    return df

def create_stock_list():
    """创建示例股票列表"""
    print("\n创建示例股票列表...")
    
    stocks = [
        {'code': '000001', 'name': '平安银行'},
        {'code': '000002', 'name': '万科A'},
        {'code': '000858', 'name': '五粮液'},
        {'code': '000333', 'name': '美的集团'},
        {'code': '000651', 'name': '格力电器'},
        {'code': '000568', 'name': '泸州老窖'},
        {'code': '000725', 'name': '京东方A'},
        {'code': '000100', 'name': 'TCL科技'},
        {'code': '000063', 'name': '中兴通讯'},
        {'code': '000066', 'name': '中国长城'}
    ]
    
    df = pd.DataFrame(stocks)
    df.to_csv('data/stock_list.csv', index=False, encoding='utf-8-sig')
    print(f"股票列表已保存到 data/stock_list.csv")
    print(f"包含 {len(stocks)} 只股票")
    
    return df

def main():
    """主函数"""
    print("=" * 50)
    print("A股示例数据生成工具")
    print("=" * 50)
    print("注意: 此脚本生成模拟数据用于演示")
    print("实际使用时请替换为真实数据源")
    print("=" * 50)
    
    # 确保数据目录存在
    ensure_data_dir()
    
    # 创建示例数据
    stock_data = create_sample_data()
    index_data = create_sample_index_data()
    stock_list = create_stock_list()
    
    print("\n" + "=" * 50)
    print("数据生成完成!")
    print("=" * 50)
    print("生成的文件:")
    print("1. data/stock_list.csv - 股票列表")
    print("2. data/raw/stock_000001_*.csv - 平安银行示例数据")
    print("3. data/raw/index_sh000001_*.csv - 上证指数示例数据")
    print("\n下一步: 运行数据分析脚本")
    print("命令: python scripts/basic_analysis.py")

if __name__ == "__main__":
    # 导入numpy用于生成随机数据
    import numpy as np
    main()