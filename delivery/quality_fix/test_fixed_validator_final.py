#!/usr/bin/env python3
"""
测试修复后的数据质量验证
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.data_quality_validator import DataQualityValidator

def test_problem_cases():
    """测试之前有问题的案例"""
    print("测试修复后的数据质量验证")
    print("=" * 60)
    
    validator = DataQualityValidator()
    
    # 案例1：利润为0（之前得100分，现在应该降低）
    print("\n1. 测试利润为0的情况（之前问题）:")
    data1 = {
        'report_type': '年报',
        'report_date': '2026-03-30',
        'revenue_yoy': 0.15,
        'profit_yoy': 0.0,
        'gross_margin': 0.25,
        'net_margin': 0.08,
        'debt_ratio': 0.45
    }
    
    result1 = validator.validate_financial_data('000001', '测试股票', data1)
    print(f"   之前分数: 100.0")
    print(f"   现在分数: {result1['overall_score']:.1f}")
    print(f"   是否合理: {result1['is_reasonable']}")
    print(f"   主要错误: {result1['errors'][0] if result1['errors'] else '无'}")
    
    # 案例2：极端数据（昨天的问题）
    print("\n2. 测试极端数据（昨天的问题）:")
    data2 = {
        'report_type': '季报',
        'report_date': '2026-03-30',
        'revenue_yoy': 34.813,
        'profit_yoy': 16.047,
        'gross_margin': 0.85,
        'net_margin': 0.65,
        'debt_ratio': 0.15
    }
    
    result2 = validator.validate_financial_data('002352', '顺丰控股', data2)
    print(f"   营收增长: {data2['revenue_yoy']:.1%}")
    print(f"   利润增长: {data2['profit_yoy']:.1%}")
    print(f"   质量分数: {result2['overall_score']:.1f}")
    print(f"   是否合理: {result2['is_reasonable']}")
    print(f"   错误数量: {len(result2['errors'])}")
    
    # 案例3：正常数据
    print("\n3. 测试正常数据:")
    data3 = {
        'report_type': '年报',
        'report_date': '2026-03-30',
        'revenue_yoy': 0.15,
        'profit_yoy': 0.12,
        'gross_margin': 0.25,
        'net_margin': 0.08,
        'debt_ratio': 0.45
    }
    
    result3 = validator.validate_financial_data('000002', '正常股票', data3)
    print(f"   质量分数: {result3['overall_score']:.1f}")
    print(f"   是否合理: {result3['is_reasonable']}")
    print(f"   警告数量: {len(result3['warnings'])}")
    print(f"   错误数量: {len(result3['errors'])}")
    
    print("\n" + "=" * 60)
    print("测试总结:")
    print(f"  修复前问题1分数: 100.0 → 修复后: {result1['overall_score']:.1f}")
    print(f"  修复前问题2分数: 56.0 → 修复后: {result2['overall_score']:.1f}")
    print(f"  正常数据分数: {result3['overall_score']:.1f} (应接近100)")
    
    if result1['overall_score'] < 100 and result2['overall_score'] < 75 and result3['overall_score'] > 90:
        print("\n✅ 修复成功！问题数据得到正确识别。")
    else:
        print("\n❌ 修复可能有问题，需要进一步检查。")

if __name__ == "__main__":
    test_problem_cases()