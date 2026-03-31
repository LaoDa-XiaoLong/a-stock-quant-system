#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建股票投资跟踪系统
"""

import json
import pandas as pd
from datetime import datetime
import os
import sys

def select_investment_stocks():
    """选择值得投资的股票"""
    print('🎯 选择值得投资的股票并分析进场点位')
    print('=' * 60)
    
    # 读取最新的筛选结果
    screening_file = 'data/stock_pool/screening_results_20260331_093829.json'
    
    if not os.path.exists(screening_file):
        print('⚠️ 未找到筛选结果文件')
        return []
    
    with open(screening_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 选择标准：评分高 + 今日表现良好
    stocks = data['stocks']
    
    # 过滤条件
    selected_stocks = []
    for stock in stocks:
        # 选择评分85以上且今日涨跌在-2%到+5%之间的
        if stock['score'] >= 85 and -2 <= stock['change_pct'] <= 5:
            selected_stocks.append(stock)
    
    # 按评分排序，取前5只
    selected_stocks = sorted(selected_stocks, key=lambda x: x['score'], reverse=True)[:5]
    
    print(f'从{len(stocks)}只股票中筛选出{len(selected_stocks)}只值得投资的股票:')
    print()
    
    investment_stocks = []
    for i, stock in enumerate(selected_stocks, 1):
        print(f'{i}. {stock["code"]} {stock["name"]}')
        print(f'   综合评分: {stock["score"]}/100')
        print(f'   今日涨跌: {stock["change_pct"]:.2f}%')
        print(f'   入选理由: {stock["selection_reason"]}')
        
        # 分析进场点位（模拟价格）
        base_price = 8.0 + (stock['score'] - 85) * 0.3
        
        if stock['change_pct'] > 0:
            current_price = base_price * (1 + stock['change_pct'] / 100 * 0.8)
        else:
            current_price = base_price * (1 + stock['change_pct'] / 100 * 1.2)
        
        current_price = round(current_price, 2)
        
        # 进场策略
        entry_strategy = {
            '激进进场': round(current_price * 0.99, 2),
            '稳健进场': round(current_price * 0.97, 2),
            '保守进场': round(current_price * 0.95, 2),
        }
        
        # 风险控制
        stop_loss = round(current_price * 0.92, 2)
        take_profit_1 = round(current_price * 1.08, 2)
        take_profit_2 = round(current_price * 1.15, 2)
        
        print(f'   模拟当前价格: {current_price}元')
        print(f'   建议进场点位:')
        print(f'     - 激进: {entry_strategy["激进进场"]}元')
        print(f'     - 稳健: {entry_strategy["稳健进场"]}元')
        print(f'     - 保守: {entry_strategy["保守进场"]}元')
        print(f'   风险控制:')
        print(f'     - 止损: {stop_loss}元')
        print(f'     - 止盈1: {take_profit_1}元')
        print(f'     - 止盈2: {take_profit_2}元')
        print()
        
        investment_stocks.append({
            'code': stock['code'],
            'name': stock['name'],
            'score': stock['score'],
            'current_change': stock['change_pct'],
            'current_price': current_price,
            'entry_strategy': entry_strategy,
            'stop_loss': stop_loss,
            'take_profit': [take_profit_1, take_profit_2],
            'selection_date': datetime.now().strftime('%Y-%m-%d'),
            'selection_time': datetime.now().strftime('%H:%M:%S'),
            'selection_reason': stock['selection_reason'],
            'status': '待进场',
            'entry_price': None,
            'entry_date': None,
            'current_position': 0,
            'total_investment': 0,
            'profit_loss': 0,
            'profit_loss_pct': 0
        })
    
    return investment_stocks

def create_tracking_files(investment_stocks):
    """创建跟踪文件"""
    print('📊 创建股票投资跟踪文件')
    print('=' * 60)
    
    # 创建跟踪目录
    tracking_dir = 'data/investment_tracking'
    os.makedirs(tracking_dir, exist_ok=True)
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 1. 创建投资组合文件
    portfolio_file = f'{tracking_dir}/investment_portfolio.json'
    
    portfolio = {
        'created_date': today,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_stocks': len(investment_stocks),
        'total_investment': 0,
        'current_value': 0,
        'total_profit_loss': 0,
        'total_profit_loss_pct': 0,
        'stocks': investment_stocks
    }
    
    with open(portfolio_file, 'w', encoding='utf-8') as f:
        json.dump(portfolio, f, ensure_ascii=False, indent=2)
    
    print(f'✅ 投资组合文件: {portfolio_file}')
    
    # 2. 创建今日复盘报告
    review_file = f'{tracking_dir}/daily_review_{today}.md'
    
    review_content = f"""# 股票投资每日复盘报告
## 报告日期: {today}
## 生成时间: {datetime.now().strftime('%H:%M:%S')}

## 一、投资组合概况
- 选股数量: {len(investment_stocks)}只
- 当前状态: 待建仓
- 总投资: 0元
- 总盈亏: 0元 (0.00%)

## 二、今日选股详情

"""
    
    for i, stock in enumerate(investment_stocks, 1):
        review_content += f"""### {i}. {stock['code']} {stock['name']}
- **综合评分**: {stock['score']}/100
- **今日涨跌**: {stock['current_change']:.2f}%
- **模拟价格**: {stock['current_price']}元
- **进场策略**:
  - 激进: {stock['entry_strategy']['激进进场']}元
  - 稳健: {stock['entry_strategy']['稳健进场']}元  
  - 保守: {stock['entry_strategy']['保守进场']}元
- **风险控制**:
  - 止损: {stock['stop_loss']}元
  - 止盈1: {stock['take_profit'][0]}元
  - 止盈2: {stock['take_profit'][1]}元

**选股理由**: {stock['selection_reason']}

**操作计划**:
1. 监控价格，达到进场条件时执行
2. 分批建仓，控制风险
3. 设置止损止盈

"""
    
    review_content += f"""
## 三、市场分析
- **上证指数**: 3923.29点 (+0.24%)
- **深证成指**: 13726.19点 (-0.25%)
- **市场状态**: 震荡整理，创业板偏弱

## 四、风险提示
1. 市场震荡，建议控制仓位
2. 分批建仓，避免一次性重仓
3. 严格执行止损纪律

## 五、明日计划
1. 监控选股价格变化
2. 执行进场操作（如条件满足）
3. 更新持仓记录

## 六、投资纪律
- 单只股票仓位不超过10%
- 总仓位控制在60-70%
- 止损位: -8%
- 止盈位: +8% (第一目标), +15% (第二目标)
"""
    
    with open(review_file, 'w', encoding='utf-8') as f:
        f.write(review_content)
    
    print(f'✅ 今日复盘报告: {review_file}')
    
    # 3. 创建自动跟踪脚本
    script_file = f'{tracking_dir}/update_tracking.py'
    
    script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新股票投资跟踪
"""

import json
import pandas as pd
from datetime import datetime
import os

def update_portfolio():
    """更新投资组合"""
    tracking_dir = 'data/investment_tracking'
    portfolio_file = f'{tracking_dir}/investment_portfolio.json'
    
    if not os.path.exists(portfolio_file):
        print('❌ 投资组合文件不存在')
        return
    
    with open(portfolio_file, 'r', encoding='utf-8') as f:
        portfolio = json.load(f)
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    print(f'📊 更新投资组合 ({today})')
    print('=' * 50)
    
    # 模拟更新价格（实际应从数据源获取）
    for stock in portfolio['stocks']:
        if stock['status'] == '已进场' and stock['entry_price']:
            # 模拟价格变化
            import random
            price_change = random.uniform(-0.03, 0.05)  # -3%到+5%
            current_price = round(stock['entry_price'] * (1 + price_change), 2)
            
            # 计算盈亏
            if stock['current_position'] > 0:
                profit_loss = (current_price - stock['entry_price']) * stock['current_position']
                profit_loss_pct = (current_price - stock['entry_price']) / stock['entry_price'] * 100
                
                stock['current_price'] = current_price
                stock['profit_loss'] = round(profit_loss, 2)
                stock['profit_loss_pct'] = round(profit_loss_pct, 2)
                
                print(f'{stock["code"]} {stock["name"]}:')
                print(f'  当前价: {current_price}元, 盈亏: {stock["profit_loss"]}元 ({stock["profit_loss_pct"]:.2f}%)')
    
    # 更新总览
    portfolio['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(portfolio_file, 'w', encoding='utf-8') as f:
        json.dump(portfolio, f, ensure_ascii=False, indent=2)
    
    print('✅ 投资组合已更新')

def record_transaction(stock_code, action, price, quantity, date=None):
    """记录交易"""
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    tracking_dir = 'data/investment_tracking'
    portfolio_file = f'{tracking_dir}/investment_portfolio.json'
    
    if not os.path.exists(portfolio_file):
        print('❌ 投资组合文件不存在')
        return
    
    with open(portfolio_file, 'r', encoding='utf-8') as f:
        portfolio = json.load(f)
    
    # 找到对应的股票
    for stock in portfolio['stocks']:
        if stock['code'] == stock_code:
            if action == '买入':
                stock['status'] = '已进场'
                stock['entry_price'] = price
                stock['entry_date'] = date
                stock['current_position'] = quantity
                stock['total_investment'] = price * quantity
                print(f'✅ 记录买入: {stock_code} {price}元 × {quantity}股')
            elif action == '卖出':
                stock['status'] = '已平仓'
                profit = (price - stock['entry_price']) * quantity
                print(f'✅ 记录卖出: {stock_code} {price}元, 盈利: {profit:.2f}元')
            
            break
    
    # 保存更新
    with open(portfolio_file, 'w', encoding='utf-8') as f:
        json.dump(portfolio, f, ensure_ascii=False, indent=2)
    
    print('✅ 交易记录已保存')

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'update':
            update_portfolio()
        elif sys.argv[1] == 'buy' and len(sys.argv) == 5:
            record_transaction(sys.argv[2], '买入', float(sys.argv[3]), int(sys.argv[4]))
        elif sys.argv[1] == 'sell' and len(sys.argv) == 5:
            record_transaction(sys.argv[2], '卖出', float(sys.argv[3]), int(sys.argv[4]))
        else:
            print('用法:')
            print('  python3 update_tracking.py update')
            print('  python3 update_tracking.py buy 股票代码 价格 数量')
            print('  python3 update_tracking.py sell 股票代码 价格 数量')
    else:
        update_portfolio()
'''
    
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # 设置执行权限
    os.chmod(script_file, 0o755)
    
    print(f'✅ 自动跟踪脚本: {script_file}')
    
    return True

def main():
    """主函数"""
    # 选择投资股票
    stocks = select_investment_stocks()
    
    if not stocks:
        print('❌ 未选择到合适的投资股票')
        return
    
    # 创建跟踪文件
    success = create_tracking_files(stocks)
    
    if success:
        print('=' * 60)
        print('🎉 股票投资跟踪系统创建完成！')
        print()
        print('📁 生成的文件:')
        print('1. data/investment_tracking/investment_portfolio.json')
        print('2. data/investment_tracking/daily_review_YYYY-MM-DD.md')
        print('3. data/investment_tracking/update_tracking.py')
        print()
        print('📅 使用说明:')
        print('1. 每日更新: python3 data/investment_tracking/update_tracking.py update')
        print('2. 记录买入: python3 update_tracking.py buy 股票代码 价格 数量')
        print('3. 记录卖出: python3 update_tracking.py sell 股票代码 价格 数量')
        print('4. 查看报告: 查看每日生成的复盘报告')
        print()
        print('💡 建议:')
        print('- 每日收盘后运行更新脚本')
        print('- 执行交易后立即记录')
        print('- 定期复盘，优化策略')

if __name__ == '__main__':
    main()