#!/usr/bin/env python3
"""
切换到真实价格系统 - 简化版
获取真实股票价格，更新所有持仓和策略配置
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
    格式: 000001 -> sz000001, 600000 -> sh600000
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
            # 解析数据格式: var hq_str_sh600000="浦发银行,12.34,12.35,...";
            if '="' in content:
                data_str = content.split('="')[1].split('"')[0]
                data_parts = data_str.split(',')
                if len(data_parts) > 1:
                    # 当前价格是第二个字段
                    current_price = float(data_parts[3])  # 当前价格
                    yesterday_close = float(data_parts[2])  # 昨日收盘价

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

def update_portfolio_with_real_prices():
    """更新投资组合中的价格为真实价格"""
    print("🔍 更新投资组合为真实价格...")

    # 投资组合文件路径
    portfolio_path = "/Users/ago/.openclaw/workspace/data/simulated_trading/simulated_portfolio.json"

    if not os.path.exists(portfolio_path):
        print(f"❌ 投资组合文件不存在: {portfolio_path}")
        return False

    try:
        # 读取投资组合
        with open(portfolio_path, 'r', encoding='utf-8') as f:
            portfolio = json.load(f)

        print(f"📊 当前投资组合: {len(portfolio.get('holdings', []))} 只股票")

        # 获取所有股票代码
        stock_codes = []
        for holding in portfolio.get('holdings', []):
            stock_code = holding.get('stock_code', '')
            if stock_code:
                stock_codes.append(stock_code)

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
                print(f"    ⚠️  {stock_code}: 获取失败，使用原价")
            time.sleep(0.5)  # 避免请求过快

        # 更新投资组合
        updated_count = 0
        for holding in portfolio.get('holdings', []):
            stock_code = holding.get('stock_code', '')
            if stock_code in real_prices:
                price_data = real_prices[stock_code]

                # 更新当前价格
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

                # 更新股票名称
                holding['stock_name'] = price_data['name']

                updated_count += 1

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

        # 保存更新后的投资组合
        with open(portfolio_path, 'w', encoding='utf-8') as f:
            json.dump(portfolio, f, ensure_ascii=False, indent=2)

        print(f"✅ 成功更新 {updated_count} 只股票的实时价格")
        print(f"💰 总资产: {portfolio['total_assets']}元")
        print(f"📈 总收益率: {portfolio.get('total_return_percent', 0)}%")

        return True

    except Exception as e:
        print(f"❌ 更新投资组合失败: {e}")
        return False

def update_strategy_config():
    """更新策略配置，确保使用真实价格"""
    print("🔧 更新策略配置...")

    # 尾盘选股法Skill配置
    skill_config_path = "/Users/ago/.openclaw/workspace/skills/tail_end_selection/config.json"

    try:
        if os.path.exists(skill_config_path):
            with open(skill_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 更新配置
            config['use_real_prices'] = True
            config['price_source'] = "sina_finance"
            config['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            with open(skill_config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            print("✅ 尾盘选股法Skill配置已更新")
        else:
            print("⚠️  尾盘选股法Skill配置文件不存在，创建新配置")

            config = {
                "skill_name": "尾盘选股法",
                "version": "1.0",
                "use_real_prices": True,
                "price_source": "sina_finance",
                "max_position_percent": 0.1,
                "stop_loss_percent": 0.05,
                "take_profit_percent": 0.08,
                "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            os.makedirs(os.path.dirname(skill_config_path), exist_ok=True)
            with open(skill_config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            print("✅ 创建尾盘选股法Skill配置")

        return True

    except Exception as e:
        print(f"❌ 更新策略配置失败: {e}")
        return False

def create_real_price_monitor_script():
    """创建真实价格监控脚本"""
    print("📊 创建真实价格监控脚本...")

    monitor_script = """#!/usr/bin/env python3
\"\"\"
真实价格监控脚本
每3分钟获取一次真实价格，更新投资组合
\"\"\"

import os
import sys
import json
import time
import requests
from datetime import datetime
import schedule

def get_real_stock_price(stock_code):
    \"\"\"从新浪财经API获取真实股票价格\"\"\"
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
    \"\"\"更新投资组合价格\"\"\"
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
    \"\"\"主函数\"\"\"
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
"""

    # 保存监控脚本
    monitor_path = "/Users/ago/.openclaw/workspace/scripts/real_price_monitor.py"
    with open(monitor_path, 'w', encoding='utf-8') as f:
        f.write(monitor_script)

    # 设置执行权限
    os.chmod(monitor_path, 0o755)

    print(f"✅ 监控脚本已创建: {monitor_path}")
    return monitor_path

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 切换到真实价格系统")
    print("=" * 60)

    # 1. 更新投资组合为真实价格
    if not update_portfolio_with_real_prices():
        print("❌ 投资组合更新失败")
        return False

    print("-" * 40)

    # 2. 更新策略配置
    if not update_strategy_config():
        print("❌ 策略配置更新失败")
        return False

    print("-" * 40)

    # 3. 创建监控脚本
    monitor_path = create_real_price_monitor_script()
    print(f"📋 监控脚本位置: {monitor_path}")

    print("-" * 40)

    # 4. 创建启动脚本
    launch_script = """#!/usr/bin/env bash
# 启动真实价格监控系统
cd /Users/ago/.openclaw/workspace
python3 scripts/real_price_monitor.py
"""

    launch_path = "/Users/ago/.openclaw/workspace/scripts/start_real_price_monitor.sh"
    with open(launch_path, 'w', encoding='utf-8') as f:
        f.write(launch_script)

    os.chmod(launch_path, 0o755)
    print(f"✅ 启动脚本已创建: {launch_path}")

    print("=" * 60)
    print("🎉 真实价格系统切换完成!")
    print("=" * 60)
    print("📋 下一步操作:")
    print("1. 手动启动监控: bash scripts/start_real_price_monitor.sh")
    print("2. 或设置定时任务: 每3分钟自动更新")
    print("3. 尾盘选股策略将使用真实价格执行")
    print("=" * 60)

    return True

if __name__ == "__main__":
    main()
