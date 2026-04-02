#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
尾盘选股策略 v2.0 - 修复版
基于常见尾盘选股方法优化
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

class TailEndStrategyV2:
    """尾盘选股策略 v2.0"""

    def __init__(self):
        self.strategy_name = "尾盘选股策略"
        self.strategy_version = "v2.0"
        self.selection_time = "14:30-15:00"
        self.output_dir = "data/tail_end_selection_v2"

        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)

        # 策略权重配置
        self.weights = {
            "price_movement": 25,      # 价格走势
            "volume_analysis": 20,     # 成交量分析
            "capital_flow": 25,        # 资金流向
            "technical_indicators": 20, # 技术指标
            "pattern_analysis": 10     # 形态分析
        }

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

    def analyze_price_movement(self, stock_data: Dict) -> Dict:
        """分析价格走势"""
        score = 0
        reasons = []

        # 1. 当日涨跌幅
        change = stock_data.get("change_percent", 0)
        if 0 < change <= 5:  # 小幅上涨最佳
            score += 10
            reasons.append(f"当日上涨{change:.2f}%，幅度适中")
        elif -3 <= change <= 0:  # 小幅下跌或平盘
            score += 5
            reasons.append(f"当日涨跌{change:.2f}%，波动可控")

        # 2. 日内振幅
        amplitude = stock_data.get("amplitude", 0)
        if 2 <= amplitude <= 8:  # 适中振幅
            score += 5
            reasons.append(f"日内振幅{amplitude:.1f}%，波动合理")

        # 3. 尾盘走势（模拟数据）
        tail_trend = stock_data.get("tail_trend", "unknown")
        if tail_trend == "拉升":
            score += 10
            reasons.append("尾盘明显拉升")
        elif tail_trend == "平稳":
            score += 5
            reasons.append("尾盘走势平稳")

        return {"score": score, "reasons": reasons}

    def analyze_volume(self, stock_data: Dict) -> Dict:
        """分析成交量"""
        score = 0
        reasons = []

        # 1. 尾盘量比
        tail_volume_ratio = stock_data.get("tail_volume_ratio", 1.0)
        if tail_volume_ratio > 1.5:
            score += 10
            reasons.append(f"尾盘明显放量（量比{tail_volume_ratio:.2f}）")
        elif tail_volume_ratio > 1.2:
            score += 5
            reasons.append(f"尾盘温和放量（量比{tail_volume_ratio:.2f}）")

        # 2. 换手率
        turnover = stock_data.get("turnover_rate", 0)
        if 3 <= turnover <= 15:  # 适中换手
            score += 5
            reasons.append(f"换手率{turnover:.1f}%，交投活跃")
        elif turnover > 15:  # 过高换手
            score += 2
            reasons.append(f"换手率{turnover:.1f}%，需注意风险")

        # 3. 成交量趋势
        volume_trend = stock_data.get("volume_trend", "unknown")
        if volume_trend == "递增":
            score += 5
            reasons.append("成交量递增")

        return {"score": score, "reasons": reasons}

    def analyze_capital_flow(self, stock_data: Dict) -> Dict:
        """分析资金流向"""
        score = 0
        reasons = []

        # 1. 大单资金流
        large_order_flow = stock_data.get("large_order_flow", 0)
        if large_order_flow > 10000000:  # 1000万以上
            score += 15
            reasons.append(f"大单资金净流入{large_order_flow/10000:.0f}万元")
        elif large_order_flow > 0:
            score += 10
            reasons.append(f"大单资金净流入{large_order_flow/10000:.0f}万元")
        elif large_order_flow > -5000000:  # 流出可控
            score += 3
            reasons.append(f"资金小幅流出{abs(large_order_flow)/10000:.0f}万元")

        # 2. 主力资金
        main_capital = stock_data.get("main_capital_ratio", 0)
        if main_capital > 0.1:  # 主力资金占比10%以上
            score += 10
            reasons.append(f"主力资金占比{main_capital*100:.1f}%")

        return {"score": score, "reasons": reasons}

    def analyze_technical_indicators(self, stock_data: Dict) -> Dict:
        """分析技术指标"""
        score = 0
        reasons = []

        tech = stock_data.get("technical_indicators", {})

        # 1. MACD分析
        macd = tech.get("macd", {})
        if macd.get("signal") == "金叉":
            score += 8
            reasons.append("MACD金叉信号")
        elif macd.get("dif", 0) > macd.get("dea", 0):
            score += 5
            reasons.append("MACD即将金叉")

        # 2. KDJ分析
        kdj = tech.get("kdj", {})
        k_value = kdj.get("k", 50)
        d_value = kdj.get("d", 50)
        if k_value < 30 and d_value < 30:  # 超卖区域
            score += 6
            reasons.append("KDJ超卖，有反弹机会")
        elif 20 < k_value < 80 and 20 < d_value < 80:  # 正常区域
            score += 4
            reasons.append("KDJ处于正常区域")

        # 3. RSI分析
        rsi = tech.get("rsi", {})
        rsi6 = rsi.get("rsi6", 50)
        if 30 < rsi6 < 70:  # 正常区域
            score += 6
            reasons.append(f"RSI({rsi6:.0f})处于正常区域")

        return {"score": score, "reasons": reasons}

    def analyze_pattern(self, stock_data: Dict) -> Dict:
        """分析形态"""
        score = 0
        reasons = []

        # 1. 分时图形态
        intraday_pattern = stock_data.get("intraday_pattern", "")
        good_patterns = ["V型反转", "U型反转", "尾盘拉升", "突破平台", "单边上涨"]

        if intraday_pattern in good_patterns:
            score += 10
            reasons.append(f"分时图呈现{intraday_pattern}形态")

        # 2. K线形态
        kline_pattern = stock_data.get("kline_pattern", "")
        good_kline_patterns = ["W底", "头肩底", "突破整理", "均线多头"]

        if kline_pattern in good_kline_patterns:
            score += 10
            reasons.append(f"日K线呈现{kline_pattern}形态")

        return {"score": score, "reasons": reasons}

    def apply_selection_criteria(self, stock_data: Dict[str, Dict]) -> List[Dict]:
        """
        应用尾盘选股标准 v2.0
        """
        selected_stocks = []

        for code, data in stock_data.items():
            total_score = 0
            all_reasons = []

            # 1. 价格走势分析
            price_result = self.analyze_price_movement(data)
            price_score = price_result["score"] * self.weights["price_movement"] / 100
            total_score += price_score

            # 2. 成交量分析
            volume_result = self.analyze_volume(data)
            volume_score = volume_result["score"] * self.weights["volume_analysis"] / 100
            total_score += volume_score

            # 3. 资金流向分析
            capital_result = self.analyze_capital_flow(data)
            capital_score = capital_result["score"] * self.weights["capital_flow"] / 100
            total_score += capital_score

            # 4. 技术指标分析
            tech_result = self.analyze_technical_indicators(data)
            tech_score = tech_result["score"] * self.weights["technical_indicators"] / 100
            total_score += tech_score

            # 5. 形态分析
            pattern_result = self.analyze_pattern(data)
            pattern_score = pattern_result["score"] * self.weights["pattern_analysis"] / 100
            total_score += pattern_score

            # 汇总理由
            all_reasons.extend(price_result["reasons"])
            all_reasons.extend(volume_result["reasons"])
            all_reasons.extend(capital_result["reasons"])
            all_reasons.extend(tech_result["reasons"])
            all_reasons.extend(pattern_result["reasons"])

            # 最终评分（0-100）
            final_score = min(int(total_score), 100)

            if final_score >= 70:  # 合格线提高到70分
                stock_info = {
                    "code": code,
                    "name": data.get("name", f"股票{code}"),
                    "score": final_score,
                    "current_price": data.get("current_price", 0),
                    "change_percent": data.get("change_percent", 0),
                    "selection_reasons": all_reasons,
                    "analysis_details": {
                        "price_movement": price_result,
                        "volume_analysis": volume_result,
                        "capital_flow": capital_result,
                        "technical_indicators": tech_result,
                        "pattern_analysis": pattern_result
                    },
                    "selection_time": self.get_current_time().strftime("%Y-%m-%d %H:%M:%S"),
                    "selection_strategy": self.strategy_name,
                    "strategy_version": self.strategy_version
                }
                selected_stocks.append(stock_info)

        # 按评分排序
        selected_stocks.sort(key=lambda x: x["score"], reverse=True)

        return selected_stocks

    def calculate_tail_end_entry_points(self, stock: Dict) -> Dict:
        """
        计算尾盘进场点位 v2.0
        更保守的尾盘进场策略
        """
        current_price = stock["current_price"]

        # 基于评分调整进场策略
        score = stock["score"]

        if score >= 90:  # 优质股票
            entry_points = {
                "激进进场": round(current_price * 0.995, 2),   # 下跌0.5%
                "稳健进场": round(current_price * 0.985, 2),   # 下跌1.5%
                "保守进场": round(current_price * 0.975, 2),   # 下跌2.5%
                "尾盘追涨": round(current_price * 1.005, 2)    # 上涨0.5%
            }
            stop_loss = round(current_price * 0.94, 2)  # 止损6%
        elif score >= 80:  # 良好股票
            entry_points = {
                "激进进场": round(current_price * 0.99, 2),    # 下跌1%
                "稳健进场": round(current_price * 0.97, 2),    # 下跌3%
                "保守进场": round(current_price * 0.95, 2),    # 下跌5%
                "尾盘追涨": round(current_price * 1.01, 2)     # 上涨1%
            }
            stop_loss = round(current_price * 0.92, 2)  # 止损8%
        else:  # 一般股票（70-79分）
            entry_points = {
                "激进进场": round(current_price * 0.98, 2),    # 下跌2%
                "稳健进场": round(current_price * 0.96, 2),    # 下跌4%
                "保守进场": round(current_price * 0.94, 2),    # 下跌6%
                "尾盘追涨": round(current_price * 1.02, 2)     # 上涨2%
            }
            stop_loss = round(current_price * 0.90, 2)  # 止损10%

        # 止盈点位
        take_profit = [
            round(current_price * 1.08, 2),  # 第一止盈8%
            round(current_price * 1.15, 2)   # 第二止盈15%
        ]

        # 风险收益比
        risk = current_price - stop_loss
        reward = take_profit[0] - current_price
        risk_reward_ratio = round(reward / risk, 2) if risk > 0 else 0

        return {
            "entry_points": entry_points,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "risk_reward_ratio": risk_reward_ratio,
            "position_suggestion": self.get_position_suggestion(score, risk_reward_ratio)
        }

    def get_position_suggestion(self, score: int, risk_reward_ratio: float) -> str:
        """获取仓位建议"""
        if score >= 90 and risk_reward_ratio >= 2:
            return "重仓（不超过总资金的30%）"
        elif score >= 80 and risk_reward_ratio >= 1.5:
            return "中等仓位（不超过总资金的20%）"
        elif score >= 70 and risk_reward_ratio >= 1:
            return "轻仓（不超过总资金的10%）"
        else:
            return "观察或放弃"

    def generate_detailed_report(self, selected_stocks: List[Dict]) -> str:
        """生成详细报告"""
        report_lines = []

        report_lines.append("# 尾盘选股策略详细报告 v2.0")
        report_lines.append(f"## 生成时间: {self.get_current_time().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"## 策略版本: {self.strategy_name} {self.strategy_version}")
        report_lines.append(f"## 选股时间窗口: {self.selection_time}")
        report_lines.append(f"## 策略权重: {json.dumps(self.weights, ensure_ascii=False)}")
        report_lines.append("")

        if not selected_stocks:
            report_lines.append("## 选股结果: 无符合条件的股票")
            return "\n".join(report_lines)

        report_lines.append(f"## 选股结果: 共筛选出 {len(selected_stocks)} 只股票")
        report_lines.append("")

        for i, stock in enumerate(selected_stocks[:10], 1):  # 只显示前10只
            risk_data = self.calculate_tail_end_entry_points(stock)

            report_lines.append(f"### {i}. {stock['name']} ({stock['code']})")
            report_lines.append(f"- **综合评分**: {stock['score']}/100")
            report_lines.append(f"- **当前价格**: {stock['current_price']:.2f}元")
            report_lines.append(f"- **今日涨跌**: {stock['change_percent']:.2f}%")
            report_lines.append(f"- **仓位建议**: {risk_data['position_suggestion']}")
            report_lines.append("")

            # 各维度评分
            details = stock['analysis_details']
            report_lines.append("#### 各维度评分:")
            for category, result in details.items():
                weight = self.weights.get(category, 0)
                actual_score = result["score"] * weight / 100
                report_lines.append(f"  - {category}: {result['score']}分 × {weight}% = {actual_score:.1f}分")

            report_lines.append("")
            report_lines.append("#### 进场点位建议:")
            for entry_type, price in risk_data["entry_points"].items():
                diff_percent = (price - stock['current_price']) / stock['current_price'] * 100
                direction = "上涨" if diff_percent > 0 else "下跌"
                report_lines.append(f"  - **{entry_type}**: {price:.2f}元 ({direction}{abs(diff_percent):.1f}%)")

            report_lines.append("")
            report_lines.append("#### 风险控制:")
            report_lines.append(f"  - **止损位**: {risk_data['stop_loss']:.2f}元 (下跌{((stock['current_price'] - risk_data['stop_loss']) / stock['current_price'] * 100):.1f}%)")
            report_lines.append(f
