#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版策略点位计算
为量化策略添加具体的入场出场点位
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class TradingPointsCalculator:
    """交易点位计算器"""

    def __init__(self):
        self.calculator_name = "交易点位计算器 v1.0"

        # 技术分析参数
        self.params = {
            'support_resistance_lookback': 20,  # 支撑阻力计算周期
            'atr_period': 14,                   # ATR计算周期
            'volatility_multiplier': 1.5,       # 波动率乘数
            'risk_reward_ratio': 2.0,           # 风险收益比
            'min_position_size': 0.05,          # 最小仓位5%
            'max_position_size': 0.20,          # 最大仓位20%
        }

        print(f"🚀 {self.calculator_name} 初始化完成")

    def calculate_support_resistance(self, price_data):
        """计算支撑阻力位"""
        if len(price_data) < self.params['support_resistance_lookback']:
            return {'support': None, 'resistance': None}

        # 简单实现：使用近期高低点
        recent_data = price_data[-self.params['support_resistance_lookback']:]

        support = recent_data.min()
        resistance = recent_data.max()
        current = price_data.iloc[-1]

        # 计算具体支撑阻力位
        levels = {
            'strong_support': support * 0.98,      # 强支撑
            'weak_support': (support + current) / 2,  # 弱支撑
            'current_price': current,
            'weak_resistance': (current + resistance) / 2,  # 弱阻力
            'strong_resistance': resistance * 1.02,  # 强阻力
            'recent_high': resistance,
            'recent_low': support
        }

        return levels

    def calculate_atr(self, high, low, close, period=14):
        """计算平均真实波幅(ATR)"""
        if len(high) < period:
            return 0

        tr = np.maximum(
            high - low,
            np.maximum(
                abs(high - close.shift(1)),
                abs(low - close.shift(1))
            )
        )

        atr = tr.rolling(window=period).mean().iloc[-1]
        return atr

    def calculate_entry_points(self, stock_data, strategy_signal):
        """计算入场点位"""
        print(f"🎯 计算 {stock_data.get('code', '未知')} 入场点位")

        # 模拟价格数据
        current_price = stock_data.get('current_price', 100)
        volatility = stock_data.get('volatility', 0.02)  # 2%波动率

        # 基于策略信号计算入场区间
        if strategy_signal == 'BUY':
            # 买入策略的入场点位
            entry_points = {
                'aggressive_entry': current_price * (1 - volatility * 0.5),  # 激进入场
                'normal_entry': current_price * (1 - volatility * 0.3),      # 正常入场
                'conservative_entry': current_price * (1 - volatility * 0.1), # 保守入场
                'breakout_entry': current_price * (1 + volatility * 0.2),    # 突破入场
                'current_price': current_price
            }

            # 入场建议
            advice = {
                'best_entry': 'normal_entry',
                'price_range': f"{entry_points['conservative_entry']:.2f}-{entry_points['breakout_entry']:.2f}",
                'trigger_condition': f"价格回调至{entry_points['normal_entry']:.2f}或突破{entry_points['breakout_entry']:.2f}",
                'timing_suggestion': '上午10:00-11:00或下午14:00-14:30'
            }

        elif strategy_signal == 'SELL':
            # 卖出策略的入场点位
            entry_points = {
                'aggressive_entry': current_price * (1 + volatility * 0.5),  # 激进出场
                'normal_entry': current_price * (1 + volatility * 0.3),      # 正常出场
                'conservative_entry': current_price * (1 + volatility * 0.1), # 保守出场
                'breakdown_entry': current_price * (1 - volatility * 0.2),   # 跌破出场
                'current_price': current_price
            }

            advice = {
                'best_entry': 'normal_entry',
                'price_range': f"{entry_points['breakdown_entry']:.2f}-{entry_points['conservative_entry']:.2f}",
                'trigger_condition': f"价格反弹至{entry_points['normal_entry']:.2f}或跌破{entry_points['breakdown_entry']:.2f}",
                'timing_suggestion': '避开开盘半小时，选择流动性好的时段'
            }

        else:  # HOLD
            entry_points = {'current_price': current_price}
            advice = {
                'best_entry': '等待更好机会',
                'price_range': '观察',
                'trigger_condition': '等待明确信号',
                'timing_suggestion': '继续观察'
            }

        return {
            'entry_points': entry_points,
            'advice': advice,
            'current_price': current_price
        }

    def calculate_exit_points(self, entry_price, strategy_type, stock_data):
        """计算出场点位"""
        print(f"🎯 计算出场点位 (入场价: {entry_price:.2f})")

        current_price = stock_data.get('current_price', entry_price)
        volatility = stock_data.get('volatility', 0.02)

        # 基于策略类型计算止盈止损
        if strategy_type == 'momentum':  # 动量策略
            take_profit = entry_price * (1 + volatility * 3)  # 3倍波动率
            stop_loss = entry_price * (1 - volatility * 1.5)  # 1.5倍波动率
            trailing_stop = entry_price * (1 + volatility * 2)  # 移动止盈

        elif strategy_type == 'reversal':  # 反转策略
            take_profit = entry_price * (1 + volatility * 2.5)  # 2.5倍波动率
            stop_loss = entry_price * (1 - volatility * 1.0)  # 1倍波动率
            trailing_stop = entry_price * (1 + volatility * 1.5)  # 保守移动止盈

        elif strategy_type == 'trend':  # 趋势策略
            take_profit = entry_price * (1 + volatility * 4)  # 4倍波动率
            stop_loss = entry_price * (1 - volatility * 2)  # 2倍波动率
            trailing_stop = entry_price * (1 + volatility * 3)  # 积极移动止盈

        else:  # 默认
            take_profit = entry_price * (1 + volatility * 2)  # 2倍波动率
            stop_loss = entry_price * (1 - volatility * 1)  # 1倍波动率
            trailing_stop = entry_price * (1 + volatility * 1.5)  # 标准移动止盈

        exit_points = {
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'trailing_stop': trailing_stop,
            'risk_reward_ratio': (take_profit - entry_price) / (entry_price - stop_loss),
            'profit_target_pct': (take_profit / entry_price - 1) * 100,
            'stop_loss_pct': (1 - stop_loss / entry_price) * 100
        }

        # 出场建议
        advice = {
            'primary_exit': 'take_profit' if exit_points['risk_reward_ratio'] >= 2 else 'trailing_stop',
            'exit_strategy': '分批止盈，移动止损',
            'monitor_frequency': '每日收盘检查，关键点位实时监控',
            'adjustment_rules': '价格上涨后提高止损至成本价，达到第一目标后移动止盈'
        }

        return {
            'exit_points': exit_points,
            'advice': advice
        }

    def calculate_position_size(self, account_size, risk_per_trade, stop_loss_pct):
        """计算仓位大小"""
        # 凯利公式简化版
        risk_amount = account_size * risk_per_trade
        position_size = risk_amount / abs(stop_loss_pct / 100)

        # 限制仓位大小
        position_size = min(position_size, account_size * self.params['max_position_size'])
        position_size = max(position_size, account_size * self.params['min_position_size'])

        return {
            'position_size': position_size,
            'position_pct': position_size / account_size * 100,
            'risk_amount': risk_amount,
            'shares_to_buy': int(position_size / 100) * 100  # 按手数取整
        }

    def generate_trading_plan(self, stock_info, strategy_signals):
        """生成完整交易计划"""
        print(f"\n📋 生成交易计划: {stock_info.get('code')} {stock_info.get('name')}")
        print("=" * 60)

        # 获取主要策略信号
        main_signal = strategy_signals.get('consensus_signal', 'HOLD')
        signal_score = strategy_signals.get('signal_score', 50)
        confidence = strategy_signals.get('confidence', 50)

        # 计算入场点位
        entry_calculation = self.calculate_entry_points(stock_info, main_signal)

        # 选择最佳入场价
        best_entry_price = entry_calculation['entry_points'].get(
            entry_calculation['advice']['best_entry'],
            stock_info.get('current_price', 100)
        )

        # 计算出场点位
        strategy_type = self._determine_strategy_type(strategy_signals)
        exit_calculation = self.calculate_exit_points(best_entry_price, strategy_type, stock_info)

        # 计算仓位
        account_size = 1000000  # 假设账户规模100万
        risk_per_trade = 0.02 if confidence >= 70 else 0.01  # 2%或1%风险
        position_calculation = self.calculate_position_size(
            account_size, risk_per_trade, exit_calculation['exit_points']['stop_loss_pct']
        )

        # 生成完整交易计划
        trading_plan = {
            'stock_info': {
                'code': stock_info.get('code'),
                'name': stock_info.get('name'),
                'industry': stock_info.get('industry', '未知'),
                'current_price': stock_info.get('current_price', 100)
            },
            'strategy_signals': strategy_signals,
            'entry_plan': {
                'signal': main_signal,
                'signal_score': signal_score,
                'confidence': confidence,
                'best_entry_price': best_entry_price,
                'price_range': entry_calculation['advice']['price_range'],
                'trigger_condition': entry_calculation['advice']['trigger_condition'],
                'timing_suggestion': entry_calculation['advice']['timing_suggestion'],
                'entry_type': entry_calculation['advice']['best_entry']
            },
            'exit_plan': {
                'take_profit': exit_calculation['exit_points']['take_profit'],
                'stop_loss': exit_calculation['exit_points']['stop_loss'],
                'trailing_stop': exit_calculation['exit_points']['trailing_stop'],
                'risk_reward_ratio': round(exit_calculation['exit_points']['risk_reward_ratio'], 2),
                'profit_target_pct': f"{exit_calculation['exit_points']['profit_target_pct']:.1f}%",
                'stop_loss_pct': f"{exit_calculation['exit_points']['stop_loss_pct']:.1f}%",
                'exit_strategy': exit_calculation['advice']['exit_strategy'],
                'adjustment_rules': exit_calculation['advice']['adjustment_rules']
            },
            'position_plan': {
                'position_size': position_calculation['position_size'],
                'position_pct': f"{position_calculation['position_pct']:.1f}%",
                'shares_to_buy': position_calculation['shares_to_buy'],
                'risk_amount': position_calculation['risk_amount'],
                'account_size': account_size
            },
            'holding_strategy': {
                'holding_period': '10-20天' if strategy_type == 'momentum' else '5-15天',
                'monitor_frequency': '每日收盘检查，关键点位实时监控',
                'reassessment_triggers': [
                    '达到止盈目标50%',
                    '价格触及止损区域',
                    '基本面重大变化',
                    '策略信号反转'
                ]
            }
        }

        return trading_plan

    def _determine_strategy_type(self, strategy_signals):
        """确定策略类型"""
        if 'momentum' in str(strategy_signals).lower():
            return 'momentum'
        elif 'reversal' in str(strategy_signals).lower():
            return 'reversal'
        elif 'trend' in str(strategy_signals).lower():
            return 'trend'
        else:
            return 'general'

    def format_trading_plan(self, trading_plan):
        """格式化交易计划输出"""
        print(f"\n🎯 交易计划: {trading_plan['stock_info']['code']} {trading_plan['stock_info']['name']}")
        print("=" * 60)

        # 股票信息
        stock = trading_plan['stock_info']
        print(f"📊 股票信息:")
        print(f"  代码: {stock['code']}")
        print(f"  名称: {stock['name']}")
        print(f"  行业: {stock['industry']}")
        print(f"  当前价: {stock['current_price']:.2f}元")

        # 入场计划
        entry = trading_plan['entry_plan']
        print(f"\n🎯 入场计划:")
        print(f"  信号: {entry['signal']} (分数: {entry['signal_score']}, 置信度: {entry['confidence']}%)")
        print(f"  最佳入场价: {entry['best_entry_price']:.2f}元")
        print(f"  价格区间: {entry['price_range']}元")
        print(f"  触发条件: {entry['trigger_condition']}")
        print(f"  时机建议: {entry['timing_suggestion']}")

        # 出场计划
        exit_plan = trading_plan['exit_plan']
        print(f"\n🚪 出场计划:")
        print(f"  止盈目标: {exit_plan['take_profit']:.2f}元 ({exit_plan['profit_target_pct']})")
        print(f"  止损点位: {exit_plan['stop_loss']:.2f}元 ({exit_plan['stop_loss_pct']})")
        print(f"  移动止损: {exit_plan['trailing_stop']:.2f}元")
        print(f"  风险收益比: {exit_plan['risk_reward_ratio']}:1")
        print(f"  出场策略: {exit_plan['exit_strategy']}")

        # 仓位计划
        position = trading_plan['position_plan']
        print(f"\n💰 仓位计划:")
        print(f"  建议仓位: {position['position_pct']} ({position['position_size']:,.0f}元)")
        print(f"  买入股数: {position['shares_to_buy']}股")
        print(f"  单笔风险: {position['risk_amount']:,.0f}元")

        # 持有策略
        holding = trading_plan['holding_strategy']
        print(f"\n⏳ 持有策略:")
        print(f"  持有周期: {holding['holding_period']}")
        print(f"  监控频率: {holding['monitor_frequency']}")
        print(f"  重估触发:")
        for trigger in holding['reassessment_triggers']:
            print(f"    • {trigger}")

        print("\n" + "=" * 60)
        print("✅ 交易计划生成完成")


def main():
    """主函数"""
    print("🚀 增强版策略点位计算演示")
    print("=" * 70)

    # 创建计算器
    calculator = TradingPointsCalculator()

    # 示例股票数据
    stock_examples = [
        {
            'code': '002594',
            'name': '比亚迪',
            'industry': '新能源汽车',
            'current_price': 105.5,
            'volatility': 0.025
        },
        {
            'code': '603728',
            'name': '鸣志电器',
            'industry': '电机',
            'current_price': 57.2,
            'volatility': 0.035
        }
    ]

    # 示例策略信号
    strategy_signals_examples = [
        {
            'consensus_signal': 'BUY',
            'signal_score': 85,
            'confidence': 75,
            'strategies': ['动量策略', '资金流向策略', '题材热度策略']
        },
        {
            'consensus_signal': 'BUY',
            'signal_score': 80,
            'confidence': 70,
            'strategies': ['反转策略', '超卖反弹']
        }
    ]

    # 为每只股票生成交易计划
