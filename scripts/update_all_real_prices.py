#!/usr/bin/env python3
"""
更新所有持仓为真实价格系统
"""

import os
import sys
import json
import time
import requests
from datetime import datetime

def get_real_stock_price(stock_code):
    """
    从新浪财经API获取真实股票价格
    """
    try:
        # 判断市场
        if stock_code.startswith('6'):
            market_code = f"sh{stock_code}"
        elif stock_code.startswith('0') or stock_code.startswith('3'):
            market_code = f"sz{stock_code}"
        else:
            print(f"⚠️ 无法识别股票代码: {stock_code}")
            return None
        
        # 新浪财经API
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
                    # 当前价格是第4个字段 (索引3)
                    current_price = float(data_parts[3])
                    yesterday_close = float(data_parts[2])
                    
                    # 计算涨跌幅
                    if yesterday_close > 0:
                        change_percent = (current_price - yesterday_close) / yesterday_close * 100
                    else:
                        change_percent = 0.0
                    
                    return {
                        'code': stock_code,
                        'name': data_parts[0],
                        'current_price': round(current_price, 2),
                        'yesterday_close': round(yesterday_close, 2),
                        'change_percent': round(change_percent, 2),
                        'high': float(data_parts[4]),
                        'low': float(data_parts[5]),
                        'volume': int(data_parts[8]),
                        'amount': float(data_parts[9]),
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
    except Exception as e:
        print(f"❌ 获取股票 {stock_code} 价格失败: {e}")
    
    return None

def update_investment_portfolio():
    """更新投资组合为真实价格"""
    print("🔍 更新投资组合为真实价格...")
    
    portfolio_path = "/Users/ago/.openclaw/workspace/data/investment_tracking/investment_portfolio.json"
    
    if not os.path.exists(portfolio_path):
        print(f"❌ 投资组合文件不存在: {portfolio_path}")
        return False
    
    try:
        # 读取投资组合
        with open(portfolio_path, 'r', encoding='utf-8') as f:
            portfolio = json.load(f)
        
        stocks = portfolio.get('stocks', [])
        print(f"📊 当前投资组合: {len(stocks)} 只股票")
        
        # 获取所有股票代码
        stock_codes = [stock['code'] for stock in stocks if 'code' in stock]
        
        print(f"📈 需要获取 {len(stock_codes)} 只股票的实时价格")
        
        # 获取真实价格
        real_prices = {}
        for stock_code in stock_codes:
            print(f"  正在获取 {stock_code} 的实时价格...")
            price_data = get_real_stock_price(stock_code)
            if price_data:
                real_prices[stock_code] = price_data
                print(f"    ✅ {price_data['name']}: {price_data['current_price']}元 ({price_data['change_percent']}%)")
            else:
                print(f"    ⚠️  {stock_code}: 获取失败")
            time.sleep(0.5)
        
        # 更新投资组合
        updated_count = 0
        for stock in stocks:
            stock_code = stock.get('code', '')
            if stock_code in real_prices:
                price_data = real_prices[stock_code]
                
                # 更新价格信息
                stock['current_price'] = price_data['current_price']
                stock['current_change'] = price_data['change_percent']
                stock['yesterday_close'] = price_data['yesterday_close']
                stock['price_source'] = 'sina_real_time'
                stock['price_timestamp'] = price_data['timestamp']
                
                # 重新计算进场点位 (基于真实价格)
                current_price = price_data['current_price']
                stock['entry_strategy'] = {
                    '激进进场': round(current_price * 0.99, 2),  # 下跌1%
                    '稳健进场': round(current_price * 0.97, 2),  # 下跌3%
                    '保守进场': round(current_price * 0.95, 2)   # 下跌5%
                }
                
                # 重新计算止损止盈
                aggressive_entry = current_price * 0.99
                stock['stop_loss'] = round(aggressive_entry * 0.92, 2)  # 止损8%
                stock['take_profit'] = [
                    round(aggressive_entry * 1.08, 2),  # 第一止盈8%
                    round(aggressive_entry * 1.15, 2)   # 第二止盈15%
                ]
                
                updated_count += 1
        
        # 更新投资组合信息
        portfolio['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        portfolio['price_source'] = 'sina_real_time'
        
        # 计算总投资
        total_investment = 0
        current_value = 0
        
        for stock in stocks:
            if stock.get('position', 0) > 0:
                position = stock['position']
                entry_price = stock.get('entry_price', 0)
                current_price = stock.get('current_price', 0)
                
                if entry_price > 0:
                    total_investment += position * entry_price
                    current_value += position * current_price
        
        portfolio['total_investment'] = round(total_investment, 2)
        portfolio['current_value'] = round(current_value, 2)
        
        if total_investment > 0:
            total_profit_loss = current_value - total_investment
            total_profit_loss_pct = (total_profit_loss / total_investment) * 100
            portfolio['total_profit_loss'] = round(total_profit_loss, 2)
            portfolio['total_profit_loss_pct'] = round(total_profit_loss_pct, 2)
        
        # 保存更新后的投资组合
        with open(portfolio_path, 'w', encoding='utf-8') as f:
            json.dump(portfolio, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 成功更新 {updated_count} 只股票的实时价格")
        print(f"💰 总投资: {portfolio['total_investment']}元")
        print(f"📈 当前价值: {portfolio['current_value']}元")
        
        if 'total_profit_loss' in portfolio:
            profit_loss = portfolio['total_profit_loss']
            profit_loss_pct = portfolio['total_profit_loss_pct']
            status = "📈" if profit_loss >= 0 else "📉"
            print(f"{status} 总盈亏: {profit_loss}元 ({profit_loss_pct}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ 更新投资组合失败: {e}")
        return False

def update_tail_end_portfolio():
    """更新尾盘选股投资组合"""
    print("🔍 更新尾盘选股投资组合...")
    
    portfolio_path = "/Users/ago/.openclaw/workspace/data/investment_tracking/tail_end_portfolio.json"
    
    if not os.path.exists(portfolio_path):
        print(f"⚠️  尾盘选股投资组合文件不存在: {portfolio_path}")
        return False
    
    try:
        with open(portfolio_path, 'r', encoding='utf-8') as f:
            portfolio = json.load(f)
        
        stocks = portfolio.get('stocks', [])
        print(f"📊 尾盘选股组合: {len(stocks)} 只股票")
        
        # 获取所有股票代码
        stock_codes = [stock['code'] for stock in stocks if 'code' in stock]
        
        # 获取真实价格
        real_prices = {}
        for stock_code in stock_codes:
            price_data = get_real_stock_price(stock_code)
            if price_data:
                real_prices[stock_code] = price_data
            time.sleep(0.5)
        
        # 更新价格
        updated_count = 0
        for stock in stocks:
            stock_code = stock.get('code', '')
            if stock_code in real_prices:
                price_data = real_prices[stock_code]
                stock['current_price'] = price_data['current_price']
                stock['change_percent'] = price_data['change_percent']
                stock['price_timestamp'] = price_data['timestamp']
                updated_count += 1
        
        portfolio['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        portfolio['price_source'] = 'sina_real_time'
        
        with open(portfolio_path, 'w', encoding='utf-8') as f:
            json.dump(portfolio, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 成功更新 {updated_count} 只尾盘选股的价格")
        return True
        
    except Exception as e:
        print(f"❌ 更新尾盘选股组合失败: {e}")
        return False

def update_simulated_trading():
    """更新模拟交易系统"""
    print("🔍 更新模拟交易系统...")
    
    # 模拟投资组合
    portfolio_path = "/Users/ago/.openclaw/workspace/data/simulated_trading/simulated_portfolio.json"
    trades_path = "/Users/ago/.openclaw/workspace/data/simulated_trading/simulated_trades.json"
    
    updated_files = []
    
    # 更新模拟投资组合
    if os.path.exists(portfolio_path):
        try:
            with open(portfolio_path, 'r', encoding='utf-8') as f:
                portfolio = json.load(f)
            
            holdings = portfolio.get('holdings', [])
            if holdings:
                print(f"📊 模拟持仓: {len(holdings)} 只股票")
                
                # 获取股票代码
                stock_codes = [h['stock_code'] for h in holdings if 'stock_code' in h]
                
                # 获取真实价格
                real_prices = {}
                for stock_code in stock_codes:
                    price_data = get_real_stock_price(stock_code)
                    if price_data:
                        real_prices[stock_code] = price_data
                    time.sleep(0.5)
                
                # 更新持仓
                for holding in holdings:
                    stock_code = holding.get('stock_code', '')
                    if stock_code in real_prices:
                        price_data = real_prices[stock_code]
                        holding['current_price'] = price_data['current_price']
                        
                        # 计算浮动盈亏
                        entry_price = holding.get('entry_price', 0)
                        if entry_price > 0:
                            position = holding.get('position', 0)
                            current_value = position * price_data['current_price']
                            entry_value = position * entry_price
                            profit_loss = current_value - entry_value
                            profit_loss_percent = (profit_loss / entry_value * 100) if entry_value > 0 else 0
                            
                            holding['profit_loss'] = round(profit_loss, 2)
                            holding['profit_loss_percent'] = round(profit_loss_percent, 2)
                            holding['position_value'] = round(current_value, 2)
                
                # 更新总资产
                total_assets = portfolio.get('initial_capital', 1000000.0)
                for holding in holdings:
                    total_assets += holding.get('profit_loss', 0)
                portfolio['total_assets'] = round(total_assets, 2)
                
                # 计算总收益率
                initial_capital = portfolio.get('initial_capital', 1000000.0)
                if initial_capital > 0:
                    total_return = (total_assets - initial_capital) / initial_capital * 100
                    portfolio['total_return_percent'] = round(total_return, 2)
                
                portfolio['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                with open(portfolio_path, 'w', encoding='utf-8') as f:
                    json.dump(portfolio, f, ensure_ascii=False, indent=2)
                
                updated_files.append('simulated_portfolio.json')
                print(f"✅ 模拟投资组合更新完成")
        
        except Exception as e:
            print(f"❌ 更新模拟投资组合失败: {e}")
    
    # 更新交易记录
    if os.path.exists(trades_path):
        try:
            with open(trades_path, 'r', encoding='utf-8') as f:
                trades_data = json.load(f)
            
            trades = trades_data.get('trades', [])
            active_trades = [t for t in trades if t.get('status') == 'active']
            
            if active_trades:
                print(f"📊 活跃交易: {len(active_trades)} 笔")
                
                # 获取股票代码
                stock_codes = list(set([t['stock_code'] for t in active_trades if 'stock_code' in t]))
                
                # 获取真实价格
                real_prices = {}
                for stock_code in stock_codes:
                    price_data = get_real_stock_price(stock_code)
                    if price_data:
                        real_prices[stock_code] = price_data
                    time.sleep(0.5)
                
                # 更新交易记录
                for trade in active_trades:
                    stock_code = trade.get('stock_code', '')
                    if stock_code in real_prices:
                        price_data = real_prices[stock_code]
                        trade['current_price'] = price_data['current_price']
                        
                        # 计算浮动盈亏
                        entry_price = trade.get('entry_price', 0)
                        if entry_price > 0:
                            position = trade.get('position', 0)
                            current_value = position * price_data['current_price']
                            entry_value = position * entry_price
                            profit_loss = current_value - entry_value
                            profit_loss_percent = (profit_loss / entry_value * 100) if entry_value > 0 else 0
                            
                            trade['profit_loss'] = round(profit_loss, 2)
                            trade['profit_loss_percent'] = round(profit_loss_percent, 2)
                            trade['current_value'] = round(current_value, 2)
                
                trades_data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                with open(trades_path, 'w', encoding='utf-8') as f:
                    json.dump(trades_data, f, ensure_ascii=False, indent=2)
                
                updated_files.append('simulated_trades.json')
                print(f"✅ 交易记录更新完成")
        
        except Exception as e:
            print(f"❌ 更新交易记录失败: {e}")
    
    return len(updated_files) > 0

def create_real_time_strategy():
    """创建实时策略脚本"""
    print("🔧 创建实时策略脚本...")
    
    strategy_script = """#!/usr/bin/env python3
\"\"\"
实时价格尾盘选股策略
基于真实价格执行尾盘选股
\"\"\"

import os
import sys
import json
import time
import requests
from datetime import datetime

def get_real_stock_price(stock_code):
    \"\"\"获取真实股票价格\"\"\"
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

def execute_tail_end_selection():
    \"\"\"执行尾盘选股\"\"\"
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🎯 执行尾盘选股策略")
    
    # 这里应该从数据库或配置中获取股票池
    # 暂时使用示例股票
    stock_p