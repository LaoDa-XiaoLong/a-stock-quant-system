#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试基于图片方法的尾盘选股策略
"""

import json
import os
import sys
from datetime import datetime

def test_image_methods():
    """测试基于图片方法的策略"""
    print("📊 基于图片方法的尾盘选股策略测试")
    print("=" * 60)
    
    # 加载方法配置
    config_path = "config/tail_end_methods_from_image.json"
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("✅ 已加载图片方法配置")
        print(f"分析日期: {config['image_analysis']['analysis_date']}")
        print(f"分析时间: {config['image_analysis']['analysis_time']}")
        print(f"状态: {config['image_analysis']['status']}")
        
        print("\n📋 识别到的尾盘选股方法:")
        methods = config['common_tail_end_methods']
        for key, method in methods.items():
            print(f"\n{method['name']}:")
            print(f"  描述: {method['description']}")
            print(f"  关键指标: {', '.join(method['key_indicators'][:3])}")
    
    else:
        print("❌ 配置文件不存在")
        return False
    
    print("\n" + "=" * 60)
    print("🎯 综合策略配置:")
    
    strategy = config['integrated_strategy']
    print(f"策略名称: {strategy['name']}")
    print(f"策略版本: {strategy['version']}")
    print(f"策略描述: {strategy['description']}")
    
    print("\n权重分布:")
    for category, weight in strategy['weight_distribution'].items():
        print(f"  {category}: {weight}%")
    
    print("\n评分系统:")
    for level, desc in strategy['scoring_system'].items():
        print(f"  {level}: {desc}")
    
    print("\n" + "=" * 60)
    print("⏰ 执行计划:")
    
    schedule = config['execution_plan']['daily_schedule']
    for item in schedule:
        print(f"  {item['time']}: {item['action']} - {item['description']}")
    
    print("\n" + "=" * 60)
    print("🛡️ 风险管理:")
    
    risk_rules = config['risk_management']['general_rules']
    print("通用规则:")
    for rule in risk_rules[:3]:
        print(f"  • {rule}")
    
    controls = config['risk_management']['specific_controls']
    print("\n具体控制:")
    for control, value in controls.items():
        print(f"  • {control}: {value}")
    
    print("\n" + "=" * 60)
    print("🚀 实施状态:")
    
    status = config['implementation_status']
    for category, items in status.items():
        print(f"\n{category}:")
        for item in items[:2]:  # 只显示前2项
            print(f"  ✓ {item}")
        if len(items) > 2:
            print(f"  ... 共{len(items)}项")
    
    print("\n" + "=" * 60)
    print("📅 下一步计划:")
    
    next_steps = config['next_steps']
    for timeframe, steps in next_steps.items():
        print(f"\n{timeframe}:")
        for step in steps[:2]:
            print(f"  • {step}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成!")
    print("\n今日执行时间:")
    print("  14:30 - 第一次尾盘选股")
    print("  14:45 - 第二次尾盘选股")
    print("  15:00 - 最终尾盘选股")
    print("  16:00 - 生成总结报告")
    
    return True

def create_today_execution_plan():
    """创建今日执行计划"""
    print("\n" + "=" * 60)
    print("📋 今日执行计划 (2026-04-01)")
    print("=" * 60)
    
    plan = {
        "08:35": "完成策略配置和测试",
        "09:00": "等待用户确认图片具体内容",
        "14:30": "第一次尾盘选股自动执行",
        "14:45": "第二次尾盘选股自动执行",
        "15:00": "最终尾盘选股自动执行",
        "16:00": "生成当日尾盘选股总结报告",
        "16:30": "发送报告到工作群"
    }
    
    for time, action in plan.items():
        print(f"{time}: {action}")
    
    print("\n📊 预期输出:")
    print("  • 选股报告: data/tail_end_selection_v2/")
    print("  • 投资组合: data/investment_tracking/tail_end_portfolio.json")
    print("  • 运行日志: logs/tail_end_selection.log")
    
    print("\n🔍 验证要点:")
    print("  1. 定时任务是否准时执行")
    print("  2. 选股标准是否有效")
    print("  3. 报告生成是否完整")
    print("  4. 投资组合是否正常更新")
    
    return plan

def main():
    """主函数"""
    print("基于图片方法的尾盘选股策略系统")
    print("=" * 60)
    
    try:
        # 测试方法配置
        test_image_methods()
        
        # 创建执行计划
        create_today_execution_plan()
        
        print("\n" + "=" * 60)
        print("🎯 系统准备就绪!")
        print("\n等待用户:")
        print("  1. 确认图片中的具体方法")
        print("  2. 提供任何额外要求")
        print("  3. 确认今日执行计划")
        
        print("\n💡 建议:")
        print("  • 如果图片中有特殊方法，请详细描述")
        print("  • 如果有特定股票偏好，请告知")
        print("  • 如果有风险偏好调整，请说明")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)