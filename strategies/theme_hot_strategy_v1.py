#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
题材热度识别策略 v1.0
识别A股热点题材，捕捉板块轮动机会
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class ThemeHotStrategy:
    """题材热度识别策略"""

    def __init__(self):
        self.strategy_name = "题材热度识别策略 v1.0"
        self.strategy_version = "1.0"
        self.author = "量化小助理"
        self.created_date = "2026-03-29"

        # 策略参数
        self.params = {
            'hot_keywords': [
                '人工智能', 'AI', '芯片', '半导体', '新能源汽车', '锂电池',
                '光伏', '储能', '医药', '创新药', '消费电子', '5G',
                '数字经济', '信创', '军工', '航天', '国企改革', '一带一路'
            ],
            'min_news_count': 5,           # 最小新闻数量
            'hot_threshold': 0.7,          # 热度阈值
            'momentum_days': 5,            # 动量计算天数
            'volume_increase_ratio': 1.3,  # 成交量增加比率
        }

        print(f"🚀 {self.strategy_name} 初始化完成")
        print(f"📊 监控关键词: {', '.join(self.params['hot_keywords'][:5])}...")

    def fetch_theme_data(self):
        """获取题材热度数据"""
        print("📡 获取题材热度数据")

        try:
            # 这里模拟获取题材热度数据
            # 实际实现需要接入财经新闻API、社交媒体数据等

            # 模拟热门题材数据
            hot_themes = self._generate_mock_theme_data()
            return hot_themes

        except Exception as e:
            print(f"❌ 获取题材数据失败: {e}")
            print("⚠️  使用模拟数据进行策略演示")
            return self._generate_mock_theme_data()

    def _generate_mock_theme_data(self):
        """生成模拟题材热度数据（演示用）"""
        print("📊 生成模拟题材热度数据（演示）")

        # 当前热门题材
        themes = [
            {
                'theme': '人工智能',
                'hot_score': 85,
                'news_count': 25,
                'discussion_count': 1200,
                'related_stocks': ['002230', '002415', '300496'],
                'momentum': 1.2,
                'volume_ratio': 1.8,
                'description': 'AI大模型应用加速，政策支持力度加大'
            },
            {
                'theme': '新能源汽车',
                'hot_score': 78,
                'news_count': 18,
                'discussion_count': 950,
                'related_stocks': ['002594', '300750', '002460'],
                'momentum': 1.1,
                'volume_ratio': 1.5,
                'description': '销量持续增长，产业链景气度提升'
            },
            {
                'theme': '医药',
                'hot_score': 72,
                'news_count': 15,
                'discussion_count': 800,
                'related_stocks': ['603259', '600276', '000538'],
                'momentum': 0.9,
                'volume_ratio': 1.3,
                'description': '创新药研发进展，医保政策优化'
            },
            {
                'theme': '芯片半导体',
                'hot_score': 68,
                'news_count': 12,
                'discussion_count': 700,
                'related_stocks': ['603986', '002049', '300661'],
                'momentum': 0.8,
                'volume_ratio': 1.2,
                'description': '国产替代加速，行业周期见底'
            },
            {
                'theme': '光伏储能',
                'hot_score': 65,
                'news_count': 10,
                'discussion_count': 600,
                'related_stocks': ['300274', '002129', '601012'],
                'momentum': 0.7,
                'volume_ratio': 1.1,
                'description': '装机量超预期，成本持续下降'
            }
        ]

        return pd.DataFrame(themes)

    def analyze_theme_hotness(self, theme_df):
        """分析题材热度"""
        print("\n📈 题材热度分析")
        print("=" * 60)

        if theme_df.empty:
            print("❌ 题材数据为空")
            return None

        # 计算综合热度分数
        analysis_results = []

        for _, row in theme_df.iterrows():
            theme = row['theme']
            hot_score = row['hot_score']
            news_count = row['news_count']
            discussion_count = row['discussion_count']
            momentum = row['momentum']
            volume_ratio = row['volume_ratio']

            # 计算综合热度
            composite_score = (
                hot_score * 0.4 +
                min(news_count / 30 * 100, 100) * 0.3 +
                min(discussion_count / 1500 * 100, 100) * 0.2 +
                momentum * 10 * 0.1
            )

            # 判断热度等级
            if composite_score >= 80:
                hot_level = "🔥 极度热门"
                signal_strength = "极强"
                action = "重点关注"
            elif composite_score >= 70:
                hot_level = "📈 高度热门"
                signal_strength = "强"
                action = "积极关注"
            elif composite_score >= 60:
                hot_level = "📊 中度热门"
                signal_strength = "中"
                action = "适度关注"
            elif composite_score >= 50:
                hot_level = "📉 轻度热门"
                signal_strength = "弱"
                action = "观察"
            else:
                hot_level = "❄️  冷门"
                signal_strength = "无"
                action = "回避"

            # 判断趋势
            if momentum > 1.2 and volume_ratio > 1.5:
                trend = "🚀 加速上涨"
            elif momentum > 1.0:
                trend = "📈 稳步上涨"
            elif momentum > 0.8:
                trend = "📊 横盘震荡"
            else:
                trend = "📉 趋势转弱"

            analysis_results.append({
                'theme': theme,
                'hot_score': hot_score,
                'composite_score': round(composite_score, 1),
                'hot_level': hot_level,
                'signal_strength': signal_strength,
                'action': action,
                'trend': trend,
                'news_count': news_count,
                'discussion_count': discussion_count,
                'momentum': momentum,
                'volume_ratio': volume_ratio,
                'description': row['description'],
                'related_stocks': row['related_stocks']
            })

        return pd.DataFrame(analysis_results)

    def match_holdings_with_themes(self, holdings_df, theme_analysis_df):
        """匹配持仓股票与热门题材"""
        print("\n🎯 持仓股票题材匹配")
        print("=" * 60)

        if holdings_df.empty or theme_analysis_df.empty:
            print("❌ 持仓或题材数据为空")
            return None

        matches = []

        # 简单的关键词匹配（实际应该更复杂）
        theme_keywords = {
            '新能源汽车': ['汽车', '新能源', '电池', '电动'],
            '人工智能': ['智能', 'AI', '算法', '模型'],
            '医药': ['医药', '医疗', '生物', '制药'],
            '芯片半导体': ['芯片', '半导体', '集成电路'],
            '光伏储能': ['光伏', '太阳能', '储能', '新能源']
        }

        for _, holding in holdings_df.iterrows():
            stock_code = holding['code']
            stock_name = holding['name']

            matched_themes = []

            for _, theme_row in theme_analysis_df.iterrows():
                theme = theme_row['theme']
                related_stocks = theme_row['related_stocks']

                # 检查是否在相关股票列表中
                if stock_code in related_stocks:
                    matched_themes.append({
                        'theme': theme,
                        'hot_level': theme_row['hot_level'],
                        'composite_score': theme_row['composite_score'],
                        'trend': theme_row['trend']
                    })
                # 或者通过名称关键词匹配
                elif theme in theme_keywords:
                    keywords = theme_keywords[theme]
                    if any(keyword in stock_name for keyword in keywords):
                        matched_themes.append({
                            'theme': theme,
                            'hot_level': theme_row['hot_level'],
                            'composite_score': theme_row['composite_score'],
                            'trend': theme_row['trend']
                        })

            if matched_themes:
                # 按热度排序
                matched_themes.sort(key=lambda x: x['composite_score'], reverse=True)
                best_theme = matched_themes[0]

                matches.append({
                    'code': stock_code,
                    'name': stock_name,
                    'matched_theme': best_theme['theme'],
                    'theme_hot_level': best_theme['hot_level'],
                    'theme_score': best_theme['composite_score'],
                    'theme_trend': best_theme['trend'],
                    'all_matched_themes': [t['theme'] for t in matched_themes]
                })

        return pd.DataFrame(matches)

    def generate_trading_signals(self, theme_matches_df):
        """生成交易信号"""
        print("\n🎯 生成题材交易信号")
        print("=" * 60)

        if theme_matches_df is None or theme_matches_df.empty:
            print("❌ 无题材匹配数据，无法生成信号")
            return None

        signals = []

        for _, row in theme_matches_df.iterrows():
            stock_code = row['code']
            stock_name = row['name']
            theme = row['matched_theme']
            theme_score = row['theme_score']
            hot_level = row['theme_hot_level']
            trend = row['theme_trend']

            # 根据题材热度生成交易信号
            if theme_score >= 80:
                signal_type = "BUY"
                signal_score = 90
                reason = f"涉及极度热门题材: {theme}，{hot_level}"
                position = "建议仓位: 10-15%"

            elif theme_score >= 70:
                signal_type = "BUY"
                signal_score = 75
                reason = f"涉及高度热门题材: {theme}，{hot_level}"
                position = "建议仓位: 8-12%"

            elif theme_score >= 60:
                signal_type = "HOLD"
                signal_score = 65
                reason = f"涉及中度热门题材: {theme}，{hot_level}"
                position = "建议仓位: 5-8%"

            elif theme_score >= 50:
                signal_type = "HOLD"
                signal_score = 55
                reason = f"涉及轻度热门题材: {theme}，{hot_level}"
                position = "建议仓位: 3-5%"

            else:
                signal_type = "HOLD"
                signal_score = 45
                reason = f"涉及冷门题材: {theme}"
                position = "建议仓位: 0-3%"

            # 考虑趋势因素
            if "加速上涨" in trend and signal_type == "BUY":
                signal_score += 5
                reason += "，趋势加速上涨"
            elif "趋势转弱" in trend:
                signal_score -= 10
                reason += "，但趋势转弱需谨慎"

            signals.append({
                'code': stock_code,
                'name': stock_name,
                'signal_type': signal_type,
                'signal_score': signal_score,
                'reason': reason,
                'position': position,
                'matched_theme': theme,
                'theme_score': theme_score,
                'hot_level': hot_level,
                'trend': trend,
                'all_themes': row['all_matched_themes']
            })

        # 按信号分数排序
        signals_df = pd.DataFrame(signals)
        signals_df = signals_df.sort_values('signal_score', ascending=False)

        return signals_df

    def generate_analysis_report(self, theme_analysis_df, theme_matches_df, signals_df):
        """生成分析报告"""
        print("\n📋 题材热度分析报告")
        print("=" * 60)

        report = {
            'strategy_name': self.strategy_name,
            'analysis_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'total_themes': len(theme_analysis_df) if theme_analysis_df is not None else 0,
            'hot_themes': 0,
            'matched_stocks': len(theme_matches_df) if theme_matches_df is not None else 0,
            'buy_signals': 0,
            'hold_signals': 0,
            'theme_details': []
        }

        if theme_analysis_df is not None:
            report['hot_themes'] = len(theme_analysis_df[theme_analysis_df['composite_score'] >= 70])

            print(f"📊 题材热度统计:")
            print(f"  监控题材: {report['total_themes']} 个")
            print(f"  热门题材: {report['hot_themes']} 个")
            print(f"  匹配股票: {report['matched_stocks']} 只")

            print(f"\n🔥 热门题材排名:")
            top_themes = theme_analysis_df.sort_values('composite_score', ascending=False).head(3)
            for idx, (_, row) in enumerate(top_themes.iterrows(), 1):
                print(f"  {idx}. {row['theme']}: {row['hot_level']} (分数: {row['composite_score']})")
                print(f"     描述: {row['description']}")
                print(f"     趋势: {row['trend']}")

        if signals_df is not None and not signals_df.empty:
            report['buy_signals'] = len(signals_df[signals_df['signal_type'] == 'BUY'])
            report['hold_signals'] = len(signals_df[signals_df['signal_type'] == 'HOLD'])

            print(f"\n🎯 题材交易信号:")
            top_signals = signals_df.head(3)
            for idx, (_, row) in enumerate(top_signals.iterrows(), 1):
                print(f"  {idx}. {row['code']} {row['name']}")
                print(f"     题材: {row['matched_theme']} ({row['hot_level']})")
                print(f"     信号: {row['signal_type']} (分数: {row['signal_score']})")
                print(f"     理由: {row['reason']}")

        # 保存详细结果
        if signals_df is not None:
            report_file = f"reports/theme_hot_analysis_{datetime.now().strftime('%Y%m%d')}.csv"
            signals_df.to_csv(report_file, index=False, encoding='utf-8-sig')
            print(f"\n💾 详细报告已保存: {report_file}")

        return report

    def run_strategy(self, holdings_df):
        """运行策略"""
        print(f"\n🚀 开始运行 {self.strategy_name}")
        print("=" * 60)

        try:
            # 1. 获取题材热度数据
            theme_df = self.fetch_theme_data()

            # 2. 分析题材热度
            theme_analysis_df = self.analyze_theme_hotness(theme_df)

            # 3. 匹配持仓股票与题材
            theme_matches_df = self.match_holdings_with_themes(holdings_df, theme_analysis_df)

            # 4. 生成交易信号
            signals_df = self.generate_trading_signals(theme_matches_df)

            # 5. 生成报告
            report = self.generate_analysis_report(theme_analysis_df, theme_matches_df, signals_df)

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


def load_holdings():
    """加载持仓数据"""
    try:
        holdings_file = "data/holdings/holding_stocks.csv"
        df = pd.read_csv(holdings_file)
        print(f"📊 加载持仓股票: {len(df)} 只")
        return df
    except Exception as e:
        print(f"❌ 加载持仓数据失败: {e}")
        # 返回模拟持仓数据
        return pd.DataFrame({
            'code': ['002594', '603728', '600580', '600183', '603259', '002352', '600096'],
            'name': ['比亚迪', '鸣志电器', '卧龙电驱', '生益科技', '药明康德', '顺丰控股', '云天化']
        })


def main():
    """主函数"""
    # 加载持仓数据
    holdings_df = load_holdings()

    strategy = ThemeHotStrategy()
    result = strategy.run_strategy(holdings_df)

    if result['success']:
        print("\n🎉 题材热度识别策略执行成功！")
        print("=" * 60)

        # 显示关键信号
        signals = result.get('signals')
        if signals is not None and not signals.empty:
            print("\n📊 题材交易信号汇总:")
            print("-" * 40)
            for _, row in signals.iterrows():
                emoji = "🟢"
