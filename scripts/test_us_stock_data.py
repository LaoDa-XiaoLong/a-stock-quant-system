#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试美股免费数据源
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import json
import os

class USStockDataTester:
    """美股数据测试器"""

    def __init__(self):
        self.cache_dir = "data/us_stocks"
        os.makedirs(self.cache_dir, exist_ok=True)

        # 测试股票列表
        self.test_symbols = {
            'AAPL': '苹果',
            'MSFT': '微软',
            'NVDA': '英伟达',
            'AMD': 'AMD',
            'TSM': '台积电',
            'AVGO': '博通',
            'QCOM': '高通',
            'INTC': '英特尔',
            'BABA': '阿里巴巴',
            'PDD': '拼多多',
            '^GSPC': '标普500',
            '^IXIC': '纳斯达克',
            '^SOX': '费城半导体'
        }

    def test_yfinance(self):
        """测试yfinance数据获取"""
        print("测试 yfinance 数据获取")
        print("=" * 50)

        results = []

        for symbol, name in list(self.test_symbols.items())[:5]:  # 先测试5个
            print(f"获取 {symbol} ({name}) 数据...")

            try:
                start_time = time.time()

                # 创建Ticker对象
                ticker = yf.Ticker(symbol)

                # 获取历史数据（过去30天）
                hist = ticker.history(period="1mo")

                # 获取公司信息
                info = ticker.info

                end_time = time.time()
                elapsed = end_time - start_time

                if not hist.empty:
                    result = {
                        'symbol': symbol,
                        'name': name,
                        'status': '成功',
                        'data_points': len(hist),
                        'latest_price': hist['Close'].iloc[-1] if len(hist) > 0 else 0,
                        'latest_date': hist.index[-1].strftime('%Y-%m-%d') if len(hist) > 0 else '',
                        'response_time': f"{elapsed:.2f}s",
                        'info_keys': len(info),
                        'error': None
                    }

                    # 保存数据
                    self.save_data(symbol, hist, info)

                else:
                    result = {
                        'symbol': symbol,
                        'name': name,
                        'status': '失败',
                        'data_points': 0,
                        'latest_price': 0,
                        'latest_date': '',
                        'response_time': f"{elapsed:.2f}s",
                        'info_keys': 0,
                        'error': '历史数据为空'
                    }

                results.append(result)
                print(f"  ✅ 成功: {len(hist)}个数据点, 最新价: {result['latest_price']:.2f}")

                # 避免请求过快
                time.sleep(1)

            except Exception as e:
                error_result = {
                    'symbol': symbol,
                    'name': name,
                    'status': '错误',
                    'data_points': 0,
                    'latest_price': 0,
                    'latest_date': '',
                    'response_time': 'N/A',
                    'info_keys': 0,
                    'error': str(e)
                }
                results.append(error_result)
                print(f"  ❌ 失败: {e}")
                continue

        # 显示结果汇总
        print("\n" + "=" * 50)
        print("yfinance 测试结果汇总")
        print("=" * 50)

        success_count = sum(1 for r in results if r['status'] == '成功')
        fail_count = sum(1 for r in results if r['status'] == '失败')
        error_count = sum(1 for r in results if r['status'] == '错误')

        print(f"测试股票数: {len(results)}")
        print(f"成功: {success_count}")
        print(f"失败: {fail_count}")
        print(f"错误: {error_count}")
        print(f"成功率: {success_count/len(results)*100:.1f}%")

        # 显示详情
        print("\n详细结果:")
        print("-" * 80)
        print(f"{'代码':<8} {'名称':<10} {'状态':<6} {'数据点':<8} {'最新价':<10} {'响应时间':<10} {'错误信息':<20}")
        print("-" * 80)

        for result in results:
            error_msg = result['error'][:18] + '...' if result['error'] and len(result['error']) > 20 else result['error'] or ''
            print(f"{result['symbol']:<8} {result['name']:<10} {result['status']:<6} "
                  f"{result['data_points']:<8} {result['latest_price']:<10.2f} "
                  f"{result['response_time']:<10} {error_msg:<20}")

        return results

    def save_data(self, symbol, hist_data, info_data):
        """保存数据到文件"""
        # 保存历史数据
        hist_file = os.path.join(self.cache_dir, f"{symbol}_history.csv")
        hist_data.to_csv(hist_file, encoding='utf-8')

        # 保存公司信息
        info_file = os.path.join(self.cache_dir, f"{symbol}_info.json")
        with open(info_file, 'w', encoding='utf-8') as f:
            # 过滤掉不能JSON序列化的数据
            serializable_info = {}
            for key, value in info_data.items():
                try:
                    json.dumps({key: value})
                    serializable_info[key] = value
                except:
                    serializable_info[key] = str(value)

            json.dump(serializable_info, f, ensure_ascii=False, indent=2)

    def analyze_correlation(self):
        """分析美股-A股相关性"""
        print("\n" + "=" * 50)
        print("分析美股-A股相关性（示例）")
        print("=" * 50)

        # 这里简化处理，实际需要获取A股数据
        print("需要获取A股对应股票数据进行分析")
        print("建议分析方向:")
        print("1. 苹果(AAPL) vs 立讯精密(002475)")
        print("2. 英伟达(NVDA) vs 寒武纪(688256)")
        print("3. 台积电(TSM) vs 中芯国际(688981)")
        print("4. 纳斯达克(^IXIC) vs 创业板指(399006)")

        return None

    def generate_report(self, test_results):
        """生成测试报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(self.cache_dir, f"test_report_{timestamp}.md")

        report = []
        report.append("# 美股免费数据源测试报告")
        report.append(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"测试数据源: yfinance")
        report.append("")

        # 汇总统计
        success_count = sum(1 for r in test_results if r['status'] == '成功')
        total_count = len(test_results)

        report.append("## 测试结果汇总")
        report.append(f"- 测试股票数: {total_count}")
        report.append(f"- 成功: {success_count}")
        report.append(f"- 失败: {total_count - success_count}")
        report.append(f"- 成功率: {success_count/total_count*100:.1f}%")
        report.append("")

        # 详细结果
        report.append("## 详细测试结果")
        report.append("| 代码 | 名称 | 状态 | 数据点 | 最新价 | 响应时间 | 错误信息 |")
        report.append("|------|------|------|--------|--------|----------|----------|")

        for result in test_results:
            error_msg = result['error'] or ''
            report.append(f"| {result['symbol']} | {result['name']} | {result['status']} | "
                         f"{result['data_points']} | {result['latest_price']:.2f} | "
                         f"{result['response_time']} | {error_msg[:30]} |")

        # 结论与建议
        report.append("")
        report.append("## 结论与建议")

        if success_count / total_count >= 0.8:
            report.append("✅ **yfinance可用性良好**，适合作为美股数据源")
            report.append("")
            report.append("### 优点")
            report.append("1. 完全免费，无API调用限制")
            report.append("2. 数据质量较好，包含历史数据和公司信息")
            report.append("3. Python接口简单易用")
            report.append("")
            report.append("### 注意事项")
            report.append("1. 非官方API，稳定性依赖Yahoo Finance")
            report.append("2. 实时数据有延迟（约15分钟）")
            report.append("3. 需要处理可能的限流")
            report.append("")
            report.append("### 建议")
            report.append("1. 作为主要免费数据源使用")
            report.append("2. 配合缓存机制减少重复请求")
            report.append("3. 考虑添加备用数据源（如Alpha Vantage）")
        else:
            report.append("⚠️ **yfinance可用性存在问题**，需要进一步测试")
            report.append("")
            report.append("### 建议")
            report.append("1. 检查网络连接和代理设置")
            report.append("2. 测试其他数据源（Alpha Vantage）")
            report.append("3. 调整请求频率和重试机制")

        # 保存报告
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(report))

        print(f"\n测试报告已保存: {report_file}")
        return report_file


def main():
    """主函数"""
    print("美股免费数据源测试")
    print("=" * 50)

    # 创建测试器
    tester = USStockDataTester()

    # 测试yfinance
    test_results = tester.test_yfinance()

    # 生成报告
    report_file = tester.generate_report(test_results)

    print("\n" + "=" * 50)
    print("测试完成")
    print(f"详细报告: {report_file}")
    print("\n下一步:")
    print("1. 注册Alpha Vantage进行对比测试")
    print("2. 开发多数据源聚合模块")
    print("3. 集成到美股-A股联动分析")


if __name__ == "__main__":
    main()
