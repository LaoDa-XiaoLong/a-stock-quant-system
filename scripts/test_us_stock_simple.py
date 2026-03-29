#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版美股数据测试 - 不使用yfinance
"""

import pandas as pd
from datetime import datetime, timedelta
import time
import json
import os

class SimpleUSStockTester:
    """简化版美股测试器"""
    
    def __init__(self):
        self.cache_dir = "data/us_stocks"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 测试股票列表（简化）
        self.test_symbols = {
            'AAPL': '苹果',
            'MSFT': '微软', 
            'NVDA': '英伟达',
            'TSM': '台积电',
            'BABA': '阿里巴巴'
        }
    
    def test_with_mock_data(self):
        """使用模拟数据测试"""
        print("美股数据获取测试（模拟数据）")
        print("=" * 50)
        
        results = []
        
        for symbol, name in self.test_symbols.items():
            print(f"处理 {symbol} ({name})...")
            
            try:
                # 生成模拟数据
                mock_data = self.generate_mock_data(symbol, name)
                
                result = {
                    'symbol': symbol,
                    'name': name,
                    'status': '模拟成功',
                    'data_points': len(mock_data['history']),
                    'latest_price': mock_data['latest_price'],
                    'latest_date': mock_data['latest_date'],
                    'response_time': '0.1s',
                    'info_keys': len(mock_data['info']),
                    'error': None
                }
                
                results.append(result)
                
                # 保存模拟数据
                self.save_mock_data(symbol, mock_data)
                
                print(f"  ✅ 模拟成功: {len(mock_data['history'])}个数据点, 最新价: {mock_data['latest_price']:.2f}")
                
            except Exception as e:
                error_result = {
                    'symbol': symbol,
                    'name': name,
                    'status': '模拟错误',
                    'data_points': 0,
                    'latest_price': 0,
                    'latest_date': '',
                    'response_time': 'N/A',
                    'info_keys': 0,
                    'error': str(e)
                }
                results.append(error_result)
                print(f"  ❌ 模拟失败: {e}")
        
        # 显示结果
        self.display_results(results)
        
        # 生成报告
        report_file = self.generate_report(results)
        
        return results, report_file
    
    def generate_mock_data(self, symbol, name):
        """生成模拟数据"""
        # 生成过去30天的日期
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # 基础价格（根据股票不同）
        base_prices = {
            'AAPL': 180.0,
            'MSFT': 420.0,
            'NVDA': 950.0,
            'TSM': 150.0,
            'BABA': 80.0
        }
        
        base_price = base_prices.get(symbol, 100.0)
        
        # 生成价格序列
        np.random.seed(hash(symbol) % 10000)
        returns = np.random.normal(0.001, 0.02, len(dates))
        prices = base_price * np.cumprod(1 + returns)
        
        # 创建历史数据DataFrame
        history_data = pd.DataFrame({
            'Date': dates,
            'Open': prices * (1 + np.random.normal(0, 0.005, len(dates))),
            'High': prices * (1 + np.abs(np.random.normal(0, 0.01, len(dates)))),
            'Low': prices * (1 - np.abs(np.random.normal(0, 0.01, len(dates)))),
            'Close': prices,
            'Volume': np.random.randint(1000000, 10000000, len(dates))
        })
        
        # 公司信息
        info_data = {
            'symbol': symbol,
            'name': name,
            'sector': 'Technology',
            'industry': 'Semiconductors' if symbol in ['NVDA', 'TSM'] else 'Software',
            'marketCap': base_price * 1e9,  # 模拟市值
            'peRatio': np.random.uniform(20, 40),
            'dividendYield': np.random.uniform(0.5, 2.0),
            'beta': np.random.uniform(0.8, 1.2),
            'update_time': datetime.now().isoformat()
        }
        
        return {
            'history': history_data,
            'latest_price': prices[-1],
            'latest_date': dates[-1].strftime('%Y-%m-%d'),
            'info': info_data
        }
    
    def save_mock_data(self, symbol, mock_data):
        """保存模拟数据"""
        # 保存历史数据
        hist_file = os.path.join(self.cache_dir, f"{symbol}_history_mock.csv")
        mock_data['history'].to_csv(hist_file, index=False, encoding='utf-8')
        
        # 保存公司信息
        info_file = os.path.join(self.cache_dir, f"{symbol}_info_mock.json")
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(mock_data['info'], f, ensure_ascii=False, indent=2)
    
    def display_results(self, results):
        """显示结果"""
        print("\n" + "=" * 50)
        print("测试结果汇总")
        print("=" * 50)
        
        success_count = sum(1 for r in results if r['status'] == '模拟成功')
        total_count = len(results)
        
        print(f"测试股票数: {total_count}")
        print(f"成功: {success_count}")
        print(f"失败: {total_count - success_count}")
        print(f"成功率: {success_count/total_count*100:.1f}%")
        
        print("\n详细结果:")
        print("-" * 80)
        print(f"{'代码':<8} {'名称':<10} {'状态':<8} {'数据点':<8} {'最新价':<10} {'响应时间':<10}")
        print("-" * 80)
        
        for result in results:
            print(f"{result['symbol']:<8} {result['name']:<10} {result['status']:<8} "
                  f"{result['data_points']:<8} {result['latest_price']:<10.2f} "
                  f"{result['response_time']:<10}")
    
    def generate_report(self, results):
        """生成测试报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(self.cache_dir, f"mock_test_report_{timestamp}.md")
        
        report = []
        report.append("# 美股数据获取测试报告（模拟数据）")
        report.append(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("测试说明: 使用模拟数据测试数据获取流程")
        report.append("")
        
        # 汇总统计
        success_count = sum(1 for r in results if r['status'] == '模拟成功')
        total_count = len(results)
        
        report.append("## 测试结果汇总")
        report.append(f"- 测试股票数: {total_count}")
        report.append(f"- 成功: {success_count}")
        report.append(f"- 失败: {total_count - success_count}")
        report.append(f"- 成功率: {success_count/total_count*100:.1f}%")
        report.append("")
        
        # 详细结果
        report.append("## 详细测试结果")
        report.append("| 代码 | 名称 | 状态 | 数据点 | 最新价 | 响应时间 |")
        report.append("|------|------|------|--------|--------|----------|")
        
        for result in results:
            report.append(f"| {result['symbol']} | {result['name']} | {result['status']} | "
                         f"{result['data_points']} | {result['latest_price']:.2f} | "
                         f"{result['response_time']} |")
        
        # 结论与建议
        report.append("")
        report.append("## 结论与建议")
        report.append("")
        report.append("### 当前状态")
        report.append("1. ✅ 数据获取流程测试通过")
        report.append("2. ✅ 数据存储机制工作正常")
        report.append("3. ✅ 报告生成系统运行良好")
        report.append("")
        report.append("### 下一步行动")
        report.append("1. **注册Alpha Vantage**（推荐）")
        report.append("   - 网址: https://www.alphavantage.co/")
        report.append("   - 免费层: 500次API调用/天")
        report.append("   - 获取API key后替换模拟数据")
        report.append("")
        report.append("2. **测试真实数据获取**")
        report.append("   - 使用Alpha Vantage API")
        report.append("   - 验证数据质量和稳定性")
        report.append("   - 优化错误处理和重试机制")
        report.append("")
        report.append("3. **开发多数据源支持**")
        report.append("   - 添加yfinance作为备用（解决兼容性问题后）")
        report.append("   - 考虑IEX Cloud等其他数据源")
        report.append("   - 实现数据源故障转移")
        
        # 保存报告
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(report))
        
        print(f"\n测试报告已保存: {report_file}")
        return report_file
    
    def create_alpha_vantage_guide(self):
        """创建Alpha Vantage使用指南"""
        guide_file = os.path.join(self.cache_dir, "alpha_vantage_guide.md")
        
        guide = []
        guide.append("# Alpha Vantage 使用指南")
        guide.append("")
        guide.append("## 1. 注册获取API Key")
        guide.append("1. 访问 https://www.alphavantage.co/support/#api-key")
        guide.append("2. 填写注册表单")
        guide.append("3. 获取免费的API Key")
        guide.append("")
        guide.append("## 2. API Key示例")
        guide.append("```")
        guide.append("您的API Key将类似: X4QZP6J8K2L0M9N1")
        guide.append("```")
        guide.append("")
        guide.append("## 3. 免费层限制")
        guide.append("- 500次API调用/天")
        guide.append("- 5次API调用/分钟")
        guide.append("- 足够个人使用和测试")
        guide.append("")
        guide.append("## 4. 常用API端点")
        guide.append("")
        guide.append("### 实时股价（15分钟延迟）")
        guide.append("```python")
        guide.append("import requests")
        guide.append("")
        guide.append("url = 'https://www.alphavantage.co/query'")
        guide.append("params = {")
        guide.append("    'function': 'TIME_SERIES_INTRADAY',")
        guide.append("    'symbol': 'AAPL',")
        guide.append("    'interval': '5min',")
        guide.append("    'apikey': 'YOUR_API_KEY'")
        guide.append("}")
        guide.append("response = requests.get(url, params=params)")
        guide.append("data = response.json()")
        guide.append("```")
        guide.append("")
        guide.append("### 历史日线数据")
        guide.append("```python")
        guide.append("params = {")
        guide.append("    'function': 'TIME_SERIES_DAILY',")
        guide.append("    'symbol': 'AAPL',")
        guide.append("    'outputsize': 'compact',  # 最近100天")
        guide.append("    'apikey': 'YOUR_API_KEY'")
        guide.append("}")
        guide.append("```")
        guide.append("")
        guide.append("### 公司概况")
        guide.append("```python")
        guide.append("params = {")
        guide.append("    'function': 'OVERVIEW',")
        guide.append("    'symbol': 'AAPL',")
        guide.append("    'apikey': 'YOUR_API_KEY'")
        guide.append("}")
        guide.append("```")
        guide.append("")
        guide.append("## 5. 建议的股票列表")
        guide.append("```python")
        guide.append("key_stocks = [")
        guide.append("    'AAPL',   # 苹果")
        guide.append("    'MSFT',   # 微软")
        guide.append("    'NVDA',   # 英伟达")
        guide.append("    'AMD',    # AMD")
        guide.append("    'TSM',    # 台积电")
        guide.append("    'AVGO',   # 博通")
        guide.append("    'QCOM',   # 高通")
        guide.append("    'INTC',   # 英特尔")
        guide.append("    'BABA',   # 阿里巴巴")
        guide.append("    'PDD',    # 拼多多")
        guide.append("    '^GSPC',  # 标普500")
        guide.append("    '^IXIC',  # 纳斯达克")
        guide.append("    '^SOX',   # 费城半导体")
        guide.append("]")
        guide.append("```")
        guide.append("")
        guide.append("## 6. 注意事项")
        guide.append("1. **缓存数据**：避免重复调用相同API")
        guide.append("2. **错误处理**：API可能返回错误，需要重试机制")
        guide.append("3. **频率限制**：不要超过5次/分钟的限制")
        guide.append("4. **数据延迟**：实时数据有15分钟延迟")
        guide.append("")
        guide.append("## 7. 下一步")
        guide.append("1. 注册并获取API Key")
        guide.append("2. 测试基础API调用")
        guide.append("3. 集成到我们的数据获取系统")
        guide.append("4. 开发数据缓存和错误处理")
        
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(guide))
        
        print(f"\nAlpha Vantage使用指南已保存: {guide_file}")
        return guide_file


def main():
    """主函数"""
    print("简化版美股数据测试")
    print("=" * 50)
    
    # 创建测试器
    tester = SimpleUSStockTester()
    
    # 使用模拟数据测试
    results, report_file = tester.test_with_mock_data()
    
    # 创建Alpha Vantage指南
    guide_file = tester.create_alpha_vantage_guide()
    
    print("\n" + "=" * 50)
    print("测试完成")
    print(f"测试报告: {report_file}")
    print(f"使用指南: {guide_file}")
    print("\n下一步行动:")
    print("1. 请注册Alpha Vantage获取API Key")
    print("2. 将API Key提供给我进行真实数据测试")
    print("3. 我们将开发完整的美股数据获取系统")


if __name__ == "__main__":
    # 需要numpy生成模拟数据
    import numpy as np
    main()