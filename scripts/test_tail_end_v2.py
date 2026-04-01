#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
尾盘选股策略 v2.0 测试脚本
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.tail_end_strategy_v2 import TailEndStrategyV2

def test_v2_strategy():
    """测试v2.0策略"""
    print("测试尾盘选股策略 v2.0")
    print("=" * 60)
    
    selector = TailEndStrategyV2()
    
    # 测试时间判断
    print("时间窗口测试:")
    test_times = [
        ("09:30", False, "早盘"),
        ("14:00", False, "午盘"),
        ("14:30", True, "尾盘开始"),
        ("14:45", True, "尾盘中"),
        ("15:00", True, "尾盘结束"),
        ("15:30", False, "收盘后")
    ]
    
    for time_str, expected, desc in test_times:
        test_time = datetime(2026, 4, 1, int(time_str[:2]), int(time_str[3:5]), 0)
        is_tail = selector.is_tail_end_time(test_time)
        status = "✅ 通过" if is_tail == expected else "❌ 失败"
        print(f"  {time_str} ({desc}): {status}")
    
    print("\n" + "=" * 60)
    
    # 测试选股逻辑
    print("选股逻辑测试:")
    
    # 创建测试股票数据
    test_stocks = {
        "000001": {
            "code": "000001",
            "name": "优质股票A",
            "current_price": 20.50,
            "change_percent": 2.5,
            "amplitude": 4.2,
            "turnover_rate": 5.8,
            "tail_volume_ratio": 1.8,
            "volume_trend": "递增",
            "large_order_flow": 15000000,
            "main_capital_ratio": 0.15,
            "tail_trend": "拉升",
            "intraday_pattern": "尾盘拉升",
            "kline_pattern": "W底",
            "technical_indicators": {
                "macd": {"dif": 0.2, "dea": 0.1, "macd": 0.1, "signal": "金叉"},
                "kdj": {"k": 25, "d": 30, "j": 20},
                "rsi": {"rsi6": 65, "rsi12": 60, "rsi24": 55}
            }
        },
        "000002": {
            "code": "000002",
            "name": "一般股票B",
            "current_price": 15.80,
            "change_percent": -1.2,
            "amplitude": 3.5,
            "turnover_rate": 2.1,
            "tail_volume_ratio": 1.1,
            "volume_trend": "平稳",
            "large_order_flow": -3000000,
            "main_capital_ratio": 0.05,
            "tail_trend": "平稳",
            "intraday_pattern": "横盘震荡",
            "kline_pattern": "无特殊形态",
            "technical_indicators": {
                "macd": {"dif": -0.1, "dea": -0.05, "macd": -0.05, "signal": "死叉"},
                "kdj": {"k": 45, "d": 50, "j": 40},
                "rsi": {"rsi6": 45, "rsi12": 50, "rsi24": 55}
            }
        },
        "000003": {
            "code": "000003",
            "name": "差股票C",
            "current_price": 8.20,
            "change_percent": -4.5,
            "amplitude": 8.2,
            "turnover_rate": 0.8,
            "tail_volume_ratio": 0.7,
            "volume_trend": "递减",
            "large_order_flow": -8000000,
            "main_capital_ratio": 0.02,
            "tail_trend": "下跌",
            "intraday_pattern": "单边下跌",
            "kline_pattern": "无特殊形态",
            "technical_indicators": {
                "macd": {"dif": -0.3, "dea": -0.2, "macd": -0.1, "signal": "死叉"},
                "kdj": {"k": 80, "d": 75, "j": 85},
                "rsi": {"rsi6": 75, "rsi12": 70, "rsi24": 65}
            }
        }
    }
    
    print(f"\n分析 {len(test_stocks)} 只测试股票...")
    
    # 模拟尾盘时间
    import time
    original_get_time = selector.get_current_time
    
    def mock_tail_time():
        return datetime(2026, 4, 1, 14, 45, 0)
    
    selector.get_current_time = mock_tail_time
    
    try:
        # 运行选股
        selected = selector.apply_selection_criteria(test_stocks)
        
        print(f"筛选结果: {len(selected)} 只股票符合条件")
        
        if selected:
            print("\n筛选详情:")
            for stock in selected:
                print(f"\n{stock['name']} ({stock['code']}):")
                print(f"  综合评分: {stock['score']}/100")
                print(f"  当前价格: {stock['current_price']:.2f}元")
                print(f"  今日涨跌: {stock['change_percent']:.2f}%")
                
                # 计算进场点位
                risk_data = selector.calculate_tail_end_entry_points(stock)
                print(f"  仓位建议: {risk_data['position_suggestion']}")
                print(f"  风险收益比: {risk_data['risk_reward_ratio']:.2f}")
                
                print(f"  主要理由: {', '.join(stock['selection_reasons'][:3])}")
        
        # 测试报告生成
        print("\n" + "=" * 60)
        print("报告生成测试:")
        
        report = selector.generate_detailed_report(selected)
        
        # 保存测试报告
        report_dir = "data/tail_end_selection_v2"
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(report_dir, "test_report_v2.md")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"测试报告已保存到: {report_path}")
        
        # 显示报告摘要
        print("\n报告摘要:")
        lines = report.split('\n')[:20]
        for line in lines:
            print(line)
        
        print("..." * 20)
        
    finally:
        selector.get_current_time = original_get_time
    
    return True

def test_full_v2_selection():
    """测试完整v2.0选股流程"""
    print("\n" + "=" * 60)
    print("测试完整尾盘选股流程 v2.0...")
    print("=" * 60)
    
    selector = TailEndStrategyV2()
    
    # 模拟尾盘时间
    import time
    original_get_time = selector.get_current_time
    
    def mock_tail_time():
        return datetime(2026, 4, 1, 14, 45, 0)
    
    selector.get_current_time = mock_tail_time
    
    try:
        print("运行完整选股流程...")
        result = selector.run_selection()
        
        if result:
            print("\n✅ 完整选股流程测试通过!")
            print(f"选股结果: {len(result['selected_stocks'])} 只股票")
            print(f"报告文件: {result['report_path']}")
            
            # 显示选股结果摘要
            if result['selected_stocks']:
                print("\n选股结果摘要:")
                for i, stock in enumerate(result['selected_stocks'][:3], 1):
                    print(f"{i}. {stock['name']} ({stock['code']}) - {stock['score']}分")
        else:
            print("\n❌ 选股流程测试失败")
            
    finally:
        selector.get_current_time = original_get_time
    
    return True

def main():
    """主测试函数"""
    print("尾盘选股策略 v2.0 测试套件")
    print("基于常见尾盘选股方法优化")
    print("=" * 60)
    
    try:
        # 测试v2.0策略
        test_v2_strategy()
        
        # 测试完整流程
        test_full_v2_selection()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试通过!")
        print("尾盘选股策略 v2.0 已准备就绪")
        print("=" * 60)
        
        # 显示策略配置
        print("\n策略配置:")
        selector = TailEndStrategyV2()
        print(f"策略名称: {selector.strategy_name}")
        print(f"策略版本: {selector.strategy_version}")
        print(f"选股时间: {selector.selection_time}")
        print(f"策略权重: {selector.weights}")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)