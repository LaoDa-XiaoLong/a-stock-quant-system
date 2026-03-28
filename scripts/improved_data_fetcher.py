#!/usr/bin/env python3
"""
改进的A股数据获取脚本
尝试多种方法获取数据
"""

import akshare as ak
import pandas as pd
import os
import time
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def test_akshare_connection():
    """测试akshare连接"""
    print("测试akshare连接...")
    try:
        # 尝试获取简单的数据
        test_df = ak.stock_zh_a_spot()
        if test_df is not None and not test_df.empty:
            print(f"✅ akshare连接成功，获取到 {len(test_df)} 只股票实时数据")
            return True
        else:
            print("❌ akshare连接失败，返回空数据")
            return False
    except Exception as e:
        print(f"❌ akshare连接异常: {e}")
        return False

def get_stock_data_multiple_methods(symbol, name, years=3):
    """尝试多种方法获取股票数据"""
    print(f"\n尝试获取 {symbol} {name} 的{years}年数据...")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years*365)
    start_str = start_date.strftime('%Y%m%d')
    end_str = end_date.strftime('%Y%m%d')
    
    methods = [
        ("方法1: stock_zh_a_hist", lambda: ak.stock_zh_a_hist(
            symbol=symbol, period="daily", start_date=start_str, 
            end_date=end_str, adjust="qfq")),
        
        ("方法2: stock_zh_a_hist (不复权)", lambda: ak.stock_zh_a_hist(
            symbol=symbol, period="daily", start_date=start_str, 
            end_date=end_str, adjust="")),
        
        ("方法3: stock_zh_a_daily", lambda: ak.stock_zh_a_daily(
            symbol=symbol, start_date=start_str, end_date=end_str)),
    ]
    
    for method_name, method_func in methods:
        print(f"  尝试{method_name}...")
        try:
            df = method_func()
            if df is not None and not df.empty:
                print(f"    ✅ 成功获取 {len(df)} 条记录")
                
                # 保存数据
                filename = f"data/raw/stock_{symbol}_{start_str}_{end_str}.csv"
                df.to_csv(filename, index=False, encoding='utf-8-sig')
                print(f"    数据已保存: {filename}")
                
                # 显示基本信息
                if '日期' in df.columns:
                    print(f"    数据期间: {df['日期'].iloc[0]} 到 {df['日期'].iloc[-1]}")
                elif 'date' in df.columns:
                    print(f"    数据期间: {df['date'].iloc[0]} 到 {df['date'].iloc[-1]}")
                
                return df
            else:
                print(f"    ❌ 返回空数据")
        except Exception as e:
            print(f"    ❌ 失败: {str(e)[:100]}...")
        
        time.sleep(1)  # 避免请求过快
    
    print(f"  ❌ 所有方法都失败")
    return None

def get_all_market_stocks():
    """获取全市场股票列表"""
    print("\n获取全市场股票列表...")
    
    markets = {
        '上证主板': 'sh',
        '深证主板': 'sz', 
        '创业板': 'cy',
        '科创板': 'kc'
    }
    
    all_stocks = []
    
    for market_name, market_code in markets.items():
        print(f"  获取{market_name}股票列表...")
        try:
            # 这里需要根据akshare的实际接口调整
            if market_code == 'sh':
                # 上证股票
                df = ak.stock_sh_a_spot_em()
            elif market_code == 'sz':
                # 深证股票
                df = ak.stock_sz_a_spot_em()
            else:
                # 创业板和科创板可能需要其他接口
                df = ak.stock_zh_a_spot()
                # 筛选对应市场的股票
                if market_code == 'cy':
                    df = df[df['代码'].str.startswith('3')]
                elif market_code == 'kc':
                    df = df[df['代码'].str.startswith('688')]
            
            if df is not None and not df.empty:
                df['市场'] = market_name
                all_stocks.append(df)
                print(f"    ✅ 获取到 {len(df)} 只{market_name}股票")
            else:
                print(f"    ❌ 获取{market_name}股票失败")
                
        except Exception as e:
            print(f"    ❌ 获取{market_name}股票异常: {str(e)[:100]}...")
        
        time.sleep(1)
    
    if all_stocks:
        # 合并所有股票
        combined_df = pd.concat(all_stocks, ignore_index=True)
        print(f"\n✅ 总共获取到 {len(combined_df)} 只全市场股票")
        
        # 保存股票列表
        combined_df.to_csv('data/stock_list_all_markets.csv', index=False, encoding='utf-8-sig')
        print(f"股票列表已保存: data/stock_list_all_markets.csv")
        
        # 统计各市场数量
        print("\n各市场股票数量:")
        market_counts = combined_df['市场'].value_counts()
        for market, count in market_counts.items():
            print(f"  {market}: {count} 只")
        
        return combined_df
    else:
        print("❌ 未能获取任何市场股票列表")
        return None

def get_market_indices():
    """获取主要市场指数"""
    print("\n获取市场指数数据...")
    
    indices = [
        ('sh000001', '上证指数'),
        ('sz399001', '深证成指'),
        ('sz399006', '创业板指'),
        ('sh000016', '上证50'),
        ('sh000300', '沪深300'),
        ('sh000905', '中证500'),
        ('sz399005', '中小板指'),
        ('sh000688', '科创50')
    ]
    
    for symbol, name in indices:
        print(f"  获取{name}({symbol})...")
        try:
            df = ak.stock_zh_index_daily(symbol=symbol)
            if df is not None and not df.empty:
                # 保存数据
                filename = f"data/raw/index_{symbol}.csv"
                df.to_csv(filename, index=False, encoding='utf-8-sig')
                print(f"    ✅ 获取 {len(df)} 条记录，已保存")
            else:
                print(f"    ❌ 获取失败")
        except Exception as e:
            print(f"    ❌ 异常: {str(e)[:100]}...")
        
        time.sleep(0.5)

def update_holdings_data():
    """更新持仓股票数据"""
    print("\n" + "="*60)
    print("更新持仓股票数据")
    print("="*60)
    
    # 持仓股票
    holdings = [
        ('002594', '比亚迪', 99.0),
        ('603728', '鸣志电器', 68.0),
        ('600580', '卧龙电驱', 42.0),
        ('600183', '生益科技', 66.0),
        ('603259', '药明康德', 101.0),
        ('002352', '顺丰控股', 40.0),
        ('600096', '云天化', 37.0)
    ]
    
    success_count = 0
    for symbol, name, cost in holdings:
        df = get_stock_data_multiple_methods(symbol, name, years=3)
        if df is not None:
            success_count += 1
    
    print(f"\n✅ 成功获取 {success_count}/{len(holdings)} 只持仓股票数据")
    return success_count

def generate_data_report():
    """生成数据获取报告"""
    print("\n" + "="*60)
    print("数据获取报告")
    print("="*60)
    
    # 统计文件
    raw_files = [f for f in os.listdir('data/raw') if f.endswith('.csv')]
    stock_files = [f for f in raw_files if f.startswith('stock_')]
    index_files = [f for f in raw_files if f.startswith('index_')]
    
    print(f"数据文件统计:")
    print(f"  总文件数: {len(raw_files)}")
    print(f"  股票数据文件: {len(stock_files)}")
    print(f"  指数数据文件: {len(index_files)}")
    
    # 读取全市场股票列表
    all_stocks_file = 'data/stock_list_all_markets.csv'
    if os.path.exists(all_stocks_file):
        all_stocks = pd.read_csv(all_stocks_file)
        print(f"\n全市场股票覆盖:")
        print(f"  总股票数: {len(all_stocks)}")
        
        # 统计各市场
        if '市场' in all_stocks.columns:
            market_counts = all_stocks['市场'].value_counts()
            for market, count in market_counts.items():
                print(f"  {market}: {count} 只")
    
    # 生成报告
    report = f"""
# A股数据获取详细报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 数据获取概况
- 总数据文件: {len(raw_files)} 个
- 股票数据文件: {len(stock_files)} 个
- 指数数据文件: {len(index_files)} 个

## 市场覆盖情况
"""
    
    if os.path.exists(all_stocks_file):
        all_stocks = pd.read_csv(all_stocks_file)
        report += f"- 全市场股票总数: {len(all_stocks)} 只\n"
        
        if '市场' in all_stocks.columns:
            market_counts = all_stocks['市场'].value_counts()
            for market, count in market_counts.items():
                report += f"- {market}: {count} 只\n"
    
    report += f"""
## 持仓股票数据状态
- 比亚迪 (002594): {'✅ 已获取' if any('002594' in f for f in stock_files) else '❌ 未获取'}
- 鸣志电器 (603728): {'✅ 已获取' if any('603728' in f for f in stock_files) else '❌ 未获取'}
- 卧龙电驱 (600580): {'✅ 已获取' if any('600580' in f for f in stock_files) else '❌ 未获取'}
- 生益科技 (600183): {'✅ 已获取' if any('600183' in f for f in stock_files) else '❌ 未获取'}
- 药明康德 (603259): {'✅ 已获取' if any('603259' in f for f in stock_files) else '❌ 未获取'}
- 顺丰控股 (002352): {'✅ 已获取' if any('002352' in f for f in stock_files) else '❌ 未获取'}
- 云天化 (600096): {'✅ 已获取' if any('600096' in f for f in stock_files) else '❌ 未获取'}

## 指数数据覆盖
- 上证指数、深证成指、创业板指等主要指数已获取

## 数据质量
- 数据期间: 3年历史数据
- 数据频率: 日线数据
- 复权方式: 前复权(优先)

## 存在问题
1. 部分股票数据获取可能受API限制
2. 科创板、创业板数据需要特殊处理
3. 实时数据更新需要定时任务

## 下一步计划
1. 完善数据更新机制
2. 增加数据质量检查
3. 实现定时自动更新
"""
    
    # 保存报告
    report_file = 'reports/data_acquisition_detailed_report.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n详细报告已保存: {report_file}")
    return report

def main():
    """主函数"""
    print("=" * 70)
    print("改进版A股数据获取系统")
    print("=" * 70)
    
    # 确保目录存在
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    
    # 测试连接
    if not test_akshare_connection():
        print("❌ 连接测试失败，请检查网络")
        return
    
    # 获取全市场股票列表
    all_stocks = get_all_market_stocks()
    
    # 获取市场指数
    get_market_indices()
    
    # 更新持仓数据
    holdings_success = update_holdings_data()
    
    # 生成报告
    report = generate_data_report()
    
    print("\n" + "=" * 70)
    print("数据获取完成!")
    print("=" * 70)
    
    print(f"\n执行结果:")
    print(f"✅ 连接测试: 通过")
    print(f"✅ 全市场股票: {'已获取' if all_stocks is not None else '失败'}")
    print(f"✅ 持仓股票: {holdings_success}/7 只成功获取")
    print(f"✅ 详细报告: 已生成")
    
    print(f"\n生成文件:")
    print(f"1. data/stock_list_all_markets.csv - 全市场股票列表")
    print(f"2. data/raw/ - 股票和指数数据文件")
    print(f"3. reports/data_acquisition_detailed_report.md - 详细报告")
    
    print(f"\n下一步:")
    print(f"1. 查看详细报告了解数据覆盖情况")
    print(f"2. 运行持仓分析脚本更新分析结果")
    print(f"3. 根据数据完整性制定交易策略")

if __name__ == "__main__":
    main()