#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析建议风险问题：基于错误数据给出投资建议
"""

import sys
import os
from typing import Dict, List

class AdviceRiskAnalyzer:
    """建议风险分析器"""

    def __init__(self):
        self.issues = []

    def analyze_advice_logic(self):
        """分析建议生成逻辑的问题"""
        print("=" * 70)
        print("🔍 建议风险问题分析")
        print("=" * 70)

        # 问题1: 基于错误数据给出激进建议
        print("\n1. 问题分析：基于错误数据给出激进建议")
        print("-" * 50)

        # 模拟错误数据场景
        error_scenarios = [
            {
                'name': '利润为0的情况',
                'stock': {
                    'stock_code': '002594',
                    'stock_name': '比亚迪',
                    'metric': '净利润',
                    'actual_value': 0,  # 错误数据：利润为0
                    'expected_value': 10000000000,
                    'surprise_ratio': -1.0,  # -100%
                    'data_quality_score': 100,
                    'is_holding': 1
                },
                'expected_advice': '强烈推荐加仓',
                'problem': '基于利润为0的错误数据，系统可能错误计算超预期比例'
            },
            {
                'name': '预期值为0的情况',
                'stock': {
                    'stock_code': '603259',
                    'stock_name': '药明康德',
                    'metric': '营收',
                    'actual_value': 5000000000,
                    'expected_value': 0,  # 错误数据：预期值为0
                    'surprise_ratio': float('inf'),  # 无穷大
                    'data_quality_score': 100,
                    'is_holding': 1
                },
                'expected_advice': '强烈推荐加仓',
                'problem': '除零错误导致超预期比例计算异常'
            },
            {
                'name': '数据质量低但给出激进建议',
                'stock': {
                    'stock_code': '600580',
                    'stock_name': '卧龙电驱',
                    'metric': '营收',
                    'actual_value': 3000000000,
                    'expected_value': 2000000000,
                    'surprise_ratio': 0.5,  # +50%
                    'data_quality_score': 60,  # 低质量数据
                    'is_holding': 1
                },
                'expected_advice': '强烈推荐加仓',
                'problem': '数据质量分数低但未在建议中体现风险'
            }
        ]

        for scenario in error_scenarios:
            print(f"\n📊 场景: {scenario['name']}")
            print(f"   数据: {scenario['stock']}")
            print(f"   问题: {scenario['problem']}")

            # 分析建议生成逻辑
            advice = self._simulate_advice_generation(scenario['stock'])
            print(f"   当前逻辑建议: {advice}")

            if "强烈推荐加仓" in advice:
                print(f"   ❌ 风险: 基于错误数据给出激进建议")
                self.issues.append({
                    'type': '激进建议风险',
                    'scenario': scenario['name'],
                    'problem': scenario['problem'],
                    'current_advice': advice
                })
            else:
                print(f"   ✅ 安全: 建议相对保守")

    def _simulate_advice_generation(self, stock: Dict) -> str:
        """模拟当前建议生成逻辑"""
        surprise_ratio = stock.get('surprise_ratio', 0)

        # 当前逻辑（来自send_financial_report_v3_fixed.py）
        if surprise_ratio >= 0.30:  # ≥30%
            return "<font color='green'>✅ 强烈推荐加仓</font>"
        elif surprise_ratio >= 0.20:  # ≥20%
            return "<font color='green'>✅ 考虑加仓</font>"
        elif surprise_ratio >= 0.10:  # ≥10%
            return "<font color='blue'>🔍 持有观察</font>"
        elif surprise_ratio >= -0.10:  # -10% ~ 10%
            return "<font color='gray'>📋 维持现状</font>"
        elif surprise_ratio >= -0.20:  # -20% ~ -10%
            return "<font color='orange'>⚠️ 关注风险</font>"
        else:  # < -20%
            return "<font color='red'>🚨 考虑减仓</font>"

    def analyze_data_validation(self):
        """分析数据验证前置条件"""
        print("\n2. 数据验证前置条件分析")
        print("-" * 50)

        validation_checks = [
            {
                'check': '实际值是否为0',
                'importance': '高',
                'risk': '除零错误、无限大比例计算',
                'solution': '检查actual_value != 0'
            },
            {
                'check': '预期值是否为0',
                'importance': '高',
                'risk': '除零错误、无限大比例计算',
                'solution': '检查expected_value != 0'
            },
            {
                'check': '数据质量分数',
                'importance': '中',
                'risk': '基于低质量数据给出建议',
                'solution': 'data_quality_score >= 80才生成建议'
            },
            {
                'check': '超预期比例合理性',
                'importance': '高',
                'risk': '极端值导致错误建议',
                'solution': '限制surprise_ratio在[-1.0, 1.0]范围内'
            },
            {
                'check': '数据完整性',
                'importance': '中',
                'risk': '缺失关键字段',
                'solution': '验证required_fields完整性'
            }
        ]

        for check in validation_checks:
            print(f"   ✅ {check['check']}:")
            print(f"      重要性: {check['importance']}")
            print(f"      风险: {check['risk']}")
            print(f"      解决方案: {check['solution']}")

    def propose_fixed_advice_logic(self):
        """提出修复后的建议生成算法"""
        print("\n3. 修复后的建议生成算法设计")
        print("-" * 50)

        print("""
class FixedAdviceGenerator:
    def __init__(self):
        self.min_data_quality = 80  # 最低数据质量分数
        self.max_surprise_ratio = 1.0  # 最大超预期比例
        self.min_valid_value = 1  # 最小有效数值

    def validate_data(self, stock: Dict) -> Tuple[bool, str]:
        '''数据验证前置检查'''
        # 1. 检查数据完整性
        required_fields = ['actual_value', 'expected_value', 'surprise_ratio', 'data_quality_score']
        for field in required_fields:
            if field not in stock:
                return False, f"缺失必要字段: {field}"

        # 2. 检查数值有效性
        if stock['actual_value'] == 0:
            return False, "实际值为0，数据异常"
        if stock['expected_value'] == 0:
            return False, "预期值为0，数据异常"

        # 3. 检查数据质量
        if stock['data_quality_score'] < self.min_data_quality:
            return False, f"数据质量分数过低: {stock['data_quality_score']}"

        # 4. 检查超预期比例合理性
        if abs(stock['surprise_ratio']) > self.max_surprise_ratio:
            return False, f"超预期比例异常: {stock['surprise_ratio']}"

        return True, "数据验证通过"

    def get_trading_advice(self, stock: Dict) -> str:
        '''修复后的交易建议生成'''
        # 数据验证
        is_valid, message = self.validate_data(stock)
        if not is_valid:
            return f"<font color='red'>⚠️ 数据异常: {message}</font>"

        surprise_ratio = stock['surprise_ratio']
        data_quality = stock['data_quality_score']

        # 根据数据质量调整建议强度
        quality_factor = data_quality / 100.0

        if surprise_ratio >= 0.30 * quality_factor:
            advice = "强烈推荐加仓"
            color = "green"
        elif surprise_ratio >= 0.20 * quality_factor:
            advice = "考虑加仓"
            color = "green"
        elif surprise_ratio >= 0.10 * quality_factor:
            advice = "持有观察"
            color = "blue"
        elif surprise_ratio >= -0.10 * quality_factor:
            advice = "维持现状"
            color = "gray"
        elif surprise_ratio >= -0.20 * quality_factor:
            advice = "关注风险"
            color = "orange"
        else:
            advice = "考虑减仓"
            color = "red"

        # 添加数据质量提示
        if data_quality < 90:
            advice = f"{advice} (数据质量: {data_quality}分)"

        return f"<font color='{color}'>✅ {advice}</font>"
""")

    def design_risk_warning_mechanism(self):
        """设计风险提示机制"""
        print("\n4. 风险提示机制设计")
        print("-" * 50)

        print("""
风险提示机制设计：
1. 数据异常警告系统
   - 实际值/预期值为0 → 红色警告
   - 数据质量分数<80 → 黄色警告
   - 超预期比例异常 → 橙色警告

2. 建议强度分级
   - 高质量数据(≥90分): 正常建议强度
   - 中等质量数据(80-89分): 建议强度降低20%
   - 低质量数据(<80分): 仅提供观察建议，不提供交易建议

3. 风险提示内容
   - 数据来源说明
   - 数据质量评估
   - 建议置信度
   - 核实建议

4. 核实建议模板
   - "建议核实财报原始数据"
   - "建议关注公司官方公告"
   - "建议结合其他信息源验证"
   - "建议等待下个报告期确认"
""")

    def create_test_cases(self):
        """创建测试验证用例"""
        print("\n5. 测试验证用例")
        print("-" * 50)

        test_cases = [
            {
                'name': '正常高质量数据',
                'stock': {
                    'actual_value': 15000000000,
                    'expected_value': 12000000000,
                    'surprise_ratio': 0.25,
                    'data_quality_score': 95
                },
                'expected': '考虑加仓',
                'should_pass': True
            },
            {
                'name': '利润为0的错误数据',
                'stock': {
                    'actual_value': 0,
                    'expected_value': 10000000000,
                    'surprise_ratio': -1.0,
                    'data_quality_score': 100
                },
                'expected': '数据异常警告',
                'should_pass': False
            },
            {
                'name': '低质量数据',
                'stock': {
                    'actual_value': 5000000000,
                    'expected_value': 4000000000,
                    'surprise_ratio': 0.25,
                    'data_quality_score': 75
                },
                'expected': '数据质量警告',
                'should_pass': False
            },
            {
                'name': '极端超预期比例',
                'stock': {
                    'actual_value': 10000000000,
                    'expected_value': 1000000,
                    'surprise_ratio': 99.0,
                    'data_quality_score': 100
                },
                'expected': '超预期比例异常',
                'should_pass': False
            }
        ]

        for test in test_cases:
            status = "✅" if test['should_pass'] else "❌"
            print(f"{status} {test['name']}:")
            print(f"   数据: {test['stock']}")
            print(f"   预期结果: {test['expected']}")

    def generate_report(self):
        """生成分析报告"""
        print("\n" + "=" * 70)
        print("📋 建议风险问题分析报告")
        print("=" * 70)

        print("\n🎯 核心问题总结:")
        print("1. 基于错误数据（如利润为0）给出激进投资建议")
        print("2. 缺乏数据验证前置检查")
        print("3. 风险提示机制不完善")
        print("4. 建议生成算法未考虑数据质量")

        print("\n🔧 解决方案:")
        print("1. 添加数据验证前置条件")
        print("2. 修复建议生成算法")
        print("3. 完善风险提示机制")
        print("4. 优化建议内容和格式")

        print("\n🚀 实施计划:")
        print("1. 立即修复数据验证逻辑")
        print("2. 更新建议生成算法")
        print("3. 添加风险提示系统")
        print("4. 创建测试用例验证修复效果")

        if self.issues:
            print("\n⚠️ 发现的具体问题:")
            for issue in self.issues:
                print(f"   • {issue['type']}: {issue['scenario']}")
                print(f"     问题: {issue['problem']}")
                print(f"     当前建议: {issue['current_advice']}")

def main():
    """主函数"""
    analyzer = AdviceRiskAnalyzer()

    # 执行分析
    analyzer.analyze_advice_logic()
    analyzer.analyze_data_validation()
    analyzer.propose_fixed_advice_logic()
    analyzer.design_risk_warning_mechanism()
    analyzer.create_test_cases()
    analyzer.generate_report()

    print("\n" + "=" * 70)
    print("✅ 分析完成！")
    print("=" * 70)

if __name__ == "__main__":
    main()
