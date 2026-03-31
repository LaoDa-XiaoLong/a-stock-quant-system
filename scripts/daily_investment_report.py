#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日投资报告生成脚本
收盘后自动运行，生成当日投资报告
"""

import json
import pandas as pd
from datetime import datetime, timedelta
import os
import sys

def generate_daily_report():
    """生成每日投资报告"""
    tracking_dir = 'data/investment_tracking'
    portfolio_file = f'{tracking_dir}/investment_portfolio.json'
    
    if not os.path.exists(portfolio_file):
        print('❌ 投资组合文件不存在')
        return False
    
    with open(portfolio_file, 'r', encoding='utf-8') as f:
        portfolio = json.load(f)
    
    today = datetime.now().strftime('%Y-%m-%d')
    report_time = datetime.now().strftime('%H:%M:%S')
    
    # 报告文件
    report_file = f'{tracking_dir}/investment_report_{today}.md'
    
    # 计算统计数据
    total_stocks = len(portfolio['stocks'])
    invested_stocks = len([s for s in portfolio['stocks'] if s['status'] == '已进场'])
    pending_stocks = len([s for s in portfolio['stocks'] if s['status'] == '待进场'])
    
    total_investment = portfolio['total_investment']
    current_value = portfolio['current_value']
    total_profit_loss = portfolio['total_profit_loss']
    total_profit_loss_pct = portfolio['total_profit_loss_pct']
    
    # 生成报告内容
    report_content = f"""# 📈 股票投资每日报告
## 报告日期: {today}
## 生成时间: {report_time}

## 一、投资组合概览

| 指标 | 数值 |
|------|------|
| 总选股数量 | {total_stocks}只 |
| 已进场股票 | {invested_stocks}只 |
| 待进场股票 | {pending_stocks}只 |
| 总投资金额 | {total_investment:.2f}元 |
| 当前市值 | {current_value:.2f}元 |
| 总盈亏金额 | {total_profit_loss:+.2f}元 |
| 总盈亏比例 | {total_profit_loss_pct:+.2f}% |

## 二、持仓股票表现

"""
    
    # 已进场股票
    if invested_stocks > 0:
        report_content += "### 🟢 已进场股票\n\n"
        
        for stock in portfolio['stocks']:
            if stock['status'] == '已进场':
                profit_symbol = "📈" if stock['profit_loss'] >= 0 else "📉"
                report_content += f"""#### {stock['code']} {stock['name']} {profit_symbol}
- **进场价格**: {stock['entry_price']}元
- **当前价格**: {stock['current_price']}元
- **持仓数量**: {stock['current_position']}股
- **投资金额**: {stock['total_investment']:.2f}元
- **盈亏金额**: {stock['profit_loss']:+.2f}元
- **盈亏比例**: {stock['profit_loss_pct']:+.2f}%
- **止损点位**: {stock['stop_loss']}元
- **止盈点位**: {stock['take_profit'][0]}元 / {stock['take_profit'][1]}元

**今日分析**:
- 价格走势: 
- 成交量: 
- 技术指标: 
- 明日策略: 

"""
    
    # 待进场股票
    if pending_stocks > 0:
        report_content += "### 🟡 待进场股票\n\n"
        
        for stock in portfolio['stocks']:
            if stock['status'] == '待进场':
                report_content += f"""#### {stock['code']} {stock['name']}
- **综合评分**: {stock['score']}/100
- **建议进场点位**:
  - 激进: {stock['entry_strategy']['激进进场']}元
  - 稳健: {stock['entry_strategy']['稳健进场']}元
  - 保守: {stock['entry_strategy']['保守进场']}元
- **风险控制**:
  - 止损: {stock['stop_loss']}元
  - 止盈: {stock['take_profit'][0]}元 / {stock['take_profit'][1]}元

**监控状态**: 等待进场机会
**明日计划**: 价格达到进场条件时执行

"""
    
    # 市场分析
    report_content += f"""
## 三、市场环境分析

### 📊 主要指数表现
- 上证指数: 
- 深证成指: 
- 创业板指: 
- 沪深300: 

### 🔥 市场热点
1. 
2. 
3. 

### 💰 资金流向
- 主力资金: 
- 北向资金: 
- 板块资金: 

## 四、风险提示
1. 市场波动风险
2. 个股基本面风险  
3. 政策变化风险
4. 流动性风险

## 五、明日操作计划
1. 持仓股票: 
2. 待进场股票: 
3. 风险控制: 

## 六、投资心得与反思
1. 今日操作总结:
2. 经验教训:
3. 改进计划:

---

*报告生成: 量化小助理投资跟踪系统*
*下次报告时间: {(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')} 收盘后*
"""
    
    # 写入报告文件
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f'✅ 每日投资报告已生成: {report_file}')
    
    # 同时生成简版报告（用于消息通知）
    summary_file = f'{tracking_dir}/daily_summary_{today}.txt'
    
    summary_content = f"""📊 股票投资每日摘要 ({today})

【组合概览】
选股: {total_stocks}只 (已进场: {invested_stocks}, 待进场: {pending_stocks})
投资: {total_investment:.2f}元
市值: {current_value:.2f}元
盈亏: {total_profit_loss:+.2f}元 ({total_profit_loss_pct:+.2f}%)

【持仓表现】
"""
    
    for stock in portfolio['stocks']:
        if stock['status'] == '已进场':
            profit_symbol = "↑" if stock['profit_loss'] >= 0 else "↓"
            summary_content += f"{stock['code']} {stock['name']}: {stock['profit_loss_pct']:+.2f}% {profit_symbol}\n"
    
    summary_content += f"""
【明日关注】
1. 监控待进场股票价格
2. 关注持仓股票止盈止损
3. 更新市场分析

生成时间: {report_time}
"""
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary_content)
    
    print(f'✅ 每日摘要已生成: {summary_file}')
    
    return True

def update_portfolio_prices():
    """更新投资组合价格（模拟）"""
    tracking_dir = 'data/investment_tracking'
    portfolio_file = f'{tracking_dir}/investment_portfolio.json'
    
    if not os.path.exists(portfolio_file):
        return False
    
    with open(portfolio_file, 'r', encoding='utf-8') as f:
        portfolio = json.load(f)
    
    # 模拟价格更新（实际应从数据源获取）
    import random
    
    total_investment = 0
    current_value = 0
    
    for stock in portfolio['stocks']:
        if stock['status'] == '已进场' and stock['entry_price']:
            # 模拟价格波动
            price_change = random.uniform(-0.05, 0.08)  # -5%到+8%
            current_price = round(stock['entry_price'] * (1 + price_change), 2)
            
            # 计算盈亏
            if stock['current_position'] > 0:
                profit_loss = (current_price - stock['entry_price']) * stock['current_position']
                profit_loss_pct = (current_price - stock['entry_price']) / stock['entry_price'] * 100
                
                stock['current_price'] = current_price
                stock['profit_loss'] = round(profit_loss, 2)
                stock['profit_loss_pct'] = round(profit_loss_pct, 2)
                
                total_investment += stock['total_investment']
                current_value += current_price * stock['current_position']
    
    # 更新组合总览
    portfolio['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    portfolio['total_investment'] = total_investment
    portfolio['current_value'] = current_value
    portfolio['total_profit_loss'] = current_value - total_investment
    portfolio['total_profit_loss_pct'] = (current_value - total_investment) / total_investment * 100 if total_investment > 0 else 0
    
    with open(portfolio_file, 'w', encoding='utf-8') as f:
        json.dump(portfolio, f, ensure_ascii=False, indent=2)
    
    print('✅ 投资组合价格已更新')
    return True

def main():
    """主函数"""
    print('📈 开始生成每日投资报告')
    print('=' * 50)
    
    # 1. 更新投资组合价格
    print('1. 更新投资组合价格...')
    update_success = update_portfolio_prices()
    
    if not update_success:
        print('⚠️ 价格更新失败，使用现有数据')
    
    # 2. 生成每日报告
    print('2. 生成每日报告...')
    report_success = generate_daily_report()
    
    if report_success:
        print('=' * 50)
        print('🎉 每日投资报告生成完成！')
        
        # 显示报告位置
        today = datetime.now().strftime('%Y-%m-%d')
        tracking_dir = 'data/investment_tracking'
        
        print()
        print('📁 生成的文件:')
        print(f'1. {tracking_dir}/investment_report_{today}.md - 详细报告')
        print(f'2. {tracking_dir}/daily_summary_{today}.txt - 摘要报告')
        print()
        print('📅 建议每日收盘后运行此脚本')
    else:
        print('❌ 报告生成失败')

if __name__ == '__main__':
    main()