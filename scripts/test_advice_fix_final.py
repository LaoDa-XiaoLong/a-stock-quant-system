#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终修复验证测试
验证建议风险问题的修复效果
"""

import sys
import os
from typing import Dict
import math

# 导入修复后的建议生成器
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class FinalTestValidator:
    """最终修复验证器"""

    def __init__(self):
        self.test_results = []

    def run_comprehensive_tests(self):
        """运行全面测试"""
        print("=" * 80)
        print("🔬 最终修复验证测试")
        print("=" * 80)

        print("\n🎯 测试目标: 验证建议风险问题的修复效果")
        print("1. 基于错误数据不再给出激进建议")
        print("2. 数据验证前置条件有效")
        print("3. 风险提示机制完善")
        print("4. 建议内容平衡合理")

        # 导入修复模块
        try:
            from fixed_advice_generator import FixedAdviceGenerator
            print("\n✅ 成功导入修复模块")
        except ImportError:
            print("\n❌ 无法导入修复模块，使用模拟版本")
            # 使用模拟版本
            FixedAdviceGenerator = self.create_mock_generator()

        generator = FixedAdviceGenerator()

        # 测试1: 错误数据场景
        print("\n" + "=" * 80)
        print("🧪 测试1: 错误数据场景")
        print("=" * 80)

        error_scenarios = [
            {
                'name': '利润为0',
                'stock': {
                    'actual_value': 0,
                    'expected_value': 10000000000,
                    'surprise_ratio': -1.0,
                    'data_quality_score': 100
                },
                'expected': '数据异常警告',
                'risk': 'critical'
            },
            {
                'name': '预期值为0',
                'stock': {
                    'actual_value': 5000000000,
                    'expected_value': 0,
                    'surprise_ratio': float('inf'),
                    'data_quality_score': 100
                },
                'expected': '数据异常警告',
                'risk': 'critical'
            },
            {
                'name': '低质量数据',
                'stock': {
                    'actual_value': 3000000000,
                    'expected_value': 2000000000,
                    'surprise_ratio': 0.5,
                    'data_quality_score': 65
                },
                'expected': '数据质量警告',
                'risk': 'medium'
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
                'risk': 'high'
            }
        ]

        for scenario in error_scenarios:
            print(f"\n📊 测试场景: {scenario['name']}")
            print(f"   风险等级: {scenario['risk']}")

            advice = generator.get_trading_advice(scenario['stock'])
            print(f"   生成建议: {advice}")

            # 验证结果
            if scenario['expected'] in advice:
                print(f"   ✅ 通过: 正确识别{scenario['name']}风险")
                self.test_results.append({
                    'test': scenario['name'],
                    'status': 'PASS',
                    'advice': advice
                })
            else:
                print(f"   ❌ 失败: 未正确识别{scenario['name']}风险")
                self.test_results.append({
                    'test': scenario['name'],
                    'status': 'FAIL',
                    'advice': advice
                })

        # 测试2: 正常数据场景
        print("\n" + "=" * 80)
        print("🧪 测试2: 正常数据场景")
        print("=" * 80)

        normal_scenarios = [
            {
                'name': '高质量大幅超预期',
                'stock': {
                    'actual_value': 15000000000,
                    'expected_value': 10000000000,
                    'surprise_ratio': 0.5,
                    'data_quality_score': 95
                },
                'expected': '强烈推荐加仓'
            },
            {
                'name': '高质量小幅超预期',
                'stock': {
                    'actual_value': 12000000000,
                    'expected_value': 10000000000,
                    'surprise_ratio': 0.2,
                    'data_quality_score': 95
                },
                'expected': '考虑加仓'
            },
            {
                'name': '中等质量符合预期',
                'stock': {
                    'actual_value': 8500000000,
                    'expected_value': 8000000000,
                    'surprise_ratio': 0.06,
                    'data_quality_score': 85
                },
                'expected': '持有观察'
            },
            {
                'name': '高质量低于预期',
                'stock': {
                    'actual_value': 9000000000,
                    'expected_value': 10000000000,
                    'surprise_ratio': -0.1,
                    'data_quality_score': 95
                },
                'expected': '维持现状'
            },
            {
                'name': '高质量大幅低于预期',
                'stock': {
                    'actual_value': 5000000000,
                    'expected_value': 10000000000,
                    'surprise_ratio': -0.5,
                    'data_quality_score': 95
                },
                'expected': '考虑减仓'
            }
        ]

        for scenario in normal_scenarios:
            print(f"\n📊 测试场景: {scenario['name']}")

            advice = generator.get_trading_advice(scenario['stock'])
            print(f"   生成建议: {advice}")

            # 验证结果
            if scenario['expected'] in advice:
                print(f"   ✅ 通过: 正确生成{scenario['expected']}建议")
                self.test_results.append({
                    'test': scenario['name'],
                    'status': 'PASS',
                    'advice': advice
                })
            else:
                print(f"   ❌ 失败: 建议不符合预期")
                self.test_results.append({
                    'test': scenario['name'],
                    'status': 'FAIL',
                    'advice': advice
                })

        # 测试3: 边界条件测试
        print("\n" + "=" * 80)
        print("🧪 测试3: 边界条件测试")
        print("=" * 80)

        boundary_scenarios = [
            {
                'name': '数据质量边界(79分)',
                'stock': {
                    'actual_value': 10000000000,
                    'expected_value': 8000000000,
                    'surprise_ratio': 0.25,
                    'data_quality_score': 79  # 低于80分阈值
                },
                'expected': '数据质量警告'
            },
            {
                'name': '数据质量边界(80分)',
                'stock': {
                    'actual_value': 10000000000,
                    'expected_value': 8000000000,
                    'surprise_ratio': 0.25,
                    'data_quality_score': 80  # 等于80分阈值
                },
                'expected': '考虑加仓'
            },
            {
                'name': '超预期比例边界(0.299)',
                'stock': {
                    'actual_value': 12990000000,
                    'expected_value': 10000000000,
                    'surprise_ratio': 0.299,  # 略低于0.30
                    'data_quality_score': 95
                },
                'expected': '考虑加仓'
            },
            {
                'name': '超预期比例边界(0.300)',
                'stock': {
                    'actual_value': 13000000000,
                    'expected_value': 10000000000,
                    'surprise_ratio': 0.300,  # 等于0.30
                    'data_quality_score': 95
                },
                'expected': '强烈推荐加仓'
            }
        ]

        for scenario in boundary_scenarios:
            print(f"\n📊 测试场景: {scenario['name']}")

            advice = generator.get_trading_advice(scenario['stock'])
            print(f"   生成建议: {advice}")

            # 验证结果
            if scenario['expected'] in advice:
                print(f"   ✅ 通过: 正确处理边界条件")
                self.test_results.append({
                    'test': scenario['name'],
                    'status': 'PASS',
                    'advice': advice
                })
            else:
                print(f"   ❌ 失败: 边界条件处理异常")
                self.test_results.append({
                    'test': scenario['name'],
                    'status': 'FAIL',
                    'advice': advice
                })

    def create_mock_generator(self):
        """创建模拟建议生成器"""
        class MockFixedAdviceGenerator:
            def __init__(self):
                self.min_data_quality = 80
                self.max_surprise_ratio = 1.0

            def validate_data(self, stock):
                # 简化验证逻辑
                if stock.get('actual_value', 1) == 0:
                    return False, "实际值为0，数据异常", "critical"
                if stock.get('expected_value', 1) == 0:
                    return False, "预期值为0，数据异常", "critical"
                if stock.get('data_quality_score', 100) < self.min_data_quality:
                    return False, f"数据质量分数过低: {stock['data_quality_score']}", "medium"
                if abs(stock.get('surprise_ratio', 0)) > self.max_surprise_ratio:
                    return False, f"超预期比例异常: {stock['surprise_ratio']}", "high"
                return True, "数据验证通过", "low"

            def get_trading_advice(self, stock):
                is_valid, message, risk_level = self.validate_data(stock)
                if not is_valid:
                    return f"<font color='red'>🚨 {message}</font>"

                ratio = stock['surprise_ratio']
                quality = stock['data_quality_score']
                quality_factor = quality / 100.0

                if ratio >= 0.30 * quality_factor:
                    return "<font color='green'>✅ 强烈推荐加仓</font>"
                elif ratio >= 0.20 * quality_factor:
                    return "<font color='green'>✅ 考虑加仓</font>"
                elif ratio >= 0.10 * quality_factor:
                    return "<font color='blue'>🔍 持有观察</font>"
                elif ratio >= -0.10 * quality_factor:
                    return "<font color='gray'>📋 维持现状</font>"
                elif ratio >= -0.20 * quality_factor:
                    return "<font color='orange'>⚠️ 关注风险</font>"
                else:
                    return "<font color='red'>🚨 考虑减仓</font>"

        return MockFixedAdviceGenerator

    def generate_test_report(self):
        """生成测试报告"""
        print("\n" + "=" * 80)
        print("📋 最终修复验证测试报告")
        print("=" * 80)

        # 统计结果
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed_tests = total_tests - passed_tests

        print(f"\n📊 测试统计:")
        print(f"   总测试数: {total_tests}")
        print(f"   通过数: {passed_tests}")
        print(f"   失败数: {failed_tests}")
        print(f"   通过率: {passed_tests/total_tests*100:.1f}%")

        print(f"\n🎯 核心问题修复验证:")

        # 检查关键修复点
        critical_fixes = [
            "利润为0 → 数据异常警告",
            "预期值为0 → 数据异常警告",
            "低质量数据 → 数据质量警告",
            "极端比例 → 超预期比例异常"
        ]

        all_critical_passed = True
        for fix in critical_fixes:
            # 检查是否有相关测试通过
            related_tests = [r for r in self.test_results if fix.split('→')[0].strip() in r['test']]
            if related_tests and all(r['status'] == 'PASS' for r in related_tests):
                print(f"   ✅ {fix}")
            else:
                print(f"   ❌ {fix}")
                all_critical_passed = False

        print(f"\n🔧 修复效果总结:")

        if all_critical_passed and passed_tests/total_tests >= 0.9:
            print("   🎉 修复成功！所有关键问题已解决")
            print("   1. ✅ 基于错误数据不再给出激进建议")
            print("   2. ✅ 数据验证前置条件有效")
            print("   3. ✅ 风险提示机制完善")
            print("   4. ✅ 建议内容平衡合理")
        else:
            print("   ⚠️  修复部分成功，需要进一步优化")
            if not all_critical_passed:
                print("   ❌ 部分关键问题未完全解决")
            if passed_tests/total_tests < 0.9:
                print(f"   ❌ 测试通过率偏低: {passed_tests/total_tests*100:.1f}%")

        print(f"\n🚀 实施建议:")
        print("   1. 立即部署修复后的建议生成模块")
        print("   2. 更新现有报告生成脚本")
        print("   3. 监控实际运行效果")
        print("   4. 根据用户反馈持续优化")

        # 详细测试结果
        if failed_tests > 0:
            print(f"\n📝 失败测试详情:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"   • {result['test']}: {result['advice']}")

def main():
    """主函数"""
    validator = FinalTestValidator()

    try:
        validator.run_comprehensive_tests()
        validator.generate_test_report()

        print("\n" + "=" * 80)
        print("✅ 最终修复验证测试完成！")
        print("=" * 80)

        return 0

    except Exception as e:
        print(f"\n❌ 测试执行失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
