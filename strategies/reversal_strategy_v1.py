#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
反转策略 v1.0
抄底超卖股，捕捉反弹机会
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class ReversalStrategy:
    """反转策略"""

    def __init__(self):
        self.strategy_name = "反转策略 v1.0"
        self.strategy_version = "1.0"
        self.author = "量化小助理"
        self.created_date = "2026-03-29"

        # 策略参数
        self.params = {
            'rsi_oversold': 30,               # RSI超卖阈值
            'rsi_overbought': 70,             # RSI超买阈值
            'max_drawdown': -0.20,            # 最大回撤阈值(-20%)
            'bollinger_bands_std': 2,         # 布林带标准差
            'volume_spike_ratio': 2.0,        # 成交量突增比率
            'recovery_days': 3,               # 反弹确认天数
            'stop_loss': -0.08,               # 止损线(-8%)
            'take_profit': 0.15,              # 止盈线(15%)
        }

        print(f"🚀 {self.strategy_name} 初始化完成")
        print(f"📊 策略参数: {self.params}")

    def identify_reversal_candidates(self):
        """识别反转候选股票"""
        print("📉 识别反转候选股票")

        # 模拟超卖股票数据
        oversold_stocks = []

        # 示例股票数据
        stocks = [
            {
                'code': '603728',
                'name': '鸣志电器',
                'current_price': 57.2,
                'cost_price': 68.0,
                'drawdown': -0.159,
                'rsi': 27.3,
                'bollinger_position': '下轨附近',
                'volume_ratio': 1.8,
                'recovery_signal': '初步企稳',
                'industry': '电机',
                'days_down': 8,
                'panic_selling': True
            },
            {
                'code': '600580',
                'name': '卧龙电驱',
                'current_price': 38.5,
                'cost_price': 42.0,
                'drawdown': -0.083,
                'rsi': 35.2,
                'bollinger_position': '中下轨',
                'volume_ratio': 1.2,
                'recovery_signal': '横盘整理',
                'industry': '新能源汽车',
                'days_down': 5,
                'panic_selling': False
            },
            {
                'code': '600096',
                'name': '云天化',
                'current_price': 34.2,
                'cost_price': 37.0,
                'drawdown': -0.076,
                'rsi': 38.5,
                'bollinger_position': '中轨',
                'volume_ratio': 0.9,
                'recovery_signal': '弱势',
                'industry': '化工',
                'days_down': 3,
                'panic_selling': False
            },
            {
                'code': '002594',
                'name': '比亚迪',
                'current_price': 105.5,
                'cost_price': 99.0,
                'drawdown': 0.066,
                'rsi': 62.3,
                'bollinger_position': '上轨',
                'volume_ratio': 1.5,
                'recovery_signal': '强势',
                'industry': '新能源汽车',
                'days_down': 0,
                'panic_selling': False
            }
        ]

        for stock in stocks:
            # 检查超卖条件
            is_oversold = (
                stock['rsi'] <= self.params['rsi_oversold'] or
                stock['drawdown'] <= self.params['max_drawdown']
            )

            # 检查反转信号
            has_reversal_signal = (
                stock['bollinger_position'] in ['下轨附近', '下轨'] or
                stock['volume_ratio'] >= self.params['volume_spike_ratio'] or
                stock['panic_selling'] == True
            )

            if is_oversold:
                if has_reversal_signal:
                    reversal_level = "🚨 强烈反转信号"
                    signal_strength = "极强"
                else:
                    reversal_level = "📉 超卖待反弹"
                    signal_strength = "强"
            elif stock['rsi'] <= 40:
                reversal_level = "📊 接近超卖"
                signal_strength = "中"
            else:
                reversal_level = "📈 非超卖区"
                signal_strength = "弱"

            # 计算风险收益比
            if stock['drawdown'] < 0:
                risk_reward_ratio = abs(self.params['take_profit'] / stock['drawdown'])
            else:
                risk_reward_ratio = 1.0

            oversold_stocks.append({
                **stock,
                'reversal_level': reversal_level,
                'signal_strength': signal_strength,
                'is_oversold': is_oversold,
                'has_reversal_signal': has_reversal_signal,
                'risk_reward_ratio': round(risk_reward_ratio, 2)
            })

        return pd.DataFrame(oversold_stocks)

    def generate_trading_signals(self, reversal_stocks):
        """生成交易信号"""
        print("\n🎯 生成反转交易信号")

        signals = []

        for _, stock in reversal_stocks.iterrows():
            if stock['reversal_level'] == "🚨 强烈反转信号":
                # 强烈反转信号
                signal_type = "BUY"
                signal_score = 90
                reason = f"强烈反转信号，{stock['reversal_level']}，{stock['recovery_signal']}"
                position = "建议仓位: 8-12%"
                stop_loss = f"止损: {abs(stock['drawdown']*100):.1f}%"
                take_profit = f"止盈: {self.params['take_profit']*100:.0f}%"

            elif stock['reversal_level'] == "📉 超卖待反弹":
                signal_type = "BUY"
                signal_score = 75
                reason = f"超卖待反弹，{stock['reversal_level']}，RSI: {stock['rsi']}"
                position = "建议仓位: 5-8%"
                stop_loss = f"止损: {abs(self.params['stop_loss']*100):.0f}%"
                take_profit = f"止盈: {self.params['take_profit']*100:.0f}%"

            elif stock['reversal_level'] == "📊 接近超卖":
                signal_type = "HOLD"
                signal_score = 60
                reason = f"接近超卖区，{stock['reversal_level']}，继续观察"
                position = "建议仓位: 3-5%"
                stop_loss = f"止损: {abs(self.params['stop_loss']*100):.0f}%"
                take_profit = f"止盈: {self.params['take_profit']*100:.0f}%"

            else:
                signal_type = "HOLD"
                signal_score = 45
                reason = f"非超卖区，{stock['reversal_level']}"
                position = "建议仓位: 0-3%"
                stop_loss = "无需设置"
                take_profit = "无需设置"

            # 考虑风险收益比
            if stock['risk_reward_ratio'] >= 2.0 and signal_type == "BUY":
                signal_score += 10
                reason += f"，风险收益比优秀({stock['risk_reward_ratio']}:1)"
            elif stock['risk_reward_ratio'] < 1.0 and signal_type == "BUY":
                signal_score -= 10
                reason += f"，风险收益比不佳({stock['risk_reward_ratio']}:1)"

            # 考虑恐慌性抛售
            if stock['panic_selling'] and signal_type == "BUY":
                signal_score += 5
                reason += "，恐慌性抛售后的反弹机会"

            signals.append({
                'code': stock['code'],
                'name': stock['name'],
                'signal_type': signal_type,
                'signal_score': signal_score,
                'reason': reason,
                'position': position,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'reversal_level': stock['reversal_level'],
                'drawdown': f"{stock['drawdown']*100:.1f}%",
                'rsi': stock['rsi'],
                'bollinger_position': stock['bollinger_position'],
                'volume_ratio': stock['volume_ratio'],
                'risk_reward_ratio': stock['risk_reward_ratio'],
                'panic_selling': '是' if stock['panic_selling'] else '否',
                'days_down': stock['days_down']
            })

        signals_df = pd.DataFrame(signals)
        signals_df = signals_df.sort_values('signal_score', ascending=False)

        return signals_df

    def run_strategy(self):
        """运行策略"""
        print(f"\n🚀 开始运行 {self.strategy_name}")
        print("=" * 60)

        try:
            # 1. 识别反转候选股票
            reversal_stocks = self.identify_reversal_candidates()

            # 2. 生成交易信号
            signals_df = self.generate_trading_signals(reversal_stocks)

            # 3. 生成报告
            report = self.generate_analysis_report(signals_df)

            print(f"\n✅ {self.strategy_name} 执行完成")
            return {
                'success': True,
                'signals': signals_df,
                'report': report
            }

        except Exception as e:
            print(f"❌ 策略执行失败: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}

    def generate_analysis_report(self, signals_df):
        """生成分析报告"""
        print("\n📋 反转策略分析报告")
        print("=" * 60)

        report = {
            'strategy_name': self.strategy_name,
            'analysis_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'total_stocks': len(signals_df) if signals_df is not None else 0,
            'buy_signals': 0,
            'strong_reversal': 0,
            'high_rr_ratio': 0,
            'details': []
        }

        if signals_df is not None and not signals_df.empty:
            report['buy_signals'] = len(signals_df[signals_df['signal_type'] == 'BUY'])
            report['strong_reversal'] = len(signals_df[signals_df['reversal_level'] == '🚨 强烈反转信号'])
            report['high_rr_ratio'] = len(signals_df[signals_df['risk_reward_ratio'] >= 2.0])

            print(f"📊 信号统计:")
            print(f"  分析股票: {report['total_stocks']} 只")
            print(f"  买入信号: {report['buy_signals']} 只")
            print(f"  强烈反转: {report['strong_reversal']} 只")
            print(f"  高风报比: {report['high_rr_ratio']} 只")

            print(f"\n🎯 强烈反转机会:")
            strong_reversals = signals_df[signals_df['reversal_level'] == '🚨 强烈反转信号']
            for idx, (_, row) in enumerate(strong_reversals.head(3).iterrows(), 1):
                print(f"  {idx}. {row['code']} {row['name']}")
                print(f"     回撤: {row['drawdown']}，RSI: {row['rsi']}")
                print(f"     风报比: {row['risk_reward_ratio']}:1")
                print(f"     信号: {row['signal_type']} (分数: {row['signal_score']})")

        # 保存报告
        if signals_df is not None:
            report_file = f"reports/reversal_analysis_{datetime.now().strftime('%Y%m%d')}.csv"
            signals_df.to_csv(report_file, index=False, encoding='utf-8-sig')
            print(f"\n💾 详细报告已保存: {report_file}")

        return report


def main():
    """主函数"""
    strategy = ReversalStrategy()
    result = strategy.run_strategy()

    if result['success']:
        print("\n🎉 反转策略执行成功！")
        print("=" * 60)

        signals = result.get('signals')
        if signals is not None and not signals.empty:
            print("\n📊 反转交易信号汇总:")
            print("-" * 50)
            for _, row in signals.iterrows():
                emoji = "🟢" if row['signal_type'] == 'BUY' else "🔴" if row['signal_type'] == 'SELL' else "🟡"
                print(f"{emoji} {row['code']} {row['name']:10} | {row['signal_type']:4} | 反转: {row['reversal_level']} | 分数: {row['signal_score']:3}")

        report = result.get('report', {})
        print(f"\n📈 策略表现:")
        print(f"  强烈反转信号: {report.get('strong_reversal', 0)} 只")
        print(f"  高风报比机会: {report.get('high_rr_ratio', 0)} 只")

        print("\n💡 使用建议:")
        print("  1. 关注超卖股票的企稳信号")
        print("  2. 严格止损，控制下行风险")
        print("  3. 优先选择风险收益比>2:1的机会")
        print("  4. 结合其他策略验证反转有效性")

    else:
        print(f"\n❌ 策略执行失败: {result.get('error', '未知错误')}")

    return 0 if result['success'] else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
