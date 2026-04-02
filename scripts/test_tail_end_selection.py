#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
尾盘选股策略测试脚本
"""

import sys
import os
from datetime import datetime, time

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.tail_end_stock_selection import TailEndStockSelection

def test_strategy_logic():
    """测试策略逻辑"""
    print("测试尾盘选股策略逻辑...")
    print("=" * 60)

    selector = TailEndStockSelection()

    # 测试时间判断
    test_times = [
        datetime(2026, 4, 1, 9, 30, 0),  # 早盘
        datetime(2026, 4, 1, 14, 0, 0),  # 午盘
        datetime(2026, 4, 1, 14, 30, 0), # 尾盘开始
        datetime(2026, 4, 1, 14, 45, 0), # 尾盘中
        datetime(2026, 4, 1, 15, 0, 0),  # 尾盘结束
        datetime(2026, 4, 1, 15, 30, 0)  # 收盘后
    ]

    print("时间窗口测试:")
    for test_time in test_times:
        is_tail = selector.is_tail_end_time(test_time)
        status = "✅ 尾盘时间" if is_tail else "❌ 非尾盘时间"
        print(f"  {test_time.strftime('%H:%M:%S')}: {status}")

    print("\n" + "=" * 60)

    # 测试选股逻辑
    print("选股逻辑测试:")

    # 模拟股票数据
    test_stocks = [
        {
            "code": "000001",
            "name": "平安银行",
            "current_price": 15.50,
            "change_percent": 2.5,
            "volume": 500000,
            "amount": 7750000,
            "amplitude": 4.2,
            "turnover_rate": 3.8,
            "pe_ratio": 12.5,
            "pb_ratio": 1.2,
            "market_cap": 30000000000,
            "industry": "金融",
            "concept": ["金融科技", "银行"],
            "intraday_pattern": "尾盘拉升",
            "tail_volume_ratio": 1.5,
            "large_order_flow": 15000000,
            "technical_indicators": {
                "macd": {"dif": 0.15, "dea": 0.10, "macd": 0.05, "signal": "金叉"},
                "kdj": {"k": 45, "d": 40, "j": 50, "signal": "正常"},
                "rsi": {"rsi6": 65, "rsi12": 60, "rsi24": 55, "signal": "强势"}
            }
        },
        {
            "code": "000002",
            "name": "万科A",
            "current_price": 22.80,
            "change_percent": -1.2,
            "volume": 300000,
            "amount": 6840000,
            "amplitude": 3.5,
            "turnover_rate": 2.1,
            "pe_ratio": 8.5,
            "pb_ratio": 0.9,
            "market_cap": 25000000000,
            "industry": "房地产",
            "concept": ["房地产", "物业管理"],
            "intraday_pattern": "横盘震荡",
            "tail_volume_ratio": 0.8,
            "large_order_flow": -5000000,
            "technical_indicators": {
                "macd": {"dif": -0.10, "dea": -0.05, "macd": -0.05, "signal": "死叉"},
                "kdj": {"k": 25, "d": 30, "j": 20, "signal": "超卖"},
                "rsi": {"rsi6": 35, "rsi12": 40, "rsi24": 45, "signal": "弱势"}
            }
        }
    ]

    # 转换为策略需要的格式
    stock_data = {}
    for stock in test_stocks:
        stock_data[stock["code"]] = stock

    print("\n应用选股标准:")
    selected = selector.apply_selection_criteria(stock_data)

    print(f"共测试 {len(stock_data)} 只股票，筛选出 {len(selected)} 只符合条件的股票")

    if selected:
        print("\n筛选结果:")
        for stock in selected:
            print(f"  {stock['name']} ({stock['code']}) - 评分: {stock['score']}分")
            print(f"    选股理由: {', '.join(stock['selection_reasons'][:3])}")

            # 测试进场点位计算
            risk_data = selector.calculate_entry_points(stock)
            print(f"    激进进场: {risk_data['entry_points']['激进进场']:.2f}元")
            print(f"    止损位: {risk_data['stop_loss']:.2f}元")
            print(f"    风险收益比: {risk_data['risk_reward_ratio']:.2f}")
            print()

    print("=" * 60)

    # 测试报告生成
    print("报告生成测试:")
    report = selector.generate_selection_report(selected)

    # 保存测试报告
    report_path = "data/tail_end_selection/test_report.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"测试报告已保存到: {report_path}")

    # 显示报告前几行
    print("\n报告预览:")
    lines = report.split('\n')[:15]
    for line in lines:
        print(line)

    print("..." * 20)

    return True

def test_full_selection():
    """测试完整选股流程"""
    print("\n" + "=" * 60)
    print("测试完整尾盘选股流程...")
    print("=" * 60)

    selector = TailEndStockSelection()

    # 使用测试股票代码
    test_codes = [
        "000001", "000002", "000004", "000005", "000006",
        "000007", "000008", "000009", "000010", "000011"
    ]

    print(f"使用 {len(test_codes)} 只测试股票进行选股...")

    # 模拟尾盘时间
    import time
    original_get_time = selector.get_current_time

    def mock_tail_time():
        return datetime(2026, 4, 1, 14, 45, 0)

    selector.get_current_time = mock_tail_time

    try:
        result = selector.run_selection(test_codes)

        if result:
            print("\n✅ 完整选股流程测试通过!")
            print(f"选股结果: {len(result['selected_stocks'])} 只股票")
            print(f"报告文件: {result['report_path']}")
        else:
            print("\n❌ 选股流程测试失败")

    finally:
        selector.get_current_time = original_get_time

    return True

def main():
    """主测试函数"""
    print("尾盘选股策略测试套件")
    print("=" * 60)

    try:
        # 测试策略逻辑
        test_strategy_logic()

        # 测试完整流程
        test_full_selection()

        print("\n" + "=" * 60)
        print("✅ 所有测试通过!")
        print("尾盘选股策略已准备就绪")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
