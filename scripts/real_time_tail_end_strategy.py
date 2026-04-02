#!/usr/bin/env python3
"""
实时价格尾盘选股策略
基于真实价格执行尾盘选股，每3分钟更新价格
"""

import os
import sys
import json
import time
import requests
import schedule
from datetime import datetime

def get_real_stock_price(stock_code):
    """获取真实股票价格"""
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
                        'yesterday_close': round(yesterday_close, 2),
                        'change_percent': round(change_percent, 2),
                        'high': float(data_parts[4]),
                        'low': float(data_parts[5]),
                        'volume': int(data_parts[8]),
                        'amount': float(data_parts[9]),
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
    except Exception as e:
        print(f"获取股票 {stock_code} 价格失败: {e}")

    return None

def update_portfolio_prices():
    """更新投资组合价格"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 更新投资组合价格...")

    portfolio_path = "/Users/ago/.openclaw/workspace/data/investment_tracking/investment_portfolio.json"

    if not os.path.exists(portfolio_path):
        print("❌ 投资组合文件不存在")
        return

    try:
        with open(portfolio_path, 'r', encoding='utf-8') as f:
            portfolio = json.load(f)

        stocks = portfolio.get('stocks', [])
        if not stocks:
            print("⚠️  投资组合为空")
            return

        # 获取所有股票代码
        stock_codes = [stock['code'] for stock in stocks if 'code' in stock]

        # 获取真实价格
        real_prices = {}
        for stock_code in stock_codes:
            price_data = get_real_stock_price(stock_code)
            if price_data:
                real_prices[stock_code] = price_data
            time.sleep(0.3)

        # 更新投资组合
        updated_count = 0
        for stock in stocks:
            stock_code = stock.get('code', '')
            if stock_code in real_prices:
                price_data = real_prices[stock_code]

                # 更新价格信息
                stock['current_price'] = price_data['current_price']
                stock['current_change'] = price_data['change_percent']
                stock['price_source'] = 'sina_real_time'
                stock['price_timestamp'] = price_data['timestamp']

                # 重新计算进场点位
                current_price = price_data['current_price']
                stock['entry_strategy'] = {
                    '激进进场': round(current_price * 0.99, 2),
                    '稳健进场': round(current_price * 0.97, 2),
                    '保守进场': round(current_price * 0.95, 2)
                }

                # 重新计算止损止盈
                aggressive_entry = current_price * 0.99
                stock['stop_loss'] = round(aggressive_entry * 0.92, 2)
                stock['take_profit'] = [
                    round(aggressive_entry * 1.08, 2),
                    round(aggressive_entry * 1.15, 2)
                ]

                updated_count += 1

        # 更新投资组合信息
        portfolio['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        portfolio['price_source'] = 'sina_real_time'

        # 保存
        with open(portfolio_path, 'w', encoding='utf-8') as f:
            json.dump(portfolio, f, ensure_ascii=False, indent=2)

        print(f"✅ 投资组合价格更新完成，更新了 {updated_count} 只股票")

    except Exception as e:
        print(f"❌ 更新失败: {e}")

def check_entry_conditions():
    """检查进场条件"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 检查进场条件...")

    portfolio_path = "/Users/ago/.openclaw/workspace/data/investment_tracking/investment_portfolio.json"

    if not os.path.exists(portfolio_path):
        return

    try:
        with open(portfolio_path, 'r', encoding='utf-8') as f:
            portfolio = json.load(f)

        stocks = portfolio.get('stocks', [])
        if not stocks:
            return

        opportunities = []
        for stock in stocks:
            if stock.get('status') == '待进场':
                current_price = stock.get('current_price', 0)
                entry_strategy = stock.get('entry_strategy', {})

                # 检查是否达到进场条件
                aggressive_entry = entry_strategy.get('激进进场', 0)
                conservative_entry = entry_strategy.get('保守进场', 0)

                if current_price <= aggressive_entry:
                    opportunities.append({
                        'code': stock['code'],
                        'name': stock['name'],
                        'current_price': current_price,
                        'aggressive_entry': aggressive_entry,
                        'conservative_entry': conservative_entry,
                        'condition': '达到激进进场条件',
                        'recommendation': '立即进场'
                    })
                elif current_price <= conservative_entry:
                    opportunities.append({
                        'code': stock['code'],
                        'name': stock['name'],
                        'current_price': current_price,
                        'aggressive_entry': aggressive_entry,
                        'conservative_entry': conservative_entry,
                        'condition': '达到保守进场条件',
                        'recommendation': '可以考虑进场'
                    })

        if opportunities:
            print(f"🎯 发现 {len(opportunities)} 个进场机会:")
            for opp in opportunities:
                print(f"   {opp['code']} {opp['name']}: {opp['current_price']}元 ({opp['condition']})")
        else:
            print("📊 暂无进场机会")

    except Exception as e:
        print(f"❌ 检查进场条件失败: {e}")

def execute_tail_end_selection():
    """执行尾盘选股 (14:30-15:00)"""
    current_time = datetime.now()
    current_hour = current_time.hour
    current_minute = current_time.minute

    # 只在尾盘时段执行 (14:30-15:00)
    if current_hour == 14 and current_minute >= 30 or current_hour == 15 and current_minute == 0:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🎯 执行尾盘选股策略")

        # 这里应该从数据库或配置中获取股票池
        # 暂时使用示例股票
        stock_pool = [
            '000001', '000002', '000006', '000009', '000010',
            '600000', '600016', '600036', '600519', '600585'
        ]

        selected_stocks = []

        # 获取股票价格并筛选
        for stock_code in stock_pool:
            price_data = get_real_stock_price(stock_code)
            if price_data:
                # 简单的筛选逻辑 (示例)
                if 5 <= price_data['current_price'] <= 50:  # 价格在5-50元之间
                    selected_stocks.append({
                        'code': stock_code,
                        'name': price_data['name'],
                        'current_price': price_data['current_price'],
                        'change_percent': price_data['change_percent'],
                        'score': 60,  # 示例评分
                        'selection_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
            time.sleep(0.5)

        if selected_stocks:
            # 保存选股结果
            result = {
                'selection_time': datetime.now().strftime('%Y%m%d_%H%M%S'),
                'strategy_name': '尾盘选股策略 (真实价格版)',
                'strategy_version': 'v1.0',
                'total_selected': len(selected_stocks),
                'stocks': selected_stocks
            }

            result_path = f"/Users/ago/.openclaw/workspace/data/tail_end_selection/tail_end_selection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs(os.path.dirname(result_path), exist_ok=True)

            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            print(f"✅ 尾盘选股完成，选出 {len(selected_stocks)} 只股票")
            print(f"💾 结果保存到: {result_path}")
        else:
            print("⚠️  尾盘选股未选出任何股票")

def generate_daily_report():
    """生成每日报告 (18:00)"""
    current_time = datetime.now()
    if current_time.hour == 18 and current_time.minute == 0:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 📊 生成每日报告...")

        # 读取投资组合
        portfolio_path = "/Users/ago/.openclaw/workspace/data/investment_tracking/investment_portfolio.json"

        if os.path.exists(portfolio_path):
            with open(portfolio_path, 'r', encoding='utf-8') as f:
                portfolio = json.load(f)

            # 生成报告
            report = f"""# 尾盘选股策略每日报告
## 报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
## 策略版本: 尾盘选股策略 (真实价格版) v1.0

### 📊 投资组合概览
- 总股票数: {len(portfolio.get('stocks', []))}
- 最后更新: {portfolio.get('last_updated', 'N/A')}
- 价格来源: {portfolio.get('price_source', 'N/A')}

### 📈 股票详情
"""

            for stock in portfolio.get('stocks', []):
                report += f"""
#### {stock.get('code', '')} {stock.get('name', '')}
- 当前价格: {stock.get('current_price', 0)}元
- 今日涨跌: {stock.get('current_change', 0)}%
- 状态: {stock.get('status', 'N/A')}
- 激进进场: {stock.get('entry_strategy', {}).get('激进进场', 0)}元
- 保守进场: {stock.get('entry_strategy', {}).get('保守进场', 0)}元
- 止损位: {stock.get('stop_loss', 0)}元
- 第一止盈: {stock.get('take_profit', [0, 0])[0]}元
"""

            # 保存报告
            report_path = f"/Users/ago/.openclaw/workspace/reports/tail_end_daily_report_{datetime.now().strftime('%Y%m%d')}.md"
            os.makedirs(os.path.dirname(report_path), exist_ok=True)

            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)

            print(f"✅ 每日报告生成完成: {report_path}")

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 实时价格尾盘选股策略系统")
    print("=" * 60)
    print(f"📅 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📋 系统功能:")
    print("1. 🔄 每3分钟更新投资组合价格")
    print("2. 🔍 每5分钟检查进场条件")
    print("3. 🎯 14:30-15:00执行尾盘选股")
    print("4. 📊 18:00生成每日报告")
    print("=" * 60)

    # 设置定时任务
    schedule.every(3).minutes.do(update_portfolio_prices)
    schedule.every(5).minutes.do(check_entry_conditions)
    schedule.every(1).minutes.do(execute_tail_end_selection)  # 每分钟检查是否需要执行尾盘选股
    schedule.every(1).minutes.do(generate_daily_report)  # 每分钟检查是否需要生成报告

    # 立即执行一次
    update_portfolio_prices()
    check_entry_conditions()

    print("⏰ 定时任务已设置")
    print("🔄 系统运行中...")
    print("=" * 60)

    # 保持运行
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 系统已停止")

if __name__ == "__main__":
    main()
