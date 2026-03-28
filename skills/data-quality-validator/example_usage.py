#!/usr/bin/env python3
"""
数据质量验证器使用示例
"""

import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_quality_validator import DataQualityValidator

def example_basic_validation():
    """基础验证示例"""
    print("=" * 60)
    print("数据质量验证器 - 基础验证示例")
    print("=" * 60)
    
    # 创建验证器
    validator = DataQualityValidator()
    
    # 测试用例1：合理数据
    print("\n1. 测试合理数据:")
    reasonable_data = {
        'report_type': '年报',
        'report_date': '2026-03-27',
        'revenue_yoy': 0.15,      # 15%增长
        'profit_yoy': 0.12,       # 12%增长
        'gross_margin': 0.25,     # 25%毛利率
        'net_margin': 0.08,       # 8%净利率
        'debt_ratio': 0.45        # 45%负债率
    }
    
    result = validator.validate_financial_data('000001', '平安银行', reasonable_data)
    print(f"   股票: {result['stock_code']} {result['stock_name']}")
    print(f"   质量分数: {result['overall_score']:.1f}")
    print(f"   是否合理: {result['is_reasonable']}")
    print(f"   警告数量: {len(result['warnings'])}")
    
    # 测试用例2：夸张数据（会被拒绝）
    print("\n2. 测试夸张数据（类似昨天的问题）:")
    extreme_data = {
        'report_type': '季报',
        'report_date': '2026-03-28',
        'revenue_yoy': 34.813,    # 3481.3%增长（夸张！）
        'profit_yoy': 16.047,     # 1604.7%增长（夸张！）
        'gross_margin': 0.85,     # 85%毛利率（过高）
        'net_margin': 0.65,       # 65%净利率（过高）
        'debt_ratio': 0.15        # 15%负债率（过低）
    }
    
    result = validator.validate_financial_data('002352', '顺丰控股', extreme_data)
    print(f"   股票: {result['stock_code']} {result['stock_name']}")
    print(f"   质量分数: {result['overall_score']:.1f}")
    print(f"   是否合理: {result['is_reasonable']}")
    print(f"   错误数量: {len(result['errors'])}")
    
    if result['errors']:
        print(f"   第一个错误: {result['errors'][0]}")
    
    return result

def example_multi_source_comparison():
    """多源比对示例"""
    print("\n" + "=" * 60)
    print("数据质量验证器 - 多源比对示例")
    print("=" * 60)
    
    validator = DataQualityValidator()
    
    # 多源数据比对
    comparison = validator.compare_multiple_sources('002352', '顺丰控股')
    
    print(f"\n股票: {comparison['stock_code']} {comparison['stock_name']}")
    print(f"数据源数量: {len(comparison['sources'])}")
    print(f"推荐数据源: {comparison['recommended_source']}")
    print(f"发现差异: {len(comparison['discrepancies'])} 处")
    
    # 显示共识值
    print("\n共识值:")
    for field, value in comparison['consensus'].items():
        if field.endswith('_yoy'):
            print(f"  {field}: {value:.1%}")
        else:
            print(f"  {field}: {value:.3f}")
    
    return comparison

def example_integration():
    """集成示例"""
    print("\n" + "=" * 60)
    print("数据质量验证器 - 集成示例")
    print("=" * 60)
    
    # 模拟一个财务监控系统
    class SimpleFinancialMonitor:
        def __init__(self):
            self.validator = DataQualityValidator()
            self.data_quality_threshold = 75.0  # 75分阈值
        
        def analyze_stock(self, stock_code, stock_name, financial_data):
            """分析股票，包含数据质量检查"""
            print(f"\n分析股票: {stock_code} {stock_name}")
            
            # 验证数据质量
            validation = self.validator.validate_financial_data(
                stock_code, stock_name, financial_data
            )
            
            # 检查数据质量阈值
            if validation['overall_score'] < self.data_quality_threshold:
                print(f"  ❌ 数据质量不合格: {validation['overall_score']:.1f} < {self.data_quality_threshold}")
                if validation['errors']:
                    print(f"     错误: {validation['errors'][0]}")
                return None
            
            print(f"  ✅ 数据质量合格: {validation['overall_score']:.1f}")
            
            # 这里可以继续其他分析逻辑
            # ...
            
            return validation
    
    # 测试集成
    monitor = SimpleFinancialMonitor()
    
    # 测试数据
    test_data = {
        'report_type': '年报',
        'report_date': '2026-03-27',
        'revenue_yoy': 0.25,
        'profit_yoy': 0.20,
        'gross_margin': 0.30,
        'net_margin': 0.12
    }
    
    result = monitor.analyze_stock('000001', '平安银行', test_data)
    
    if result:
        print(f"\n分析完成，数据质量分数: {result['overall_score']:.1f}")
    
    return monitor

def main():
    """主函数"""
    print("数据质量验证器使用示例")
    print("版本: 1.0.0")
    print("数据质量阈值: 75分（根据老大要求）")
    print("=" * 60)
    
    # 运行示例
    example_basic_validation()
    example_multi_source_comparison()
    example_integration()
    
    print("\n" + "=" * 60)
    print("示例运行完成")
    print("=" * 60)
    print("\n使用说明:")
    print("1. 将 data_quality_validator.py 复制到你的项目")
    print("2. 导入 DataQualityValidator 类")
    print("3. 在数据获取后立即进行质量验证")
    print("4. 根据验证结果决定是否使用数据")
    print("\n注意: 数据质量阈值默认为75分，可根据需要调整")

if __name__ == "__main__":
    main()