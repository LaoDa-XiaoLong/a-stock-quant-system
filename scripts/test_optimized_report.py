#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优化版财报报告模板
生成示例报告并预览效果
"""

import json
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def create_sample_report():
    """创建示例报告数据"""
    
    # 模拟报告数据
    report_date = datetime.now().strftime('%Y-%m-%d')
    
    # 股票数据示例
    sample_stocks = [
        {
            'stock_code': '002594',
            'stock_name': '比亚迪',
            'is_holding': True,
            'report_type': '年报',
            'publish_date': report_date,
            'revenue_actual': 15000000000,
            'revenue_expected': 12000000000,
            'revenue_deviation': 0.243,  # +24.3%
            'profit_actual': 8000000000,
            'profit_expected': 10000000000,
            'profit_deviation': -0.219,  # -21.9%
            'data_quality_score': 100,
            'alert_level': '警报',
            'metric': '营收',
            'surprise_ratio': 0.243
        },
        {
            'stock_code': '603259',
            'stock_name': '药明康德',
            'is_holding': True,
            'report_type': '年报',
            'publish_date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'revenue_actual': 5000000000,
            'revenue_expected': 4000000000,
            'revenue_deviation': 0.224,  # +22.4%
            'profit_actual': 850000000,
            'profit_expected': 1000000000,
            'profit_deviation': -0.150,  # -15.0%
            'data_quality_score': 100,
            'alert_level': '警报',
            'metric': '营收',
            'surprise_ratio': 0.224
        },
        {
            'stock_code': '002415',
            'stock_name': '海康威视',
            'is_holding': True,
            'report_type': '季报',
            'publish_date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
            'revenue_actual': 3000000000,
            'revenue_expected': 2400000000,
            'revenue_deviation': 0.220,  # +22.0%
            'profit_actual': 450000000,
            'profit_expected': 400000000,
            'profit_deviation': 0.141,  # +14.1%
            'data_quality_score': 100,
            'alert_level': '警报',
            'metric': '营收',
            'surprise_ratio': 0.220
        },
        {
            'stock_code': '000858',
            'stock_name': '五粮液',
            'is_holding': True,
            'report_type': '年报',
            'publish_date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'),
            'revenue_actual': 9000000000,
            'revenue_expected': 10000000000,
            'revenue_deviation': -0.131,  # -13.1%
            'profit_actual': 3100000000,
            'profit_expected': 4000000000,
            'profit_deviation': -0.213,  # -21.3%
            'data_quality_score': 100,
            'alert_level': '警报',
            'metric': '营收',
            'surprise_ratio': -0.131
        },
        {
            'stock_code': '600036',
            'stock_name': '招商银行',
            'is_holding': True,
            'report_type': '年报',
            'publish_date': (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d'),
            'revenue_actual': 35000000000,
            'revenue_expected': 32000000000,
            'revenue_deviation': 0.115,  # +11.5%
            'profit_actual': 12000000000,
            'profit_expected': 10000000000,
            'profit_deviation': 0.199,  # +19.9%
            'data_quality_score': 100,
            'alert_level': '正常',
            'metric': '净利润',
            'surprise_ratio': 0.199
        },
        {
            'stock_code': '601318',
            'stock_name': '中国平安',
            'is_holding': True,
            'report_type': '业绩预告',
            'publish_date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
            'revenue_actual': 120000000000,
            'revenue_expected': 140000000000,
            'revenue_deviation': -0.142,  # -14.2%
            'profit_actual': 90000000000,
            'profit_expected': 80000000000,
            'profit_deviation': 0.117,  # +11.7%
            'data_quality_score': 100,
            'alert_level': '正常',
            'metric': '净利润',
            'surprise_ratio': 0.117
        },
        {
            'stock_code': '002352',
            'stock_name': '顺丰控股',
            'is_holding': True,
            'report_type': '年报',
            'publish_date': (datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d'),
            'revenue_actual': 28000000000,
            'revenue_expected': 27500000000,
            'revenue_deviation': 0.022,  # +2.2%
            'profit_actual': 6500000000,
            'profit_expected': 6520000000,
            'profit_deviation': -0.003,  # -0.3%
            'data_quality_score': 100,
            'alert_level': '正常',
            'metric': '营收',
            'surprise_ratio': 0.022
        }
    ]
    
    # 构建完整报告
    report = {
        'date': report_date,
        'total_stocks': 12,
        'valid_stocks': 12,
        'holdings_surprises': 4,
        'all_surprises': 4,
        'data_quality_score': 100.0,
        'trading_advice': '市场整体向好，持仓股票超预期，建议关注新能源汽车、医药、安防行业',
        'stocks': sample_stocks,
        'holdings': sample_stocks[:7],  # 前7只是持仓
        'surprises': [s for s in sample_stocks if abs(s['surprise_ratio']) >= 0.20],
        'industry_stats': {
            '新能源汽车': {'total': 1, 'surprises': 1, 'holdings': 1},
            '医药': {'total': 1, 'surprises': 1, 'holdings': 1},
            '安防': {'total': 1, 'surprises': 1, 'holdings': 1},
            '白酒': {'total': 1, 'surprises': 0, 'holdings': 1},
            '银行': {'total': 1, 'surprises': 1, 'holdings': 1},
            '保险': {'total': 1, 'surprises': 0, 'holdings': 1},
            '物流': {'total': 1, 'surprises': 0, 'holdings': 1}
        }
    }
    
    return report


def test_core_summary():
    """测试核心摘要生成"""
    print("=" * 60)
    print("📋 测试核心摘要生成")
    print("=" * 60)
    
    from send_financial_report_optimized import OptimizedFinancialReportSender
    
    # 创建发送器实例
    sender = OptimizedFinancialReportSender()
    
    # 创建示例报告
    report = create_sample_report()
    
    # 生成核心摘要
    core_summary = sender.generate_core_summary(report)
    
    print("\n📱 核心摘要预览（飞书消息格式）:")
    print("-" * 40)
    print(core_summary)
    print("-" * 40)
    
    # 统计信息
    lines = core_summary.split('\n')
    char_count = len(core_summary)
    line_count = len(lines)
    
    print(f"\n📊 统计信息:")
    print(f"• 总字符数: {char_count}")
    print(f"• 行数: {line_count}")
    print(f"• 建议长度: {'✅ 合适' if char_count < 1000 else '⚠️ 可能过长'}")
    
    return core_summary


def test_detailed_analysis():
    """测试详细分析生成"""
    print("\n" + "=" * 60)
    print("📊 测试详细分析生成")
    print("=" * 60)
    
    from send_financial_report_optimized import OptimizedFinancialReportSender
    
    # 创建发送器实例
    sender = OptimizedFinancialReportSender()
    
    # 创建示例报告
    report = create_sample_report()
    
    # 生成详细分析
    detailed_analysis = sender.generate_detailed_analysis(report)
    
    print("\n📄 详细分析预览（前200字符）:")
    print("-" * 40)
    print(detailed_analysis[:500] + "..." if len(detailed_analysis) > 500 else detailed_analysis)
    print("-" * 40)
    
    # 统计信息
    char_count = len(detailed_analysis)
    
    print(f"\n📊 统计信息:")
    print(f"• 总字符数: {char_count}")
    print(f"• 建议: 作为第二层消息或附件发送")
    
    return detailed_analysis


def test_message_length_control():
    """测试消息长度控制"""
    print("\n" + "=" * 60)
    print("📏 测试消息长度控制")
    print("=" * 60)
    
    from send_financial_report_optimized import OptimizedFinancialReportSender
    
    sender = OptimizedFinancialReportSender()
    report = create_sample_report()
    
    # 生成两种消息
    core_summary = sender.generate_core_summary(report)
    detailed_analysis = sender.generate_detailed_analysis(report)
    
    print("📱 核心摘要长度分析:")
    print(f"• 字符数: {len(core_summary)}")
    print(f"• 飞书限制: 约2000字符")
    print(f"• 状态: {'✅ 安全' if len(core_summary) < 1500 else '⚠️ 接近限制'}")
    
    print("\n📄 详细分析长度分析:")
    print(f"• 字符数: {len(detailed_analysis)}")
    print(f"• 建议: {'✅ 可作为第二层消息' if len(detailed_analysis) < 3000 else '📎 建议作为附件'}")
    
    # 检查是否有截断风险
    print("\n🔍 截断风险检查:")
    
    # 检查长行
    lines = core_summary.split('\n')
    long_lines = [line for line in lines if len(line) > 100]
    
    if long_lines:
        print(f"⚠️ 发现{len(long_lines)}行长于100字符:")
        for i, line in enumerate(long_lines[:3], 1):
            print(f"  {i}. {line[:50]}...")
    else:
        print("✅ 无过长行，适合移动端显示")


def preview_final_output():
    """预览最终输出效果"""
    print("\n" + "=" * 60)
    print("🎯 最终输出效果预览")
    print("=" * 60)
    
    from send_financial_report_optimized import OptimizedFinancialReportSender
    
    sender = OptimizedFinancialReportSender()
    report = create_sample_report()
    
    print("\n📱 第一层：核心摘要（即时发送）")
    print("-" * 40)
    core = sender.generate_core_summary(report)
    print(core)
    
    print("\n⏳ 等待5秒...")
    print("\n📄 第二层：详细分析（补充发送）")
    print("-" * 40)
    detailed = sender.generate_detailed_analysis(report)
    
    # 显示详细分析的前面部分
    lines = detailed.split('\n')
    for i, line in enumerate(lines[:20]):  # 只显示前20行
        print(line)
    
    if len(lines) > 20:
        print("...（完整内容共{}行）".format(len(lines)))
    
    print("\n✅ 分层发送方案预览完成")
    print("• 第一层：核心信息，快速阅读")
    print("• 第二层：详细分析，深度了解")
    print("• 避免信息过载，提升阅读体验")


def main():
    """主测试函数"""
    print("🚀 开始测试优化版财报报告模板")
    print("=" * 60)
    
    try:
        # 运行各项测试
        test_core_summary()
        test_detailed_analysis()
        test_message_length_control()
        preview_final_output()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试完成！")
        print("=" * 60)
        
        print("\n🎯 优化版模板优势总结:")
        print("1. ✅ 信息完整：包含所有关键维度")
        print("2. ✅ 避免截断：分层发送，控制长度")
        print("3. ✅ 阅读友好：移动端优化格式")
        print("4. ✅ 重点突出：核心摘要3秒可读")
        print("5. ✅ 实用性强：明确的交易建议")
        
        print("\n🔧 实施建议:")
        print("1. 替换现有的 send_financial_report.py")
        print("2. 更新调度任务配置")
        print("3. 测试实际发送效果")
        print("4. 根据反馈迭代优化")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)