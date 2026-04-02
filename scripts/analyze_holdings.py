#!/usr/bin/env python3
"""
持仓股票分析脚本
分析老大的持仓股票，提供交易策略建议
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体 - 使用优化配置
import matplotlib
# 读取项目matplotlibrc文件
try:
    with open('matplotlibrc', 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                if 'font.sans-serif' in line:
                    fonts = line.split(':')[1].strip()
                    font_list = [f.strip().strip("'\"") for f in fonts.split(',')]
                    matplotlib.rcParams['font.sans-serif'] = font_list
                elif 'axes.unicode_minus' in line:
                    value = line.split(':')[1].strip()
                    matplotlib.rcParams['axes.unicode_minus'] = value.lower() == 'true'
except:
    # 默认字体设置
    matplotlib.rcParams['font.sans-serif'] = [
        'Arial Unicode MS', 'PingFang SC', 'Heiti SC',
        'Hiragino Sans GB', 'STHeiti', 'SimHei',
        'Microsoft YaHei', 'DejaVu Sans'
    ]
    matplotlib.rcParams['axes.unicode_minus'] = False

sns.set_style("whitegrid")

def load_holding_stocks():
    """加载持仓股票信息"""
    holdings_path = 'data/holdings/holding_stocks.csv'
    if not os.path.exists(holdings_path):
        print("持仓信息文件不存在")
        return None

    holdings_df = pd.read_csv(holdings_path)
    print(f"加载 {len(holdings_df)} 只持仓股票")
    return holdings_df

def load_stock_data(symbol):
    """加载股票数据"""
    # 查找数据文件
    data_files = [f for f in os.listdir('data/raw') if f.startswith(f'stock_{symbol}_') and f.endswith('.csv')]

    if not data_files:
        print(f"未找到股票 {symbol} 的数据文件")
        return None

    # 使用最新的数据文件
    latest_file = sorted(data_files)[-1]
    filepath = os.path.join('data/raw', latest_file)

    print(f"  加载数据: {latest_file}")
    df = pd.read_csv(filepath)

    # 数据清洗 - 先检查是否已有date列
    if 'date' not in df.columns and '日期' in df.columns:
        df['date'] = pd.to_datetime(df['日期'])
        # 不删除原列，避免重复

    # 确保列名一致 - 只添加不存在的列
    column_mapping = {
        '开盘': 'open',
        '收盘': 'close',
        '最高': 'high',
        '最低': 'low',
        '成交量': 'volume',
        '成交额': 'amount'
    }

    for chinese, english in column_mapping.items():
        if chinese in df.columns and english not in df.columns:
            df[english] = df[chinese]

    # 按日期排序 - 使用正确的列名
    if 'date' in df.columns:
        df = df.sort_values('date')
    elif '日期' in df.columns:
        df = df.sort_values('日期')

    return df

def calculate_technical_indicators(df):
    """计算技术指标"""
    # 确保数据按日期排序
    df = df.sort_values('date')

    # 移动平均线
    df['SMA_5'] = df['close'].rolling(window=5).mean()
    df['SMA_10'] = df['close'].rolling(window=10).mean()
    df['SMA_20'] = df['close'].rolling(window=20).mean()
    df['SMA_60'] = df['close'].rolling(window=60).mean()

    # 指数移动平均线
    df['EMA_12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['close'].ewm(span=26, adjust=False).mean()

    # MACD
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_hist'] = df['MACD'] - df['MACD_signal']

    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # 布林带
    df['BB_middle'] = df['close'].rolling(window=20).mean()
    bb_std = df['close'].rolling(window=20).std()
    df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
    df['BB_lower'] = df['BB_middle'] - (bb_std * 2)

    # 成交量指标
    df['Volume_MA_5'] = df['volume'].rolling(window=5).mean()
    df['Volume_MA_20'] = df['volume'].rolling(window=20).mean()

    return df

def analyze_stock_performance(df, symbol, name, cost_price):
    """分析股票表现"""
    print(f"\n分析 {symbol} {name}:")

    if df is None or df.empty:
        print("  无数据可分析")
        return None

    # 基本统计
    latest_price = df['close'].iloc[-1]
    start_price = df['close'].iloc[0]
    total_return = (latest_price - start_price) / start_price

    # 相对于成本的表现
    if cost_price > 0:
        cost_return = (latest_price - cost_price) / cost_price
        print(f"  当前价格: {latest_price:.2f}元")
        print(f"  成本价格: {cost_price:.2f}元")
        print(f"  相对于成本: {cost_return:+.2%}")
        print(f"  盈亏金额: {(latest_price - cost_price):+.2f}元/股")
    else:
        cost_return = None
        print(f"  当前价格: {latest_price:.2f}元")

    print(f"  期间收益率: {total_return:+.2%}")
    print(f"  数据期间: {df['date'].iloc[0].date()} 到 {df['date'].iloc[-1].date()}")
    print(f"  数据条数: {len(df)}")

    # 波动性分析
    daily_returns = df['close'].pct_change()
    volatility = daily_returns.std() * np.sqrt(252)  # 年化波动率
    print(f"  年化波动率: {volatility:.2%}")

    # 技术指标当前值
    latest = df.iloc[-1]
    print(f"  最新技术指标:")
    print(f"    RSI: {latest['RSI']:.1f} ({'超买' if latest['RSI'] > 70 else '超卖' if latest['RSI'] < 30 else '中性'})")
    print(f"    MACD: {latest['MACD']:.3f} ({'金叉' if latest['MACD'] > latest['MACD_signal'] else '死叉'})")
    print(f"    价格 vs 布林带: {latest['close']:.2f} (上轨: {latest['BB_upper']:.2f}, 下轨: {latest['BB_lower']:.2f})")

    # 趋势分析
    trend_short = '上涨' if latest['close'] > latest['SMA_20'] else '下跌'
    trend_long = '上涨' if latest['close'] > latest['SMA_60'] else '下跌'
    print(f"    短期趋势 ({trend_short}): 价格{latest['close']:.2f} vs 20日均线{latest['SMA_20']:.2f}")
    print(f"    长期趋势 ({trend_long}): 价格{latest['close']:.2f} vs 60日均线{latest['SMA_60']:.2f}")

    return {
        'symbol': symbol,
        'name': name,
        'current_price': latest_price,
        'cost_price': cost_price,
        'cost_return': cost_return,
        'period_return': total_return,
        'volatility': volatility,
        'rsi': latest['RSI'],
        'macd_signal': '金叉' if latest['MACD'] > latest['MACD_signal'] else '死叉',
        'trend_short': trend_short,
        'trend_long': trend_long,
        'bb_position': (latest['close'] - latest['BB_lower']) / (latest['BB_upper'] - latest['BB_lower']) if latest['BB_upper'] != latest['BB_lower'] else 0.5
    }

def generate_trading_recommendation(analysis):
    """生成交易建议"""
    if analysis is None:
        return "无数据，无法提供建议"

    recommendations = []

    # 基于成本分析
    if analysis['cost_return'] is not None:
        if analysis['cost_return'] < -0.20:  # 亏损20%以上
            recommendations.append("深度套牢，考虑是否补仓或止损")
        elif analysis['cost_return'] < -0.10:  # 亏损10-20%
            recommendations.append("中度亏损，关注支撑位")
        elif analysis['cost_return'] < 0:  # 小幅亏损
            recommendations.append("小幅亏损，持有观察")
        elif analysis['cost_return'] < 0.10:  # 盈利0-10%
            recommendations.append("小幅盈利，可考虑部分止盈")
        elif analysis['cost_return'] < 0.30:  # 盈利10-30%
            recommendations.append("良好盈利，建议设置移动止盈")
        else:  # 盈利30%以上
            recommendations.append("大幅盈利，强烈建议止盈")

    # 基于技术指标
    if analysis['rsi'] > 70:
        recommendations.append("RSI超买，短期可能有回调风险")
    elif analysis['rsi'] < 30:
        recommendations.append("RSI超卖，可能是买入机会")

    if analysis['macd_signal'] == '金叉':
        recommendations.append("MACD金叉，技术面看涨")
    else:
        recommendations.append("MACD死叉，技术面看跌")

    # 基于趋势
    if analysis['trend_short'] == '上涨' and analysis['trend_long'] == '上涨':
        recommendations.append("短期和长期均线上涨，趋势良好")
    elif analysis['trend_short'] == '下跌' and analysis['trend_long'] == '下跌':
        recommendations.append("短期和长期均线下跌，趋势偏弱")

    # 基于布林带位置
    if analysis['bb_position'] > 0.8:
        recommendations.append("接近布林带上轨，可能有压力")
    elif analysis['bb_position'] < 0.2:
        recommendations.append("接近布林带下轨，可能有支撑")

    # 基于波动率
    if analysis['volatility'] > 0.40:
        recommendations.append("波动率较高，注意风险控制")
    elif analysis['volatility'] < 0.20:
        recommendations.append("波动率较低，走势相对稳定")

    return " | ".join(recommendations) if recommendations else "持有观察"

def plot_stock_analysis(df, symbol, name, analysis):
    """绘制股票分析图表"""
    if df is None or df.empty:
        return

    fig, axes = plt.subplots(3, 1, figsize=(14, 12), gridspec_kw={'height_ratios': [3, 1, 1]})

    # 价格图表
    ax1 = axes[0]
    ax1.plot(df['date'], df['close'], label='收盘价', color='blue', linewidth=1.5)
    ax1.plot(df['date'], df['SMA_20'], label='20日均线', color='orange', linewidth=1, alpha=0.7)
    ax1.plot(df['date'], df['SMA_60'], label='60日均线', color='red', linewidth=1, alpha=0.7)
    ax1.fill_between(df['date'], df['BB_lower'], df['BB_upper'], alpha=0.1, color='gray', label='布林带')

    # 标记成本价
    if analysis['cost_price'] > 0:
        ax1.axhline(y=analysis['cost_price'], color='green', linestyle='--', linewidth=1, alpha=0.7, label=f'成本价: {analysis["cost_price"]:.2f}')

    ax1.set_title(f'{symbol} {name} - 价格分析', fontsize=14, fontweight='bold')
    ax1.set_ylabel('价格 (元)')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)

    # 成交量
    ax2 = axes[1]
    ax2.bar(df['date'], df['volume'], color='green', alpha=0.5, label='成交量')
    ax2.plot(df['date'], df['Volume_MA_20'], color='red', linewidth=1, label='20日成交量均线')
    ax2.set_ylabel('成交量')
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)

    # RSI和MACD
    ax3 = axes[2]
    # RSI
    ax3.plot(df['date'], df['RSI'], label='RSI', color='purple', linewidth=1)
    ax3.axhline(y=70, color='red', linestyle='--', linewidth=0.5, alpha=0.5)
    ax3.axhline(y=30, color='green', linestyle='--', linewidth=0.5, alpha=0.5)
    ax3.fill_between(df['date'], 30, 70, alpha=0.1, color='gray')

    ax3.set_xlabel('日期')
    ax3.set_ylabel('RSI')
    ax3.legend(loc='upper left')
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()

    # 保存图表
    if not os.path.exists('reports/holdings'):
        os.makedirs('reports/holdings')

    chart_file = f'reports/holdings/{symbol}_{name}_analysis.png'
    plt.savefig(chart_file, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"  分析图表已保存: {chart_file}")

def generate_holdings_report(analyses):
    """生成持仓分析报告"""
    print("\n" + "="*60)
    print("持仓股票综合分析报告")
    print("="*60)

    report_content = f"""
# 持仓股票分析报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 持仓概况
共分析 {len(analyses)} 只持仓股票

## 详细分析
"""

    summary_data = []

    for analysis in analyses:
        if analysis is None:
            continue

        # 添加到汇总数据
        summary_data.append({
            '股票代码': analysis['symbol'],
            '股票名称': analysis['name'],
            '当前价格': analysis['current_price'],
            '成本价格': analysis['cost_price'],
            '盈亏比例': analysis['cost_return'],
            '期间收益': analysis['period_return'],
            '波动率': analysis['volatility'],
            'RSI': analysis['rsi'],
            'MACD信号': analysis['macd_signal'],
            '短期趋势': analysis['trend_short'],
            '长期趋势': analysis['trend_long']
        })

        # 生成建议
        recommendation = generate_trading_recommendation(analysis)

        # 添加到报告
        report_content += f"""
### {analysis['symbol']} {analysis['name']}

**价格信息**
- 当前价格: {analysis['current_price']:.2f}元
- 成本价格: {analysis['cost_price']:.2f}元
- 盈亏比例: {analysis['cost_return']:+.2%}
- 期间收益率: {analysis['period_return']:+.2%}

**技术分析**
- RSI: {analysis['rsi']:.1f} ({'超买' if analysis['rsi'] > 70 else '超卖' if analysis['rsi'] < 30 else '中性'})
- MACD: {analysis['macd_signal']}
- 短期趋势: {analysis['trend_short']}
- 长期趋势: {analysis['trend_long']}
- 年化波动率: {analysis['volatility']:.2%}

**交易建议**
{recommendation}

---
"""

    # 生成汇总表格
    if summary_data:
        summary_df = pd.DataFrame(summary_data)

        # 按盈亏排序
        summary_df = summary_df.sort_values('盈亏比例', ascending=False)

        report_content += "\n## 持仓汇总（按盈亏排序）\n"

        # 添加汇总表格
        for _, row in summary_df.iterrows():
            status = "✅ 盈利" if row['盈亏比例'] > 0 else "❌ 亏损" if row['盈亏比例'] < 0 else "➖ 持平"
            report_content += f"- **{row['股票代码']} {row['股票名称']}**: {status} {row['盈亏比例']:+.2%} (当前: {row['当前价格']:.2f}元, 成本: {row['成本价格']:.2f}元)\n"

        # 保存汇总数据
        summary_df.to_csv('reports/holdings/holdings_summary.csv', index=False, encoding='utf-8-sig')
        print(f"持仓汇总数据已保存: reports/holdings/holdings_summary.csv")

    # 总体建议
    report_content += f"""
## 总体投资建议

### 盈利股票处理策略
1. **大幅盈利(>30%)**: 建议分批止盈，锁定利润
2. **中等盈利(10-30%)**: 设置移动止盈，让利润奔跑
3. **小幅盈利(<10%)**: 持有观察，关注技术面变化

### 亏损股票处理策略
1. **小幅亏损(<10%)**: 持有观察，等待反弹
2. **中度亏损(10-20%)**: 评估基本面，考虑是否补仓
3. **深度亏损(>20%)**: 重新评估投资逻辑，考虑止损

### 风险管理建议
1. **仓位控制**: 单只股票仓位不宜超过总资金的20%
2. **止损纪律**: 设置8-10%的止损线
3. **分散投资**: 行业分散，避免过度集中
4. **定期复盘**: 每月回顾持仓表现

### 后续行动计划
1. **短期(1周)**: 执行上述交易建议
2. **中期(1月)**: 优化持仓结构，调整仓位
3. **长期(3月)**: 建立系统化交易策略

## 注意事项
1. 本报告基于历史数据和技术分析，不构成投资建议
2. 市场有风险，投资需谨慎
3. 请结合自身风险承受能力做出决策
4. 建议实盘前进行充分回测和模拟交易

---
**报告生成**: 量化小助理 📈
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    # 保存报告
    report_file = 'reports/holdings_analysis_report.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)

    print(f"\n持仓分析报告已保存: {report_file}")

    return summary_df

def main():
    """主函数"""
    print("=" * 60)
    print("持仓股票分析系统")
    print("=" * 60)

    # 加载持仓信息
    holdings_df = load_holding_stocks()
    if holdings_df is None:
        return

    # 确保报告目录存在
    os.makedirs('reports/holdings', exist_ok=True)

    # 分析每只持仓股票
    analyses = []

    for _, row in holdings_df.iterrows():
        symbol = str(row['code'])
        name = row['name']
        cost_price = row['cost_price']

        print(f"\n{'='*40}")
        print(f"分析: {symbol} {name}")
        print(f"{'='*40}")

        # 加载数据
        df = load_stock_data(symbol)

        if df is not None and not df.empty:
            # 计算技术指标
            df = calculate_technical_indicators(df)

            # 分析表现
            analysis = analyze_stock_performance(df, symbol, name, cost_price)
            analyses.append(analysis)

            # 生成交易建议
            recommendation = generate_trading_recommendation(analysis)
            print(f"  交易建议: {recommendation}")

            # 绘制图表
            plot_stock_analysis(df, symbol, name, analysis)

            # 保存处理后的数据
            processed_file = f'data/processed/stock_{symbol}_processed.csv'
            df.to_csv(processed_file, index=False, encoding='utf-8-sig')
            print(f"  处理后的数据已保存: {processed_file}")
        else:
            print(f"  无法获取 {symbol} {name} 的数据")
            analyses.append(None)

    # 生成综合报告
    summary_df = generate_holdings_report(analyses)

    print("\n" + "=" * 60)
    print("分析完成!")
    print("=" * 60)

    if summary_df is not None and not summary_df.empty:
        print("\n持仓股票表现汇总:")
        print("-" * 80)
        for _, row in summary_df.iterrows():
            status = "✅ 盈利" if row['盈亏比例'] > 0 else "❌ 亏损" if row['盈亏比例'] < 0 else "➖ 持平"
            print(f"{row['股票代码']} {row['股票名称']:10} {status:10} {row['盈亏比例']:+.2%} "
                  f"(当前: {row['当前价格']:6.2f}元, 成本: {row['成本价格']:6.2f}元)")

    print("\n生成的文件:")
    print("1. reports/holdings_analysis_report.md - 详细分析报告")
    print("2. reports/holdings/ - 分析图表目录")
    print("3. reports/holdings/holdings_summary.csv - 持仓汇总数据")
    print("4. data/processed/ - 处理后的股票数据")

    print("\n下一步建议:")
    print("1. 查看详细分析报告")
    print("2. 根据交易建议调整持仓")
    print("3. 运行策略回测验证交易策略")

if __name__ == "__main__":
    main()
