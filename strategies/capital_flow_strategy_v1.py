#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主力资金流向策略 v1.0
识别A股主力资金走向，捕捉机构动向
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import akshare as ak
import warnings
warnings.filterwarnings('ignore')


class CapitalFlowStrategy:
    """主力资金流向策略"""

    def __init__(self):
        self.strategy_name = "主力资金流向策略 v1.0"
        self.strategy_version = "1.0"
        self.author = "量化小助理"
        self.created_date = "2026-03-29"

        # 策略参数
        self.params = {
            'min_capital_inflow': 10000000,  # 最小资金流入(万元)
            'flow_days': 3,                   # 连续流入天数
            'volume_ratio_threshold': 1.5,    # 成交量比率阈值
            'price_change_threshold': 0.03,   # 价格变化阈值(3%)
            'market_cap_filter': 5000000000,  # 市值过滤(50亿)
        }

        print(f"🚀 {self.strategy_name} 初始化完成")
        print(f"📊 策略参数: {self.params}")

    def fetch_capital_flow_data(self, date=None):
        """获取资金流向数据"""
        if date is None:
            date = datetime.now().strftime("%Y%m%d")

        print(f"📡 获取资金流向数据，日期: {date}")

        try:
            # 获取主力资金流向数据
            # 这里使用akshare的模拟数据，实际需要根据数据源调整
            capital_flow = ak.stock_main_fund_flow(date=date)

            if capital_flow.empty:
                print("⚠️  未获取到资金流向数据，使用模拟数据")
                capital_flow = self._generate_mock_capital_flow()

            return capital_flow

        except Exception as e:
            print(f"❌ 获取资金流向数据失败: {e}")
            print("⚠️  使用模拟数据进行策略演示")
            return self._generate_mock_capital_flow()

    def _generate_mock_capital_flow(self):
        """生成模拟资金流向数据（演示用）"""
        print("📊 生成模拟资金流向数据（演示）")

        # 模拟7只持仓股票的资金流向
        stocks = [
            {'code': '002594', 'name': '比亚迪', 'main_inflow': 15000, 'retail_inflow': 5000},
            {'code': '603728', 'name': '鸣志电器', 'main_inflow': 8000, 'retail_inflow': 2000},
            {'code': '600580', 'name': '卧龙电驱', 'main_inflow': 12000, 'retail_inflow': 3000},
            {'code': '600183', 'name': '生益科技', 'main_inflow': -5000, 'retail_inflow': 1000},
            {'code': '603259', 'name': '药明康德', 'main_inflow': 20000, 'retail_inflow': 6000},
            {'code': '002352', 'name': '顺丰控股', 'main_inflow': 9000, 'retail_inflow': 2500},
            {'code': '600096', 'name': '云天化', 'main_inflow': -3000, 'retail_inflow': 800},
        ]

        df = pd.DataFrame(stocks)
        df['net_inflow'] = df['main_inflow'] + df['retail_inflow']
        df['flow_ratio'] = df['main_inflow'] / (abs(df['main_inflow']) + abs(df['retail_inflow']) + 1)

        return df

    def analyze_capital_flow(self, capital_flow_df):
        """分析资金流向"""
        print("\n📈 资金流向分析")
        print("=" * 60)

        if capital_flow_df.empty:
            print("❌ 资金流向数据为空")
            return None

        # 计算资金流向指标
        analysis_results = []

        for _, row in capital_flow_df.iterrows():
            stock_code = row['code']
            stock_name = row['name']
            main_inflow = row['main_inflow']
            retail_inflow = row['retail_inflow']
            net_inflow = row.get('net_inflow', main_inflow + retail_inflow)
            flow_ratio = row.get('flow_ratio', 0)

            # 判断主力资金动向
            if main_inflow > self.params['min_capital_inflow']:
                flow_signal = "📈 主力大幅流入"
                signal_strength = "强"
                action = "关注买入"
            elif main_inflow > 0:
                flow_signal = "📊 主力小幅流入"
                signal_strength = "中"
                action = "观察"
            elif main_inflow < -self.params['min_capital_inflow']:
                flow_signal = "📉 主力大幅流出"
                signal_strength = "强"
                action = "警惕卖出"
            else:
                flow_signal = "📊 主力小幅流出"
                signal_strength = "弱"
                action = "持有"

            # 计算资金集中度
            if abs(main_inflow) > abs(retail_inflow) * 2:
                concentration = "高度集中"
            elif abs(main_inflow) > abs(retail_inflow):
                concentration = "中度集中"
            else:
                concentration = "分散"

            analysis_results.append({
                'code': stock_code,
                'name': stock_name,
                'main_inflow': main_inflow,
                'retail_inflow': retail_inflow,
                'net_inflow': net_inflow,
                'flow_ratio': flow_ratio,
                'flow_signal': flow_signal,
                'signal_strength': signal_strength,
                'action': action,
                'concentration': concentration
            })

        return pd.DataFrame(analysis_results)

    def generate_trading_signals(self, analysis_df):
        """生成交易信号"""
        print("\n🎯 生成交易信号")
        print("=" * 60)

        if analysis_df is None or analysis_df.empty:
            print("❌ 无分析数据，无法生成信号")
            return None

        signals = []

        for _, row in analysis_df.iterrows():
            stock_code = row['code']
            stock_name = row['name']
            flow_signal = row['flow_signal']
            signal_strength = row['signal_strength']
            action = row['action']

            # 根据资金流向生成具体交易信号
            if "大幅流入" in flow_signal and signal_strength == "强":
                signal_type = "BUY"
                signal_score = 85
                reason = "主力资金大幅流入，机构看好"
                position = "建议仓位: 10-15%"

            elif "小幅流入" in flow_signal:
                signal_type = "HOLD"
                signal_score = 60
                reason = "主力资金小幅流入，继续观察"
                position = "建议仓位: 5-10%"

            elif "大幅流出" in flow_signal and signal_strength == "强":
                signal_type = "SELL"
                signal_score = 80
                reason = "主力资金大幅流出，风险较高"
                position = "建议减仓或清仓"

            elif "小幅流出" in flow_signal:
                signal_type = "HOLD"
                signal_score = 40
                reason = "主力资金小幅流出，谨慎持有"
                position = "建议仓位: 0-5%"

            else:
                signal_type = "HOLD"
                signal_score = 50
                reason = "资金流向不明，保持观望"
                position = "建议仓位: 0%"

            signals.append({
                'code': stock_code,
                'name': stock_name,
                'signal_type': signal_type,
                'signal_score': signal_score,
                'reason': reason,
                'position': position,
                'flow_signal': flow_signal,
                'main_inflow': row['main_inflow'],
                'concentration': row['concentration']
            })

        # 按信号分数排序
        signals_df = pd.DataFrame(signals)
        signals_df = signals_df.sort_values('signal_score', ascending=False)

        return signals_df

    def generate_analysis_report(self, analysis_df, signals_df):
        """生成分析报告"""
        print("\n📋 资金流向分析报告")
        print("=" * 60)

        report = {
            'strategy_name': self.strategy_name,
            'analysis_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'total_stocks': len(analysis_df) if analysis_df is not None else 0,
            'buy_signals': 0,
            'sell_signals': 0,
            'hold_signals': 0,
            'details': []
        }

        if signals_df is not None and not signals_df.empty:
            report['buy_signals'] = len(signals_df[signals_df['signal_type'] == 'BUY'])
            report['sell_signals'] = len(signals_df[signals_df['signal_type'] == 'SELL'])
            report['hold_signals'] = len(signals_df[signals_df['signal_type'] == 'HOLD'])

            print(f"📊 信号统计:")
            print(f"  买入信号: {report['buy_signals']} 只")
            print(f"  卖出信号: {report['sell_signals']} 只")
            print(f"  持有信号: {report['hold_signals']} 只")

            print(f"\n🎯 重点推荐:")
            top_signals = signals_df.head(3)
            for idx, (_, row) in enumerate(top_signals.iterrows(), 1):
                print(f"  {idx}. {row['code']} {row['name']}")
                print(f"     信号: {row['signal_type']} (分数: {row['signal_score']})")
                print(f"     理由: {row['reason']}")
                print(f"     仓位: {row['position']}")
                print(f"     资金: {row['flow_signal']}")

        # 保存详细结果
        if signals_df is not None:
            report_file = f"reports/capital_flow_analysis_{datetime.now().strftime('%Y%m%d')}.csv"
            signals_df.to_csv(report_file, index=False, encoding='utf-8-sig')
            print(f"\n💾 详细报告已保存: {report_file}")

        return report

    def run_strategy(self):
        """运行策略"""
        print(f"\n🚀 开始运行 {self.strategy_name}")
        print("=" * 60)

        try:
            # 1. 获取资金流向数据
            capital_flow_df = self.fetch_capital_flow_data()

            # 2. 分析资金流向
            analysis_df = self.analyze_capital_flow(capital_flow_df)

            # 3. 生成交易信号
            signals_df = self.generate_trading_signals(analysis_df)

            # 4. 生成报告
            report = self.generate_analysis_report(analysis_df, signals_df)

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


def main():
    """主函数"""
    strategy = CapitalFlowStrategy()
    result = strategy.run_strategy()

    if result['success']:
        print("\n🎉 主力资金流向策略执行成功！")
        print("=" * 60)

        # 显示关键信号
        signals = result.get('signals')
        if signals is not None and not signals.empty:
            print("\n📊 交易信号汇总:")
            print("-" * 40)
            for _, row in signals.iterrows():
                emoji = "🟢" if row['signal_type'] == 'BUY' else "🔴" if row['signal_type'] == 'SELL' else "🟡"
                print(f"{emoji} {row['code']} {row['name']:10} | {row['signal_type']:4} | 分数: {row['signal_score']:3} | {row['reason'][:30]}...")

        report = result.get('report', {})
        print(f"\n📈 策略表现:")
        print(f"  分析股票: {report.get('total_stocks', 0)} 只")
        print(f"  买入建议: {report.get('buy_signals', 0)} 只")
        print(f"  卖出建议: {report.get('sell_signals', 0)} 只")

        print("\n💡 使用建议:")
        print("  1. 结合其他策略信号综合判断")
        print("  2. 关注连续多日资金流向")
        print("  3. 注意大盘整体资金面情况")
        print("  4. 严格风险控制，设置止损")

    else:
        print(f"\n❌ 策略执行失败: {result.get('error', '未知错误')}")

    return 0 if result['success'] else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
