#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股多因子交易策略
基于五维分析框架：基本面 + 技术面 + 资金面 + 情绪面 + 风险面
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import backtrader as bt
import backtrader.analyzers as btanalyzers
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

class MultiFactorStrategy(bt.Strategy):
    """多因子交易策略"""

    params = (
        ('factor_weights', {
            'fundamental': 0.30,    # 基本面权重
            'technical': 0.25,      # 技术面权重
            'fund_flow': 0.20,      # 资金面权重
            'sentiment': 0.15,      # 情绪面权重
            'risk': 0.10,          # 风险面权重
        }),
        ('position_size', 0.1),     # 单只股票仓位
        ('stop_loss', 0.08),        # 止损比例
        ('take_profit', 0.20),      # 止盈比例
        ('rebalance_days', 20),     # 调仓周期
    )

    def __init__(self):
        """初始化策略"""
        # 记录交易日
        self.day_count = 0

        # 持仓股票
        self.positions = {}

        # 因子数据（这里使用模拟数据，实际应从数据库读取）
        self.factor_data = self._load_factor_data()

        # 技术指标
        for data in self.datas:
            # 移动平均线
            data.sma5 = bt.indicators.SimpleMovingAverage(data.close, period=5)
            data.sma20 = bt.indicators.SimpleMovingAverage(data.close, period=20)
            data.sma60 = bt.indicators.SimpleMovingAverage(data.close, period=60)

            # RSI
            data.rsi = bt.indicators.RSI(data.close, period=14)

            # MACD
            data.macd = bt.indicators.MACD(data.close)

            # ATR
            data.atr = bt.indicators.ATR(data, period=14)

    def _load_factor_data(self):
        """加载因子数据（示例）"""
        # 这里应该从数据库或文件加载实时因子数据
        # 目前使用模拟数据

        symbols = ['002352', '600580', '603728', '002594']
        factor_data = {}

        for symbol in symbols:
            factor_data[symbol] = {
                'fundamental': {
                    'pe_ratio': np.random.uniform(10, 50),
                    'pb_ratio': np.random.uniform(1, 5),
                    'roe': np.random.uniform(5, 25),
                    'revenue_growth': np.random.uniform(-10, 50),
                    'profit_growth': np.random.uniform(-20, 100),
                    'cash_flow_ratio': np.random.uniform(0.5, 2.0),
                },
                'technical': {
                    'ma_trend': np.random.choice([-1, 0, 1]),
                    'rsi': np.random.uniform(20, 80),
                    'macd_signal': np.random.choice([-1, 1]),
                    'volume_ratio': np.random.uniform(0.5, 2.0),
                },
                'fund_flow': {
                    'fund_inflow_5d': np.random.uniform(-1000, 1000),
                    'main_fund_ratio': np.random.uniform(0, 0.3),
                },
                'sentiment': {
                    'news_sentiment': np.random.uniform(-1, 1),
                    'search_index': np.random.randint(0, 100),
                },
                'risk': {
                    'atr_pct': np.random.uniform(0.01, 0.05),
                    'beta': np.random.uniform(0.8, 1.2),
                }
            }

        return factor_data

    def calculate_factor_score(self, symbol):
        """计算股票的综合因子得分"""
        if symbol not in self.factor_data:
            return 0

        factors = self.factor_data[symbol]
        weights = self.params.factor_weights

        # 基本面得分
        fundamental_score = 0
        fund_factors = factors['fundamental']
        if fund_factors['pe_ratio'] < 20:
            fundamental_score += 20
        elif fund_factors['pe_ratio'] < 30:
            fundamental_score += 10

        if fund_factors['roe'] > 15:
            fundamental_score += 20
        elif fund_factors['roe'] > 8:
            fundamental_score += 10

        if fund_factors['revenue_growth'] > 20:
            fundamental_score += 15
        elif fund_factors['revenue_growth'] > 0:
            fundamental_score += 5

        if fund_factors['profit_growth'] > 30:
            fundamental_score += 15
        elif fund_factors['profit_growth'] > 0:
            fundamental_score += 5

        if fund_factors['cash_flow_ratio'] > 1.0:
            fundamental_score += 10

        fundamental_score = min(fundamental_score, 100) * weights['fundamental']

        # 技术面得分
        technical_score = 0
        tech_factors = factors['technical']

        # 获取当前数据的技术指标
        data = self.getdatabyname(symbol)
        if data:
            # 均线趋势
            if data.sma5[0] > data.sma20[0] > data.sma60[0]:
                technical_score += 30
            elif data.sma5[0] < data.sma20[0] < data.sma60[0]:
                technical_score += 0
            else:
                technical_score += 15

            # RSI
            if 30 <= data.rsi[0] <= 70:
                technical_score += 20
            elif data.rsi[0] < 30:  # 超卖
                technical_score += 25
            else:  # 超买
                technical_score += 10

            # MACD
            if data.macd.macd[0] > data.macd.signal[0]:
                technical_score += 20
            else:
                technical_score += 5

            # 成交量
            if tech_factors['volume_ratio'] > 1.2:
                technical_score += 15
            elif tech_factors['volume_ratio'] > 0.8:
                technical_score += 10
            else:
                technical_score += 5

        technical_score = min(technical_score, 100) * weights['technical']

        # 资金面得分
        fund_score = 0
        flow_factors = factors['fund_flow']

        if flow_factors['fund_inflow_5d'] > 0:
            fund_score += 40

        if flow_factors['main_fund_ratio'] > 0.1:
            fund_score += 30

        fund_score = min(fund_score, 100) * weights['fund_flow']

        # 情绪面得分
        sentiment_score = 0
        sent_factors = factors['sentiment']

        if sent_factors['news_sentiment'] > 0.5:
            sentiment_score += 40
        elif sent_factors['news_sentiment'] > 0:
            sentiment_score += 20

        if sent_factors['search_index'] > 50:
            sentiment_score += 30
        elif sent_factors['search_index'] > 20:
            sentiment_score += 15

        sentiment_score = min(sentiment_score, 100) * weights['sentiment']

        # 风险面得分
        risk_score = 0
        risk_factors = factors['risk']

        if risk_factors['atr_pct'] < 0.03:
            risk_score += 50

        if 0.9 <= risk_factors['beta'] <= 1.1:
            risk_score += 30

        risk_score = min(risk_score, 100) * weights['risk']

        # 综合得分
        total_score = (
            fundamental_score +
            technical_score +
            fund_score +
            sentiment_score +
            risk_score
        )

        return total_score

    def next(self):
        """每个交易日执行"""
        self.day_count += 1

        # 调仓日执行
        if self.day_count % self.params.rebalance_days == 0:
            self.rebalance_portfolio()

        # 每日检查止损止盈
        self.check_stop_loss_take_profit()

    def rebalance_portfolio(self):
        """调仓：卖出低分股票，买入高分股票"""
        print(f"\n[{self.datetime.date()}] 执行调仓")

        # 计算所有股票得分
        scores = {}
        for data in self.datas:
            symbol = data._name
            score = self.calculate_factor_score(symbol)
            scores[symbol] = score
            print(f"  {symbol}: {score:.1f}分")

        # 按得分排序
        sorted_stocks = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # 选择前N只股票
        top_n = min(3, len(sorted_stocks))
        target_stocks = [symbol for symbol, score in sorted_stocks[:top_n]]

        print(f"  目标持仓: {target_stocks}")

        # 调整持仓
        for data in self.datas:
            symbol = data._name
            position = self.getposition(data)

            if symbol in target_stocks:
                # 应该持有
                if not position:
                    # 买入
                    size = self.calculate_position_size(data)
                    self.buy(data=data, size=size)
                    print(f"  买入 {symbol}: {size}股")
                else:
                    # 已持有，检查是否需要加仓
                    current_size = position.size
                    target_size = self.calculate_position_size(data)
                    if target_size > current_size:
                        add_size = target_size - current_size
                        self.buy(data=data, size=add_size)
                        print(f"  加仓 {symbol}: {add_size}股")
            else:
                # 不应该持有
                if position:
                    # 卖出
                    self.sell(data=data, size=position.size)
                    print(f"  卖出 {symbol}: {position.size}股")

    def calculate_position_size(self, data):
        """计算仓位大小"""
        # 基于波动率调整仓位
        atr = data.atr[0]
        close_price = data.close[0]

        if atr > 0 and close_price > 0:
            # 风险调整的仓位
            risk_per_share = atr * 2  # 2倍ATR作为风险度量
            risk_capital = self.broker.getvalue() * self.params.position_size
            position_size = int(risk_capital / risk_per_share)

            # 确保不超过可用资金
            max_by_cash = int(self.broker.getcash() / close_price)
            position_size = min(position_size, max_by_cash)

            return max(0, position_size)

        return 0

    def check_stop_loss_take_profit(self):
        """检查止损止盈"""
        for data in self.datas:
            position = self.getposition(data)
            if position:
                symbol = data._name
                entry_price = position.price
                current_price = data.close[0]

                # 计算盈亏比例
                pnl_pct = (current_price - entry_price) / entry_price

                # 止损
                if pnl_pct < -self.params.stop_loss:
                    print(f"[{self.datetime.date()}] 止损 {symbol}: {pnl_pct:.1%}")
                    self.sell(data=data, size=position.size)

                # 止盈
                elif pnl_pct > self.params.take_profit:
                    print(f"[{self.datetime.date()}] 止盈 {symbol}: {pnl_pct:.1%}")
                    self.sell(data=data, size=position.size)

    def notify_order(self, order):
        """订单通知"""
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                action = '买入'
            else:
                action = '卖出'

            print(f"[{self.datetime.date()}] {action} {order.data._name}: "
                  f"{order.executed.size}股 @ {order.executed.price:.2f}")

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            print(f"[{self.datetime.date()}] 订单取消/拒绝: {order.data._name}")


def run_backtest():
    """运行回测"""
    print("A股多因子策略回测")
    print("=" * 50)

    # 创建回测引擎
    cerebro = bt.Cerebro()

    # 设置初始资金
    cerebro.broker.setcash(1000000.0)

    # 设置佣金
    cerebro.broker.setcommission(commission=0.001)  # 0.1%佣金

    # 添加策略
    cerebro.addstrategy(MultiFactorStrategy)

    # 添加分析器
    cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(btanalyzers.Returns, _name='returns')
    cerebro.addanalyzer(btanalyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(btanalyzers.TradeAnalyzer, _name='trades')

    # 加载数据（这里使用示例数据）
    # 实际应该从数据库或文件加载真实数据
    symbols = ['002352', '600580', '603728', '002594']

    for symbol in symbols:
        # 生成示例数据
        dates = pd.date_range('2026-01-01', '2026-03-28', freq='D')
        np.random.seed(hash(symbol) % 10000)

        # 生成价格数据
        base_price = 50
        returns = np.random.normal(0.0005, 0.02, len(dates))
        prices = base_price * np.cumprod(1 + returns)

        # 创建DataFrame
        df = pd.DataFrame({
            'open': prices * (1 + np.random.normal(0, 0.005, len(dates))),
            'high': prices * (1 + np.abs(np.random.normal(0, 0.01, len(dates)))),
            'low': prices * (1 - np.abs(np.random.normal(0, 0.01, len(dates)))),
            'close': prices,
            'volume': np.random.randint(1000000, 10000000, len(dates))
        }, index=dates)

        # 转换为backtrader数据格式
        data = bt.feeds.PandasData(
            dataname=df,
            name=symbol
        )
        cerebro.adddata(data)

    print(f"回测期间: 2026-01-01 至 2026-03-28")
    print(f"初始资金: {cerebro.broker.getvalue():,.0f}元")
    print(f"股票数量: {len(symbols)}")
    print()

    # 运行回测
    print("开始回测...")
    results = cerebro.run()
    strategy = results[0]

    # 输出结果
    print("\n" + "=" * 50)
    print("回测结果")
    print("=" * 50)

    # 最终资金
    final_value = cerebro.broker.getvalue()
    initial_cash = 1000000.0
    total_return = (final_value - initial_cash) / initial_cash * 100

    print(f"初始资金: {initial_cash:,.0f}元")
    print(f"最终资金: {final_value:,.0f}元")
    print(f"总收益率: {total_return:.2f}%")

    # 分析器结果
    analysis = strategy.analyzers

    # 夏普比率
    sharpe = analysis.sharpe.get_analysis()
    if 'sharperatio' in sharpe:
        print(f"夏普比率: {sharpe['sharperatio']:.3f}")

    # 年化收益率
    returns_analysis = analysis.returns.get_analysis()
    if 'rnorm100' in returns_analysis:
        print(f"年化收益率: {returns_analysis['rnorm100']:.2f}%")

    # 最大回撤
    drawdown = analysis.drawdown.get_analysis()
    if 'max' in drawdown:
        print(f"最大回撤: {drawdown['max'].drawdown:.2f}%")
        print(f"最长回撤期: {drawdown['max'].len}天")

    # 交易统计
    trades = analysis.trades.get_analysis()
    if 'total' in trades:
        print(f"总交易次数: {trades['total']['total']}")
        if trades['total']['total'] > 0:
            print(f"胜率: {trades['won']['total'] / trades['total']['total'] * 100:.1f}%")
            print(f"平均盈利: {trades['won']['pnl']['average']:.2f}")
            print(f"平均亏损: {trades['lost']['pnl']['average']:.2f}")
            print(f"盈亏比: {abs(trades['won']['pnl']['average'] / trades['lost']['pnl']['average']):.2f}")

    print("\n策略参数:")
    print(f"  基本面权重: {strategy.params.factor_weights['fundamental']}")
    print(f"  技术面权重: {strategy.params.factor_weights['technical']}")
    print(f"  资金面权重: {strategy.params.factor_weights['fund_flow']}")
    print(f"  情绪面权重: {strategy.params.factor_weights['sentiment']}")
    print(f"  风险面权重: {strategy.params.factor_weights['risk']}")
    print(f"  单股仓位: {strategy.params.position_size*100:.0f}%")
    print(f"  止损比例: {strategy.params.stop_loss*100:.0f}%")
    print(f"  止盈比例: {strategy.params.take_profit*100:.0f}%")
    print(f"  调仓周期: {strategy.params.rebalance_days}天")

    # 绘制图表
    print("\n生成图表...")
    try:
        cerebro.plot(style='candlestick', volume=False)
    except:
        print("图表生成失败（可能缺少图形界面）")

    return strategy


def optimize_parameters():
    """参数优化"""
    print("多因子策略参数优化")
    print("=" * 50)

    # 这里可以添加参数优化逻辑
    # 例如：网格搜索不同权重组合

    print("参数优化功能待实现")
    print("建议手动调整权重进行测试")


if __name__ == "__main__":
    # 运行回测
    strategy = run_backtest()

    print("\n" + "=" * 50)
    print("下一步行动:")
    print("1. 调整因子权重优化策略")
    print("2. 使用真实数据测试")
    print("3. 增加更多因子维度")
    print("4. 优化风险控制参数")
    print("=" * 50)
