#!/usr/bin/env python3
"""
真实A股数据获取脚本
获取至少3年的历史数据
"""

import akshare as ak
import pandas as pd
import os
from datetime import datetime, timedelta
import time
import warnings
warnings.filterwarnings('ignore')

def ensure_data_dir():
    """确保数据目录存在"""
    directories = ['data', 'data/raw', 'data/processed', 'data/holdings']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"创建目录: {directory}")

def get_stock_list():
    """获取A股股票列表"""
    print("正在获取A股股票列表...")
    try:
        # 获取沪深京A股列表
        stock_info_a_code_name_df = ak.stock_info_a_code_name()
        print(f"获取到 {len(stock_info_a_code_name_df)} 只A股股票")
        
        # 保存股票列表
        stock_info_a_code_name_df.to_csv('data/stock_list_all.csv', index=False, encoding='utf-8-sig')
        print("股票列表已保存到 data/stock_list_all.csv")
        
        return stock_info_a_code_name_df
    except Exception as e:
        print(f"获取股票列表失败: {e}")
        return None

def get_stock_data_3years(symbol, name=None):
    """获取股票3年历史数据"""
    if name:
        print(f"\n正在获取 {symbol} ({name}) 的3年历史数据...")
    else:
        print(f"\n正在获取 {symbol} 的3年历史数据...")
    
    # 计算3年前的日期
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3*365)  # 3年
    
    start_str = start_date.strftime('%Y%m%d')
    end_str = end_date.strftime('%Y%m%d')
    
    try:
        # 尝试获取日线数据
        stock_df = ak.stock_zh_a_hist(
            symbol=symbol, 
            period="daily", 
            start_date=start_str, 
            end_date=end_str,
            adjust="qfq"  # 前复权
        )
        
        if stock_df is not None and not stock_df.empty:
            print(f"  成功获取 {len(stock_df)} 条记录")
            print(f"  数据期间: {stock_df['日期'].iloc[0]} 到 {stock_df['日期'].iloc[-1]}")
            
            # 保存数据
            filename = f"data/raw/stock_{symbol}_{start_str}_{end_str}.csv"
            stock_df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"  数据已保存到 {filename}")
            
            return stock_df
        else:
            print(f"  获取数据为空")
            return None
            
    except Exception as e:
        print(f"  获取数据失败: {e}")
        return None

def get_index_data_3years(symbol='sh000001', name='上证指数'):
    """获取指数3年历史数据"""
    print(f"\n正在获取 {name} ({symbol}) 的3年历史数据...")
    
    # 计算3年前的日期
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3*365)
    
    start_str = start_date.strftime('%Y%m%d')
    end_str = end_date.strftime('%Y%m%d')
    
    try:
        # 获取指数日线数据
        index_df = ak.stock_zh_index_daily(symbol=symbol)
        
        if index_df is not None and not index_df.empty:
            # 筛选日期范围
            index_df = index_df[(index_df['date'] >= start_str) & (index_df['date'] <= end_str)]
            
            print(f"  成功获取 {len(index_df)} 条记录")
            print(f"  数据期间: {index_df['date'].iloc[0]} 到 {index_df['date'].iloc[-1]}")
            
            # 保存数据
            filename = f"data/raw/index_{symbol}_{start_str}_{end_str}.csv"
            index_df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"  数据已保存到 {filename}")
            
            return index_df
        else:
            print(f"  获取数据为空")
            return None
            
    except Exception as e:
        print(f"  获取数据失败: {e}")
        return None

def get_holding_stocks_data():
    """获取持仓股票数据"""
    print("\n" + "="*50)
    print("获取持仓股票数据")
    print("="*50)
    
    # 老大的持仓股票
    holdings = {
        '002594': {'name': '比亚迪', 'cost': 99.0},
        '603728': {'name': '鸣志电器', 'cost': 68.0},
        '600580': {'name': '卧龙电驱', 'cost': 42.0},
        '600183': {'name': '生益科技', 'cost': 66.0},
        '603259': {'name': '药明康德', 'cost': 101.0},
        '002352': {'name': '顺丰控股', 'cost': 40.0},
        '600096': {'name': '云天化', 'cost': 37.0}
    }
    
    # 保存持仓信息
    holdings_df = pd.DataFrame([
        {'code': code, 'name': info['name'], 'cost_price': info['cost']}
        for code, info in holdings.items()
    ])
    holdings_df.to_csv('data/holdings/holding_stocks.csv', index=False, encoding='utf-8-sig')
    print("持仓信息已保存到 data/holdings/holding_stocks.csv")
    
    # 获取每只股票的数据
    holding_data = {}
    for symbol, info in holdings.items():
        print(f"\n处理持仓股票: {symbol} {info['name']} (成本价: {info['cost']}元)")
        
        data = get_stock_data_3years(symbol, info['name'])
        if data is not None:
            holding_data[symbol] = {
                'data': data,
                'name': info['name'],
                'cost': info['cost']
            }
        
        # 避免请求过快
        time.sleep(1)
    
    return holding_data

def get_market_indices():
    """获取主要市场指数数据"""
    print("\n" + "="*50)
    print("获取市场指数数据")
    print("="*50)
    
    indices = {
        'sh000001': '上证指数',
        'sz399001': '深证成指',
        'sz399006': '创业板指',
        'sh000016': '上证50',
        'sh000905': '中证500',
        'sh000300': '沪深300'
    }
    
    for symbol, name in indices.items():
        get_index_data_3years(symbol, name)
        time.sleep(0.5)

def generate_data_summary():
    """生成数据摘要报告"""
    print("\n" + "="*50)
    print("数据获取摘要")
    print("="*50)
    
    # 统计文件
    raw_files = [f for f in os.listdir('data/raw') if f.endswith('.csv')]
    holding_files = [f for f in os.listdir('data/holdings') if f.endswith('.csv')]
    
    print(f"原始数据文件: {len(raw_files)} 个")
    print(f"持仓数据文件: {len(holding_files)} 个")
    
    # 读取持仓信息
    holdings_path = 'data/holdings/holding_stocks.csv'
    if os.path.exists(holdings_path):
        holdings_df = pd.read_csv(holdings_path)
        print(f"\n持仓股票 ({len(holdings_df)} 只):")
        for _, row in holdings_df.iterrows():
            print(f"  {row['code']} {row['name']}: 成本价 {row['cost_price']}元")
    
    # 生成报告
    report = f"""
# A股数据获取报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 数据概况
- 原始数据文件: {len(raw_files)} 个
- 持仓数据文件: {len(holding_files)} 个
- 数据期间: 3年历史数据

## 持仓股票
"""
    
    if os.path.exists(holdings_path):
        holdings_df = pd.read_csv(holdings_path)
        for _, row in holdings_df.iterrows():
            report += f"- {row['code']} {row['name']}: 成本价 {row['cost_price']}元\n"
    
    report += f"""
## 数据文件
原始数据目录: data/raw/
持仓数据目录: data/holdings/

## 下一步
1. 运行数据分析脚本进行技术分析
2. 针对持仓股票制定交易策略
3. 进行策略回测和优化
"""
    
    # 保存报告
    report_file = 'reports/data_acquisition_report.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n数据摘要报告已保存到: {report_file}")

def main():
    """主函数"""
    print("=" * 60)
    print("A股真实数据获取工具 (3年历史数据)")
    print("=" * 60)
    print("注意: 此脚本将获取真实市场数据")
    print("数据源: akshare (免费接口)")
    print("=" * 60)
    
    # 确保目录存在
    ensure_data_dir()
    
    # 获取股票列表
    stock_list = get_stock_list()
    
    if stock_list is not None:
        # 获取持仓股票数据
        holding_data = get_holding_stocks_data()
        
        # 获取市场指数数据
        get_market_indices()
        
        # 生成摘要报告
        generate_data_summary()
        
        print("\n" + "=" * 60)
        print("数据获取完成!")
        print("=" * 60)
        print("\n下一步建议:")
        print("1. 查看 reports/data_acquisition_report.md")
        print("2. 运行持仓股票分析脚本")
        print("3. 进行策略开发和回测")
    else:
        print("获取股票列表失败，请检查网络连接或数据源")

if __name__ == "__main__":
    main()