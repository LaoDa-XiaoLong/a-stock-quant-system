#!/usr/bin/env python3
"""
基础数据分析脚本
对获取的A股数据进行基础分析
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

# 设置中文字体和样式（修复乱码问题）
import matplotlib
matplotlib.rcParams['font.sans-serif'] = [
    'Arial Unicode MS', 'PingFang SC', 'Heiti SC', 
    'Hiragino Sans GB', 'STHeiti', 'SimHei', 
    'Microsoft YaHei', 'DejaVu Sans'
]
matplotlib.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")

def load_stock_data(symbol='000001'):
    """加载股票数据"""
    # 查找最新的数据文件
    data_files = [f for f in os.listdir('data/raw') if f.startswith(f'stock_{symbol}_')]
    if not data_files:
        print(f"未找到股票 {symbol} 的数据文件")
        return None
    
    # 使用最新的数据文件
    latest_file = sorted(data_files)[-1]
    filepath = os.path.join('data/raw', latest_file)
    
    print(f"加载数据文件: {latest_file}")
    df = pd.read_csv(filepath)
    
    # 数据清洗和转换
    if '日期' in df.columns:
        df['date'] = pd.to_datetime(df['日期'])
    elif 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    
    # 确保必要的列存在
    required_cols = ['开盘', '收盘', '最高', '最低', '成交量']
    for col in required_cols:
        if col not in df.columns:
            # 尝试其他可能的列名
            if 'open' in df.columns:
                df['开盘'] = df['open']
            if 'close' in df.columns:
                df['收盘'] = df['close']
            if 'high' in df.columns:
                df['最高'] = df['high']
            if 'low' in df.columns:
                df['最低'] = df['low']
            if 'volume' in df.columns:
                df['成交量'] = df['volume']
    
    # 按日期排序
    df = df.sort_values('date')
    
    return df

def calculate_technical_indicators(df):
    """计算技术指标"""
    print("计算技术指标...")
    
    # 确保数据按日期排序
    df = df.sort_values('date')
    
    # 简单移动平均线
    df['SMA_5'] = df['收盘'].rolling(window=5).mean()
    df['SMA_10'] = df['收盘'].rolling(window=10).mean()
    df['SMA_20'] = df['收盘'].rolling(window=20).mean()
    
    # 指数移动平均线
    df['EMA_12'] = df['收盘'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['收盘'].ewm(span=26, adjust=False).mean()
    
    # MACD
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_hist'] = df['MACD'] - df['MACD_signal']
    
    # RSI (相对强弱指数)
    delta = df['收盘'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # 布林带
    df['BB_middle'] = df['收盘'].rolling(window=20).mean()
    bb_std = df['收盘'].rolling(window=20).std()
    df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
    df['BB_lower'] = df['BB_middle'] - (bb_std * 2)
    
    # 成交量移动平均
    df['Volume_MA_5'] = df['成交量'].rolling(window=5).mean()
    df['Volume_MA_10'] = df['成交量'].rolling(window=10).mean()
    
    return df

def plot_price_chart(df, symbol='000001'):
    """绘制价格图表"""
    fig, axes = plt.subplots(3, 1, figsize=(14, 12), gridspec_kw={'height_ratios': [3, 1, 1]})
    
    # 价格和移动平均线
    ax1 = axes[0]
    ax1.plot(df['date'], df['收盘'], label='收盘价', color='blue', alpha=0.7, linewidth=1)
    ax1.plot(df['date'], df['SMA_5'], label='5日移动平均', color='orange', alpha=0.7, linewidth=1)
    ax1.plot(df['date'], df['SMA_20'], label='20日移动平均', color='red', alpha=0.7, linewidth=1)
    ax1.fill_between(df['date'], df['BB_lower'], df['BB_upper'], alpha=0.1, color='gray', label='布林带')
    ax1.set_title(f'股票 {symbol} 价格走势', fontsize=14, fontweight='bold')
    ax1.set_ylabel('价格 (元)')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # 成交量
    ax2 = axes[1]
    ax2.bar(df['date'], df['成交量'], color='green', alpha=0.5, label='成交量')
    ax2.plot(df['date'], df['Volume_MA_5'], color='red', linewidth=1, label='5日成交量均线')
    ax2.set_ylabel('成交量')
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)
    
    # MACD
    ax3 = axes[2]
    ax3.plot(df['date'], df['MACD'], label='MACD', color='blue', linewidth=1)
    ax3.plot(df['date'], df['MACD_signal'], label='信号线', color='red', linewidth=1)
    ax3.bar(df['date'], df['MACD_hist'], label='MACD柱', color='gray', alpha=0.5)
    ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax3.set_xlabel('日期')
    ax3.set_ylabel('MACD')
    ax3.legend(loc='upper left')
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 保存图表
    if not os.path.exists('reports'):
        os.makedirs('reports')
    
    chart_file = f'reports/price_chart_{symbol}.png'
    plt.savefig(chart_file, dpi=300, bbox_inches='tight')
    print(f"价格图表已保存到 {chart_file}")
    
    plt.show()

def calculate_returns(df):
    """计算收益率"""
    print("\n收益率分析:")
    
    # 日收益率
    df['daily_return'] = df['收盘'].pct_change()
    
    # 累计收益率
    df['cumulative_return'] = (1 + df['daily_return']).cumprod() - 1
    
    # 统计信息
    total_return = df['cumulative_return'].iloc[-1] if not df['cumulative_return'].isna().all() else 0
    avg_daily_return = df['daily_return'].mean()
    daily_std = df['daily_return'].std()
    
    print(f"总收益率: {total_return:.2%}")
    print(f"平均日收益率: {avg_daily_return:.4%}")
    print(f"日收益率标准差: {daily_std:.4%}")
    
    # 夏普比率（假设无风险利率为0）
    sharpe_ratio = (avg_daily_return / daily_std) * np.sqrt(252) if daily_std != 0 else 0
    print(f"年化夏普比率: {sharpe_ratio:.4f}")
    
    return df

def generate_summary_report(df, symbol='000001'):
    """生成摘要报告"""
    print("\n" + "="*50)
    print(f"股票 {symbol} 分析报告")
    print("="*50)
    
    # 基本信息
    print(f"数据期间: {df['date'].min().date()} 到 {df['date'].max().date()}")
    print(f"数据条数: {len(df)}")
    
    # 价格统计
    print(f"\n价格统计:")
    print(f"  最高价: {df['最高'].max():.2f}")
    print(f"  最低价: {df['最低'].min():.2f}")
    print(f"  平均收盘价: {df['收盘'].mean():.2f}")
    
    # 成交量统计
    print(f"\n成交量统计:")
    print(f"  平均成交量: {df['成交量'].mean():,.0f}")
    print(f"  最大成交量: {df['成交量'].max():,.0f}")
    print(f"  最小成交量: {df['成交量'].min():,.0f}")
    
    # 技术指标当前值
    if not df.empty:
        latest = df.iloc[-1]
        print(f"\n最新技术指标:")
        print(f"  RSI: {latest['RSI']:.2f}")
        print(f"  MACD: {latest['MACD']:.4f}")
        print(f"  收盘价 vs 布林带: {latest['收盘']:.2f} (上轨: {latest['BB_upper']:.2f}, 下轨: {latest['BB_lower']:.2f})")
        
        # 交易信号
        if latest['RSI'] < 30:
            print("  RSI信号: 超卖 (可能买入机会)")
        elif latest['RSI'] > 70:
            print("  RSI信号: 超买 (可能卖出机会)")
        else:
            print("  RSI信号: 中性")
            
        if latest['MACD'] > latest['MACD_signal']:
            print("  MACD信号: 金叉 (看涨)")
        else:
            print("  MACD信号: 死叉 (看跌)")

def main():
    """主函数"""
    print("=" * 50)
    print("A股基础数据分析工具")
    print("=" * 50)
    
    # 示例股票代码
    symbol = '000001'  # 平安银行
    
    # 加载数据
    df = load_stock_data(symbol)
    if df is None:
        print("数据加载失败，请先运行数据获取脚本")
        return
    
    # 计算技术指标
    df = calculate_technical_indicators(df)
    
    # 计算收益率
    df = calculate_returns(df)
    
    # 生成报告
    generate_summary_report(df, symbol)
    
    # 绘制图表
    plot_price_chart(df, symbol)
    
    # 保存处理后的数据
    if not os.path.exists('data/processed'):
        os.makedirs('data/processed')
    
    processed_file = f'data/processed/stock_{symbol}_processed.csv'
    df.to_csv(processed_file, index=False, encoding='utf-8-sig')
    print(f"\n处理后的数据已保存到 {processed_file}")

if __name__ == "__main__":
    main()