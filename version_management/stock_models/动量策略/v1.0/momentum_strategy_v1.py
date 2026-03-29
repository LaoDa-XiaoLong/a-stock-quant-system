#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动量策略 v1.0
追涨强势股，强者恒强
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class MomentumStrategy:
    """动量策略"""
    
    def __init__(self):
        self.strategy_name = "动量策略 v1.0"
        self.strategy_version = "1.0"
        self.author = "量化小助理"
        self.created_date = "2026-03-29"
        
        # 策略参数
        self.params = {
            'momentum_periods': [5, 10, 20],  # 动量计算周期
            'min_price_change': 0.10,         # 最小价格变化(10%)
            'volume_ratio_threshold': 1.5,    # 成交量比率阈值
            'rs_threshold': 70,               # 相对强度阈值
            'breakout_threshold': 0.05,       # 突破阈值(5%)
            'max_hold_days': 20,              # 最大持有天数
        }
        
        print(f"🚀 {self.strategy_name} 初始化完成")
        print(f"📊 策略参数: {self.params}")
    
    def calculate_momentum(self, price_series, periods):
        """计算动量指标"""
        momentums = {}
        
        for period in periods:
            if len(price_series) >= period:
                current_price = price_series.iloc[-1]
                past_price = price_series.iloc[-period]
                momentum = (current_price - past_price) / past_price
                momentums[f'{period}日动量'] = momentum
            else:
                momentums[f'{period}日动量'] = 0
        
        return momentums
    
    def calculate_relative_strength(self, stock_returns, market_returns):
        """计算相对强度"""
        if len(stock_returns) == len(market_returns):
            # 计算超额收益
            excess_returns = stock_returns - market_returns
            # 计算相对强度分数(0-100)
            rs_score = min(100, max(0, 50 + np.mean(excess_returns) * 100))
            return rs_score
        return 50  # 默认值
    
    def identify_momentum_stocks(self, stock_data):
        """识别动量股票"""
        print("📈 识别动量股票")
        
        # 模拟股票数据
        momentum_stocks = []
        
        # 示例股票数据
        stocks = [
            {
                'code': '002594',
                'name': '比亚迪',
                'current_price': 105.5,
                '5日涨幅': 0.12,
                '10日涨幅': 0.18,
                '20日涨幅': 0.25,
                '成交量比率': 1.8,
                '相对强度': 85,
                '突破状态': '突破前期高点',
                '行业': '新能源汽车'
            },
            {
                'code': '603259',
                'name': '药明康德',
                'current_price': 108.2,
                '5日涨幅': 0.08,
                '10日涨幅': 0.15,
                '20日涨幅': 0.22,
                '成交量比率': 1.6,
                '相对强度': 78,
                '突破状态': '接近前高',
                '行业': '医药'
            },
            {
                'code': '002415',
                'name': '海康威视',
                'current_price': 45.3,
                '5日涨幅': 0.15,
                '10日涨幅': 0.22,
                '20日涨幅': 0.30,
                '成交量比率': 2.1,
                '相对强度': 92,
                '突破状态': '强势突破',
                '行业': '安防'
            },
            {
                'code': '603728',
                'name': '鸣志电器',
                'current_price': 58.5,
                '5日涨幅': -0.05,
                '10日涨幅': -0.08,
                '20日涨幅': -0.12,
                '成交量比率': 0.8,
                '相对强度': 35,
                '突破状态': '下跌趋势',
                '行业': '电机'
            }
        ]
        
        for stock in stocks:
            # 检查动量条件
            meets_criteria = (
                stock['20日涨幅'] >= self.params['min_price_change'] and
                stock['成交量比率'] >= self.params['volume_ratio_threshold'] and
                stock['相对强度'] >= self.params['rs_threshold']
            )
            
            if meets_criteria:
                momentum_level = "🚀 强势动量"
                signal_strength = "极强"
            elif stock['10日涨幅'] >= self.params['min_price_change'] * 0.7:
                momentum_level = "📈 中等动量"
                signal_strength = "强"
            elif stock['5日涨幅'] >= 0:
                momentum_level = "📊 弱动量"
                signal_strength = "中"
            else:
                momentum_level = "📉 无动量"
                signal_strength = "弱"
            
            momentum_stocks.append({
                **stock,
                'momentum_level': momentum_level,
                'signal_strength': signal_strength,
                'meets_criteria': meets_criteria
            })
        
        return pd.DataFrame(momentum_stocks)
    
    def generate_trading_signals(self, momentum_stocks):
        """生成交易信号"""
        print("\n🎯 生成动量交易信号")
        
        signals = []
        
        for _, stock in momentum_stocks.iterrows():
            if stock['meets_criteria']:
                # 强势动量股票
                signal_type = "BUY"
                signal_score = 85 + min(15, stock['相对强度'] - 70)
                reason = f"强势动量股，{stock['momentum_level']}，{stock['突破状态']}"
                position = "建议仓位: 10-15%"
                hold_days = "持有周期: 10-20天"
                
            elif stock['signal_strength'] == "强":
                signal_type = "BUY"
                signal_score = 70
                reason = f"中等动量股，{stock['momentum_level']}"
                position = "建议仓位: 8-12%"
                hold_days = "持有周期: 5-15天"
                
            elif stock['signal_strength'] == "中":
                signal_type = "HOLD"
                signal_score = 55
                reason = f"弱动量，{stock['momentum_level']}"
                position = "建议仓位: 3-5%"
                hold_days = "持有周期: 观察"
                
            else:
                signal_type = "SELL"
                signal_score = 40
                reason = f"无动量或负动量，{stock['momentum_level']}"
                position = "建议减仓或回避"
                hold_days = "不建议持有"
            
            # 考虑突破状态
            if "突破" in stock['突破状态'] and signal_type == "BUY":
                signal_score += 10
                reason += "，突破形态确认"
            
            signals.append({
                'code': stock['code'],
                'name': stock['name'],
                'signal_type': signal_type,
                'signal_score': signal_score,
                'reason': reason,
                'position': position,
                'hold_days': hold_days,
                'momentum_level': stock['momentum_level'],
                '5日涨幅': f"{stock['5日涨幅']*100:.1f}%",
                '10日涨幅': f"{stock['10日涨幅']*100:.1f}%",
                '20日涨幅': f"{stock['20日涨幅']*100:.1f}%",
                '相对强度': stock['相对强度'],
                '成交量比率': stock['成交量比率'],
                '突破状态': stock['突破状态']
            })
        
        signals_df = pd.DataFrame(signals)
        signals_df = signals_df.sort_values('signal_score', ascending=False)
        
        return signals_df
    
    def run_strategy(self):
        """运行策略"""
        print(f"\n🚀 开始运行 {self.strategy_name}")
        print("=" * 60)
        
        try:
            # 1. 识别动量股票
            momentum_stocks = self.identify_momentum_stocks(None)
            
            # 2. 生成交易信号
            signals_df = self.generate_trading_signals(momentum_stocks)
            
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
        print("\n📋 动量策略分析报告")
        print("=" * 60)
        
        report = {
            'strategy_name': self.strategy_name,
            'analysis_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'total_stocks': len(signals_df) if signals_df is not None else 0,
            'buy_signals': 0,
            'strong_momentum': 0,
            'details': []
        }
        
        if signals_df is not None and not signals_df.empty:
            report['buy_signals'] = len(signals_df[signals_df['signal_type'] == 'BUY'])
            report['strong_momentum'] = len(signals_df[signals_df['momentum_level'] == '🚀 强势动量'])
            
            print(f"📊 信号统计:")
            print(f"  分析股票: {report['total_stocks']} 只")
            print(f"  买入信号: {report['buy_signals']} 只")
            print(f"  强势动量: {report['strong_momentum']} 只")
            
            print(f"\n🎯 强势动量股票:")
            strong_stocks = signals_df[signals_df['momentum_level'] == '🚀 强势动量']
            for idx, (_, row) in enumerate(strong_stocks.head(3).iterrows(), 1):
                print(f"  {idx}. {row['code']} {row['name']}")
                print(f"     动量: {row['20日涨幅']} (20日)")
                print(f"     强度: {row['相对强度']}")
                print(f"     信号: {row['signal_type']} (分数: {row['signal_score']})")
        
        # 保存报告
        if signals_df is not None:
            report_file = f"reports/momentum_analysis_{datetime.now().strftime('%Y%m%d')}.csv"
            signals_df.to_csv(report_file, index=False, encoding='utf-8-sig')
            print(f"\n💾 详细报告已保存: {report_file}")
        
        return report


def main():
    """主函数"""
    strategy = MomentumStrategy()
    result = strategy.run_strategy()
    
    if result['success']:
        print("\n🎉 动量策略执行成功！")
        print("=" * 60)
        
        signals = result.get('signals')
        if signals is not None and not signals.empty:
            print("\n📊 动量交易信号汇总:")
            print("-" * 50)
            for _, row in signals.iterrows():
                emoji = "🟢" if row['signal_type'] == 'BUY' else "🔴" if row['signal_type'] == 'SELL' else "🟡"
                print(f"{emoji} {row['code']} {row['name']:10} | {row['signal_type']:4} | 动量: {row['momentum_level']} | 分数: {row['signal_score']:3}")
        
        report = result.get('report', {})
        print(f"\n📈 策略表现:")
        print(f"  强势动量股票: {report.get('strong_momentum', 0)} 只")
        print(f"  买入建议: {report.get('buy_signals', 0)} 只")
        
        print("\n💡 使用建议:")
        print("  1. 关注强势动量股票的持续性")
        print("  2. 结合成交量确认突破有效性")
        print("  3. 设置止损，防止动量反转")
        print("  4. 注意市场整体趋势")
        
    else:
        print(f"\n❌ 策略执行失败: {result.get('error', '未知错误')}")
    
    return 0 if result['success'] else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())