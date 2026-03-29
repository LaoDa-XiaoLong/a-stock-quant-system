#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据质量验证器 - 多源数据比对系统
用于验证财报数据的准确性和合理性
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

class DataQualityValidator:
    """数据质量验证器"""
    
    def __init__(self):
        self.data_dir = "data/quality_validation"
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
        
        # 合理性检查规则
        self.reasonability_rules = {
            'revenue_yoy': {
                'min': -0.5,    # -50%
                'max': 5.0,     # +500%（特殊情况）
                'typical_min': -0.3,
                'typical_max': 2.0,
                'warning_threshold': 3.0  # 超过300%需要特别验证
            },
            'profit_yoy': {
                'min': -1.0,    # -100%
                'max': 10.0,    # +1000%
                'typical_min': -0.5,
                'typical_max': 5.0,
                'warning_threshold': 8.0
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
        
        logger.info("数据质量验证器初始化完成")
    
    def validate_financial_data(self, stock_code: str, stock_name: str,
                               financial_data: Dict) -> Dict:
        """验证财务数据的合理性"""
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
        
        # 3. 检查数据一致性
        consistency_score = self._check_consistency(financial_data)
        validation_results['details']['consistency'] = consistency_score
        
        # 4. 检查极端值
        extreme_values = self._check_extreme_values(financial_data)
        validation_results['details']['extreme_values'] = extreme_values
        
        # 计算总体分数
        overall_score = (
            completeness_score['score'] * 0.3 +
            reasonability_results['score'] * 0.4 +
            consistency_score * 0.2 +
            (100 - extreme_values['penalty']) * 0.1
        )
        
        validation_results['overall_score'] = overall_score
        
        # 判断是否合理（根据老大要求提高到75分）
        if overall_score < 75:
            validation_results['is_reasonable'] = False
            validation_results['errors'].append(f"数据质量分数过低: {overall_score:.1f} < 75")
        
        # 收集警告和错误
        validation_results['warnings'].extend(completeness_score['warnings'])
        validation_results['warnings'].extend(reasonability_results['warnings'])
        validation_results['warnings'].extend(extreme_values['warnings'])
        
        validation_results['errors'].extend(completeness_score['errors'])
        validation_results['errors'].extend(reasonability_results['errors'])
        validation_results['errors'].extend(extreme_values['errors'])
        
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
    
    def _check_consistency(self, data: Dict) -> float:
        """检查数据一致性"""
        score = 100
        
        # 检查营收和利润的一致性
        if 'revenue_yoy' in data and 'profit_yoy' in data:
            revenue_growth = data['revenue_yoy']
            profit_growth = data['profit_yoy']
            
            # 营收增长但利润大幅下降可能有问题
            if revenue_growth > 0.1 and profit_growth < -0.3:
                score -= 20
        
        # 检查毛利率和净利率的一致性
        if 'gross_margin' in data and 'net_margin' in data:
            gross_margin = data['gross_margin']
            net_margin = data['net_margin']
            
            # 净利率不应超过毛利率
            if net_margin > gross_margin:
                score -= 30
            
            # 净利率通常远低于毛利率
            elif net_margin > gross_margin * 0.8:
                score -= 10
        
        return max(0, score)
    
    def _check_extreme_values(self, data: Dict) -> Dict:
        """检查极端值"""
        results = {
            'penalty': 0,
            'extreme_values': [],
            'warnings': [],
            'errors': []
        }
        
        extreme_thresholds = {
            'revenue_yoy': 3.0,      # 超过300%增长
            'profit_yoy': 5.0,       # 超过500%增长
            'revenue_amount': 10000, # 营收超过1万亿元
            'profit_amount': 1000,   # 利润超过1000亿元
        }
        
        for field, threshold in extreme_thresholds.items():
            if field in data and data[field] is not None:
                value = data[field]
                
                if abs(value) > threshold:
                    results['penalty'] += 20
                    results['extreme_values'].append({
                        'field': field,
                        'value': value,
                        'threshold': threshold
                    })
                    
                    if field.endswith('_yoy'):
                        results['warnings'].append(
                            f"{field}增长异常: {value:.1%} (阈值: {threshold:.1%})"
                        )
                    else:
                        results['warnings'].append(
                            f"{field}数值异常: {value:,.0f} (阈值: {threshold:,.0f})"
                        )
        
        return results
    
    def _save_validation_result(self, result: Dict):
        """保存验证结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"validation_{result['stock_code']}_{timestamp}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.debug(f"验证结果已保存: {filepath}")
    
    def compare_multiple_sources(self, stock_code: str, stock_name: str) -> Dict:
        """多源数据比对"""
        logger.info(f"开始多源数据比对: {stock_code} ({stock_name})")
        
        comparison_results = {
            'stock_code': stock_code,
            'stock_name': stock_name,
            'comparison_time': datetime.now().isoformat(),
            'sources': {},
            'consensus': {},
            'discrepancies': [],
            'recommended_source': None
        }
        
        # 这里应该从多个数据源获取数据
        # 目前先模拟，后续接入真实数据源
        
        # 模拟不同数据源的数据
        mock_sources = {
            'akshare': self._get_mock_akshare_data(stock_code),
            'eastmoney': self._get_mock_eastmoney_data(stock_code),
            'sina': self._get_mock_sina_data(stock_code),
            'mock': self._get_mock_extreme_data(stock_code)  # 模拟极端数据
        }
        
        comparison_results['sources'] = mock_sources
        
        # 计算共识值
        comparison_results['consensus'] = self._calculate_consensus(mock_sources)
        
        # 检查差异
        comparison_results['discrepancies'] = self._find_discrepancies(mock_sources)
        
        # 推荐数据源
        comparison_results['recommended_source'] = self._recommend_source(mock_sources)
        
        # 保存比对结果
        self._save_comparison_result(comparison_results)
        
        return comparison_results
    
    def _get_mock_akshare_data(self, stock_code: str) -> Dict:
        """模拟akshare数据（相对合理）"""
        return {
            'revenue_yoy': np.random.uniform(-0.2, 0.5),
            'profit_yoy': np.random.uniform(-0.3, 0.8),
            'gross_margin': np.random.uniform(0.15, 0.45),
            'net_margin': np.random.uniform(0.03, 0.2),
            'source': 'akshare',
            'reliability': 0.8
        }
    
    def _get_mock_eastmoney_data(self, stock_code: str) -> Dict:
        """模拟东方财富数据"""
        return {
            'revenue_yoy': np.random.uniform(-0.15, 0.4),
            'profit_yoy': np.random.uniform(-0.25, 0.6),
            'gross_margin': np.random.uniform(0.12, 0.4),
            'net_margin': np.random.uniform(0.02, 0.18),
            'source': 'eastmoney',
            'reliability': 0.85
        }
    
    def _get_mock_sina_data(self, stock_code: str) -> Dict:
        """模拟新浪数据"""
        return {
            'revenue_yoy': np.random.uniform(-0.1, 0.3),
            'profit_yoy': np.random.uniform(-0.2, 0.5),
            'gross_margin': np.random.uniform(0.1, 0.35),
            'net_margin': np.random.uniform(0.01, 0.15),
            'source': 'sina',
            'reliability': 0.75
        }
    
    def _get_mock_extreme_data(self, stock_code: str) -> Dict:
        """模拟极端数据（用于测试验证）"""
        return {
            'revenue_yoy': np.random.uniform(2.0, 10.0),  # 200%-1000%增长
            'profit_yoy': np.random.uniform(5.0, 20.0),   # 500%-2000%增长
            'gross_margin': np.random.uniform(0.6, 0.9),  # 60%-90%毛利率
            'net_margin': np.random.uniform(0.4, 0.7),    # 40%-70%净利率
            'source': 'mock_extreme',
            'reliability': 0.1
        }
    
    def _calculate_consensus(self, sources: Dict) -> Dict:
        """计算共识值"""
        consensus = {}
        
        # 收集所有数据源共有的字段
        common_fields = set()
        for source_data in sources.values():
            common_fields.update(source_data.keys())
        
        common_fields = common_fields - {'source', 'reliability'}
        
        for field in common_fields:
            values = []
            weights = []
            
            for source_name, source_data in sources.items():
                if field in source_data:
                    values.append(source_data[field])
                    weights.append(source_data.get('reliability', 0.5))
            
            if values:
                # 加权平均
                weighted_sum = sum(v * w for v, w in zip(values, weights))
                total_weight = sum(weights)
                
                if total_weight > 0:
                    consensus[field] = weighted_sum / total_weight
                else:
                    consensus[field] = np.mean(values)
        
        return consensus
    
    def _find_discrepancies(self, sources: Dict) -> List[Dict]:
        """查找数据差异"""
        discrepancies = []
        
        # 收集所有字段
        all_fields = set()
        for source_data in sources.values():
            all_fields.update(source_data.keys())
        
        all_fields = all_fields - {'source', 'reliability'}
        
        for field in all_fields:
            values = {}
            for source_name, source_data in sources.items():
                if field in source_data:
                    values[source_name] = source_data[field]
            
            if len(values) >= 2:
                # 计算变异系数
                value_list = list(values.values())
                mean_val = np.mean(value_list)
                std_val = np.std(value_list)
                
                if mean_val != 0:
                    cv = std_val / abs(mean_val)
                    
                    if cv > 0.5:  # 变异系数超过50%
                        discrepancies.append({
                            'field': field,
                            'values': values,
                            'mean': mean_val,
                            'std': std_val,
                            'cv': cv,
                            'severity': 'high' if cv > 1.0 else 'medium'
                        })
        
        return discrepancies
    
    def _recommend_source(self, sources: Dict) -> str:
        """推荐最佳数据源"""
        if not sources:
            return None
        
        # 根据可靠性评分
        best_source = None
        best_score = -1
        
        for source_name, source_data in sources.items():
            reliability = source_data.get('reliability', 0.5)
            
            # 检查数据合理性
            validation = self.validate_financial_data(
                'test', 'test', 
                {k: v for k, v in source_data.items() if k not in ['source', 'reliability']}
            )
            
            score = reliability * 0.7 + (validation['overall_score'] / 100) * 0.3
            
            if score > best_score:
                best_score = score
                best_source = source_name
        
        return best_source
    
    def _save_comparison_result(self, result: Dict):
        """保存比对结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comparison_{result['stock_code']}_{timestamp}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.debug(f"比对结果已保存: {filepath}")


def test_validation():
    """测试验证器"""
    print("数据质量验证器测试")
    print("=" * 50)
    
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
    
    result1 = validator.validate_financial_data('000001', '平安银行', reasonable_data)
    print(f"   分数: {result1['overall_score']:.1f}")
    print(f"   合理: {result1['is_reasonable']}")
    print(f"   警告: {len(result1['warnings'])} 个")
    
    # 测试用例2：极端数据（类似昨天的问题）
    print("\n2. 测试极端数据（类似昨天问题）:")
    extreme_data = {
        'report_type': '季报',
        'report_date': '2026-03-28',
        'revenue_yoy': 34.813,    # 3481.3%增长（夸张！）
        'profit_yoy': 16.047,     # 1604.7%增长（夸张！）
        'gross_margin': 0.85,     # 85%毛利率（过高）
        'net_margin': 0.65,       # 65%净利率（过高）
        'debt_ratio': 0.15        # 15%负债率（过低）
    }
    
    result2 = validator.validate_financial_data('002352', '顺丰控股', extreme_data)
    print(f"   分数: {result2['overall_score']:.1f}")
    print(f"   合理: {result2['is_reasonable']}")
    print(f"   错误: {len(result2['errors'])} 个")
    
    for error in result2['errors'][:3]:  # 显示前3个错误
        print(f"   - {error}")
    
    # 测试用例3：多源比对
    print("\n3. 测试多源数据比对:")
    comparison = validator.compare_multiple_sources('002352', '顺丰控股')
    print(f"   数据源数量: {len(comparison['sources'])}")
    print(f"   差异发现: {len(comparison['discrepancies'])} 处")
    print(f"   推荐数据源: {comparison['recommended_source']}")
    
    # 显示共识值
    print("\n   共识值:")
    for field, value in comparison['consensus'].items():
        if field.endswith('_yoy'):
            print(f"   {field}: {value:.1%}")
        else:
            print(f"   {field}: {value:.3f}")
    
    print("\n" + "=" * 50)
    print("数据质量验证测试完成")
    print("\n建议:")
    print("1. 将验证器集成到财报监控系统中")
    print("2. 过滤掉分数低于60的数据")
    print("3. 对极端数据进行人工复核和多源比对")


if __name__ == "__main__":
    import numpy as np
    test_validation()