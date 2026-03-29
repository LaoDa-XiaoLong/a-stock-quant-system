#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试股票池筛选系统 - 简化版本
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json
import os

class SimpleStockPoolFilter:
    """简化版股票池筛选器"""
    
    def __init__(self):
        self.cache_dir = "data/stock_pool"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 简化配置
        self.config = {
            'min_daily_turnover': 5000000,  # 500万
            'min_price': 2.0,  # 最低股价
            'max_price': 200.0,  # 最高股价
        }
    
    def get_test_stocks(self):
        """获取测试股票数据"""
        return [
            {'symbol': '000001', 'name': '平安银行', 'price': 10.5, 'turnover': 15000000},
            {'symbol': '000002', 'name': '万科A', 'price': 8.2, 'turnover': 8000000},
            {'symbol': '002352', 'name': '顺丰控股', 'price': 42.3, 'turnover': 12000000},
            {'symbol': '600580', 'name': '卧龙电驱', 'price': 15.7, 'turnover': 3000000},  # 成交额不足
            {'symbol': '603728', 'name': '鸣志电器', 'price': 25.1, 'turnover': 6000000},
            {'symbol': '002594', 'name': '比亚迪', 'price': 210.5, 'turnover': 25000000},  # 价格过高
            {'symbol': '600096', 'name': '云天化', 'price': 1.8, 'turnover': 7000000},  # 价格过低
        ]
    
    def filter_stock(self, stock):
        """筛选单个股票"""
        score = 100
        issues = []
        
        # 检查成交额
        if stock['turnover'] < self.config['min_daily_turnover']:
            issues.append(f"成交额不足: {stock['turnover']:,.0f}")
            score -= 40
        
        # 检查价格范围
        if stock['price'] < self.config['min_price']:
            issues.append(f"价格过低: {stock['price']:.2f}")
            score -= 30
        if stock['price'] > self.config['max_price']:
            issues.append(f"价格过高: {stock['price']:.2f}")
            score -= 30
        
        passed = score >= 60
        return {
            'symbol': stock['symbol'],
            'name': stock['name'],
            'price': stock['price'],
            'turnover': stock['turnover'],
            'score': score,
            'passed': passed,
            'issues': issues
        }
    
    def run_filter(self):
        """运行筛选"""
        print("简化版股票池筛选系统")
        print("=" * 50)
        
        # 获取测试数据
        test_stocks = self.get_test_stocks()
        print(f"测试股票数量: {len(test_stocks)}")
        print()
        
        # 筛选股票
        results = []
        passed_stocks = []
        
        for stock in test_stocks:
            result = self.filter_stock(stock)
            results.append(result)
            
            if result['passed']:
                passed_stocks.append(result)
        
        # 显示结果
        print("筛选结果:")
        print("-" * 80)
        print(f"{'代码':<8} {'名称':<10} {'价格':<8} {'成交额':<12} {'分数':<6} {'状态':<8} {'问题':<20}")
        print("-" * 80)
        
        for result in results:
            status = "✅通过" if result['passed'] else "❌未通过"
            issues = "; ".join(result['issues']) if result['issues'] else "无"
            print(f"{result['symbol']:<8} {result['name']:<10} {result['price']:<8.2f} "
                  f"{result['turnover']:<12,.0f} {result['score']:<6.0f} {status:<8} {issues:<20}")
        
        print("-" * 80)
        print(f"总共: {len(test_stocks)} 只股票")
        print(f"通过: {len(passed_stocks)} 只股票")
        print(f"通过率: {len(passed_stocks)/len(test_stocks)*100:.1f}%")
        
        # 保存结果
        if passed_stocks:
            # 按分数排序
            passed_stocks.sort(key=lambda x: x['score'], reverse=True)
            
            # 创建DataFrame
            df_data = []
            for stock in passed_stocks:
                df_data.append({
                    'symbol': stock['symbol'],
                    'name': stock['name'],
                    'price': stock['price'],
                    'daily_turnover': stock['turnover'],
                    'score': stock['score']
                })
            
            df = pd.DataFrame(df_data)
            
            # 保存CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_file = os.path.join(self.cache_dir, f"filtered_stocks_{timestamp}.csv")
            df.to_csv(csv_file, index=False, encoding='utf-8')
            print(f"\n筛选结果已保存: {csv_file}")
            
            # 生成报告
            report = self.generate_report(df)
            report_file = os.path.join(self.cache_dir, f"filter_report_{timestamp}.md")
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"筛选报告已保存: {report_file}")
        
        return passed_stocks
    
    def generate_report(self, filtered_df):
        """生成筛选报告"""
        report = []
        report.append("# 股票池筛选报告（简化版）")
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"筛选股票数量: {len(filtered_df)}")
        report.append("")
        
        report.append("## 筛选配置")
        report.append("```json")
        report.append(json.dumps(self.config, ensure_ascii=False, indent=2))
        report.append("```")
        report.append("")
        
        report.append("## 通过股票列表")
        report.append("| 排名 | 代码 | 名称 | 价格 | 日成交额 | 分数 |")
        report.append("|------|------|------|------|----------|------|")
        
        for i, (_, row) in enumerate(filtered_df.iterrows(), 1):
            report.append(f"| {i} | {row['symbol']} | {row['name']} | "
                         f"{row['price']:.2f} | {row['daily_turnover']/1e6:.1f}百万 | "
                         f"{row['score']:.0f} |")
        
        report.append("")
        report.append("## 下一步")
        report.append("1. 接入真实数据源（akshare）")
        report.append("2. 增加更多筛选规则（基本面、技术面）")
        report.append("3. 集成到交易系统")
        
        return "\n".join(report)


def main():
    """主函数"""
    print("股票池筛选系统测试 - 简化版")
    print("=" * 50)
    
    # 创建筛选器
    filter = SimpleStockPoolFilter()
    
    # 运行筛选
    passed_stocks = filter.run_filter()
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("下一步:")
    print("1. 接入akshare获取真实数据")
    print("2. 完善筛选规则")
    print("3. 创建完整的股票池管理系统")


if __name__ == "__main__":
    main()