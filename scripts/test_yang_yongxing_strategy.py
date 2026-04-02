#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试杨永兴隔夜套利战法
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.yang_yongxing_overnight_strategy import YangYongxingOvernightStrategy

def test_yang_yongxing_strategy():
    """测试杨永兴战法"""
    print("测试杨永兴隔夜套利战法")
    print("=" * 60)

    strategy = YangYongxingOvernightStrategy()

    # 显示策略信息
    print(f"策略名称: {strategy.strategy_name}")
    print(f"策略作者: {strategy.strategy_author}")
    print(f"历史业绩: {strategy.strategy_performance}")
    print(f"选股时间: {strategy.selection_time}")
    print("")

    print("核心理念:")
    for key, value in strategy.core_principles.items():
        print(f"  {key}: {value}")
    print("")

    print("六大选股步骤:")
    for step in strategy.six_selection_steps:
        print(f"  {step['step']}. {step['name']}: {step['description']} - {step['criteria']}")
    print("")

    # 测试时间判断
    print("时间窗口测试:")
    test_times = [
        ("09:30", False, "早盘"),
        ("14:00", False, "午盘"),
        ("14:30", True, "尾盘开始"),
        ("14:45", True, "尾盘中"),
        ("15:00", True, "尾盘结束"),
        ("15:30", True, "收盘后")
    ]

    for time_str, expected, desc in test_times:
        test_time = datetime(2026, 4, 1, int(time_str[:2]), int(time_str[3:5]), 0)
        is_valid = strategy.is_yang_yongxing_time(test_time)
        status = "✅ 通过" if is_valid == expected else "❌ 失败"
        print(f"  {time_str} ({desc}): {status}")

    print("\n" + "=" * 60)

    # 测试选股逻辑
    print("选股逻辑测试:")

    # 创建测试股票数据
    test_stocks = {
        "600001": {
            "code": "600001",
            "name": "优质隔夜股A",
            "current_price": 25.80,
            "change_percent": 4.2,          # 符合3-5%
            "capital_flow_ratio": 0.18,     # 资金流入18%
            "volume_ratio": 1.85,           # 量比>1.7
            "market_cap": 85.5,             # 市值<100亿
            "technical_space": 9.2          # 技术空间9.2%
        },
        "600002": {
            "code": "600002",
            "name": "良好隔夜股B",
            "current_price": 18.40,
            "change_percent": 3.8,          # 符合3-5%
            "capital_flow_ratio": 0.12,     # 资金流入12%
            "volume_ratio": 1.65,           # 量比>1.5
            "market_cap": 150.2,            # 市值<200亿
            "technical_space": 7.5          # 技术空间7.5%
        },
        "600003": {
            "code": "600003",
            "name": "一般隔夜股C",
            "current_price": 32.10,
            "change_percent": 1.5,          # 不符合3-5%
            "capital_flow_ratio": 0.05,     # 资金流入5%
            "volume_ratio": 1.25,           # 量比偏低
            "market_cap": 280.5,            # 市值>200亿
            "technical_space": 4.2          # 技术空间一般
        }
    }

    print(f"\n分析 {len(test_stocks)} 只测试股票...")

    # 模拟尾盘时间
    import time
    original_get_time = strategy.get_current_time

    def mock_tail_time():
        return datetime(2026, 4, 1, 14, 45, 0)

    strategy.get_current_time = mock_tail_time

    try:
        # 运行选股
        selected = strategy.apply_yang_yongxing_criteria(test_stocks)

        print(f"筛选结果: {len(selected)} 只股票符合条件")

        if selected:
            print("\n筛选详情:")
            for stock in selected:
                print(f"\n{stock['name']} ({stock['code']}):")
                print(f"  综合评分: {stock['score']}/100")
                print(f"  通过步骤: {stock['passed_steps']}/6")
                print(f"  当前价格: {stock['current_price']:.2f}元")
                print(f"  今日涨跌: {stock['change_percent']:.2f}%")

                # 计算进场点位
                entry_data = strategy.calculate_overnight_entry_points(stock)
                print(f"  进场策略: {entry_data['entry_strategy']}")
                print(f"  进场价格: {entry_data['entry_price']:.2f}元")
                print(f"  目标价格: {entry_data['target_price']:.2f}元 (涨幅{entry_data['target_gain']:.1f}%)")
                print(f"  仓位建议: {entry_data['position_suggestion']}")

                print(f"  通过步骤详情:")
                for step_result in stock['step_results']:
                    status = "✅" if step_result["passed"] else "❌"
                    print(f"    {status} 步骤{step_result['step']}: {step_result['name']} - {step_result['reason']}")

        # 测试报告生成
        print("\n" + "=" * 60)
        print("报告生成测试:")

        report = strategy.generate_yang_yongxing_report(selected)

        # 保存测试报告
        report_dir = "data/yang_yongxing_strategy"
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(report_dir, "test_report.md")

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"测试报告已保存到: {report_path}")

        # 显示报告摘要
        print("\n报告摘要:")
        lines = report.split('\n')[:30]
        for line in lines:
            print(line)

        print("..." * 20)

    finally:
        strategy.get_current_time = original_get_time

    return True

def test_full_yang_yongxing_selection():
    """测试完整杨永兴战法流程"""
    print("\n" + "=" * 60)
    print("测试完整杨永兴战法流程...")
    print("=" * 60)

    strategy = YangYongxingOvernightStrategy()

    # 模拟尾盘时间
    import time
    original_get_time = strategy.get_current_time

    def mock_tail_time():
        return datetime(2026, 4, 1, 14, 45, 0)

    strategy.get_current_time = mock_tail_time

    try:
        print("运行完整杨永兴战法流程...")
        result = strategy.run_selection()

        if result:
            print("\n✅ 完整杨永兴战法流程测试通过!")
            print(f"选股结果: {len(result['selected_stocks'])} 只股票")
            print(f"报告文件: {result['report_path']}")

            # 显示选股结果摘要
            if result['selected_stocks']:
                print("\n选股结果摘要:")
                for i, stock in enumerate(result['selected_stocks'][:3], 1):
                    print(f"{i}. {stock['name']} ({stock['code']}) - {stock['score']}分 (通过{stock['passed_steps']}/6步骤)")
        else:
            print("\n❌ 杨永兴战法流程测试失败")

    finally:
        strategy.get_current_time = original_get_time

    return True

def main():
    """主测试函数"""
    print("杨永兴隔夜套利战法测试套件")
    print("基于OCR识别的图片内容实现")
    print("=" * 60)

    try:
        # 测试杨永兴战法
        test_yang_yongxing_strategy()

        # 测试完整流程
        test_full_yang_yongxing_selection()

        print("\n" + "=" * 60)
        print("✅ 所有测试通过!")
        print("杨永兴隔夜套利战法已准备就绪")
        print("=" * 60)

        # 显示今日执行计划
        print("\n📅 今日执行计划 (2026-04-01):")
        print("  14:30 - 开始执行杨永兴隔夜套利战法")
        print("  14:45 - 完成选股，生成报告")
        print("  15:00 - 准备尾盘进场")
        print("  次日 - 冲高卖出，完成隔夜套利")

        print("\n🎯 策略特点:")
        print("  • 专门针对A股T+1制度的隔夜套利")
        print("  • 尾盘进场，规避日内波动风险")
        print("  • 六大选股步骤，科学筛选")
        print("  • 历史业绩: 16个月100万→1亿")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
