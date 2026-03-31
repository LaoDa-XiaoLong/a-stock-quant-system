#!/usr/bin/env python3
"""
分析数据质量评估失效问题
问题：明显错误的数据却得到100分质量评分
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.data_quality_validator import DataQualityValidator

def test_problematic_data():
    """测试有问题的数据"""
    print("=" * 70)
    print("数据质量评估失效问题分析")
    print("=" * 70)
    
    validator = DataQualityValidator()
    
    # 问题1：利润为0或-0的情况
    print("\n1. 测试利润为0或-0的情况:")
    problematic_data_1 = {
        'report_type': '年报',
        'report_date': '2026-03-30',
        'revenue_yoy': 0.15,      # 15%增长
        'profit_yoy': 0.0,        # 利润增长0%（问题！）
        'gross_margin': 0.25,
        'net_margin': 0.08,
        'debt_ratio': 0.45
    }
    
    result1 = validator.validate_financial_data('000001', '测试股票1', problematic_data_1)
    print(f"   数据: 利润增长0%")
    print(f"   质量分数: {result1['overall_score']:.1f}")
    print(f"   是否合理: {result1['is_reasonable']}")
    print(f"   警告数量: {len(result1['warnings'])}")
    print(f"   错误数量: {len(result1['errors'])}")
    
    # 问题2：利润为负但营收大幅增长（不合理）
    print("\n2. 测试利润为负但营收大幅增长:")
    problematic_data_2 = {
        'report_type': '年报',
        'report_date': '2026-03-30',
        'revenue_yoy': 3.0,       # 300%增长（异常）
        'profit_yoy': -0.5,       # -50%利润（问题）
        'gross_margin': 0.85,     # 85%毛利率（过高）
        'net_margin': -0.1,       # -10%净利率
        'debt_ratio': 0.15
    }
    
    result2 = validator.validate_financial_data('000002', '测试股票2', problematic_data_2)
    print(f"   数据: 营收+300%，利润-50%")
    print(f"   质量分数: {result2['overall_score']:.1f}")
    print(f"   是否合理: {result2['is_reasonable']}")
    print(f"   警告数量: {len(result2['warnings'])}")
    print(f"   错误数量: {len(result2['errors'])}")
    
    # 问题3：极端不一致的数据
    print("\n3. 测试极端不一致数据:")
    problematic_data_3 = {
        'report_type': '季报',
        'report_date': '2026-03-30',
        'revenue_yoy': 34.813,    # 3481.3%增长（昨天的问题）
        'profit_yoy': 16.047,     # 1604.7%增长
        'gross_margin': 0.85,
        'net_margin': 0.65,
        'debt_ratio': 0.15
    }
    
    result3 = validator.validate_financial_data('002352', '顺丰控股', problematic_data_3)
    print(f"   数据: 营收+3481%，利润+1605%")
    print(f"   质量分数: {result3['overall_score']:.1f}")
    print(f"   是否合理: {result3['is_reasonable']}")
    print(f"   警告数量: {len(result3['warnings'])}")
    print(f"   错误数量: {len(result3['errors'])}")
    
    # 显示详细验证结果
    print("\n" + "=" * 70)
    print("详细验证结果分析:")
    print("=" * 70)
    
    for i, (data, result) in enumerate([
        (problematic_data_1, result1),
        (problematic_data_2, result2),
        (problematic_data_3, result3)
    ], 1):
        print(f"\n测试用例 {i}:")
        print(f"  营收增长: {data['revenue_yoy']:.1%}")
        print(f"  利润增长: {data['profit_yoy']:.1%}")
        print(f"  毛利率: {data['gross_margin']:.1%}")
        print(f"  净利率: {data['net_margin']:.1%}")
        print(f"  质量分数: {result['overall_score']:.1f}")
        
        if result['warnings']:
            print(f"  警告:")
            for warning in result['warnings'][:3]:
                print(f"    - {warning}")
        
        if result['errors']:
            print(f"  错误:")
            for error in result['errors'][:3]:
                print(f"    - {error}")
        
        # 检查验证详情
        details = result.get('details', {})
        if details:
            print(f"  验证详情:")
            for category, detail in details.items():
                if isinstance(detail, dict) and 'score' in detail:
                    print(f"    {category}: {detail['score']}")
    
    # 分析问题根源
    print("\n" + "=" * 70)
    print("问题根源分析:")
    print("=" * 70)
    
    print("\n1. 当前验证器的问题:")
    print("   - 利润为0的情况没有特别检查")
    print("   - 营收和利润增长不一致性检查不够严格")
    print("   - 极端值检查阈值可能过高")
    print("   - 数据一致性检查逻辑有缺陷")
    
    print("\n2. 具体缺陷:")
    print("   - _check_consistency() 方法只检查营收增长>10%且利润<-30%的情况")
    print("   - 没有检查利润为0或接近0的情况")
    print("   - 没有检查营收和利润增长方向相反的情况")
    print("   - 极端值检查只关注绝对值，没有关注相对关系")
    
    print("\n3. 修复建议:")
    print("   - 添加利润为0或负值的专门检查")
    print("   - 加强营收和利润一致性的检查")
    print("   - 添加营收和利润增长方向相反的检查")
    print("   - 降低极端值检查的阈值")
    print("   - 添加数据逻辑一致性检查")

def analyze_scoring_algorithm():
    """分析评分算法"""
    print("\n" + "=" * 70)
    print("评分算法分析:")
    print("=" * 70)
    
    # 从验证器代码中提取评分权重
    print("\n当前评分权重:")
    print("  1. 完整性检查: 30%")
    print("  2. 合理性检查: 40%")
    print("  3. 一致性检查: 20%")
    print("  4. 极端值检查: 10%")
    
    print("\n问题:")
    print("  1. 完整性权重过高（30%），可能导致数据完整但明显错误的情况也能得高分")
    print("  2. 一致性检查不够严格，只检查特定情况")
    print("  3. 极端值检查权重过低（10%），且阈值设置不合理")
    print("  4. 没有专门检查利润为0或负值的情况")
    
    print("\n改进建议:")
    print("  1. 调整权重：完整性25%，合理性35%，一致性25%，极端值15%")
    print("  2. 加强一致性检查逻辑")
    print("  3. 添加利润质量专项检查")
    print("  4. 降低极端值检查阈值")

def create_fixed_validator():
    """创建修复后的验证器"""
    print("\n" + "=" * 70)
    print("修复方案:")
    print("=" * 70)
    
    fixed_code = '''
class FixedDataQualityValidator(DataQualityValidator):
    """修复版数据质量验证器"""
    
    def _check_consistency(self, data: Dict) -> float:
        """加强版数据一致性检查"""
        score = 100
        
        # 检查营收和利润的一致性
        if 'revenue_yoy' in data and 'profit_yoy' in data:
            revenue_growth = data['revenue_yoy']
            profit_growth = data['profit_yoy']
            
            # 1. 营收增长但利润大幅下降（增收不增利）
            if revenue_growth > 0.1 and profit_growth < -0.1:
                score -= 25
            
            # 2. 营收下降但利润大幅增长（可能有问题）
            elif revenue_growth < -0.1 and profit_growth > 0.2:
                score -= 20
            
            # 3. 营收和利润增长方向相反
            elif revenue_growth * profit_growth < 0:
                score -= 15
            
            # 4. 利润为0或接近0（特殊情况）
            if abs(profit_growth) < 0.01:  # 增长小于1%
                score -= 10
        
        # 检查毛利率和净利率的一致性
        if 'gross_margin' in data and 'net_margin' in data:
            gross_margin = data['gross_margin']
            net_margin = data['net_margin']
            
            # 净利率不应超过毛利率
            if net_margin > gross_margin:
                score -= 30
            
            # 净利率通常远低于毛利率
            elif net_margin > gross_margin * 0.7:  # 降低阈值
                score -= 15
            
            # 净利率为负但毛利率为正（可能有问题）
            elif net_margin < 0 and gross_margin > 0.1:
                score -= 20
        
        return max(0, score)
    
    def _check_extreme_values(self, data: Dict) -> Dict:
        """加强版极端值检查"""
        results = {
            'penalty': 0,
            'extreme_values': [],
            'warnings': [],
            'errors': []
        }
        
        # 降低阈值
        extreme_thresholds = {
            'revenue_yoy': 2.0,      # 降低到200%增长
            'profit_yoy': 3.0,       # 降低到300%增长
            'revenue_amount': 5000,  # 降低到5000亿元
            'profit_amount': 500,    # 降低到500亿元
        }
        
        for field, threshold in extreme_thresholds.items():
            if field in data and data[field] is not None:
                value = data[field]
                
                if abs(value) > threshold:
                    results['penalty'] += 25  # 增加惩罚
                    results['extreme_values'].append({
                        'field': field,
                        'value': value,
                        'threshold': threshold
                    })
                    
                    if field.endswith('_yoy'):
                        results['errors'].append(  # 改为错误
                            f"{field}增长异常: {value:.1%} (阈值: {threshold:.1%})"
                        )
                    else:
                        results['errors'].append(
                            f"{field}数值异常: {value:,.0f} (阈值: {threshold:,.0f})"
                        )
        
        return results
    
    def validate_financial_data(self, stock_code: str, stock_name: str,
                               financial_data: Dict) -> Dict:
        """修复版验证方法"""
        result = super().validate_financial_data(stock_code, stock_name, financial_data)
        
        # 添加专项检查
        special_checks = self._perform_special_checks(financial_data)
        
        # 更新分数
        result['overall_score'] = max(0, result['overall_score'] - special_checks['penalty'])
        
        # 更新警告和错误
        result['warnings'].extend(special_checks['warnings'])
        result['errors'].extend(special_checks['errors'])
        
        # 更新合理性判断
        if result['overall_score'] < 75:
            result['is_reasonable'] = False
        
        return result
    
    def _perform_special_checks(self, data: Dict) -> Dict:
        """专项检查"""
        results = {
            'penalty': 0,
            'warnings': [],
            'errors': []
        }
        
        # 检查利润质量
        if 'profit_yoy' in data:
            profit_growth = data['profit_yoy']
            
            # 利润为0或接近0
            if abs(profit_growth) < 0.01:
                results['penalty'] += 15
                results['errors'].append("利润增长接近0%，需要特别关注")
            
            # 利润为负但营收大幅增长
            if profit_growth < 0 and data.get('revenue_yoy', 0) > 0.5:
                results['penalty'] += 20
                results['errors'].append("营收大幅增长但利润为负，可能存在成本问题")
        
        return results
'''
    
    print("\n修复后的验证器代码已生成")
    print("主要改进:")
    print("  1. 加强一致性检查逻辑")
    print("  2. 降低极端值检查阈值")
    print("  3. 添加利润质量专项检查")
    print("  4. 增加惩罚力度")
    
    return fixed_code

if __name__ == "__main__":
    test_problematic_data()
    analyze_scoring_algorithm()
    fixed_code = create_fixed_validator()
    
    # 保存修复方案
    with open("data_quality_fix.py", "w", encoding="utf-8") as f:
        f.write(fixed_code)
    
    print("\n" + "=" * 70)
    print("修复方案已保存到: data_quality_fix.py")
    print("=" * 70)