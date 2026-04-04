#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试股票代码匹配逻辑
"""

def test_code_matching():
    """测试代码匹配逻辑"""
    print("测试股票代码匹配逻辑...")
    print("=" * 50)
    
    # 测试数据
    test_cases = [
        ("000001", ["000001", "sz000001"], "平安银行"),
        ("600519", ["600519", "sh600519"], "贵州茅台"),
        ("300750", ["300750", "sz300750"], "宁德时代"),
        ("430090", ["430090", "bj430090"], "北交所股票"),
        ("830799", ["830799", "bj830799"], "北交所股票"),
        ("870199", ["870199", "bj870199"], "北交所股票"),
    ]
    
    # 模拟spot_data_dict
    spot_data_dict = {
        "sz000001": {"代码": "sz000001", "名称": "平安银行", "最新价": 15.80, "涨跌幅": 1.5},
        "sh600519": {"代码": "sh600519", "名称": "贵州茅台", "最新价": 1800.00, "涨跌幅": 2.3},
        "sz300750": {"代码": "sz300750", "名称": "宁德时代", "最新价": 210.50, "涨跌幅": -0.8},
        "bj430090": {"代码": "bj430090", "名称": "北交所A", "最新价": 8.50, "涨跌幅": 0.5},
        "bj830799": {"代码": "bj830799", "名称": "北交所B", "最新价": 12.30, "涨跌幅": 1.2},
        "bj870199": {"代码": "bj870199", "名称": "北交所C", "最新价": 15.80, "涨跌幅": -0.3},
    }
    
    passed = 0
    total = len(test_cases)
    
    for symbol, possible_codes, expected_name in test_cases:
        print(f"\n测试股票代码: {symbol}")
        print(f"  可能的形式: {possible_codes}")
        print(f"  预期名称: {expected_name}")
        
        matched_row = None
        
        # 1. 直接匹配
        if symbol in spot_data_dict:
            matched_row = spot_data_dict[symbol]
        
        # 2. 如果是6位数字，尝试添加市场前缀匹配
        elif symbol.isdigit() and len(symbol) == 6:
            # 尝试深市代码 (00开头或30开头)
            if symbol.startswith('00') or symbol.startswith('30'):
                sz_code = f"sz{symbol}"
                if sz_code in spot_data_dict:
                    matched_row = spot_data_dict[sz_code]
            # 尝试沪市代码 (60开头)
            elif symbol.startswith('60'):
                sh_code = f"sh{symbol}"
                if sh_code in spot_data_dict:
                    matched_row = spot_data_dict[sh_code]
            # 尝试北交所代码 (43开头或83开头或87开头)
            elif symbol.startswith('43') or symbol.startswith('83') or symbol.startswith('87'):
                bj_code = f"bj{symbol}"
                if bj_code in spot_data_dict:
                    matched_row = spot_data_dict[bj_code]
        
        if matched_row is not None:
            actual_name = matched_row["名称"]
            if actual_name == expected_name:
                print(f"  ✅ 匹配成功: {actual_name}")
                passed += 1
            else:
                print(f"  ❌ 匹配失败: 预期'{expected_name}'，实际'{actual_name}'")
        else:
            print(f"  ❌ 未找到匹配数据")
    
    print(f"\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✅ 所有测试通过!")
    else:
        print("⚠️  部分测试失败")
    
    return passed == total

def test_real_akshare_matching():
    """测试真实akshare数据匹配"""
    print("\n\n测试真实akshare数据匹配...")
    print("=" * 50)
    
    try:
        import akshare as ak
        import pandas as pd
        
        # 获取股票列表
        print("获取股票列表...")
        stock_info = ak.stock_info_a_code_name()
        print(f"股票列表: {len(stock_info)} 只")
        
        # 获取前10只股票代码
        test_symbols = stock_info['code'].head(10).tolist()
        print(f"测试股票代码: {test_symbols}")
        
        # 获取实时行情
        print("获取实时行情...")
        spot_data = ak.stock_zh_a_spot()
        print(f"实时行情: {len(spot_data)} 条")
        
        # 构建spot_data_dict
        spot_data_dict = {}
        for _, row in spot_data.iterrows():
            code = str(row['代码']).strip()
            spot_data_dict[code] = row
        
        # 测试匹配
        matched_count = 0
        for symbol in test_symbols:
            symbol_str = str(symbol).strip()
            
            # 尝试多种匹配方式
            matched = False
            
            # 1. 直接匹配
            if symbol_str in spot_data_dict:
                matched = True
            # 2. 如果是6位数字，尝试添加市场前缀匹配
            elif symbol_str.isdigit() and len(symbol_str) == 6:
                if symbol_str.startswith('00') or symbol_str.startswith('30'):
                    sz_code = f"sz{symbol_str}"
                    if sz_code in spot_data_dict:
                        matched = True
                elif symbol_str.startswith('60'):
                    sh_code = f"sh{symbol_str}"
                    if sh_code in spot_data_dict:
                        matched = True
                elif symbol_str.startswith('43') or symbol_str.startswith('83') or symbol_str.startswith('87'):
                    bj_code = f"bj{symbol_str}"
                    if bj_code in spot_data_dict:
                        matched = True
            
            if matched:
                matched_count += 1
                print(f"  ✅ {symbol_str}: 匹配成功")
            else:
                print(f"  ❌ {symbol_str}: 匹配失败")
        
        match_rate = matched_count / len(test_symbols) * 100
        print(f"\n匹配成功率: {matched_count}/{len(test_symbols)} ({match_rate:.1f}%)")
        
        if match_rate >= 80:
            print("✅ 匹配逻辑有效!")
            return True
        else:
            print("⚠️  匹配率较低，可能需要优化")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """主函数"""
    print("股票代码匹配逻辑测试")
    print("=" * 50)
    
    # 测试基础匹配逻辑
    basic_ok = test_code_matching()
    
    # 测试真实akshare数据匹配
    real_ok = test_real_akshare_matching()
    
    print("\n" + "=" * 50)
    print("测试总结:")
    print(f"  基础匹配逻辑: {'✅ 通过' if basic_ok else '❌ 失败'}")
    print(f"  真实数据匹配: {'✅ 通过' if real_ok else '❌ 失败'}")
    
    if basic_ok and real_ok:
        print("\n🎉 所有测试通过! 代码匹配逻辑已优化完成。")
    else:
        print("\n⚠️  部分测试失败，请检查匹配逻辑。")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()