#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
尾盘选股策略 v1.0
在收盘前30-60分钟筛选符合条件的股票
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TailEndStockSelection:
    """尾盘选股策略"""

    def __init__(self):
        self.strategy_name = "尾盘选股策略"
        self.strategy_version = "v1.0"
        self.selection_time = "14:30-15:00"  # 尾盘选股时间窗口
        self.output_dir = "data/tail_end_selection"

        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)

    def get_current_time(self):
        """获取当前时间"""
        return datetime.now()

    def is_tail_end_time(self, current_time=None):
        """判断是否是尾盘时间"""
        if current_time is None:
            current_time = self.get_current_time()

        # 尾盘时间：14:30-15:00
        tail_start = current_time.replace(hour=14, minute=30, second=0, microsecond=0)
        tail_end = current_time.replace(hour=15, minute=0, second=0, microsecond=0)

        return tail_start <= current_time <= tail_end

    def get_stock_data(self, stock_codes: List[str]) -> Dict[str, Dict]:
        """
        获取股票数据（模拟函数，实际需要接入真实数据源）
        """
        stock_data = {}

        # 这里模拟获取股票数据
        # 实际应用中应该接入akshare、tushare等数据源
        for code in stock_codes:
            stock_data[code] = {
                "code": code,
                "name": f"股票{code}",
                "current_price": np.random.uniform(5, 50),
                "change_percent": np.random.uniform(-5, 5),
                "volume": np.random.randint(10000, 1000000),
                "amount": np.random.uniform(1000000, 100000000),
                "amplitude": np.random.uniform(1, 10),
                "turnover_rate": np.random.uniform(1, 20),
                "pe_ratio": np.random.uniform(10, 50),
                "pb_ratio": np.random.uniform(1, 5),
                "market_cap": np.random.uniform(1000000000, 100000000000),
                "industry": np.random.choice(["科技", "金融", "消费", "医药", "制造"]),
                "concept": np.random.choice(["5G", "人工智能", "新能源", "芯片", "医药"], 2),
                "intraday_pattern": self._generate_intraday_pattern(),
                "tail_volume_ratio": np.random.uniform(0.5, 2.0),  # 尾盘成交量比例
                "large_order_flow": np.random.uniform(-10000000, 10000000),  # 大单资金流
                "technical_indicators": self._generate_technical_indicators()
            }

        return stock_data

    def _generate_intraday_pattern(self):
        """生成日内分时图形态"""
        patterns = [
            "V型反转",
            "U型反转",
            "W底形态",
            "M头形态",
            "单边上涨",
            "单边下跌",
            "横盘震荡",
            "尾盘拉升",
            "尾盘跳水",
            "全天强势"
        ]
        return np.random.choice(patterns)

    def _generate_technical_indicators(self):
        """生成技术指标"""
        return {
            "macd": {
                "dif": np.random.uniform(-1, 1),
                "dea": np.random.uniform(-1, 1),
                "macd": np.random.uniform(-0.5, 0.5),
                "signal": "金叉" if np.random.random() > 0.5 else "死叉"
            },
            "kdj": {
                "k": np.random.uniform(0, 100),
                "d": np.random.uniform(0, 100),
                "j": np.random.uniform(0, 100),
                "signal": "超买" if np.random.random() > 0.7 else "超卖" if np.random.random() < 0.3 else "正常"
            },
            "rsi": {
                "rsi6": np.random.uniform(0, 100),
                "rsi12": np.random.uniform(0, 100),
                "rsi24": np.random.uniform(0, 100),
                "signal": "强势" if np.random.random() > 0.6 else "弱势"
            }
        }

    def apply_selection_criteria(self, stock_data: Dict[str, Dict]) -> List[Dict]:
        """
        应用尾盘选股标准
        """
        selected_stocks = []

        for code, data in stock_data.items():
            score = 0
            reasons = []

            # 1. 价格走势评分（20分）
            if data["change_percent"] > 0:
                score += 10
                reasons.append("当日上涨")
            if abs(data["change_percent"]) < 3:  # 波动适中
                score += 5
                reasons.append("波动适中")
            if data["intraday_pattern"] in ["尾盘拉升", "V型反转", "全天强势"]:
                score += 5
                reasons.append(f"分时形态好: {data['intraday_pattern']}")

            # 2. 成交量评分（20分）
            if data["tail_volume_ratio"] > 1.2:  # 尾盘放量
                score += 10
                reasons.append("尾盘放量")
            if data["turnover_rate"] > 3:  # 换手率适中
                score += 5
                reasons.append("换手活跃")
            if data["volume"] > 100000:  # 成交量足够
                score += 5
                reasons.append("成交量充足")

            # 3. 资金流向评分（20分）
            if data["large_order_flow"] > 0:
                score += 15
                reasons.append("大单资金净流入")
            elif data["large_order_flow"] > -1000000:
                score += 5
                reasons.append("资金流出可控")

            # 4. 技术指标评分（20分）
            tech = data["technical_indicators"]
            if tech["macd"]["signal"] == "金叉":
                score += 10
                reasons.append("MACD金叉")
            if tech["kdj"]["signal"] == "超卖":
                score += 5
                reasons.append("KDJ超卖有反弹机会")
            elif tech["kdj"]["signal"] == "正常":
                score += 3
                reasons.append("KDJ正常")
            if tech["rsi"]["signal"] == "强势":
                score += 5
                reasons.append("RSI强势")

            # 5. 基本面评分（20分）
            if data["pe_ratio"] < 30:
                score += 10
                reasons.append("估值合理")
            if data["pb_ratio"] < 3:
                score += 5
                reasons.append("市净率合理")
            if data["market_cap"] > 5000000000:  # 50亿市值以上
                score += 5
                reasons.append("市值适中")

            # 总分计算
            total_score = min(score, 100)  # 上限100分

            if total_score >= 60:  # 合格线
                stock_info = {
                    "code": code,
                    "name": data["name"],
                    "score": total_score,
                    "current_price": data["current_price"],
                    "change_percent": data["change_percent"],
                    "selection_reasons": reasons,
                    "intraday_pattern": data["intraday_pattern"],
                    "tail_volume_ratio": data["tail_volume_ratio"],
                    "large_order_flow": data["large_order_flow"],
                    "technical_indicators": data["technical_indicators"],
                    "selection_time": self.get_current_time().strftime("%Y-%m-%d %H:%M:%S"),
                    "selection_strategy": self.strategy_name,
                    "strategy_version": self.strategy_version
                }
                selected_stocks.append(stock_info)

        # 按评分排序
        selected_stocks.sort(key=lambda x: x["score"], reverse=True)

        return selected_stocks

    def calculate_entry_points(self, stock: Dict) -> Dict:
        """
        计算进场点位
        尾盘策略通常采用更保守的进场方式
        """
        current_price = stock["current_price"]

        # 尾盘策略进场点位（基于当前价格）
        entry_points = {
            "激进进场": round(current_price * 0.99, 2),      # 下跌1%
            "稳健进场": round(current_price * 0.97, 2),      # 下跌3%
            "保守进场": round(current_price * 0.95, 2),      # 下跌5%
            "尾盘追涨": round(current_price * 1.01, 2)      # 上涨1%（仅限强势股）
        }

        # 风险控制
        stop_loss = round(current_price * 0.92, 2)  # 止损8%
        take_profit = [
            round(current_price * 1.08, 2),  # 第一止盈8%
            round(current_price * 1.15, 2)   # 第二止盈15%
        ]

        return {
            "entry_points": entry_points,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "risk_reward_ratio": round((take_profit[0] - current_price) / (current_price - stop_loss), 2)
        }

    def generate_selection_report(self, selected_stocks: List[Dict]) -> str:
        """生成选股报告"""
        report_lines = []

        report_lines.append("# 尾盘选股策略报告")
        report_lines.append(f"## 生成时间: {self.get_current_time().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"## 策略版本: {self.strategy_name} {self.strategy_version}")
        report_lines.append(f"## 选股时间窗口: {self.selection_time}")
        report_lines.append("")

        if not selected_stocks:
            report_lines.append("## 选股结果: 无符合条件的股票")
            return "\n".join(report_lines)

        report_lines.append(f"## 选股结果: 共筛选出 {len(selected_stocks)} 只股票")
        report_lines.append("")

        for i, stock in enumerate(selected_stocks[:10], 1):  # 只显示前10只
            risk_data = self.calculate_entry_points(stock)

            report_lines.append(f"### {i}. {stock['name']} ({stock['code']})")
            report_lines.append(f"- **综合评分**: {stock['score']}/100")
            report_lines.append(f"- **当前价格**: {stock['current_price']:.2f}元")
            report_lines.append(f"- **今日涨跌**: {stock['change_percent']:.2f}%")
            report_lines.append(f"- **分时形态**: {stock['intraday_pattern']}")
            report_lines.append(f"- **尾盘量比**: {stock['tail_volume_ratio']:.2f}")
            report_lines.append(f"- **大单资金**: {stock['large_order_flow']:,.0f}元")
            report_lines.append("")

            report_lines.append("#### 进场点位建议:")
            for entry_type, price in risk_data["entry_points"].items():
                report_lines.append(f"  - {entry_type}: {price:.2f}元")

            report_lines.append("")
            report_lines.append("#### 风险控制:")
            report_lines.append(f"  - **止损位**: {risk_data['stop_loss']:.2f}元")
            report_lines.append(f"  - **第一止盈**: {risk_data['take_profit'][0]:.2f}元")
            report_lines.append(f"  - **第二止盈**: {risk_data['take_profit'][1]:.2f}元")
            report_lines.append(f"  - **风险收益比**: {risk_data['risk_reward_ratio']:.2f}")
            report_lines.append("")

            report_lines.append("#### 选股理由:")
            for reason in stock["selection_reasons"]:
                report_lines.append(f"  - {reason}")

            report_lines.append("")
            report_lines.append("---")
            report_lines.append("")

        return "\n".join(report_lines)

    def save_selection_results(self, selected_stocks: List[Dict]):
        """保存选股结果"""
        timestamp = self.get_current_time().strftime("%Y%m%d_%H%M%S")

        # 保存JSON格式
        json_path = os.path.join(self.output_dir, f"tail_end_selection_{timestamp}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                "selection_time": timestamp,
                "strategy_name": self.strategy_name,
                "strategy_version": self.strategy_version,
                "total_selected": len(selected_stocks),
                "stocks": selected_stocks
            }, f, ensure_ascii=False, indent=2)

        # 保存报告
        report_path = os.path.join(self.output_dir, f"tail_end_selection_report_{timestamp}.md")
        report_content = self.generate_selection_report(selected_stocks)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"选股结果已保存:")
        print(f"  - JSON文件: {json_path}")
        print(f"  - 报告文件: {report_path}")

        return json_path, report_path

    def run_selection(self, stock_codes: List[str] = None):
        """运行尾盘选股"""
        print(f"开始执行尾盘选股策略: {self.strategy_name} {self.strategy_version}")
        print(f"选股时间窗口: {self.selection_time}")
        print("=" * 60)

        # 检查是否是尾盘时间
        if not self.is_tail_end_time():
            current_time = self.get_current_time().strftime("%H:%M:%S")
            print(f"当前时间 {current_time} 不在尾盘选股时间窗口内")
            print(f"尾盘选股时间窗口: {self.selection_time}")
            return None

        # 如果没有提供股票代码，使用默认的测试代码
        if stock_codes is None:
            stock_codes = [
                "000001", "000002", "000004", "000005", "000006",
                "000007", "000008", "000009", "000010", "000011",
                "000012", "000014", "000016", "000017", "000019",
                "000020", "000021", "000023", "000025", "000026"
            ]

        print(f"获取 {len(stock_codes)} 只股票数据...")
        stock_data = self.get_stock_data(stock_codes)

        print("应用尾盘选股标准...")
        selected_stocks = self.apply_selection_criteria(stock_data)

        print(f"筛选完成，共选出 {len(selected_stocks)} 只符合条件的股票")

        if selected_stocks:
            print("\n前5只推荐股票:")
            for i, stock in enumerate(selected_stocks[:5], 1):
                print(f"{i}. {stock['name']} ({stock['code']}) - 评分: {stock['score']}分")

        # 保存结果
        json_path, report_path = self.save_selection_results(selected_stocks)

        return {
            "selected_stocks": selected_stocks,
            "json_path": json_path,
            "report_path": report_path
        }


def main():
    """主函数"""
    selector = TailEndStockSelection()

    # 运行选股
    result = selector.run_selection()

    if result:
        print("\n尾盘选股策略执行完成！")
        print(f"详细报告请查看: {result['report_path']}")
    else:
        print("尾盘选股策略未执行（不在尾盘时间窗口）")


if __name__ == "__main__":
    main()
