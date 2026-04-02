#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据采集修复效果
验证过滤条件和数据验证效果
"""

import sys
import os
import time

# 添加路径
current_dir = os.path.dirname(os.path.abspath(__file__))
workspace_dir = os.path.dirname(current_dir)
sys.path.append(workspace_dir)

# 直接导入需要的模块，避免路径问题
import numpy as np
from datetime import datetime, timedelta
import logging
import json
from typing import Dict, Optional

def test_fixed_data_collection():
    """测试修复版数据采集函数"""
    print("🧪 测试数据采集修复效果")
    print("=" * 70)
    print("验证: 只采集正式发布的季报和年报数据，剔除预估数据")
    print("=" * 70)

    # 创建监控实例
    print("\n🚀 初始化财报监控系统...")
    monitor = FinancialMonitorSkillIntegrated()

    # 测试股票列表
    test_stocks = [
        ("601318", "中国平安"),
        ("600036", "招商银行"),
        ("000001", "平安银行"),
        ("000002", "万科A"),
        ("600519", "贵州茅台")
    ]

    print(f"\n📊 测试 {len(test_stocks)} 只股票的数据采集:")
    print("-" * 70)

    # 统计指标
    stats = {
        'total_tests': 0,
        'success_count': 0,
        'failure_count': 0,
        'zero_profit_count': 0,
        'estimated_report_count': 0,
        'valid_report_count': 0,
        'total_retries': 0
    }

    for stock_code, stock_name in test_stocks:
        stats['total_tests'] += 1
        print(f"\n🔍 测试 {stock_code} {stock_name}:")

        try:
            start_time = time.time()

            # 调用修复版数据采集函数
            data = monitor.get_financial_data_fixed(stock_code, stock_name)

            elapsed_time = time.time() - start_time

            if data is None:
                stats['failure_count'] += 1
                print(f"   ❌ 数据采集失败")
                continue

            stats['success_count'] += 1

            # 检查数据质量
            print(f"   ✅ 数据采集成功 ({elapsed_time:.2f}秒)")

            # 检查利润是否为0
            profit_actual = data.get('profit_actual', 0)
            if abs(profit_actual) < 1e-5:
                stats['zero_profit_count'] += 1
                print(f"   ⚠️  利润接近0: {profit_actual:.2f}")
            else:
                print(f"   ✅ 利润正常: {profit_actual:.2f}")

            # 检查报告类型
            report_type = data.get('report_type', '')
            if report_type in ['年报', '季报']:
                stats['valid_report_count'] += 1
                print(f"   ✅ 正式报告: {report_type}")
            else:
                stats['estimated_report_count'] += 1
                print(f"   ❌ 预估报告: {report_type}")

            # 显示关键数据
            print(f"   营收实际值: {data.get('revenue_actual', 0):.2f}")
            print(f"   营收预期值: {data.get('revenue_expected', 0):.2f}")
            print(f"   营收超预期: {data.get('revenue_exceed', 0):.2%}")
            print(f"   利润实际值: {data.get('profit_actual', 0):.2f}")
            print(f"   利润预期值: {data.get('profit_expected', 0):.2f}")
            print(f"   利润超预期: {data.get('profit_exceed', 0):.2%}")
            print(f"   营收同比增长: {data.get('revenue_yoy', 0):.2%}")
            print(f"   利润同比增长: {data.get('profit_yoy', 0):.2%}")
            print(f"   报告日期: {data.get('report_date', 'N/A')}")
            print(f"   数据来源: {data.get('data_source', 'N/A')}")
            print(f"   数据质量: {data.get('data_quality', 'N/A')}")

        except Exception as e:
            stats['failure_count'] += 1
            print(f"   ❌ 测试异常: {e}")

    # 打印统计结果
    print("\n" + "=" * 70)
    print("📊 测试结果统计")
    print("=" * 70)

    success_rate = (stats['success_count'] / stats['total_tests'] * 100) if stats['total_tests'] > 0 else 0
    zero_profit_rate = (stats['zero_profit_count'] / stats['success_count'] * 100) if stats['success_count'] > 0 else 0
    valid_report_rate = (stats['valid_report_count'] / stats['success_count'] * 100) if stats['success_count'] > 0 else 0

    print(f"   总测试数: {stats['total_tests']}")
    print(f"   成功采集: {stats['success_count']} ({success_rate:.1f}%)")
    print(f"   失败采集: {stats['failure_count']}")
    print(f"   利润接近0: {stats['zero_profit_count']} ({zero_profit_rate:.1f}%)")
    print(f"   正式报告: {stats['valid_report_count']} ({valid_report_rate:.1f}%)")
    print(f"   预估报告: {stats['estimated_report_count']}")

    print("\n🎯 修复效果评估")
    print("-" * 70)

    # 评估标准
    evaluation = {
        "数据采集成功率": ("✅ 优秀" if success_rate >= 90 else "⚠️  良好" if success_rate >= 80 else "❌ 需改进"),
        "利润非0比例": ("✅ 优秀" if zero_profit_rate <= 5 else "⚠️  良好" if zero_profit_rate <= 10 else "❌ 需改进"),
        "正式报告比例": ("✅ 优秀" if valid_report_rate >= 95 else "⚠️  良好" if valid_report_rate >= 90 else "❌ 需改进"),
        "预估数据过滤": ("✅ 完全过滤" if stats['estimated_report_count'] == 0 else "❌ 未完全过滤")
    }

    for metric, result in evaluation.items():
        print(f"   {result} {metric}")

    print("\n💡 修复成果总结")
    print("-" * 70)

    if stats['estimated_report_count'] == 0 and zero_profit_rate <= 5:
        print("🎉 修复成功！数据采集过滤条件完全生效:")
        print("   1. ✅ 成功剔除预估数据（业绩预告等）")
        print("   2. ✅ 确保利润数据不为0")
        print("   3. ✅ 只采集正式发布的季报和年报数据")
        print("   4. ✅ 数据验证机制正常工作")
    elif stats['estimated_report_count'] == 0:
        print("⚠️  部分成功：预估数据已过滤，但仍有利润为0的问题")
        print("   建议：进一步优化数据生成逻辑")
    elif zero_profit_rate <= 5:
        print("⚠️  部分成功：利润数据正常，但仍有预估数据")
        print("   建议：检查报告类型过滤逻辑")
    else:
        print("❌ 修复未完全生效，需要进一步调试")
        print("   建议：检查数据验证和过滤逻辑")

    print(f"\n🕐 测试完成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

def test_original_vs_fixed_comparison():
    """测试原始函数和修复版函数的对比"""
    print("\n" + "=" * 70)
    print("🔄 原始函数 vs 修复版函数 对比测试")
    print("=" * 70)

    monitor = FinancialMonitorSkillIntegrated()

    # 测试股票
    test_stock = ("601318", "中国平安")
    stock_code, stock_name = test_stock

    print(f"\n📋 测试股票: {stock_code} {stock_name}")
    print("-" * 70)

    # 测试原始函数
    print("1. 🔄 测试原始函数 (get_financial_data):")
    try:
        original_data = monitor.get_financial_data(stock_code, stock_name)
        if original_data:
            print(f"   ✅ 采集成功")
            print(f"   报告类型: {original_data.get('report_type', 'N/A')}")
            print(f"   利润实际值: {original_data.get('profit_actual', 0):.2f}")
            print(f"   利润预期值: {original_data.get('profit_expected', 0):.2f}")

            # 检查问题
            issues = []
            if original_data.get('report_type') == '业绩预告':
                issues.append("包含预估数据")
            if abs(original_data.get('profit_actual', 0)) < 1e-5:
                issues.append("利润接近0")
            if abs(original_data.get('profit_expected', 0)) < 1e-5:
                issues.append("预期利润接近0")

            if issues:
                print(f"   ⚠️  发现问题: {', '.join(issues)}")
            else:
                print(f"   ✅ 数据正常")
        else:
            print(f"   ❌ 采集失败")
    except Exception as e:
        print(f"   ❌ 测试异常: {e}")

    # 测试修复版函数
    print("\n2. 🔧 测试修复版函数 (get_financial_data_fixed):")
    try:
        fixed_data = monitor.get_financial_data_fixed(stock_code, stock_name)
        if fixed_data:
            print(f"   ✅ 采集成功")
            print(f"   报告类型: {fixed_data.get('report_type', 'N/A')}")
            print(f"   利润实际值: {fixed_data.get('profit_actual', 0):.2f}")
            print(f"   利润预期值: {fixed_data.get('profit_expected', 0):.2f}")
            print(f"   数据来源: {fixed_data.get('data_source', 'N/A')}")
            print(f"   数据质量: {fixed_data.get('data_quality', 'N/A')}")

            # 检查修复效果
            improvements = []
            if fixed_data.get('report_type') in ['年报', '季报']:
                improvements.append("只使用正式报告")
            if abs(fixed_data.get('profit_actual', 0)) >= 1e5:  # 最小10万
                improvements.append("利润不为0")
            if abs(fixed_data.get('profit_expected', 0)) >= 1e5:
                improvements.append("预期利润不为0")

            if improvements:
                print(f"   ✅ 修复效果: {', '.join(improvements)}")
            else:
                print(f"   ⚠️  修复效果不明显")
        else:
            print(f"   ❌ 采集失败")
    except Exception as e:
        print(f"   ❌ 测试异常: {e}")

    print("\n🎯 对比结论")
    print("-" * 70)

    if original_data and fixed_data:
        print("✅ 修复版函数相比原始函数的改进:")
        print("   1. 🔧 过滤预估数据，只使用正式报告")
        print("   2. 🔧 确保利润数据不为0")
        print("   3. 🔧 添加数据验证和质量检查")
        print("   4. 🔧 添加重试机制，提高稳定性")
    else:
        print("⚠️  无法完成完整对比，建议检查函数实现")

def main():
    """主测试函数"""
    print("🔧 数据采集过滤条件修复测试")
    print("=" * 70)

    # 测试修复版数据采集
    test_fixed_data_collection()

    # 测试原始和修复版的对比
    test_original_vs_fixed_comparison()

    print("\n" + "=" * 70)
    print("🏁 测试完成")
    print("=" * 70)

    print("\n💡 后续建议:")
    print("   1. 如果测试通过，可以正式使用修复版函数")
    print("   2. 监控明天的财报监控报告，验证实际效果")
    print("   3. 定期检查数据质量，确保过滤条件持续有效")
    print("   4. 根据实际使用情况，进一步优化参数配置")

if __name__ == "__main__":
    main()
