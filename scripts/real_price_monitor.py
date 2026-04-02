#!/usr/bin/env python3
"""
真实价格监控脚本
每3分钟获取一次真实价格，更新投资组合
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
import schedule

def get_real_stock_price(stock_code):
    """从新浪财经API获取真实股票价格"""
    try:
        if stock_code.startswith('6'):
            market_code = f"sh{stock_code}"
        elif stock_code.startswith('0') or stock_code.startswith('3'):
            market_code = f"sz{stock_code}"
        else:
            return None
        
        url = f"http://hq.sinajs.cn/list={market_code}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Referer': 'http://finance.sina.com.cn'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            content = response.text
            if '="' in content:
                data_str = content.split('="')[1].split('"')[0]
                data_parts = data_str.split(',')
                if len(data_parts) > 1:
                    current_price = float(data_parts[3])
                    yesterday_close = float(data_parts[2])
                    
                    if yesterday_close > 0:
                        change_percent = (current_price - yesterday_close) / yesterday_close * 100
                    else:
                        change_percent = 0.0
                    
                    return {
                        'code': stock_code,
                        'name': data_parts[0],
                        'current_price': round(current_price, 2),
                        'change_percent': round(change_percent, 2),
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
    except Exception as e:
        print(f"获取股票 {stock_code} 价格失败: {e}")
    
    return None

def update_portfolio_prices():
    """更新投资组合价格"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 更新投资组合价格...")
    
    portfolio_path = "/Users/ago/.openclaw/workspace/data/simulated_trading/simulated_portfolio.json"
    
    if not os.path.exists(portfolio_path):
        return
    
    try:
        with open(portfolio_path, 'r', encoding='utf-8') as f:
            portfolio = json.load(f)
        
        # 获取所有股票代码
        stock_codes = []
        for holding in portfolio.get('holdings', []):
            stock_code = holding.get('stock_code', '')
            if stock_code:
                stock_codes.append(stock_code)
        
        # 获取真实价格
        real_prices = {}
        for stock_code in stock_codes:
            price_data = get_real_stock_price(stock_code)
            if price_data:
                real_prices[stock_code] = price_data
            time.sleep(0.3)
        
        # 更新投资组合
        for holding in portfolio.get('holdings', []):
            stock_code = holding.get('stock_code', '')
            if stock_code in real_prices:
                price_data = real_prices[stock_code]
                holding['current_price'] = price_data['current_price']
                
                # 计算浮动盈亏
                entry_price = holding.get('entry_price', 0)
                if entry_price > 0:
                    position = holding.get('position', 0)
                    position_value = position * price_data['current_price']
                    entry_value = position * entry_price
                    profit_loss = position_value - entry_value
                    profit_loss_percent = (profit_loss / entry_value * 100) if entry_value > 0 else 0
                    
                    holding['profit_loss'] = round(profit_loss, 2)
                    holding['profit_loss_percent'] = round(profit_loss_percent, 2)
                    holding['position_value'] = round(position_value, 2)
        
        # 更新总资产
        total_assets = portfolio.get('initial_capital', 1000000.0)
        for holding in portfolio.get('holdings', []):
            total_assets += holding.get('profit_loss', 0)
        portfolio['total_assets'] = round(total_assets, 2)
        
        # 计算总收益率
        initial_capital = portfolio.get('initial_capital', 1000000.0)
        if initial_capital > 0:
            total_return = (total_assets - initial_capital) / initial_capital * 100
            portfolio['total_return_percent'] = round(total_return, 2)
        
        # 保存
        with open(portfolio_path, 'w', encoding='utf-8') as f:
            json.dump(portfolio, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 投资组合价格更新完成，总资产: {portfolio['total_assets']}元")
        
    except Exception as e:
        print(f"❌ 更新失败: {e}")

def main():
    """主函数"""
    print("🚀 真实价格监控系统启动")
    print(f"📅 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 立即执行一次
    update_portfolio_prices()
    
    # 设置定时任务
    schedule.every(3).minutes.do(update_portfolio_prices)
    
    print("⏰ 已设置每3分钟更新一次价格")
    print("🔄 监控系统运行中...")
    
    # 保持运行
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
