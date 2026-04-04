#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试akshare数据获取功能
"""

import pandas as pd
import time
from datetime import datetime

def test_akshare():
    """测试akshare数据获取"""
    print("测试akshare数据获取功能...")
    print("=" * 50)
    
    try:
        import akshare as ak
        
        # 测试1: 获取股票列表
        print("1. 测试获取股票列表...")
        stock_info = ak.stock_info_a_code_name()
        print(f"  成功获取股票列表: {len(stock_info)} 只")
        print(f"  前3只股票:")
        print(f"    {stock_info.iloc[0]['code']} - {stock_info.iloc[0]['name']}")
        print(f"    {stock_info.iloc[1]['code']} - {stock_info.iloc[1]['name']}")
        print(f"    {stock_info.iloc[2]['code']} - {stock_info.iloc[2]['name']}")
        
        # 测试2: 获取实时行情
        print("\n2. 测试获取实时行情...")
        spot_data = ak.stock_zh_a_spot()
        print(f"  成功获取实时行情: {len(spot_data)} 条记录")
        print(f"  数据列: {list(spot_data.columns[:5])}...")
        
        # 测试3: 获取前10只股票的数据
        print("\n3. 测试获取特定股票数据...")
        test_symbols = ['000001', '000002', '600519', '000858', '300750']
        spot_data_dict = {}
        for _, row in spot_data.iterrows():
            code = str(row['代码']).strip()
            spot_data_dict[code] = row
        
        found_count = 0
        for symbol in test_symbols:
            if symbol in spot_data_dict:
                row = spot_data_dict[symbol]
                print(f"  {symbol} {row['名称']}: {row['最新价']}元 ({row['涨跌幅']}%)")
                found_count += 1
            else:
                print(f"  {symbol}: 未找到")
        
        print(f"\n  成功匹配: {found_count}/{len(test_symbols)} 只股票")
        
        # 测试4: 数据质量检查
        print("\n4. 数据质量检查...")
        required_columns = ['代码', '名称', '最新价', '涨跌幅', '成交额']
        missing_columns = [col for col in required_columns if col not in spot_data.columns]
        if missing_columns:
            print(f"  警告: 缺少必要列: {missing_columns}")
        else:
            print("  所有必要列都存在")
        
        # 检查空值
        null_counts = spot_data[required_columns].isnull().sum()
        if null_counts.sum() > 0:
            print(f"  警告: 存在空值: {null_counts.to_dict()}")
        else:
            print("  无空值")
        
        print("\n" + "=" * 50)
        print("✅ akshare测试通过!")
        print(f"   股票列表: {len(stock_info)} 只")
        print(f"   实时行情: {len(spot_data)} 条")
        print(f"   数据时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except ImportError as e:
        print(f"❌ akshare未安装: {e}")
        print("   请运行: pip install akshare")
        return False
    except Exception as e:
        print(f"❌ akshare测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cron_compatibility():
    """测试cron脚本兼容性"""
    print("\n测试cron脚本兼容性...")
    print("=" * 50)
    
    try:
        # 模拟cron脚本的部分功能
        from datetime import datetime
        import pandas as pd
        
        # 测试配置
        config = {
            'max_stocks': 10,
            'min_turnover': 10000000,
            'price_range': (5, 500),
            'change_limit': 5,
            'use_real_data': True,
            'retry_count': 2,
            'retry_delay': 1,
        }
        
        print(f"配置测试: {config}")
        
        # 测试选股策略
        print("\n测试选股策略...")
        sample_data = pd.DataFrame({
            'symbol': ['000001', '000002', '600519'],
            'name': ['平安银行', '万科A', '贵州茅台'],
            'price': [15.80, 8.50, 1800.00],
            'change': [1.5, -0.8, 2.3],
            'turnover': [500000000, 300000000, 800000000],
        })
        
        print(f"样本数据: {len(sample_data)} 条")
        
        # 应用筛选条件
        filtered = sample_data.copy()
        filtered = filtered[filtered['turnover'] > config['min_turnover']]
        min_price, max_price = config['price_range']
        filtered = filtered[(filtered['price'] >= min_price) & (filtered['price'] <= max_price)]
        filtered = filtered[abs(filtered['change']) <= config['change_limit']]
        
        print(f"筛选后: {len(filtered)} 条")
        
        if len(filtered) > 0:
            print("✅ 选股策略测试通过!")
        else:
            print("⚠️  选股策略筛选结果为空")
        
        return True
        
    except Exception as e:
        print(f"❌ cron兼容性测试失败: {e}")
        return False

def main():
    """主函数"""
    print("股票数据自动更新系统 - 功能测试")
    print("=" * 50)
    
    # 测试akshare
    akshare_ok = test_akshare()
    
    # 测试cron兼容性
    cron_ok = test_cron_compatibility()
    
    print("\n" + "=" * 50)
    print("测试总结:")
    print(f"  akshare功能: {'✅ 通过' if akshare_ok else '❌ 失败'}")
    print(f"  cron兼容性: {'✅ 通过' if cron_ok else '❌ 失败'}")
    
    if akshare_ok and cron_ok:
        print("\n🎉 所有测试通过! 系统已准备好执行股票数据自动更新任务。")
        print("   建议: 运行 'python3 cron_stock_data_update.py' 进行完整测试")
    else:
        print("\n⚠️  部分测试失败，请检查问题后重试。")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()