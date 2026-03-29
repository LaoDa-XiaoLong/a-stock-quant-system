#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多策略执行器
并行执行多个量化策略，对比分析结果
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')
import sys
import os

# 添加策略目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class MultiStrategyExecutor:
    """多策略执行器"""
    
    def __init__(self):
        self.executor_name = "多策略执行器 v1.0"
        self.strategies = {}
        self.results = {}
        
        print(f"🚀 {self.executor_name} 初始化完成")
    
    def register_strategy(self, strategy_name, strategy_module, strategy_class):
        """注册策略"""
        try:
            module = __import__(strategy_module)
            strategy_class_obj = getattr(module, strategy_class)
            self.strategies[strategy_name] = {
                'module': strategy_module,
                'class': strategy_class,
                'instance': None
            }
            print(f"✅ 注册策略: {strategy_name}")
            return True
        except Exception as e:
            print(f"❌ 注册策略失败 {strategy_name}: {e}")
            return False
    
    def load_holdings(self):
        """加载持仓数据"""
        try:
            holdings_file = "data/holdings/holding_stocks.csv"
            if os.path.exists(holdings_file):
                df = pd.read_csv(holdings_file)
                print(f"📊 加载持仓股票: {len(df)} 只")
                return df
            else:
                print("⚠️  持仓文件不存在，使用模拟数据")
                return self._generate_mock_holdings()
        except Exception as e:
            print(f"❌ 加载持仓数据失败: {e}")
            return self._generate_mock_holdings()
    
    def _generate_mock_holdings(self):
        """生成模拟持仓数据"""
        return pd.DataFrame({
            'code': ['002594', '603728', '600580', '600183', '603259', '002352', '600096'],
            'name': ['比亚迪', '鸣志电器', '卧龙电驱', '生益科技', '药明康德', '顺丰控股', '云天化'],
            'cost_price': [99.0, 68.0, 42.0, 66.0, 101.0, 40.0, 37.0]
        })
    
    def execute_strategy(self, strategy_name, holdings_df):
        """执行单个策略"""
        print(f"\n🎯 执行策略: {strategy_name}")
        print("-" * 40)
        
        if strategy_name not in self.strategies:
            print(f"❌ 策略未注册: {strategy_name}")
            return None
        
        try:
            strategy_info = self.strategies[strategy_name]
            module = __import__(strategy_info['module'])
            strategy_class = getattr(module, strategy_info['class'])
            
            # 创建策略实例
            strategy_instance = strategy_class()
            self.strategies[strategy_name]['instance'] = strategy_instance
            
            # 执行策略
            if strategy_name == "主力资金流向策略":
                result = strategy_instance.run_strategy()
            elif strategy_name == "题材热度识别策略":
                result = strategy_instance.run_strategy(holdings_df)
            else:
                # 通用执行方法
                if hasattr(strategy_instance, 'run_strategy'):
                    result = strategy_instance.run_strategy()
                else:
                    print(f"❌ 策略 {strategy_name} 没有 run_strategy 方法")
                    return None
            
            self.results[strategy_name] = result
            return result
            
        except Exception as e:
            print(f"❌ 执行策略 {strategy_name} 失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def compare_strategy_results(self):
        """比较策略结果"""
        print("\n📊 策略结果对比分析")
        print("=" * 60)
        
        if not self.results:
            print("❌ 无策略执行结果")
            return None
        
        comparison_data = []
        
        for strategy_name, result in self.results.items():
            if result.get('success'):
                signals = result.get('signals')
                report = result.get('report', {})
                
                if signals is not None and not signals.empty:
                    buy_signals = len(signals[signals['signal_type'] == 'BUY'])
                    sell_signals = len(signals[signals['signal_type'] == 'SELL'])
                    hold_signals = len(signals[signals['signal_type'] == 'HOLD'])
                    
                    # 计算平均信号分数
                    avg_score = signals['signal_score'].mean() if 'signal_score' in signals.columns else 0
                    
                    comparison_data.append({
                        'strategy': strategy_name,
                        'buy_signals': buy_signals,
                        'sell_signals': sell_signals,
                        'hold_signals': hold_signals,
                        'avg_score': round(avg_score, 1),
                        'total_stocks': report.get('total_stocks', 0),
                        'status': '✅ 成功'
                    })
                else:
                    comparison_data.append({
                        'strategy': strategy_name,
                        'buy_signals': 0,
                        'sell_signals': 0,
                        'hold_signals': 0,
                        'avg_score': 0,
                        'total_stocks': 0,
                        'status': '⚠️  无信号'
                    })
            else:
                comparison_data.append({
                    'strategy': strategy_name,
                    'buy_signals': 0,
                    'sell_signals': 0,
                    'hold_signals': 0,
                    'avg_score': 0,
                    'total_stocks': 0,
                    'status': '❌ 失败'
                })
        
        # 创建对比表格
        comparison_df = pd.DataFrame(comparison_data)
        
        print("策略表现对比:")
        print("-" * 60)
        for _, row in comparison_df.iterrows():
            print(f"{row['strategy']:20} | 买入: {row['buy_signals']:2} | 卖出: {row['sell_signals']:2} | 持有: {row['hold_signals']:2} | 均分: {row['avg_score']:5.1f} | {row['status']}")
        
        return comparison_df
    
    def generate_consensus_signals(self):
        """生成共识信号（多策略投票）"""
        print("\n🤝 多策略共识信号")
        print("=" * 60)
        
        if not self.results:
            print("❌ 无策略执行结果")
            return None
        
        # 收集所有策略的信号
        all_signals = []
        
        for strategy_name, result in self.results.items():
            if result.get('success'):
                signals = result.get('signals')
                if signals is not None and not signals.empty:
                    for _, signal in signals.iterrows():
                        all_signals.append({
                            'code': signal['code'],
                            'name': signal['name'],
                            'strategy': strategy_name,
                            'signal_type': signal['signal_type'],
                            'signal_score': signal.get('signal_score', 50),
                            'reason': signal.get('reason', '')
                        })
        
        if not all_signals:
            print("❌ 无有效信号")
            return None
        
        # 转换为DataFrame
        signals_df = pd.DataFrame(all_signals)
        
        # 计算共识信号
        consensus_signals = []
        
        for (code, name), group in signals_df.groupby(['code', 'name']):
            total_strategies = len(group)
            
            # 统计信号类型
            buy_count = len(group[group['signal_type'] == 'BUY'])
            sell_count = len(group[group['signal_type'] == 'SELL'])
            hold_count = len(group[group['signal_type'] == 'HOLD'])
            
            # 计算平均分数
            avg_score = group['signal_score'].mean()
            
            # 确定共识信号（简单多数投票）
            if buy_count > sell_count and buy_count > hold_count:
                consensus_type = "BUY"
                confidence = buy_count / total_strategies
            elif sell_count > buy_count and sell_count > hold_count:
                consensus_type = "SELL"
                confidence = sell_count / total_strategies
            else:
                consensus_type = "HOLD"
                confidence = hold_count / total_strategies
            
            # 收集理由
            reasons = []
            for _, row in group.iterrows():
                reasons.append(f"{row['strategy']}: {row['reason']}")
            
            consensus_signals.append({
                'code': code,
                'name': name,
                'consensus_signal': consensus_type,
                'confidence': round(confidence * 100, 1),
                'avg_score': round(avg_score, 1),
                'strategies_count': total_strategies,
                'buy_votes': buy_count,
                'sell_votes': sell_count,
                'hold_votes': hold_count,
                'reasons': ' | '.join(reasons[:3])  # 只显示前3个理由
            })
        
        consensus_df = pd.DataFrame(consensus_signals)
        consensus_df = consensus_df.sort_values(['confidence', 'avg_score'], ascending=False)
        
        print("共识信号排名:")
        print("-" * 60)
        for idx, (_, row) in enumerate(consensus_df.head(5).iterrows(), 1):
            emoji = "🟢" if row['consensus_signal'] == 'BUY' else "🔴" if row['consensus_signal'] == 'SELL' else "🟡"
            print(f"{idx}. {emoji} {row['code']} {row['name']:10}")
            print(f"   共识: {row['consensus_signal']} | 置信度: {row['confidence']}% | 策略数: {row['strategies_count']}")
            print(f"   投票: 买入{row['buy_votes']} | 卖出{row['sell_votes']} | 持有{row['hold_votes']}")
            print(f"   理由: {row['reasons'][:80]}...")
        
        return consensus_df
    
    def generate_comprehensive_report(self, comparison_df, consensus_df):
        """生成综合报告"""
        print("\n📋 多策略综合报告")
        print("=" * 60)
        
        report = {
            'report_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'total_strategies': len(self.strategies),
            'successful_strategies': len([r for r in self.results.values() if r.get('success')]),
            'total_consensus_signals': len(consensus_df) if consensus_df is not None else 0,
            'buy_consensus': 0,
            'sell_consensus': 0,
            'hold_consensus': 0,
            'details': {}
        }
        
        if consensus_df is not None:
            report['buy_consensus'] = len(consensus_df[consensus_df['consensus_signal'] == 'BUY'])
            report['sell_consensus'] = len(consensus_df[consensus_df['consensus_signal'] == 'SELL'])
            report['hold_consensus'] = len(consensus_df[consensus_df['consensus_signal'] == 'HOLD'])
            
            print(f"📊 共识信号统计:")
            print(f"  买入共识: {report['buy_consensus']} 只")
            print(f"  卖出共识: {report['sell_consensus']} 只")
            print(f"  持有共识: {report['hold_consensus']} 只")
        
        if comparison_df is not None:
            print(f"\n📈 策略表现统计:")
            successful = comparison_df[comparison_df['status'] == '✅ 成功']
            if not successful.empty:
                best_strategy = successful.loc[successful['avg_score'].idxmax()]
                print(f"  最佳策略: {best_strategy['strategy']} (均分: {best_strategy['avg_score']})")
                
                most_buy_signals = successful.loc[successful['buy_signals'].idxmax()]
                print(f"  最多买入信号: {most_buy_signals['strategy']} ({most_buy_signals['buy_signals']}个)")
        
        # 保存报告
        report_file = f"reports/multi_strategy_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(f"# 多策略量化分析报告\n")
                f.write(f"生成时间: {report['report_date']}\n\n")
                
                f.write("## 执行概况\n")
                f.write(f"- 总策略数: {report['total_strategies']}\n")
                f.write(f"- 成功执行: {report['successful_strategies']}\n")
                f.write(f"- 共识信号: {report['total_consensus_signals']} 只股票\n\n")
                
                f.write("## 共识信号分布\n")
                f.write(f"- 买入共识: {report['buy_consensus']} 只\n")
                f.write(f"- 卖出共识: {report['sell_consensus']} 只\n")
                f.write(f"- 持有共识: {report['hold_consensus']} 只\n\n")
                
                if consensus_df is not None and not consensus_df.empty:
                    f.write("## 重点共识信号\n")
                    for _, row in consensus_df.head(10).iterrows():
                        f.write(f"### {row['code']} {row['name']}\n")
                        f.write(f"- 共识信号: **{row['consensus_signal']}** (置信度: {row['confidence']}%)\n")
                        f.write(f"- 平均分数: {row['avg_score']}\n")
                        f.write(f"- 参与策略: {row['strategies_count']} 个\n")
                        f.write(f"- 投票结果: 买入{row['buy_votes']} | 卖出{row['sell_votes']} | 持有{row['hold_votes']}\n")
                        f.write(f"- 理由摘要: {row['reasons']}\n\n")
                
                f.write("## 策略表现对比\n")
                if comparison_df is not None:
                    f.write("| 策略 | 买入信号 | 卖出信号 | 持有信号 | 平均分数 | 状态 |\n")
                    f.write("|------|----------|----------|----------|----------|------|\n")
                    for _, row in comparison_df.iterrows():
                        f.write(f"| {row['strategy']} | {row['buy_signals']} | {row['sell_signals']} | {row['hold_signals']} | {row['avg_score']} | {row['status']} |\n")
                
                f.write("\n## 使用建议\n")
                f.write("1. **高置信度共识信号优先**：置信度>70%的共识信号可靠性较高\n")
                f.write("2. **多策略验证**：单个策略信号需其他策略验证\n")
                f.write("3. **风险控制**：即使共识买入也需设置止损\n")
                f.write("4. **动态调整**：根据市场环境调整策略权重\n")
                f.write("5. **持续监控**：定期评估策略表现，及时优化\n")
            
            print(f"\n💾 综合报告已保存: {report_file}")
            
        except Exception as e:
            print(f"❌ 保存报告失败: {e}")
        
        return report
    
    def run_all_strategies(self):
        """运行所有策略"""
        print(f"\n🚀 开始执行多策略量化分析")
        print("=" * 60)
        
        # 加载持仓数据
        holdings_df = self.load_holdings()
        
        # 注册策略
        print("\n📋 注册策略:")
        self.register_strategy("主力资金流向策略", "strategies.capital_flow_strategy_v1", "CapitalFlowStrategy")
        self.register_strategy("题材热度识别策略", "strategies.theme_hot_strategy_v1", "ThemeHotStrategy")
        
        # 执行所有策略
        print(f"\n🎯 执行 {len(self.strategies)} 个策略:")
        for strategy_name in self.strategies.keys():
            self.execute_strategy(strategy_name, holdings_df)
        
        # 对比分析
        comparison_df = self.compare_strategy_results()
        
        # 生成共识信号
        consensus_df = self.generate_consensus_signals()
        
        # 生成综合报告
        report = self.generate_comprehensive_report(comparison_df, consensus_df)
        
        print(f"\n✅ 多策略分析执行完成")
        return {
            'success': True,
            'comparison': comparison_df,
            'consensus': consensus_df,
            'report': report
        }


def main():
    """主函数"""
    executor = MultiStrategyExecutor()
    result = executor.run_all_strategies()
    
    if result['success']:
        print("\n🎉 多策略量化分析成功完成！")
        print("=" * 60)
        
        consensus_df = result.get('consensus')
        if consensus_df is not None and not consensus_df.empty:
            print("\n📊 最终交易建议（基于多策略共识）:")
            print("-" * 50)
            
            # 只显示高置信度的共识信号
            high_confidence = consensus_df[consensus_df['confidence'] >= 70]
            
            if not high_confidence.empty:
                print("🚀 高置信度交易机会（置信度≥70%）:")
                for _, row in high_confidence.iterrows():
                    action = "🟢 强烈建议买入" if row['consensus_signal'] == 'BUY' else "🔴 强烈建议卖出"
                    print(f"  {