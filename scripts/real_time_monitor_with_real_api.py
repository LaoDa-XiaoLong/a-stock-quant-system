#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时股票监控系统 - 使用真实API价格
每3分钟获取一次真实价格，自动检查进场条件
"""

import json
import time
import schedule
import threading
from datetime import datetime, timedelta
import os
import sys
import requests
import re

class RealTimeStockMonitorWithRealAPI:
    """使用真实API的实时股票监控系统"""

    def __init__(self):
        self.tracking_dir = 'data/investment_tracking'
        self.portfolio_file = f'{self.tracking_dir}/investment_portfolio.json'
        self.monitor_log_file = f'{self.tracking_dir}/monitor_log_{datetime.now().strftime("%Y%m%d")}.log'

        # 交易时间配置
        self.trading_hours = {
            'morning_start': '09:30',
            'morning_end': '11:30',
            'afternoon_start': '13:00',
            'afternoon_end': '15:00'
        }

        # 监控间隔（秒）
        self.monitor_interval = 180  # 3分钟

        # 加载投资组合
        self.portfolio = self.load_portfolio()

        # 监控状态
        self.monitoring = False
        self.monitor_thread = None

        # 创建日志目录
        os.makedirs(self.tracking_dir, exist_ok=True)

        print("🚀 实时股票监控系统（真实API版）初始化完成")
        print(f"📊 监控股票数量: {len(self.portfolio['stocks'])}")
        print(f"⏰ 交易时间: {self.trading_hours['morning_start']}-{self.trading_hours['morning_end']}, "
              f"{self.trading_hours['afternoon_start']}-{self.trading_hours['afternoon_end']}")
        print(f"🔄 监控间隔: {self.monitor_interval}秒")
        print(f"📡 数据源: 新浪财经实时API")

    def load_portfolio(self):
        """加载投资组合"""
        if not os.path.exists(self.portfolio_file):
            print(f"❌ 投资组合文件不存在: {self.portfolio_file}")
            return {'stocks': []}

        with open(self.portfolio_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_portfolio(self):
        """保存投资组合"""
        with open(self.portfolio_file, 'w', encoding='utf-8') as f:
            json.dump(self.portfolio, f, ensure_ascii=False, indent=2)

    def log_message(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        with open(self.monitor_log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)

        print(log_entry.strip())

    def is_trading_time(self) -> bool:
        """判断当前是否为交易时间"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")

        # 检查是否为交易日（周一至周五）
        weekday = now.weekday()  # 0=周一, 4=周五
        if weekday >= 5:  # 周六日
            return False

        # 检查时间
        morning_start = self.trading_hours['morning_start']
        morning_end = self.trading_hours['morning_end']
        afternoon_start = self.trading_hours['afternoon_start']
        afternoon_end = self.trading_hours['afternoon_end']

        return (morning_start <= current_time <= morning_end) or \
               (afternoon_start <= current_time <= afternoon_end)

    def get_real_time_price_sina(self, stock_code: str):
        """使用新浪财经获取实时价格"""
        try:
            # 确定市场前缀
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

            # 解析数据
            data_str = response.text
            match = re.search(r'="(.*?)"', data_str)

            if match:
                data = match.group(1).split(',')
                if len(data) > 3:
                    stock_name = data[0]
                    latest_price = float(data[3])  # 最新价
                    yesterday_close = float(data[2])  # 昨日收盘价

                    if yesterday_close > 0:
                        change_pct = (latest_price - yesterday_close) / yesterday_close * 100
                    else:
                        change_pct = 0.0

                    return {
                        'success': True,
                        'price': latest_price,
                        'change_pct': change_pct,
                        'name': stock_name,
                        'yesterday_close': yesterday_close,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }

            return {
                'success': False,
                'error': '数据解析失败'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def check_entry_conditions(self, stock: dict, current_price: float) -> tuple:
        """检查是否满足进场条件"""
        if stock['status'] != '待进场':
            return False, None

        entry_strategy = stock['entry_strategy']

        # 检查是否达到任何进场条件
        if current_price <= entry_strategy['激进进场']:
            return True, '激进进场'
        elif current_price <= entry_strategy['稳健进场']:
            return True, '稳健进场'
        elif current_price <= entry_strategy['保守进场']:
            return True, '保守进场'

        return False, None

    def execute_simulated_trade(self, stock: dict, entry_type: str, current_price: float):
        """执行模拟交易"""
        stock_code = stock['code']
        stock_name = stock['name']

        # 计算仓位（模拟）
        # 假设总投资10万元，单只股票仓位10%，即1万元
        total_capital = 100000
        single_position_cap = total_capital * 0.10  # 单只股票最大仓位

        # 根据进场类型确定仓位比例
        if entry_type == '激进进场':
            position_ratio = 0.6  # 60%的仓位
        elif entry_type == '稳健进场':
            position_ratio = 0.8  # 80%的仓位
        else:  # 保守进场
            position_ratio = 1.0  # 100%的仓位

        # 计算购买数量和金额
        position_amount = single_position_cap * position_ratio
        quantity = int(position_amount / current_price / 100) * 100  # 按手数（100股）取整

        if quantity < 100:  # 最少1手
            quantity = 100

        investment = current_price * quantity

        # 更新股票信息
        stock['status'] = '已进场'
        stock['entry_price'] = current_price
        stock['entry_date'] = datetime.now().strftime('%Y-%m-%d')
        stock['entry_time'] = datetime.now().strftime('%H:%M:%S')
        stock['entry_type'] = entry_type
        stock['current_position'] = quantity
        stock['total_investment'] = investment
        stock['current_price'] = current_price
        stock['profit_loss'] = 0
        stock['profit_loss_pct'] = 0

        # 记录交易
        trade_record = {
            'stock_code': stock_code,
            'stock_name': stock_name,
            'action': '买入',
            'price': current_price,
            'quantity': quantity,
            'amount': investment,
            'entry_type': entry_type,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # 保存交易记录
        self.save_trade_record(trade_record)

        # 更新投资组合总览
        self.update_portfolio_summary()

        # 记录日志
        self.log_message(f"✅ 模拟成交: {stock_code} {stock_name}")
        self.log_message(f"   进场类型: {entry_type}")
        self.log_message(f"   成交价格: {current_price}元")
        self.log_message(f"   成交数量: {quantity}股")
        self.log_message(f"   投资金额: {investment:.2f}元")

        return True

    def save_trade_record(self, trade_record: dict):
        """保存交易记录"""
        trades_file = f'{self.tracking_dir}/trade_records_{datetime.now().strftime("%Y%m%d")}.json'

        trades = []
        if os.path.exists(trades_file):
            with open(trades_file, 'r', encoding='utf-8') as f:
                trades = json.load(f)

        trades.append(trade_record)

        with open(trades_file, 'w', encoding='utf-8') as f:
            json.dump(trades, f, ensure_ascii=False, indent=2)

    def update_portfolio_summary(self):
        """更新投资组合总览"""
        total_investment = 0
        current_value = 0

        for stock in self.portfolio['stocks']:
            if stock['status'] == '已进场':
                total_investment += stock['total_investment']
                if 'current_price' in stock:
                    current_value += stock['current_price'] * stock['current_position']

        self.portfolio['total_investment'] = total_investment
        self.portfolio['current_value'] = current_value
        self.portfolio['total_profit_loss'] = current_value - total_investment
        self.portfolio['total_profit_loss_pct'] = (current_value - total_investment) / total_investment * 100 if total_investment > 0 else 0
        self.portfolio['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.save_portfolio()

    def monitor_cycle(self):
        """监控循环"""
        self.log_message("=" * 50)
        self.log_message("📈 开始监控循环（真实API）")

        # 检查交易时间
        if not self.is_trading_time():
            self.log_message("⏸️ 非交易时间，暂停监控")
            return

        current_time = datetime.now().strftime("%H:%M:%S")
        self.log_message(f"🕐 当前时间: {current_time}")

        # 重新加载投资组合（防止外部修改）
        self.portfolio = self.load_portfolio()

        # 检查每只股票
        for stock in self.portfolio['stocks']:
            stock_code = stock['code']
            stock_name = stock['name']

            # 获取实时价格
            price_result = self.get_real_time_price_sina(stock_code)

            if price_result['success']:
                current_price = price_result['price']
                change_pct = price_result['change_pct']

                self.log_message(f"📊 {stock_code} {stock_name}: {current_price}元 ({change_pct:+.2f}%)")

                # 更新股票价格信息
                stock['current_price'] = current_price
                stock['current_change'] = change_pct
                stock['price_source'] = 'sina'
                stock['price_timestamp'] = price_result['timestamp']

                # 检查进场条件
                if stock['status'] == '待进场':
                    should_enter, entry_type = self.check_entry_conditions(stock, current_price)
                    if should_enter:
                        self.execute_simulated_trade(stock, entry_type, current_price)

                # 更新已进场股票盈亏
                elif stock['status'] == '已进场':
                    if stock['current_position'] > 0 and 'entry_price' in stock:
                        profit_loss = (current_price - stock['entry_price']) * stock['current_position']
                        profit_loss_pct = (current_price - stock['entry_price']) / stock['entry_price'] * 100

                        stock['profit_loss'] = round(profit_loss, 2)
                        stock['profit_loss_pct'] = round(profit_loss_pct, 2)

                        # 记录价格变化
                        price_change = current_price - stock.get('last_price', current_price)
                        if price_change != 0:
                            change_symbol = "📈" if price_change > 0 else "📉"
                            self.log_message(f"   {change_symbol} 价格变化: {price_change:+.2f}元, 盈亏: {stock['profit_loss']:+.2f}元 ({stock['profit_loss_pct']:+.2f}%)")

                        stock['last_price'] = current_price

                        # 检查止损止盈条件
                        self.check_stop_loss_take_profit(stock, current_price)
            else:
                self.log_message(f"❌ {stock_code} {stock_name}: 获取价格失败 - {price_result.get('error', '未知错误')}")

        # 保存更新
        self.save_portfolio()

        self.log_message("✅ 监控循环完成")
        self.log_message("=" * 50)

    def check_stop_loss_take_profit(self, stock: dict, current_price: float):
        """检查止损止盈条件"""
        if stock['status'] != '已进场' or 'entry_price' not in stock:
            return

        entry_price = stock['entry_price']

        # 检查止损
        if current_price <= stock['stop_loss']:
            self.execute_stop_loss(stock, current_price)

        # 检查止盈
        elif current_price >= stock['take_profit'][0]:
            if current_price >= stock['take_profit'][1]:
                # 达到第二止盈，全部卖出
                self.execute_take_profit(stock, current_price, '全部止盈')
            else:
                # 达到第一止盈，卖出50%
                self.execute_partial_take_profit(stock, current_price)

    def execute_stop_loss(self, stock: dict, current_price: float):
        """执行止损"""
        stock_code = stock['code']
        stock_name = stock['name']
        quantity = stock['current_position']

        # 计算盈亏
        profit_loss = (current_price - stock['entry_price']) * quantity

        # 更新股票状态
        stock['status'] = '已止损'
        stock['exit_price'] = current_price
        stock['exit_date'] = datetime.now().strftime('%Y-%m-%d')
        stock['exit_time'] = datetime.now().strftime('%H:%M:%S')
        stock['exit_reason'] = '止损'
        stock['current_position'] = 0

        # 记录交易
        trade_record = {
            'stock_code': stock_code,
            'stock_name': stock_name,
            'action': '卖出(止损)',
            'price': current_price,
            'quantity': quantity,
            'amount': current_price * quantity,
            'profit_loss': profit_loss,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        self.save_trade_record(trade_record)
        self.log_message(f"⚠️ 止损触发: {stock_code} {stock_name}")
        self.log_message(f"   进场价: {stock['entry_price']}元, 止损价: {current_price}元")
        self.log_message(f"   盈亏: {profit_loss:.2f}元 ({(current_price - stock['entry_price'])/stock['entry_price']*100:.2f}%)")

    def execute_take_profit(self, stock: dict, current_price: float, reason: str):
        """执行止盈"""
        stock_code = stock['code']
        stock_name = stock['name']
        quantity = stock['current_position']

        # 计算盈亏
        profit_loss = (current_price - stock['entry_price']) * quantity

        # 更新股票状态
        stock['status'] = '已止盈'
        stock['exit_price'] = current_price
        stock['exit_date'] = datetime.now().strftime('%Y-%m-%d')
        stock['exit_time'] = datetime.now().strftime('%H:%M:%S')
        stock['exit_reason'] = reason
        stock['current_position'] = 0

        # 记录交易
        trade_record = {
            'stock_code': stock_code,
            'stock_name': stock_name,
            'action': f'卖出({reason})',
            'price': current_price,
            'quantity': quantity,
            'amount': current_price * quantity,
            'profit_loss': profit_loss,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        self.save_trade_record(trade_record)
        self.log_message(f"🎯 {reason}: {stock_code} {stock_name}")
        self.log_message(f"   进场价: {stock['entry_price']}元, 止盈价: {current_price}元")
        self.log_message(f"   盈亏: {profit_loss:.2f}元 ({(current_price - stock['entry_price'])/stock['entry_price']*100:.2f}%)")

    def execute_partial_take_profit(self, stock: dict, current_price: float):
        """执行部分止盈（卖出50%）"""
        stock_code = stock['code']
        stock_name = stock['name']
        total_quantity = stock['current_position']
        sell_
