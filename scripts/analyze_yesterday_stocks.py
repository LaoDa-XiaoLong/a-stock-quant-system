#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析昨天符合杨永兴战法的股票
找出昨天的尾盘选股标的及进场价格
"""

import json
import os
import sys
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.yang_yongxing_fixed import YangYongxingOvernightStrategy

class YesterdayStockAnalyzer:
    """昨天股票分析器"""
    
    def __init__(self):
        self.strategy = YangYongxingOvernightStrategy()
        self.yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        self.output_dir = "data/yesterday_analysis"
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
    
    def get_yesterday_stock_data(self):
        """获取昨天的股票数据（模拟）"""
        print(f"获取 {self.yesterday} 的股票数据...")
        
        # 模拟昨天的A股股票数据
        stocks = {}
        
        # A股主要股票代码（示例）
        stock_codes = [
            "000001", "000002", "000004", "000005", "000006",
            "000007", "000008", "000009", "000010", "000011",
            "600000", "600036", "600030", "600016", "600519",
            "600887", "600104", "600276", "600309", "600585",
            "300059", "300122", "300124", "300142", "300144"
        ]
        
        for code in stock_codes:
            # 随机生成昨天的股票数据
            # 注意：实际应用中应该从数据库或API获取真实数据
            
            # 基础信息
            if code.startswith("000"):
                exchange = "SZ"
                name_prefix = "深市"
            elif code.startswith("600"):
                exchange = "SH"
                name_prefix = "沪市"
            else:
                exchange = "SZ"
                name_prefix = "创业"
            
            # 随机生成符合杨永兴战法的数据
            base_price = np.random.uniform(5, 100)
            
            # 模拟昨天的走势：大部分股票小幅上涨，部分符合杨永兴条件
            if np.random.random() < 0.3:  # 30%的股票符合杨永兴条件
                change_percent = np.random.uniform(3, 5)  # 3-5%涨幅
                capital_flow = np.random.uniform(0.1, 0.3)  # 资金大幅流入
                volume_ratio = np.random.uniform(1.7, 2.5)  # 明显放量
                market_cap = np.random.uniform(50, 180)  # 中小盘
                tech_space = np.random.uniform(8, 12)  # 技术空间好
            else:
                change_percent = np.random.uniform(-2, 3)  # 普通涨跌
                capital_flow = np.random.uniform(-0.1, 0.1)
                volume_ratio = np.random.uniform(0.8, 1.6)
                market_cap = np.random.uniform(100, 500)
                tech_space = np.random.uniform(0, 8)
            
            stocks[code] = {
                "code": code,
                "name": f"{name_prefix}股票{code[-3:]}",
                "current_price": round(base_price * (1 + change_percent/100), 2),
                "change_percent": round(change_percent, 2),
                "capital_flow_ratio": round(capital_flow, 3),
                "volume_ratio": round(volume_ratio, 2),
                "market_cap": round(market_cap, 1),
                "technical_space": round(tech_space, 1),
                "date": self.yesterday,
                "exchange": exchange
            }
        
        print(f"共获取 {len(stocks)} 只股票数据")
        return stocks
    
    def analyze_yesterday_tail_end(self, stock_data: Dict[str, Dict]):
        """分析昨天的尾盘选股机会"""
        print(f"\n分析 {self.yesterday} 的尾盘选股机会...")
        
        # 模拟昨天尾盘时间
        original_get_time = self.strategy.get_current_time
        
        def mock_yesterday_tail_time():
            # 昨天的14:45
            yesterday_date = datetime.now() - timedelta(days=1)
            return yesterday_date.replace(hour=14, minute=45, second=0, microsecond=0)
        
        self.strategy.get_current_time = mock_yesterday_tail_time
        
        try:
            # 应用杨永兴战法选股标准
            selected_stocks = self.strategy.apply_yang_yongxing_criteria(stock_data)
            
            print(f"✅ 昨天尾盘符合杨永兴战法的股票: {len(selected_stocks)} 只")
            
            return selected_stocks
            
        finally:
            self.strategy.get_current_time = original_get_time
    
    def calculate_yesterday_entry_prices(self, selected_stocks: List[Dict]):
        """计算昨天的进场价格"""
        print(f"\n计算昨天的进场价格...")
        
        entry_details = []
        
        for stock in selected_stocks:
            # 计算进场点位
            entry_data = self.strategy.calculate_overnight_entry_points(stock)
            
            # 模拟昨天的实际走势
            # 假设昨天尾盘进场，今天观察结果
            today_price = stock["current_price"] * (1 + np.random.uniform(-3, 5)/100)
            today_change = (today_price - stock["current_price"]) / stock["current_price"] * 100
            
            entry_detail = {
                "code": stock["code"],
                "name": stock["name"],
                "yesterday_data": {
                    "date": self.yesterday,
                    "price": stock["current_price"],
                    "change": stock["change_percent"],
                    "capital_flow": stock.get("capital_flow_ratio", 0),
                    "volume_ratio": stock.get("volume_ratio", 1.0),
                    "market_cap": stock.get("market_cap", 0)
                },
                "entry_strategy": entry_data,
                "simulated_today": {
                    "price": round(today_price, 2),
                    "change": round(today_change, 2),
                    "result": "盈利" if today_change > 0 else "亏损",
                    "profit_loss": round(today_change, 2)
                },
                "strategy_score": stock["score"],
                "passed_steps": stock["passed_steps"]
            }
            
            entry_details.append(entry_detail)
        
        # 按策略评分排序
        entry_details.sort(key=lambda x: x["strategy_score"], reverse=True)
        
        return entry_details
    
    def generate_yesterday_report(self, entry_details: List[Dict]):
        """生成昨天分析报告"""
        report_lines = []
        
        report_lines.append("# 昨天尾盘选股分析报告")
        report_lines.append(f"## 分析日期: {datetime.now().strftime('%Y-%m-%d')}")
        report_lines.append(f"## 分析目标: {self.yesterday} 的尾盘选股机会")
        report_lines.append(f"## 使用策略: {self.strategy.strategy_name}")
        report_lines.append(f"## 策略作者: {self.strategy.strategy_author}")
        report_lines.append("")
        
        if not entry_details:
            report_lines.append("## 分析结果: 昨天无符合条件的尾盘选股机会")
            return "\n".join(report_lines)
        
        report_lines.append(f"## 分析结果: 昨天共发现 {len(entry_details)} 只符合条件的股票")
        report_lines.append("")
        
        report_lines.append("## 一、策略核心理念")
        for key, value in self.strategy.core_principles.items():
            report_lines.append(f"- **{key}**: {value}")
        report_lines.append("")
        
        report_lines.append("## 二、昨天尾盘选股详情")
        
        for i, detail in enumerate(entry_details[:10], 1):  # 只显示前10只
            report_lines.append(f"### {i}. {detail['name']} ({detail['code']})")
            report_lines.append(f"- **策略评分**: {detail['strategy_score']}/100")
            report_lines.append(f"- **通过步骤**: {detail['passed_steps']}/6")
            report_lines.append("")
            
            report_lines.append("#### 昨天数据:")
            yesterday = detail["yesterday_data"]
            report_lines.append(f"- **日期**: {yesterday['date']}")
            report_lines.append(f"- **收盘价**: {yesterday['price']:.2f}元")
            report_lines.append(f"- **涨跌幅**: {yesterday['change']:.2f}%")
            report_lines.append(f"- **资金流入**: {yesterday['capital_flow']*100:.1f}%")
            report_lines.append(f"- **量比**: {yesterday['volume_ratio']:.2f}")
            report_lines.append(f"- **市值**: {yesterday['market_cap']:.1f}亿元")
            report_lines.append("")
            
            report_lines.append("#### 尾盘进场策略:")
            entry = detail["entry_strategy"]
            report_lines.append(f"- **进场价格**: {entry['entry_price']:.2f}元")
            report_lines.append(f"- **目标价格**: {entry['target_price']:.2f}元 (涨幅{entry['target_gain']:.1f}%)")
            report_lines.append(f"- **止损价格**: {entry['stop_loss']:.2f}元")
            report_lines.append(f"- **风险收益比**: {entry['risk_reward_ratio']:.2f}")
            report_lines.append(f"- **仓位建议**: {entry['position_suggestion']}")
            report_lines.append("")
            
            report_lines.append("#### 模拟今日表现:")
            today = detail["simulated_today"]
            result_emoji = "📈" if today["result"] == "盈利" else "📉"
            report_lines.append(f"- **今日价格**: {today['price']:.2f}元")
            report_lines.append(f"- **今日涨跌**: {today['change']:.2f}%")
            report_lines.append(f"- **交易结果**: {result_emoji} {today['result']}")
            report_lines.append(f"- **盈亏**: {today['profit_loss']:.2f}%")
            report_lines.append("")
            
            report_lines.append("---")
            report_lines.append("")
        
        report_lines.append("## 三、策略效果统计")
        
        if entry_details:
            total_stocks = len(entry_details)
            profitable = sum(1 for d in entry_details if d["simulated_today"]["result"] == "盈利")
            win_rate = profitable / total_stocks * 100
            
            avg_profit = np.mean([d["simulated_today"]["profit_loss"] for d in entry_details if d["simulated_today"]["result"] == "盈利"])
            avg_loss = np.mean([d["simulated_today"]["profit_loss"] for d in entry_details if d["simulated_today"]["result"] == "亏损"])
            
            report_lines.append(f"- **总股票数**: {total_stocks} 只")
            report_lines.append(f"- **盈利股票**: {profitable} 只")
            report_lines.append(f"- **亏损股票**: {total_stocks - profitable} 只")
            report_lines.append(f"- **胜率**: {win_rate:.1f}%")
            report_lines.append(f"- **平均盈利**: {avg_profit:.2f}%" if profitable > 0 else "- **平均盈利**: 无盈利")
            report_lines.append(f"- **平均亏损**: {avg_loss:.2f}%" if total_stocks - profitable > 0 else "- **平均亏损**: 无亏损")
            report_lines.append("")
        
        report_lines.append("## 四、今日操作建议")
        report_lines.append("1. **学习昨天经验**: 分析昨天选股的成功与失败原因")
        report_lines.append("2. **优化策略参数**: 根据昨天表现调整选股标准")
        report_lines.append("3. **准备今天尾盘**: 今天14:30开始执行杨永兴战法")
        report_lines.append("4. **严格风险控制**: 设置止损，控制仓位")
        report_lines.append("5. **持续跟踪**: 记录每笔交易，总结经验")
        report_lines.append("")
        
        report_lines.append("## 五、风险提示")
        report_lines.append("1. **历史不代表未来**: 昨天表现好不代表今天也会好")
        report_lines.append("2. **市场变化**: 市场环境随时可能变化")
        report_lines.append("3. **严格执行**: 必须严格执行止损止盈纪律")
        report_lines.append("4. **分散投资**: 不要把所有资金投入一只股票")
        report_lines.append("5. **持续学习**: 投资需要不断学习和调整")
        
        return "\n".join(report_lines)
    
    def save_analysis_results(self, entry_details: List[Dict], report: str):
        """保存分析结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存JSON数据
        json_path = os.path.join(self.output_dir, f"yesterday_analysis_{timestamp}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                "analysis_date": datetime.now().strftime("%Y-%m-%d"),
                "target_date": self.yesterday,
                "strategy_name": self.strategy.strategy_name,
                "total_stocks": len(entry_details),
                "entry_details": entry_details
            }, f, ensure_ascii=False, indent=2)
        
        # 保存报告
        report_path = os.path.join(self.output_dir, f"yesterday_report_{timestamp}.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ 分析结果已保存:")
        print(f"  - JSON文件: {json_path}")
        print(f"  - 报告文件: {report_path}")
        
        return json_path, report_path
    
    def run_analysis(self):
        """运行昨天分析"""
        print("=" * 60)
        print("昨天尾盘选股分析系统")
        print(f"分析日期: {self.yesterday}")
        print(f"使用策略: {self.strategy.strategy_name}")
        print("=" * 60)
        
        # 获取昨天股票数据
        stock_data = self.get_yesterday_stock_data()
        
        # 分析尾盘选股机会
        selected_stocks = self.analyze_yesterday_tail_end(stock_data)
        
        if not selected_stocks:
            print("\n❌ 昨天没有符合条件的尾盘选股机会")
            return None
        
        # 计算进场价格
        entry_details = self.calculate_yesterday_entry_prices(selected_stocks)
        
        # 生成报告
        report = self.generate_yesterday_report(entry_details)
        
        # 保存结果
        json_path, report_path = self.save_analysis_results(entry_details, report)
        
        # 显示摘要
        print("\n" + "=" * 60)
        print("📊 分析摘要:")
        print("=" * 60)
        
        profitable = sum(1 for d in entry_details if d["simulated_today"]["result"] == "盈利")
        win_rate = profitable / len(entry_details) * 100
        
        print(f"昨天符合条件的股票: {len(entry_details)} 只")
        print(f"模拟盈利股票: {profitable} 只")
        print(f"模拟胜率: {win_rate:.1f}%")
        print("")
        
        print("前3只推荐股票:")
        for i, detail in enumerate(entry_details[:3], 1):
            today = detail["simulated_today"]
            result_emoji = "📈" if today["result"] == "盈利" else "📉"
            print(f"{i}. {detail['name']} ({detail['code']})")
            print(f"   评分: {detail['strategy_score']}分 | 通过步骤: {detail['passed_steps']}/6")
            print(f"   进场价: {detail['entry_strategy']['entry_price']:.2f}元")
            print(f"   模拟结果: {result_emoji} {today['result']} {today['profit_loss']:.2f}%")
        
        print(f"\n详细报告: {report_path}")
        
        return {
            "entry_details": entry_details,
            "json_path": json_path,
            "report_path": report_path
        }


def main():
    """主函数"""
    analyzer = YesterdayStockAnalyzer()
    
    result = analyzer.run_analysis()
    
    if result:
        print("\n" + "=" * 60)
        print("✅ 昨天尾盘选股分析完成!")
        print("=" * 60)
    else:
        print("\n❌ 分析失败或无符合条件的股票")


if __name__ == "__main__":
    main()