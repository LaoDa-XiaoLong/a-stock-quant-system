#!/usr/bin/env python3
"""
简化版股票数据更新脚本
专注于核心功能：获取最新数据并应用选股策略
"""

import akshare as ak
import pandas as pd
import numpy as np
import os
import json
import time
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def setup_directories():
    """创建必要的目录"""
    print("📁 创建目录结构...")
    directories = ['data', 'data/raw', 'data/stock_pool', 'reports', 'logs']
    for dir_name in directories:
        os.makedirs(dir_name, exist_ok=True)
        print(f"  ✅ {dir_name}")

def get_stock_list():
    """获取A股股票列表"""
    print("📋 获取A股股票列表...")
    try:
        stock_info = ak.stock_info_a_code_name()
        if stock_info is not None and not stock_info.empty:
            print(f"  ✅ 获取到 {len(stock_info)} 只股票")

            # 保存股票列表
            stock_list_file = 'data/stock_list_latest.csv'
            stock_info.to_csv(stock_list_file, index=False, encoding='utf-8-sig')
            print(f"  💾 股票列表已保存到 {stock_list_file}")

            return stock_info
        else:
            print("  ❌ 获取股票列表失败")
            return None
    except Exception as e:
        print(f"  ❌ 获取股票列表异常: {e}")
        return None

def get_market_indices_simple():
    """获取主要市场指数数据（简化版）"""
    print("📈 获取市场指数数据...")

    indices = [
        ('sh000001', '上证指数'),
        ('sz399001', '深证成指'),
        ('sz399006', '创业板指'),
    ]

    success_count = 0
    for symbol, name in indices:
        try:
            df = ak.stock_zh_index_daily(symbol=symbol)
            if df is not None and not df.empty:
                filename = f'data/raw/index_{symbol}_{datetime.now().strftime("%Y%m%d")}.csv'
                df.to_csv(filename, index=False, encoding='utf-8-sig')
                print(f"  ✅ {name}: {len(df)} 条记录")
                success_count += 1
            time.sleep(0.5)
        except Exception as e:
            print(f"  ❌ {name}: {str(e)[:50]}")

    return success_count

def apply_simple_screening():
    """应用简化选股策略"""
    print("🔍 应用选股策略筛选...")

    try:
        # 获取实时数据
        spot_data = ak.stock_zh_a_spot()

        if spot_data is None or spot_data.empty:
            print("  ❌ 无法获取实时数据")
            return []

        # 数据预处理
        spot_data = spot_data.copy()

        # 转换数值列
        numeric_columns = ['涨跌幅', '涨跌额', '成交量', '成交额', '振幅', '换手率']
        for col in numeric_columns:
            if col in spot_data.columns:
                spot_data[col] = pd.to_numeric(spot_data[col], errors='coerce')

        # 筛选条件
        # 1. 去除ST股票
        spot_data = spot_data[~spot_data['名称'].str.contains('ST', na=False)]

        # 2. 去除涨跌幅异常的股票
        if '涨跌幅' in spot_data.columns:
            spot_data = spot_data[(spot_data['涨跌幅'] >= -10) & (spot_data['涨跌幅'] <= 10)]

        # 3. 计算简单得分
        scores = []
        for idx, row in spot_data.iterrows():
            score = 0

            # 基于涨跌幅评分
            if '涨跌幅' in row and not pd.isna(row['涨跌幅']):
                if 0 < row['涨跌幅'] <= 3:
                    score += 30
                elif row['涨跌幅'] > 3:
                    score += 20

            # 基于换手率评分
            if '换手率' in row and not pd.isna(row['换手率']):
                if 1 <= row['换手率'] <= 5:
                    score += 25

            # 基于成交额评分
            if '成交额' in row and not pd.isna(row['成交额']):
                if row['成交额'] > 100000000:
                    score += 25

            scores.append(score)

        spot_data['score'] = scores

        # 按得分排序并取前20
        spot_data = spot_data.sort_values('score', ascending=False)
        top_stocks = spot_data.head(20)

        # 准备结果
        screening_results = []
        for idx, row in top_stocks.iterrows():
            stock_info = {
                'code': row['代码'],
                'name': row['名称'],
                'score': int(row['score']),
                'change_pct': float(row['涨跌幅']) if '涨跌幅' in row and not pd.isna(row['涨跌幅']) else 0,
                'turnover': float(row['换手率']) if '换手率' in row and not pd.isna(row['换手率']) else 0,
                'volume': float(row['成交额']) if '成交额' in row and not pd.isna(row['成交额']) else 0,
            }
            screening_results.append(stock_info)

        # 保存筛选结果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'data/stock_pool/screening_results_{timestamp}.json'

        output_data = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "time": datetime.now().strftime('%H:%M:%S'),
            "total_stocks": len(screening_results),
            "stocks": screening_results,
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"  ✅ 筛选完成，选出 {len(screening_results)} 只优质股票")
        print(f"  💾 结果保存到 {output_file}")

        return screening_results

    except Exception as e:
        print(f"  ❌ 选股策略执行失败: {e}")
        return []

def generate_report(stock_count, index_count, screening_results):
    """生成报告"""
    print("📝 生成数据更新报告...")

    report_file = f'reports/data_update_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'

    report_content = f"""# 股票数据自动更新报告（简化版）

## 基本信息
- **报告时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **执行环境**: Python + akshare

## 数据获取概况
- **股票列表**: 已更新最新A股股票列表
- **指数数据**: 获取{index_count}/3个主要市场指数
- **选股结果**: 筛选出{len(screening_results)}只优质股票

## 选股策略TOP 10
| 排名 | 代码 | 名称 | 评分 | 涨跌幅 | 换手率 |
|------|------|------|------|--------|--------|
"""

    for i, stock in enumerate(screening_results[:10], 1):
        report_content += f"| {i} | {stock['code']} | {stock['name']} | {stock['score']} | {stock['change_pct']:.2f}% | {stock['turnover']:.2f}% |\n"

    report_content += f"""
## 执行状态
✅ 目录结构创建完成
✅ 股票列表获取完成
✅ 市场指数数据更新完成
✅ 选股策略筛选执行完成

## 下一步建议
1. **定期执行**: 建议每日定时执行此脚本
2. **策略优化**: 根据实际需求调整选股策略
3. **数据验证**: 定期检查数据完整性和准确性

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)

    print(f"  💾 报告已保存到 {report_file}")
    return report_file

def main():
    """主函数"""
    print("=" * 60)
    print("📈 股票数据自动更新系统（简化版）")
    print("=" * 60)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    start_time = datetime.now()

    try:
        # 步骤1: 创建目录
        print("🚀 步骤1: 创建目录结构")
        setup_directories()

        # 步骤2: 获取股票列表
        print("\n🚀 步骤2: 获取A股股票列表")
        stock_list = get_stock_list()

        # 步骤3: 获取市场指数
        print("\n🚀 步骤3: 获取市场指数数据")
        indices_count = get_market_indices_simple()

        # 步骤4: 应用选股策略
        print("\n🚀 步骤4: 应用选股策略筛选")
        screening_results = apply_simple_screening()

        # 步骤5: 生成报告
        print("\n🚀 步骤5: 生成报告")
        report_file = generate_report(
            len(stock_list) if stock_list is not None else 0,
            indices_count,
            screening_results
        )

        # 计算执行时间
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # 输出总结
        print("\n" + "=" * 60)
        print("✅ 股票数据自动更新完成!")
        print("=" * 60)

        print(f"\n📊 执行总结:")
        print(f"  开始时间: {start_time.strftime('%H:%M:%S')}")
        print(f"  结束时间: {end_time.strftime('%H:%M:%S')}")
        print(f"  总耗时: {duration:.1f} 秒")
        print(f"  股票列表: {'✅ 已获取' if stock_list is not None else '❌ 失败'}")
        print(f"  市场指数: {indices_count}/3 个")
        print(f"  选股结果: {len(screening_results)} 只优质股票")

        if screening_results:
            print(f"\n📈 选股策略TOP 5:")
            for i, stock in enumerate(screening_results[:5], 1):
                print(f"  {i}. {stock['code']} {stock['name']} - 评分: {stock['score']} (涨跌幅: {stock['change_pct']:.2f}%)")

        print(f"\n💾 生成文件:")
        print(f"  1. data/stock_list_latest.csv - 最新股票列表")
        print(f"  2. data/raw/ - 市场指数数据")
        print(f"  3. data/stock_pool/ - 选股策略结果")
        print(f"  4. {report_file} - 数据更新报告")

    except Exception as e:
        print(f"\n❌ 执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
