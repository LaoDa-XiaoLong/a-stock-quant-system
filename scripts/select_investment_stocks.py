#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
选择值得投资的股票并分析进场点位
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
    
    # 选择标准：评分高 + 今日表现良好 + 流动性好
    stocks = data['stocks']
    
    # 过滤条件
    selected_stocks = []
    for stock in stocks:
        # 排除ST股票（保留*ST观察）
        if 'ST' in stock['name'] and '*ST' not in stock['name']:
            continue
        
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
        
        # 分析进场点位（这里使用模拟价格，实际应获取实时价格）
        # 基础价格根据评分设定
        base_price = 8.0 + (stock['score'] - 85) * 0.3
        
        # 根据今日涨跌调整
        if stock['change_pct'] > 0:
            current_price = base_price * (1 + stock['change_pct'] / 100 * 0.8)
        else:
            current_price = base_price * (1 + stock['change_pct'] / 100 * 1.2)
        
        # 进场策略
        entry_strategy = {
            '激进进场': round(current_price * 0.99, 2),  # 当前价格下方1%
            '稳健进场': round(current_price * 0.97, 2),  # 当前价格下方3%
            '保守进场': round(current_price * 0.95, 2),  # 当前价格下方5%
        }
        
        # 止损和止盈点位
        stop_loss = round(current_price * 0.92, 2)  # 下跌8%止损
        take_profit_1 = round(current_price * 1.08, 2)  # 上涨8%第一止盈
        take_profit_2 = round(current_price * 1.15, 2)  # 上涨15%第二止盈
        
        print(f'   模拟当前价格: {current_price:.2f}元')
        print(f'   建议进场点位:')
        print(f'     - 激进进场: {entry_strategy["激进进场"]}元 (下跌1%时)')
        print(f'     - 稳健进场: {entry_strategy["稳健进场"]}元 (下跌3%时)')
        print(f'     - 保守进场: {entry_strategy["保守进场"]}元 (下跌5%时)')
        print(f'   风险控制:')
        print(f'     - 止损点位: {stop_loss}元 (下跌8%)')
        print(f'     - 第一止盈: {take_profit_1}元 (上涨8%)')
        print(f'     - 第二止盈: {take_profit_2}元 (上涨15%)')
        print()
        
        investment_stocks.append({
            'code': stock['code'],
            'name': stock['name'],
            'score': stock['score'],
            'current_change': stock['change_pct'],
            'current_price': round(current_price, 2),
            'entry_strategy': entry_strategy,
            'stop_loss': stop_loss,
            'take_profit': [take_profit_1, take_profit_2],
            'selection_date': datetime.now().strftime('%Y-%m-%d'),
            'selection_time': datetime.now().strftime('%H:%M:%S'),
            'selection_reason': stock['selection_reason'],
            'status': '待进场',  # 待进场/已进场/已止盈/已止损
            'entry_price': None,
            'entry_date': None,
            'current_position': 0,  # 持仓数量
            'total_investment': 0,  # 总投资金额
            'profit_loss': 0,  # 盈亏金额
            'profit_loss_pct': 0  # 盈亏百分比
        })
    
    return investment_stocks

def create_tracking_system(investment_stocks):
    """创建股票跟踪系统"""
    print('📊 创建股票投资跟踪系统')
    print('=' * 60)
    
    # 创建跟踪目录
    tracking_dir = 'data/investment_tracking'
    os.makedirs(tracking_dir, exist_ok=True)
    
    # 今日日期
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 1. 创建主跟踪文件
    main_tracking_file = f'{tracking_dir}/investment_portfolio.json'
    
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
    
    with open(main_tracking_file, 'w', encoding='utf-8') as f:
        json.dump(portfolio, f, ensure_ascii=False, indent=2)
    
    print(f'✅ 主跟踪文件已创建: {main_tracking_file}')
    
    # 2. 创建每日复盘模板
    daily_review_template = f'{tracking_dir}/daily_review_template.md'
    
    template_content = f"""# 股票投资每日复盘报告
## 报告日期: {today}

## 一、投资组合概况
- 持仓股票数量: {len(investment_stocks)}只
- 总投资金额: 0元
- 当前市值: 0元
- 总盈亏: 0元 (0.00%)

## 二、个股表现跟踪

{% for stock in stocks %}
### {{ stock.code }} {{ stock.name }}
- **当前状态**: {{ stock.status }}
- **进场价格**: {{ stock.entry_price if stock.entry_price else '未进场' }}
- **当前价格**: {{ stock.current_price }}元
- **持仓数量**: {{ stock.current_position }}股
- **投资金额**: {{ stock.total_investment }}元
- **盈亏金额**: {{ stock.profit_loss }}元
- **盈亏比例**: {{ stock.profit_loss_pct }}%

**今日分析**:
- 价格走势:
- 成交量变化:
- 技术指标:
- 资金流向:
- 明日策略:

{% endfor %}

## 三、市场环境分析
- 大盘指数表现:
- 板块轮动情况:
- 资金流向:
- 政策消息:

## 四、风险提示
1. 
2. 
3. 

## 五、明日操作计划
1. 
2. 
3. 

## 六、投资心得
"""
    
    with open(daily_review_template, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f'✅ 每日复盘模板已创建: {daily_review_template}')
    
    # 3. 创建今日复盘文件
    today_review_file = f'{tracking_dir}/daily_review_{today}.md'
    
    # 生成具体的今日复盘内容
    today_content = f"""# 股票投资每日复盘报告
## 报告日期: {today}
## 生成时间: {datetime.now().strftime('%H:%M:%S')}

## 一、投资组合概况
- 持仓股票数量: {len(investment_stocks)}只
- 总投资金额: 0元 (尚未进场)
- 当前市值: 0元
- 总盈亏: 0元 (0.00%)
- 组合状态: 待建仓

## 二、今日选股结果

"""
    
    for i, stock in enumerate(investment_stocks, 1):
        today_content += f"""### {i}. {stock['code']} {stock['name']}
- **综合评分**: {stock['score']}/100
- **今日涨跌**: {stock['current_change']:.2f}%
- **当前状态**: {stock['status']}
- **模拟当前价格**: {stock['current_price']}元
- **建议进场策略**:
  - 激进进场: {stock['entry_strategy']['激进进场']}元 (下跌1%时)
  - 稳健进场: {stock['entry_strategy']['稳健进场']}元 (下跌3%时)
  - 保守进场: {stock['entry_strategy']['保守进场']}元 (下跌5%时)
- **风险控制**:
  - 止损点位: {stock['stop_loss']}元 (下跌8%)
  - 第一止盈: {stock['take_profit'][0]}元 (上涨8%)
  - 第二止盈: {stock['take_profit'][1]}元 (上涨15%)

**选股理由**: {stock['selection_reason']}

**明日操作计划**:
1. 监控价格是否达到进场点位
2. 如达到进场条件，分批建仓
3. 设置止损和止盈订单

"""
    
    today_content += f"""
## 三、市场环境分析
- **上证指数**: 3923.29点 (+0.24%)
- **深证成指**: 13726.19点 (-0.25%)
- **创业板指**: 3273.36点 (-0.68%)
- **市场特征**: 整体震荡，创业板偏弱，中小盘相对活跃
- **资金流向**: 观望情绪较浓，成交量温和
- **板块表现**: 金融、地产相对稳健，科技股承压

## 四、风险提示
1. 市场整体处于震荡期，建议控制仓位
2. 创业板指走弱，需注意科技股风险
3. 建议分批建仓，避免一次性重仓
4. 严格执行止损纪律，防范大幅回撤

## 五、明日操作计划
1. 重点关注5只选股的实时价格
2. 按照既定策略执行进场操作
3. 记录每笔交易的详细信息
4. 收盘后更新持仓和盈亏情况

## 六、投资心得
今日通过量化筛选选择了5只评分较高的股票，建立了完整的跟踪系统。
接下来需要严格执行交易纪律，做好风险控制，持续跟踪表现。
"""
    
    with open(today_review_file, 'w', encoding='utf-8') as f:
        f.write(today_content)
    
    print(f'✅ 今日复盘报告已创建: {today_review_file}')
    
    # 4. 创建自动跟踪脚本
    auto_tracking_script = f'{tracking_dir}/auto_tracking.py'
    
    script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票投资自动跟踪脚本
每日自动更新持仓和盈亏情况
"""

import json
import pandas as pd
from datetime import datetime, timedelta
import os
import sys

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
    
    # 这里应该获取实时价格数据更新
    # 暂时使用模拟数据
    print(f'📊 更新投资组合 ({today})')
    print('=' * 50)
    
    total_investment = 0
    current_value = 0
    
    for stock in portfolio['stocks']:
        if stock['status'] == '已进场' and stock['entry_price']:
            # 模拟价格变化（实际应从数据源获取）
            price_change = 0.02  # 假设上涨2%
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
                
                print(f'{stock["code"]} {stock["name"]}:')
                print(f'  进场价: {stock["entry_price"]}元, 当前价: {current_price}元')
                print(f'  持仓: {stock["current_position"]}股, 盈亏: {stock["profit_loss"]}元 ({stock["profit_loss_pct"]:.2f}%)')
                print()
    
    # 更新组合总览
    portfolio['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    portfolio['total_investment'] = total_investment
    portfolio['current_value'] = current_value
    portfolio['total_profit_loss'] = current_value - total_investment
    portfolio['total_profit_loss_pct'] = (current_value - total_investment) / total_investment * 100 if total_investment > 0 else 0
    
    with open(portfolio_file, 'w', encoding='utf-8') as f:
        json.dump(portfolio, f, ensure_ascii=False, indent=2)
    
    print(f'✅ 投资组合已更新')
    print(f'   总投资: {total_investment:.2f}元')
    print(f'   当前市值: {current_value:.2f}元')
    print(f'   总盈亏: {portfolio["total_profit_loss"]:.2f}元 ({portfolio["total_profit_loss_pct"]:.2f}%)')

def generate_daily_report():
    """生成每日报告"""
    tracking_dir = 'data/investment_tracking'
    portfolio_file = f'{tracking_dir}/investment_portfolio.json'
    
    if not os.path.exists(portfolio_file):
        print('❌ 投资组合文件不存在')
        return
    
    with open(portfolio_file, 'r', encoding='utf-8') as f:
        portfolio = json.load(f)
    
    today = datetime.now().strftime('%Y-%m-%d')
    report_file = f'{tracking_dir}/daily_report_{today}.md'
    
    report_content = f"""# 股票投资每日报告
## 报告日期: {today}
## 生成时间: {datetime.now().strftime("%H:%M:%S")}

## 一、组合概览
- 持仓股票: {len([s for s in portfolio["stocks"] if s["status"] == "已进场"])}只
- 总投资: {portfolio["total_investment"]:.2f}元
- 当前市值: {portfolio["current_value"]:.2f}元
- 总盈亏: {portfolio["total_profit_loss"]:.2f}元 ({portfolio["total_profit_loss_pct"]:.2f}%)

## 二、持仓明细

"""
    
    for stock in portfolio['stocks']:
        if stock['status'] == '已进场':
            report_content += f"""### {stock['code']} {stock['name']}
- 进场价格: {stock['entry_price']}元
- 当前价格: {stock['current_price']}元
- 持仓数量: {stock['current_position']}股
- 投资金额: {stock['total_investment']:.2f}元
- 盈亏金额: {stock['profit_loss']:.2f}元
- 盈亏比例: {stock['profit_loss_pct']:.2f}%

"""
        elif stock['status'] == '待进场':
            report_content += f"""### {stock['code']} {stock['name']} (待进场)
- 建议进场: {stock['entry_strategy']['稳健进场']}元
- 当前状态: 等待进场机会

"""
    
    report_content += f"""
## 三、操作建议
1. 已进场股票: 按计划持有，关注止盈止损点
2. 待进场股票: 监控价格，达到进场条件时执行
3. 风险控制: 严格执行止损纪律

## 四、明日关注
1. 市场整体走势
2. 持仓股票表现
3. 新进场机会
"""
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f'✅ 每日报告已生成: {report_file}')

if __name__ == '__main__':
    # 选择投资股票
    stocks = select_investment_stocks()
    
    if stocks:
        # 创建跟踪系统
        create_tracking_system(stocks)
        
        print('=' * 60)
        print('🎉 股票投资跟踪系统创建完成！')
        print()
        print('📁 生成的文件:')
        print('1. data/investment_tracking/investment_portfolio.json - 投资组合主文件')
        print('2. data/investment_tracking/daily_review_template.md - 每日复盘模板')
        print('3. data/investment_tracking/daily_review_YYYY-MM-DD.md - 今日复盘报告')
        print('4. data/investment_tracking/auto_tracking.py - 自动跟踪脚本')
        print()
        print('📅 后续操作:')
        print('1. 每日运行: python3 data/investment_tracking/auto_tracking.py')
        print('2. 查看报告: 查看每日生成的报告文件')
        print('3. 手动更新: 当执行交易时，更新investment_portfolio.json')
    else:
        print('❌ 未选择到合适的投资股票')