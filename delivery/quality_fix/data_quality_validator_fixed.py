#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据质量验证器 - 修复版
修复问题：明显错误的数据却得到100分质量评分
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import json
import os
from typing import Dict, List, Tuple, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataQualityValidatorFixed:
    """数据质量验证器 - 修复版"""
    
    def __init__(self):
        self.data_dir = "data/quality_validation_fixed"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 数据源配置
        self.data_sources = {
            'akshare': {
                'name': 'akshare',
                'priority': 1,
                'description': '免费A股数据源',
                'coverage': ['股价', '基本面', '财务数据'],
                'reliability': 0.8
            },
            'sina_finance': {
                'name': '新浪财经',
                'priority': 2,
                'description': '实时股价数据',
                'coverage': ['股价', '成交量'],
                'reliability': 0.9
            },
            'eastmoney': {
                'name': '东方财富',
                'priority': 3,
                'description': '财务数据和新闻',
                'coverage': ['财务数据', '新闻', '研报'],
                'reliability': 0.85
            },
            'mock_data': {
                'name': '模拟数据',
                'priority': 99,
                'description': '测试用模拟数据',
                'coverage': ['所有数据'],
                'reliability': 0.1  # 可靠性很低
            }
        }
        
        # 合理性检查规则（优化版）
        self.reasonability_rules = {
            'revenue_yoy': {
                'min': -0.5,    # -50%
                'max': 2.0,     # +200%（降低阈值）
                'typical_min': -0.3,
                'typical_max': 1.0,  # 降低典型最大值
                'warning_threshold': 1.5  # 降低警告阈值
            },
            'profit_yoy': {
                'min': -1.0,    # -100%
                'max': 3.0,     # +300%（降低阈值）
                'typical_min': -0.5,
                'typical_max': 2.0,  # 降低典型最大值
                'warning_threshold': 2.5  # 降低警告阈值
            },
            'gross_margin': {
                'min': 0.0,
                'max': 0.8,     # 80%
                'typical_min': 0.1,
                'typical_max': 0.6
            },
            'net_margin': {
                'min': -0.2,    # -20%
                'max': 0.5,     # 50%
                'typical_min': 0.0,
                'typical_max': 0.3
            },
            'debt_ratio': {
                'min': 0.0,
                'max': 1.0,     # 100%
                'typical_min': 0.2,
                'typical_max': 0.8
            }
        }
        
        # 评分权重（优化版）
        self.scoring_weights = {
            'completeness': 0.25,  # 降低权重
            'reasonability': 0.35, # 保持
            'consistency': 0.25,   # 提高权重
            'extreme_values': 0.15 # 提高权重
        }
        
        logger.info("修复版数据质量验证器初始化完成")
        logger.info(f"评分权重: 完整性{self.scoring_weights['completeness']*100:.0f}%, "
                   f"合理性{self.scoring_weights['reasonability']*100:.0f}%, "
                   f"一致性{self.scoring_weights['consistency']*100:.0f}%, "
                   f"极端值{self.scoring_weights['extreme_values']*100:.0f}%")
    
    def validate_financial_data(self, stock_code: str, stock_name: str,
                               financial_data: Dict) -> Dict:
        """验证财务数据的合理性 - 修复版"""
        logger.info(f"验证股票 {stock_code} ({stock_name}) 的财务数据")
        
        validation_results = {
            'stock_code': stock_code,
            'stock_name': stock_name,
            'validation_time': datetime.now().isoformat(),
            'overall_score': 0,
            'is_reasonable': True,
            'warnings': [],
            'errors': [],
            'details': {}
        }
        
        # 1. 检查数据完整性
        completeness_score = self._check_completeness(financial_data)
        validation_results['details']['completeness'] = completeness_score
        
        # 2. 检查数据合理性
        reasonability_results = self._check_reasonability(financial_data)
        validation_results['details']['reasonability'] = reasonability_results
        
        # 3. 检查数据一致性（加强版）
        consistency_score = self._check_consistency_enhanced(financial_data)
        validation_results['details']['consistency'] = consistency_score
        
        # 4. 检查极端值（加强版）
        extreme_values = self._check_extreme_values_enhanced(financial_data)
        validation_results['details']['extreme_values'] = extreme_values
        
        # 5. 专项检查：利润质量
        profit_quality = self._check_profit_quality(financial_data)
        validation_results['details']['profit_quality'] = profit_quality
        
        # 计算总体分数（使用优化权重）
        overall_score = (
            completeness_score['score'] * self.scoring_weights['completeness'] +
            reasonability_results['score'] * self.scoring_weights['reasonability'] +
            consistency_score * self.scoring_weights['consistency'] +
            (100 - extreme_values['penalty']) * self.scoring_weights['extreme_values']
        )
        
        # 应用利润质量惩罚
        overall_score = max(0, overall_score - profit_quality['penalty'])
        
        validation_results['overall_score'] = overall_score
        
        # 判断是否合理（根据老大要求提高到75分）
        if overall_score < 75:
            validation_results['is_reasonable'] = False
            validation_results['errors'].append(f"数据质量分数过低: {overall_score:.1f} < 75")
        
        # 收集警告和错误
        validation_results['warnings'].extend(completeness_score['warnings'])
        validation_results['warnings'].extend(reasonability_results['warnings'])
        validation_results['warnings'].extend(extreme_values['warnings'])
        validation_results['warnings'].extend(profit_quality['warnings'])
        
        validation_results['errors'].extend(completeness_score['errors'])
        validation_results['errors'].extend(reasonability_results['errors'])
        validation_results['errors'].extend(extreme_values['errors'])
        validation_results['errors'].extend(profit_quality['errors'])
        
        # 保存验证结果
        self._save_validation_result(validation_results)
        
        logger.info(f"验证完成: 分数={overall_score:.1f}, 合理={validation_results['is_reasonable']}")
        
        return validation_results
    
    def _check_completeness(self, data: Dict) -> Dict:
        """检查数据完整性"""
        required_fields = [
            'report_type', 'report_date', 'revenue_yoy', 
            'profit_yoy', 'gross_margin', 'net_margin'
        ]
        
        optional_fields = [
            'revenue_amount', 'profit_amount', 'operating_cash_flow',
            'debt_ratio', 'revenue_3y_cagr', 'profit_3y_cagr'
        ]
        
        completeness = {
            'score': 0,
            'missing_required': [],
            'missing_optional': [],
            'warnings': [],
            'errors': []
        }
        
        # 检查必填字段
        missing_count = 0
        for field in required_fields:
            if field not in data or data[field] is None:
                completeness['missing_required'].append(field)
                missing_count += 1
        
        # 检查可选字段
        for field in optional_fields:
            if field not in data or data[field] is None:
                completeness['missing_optional'].append(field)
        
        # 计算完整性分数
        if len(required_fields) > 0:
            completeness['score'] = (1 - missing_count / len(required_fields)) * 100
        
        # 生成警告和错误
        if missing_count > 0:
            completeness['errors'].append(f"缺少{missing_count}个必填字段")
        
        if len(completeness['missing_optional']) > 3:
            completeness['warnings'].append(f"缺少{len(completeness['missing_optional'])}个可选字段")
        
        return completeness
    
    def _check_reasonability(self, data: Dict) -> Dict:
        """检查数据合理性"""
        results = {
            'score': 100,
            'warnings': [],
            'errors': [],
            'violations': []
        }
        
        for field, rule in self.reasonability_rules.items():
            if field in data and data[field] is not None:
                value = data[field]
                
                # 检查是否在合理范围内
                if value < rule['min'] or value > rule['max']:
                    results['score'] -= 30
                    results['errors'].append(
                        f"{field}超出合理范围: {value:.1%} (范围: {rule['min']:.1%} ~ {rule['max']:.1%})"
                    )
                    results['violations'].append({
                        'field': field,
                        'value': value,
                        'type': 'out_of_range',
                        'severity': 'error'
                    })
                
                # 检查是否在典型范围内
                elif value < rule['typical_min'] or value > rule['typical_max']:
                    results['score'] -= 15
                    results['warnings'].append(
                        f"{field}超出典型范围: {value:.1%} (典型: {rule['typical_min']:.1%} ~ {rule['typical_max']:.1%})"
                    )
                    results['violations'].append({
                        'field': field,
                        'value': value,
                        'type': 'atypical',
                        'severity': 'warning'
                    })
                
                # 检查警告阈值
                elif 'warning_threshold' in rule and abs(value) > rule['warning_threshold']:
                    results['score'] -= 10
                    results['warnings'].append(
                        f"{field}超过警告阈值: {value:.1%} (阈值: {rule['warning_threshold']:.1%})"
                    )
                    results['violations'].append({
                        'field': field,
                        'value': value,
                        'type': 'warning_threshold',
                        'severity': 'warning'
                    })
        
        # 确保分数不低于0
        results['score'] = max(0, results['score'])
        
        return results
    
    def _check_consistency_enhanced(self, data: Dict) -> float:
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
    
    def _check_extreme_values_enhanced(self, data: Dict) -> Dict:
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
    
    def _check_profit_quality(self, data: Dict) -> Dict:
        """检查利润质量"""
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
            
            # 利润为负但毛利率正常
            if profit_growth < 0 and data.get('gross_margin', 0) > 0.2:
                results['penalty'] += 10
                results['warnings'].append("毛利率正常但利润为负，可能存在费用控制问题")
        
        return results
    
    def _save_validation_result(self, result: Dict):
        """保存验证结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"validation_fixed_{result['stock_code']}_{timestamp}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.debug(f"验证结果已保存: {filepath}")
    
    def test_fixed_validator(self):
        """测试修复后的验证器"""
        print("修复版数据质量验证器测试")
        print("=" * 60)
        
        test_cases = [
            {
                'name': '利润为0的情况',
                'data': {
                    'report_type': '年报',
                    'report_date': '2026-03-30',
                    'revenue_yoy': 0.15,
                    'profit_yoy': 0.0,
                    'gross_margin': 0.25,
                    'net_margin': 0.08,
                    'debt_ratio': 0.45
                }
            },
            {
                'name': '营收大幅增长但利润为负',
                'data': {
                    'report_type': '年报',
                    'report_date': '2026-03-30',
                    'revenue_yoy': 3.0,
                    'profit_yoy': -0.5,
                    'gross_margin': 0.85,
                    'net_margin': -0.1,
                    'debt_ratio': 0.15
                }
            },
            {
                'name': '极端不一致数据（昨天的问题）',
                'data': {
                    'report_type': '季报',
                    'report_date': '2026-03-30',
                    'revenue_yoy': 34.813,
                    'profit_yoy': 16.047,
                    'gross_margin': 0.85,
                    'net_margin': 0.65,
                    'debt_ratio': 0.15
                }
            },
            {
                'name': '正常数据',
                'data': {
                    'report_type': '年报',
                    'report_date': '2026-03-30',
                    'revenue_yoy': 0.15,
                    'profit_yoy': 0.12,
                    'gross_margin': 0.25,
                    'net_margin': 0.08,
                    'debt_ratio': 0.45
                }
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n测试用例 {i}: {test_case['name']}")
            result = self.validate_financial_data(
                f'test{i:03d}', 
                f'测试股票{i}', 
                test_case['data']
            )
            
            print(f"  质量分数: {result['overall_score']:.1f}")
            print(f"  是否合理: {result['is_reasonable']}")
            print(f"  警告数量: {len(result['warnings'])}")
            print(f"  错误数量: {len(result['errors'])}")
            
            if result['errors']:
                print(f"  主要错误: {result['errors'][0]}")
        
        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)


def main():
    """主函数"""
    print("数据质量验证器修复版")
    print("版本: 1.0.0 (修复数据质量评估失效问题)")
    print("=" * 60)
    
    validator = DataQualityValidatorFixed()
    
    # 运行测试
    validator.test_fixed_validator()
    
    print("\n修复内容总结:")
    print("1. ✅ 加强一致性检查逻辑")
    print("2. ✅ 降低极端值检查阈值")
    print("3. ✅ 添加利润质量专项检查")
    print("4. ✅ 优化评分权重")
    print("5. ✅ 增加惩罚力度")
    print("6. ✅ 修复利润为0的检查漏洞")
    
    print("\n使用说明:")
    print("1. 替换原有的 data_quality_validator.py")
    print("2. 在财报监控系统中导入 FixedDataQualityValidator")
    print("3. 设置数据质量阈值为75分")
    print("4. 定期检查验证结果日志")


if __name__ == "__main__":
    main()
