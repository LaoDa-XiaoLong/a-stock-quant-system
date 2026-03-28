#!/usr/bin/env python3
"""
A股数据获取脚本
使用akshare获取免费A股数据
"""

import akshare as ak
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

def get_stock_list():
    """获取A股股票列表"""
    print("正在获取A股股票列表...")
    try:
        # 获取沪深京A股列表
        stock_info_a_code_name_df = ak.stock_info_a_code_name()
        print(f"获取到 {len(stock_info_a_code_name_df)} 只股票")
        
        # 保存股票列表
        stock_info_a_code_name_df.to_csv('data/stock_list.csv', index=False, encoding='utf-8-sig')
        print("股票列表已保存到 data/stock_list.csv")
        
        return stock_info_a_code_name_df
    except Exception as e:
        print(f"获取股票列表失败: {e}")
        return None

def get_index_data(symbol='sh000001', start_date='20200101', end_date=None):
    """获取指数数据"""
    if end_date is None:
        end_date = datetime.now().strftime('%Y%m%d')
    
    print(f"正在获取指数数据 {symbol} ({start_date} 到 {end_date})...")
    try:
        # 获取指数日线数据
        index_df = ak.stock_zh_index_daily(symbol=symbol)
        
        # 筛选日期范围
        index_df = index_df[(index_df['date'] >= start_date) & (index_df['date'] <= end_date)]
        
        # 保存数据
        filename = f"data/raw/index_{symbol}_{start_date}_{end_date}.csv"
        index_df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"指数数据已保存到 {filename}")
        
        return index_df
    except Exception as e:
        print(f"获取指数数据失败: {e}")
        return None

def get_stock_data(symbol='000001', start_date='20200101', end_date=None):
    """获取个股数据"""
    if end_date is None:
        end_date = datetime.now().strftime('%Y%m%d')
    
    print(f"正在获取股票数据 {symbol} ({start_date} 到 {end_date})...")
    try:
        # 获取个股日线数据
        stock_df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start_date, end_date=end_date)
        
        # 保存数据
        filename = f"data/raw/stock_{symbol}_{start_date}_{end_date}.csv"
        stock_df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"股票数据已保存到 {filename}")
        
        return stock_df
    except Exception as e:
        print(f"获取股票数据失败: {e}")
        return None

def get_top_n_stocks(n=10, start_date='20230101'):
    """获取前N只股票的数据（用于演示）"""
    print(f"正在获取前{n}只股票的数据...")
    
    # 读取股票列表
    if os.path.exists('data/stock_list.csv'):
        stock_list = pd.read_csv('data/stock_list.csv')
    else:
        stock_list = get_stock_list()
        if stock_list is None:
            return
    
    # 取前N只股票
    top_stocks = stock_list.head(n)
    
    for index, row in top_stocks.iterrows():
        symbol = row['code']
        name = row['name']
        print(f"正在处理 {symbol} ({name})...")
        
        try:
            stock_data = get_stock_data(symbol=symbol, start_date=start_date)
            if stock_data is not None:
                print(f"  {symbol} 数据获取成功，共 {len(stock_data)} 条记录")
            time.sleep(1)  # 避免请求过快
        except Exception as e:
            print(f"  获取 {symbol} 数据失败: {e}")
            continue

def main():
    """主函数"""
    print("=" * 50)
    print("A股数据获取工具")
    print("=" * 50)
    
    # 确保数据目录存在
    ensure_data_dir()
    
    # 获取股票列表
    stock_list = get_stock_list()
    
    if stock_list is not None:
        # 获取上证指数数据（用于演示）
        index_data = get_index_data(symbol='sh000001', start_date='20230101')
        
        # 获取几只示例股票的数据
        get_top_n_stocks(n=5, start_date='20230101')
    
    print("\n数据获取完成！")

if __name__ == "__main__":
    main()