#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试股票数据自动更新功能
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stock_data_updater_v1 import StockDataUpdater
import pandas as pd
from datetime import datetime

def test_basic_functionality():
    """测试基本功能"""
    print("测试股票数据自动更新系统基本功能")
    print("=" * 60)
    
    # 创建更新器
    updater = StockDataUpdater()
    
    print("1. 测试获取A股列表...")
    all_stocks = updater.get_all_a_shares()
    print(f"   获取到 {len(all_stocks)} 只A股股票")
    
    if len(all_stocks) > 0:
        print(f"   示例股票: {all_stocks['symbol'].iloc[0]} {all_stocks['name'].iloc[0]}")
    
    print("\n2. 测试获取实时数据...")
    test_symbols = ['000001', '000002', '300750']  # 平安银行, 万科A, 宁德时代
    
    for symbol in test_symbols:
        realtime_data = updater.get_stock_real_time_data(symbol)
        if realtime_data:
            print(f"   {symbol}: {realtime_data.get('name', 'N/A')} - "
                  f"价格: {realtime_data.get('price', 0):.2f} - "
                  f"涨跌: {realtime_data.get('change', 0):.2f}%")
        else:
            print(f"   {symbol}: 获取失败")
    
    print("\n3. 测试批量更新（样本模式）...")
    sample_symbols = test_symbols  # 只测试3只股票
    updated_data = updater.update_stock_data_batch(sample_symbols)
    print(f"   成功更新 {len(updated_data)} 只股票数据")
    
    if not updated_data.empty:
        print("\n   更新数据示例:")
        for _, row in updated_data.head(3).iterrows():
            print(f"   - {row['symbol']} {row.get('name', 'N/A')}: "
                  f"价格{row.get('price', 0):.2f}, "
                  f"成交额{row.get('turnover', 0)/1e8:.2f}亿")
    
    print("\n4. 测试选股策略...")
    if not updated_data.empty:
        filtered_stocks = updater.apply_stock_selection_strategy(updated_data)
        print(f"   原始数据: {len(updated_data)} 只")
        print(f"   筛选后: {len(filtered_stocks)} 只")
        
        if not filtered_stocks.empty:
            print("\n   筛选结果:")
            for _, row in filtered_stocks.iterrows():
                print(f"   - {row['symbol']} {row.get('name', 'N/A')}: "
                      f"评分{row.get('composite_score', 0):.1f}")
    
    print("\n5. 测试报告生成...")
    if not updated_data.empty:
        report = updater.generate_update_report(updated_data, filtered_stocks if 'filtered_stocks' in locals() else pd.DataFrame())
        print(f"   报告长度: {len(report)} 字符")
        print(f"   报告已保存到 data/stock_pool/ 目录")
    
    print("\n" + "=" * 60)
    print("基本功能测试完成")

def test_full_update_sample():
    """测试完整更新流程（样本模式）"""
    print("测试完整更新流程（样本模式）")
    print("=" * 60)
    
    updater = StockDataUpdater()
    
    # 运行样本模式更新
    success = updater.run_full_update(sample_mode=True, max_stocks=10)
    
    if success:
        print("\n✅ 样本更新成功!")
        
        # 检查生成的文件
        import glob
        report_files = glob.glob("data/stock_pool/update_report_*.md")
        if report_files:
            print(f"   生成报告: {report_files[-1]}")
        
        data_files = glob.glob("data/stock_list_latest.csv")
        if data_files:
            print(f"   数据文件: {data_files[0]}")
    else:
        print("\n❌ 样本更新失败!")
    
    print("\n" + "=" * 60)

def check_dependencies():
    """检查依赖包"""
    print("检查Python依赖包...")
    
    required_packages = ['pandas', 'numpy', 'akshare']
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} 未安装")
            print(f"     安装命令: pip install {package}")
    
    print()

def main():
    """主测试函数"""
    print("股票数据自动更新系统测试套件")
    print("=" * 60)
    
    # 检查依赖
    check_dependencies()
    
    # 创建必要的目录
    os.makedirs("data/stock_pool", exist_ok=True)
    os.makedirs("data/raw", exist_ok=True)
    
    # 运行测试
    try:
        test_basic_functionality()
        print("\n\n")
        test_full_update_sample()
        
        print("\n✅ 所有测试完成!")
        print("\n使用说明:")
        print("  1. 完整更新: python stock_data_updater_v1.py")
        print("  2. 样本更新: python stock_data_updater_v1.py --sample --max-stocks 50")
        print("  3. 指定配置: python stock_data_updater_v1.py --config config/stock_pool_config.json")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()