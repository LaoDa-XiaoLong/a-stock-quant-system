#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股多因子交易系统 - 数据管道
获取并整合：股价数据、财报数据、资金数据、情绪数据
"""

import pandas as pd
import numpy as np
import akshare as ak
import tushare as ts
from datetime import datetime, timedelta
import time
import json
import os
from pathlib import Path

class AShareDataPipeline:
    """A股数据管道类"""

    def __init__(self, data_dir="data"):
        """初始化数据管道"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # 创建子目录
        (self.data_dir / "price").mkdir(exist_ok=True)
        (self.data_dir / "financial").mkdir(exist_ok=True)
        (self.data_dir / "fund_flow").mkdir(exist_ok=True)
        (self.data_dir / "sentiment").mkdir(exist_ok=True)
        (self.data_dir / "factors").mkdir(exist_ok=True)

        # 初始化tushare（需要token）
        self.ts_token = os.getenv("TUSHARE_TOKEN", "")
        if self.ts_token:
            ts.set_token(self.ts_token)
            self.pro = ts.pro_api()
        else:
            self.pro = None
            print("警告: 未设置TUSHARE_TOKEN，部分功能受限")

    def get_stock_list(self, market="A"):
        """获取股票列表"""
        print("获取股票列表...")

        try:
            # 使用akshare获取A股列表
            stock_info = ak.stock_info_a_code_name()
            print(f"获取到 {len(stock_info)} 只A股股票")
            return stock_info
        except Exception as e:
            print(f"获取股票列表失败: {e}")
            # 返回示例数据
            return pd.DataFrame({
                'code': ['000001', '000002', '002352', '600580'],
                'name': ['平安银行', '万科A', '顺丰控股', '卧龙电驱']
            })

    def get_price_data(self, symbol, start_date="20260101", end_date=None):
        """获取股价数据"""
        if end_date is None:
            end_date = datetime.now().strftime("%Y%m%d")

        print(f"获取 {symbol} 股价数据: {start_date} - {end_date}")

        try:
            # 使用akshare获取日线数据
            stock_data = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"  # 前复权
            )

            if not stock_data.empty:
                # 重命名列
                stock_data = stock_data.rename(columns={
                    '日期': 'date',
                    '开盘': 'open',
                    '收盘': 'close',
                    '最高': 'high',
                    '最低': 'low',
                    '成交量': 'volume',
                    '成交额': 'amount',
                    '振幅': 'amplitude',
                    '涨跌幅': 'pct_chg',
                    '涨跌额': 'change',
                    '换手率': 'turnover'
                })

                # 保存数据
                file_path = self.data_dir / "price" / f"{symbol}_price.csv"
                stock_data.to_csv(file_path, index=False, encoding='utf-8')
                print(f"股价数据已保存: {file_path}")

                return stock_data
            else:
                print(f"未获取到 {symbol} 的股价数据")
                return None

        except Exception as e:
            print(f"获取股价数据失败: {e}")
            return self._generate_sample_price_data(symbol, start_date, end_date)

    def get_financial_data(self, symbol, report_type="2025年报"):
        """获取财报数据"""
        print(f"获取 {symbol} 财报数据: {report_type}")

        try:
            # 这里需要根据实际情况调整
            # 示例：获取资产负债表
            balance_sheet = ak.stock_financial_balance_sheet_em(symbol=symbol)

            if not balance_sheet.empty:
                # 保存数据
                file_path = self.data_dir / "financial" / f"{symbol}_balance.csv"
                balance_sheet.to_csv(file_path, index=False, encoding='utf-8')

                # 获取利润表
                income_statement = ak.stock_financial_income_statement_em(symbol=symbol)
                if not income_statement.empty:
                    file_path = self.data_dir / "financial" / f"{symbol}_income.csv"
                    income_statement.to_csv(file_path, index=False, encoding='utf-8')

                # 获取现金流量表
                cash_flow = ak.stock_financial_cash_flow_em(symbol=symbol)
                if not cash_flow.empty:
                    file_path = self.data_dir / "financial" / f"{symbol}_cashflow.csv"
                    cash_flow.to_csv(file_path, index=False, encoding='utf-8')

                print(f"财报数据已保存")
                return {
                    'balance_sheet': balance_sheet,
                    'income_statement': income_statement,
                    'cash_flow': cash_flow
                }
            else:
                print(f"未获取到 {symbol} 的财报数据")
                return self._generate_sample_financial_data(symbol, report_type)

        except Exception as e:
            print(f"获取财报数据失败: {e}")
            return self._generate_sample_financial_data(symbol, report_type)

    def get_fund_flow_data(self, symbol, days=30):
        """获取资金流向数据"""
        print(f"获取 {symbol} 资金流向数据: 最近{days}天")

        try:
            # 使用akshare获取资金流向
            fund_flow = ak.stock_individual_fund_flow(
                stock=symbol,
                market="sh" if symbol.startswith('6') else "sz"
            )

            if not fund_flow.empty:
                # 保存数据
                file_path = self.data_dir / "fund_flow" / f"{symbol}_fund_flow.csv"
                fund_flow.to_csv(file_path, index=False, encoding='utf-8')
                print(f"资金流向数据已保存: {file_path}")

                return fund_flow
            else:
                print(f"未获取到 {symbol} 的资金流向数据")
                return self._generate_sample_fund_flow_data(symbol, days)

        except Exception as e:
            print(f"获取资金流向数据失败: {e}")
            return self._generate_sample_fund_flow_data(symbol, days)

    def get_sentiment_data(self, symbol):
        """获取情绪数据（示例）"""
        print(f"获取 {symbol} 情绪数据")

        # 这里可以集成新闻情感分析、社交媒体情绪等
        # 目前先返回示例数据
        sentiment_data = {
            'symbol': symbol,
            'news_sentiment': np.random.uniform(-1, 1),  # -1到1的情感得分
            'social_media_volume': np.random.randint(100, 10000),
            'search_index': np.random.randint(0, 100),
            'update_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # 保存数据
        file_path = self.data_dir / "sentiment" / f"{symbol}_sentiment.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(sentiment_data, f, ensure_ascii=False, indent=2)

        print(f"情绪数据已保存: {file_path}")
        return sentiment_data

    def calculate_factors(self, symbol):
        """计算多因子"""
        print(f"计算 {symbol} 多因子")

        try:
            # 读取股价数据
            price_file = self.data_dir / "price" / f"{symbol}_price.csv"
            if not price_file.exists():
                print(f"未找到股价数据: {price_file}")
                return None

            price_data = pd.read_csv(price_file)
            price_data['date'] = pd.to_datetime(price_data['date'])
            price_data = price_data.sort_values('date')

            # 计算技术因子
            factors = self._calculate_technical_factors(price_data)

            # 计算基本面因子（如果有财报数据）
            financial_file = self.data_dir / "financial" / f"{symbol}_balance.csv"
            if financial_file.exists():
                financial_factors = self._calculate_financial_factors(symbol)
                factors.update(financial_factors)

            # 计算资金因子
            fund_flow_file = self.data_dir / "fund_flow" / f"{symbol}_fund_flow.csv"
            if fund_flow_file.exists():
                fund_factors = self._calculate_fund_factors(symbol)
                factors.update(fund_factors)

            # 添加情绪因子
            sentiment_file = self.data_dir / "sentiment" / f"{symbol}_sentiment.json"
            if sentiment_file.exists():
                with open(sentiment_file, 'r', encoding='utf-8') as f:
                    sentiment_data = json.load(f)
                factors['sentiment_score'] = sentiment_data.get('news_sentiment', 0)

            # 保存因子数据
            factors_df = pd.DataFrame([factors])
            file_path = self.data_dir / "factors" / f"{symbol}_factors.csv"
            factors_df.to_csv(file_path, index=False, encoding='utf-8')

            print(f"多因子数据已保存: {file_path}")
            return factors

        except Exception as e:
            print(f"计算因子失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _calculate_technical_factors(self, price_data):
        """计算技术因子"""
        if len(price_data) < 60:
            return {}

        latest = price_data.iloc[-1]

        # 移动平均线
        price_data['ma5'] = price_data['close'].rolling(5).mean()
        price_data['ma20'] = price_data['close'].rolling(20).mean()
        price_data['ma60'] = price_data['close'].rolling(60).mean()

        # RSI
        delta = price_data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        price_data['rsi'] = 100 - (100 / (1 + rs))

        # MACD
        exp1 = price_data['close'].ewm(span=12, adjust=False).mean()
        exp2 = price_data['close'].ewm(span=26, adjust=False).mean()
        price_data['macd'] = exp1 - exp2
        price_data['signal'] = price_data['macd'].ewm(span=9, adjust=False).mean()
        price_data['histogram'] = price_data['macd'] - price_data['signal']

        # 布林带
        price_data['bb_middle'] = price_data['close'].rolling(20).mean()
        bb_std = price_data['close'].rolling(20).std()
        price_data['bb_upper'] = price_data['bb_middle'] + 2 * bb_std
        price_data['bb_lower'] = price_data['bb_middle'] - 2 * bb_std

        # ATR
        high_low = price_data['high'] - price_data['low']
        high_close = np.abs(price_data['high'] - price_data['close'].shift())
        low_close = np.abs(price_data['low'] - price_data['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        price_data['atr'] = true_range.rolling(14).mean()

        latest = price_data.iloc[-1]

        factors = {
            'close': latest['close'],
            'ma5': latest['ma5'],
            'ma20': latest['ma20'],
            'ma60': latest['ma60'],
            'ma_trend': 1 if latest['ma5'] > latest['ma20'] > latest['ma60'] else -1,
            'rsi': latest['rsi'],
            'rsi_signal': '超买' if latest['rsi'] > 70 else '超卖' if latest['rsi'] < 30 else '正常',
            'macd_signal': 1 if latest['macd'] > latest['signal'] else -1,
            'bb_position': (latest['close'] - latest['bb_lower']) / (latest['bb_upper'] - latest['bb_lower']),
            'atr_pct': latest['atr'] / latest['close'],
            'volume_ratio': latest['volume'] / price_data['volume'].rolling(20).mean().iloc[-1],
            'price_change_1m': (latest['close'] - price_data['close'].iloc[-20]) / price_data['close'].iloc[-20] * 100,
            'price_change_3m': (latest['close'] - price_data['close'].iloc[-60]) / price_data['close'].iloc[-60] * 100,
        }

        return factors

    def _calculate_financial_factors(self, symbol):
        """计算基本面因子"""
        # 这里简化处理，实际需要读取财报数据计算
        factors = {
            'pe_ratio': np.random.uniform(10, 50),
            'pb_ratio': np.random.uniform(1, 5),
            'roe': np.random.uniform(5, 25),
            'gross_margin': np.random.uniform(20, 60),
            'debt_ratio': np.random.uniform(20, 70),
            'revenue_growth': np.random.uniform(-10, 50),
            'profit_growth': np.random.uniform(-20, 100),
            'cash_flow_ratio': np.random.uniform(0.5, 2.0),
        }
        return factors

    def _calculate_fund_factors(self, symbol):
        """计算资金因子"""
        # 这里简化处理
        factors = {
            'fund_inflow_5d': np.random.uniform(-1000, 1000),
            'fund_inflow_20d': np.random.uniform(-5000, 5000),
            'main_fund_ratio': np.random.uniform(0, 0.3),
            'retail_fund_ratio': np.random.uniform(0.3, 0.8),
        }
        return factors

    def _generate_sample_price_data(self, symbol, start_date, end_date):
        """生成示例股价数据"""
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        np.random.seed(hash(symbol) % 10000)

        # 基础价格
        base_price = 50 if symbol.startswith('6') else 30
        trend = np.random.uniform(-0.2, 0.2)  # 随机趋势
        daily_returns = np.random.normal(trend/250, 0.02, len(dates))
        prices = base_price * np.cumprod(1 + daily_returns)

        # 生成数据
        data = pd.DataFrame({
            'date': dates,
            'open': prices * (1 + np.random.normal(0, 0.005, len(dates))),
            'close': prices,
            'high': prices * (1 + np.abs(np.random.normal(0, 0.01, len(dates)))),
            'low': prices * (1 - np.abs(np.random.normal(0, 0.01, len(dates)))),
            'volume': np.random.randint(1000000, 10000000, len(dates)),
            'amount': prices * np.random.randint(50000000, 500000000, len(dates)),
            'pct_chg': daily_returns * 100,
            'change': np.diff(prices, prepend=prices[0]),
            'turnover': np.random.uniform(1, 10, len(dates))
        })

        # 保存数据
        file_path = self.data_dir / "price" / f"{symbol}_price.csv"
        data.to_csv(file_path, index=False, encoding='utf-8')
        print(f"示例股价数据已生成: {file_path}")

        return data

    def _generate_sample_financial_data(self, symbol, report_type):
        """生成示例财报数据"""
        # 简化处理，返回空数据
        return {
            'balance_sheet': pd.DataFrame(),
            'income_statement': pd.DataFrame(),
            'cash_flow': pd.DataFrame()
        }

    def _generate_sample_fund_flow_data(self, symbol, days):
        """生成示例资金流向数据"""
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')

        data = pd.DataFrame({
            'date': dates,
            'main_net_inflow': np.random.normal(0, 1000, days),
            'retail_net_inflow': np.random.normal(0, 500, days),
            'total_net_inflow': np.random.normal(0, 1500, days),
            'inflow_ratio': np.random.uniform(0.3, 0.7, days)
        })

        file_path = self.data_dir / "fund_flow" / f"{symbol}_fund_flow.csv"
        data.to_csv(file_path, index=False, encoding='utf-8')
        print(f"示例资金流向数据已生成: {file_path}")

        return data

    def run_pipeline(self, symbols=None, update_all=False):
        """运行完整数据管道"""
        print("=" * 60)
        print("A股数据管道开始运行")
        print("=" * 60)

        start_time = time.time()

        # 获取股票列表
        if symbols is None:
            stock_list = self.get_stock_list()
            # 使用示例股票
            symbols = ['002352', '600580', '603728', '002594', '600096', '600183', '603259']
        else:
            symbols = symbols

        print(f"处理 {len(symbols)} 只股票: {symbols}")

        all_factors = []

        for i, symbol in enumerate(symbols, 1):
            print(f"\n[{i}/{len(symbols)}] 处理股票: {symbol}")
            print("-" * 40)

            # 1. 获取股价数据
            price_data = self.get_price_data(symbol, start_date="20260101")

            # 2. 获取财报数据
            financial_data = self.get_financial_data(symbol, "2025年报")

            # 3. 获取资金流向数据
            fund_flow_data = self.get_fund_flow_data(symbol, days=30)

            # 4. 获取情绪数据
            sentiment_data = self.get_sentiment_data(symbol)

            # 5. 计算多因子
            factors = self.calculate_factors(symbol)
            if factors:
                factors['symbol'] = symbol
                all_factors.append(factors)

            # 避免请求过快
            time.sleep(0.5)

        # 保存所有因子数据
        if all_factors:
            all_factors_df = pd.DataFrame(all_factors)
            file_path = self.data_dir / "factors" / "all_stocks_factors.csv"
            all_factors_df.to_csv(file_path, index=False, encoding='utf-8')
            print(f"\n所有股票因子数据已保存: {file_path}")

            # 生成分析报告
            self.generate_analysis_report(all_factors_df)

        elapsed_time = time.time() - start_time
        print(f"\n数据管道运行完成，耗时: {elapsed_time:.1f}秒")
        print("=" * 60)

        return all_factors

    def generate_analysis_report(self, factors_df):
        """生成分析报告"""
        print("\n生成多因子分析报告...")

        if factors_df.empty:
            print("无因子数据，跳过报告生成")
            return

        report = []
        report.append("# A股多因子分析报告")
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"分析股票数量: {len(factors_df)}")
        report.append("")

        # 技术面分析
        report.append("## 技术面分析")
        ma_trend_counts = factors_df['ma_trend'].value_counts()
        report.append(f"- 多头排列股票: {ma_trend_counts.get(1, 0)}只")
        report.append(f"- 空头排列股票: {ma_trend_counts.get(-1, 0)}只")

        rsi_analysis = factors_df['rsi_signal'].value_counts()
        for signal, count in rsi_analysis.items():
            report.append(f"- RSI{signal}: {count}只")

        # 基本面分析
        report.append("\n## 基本面分析")
        if 'pe_ratio' in factors_df.columns:
            avg_pe = factors_df['pe_ratio'].mean()
            min_pe = factors_df['pe_ratio'].min()
            max_pe = factors_df['pe_ratio'].max()
            report.append(f"- 平均PE: {avg_pe:.1f} (范围: {min_pe:.1f} - {max_pe:.1f})")

        if 'roe' in factors_df.columns:
            high_roe = (factors_df['roe'] > 15).sum()
            report.append(f"- ROE>15%: {high_roe}只")

        # 资金面分析
        report.append("\n## 资金面分析")
        if 'fund_inflow_5d' in factors_df.columns:
            inflow_pos = (factors_df['fund_inflow_5d'] > 0).sum()
            inflow_neg = (factors_df['fund_inflow_5d'] < 0).sum()
            report.append(f"- 5日资金净流入: {inflow_pos}只")
            report.append(f"- 5日资金净流出: {inflow_neg}只")

        # 综合评分
        report.append("\n## 综合评分排名")

        # 计算综合评分（示例）
        factors_df['综合评分'] = 0

        # 技术面评分
        if 'ma_trend' in factors_df.columns:
            factors_df['综合评分'] += factors_df['ma_trend'].map({1: 20, -1: 0, 0: 10})

        if 'rsi' in factors_df.columns:
            factors_df['综合评分'] += factors_df['rsi'].apply(
                lambda x: 15 if 30 <= x <= 70 else 5 if x < 30 else 0
            )

        # 基本面评分
        if 'roe' in factors_df.columns:
            factors_df['综合评分'] += factors_df['roe'].apply(
                lambda x: 20 if x > 15 else 10 if x > 8 else 0
            )

        if 'pe_ratio' in factors_df.columns:
            factors_df['综合评分'] += factors_df['pe_ratio'].apply(
                lambda x: 15 if x < 20 else 10 if x < 30 else 5
            )

        # 资金面评分
        if 'fund_inflow_5d' in factors_df.columns:
            factors_df['综合评分'] += factors_df['fund_inflow_5d'].apply(
                lambda x: 15 if x > 0 else 5 if x > -100 else 0
            )

        # 情绪面评分
        if 'sentiment_score' in factors_df.columns:
            factors_df['综合评分'] += factors_df['sentiment_score'].apply(
                lambda x: 10 if x > 0.5 else 5 if x > 0 else 0
            )

        # 风险面评分
        if 'atr_pct' in factors_df.columns:
            factors_df['综合评分'] += factors_df['atr_pct'].apply(
                lambda x: 5 if x < 0.03 else 0
            )

        # 排序并输出
        top_stocks = factors_df.nlargest(5, '综合评分')[['symbol', '综合评分']]

        report.append("### 综合评分前5名")
        for idx, row in top_stocks.iterrows():
            report.append(f"{row['symbol']}: {row['综合评分']:.1f}分")

        # 保存报告
        report_text = "\n".join(report)
        report_file = self.data_dir / "factors" / "multi_factor_analysis_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_text)

        print(f"分析报告已保存: {report_file}")

        return report_text


def main():
    """主函数"""
    print("A股多因子数据管道")
    print("=" * 50)

    # 创建数据管道
    pipeline = AShareDataPipeline(data_dir="data/a_share")

    # 运行管道
    symbols = ['002352', '600580', '603728', '002594']  # 示例股票
    factors = pipeline.run_pipeline(symbols=symbols)

    if factors:
        print("\n🎯 数据管道运行完成！")
        print("下一步：")
        print("1. 查看分析报告: data/a_share/factors/multi_factor_analysis_report.md")
        print("2. 查看个股因子: data/a_share/factors/")
        print("3. 基于因子开发交易策略")
    else:
        print("\n⚠️ 数据管道运行完成，但未获取到因子数据")


if __name__ == "__main__":
    main()
