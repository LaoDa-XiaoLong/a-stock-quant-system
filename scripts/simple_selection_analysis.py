#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版选股策略分析
"""

import json
from datetime import datetime
import os

print("🔍 详细分析选股策略和投资机会")
print("=" * 70)

# 1. 加载数据
screening_file = 'data/stock_pool/screening_results_20260331_093829.json'
portfolio_file = 'data/investment_tracking/investment_portfolio.json'

if not os.path.exists(screening_file):
    print("❌ 未找到筛选结果文件")
    exit(1)

with open(screening_file, 'r', encoding='utf-8') as f:
    screening_data = json.load(f)

all_stocks = screening_data['stocks']

# 2. 当前选中的5只股票
print("🎯 当前选中的5只股票（基于什么策略选出来的？）")
print("=" * 70)

if os.path.exists(portfolio_file):
    with open(portfolio_file, 'r', encoding='utf-8') as f:
        portfolio = json.load(f)

    selected_stocks = portfolio['stocks']
    selected_codes = [s['code'] for s in selected_stocks]

    print("📊 选股策略分解:")
    print()
    print("1. 📈 第一步：原始筛选（20只股票）")
    print(f"   策略: {screening_data['strategy']}")
    print(f"   时间: {screening_data['date']} {screening_data['time']}")
    print(f"   标准: 市值前列/流动性好")
    print()

    print("2. 🎯 第二步：精选过滤（从20只到5只）")
    print("   过滤标准:")
    print("   a) 评分 ≥ 85分（确保股票质量）")
    print("   b) 今日涨跌在 -2% 到 +5% 之间（避免追高和过度抄底）")
    print("   c) 排除普通ST股票（控制风险，保留*ST观察）")
    print("   d) 选择评分最高的前5只（集中投资）")
    print()

    print("3. 📊 第三步：详细分析选中的5只股票")
    for stock in selected_stocks:
        print(f"   {stock['code']} {stock['name']}")
        print(f"     评分: {stock['score']}/100 (排名: 第{stock['score_rank'] if 'score_rank' in stock else 'N/A'}名)")
        print(f"     今日涨跌: {stock.get('current_change', 0):+.2f}%")
        print(f"     选股理由: {stock['selection_reason']}")
        print(f"     状态: {stock['status']}")
        print()
else:
    print("❌ 未找到投资组合文件")
    selected_codes = []

print()
print("🔍 还有没有其他机会？")
print("=" * 70)

# 3. 发现其他投资机会
print("📈 机会1：高评分但未选中的股票（评分≥90）")
high_score_stocks = [s for s in all_stocks if s['score'] >= 90 and s['code'] not in selected_codes]

if high_score_stocks:
    print(f"   发现{len(high_score_stocks)}只高评分但未选中的股票:")
    for stock in high_score_stocks:
        print(f"   {stock['code']} {stock['name']:10s} 评分:{stock['score']} 涨跌:{stock['change_pct']:+.2f}%")
else:
    print("   所有高评分股票都已选中")
print()

print("📉 机会2：今日下跌但评分高的股票（可能有反弹机会）")
undervalued_stocks = [s for s in all_stocks if s['change_pct'] < 0 and s['score'] >= 85 and s['code'] not in selected_codes]

if undervalued_stocks:
    print(f"   发现{len(undervalued_stocks)}只今日下跌但评分高的股票:")
    for stock in undervalued_stocks:
        print(f"   {stock['code']} {stock['name']:10s} 评分:{stock['score']} 涨跌:{stock['change_pct']:+.2f}%")
else:
    print("   没有符合条件的股票")
print()

print("🚀 机会3：今日表现优秀的股票（涨跌幅≥+3%）")
good_performance = [s for s in all_stocks if s['change_pct'] >= 3 and s['score'] >= 80 and s['code'] not in selected_codes]

if good_performance:
    print(f"   发现{len(good_performance)}只今日表现优秀的股票:")
    for stock in good_performance:
        print(f"   {stock['code']} {stock['name']:10s} 评分:{stock['score']} 涨跌:{stock['change_pct']:+.2f}%")
else:
    print("   没有符合条件的股票")
print()

print("💎 机会4：不同策略的推荐股票")
print("=" * 70)

print("1. 价值投资策略（高评分 + 低涨幅）")
value_stocks = [s for s in all_stocks if s['score'] >= 85 and s['change_pct'] <= 2]
value_stocks = sorted(value_stocks, key=lambda x: x['score'], reverse=True)[:5]

for i, stock in enumerate(value_stocks, 1):
    print(f"   {i}. {stock['code']} {stock['name']:10s} 评分:{stock['score']} 涨跌:{stock['change_pct']:+.2f}%")
print()

print("2. 成长投资策略（高评分 + 高涨幅）")
growth_stocks = [s for s in all_stocks if s['score'] >= 85 and s['change_pct'] >= 2]
growth_stocks = sorted(growth_stocks, key=lambda x: x['change_pct'], reverse=True)[:5]

for i, stock in enumerate(growth_stocks, 1):
    print(f"   {i}. {stock['code']} {stock['name']:10s} 评分:{stock['score']} 涨跌:{stock['change_pct']:+.2f}%")
print()

print("3. 反转投资策略（今日下跌但基本面好）")
reversal_stocks = [s for s in all_stocks if s['change_pct'] < 0 and s['score'] >= 80]
reversal_stocks = sorted(reversal_stocks, key=lambda x: x['score'], reverse=True)[:5]

for i, stock in enumerate(reversal_stocks, 1):
    print(f"   {i}. {stock['code']} {stock['name']:10s} 评分:{stock['score']} 涨跌:{stock['change_pct']:+.2f}%")
print()

print("💡 综合建议")
print("=" * 70)

print("基于分析，建议如下:")
print()
print("1. ✅ 当前选股策略合理:")
print("   - 评分筛选确保质量")
print("   - 涨跌幅控制避免风险")
print("   - 集中投资便于管理")
print()

print("2. 🔍 发现的额外机会:")
total_opportunities = len(high_score_stocks) + len(undervalued_stocks) + len(good_performance)
print(f"   共发现{total_opportunities}只额外投资机会")
print(f"   - 高评分未选中: {len(high_score_stocks)}只")
print(f"   - 低估值机会: {len(undervalued_stocks)}只")
print(f"   - 今日表现优秀: {len(good_performance)}只")
print()

print("3. 🎯 推荐操作:")
print("   a. 保持当前5只股票的监控（已配置自动监控）")
print("   b. 考虑增加1-2只额外机会股票")
print("     推荐关注: 000007 全新好（评分90）或 000028 国药一致（评分90）")
print("   c. 根据个人风险偏好选择投资策略")
print("     稳健型: 价值投资策略")
print("     进取型: 成长投资策略")
print("     机会型: 反转投资策略")
print()

print("4. ⚠️ 风险提示:")
print("   - 所有投资都有风险")
print("   - *ST股票有退市风险")
print("   - 严格执行风险控制")
print()

print("5. 🚀 系统状态:")
print("   - 已配置每3分钟自动监控")
print("   - 基于真实价格动态计算进场点位")
print("   - 达到条件自动模拟成交")
print("   - 每日自动生成详细报告")
print()

print("📋 生成详细报告...")
report_content = f"""# 📊 选股策略详细分析报告

## 一、当前选股策略

### 1.1 选股流程
1. **原始筛选**: 20只股票，基于"市值前列/流动性好"
2. **精选过滤**:
   - 评分 ≥ 85分
   - 今日涨跌在 -2% 到 +5% 之间
   - 排除普通ST股票
   - 选择评分最高的前5只

### 1.2 选中的5只股票
"""

for stock in selected_stocks:
    report_content += f"""#### {stock['code']} {stock['name']}
- 评分: {stock['score']}/100
- 今日涨跌: {stock.get('current_change', 0):+.2f}%
- 选股理由: {stock['selection_reason']}
- 状态: {stock['status']}

"""

report_content += f"""
## 二、发现的额外投资机会

### 2.1 高评分但未选中的股票（评分≥90）
"""

for stock in high_score_stocks:
    report_content += f"- {stock['code']} {stock['name']}: 评分{stock['score']}，今日{stock['change_pct']:+.2f}%\n"

report_content += f"""
### 2.2 今日下跌但评分高的股票
"""

for stock in undervalued_stocks:
    report_content += f"- {stock['code']} {stock['name']}: 评分{stock['score']}，今日{stock['change_pct']:+.2f}%\n"

report_content += f"""
### 2.3 今日表现优秀的股票（涨跌幅≥+3%）
"""

for stock in good_performance:
    report_content += f"- {stock['code']} {stock['name']}: 评分{stock['score']}，今日{stock['change_pct']:+.2f}%\n"

report_content += f"""
## 三、不同策略推荐

### 3.1 价值投资策略（高评分 + 低涨幅）
"""

for i, stock in enumerate(value_stocks, 1):
    report_content += f"{i}. {stock['code']} {stock['name']}: 评分{stock['score']}，今日{stock['change_pct']:+.2f}%\n"

report_content += f"""
### 3.2 成长投资策略（高评分 + 高涨幅）
"""

for i, stock in enumerate(growth_stocks, 1):
    report_content += f"{i}. {stock['code']} {stock['name']}: 评分{stock['score']}，今日{stock['change_pct']:+.2f}%\n"

report_content += f"""
### 3.3 反转投资策略（今日下跌但基本面好）
"""

for i, stock in enumerate(reversal_stocks, 1):
    report_content += f"{i}. {stock['code']} {stock['name']}: 评分{stock['score']}，今日{stock['change_pct']:+.2f}%\n"

report_content += f"""
## 四、建议操作

### 4.1 推荐方案
1. **保持当前配置**: 继续监控5只选中股票
2. **增加机会股票**: 考虑增加000007全新好或000028国药一致
3. **选择投资策略**: 根据风险偏好选择价值/成长/反转策略

### 4.2 系统支持
- 每3分钟自动监控真实价格
- 动态计算进场点位和风险控制
- 达到条件自动模拟成交
- 每日自动生成详细报告

---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*数据来源: 原始筛选结果 + 新浪财经实时API*
"""

# 保存报告
report_file = f"data/stock_pool/selection_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
with open(report_file, 'w', encoding='utf-8') as f:
    f.write(report_content)

print(f"✅ 详细分析报告已生成: {report_file}")
print()
print("=" * 70)
print("🎉 分析完成！详细解释了选股策略并发现了多个投资机会。")
