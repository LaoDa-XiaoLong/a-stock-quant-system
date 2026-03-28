#!/usr/bin/env python3
"""
简单的MACD策略
基于MACD指标的交易策略
"""

import backtrader as bt
import pandas as pd
import numpy as np
from datetime import datetime
import os

class MACDStrategy(bt.Strategy):
    """MACD交易策略"""
    
    params = (
        ('macd1', 12),   # MACD快速EMA周期
        ('macd2', 26),   # MACD慢速EMA周期
        ('macdsig', 9),  # MACD信号线周期
        ('printlog', True),
    )
    
    def __init__(self):
        """初始化策略"""
        # 保存订单引用
        self.order = None
        self.buyprice = None
        self.buycomm = None
        
        # 添加MACD指标
        self.macd = bt.indicators.MACD(
            self.data.close,
            period_me1=self.params.macd1,
            period_me2=self.params.macd2,
            period_signal=self.params.macdsig
        )
        
        # 交叉信号
        self.macd_cross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
        
        # 跟踪交易统计
        self.trades = []
        self.trade_count = 0
        
    def log(self, txt, dt=None, doprint=False):
        """日志函数"""
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()} {txt}')
    
    def notify_order(self, order):
        """订单状态通知"""
        if order.status in [order.Submitted, order.Accepted]:
            # 订单已提交/接受 - 无需操作
            return
        
        # 检查订单是否完成
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f'买入执行, 价格: {order.executed.price:.2f}, '
                    f'成本: {order.executed.value:.2f}, '
                    f'佣金: {order.executed.comm:.2f}'
                )
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log(
                    f'卖出执行, 价格: {order.executed.price:.2f}, '
                    f'成本: {order.executed.value:.2f}, '
                    f'佣金: {order.executed.comm:.2f}'
                )
            
            self.bar_executed = len(self)
            
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单取消/保证金不足/拒绝')
        
        # 重置订单
        self.order = None
    
    def notify_trade(self, trade):
        """交易通知"""
        if not trade.isclosed:
            return
        
        try:
            entry_date = trade.dtopen.date() if hasattr(trade.dtopen, 'date') else trade.dtopen
            exit_date = trade.dtclose.date() if hasattr(trade.dtclose, 'date') else trade.dtclose
            
            self.trades.append({
                'entry_date': entry_date,
                'exit_date': exit_date,
                'entry_price': trade.price,
                'exit_price': trade.price + trade.pnl / trade.size if trade.size != 0 else trade.price,
                'size': trade.size,
                'pnl': trade.pnl,
                'pnl_percent': trade.pnl / trade.value * 100 if trade.value != 0 else 0,
                'commission': trade.commission
            })
        except Exception as e:
            print(f"记录交易时出错: {e}")
        
        self.trade_count += 1
        self.log(f'交易利润, 毛利润: {trade.pnl:.2f}, 净利润: {trade.pnlcomm:.2f}')
    
    def next(self):
        """下一个数据点"""
        # 检查是否有未完成的订单
        if self.order:
            return
        
        # 检查是否持有头寸
        if not self.position:
            # 没有头寸，寻找买入信号
            if self.macd_cross > 0:  # MACD上穿信号线，买入信号
                self.log(f'买入信号: MACD={self.macd.macd[0]:.4f}, Signal={self.macd.signal[0]:.4f}')
                
                # 计算买入数量（使用95%的资金）
                size = int(self.broker.getcash() * 0.95 / self.data.close[0])
                if size > 0:
                    self.log(f'创建买入订单, 数量: {size}')
                    self.order = self.buy(size=size)
        
        else:
            # 持有头寸，寻找卖出信号
            if self.macd_cross < 0:  # MACD下穿信号线，卖出信号
                self.log(f'卖出信号: MACD={self.macd.macd[0]:.4f}, Signal={self.macd.signal[0]:.4f}')
                self.order = self.sell(size=self.position.size)
    
    def stop(self):
        """策略结束"""
        self.log(f'策略结束，总交易次数: {self.trade_count}')
        self.log(f'期末资产: {self.broker.getvalue():.2f}')

def prepare_data_for_backtrader(csv_file):
    """准备Backtrader数据"""
    # 读取CSV文件
    df = pd.read_csv(csv_file)
    
    # 确保日期列正确
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    elif '日期' in df.columns:
        df['date'] = pd.to_datetime(df['日期'])
        df.rename(columns={'日期': 'date'}, inplace=True)
    
    # 重命名列以匹配Backtrader的期望
    column_mapping = {
        '开盘': 'open',
        '收盘': 'close', 
        '最高': 'high',
        '最低': 'low',
        '成交量': 'volume'
    }
    
    for chinese, english in column_mapping.items():
        if chinese in df.columns:
            df[english] = df[chinese]
    
    # 设置日期索引
    df.set_index('date', inplace=True)
    
    # 确保所有必要列都存在
    required_cols = ['open', 'high', 'low', 'close', 'volume']
    for col in required_cols:
        if col not in df.columns:
            print(f"警告: 缺少列 {col}")
    
    # 排序并返回
    df = df.sort_index()
    return df

def run_backtest(data_file, initial_cash=100000.0, commission=0.001):
    """运行回测"""
    print("=" * 50)
    print("MACD策略回测")
    print("=" * 50)
    
    # 创建Cerebro引擎
    cerebro = bt.Cerebro()
    
    # 设置初始资金
    cerebro.broker.setcash(initial_cash)
    
    # 设置佣金
    cerebro.broker.setcommission(commission=commission)
    
    # 添加策略
    cerebro.addstrategy(MACDStrategy)
    
    # 准备数据
    df = prepare_data_for_backtrader(data_file)
    
    # 创建数据源
    data = bt.feeds.PandasData(
        dataname=df,
        datetime=None,  # 使用索引作为日期时间
        open='open',
        high='high',
        low='low',
        close='close',
        volume='volume',
        openinterest=None
    )
    
    # 添加数据
    cerebro.adddata(data)
    
    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', riskfreerate=0.0)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    
    # 运行回测
    print(f'初始资金: {cerebro.broker.getvalue():.2f}')
    results = cerebro.run()
    print(f'期末资金: {cerebro.broker.getvalue():.2f}')
    
    # 获取策略实例
    strat = results[0]
    
    # 打印分析结果
    print("\n" + "=" * 50)
    print("回测结果分析")
    print("=" * 50)
    
    # 收益率
    returns_analysis = strat.analyzers.returns.get_analysis()
    if 'rtot' in returns_analysis:
        print(f"总收益率: {returns_analysis['rtot']:.2%}")
    if 'rnorm100' in returns_analysis:
        print(f"年化收益率: {returns_analysis['rnorm100']:.2f}%")
    
    # 夏普比率
    sharpe_analysis = strat.analyzers.sharpe.get_analysis()
    if 'sharperatio' in sharpe_analysis:
        print(f"夏普比率: {sharpe_analysis['sharperatio']:.4f}")
    
    # 最大回撤
    drawdown_analysis = strat.analyzers.drawdown.get_analysis()
    if 'max' in drawdown_analysis:
        print(f"最大回撤: {drawdown_analysis['max'].drawdown:.2%}")
        print(f"最大回撤期间: {drawdown_analysis['max'].len}")
    
    # 交易分析
    trade_analysis = strat.analyzers.trades.get_analysis()
    if 'total' in trade_analysis:
        print(f"\n交易统计:")
        print(f"  总交易次数: {trade_analysis['total']['total']}")
        print(f"  盈利交易次数: {trade_analysis['won']['total']}")
        print(f"  亏损交易次数: {trade_analysis['lost']['total']}")
        
        if trade_analysis['total']['total'] > 0:
            win_rate = trade_analysis['won']['total'] / trade_analysis['total']['total']
            print(f"  胜率: {win_rate:.2%}")
            
            if 'pnl' in trade_analysis and 'net' in trade_analysis['pnl']:
                print(f"  总净利润: {trade_analysis['pnl']['net']['total']:.2f}")
                print(f"  平均盈利: {trade_analysis['won']['pnl']['average']:.2f}")
                print(f"  平均亏损: {trade_analysis['lost']['pnl']['average']:.2f}")
    
    # 保存交易记录
    if hasattr(strat, 'trades') and strat.trades:
        trades_df = pd.DataFrame(strat.trades)
        trades_file = 'reports/trade_records.csv'
        trades_df.to_csv(trades_file, index=False, encoding='utf-8-sig')
        print(f"\n交易记录已保存到 {trades_file}")
    
    return cerebro, strat

def main():
    """主函数"""
    # 检查数据文件
    data_file = 'data/processed/stock_000001_processed.csv'
    
    if not os.path.exists(data_file):
        print(f"数据文件不存在: {data_file}")
        print("请先运行数据获取和分析脚本")
        return
    
    # 确保报告目录存在
    if not os.path.exists('reports'):
        os.makedirs('reports')
    
    # 运行回测
    cerebro, strat = run_backtest(data_file)
    
    # 绘制图表
    try:
        # 创建图表
        fig = cerebro.plot(style='candlestick', volume=True, iplot=False)[0][0]
        
        # 保存图表
        chart_file = 'reports/backtest_chart.png'
        fig.savefig(chart_file, dpi=300, bbox_inches='tight')
        print(f"\n回测图表已保存到 {chart_file}")
    except Exception as e:
        print(f"绘制图表时出错: {e}")

if __name__ == "__main__":
    main()