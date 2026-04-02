#!/usr/bin/env python3
"""
简单的股票数据测试脚本
"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime

def test_stock_functions():
    """测试股票数据函数"""
    print("🔍 测试akshare股票数据函数...")

    # 测试不同的股票数据获取方法
    test_cases = [
        ("获取A股实时数据", lambda: ak.stock_zh_a_spot()),
        ("获取A股列表", lambda: ak.stock_info_a_code_name()),
        ("获取上证指数", lambda: ak.stock_zh_index_daily(symbol="sh000001")),
        ("获取深证成指", lambda: ak.stock_zh_index_daily(symbol="sz399001")),
        ("获取创业板指", lambda: ak.stock_zh_index_daily(symbol="sz399006")),
    ]

    results = []
    for name, func in test_cases:
        print(f"\n📊 测试: {name}")
        try:
            data = func()
            if data is not None and not data.empty:
                print(f"  ✅ 成功，获取到 {len(data)} 条记录")
                print(f"     列名: {data.columns.tolist()[:5]}...")
                results.append((name, True, len(data)))
            else:
                print(f"  ⚠️ 获取到空数据")
                results.append((name, False, 0))
        except AttributeError as e:
            print(f"  ❌ 函数不存在: {e}")
            results.append((name, False, 0))
        except Exception as e:
            print(f"  ❌ 执行错误: {str(e)[:100]}")
            results.append((name, False, 0))

    return results

def explore_available_functions():
    """探索可用的函数"""
    print("\n🔍 探索akshare可用函数...")

    # 获取所有函数
    all_funcs = dir(ak)

    # 筛选股票相关函数
    stock_keywords = ['stock', 'zh_a', 'index', 'market', 'quote']
    stock_funcs = []

    for func_name in all_funcs:
        if any(keyword in func_name.lower() for keyword in stock_keywords):
            stock_funcs.append(func_name)

    print(f"找到 {len(stock_funcs)} 个股票相关函数")

    # 分组显示
    categories = {
        '实时数据': [f for f in stock_funcs if 'spot' in f.lower() or 'real' in f.lower()],
        '历史数据': [f for f in stock_funcs if 'hist' in f.lower() or 'daily' in f.lower()],
        '指数数据': [f for f in stock_funcs if 'index' in f.lower()],
        '基本信息': [f for f in stock_funcs if 'info' in f.lower() or 'list' in f.lower()],
        '资金流向': [f for f in stock_funcs if 'flow' in f.lower() or 'money' in f.lower()],
    }

    for category, funcs in categories.items():
        if funcs:
            print(f"\n📋 {category} ({len(funcs)}个):")
            for i, func in enumerate(funcs[:10]):  # 只显示前10个
                print(f"  {i+1}. {func}")
            if len(funcs) > 10:
                print(f"  ... 还有 {len(funcs)-10} 个函数")

def test_alternative_methods():
    """测试替代方法"""
    print("\n🔄 测试替代数据获取方法...")

    # 方法1: 使用stock_info_a_code_name
    print("\n方法1: 获取A股股票列表")
    try:
        stock_list = ak.stock_info_a_code_name()
        if stock_list is not None and not stock_list.empty:
            print(f"  ✅ 成功获取 {len(stock_list)} 只股票")
            print(f"     示例: {stock_list.head(3).to_dict('records')}")

            # 保存示例
            stock_list.head(10).to_csv('data/test_stock_list.csv', index=False, encoding='utf-8-sig')
            print(f"  💾 已保存前10只股票到 data/test_stock_list.csv")
        else:
            print("  ❌ 获取失败")
    except Exception as e:
        print(f"  ❌ 错误: {e}")

    # 方法2: 使用stock_zh_index_daily
    print("\n方法2: 获取指数数据")
    try:
        index_data = ak.stock_zh_index_daily(symbol="sh000001")
        if index_data is not None and not index_data.empty:
            print(f"  ✅ 成功获取上证指数 {len(index_data)} 条记录")
            print(f"     最新数据: {index_data.iloc[-1].to_dict()}")

            # 保存示例
            index_data.tail(10).to_csv('data/test_index_data.csv', index=False, encoding='utf-8-sig')
            print(f"  💾 已保存最近10条数据到 data/test_index_data.csv")
        else:
            print("  ❌ 获取失败")
    except Exception as e:
        print(f"  ❌ 错误: {e}")

    # 方法3: 尝试其他数据源
    print("\n方法3: 尝试其他数据源")
    try:
        # 尝试获取港股数据
        hk_data = ak.stock_hk_spot()
        if hk_data is not None and not hk_data.empty:
            print(f"  ✅ 成功获取港股数据 {len(hk_data)} 条记录")
        else:
            print("  ⚠️ 港股数据获取失败，尝试其他方法")
    except Exception as e:
        print(f"  ⚠️ 港股数据错误: {e}")

def main():
    """主函数"""
    print("=" * 70)
    print("📈 股票数据获取测试")
    print("=" * 70)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"akshare版本: {ak.__version__}")
    print()

    # 创建数据目录
    import os
    os.makedirs('data', exist_ok=True)

    # 测试基本函数
    results = test_stock_functions()

    # 探索可用函数
    explore_available_functions()

    # 测试替代方法
    test_alternative_methods()

    # 总结
    print("\n" + "=" * 70)
    print("📊 测试总结")
    print("=" * 70)

    success_count = sum(1 for _, success, _ in results if success)
    total_count = len(results)

    print(f"测试用例: {total_count} 个")
    print(f"成功: {success_count} 个")
    print(f"失败: {total_count - success_count} 个")

    if success_count > 0:
        print("\n✅ 部分功能可用，可以继续开发")
        print("建议:")
        print("1. 使用 stock_info_a_code_name() 获取股票列表")
        print("2. 使用 stock_zh_index_daily() 获取指数数据")
        print("3. 探索其他可用的股票数据函数")
    else:
        print("\n❌ 所有测试都失败，需要检查akshare安装或网络连接")
        print("建议:")
        print("1. 更新akshare: pip install akshare --upgrade")
        print("2. 检查网络连接")
        print("3. 查看akshare官方文档")

    print(f"\n📝 测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
