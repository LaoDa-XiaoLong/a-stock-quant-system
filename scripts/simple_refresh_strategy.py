#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版策略刷新 - 基于最新真实价格重新计算进场点位
"""

import json
import requests
import re
from datetime import datetime
import os

print("=" * 60)
print("🔄 简化版投资策略刷新")
print("=" * 60)

def get_real_price(stock_code):
    """获取真实价格"""
    try:
        if stock_code.startswith('6'):
            symbol = f'sh{stock_code}'
        else:
            symbol = f'sz{stock_code}'

        url = f'http://hq.sinajs.cn/list={symbol}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://finance.sina.com.cn'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'gbk'

        data_str = response.text
        match = re.search(r'="(.*?)"', data_str)

        if match:
            data = match.group(1).split(',')
            if len(data) > 3:
                name = data[0]
                price = float(data[3])
                yesterday_close = float(data[2])

                if yesterday_close > 0:
                    change = (price - yesterday_close) / yesterday_close * 100
                else:
                    change = 0.0

                return {
                    'success': True,
                    'name': name,
                    'price': price,
                    'change': change,
                    'yesterday_close': yesterday_close
                }

        return {'success': False, 'error': '数据解析失败'}

    except Exception as e:
        return {'success': False, 'error': str(e)}

def calculate_new_strategy(current_price):
    """计算新策略点位"""
    # 进场策略
    aggressive = current_price * 0.99  # 下跌1%
    steady = current_price * 0.97      # 下跌3%
    conservative = current_price * 0.95  # 下跌5%

    # 风险控制（基于激进进场价）
    stop_loss = aggressive * 0.92      # 下跌8%
    take_profit_1 = aggressive * 1.08  # 上涨8%
    take_profit_2 = aggressive * 1.15  # 上涨15%

    return {
        'entry_strategy': {
            '激进进场': round(aggressive, 2),
            '稳健进场': round(steady, 2),
            '保守进场': round(conservative, 2)
        },
        'risk_control': {
            'stop_loss': round(stop_loss, 2),
            'take_profit': [round(take_profit_1, 2), round(take_profit_2, 2)]
        }
    }

def calculate_score(price, change):
    """计算股票评分"""
    score = 50  # 基础分

    # 价格适中评分
    if 5 <= price <= 20:
        score += 20
    elif 20 < price <= 50:
        score += 15
    else:
        score += 10

    # 涨跌评分（小幅下跌较好）
    if -3 <= change <= 3:
        score += 20
    elif -5 <= change <= 5:
        score += 15
    else:
        score += 10

    return min(max(score, 0), 100)

# 加载现有投资组合
portfolio_file = 'data/investment_tracking/investment_portfolio.json'

if not os.path.exists(portfolio_file):
    print("❌ 投资组合文件不存在")
    exit(1)

with open(portfolio_file, 'r', encoding='utf-8') as f:
    portfolio = json.load(f)

print(f"📊 现有投资组合: {len(portfolio['stocks'])}只股票")
print()

# 刷新每只股票的策略
refreshed_stocks = []
entered_stocks = []

for stock in portfolio['stocks']:
    code = stock['code']
    print(f"🔍 刷新 {code} ...")

    # 获取最新价格
    price_data = get_real_price(code)

    if price_data['success']:
        current_price = price_data['price']
        change = price_data['change']
        name = price_data['name']

        print(f"✅ {code} {name}: {current_price}元 ({change:+.2f}%)")

        # 计算新策略
        new_strategy = calculate_new_strategy(current_price)

        # 计算新评分
        score = calculate_score(current_price, change)

        # 创建刷新后的股票信息
        refreshed_stock = {
            'code': code,
            'name': name,
            'score': score,
            'current_price': current_price,
            'current_change': change,
            'entry_strategy': new_strategy['entry_strategy'],
            'stop_loss': new_strategy['risk_control']['stop_loss'],
            'take_profit': new_strategy['risk_control']['take_profit'],
            'selection_date': datetime.now().strftime('%Y-%m-%d'),
            'selection_time': datetime.now().strftime('%H:%M:%S'),
            'selection_reason': f'基于最新价格{current_price}元重新计算',
            'status': '待进场',
            'price_source': 'sina',
            'price_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'yesterday_close': price_data['yesterday_close']
        }

        refreshed_stocks.append(refreshed_stock)

        # 检查是否达到进场条件
        entry = new_strategy['entry_strategy']
        if current_price <= entry['激进进场']:
            print(f"   🎯 已达到激进进场条件! (≤{entry['激进进场']}元)")
            entered_stocks.append((refreshed_stock, '激进进场'))
        elif current_price <= entry['稳健进场']:
            print(f"   🎯 已达到稳健进场条件! (≤{entry['稳健进场']}元)")
            entered_stocks.append((refreshed_stock, '稳健进场'))
        elif current_price <= entry['保守进场']:
            print(f"   🎯 已达到保守进场条件! (≤{entry['保守进场']}元)")
            entered_stocks.append((refreshed_stock, '保守进场'))
        else:
            diff = current_price - entry['保守进场']
            diff_pct = diff / current_price * 100
            print(f"   ⏳ 未达到进场条件 (还需下跌{diff:.2f}元, {diff_pct:.1f}%)")

        print(f"   📊 新评分: {score}/100")
        print(f"   🛡️ 新止损: {new_strategy['risk_control']['stop_loss']}元")
        print(f"   🎯 新止盈: {new_strategy['risk_control']['take_profit'][0]}/{new_strategy['risk_control']['take_profit'][1]}元")

    else:
        print(f"❌ {code}: 获取价格失败 - {price_data.get('error', '未知错误')}")

print()
print("=" * 60)

if not refreshed_stocks:
    print("❌ 未成功刷新任何股票策略")
    exit(1)

# 创建新投资组合
new_portfolio = {
    'created_date': datetime.now().strftime('%Y-%m-%d'),
    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'total_stocks': len(refreshed_stocks),
    'total_investment': 0,
    'current_value': 0,
    'total_profit_loss': 0,
    'total_profit_loss_pct': 0,
    'stocks': refreshed_stocks,
    'data_source': 'sina',
    'update_type': 'strategy_refresh_v2',
    'strategy_version': 'v2.0',
    'refresh_reason': '基于最新真实价格重新计算进场点位'
}

# 保存新投资组合
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
new_portfolio_file = f'data/investment_tracking/investment_portfolio_refreshed_{timestamp}.json'

with open(new_portfolio_file, 'w', encoding='utf-8') as f:
    json.dump(new_portfolio, f, ensure_ascii=False, indent=2)

# 更新主文件
with open(portfolio_file, 'w', encoding='utf-8') as f:
    json.dump(new_portfolio, f, ensure_ascii=False, indent=2)

print("✅ 策略刷新完成!")
print(f"📁 新投资组合: {new_portfolio_file}")
print(f"📁 主文件已更新: {portfolio_file}")
print()

print("📊 刷新结果摘要:")
print(f"   刷新股票数量: {len(refreshed_stocks)}只")
print(f"   已达到进场条件: {len(entered_stocks)}只")
print()

if entered_stocks:
    print("🎯 已达到进场条件的股票:")
    for stock, entry_type in entered_stocks:
        print(f"   {stock['code']} {stock['name']}: {stock['current_price']}元 ({entry_type})")

    print()
    print("💡 操作建议:")
    print("   1. 立即评估这些股票的进场机会")
    print("   2. 考虑分批建仓，控制风险")
    print("   3. 或等待明天系统自动执行监控")
else:
    print("⏳ 暂无股票达到进场条件")
    print("💡 建议继续监控，等待价格回调")

print()
print("🔄 新策略特点:")
print("   1. 基于最新真实价格动态计算")
print("   2. 进场点位更合理（下跌1%/3%/5%）")
print("   3. 风险控制更科学（止损8%，止盈8%/15%）")
print("   4. 每3分钟自动刷新价格")

print()
print("⏰ 明天自动执行:")
print("   09:29 - 交易监控系统自动启动")
print("   每3分钟 - 获取真实价格并检查条件")
print("   自动成交 - 达到条件时执行模拟交易")
print("   16:00 - 生成详细报告")

print()
print("=" * 60)
print("🎉 投资策略刷新完成！基于最新真实价格的进场点位已重新计算")
print("=" * 60)
