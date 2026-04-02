#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
杨永兴隔夜套利战法 - 尾盘选股策略（修复版）
基于OCR识别的图片内容实现
"""

import json
import os
import sys
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional

class YangYongxingOvernightStrategy:
    """杨永兴隔夜套利战法"""

    def __init__(self):
        self.strategy_name = "杨永兴隔夜套利战法"
        self.strategy_version = "v1.0"
        self.strategy_author = "杨永兴（短线快刀客）"
        self.strategy_performance = "16个月100万→1亿"
        self.selection_time = "14:30之后"
        self.output_dir = "data/yang_yongxing_strategy"

        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)

        # 策略核心原理（基于OCR识别内容）
        self.core_principles = {
            "核心理念": "不靠长线，不靠龙头，只靠一招隔夜套利，把T+1做成了T+0",
            "散户死穴": "早盘追高，盘中跳水，T+1制度下跑都跑不掉，只能眼睁睁亏损",
            "核心解法": "尾盘战法14:30之后进场，当天风险已释放，主力底牌已亮出，直接过滤90%风险",
            "优势": "别人早盘冲锋接飞刀，你尾盘捡筹码，稳赢"
        }

        # 六大选股步骤（基于OCR识别）
        self.six_selection_steps = [
            {"step": 1, "name": "时间筛选", "description": "14:30之后进场", "criteria": "尾盘时段，风险已释放"},
            {"step": 2, "name": "涨跌幅筛选", "description": "3%~5%涨幅", "criteria": "适度上涨，有冲劲但不过热"},
            {"step": 3, "name": "资金流向筛选", "description": "主力资金净流入", "criteria": "有大单资金持续流入"},
            {"step": 4, "name": "成交量筛选", "description": "量比>1.7", "criteria": "放量明显，有资金关注"},
            {"step": 5, "name": "市值筛选", "description": "市值<200亿", "criteria": "中小盘股，弹性好"},
            {"step": 6, "name": "技术形态筛选", "description": "5%~10%涨幅空间", "criteria": "有继续上涨的技术空间"}
        ]

    def get_current_time(self):
        """获取当前时间"""
        return datetime.now()

    def is_yang_yongxing_time(self, current_time=None):
        """判断是否是杨永兴战法的时间窗口"""
        if current_time is None:
            current_time = self.get_current_time()

        # 杨永兴战法时间：14:30之后
        strategy_start = current_time.replace(hour=14, minute=30, second=0, microsecond=0)

        return current_time >= strategy_start

    def apply_yang_yongxing_criteria(self, stock_data: Dict[str, Dict]) -> List[Dict]:
        """应用杨永兴隔夜套利战法选股标准"""
        selected_stocks = []

        for code, data in stock_data.items():
            score = 0
            reasons = []
            step_results = []

            # 步骤1: 时间窗口检查
            step1_score = 20 if self.is_yang_yongxing_time() else 0
            score += step1_score
            step_results.append({
                "step": 1, "name": "时间筛选", "score": step1_score,
                "passed": step1_score > 0, "reason": "尾盘时段执行" if step1_score > 0 else "非尾盘时段"
            })

            # 步骤2: 涨跌幅筛选 (3%~5%)
            change = data.get("change_percent", 0)
            if 3 <= change <= 5:
                step2_score = 20
                reasons.append(f"涨幅适中({change:.1f}%)，符合3%~5%要求")
            elif 2 <= change <= 6:
                step2_score = 15
                reasons.append(f"涨幅{change:.1f}%，接近理想区间")
            else:
                step2_score = 5
                reasons.append(f"涨幅{change:.1f}%，偏离理想区间")

            score += step2_score
            step_results.append({
                "step": 2, "name": "涨跌幅筛选", "score": step2_score,
                "passed": step2_score >= 15, "reason": reasons[-1]
            })

            # 步骤3: 资金流向筛选
            capital_flow = data.get("capital_flow_ratio", 0)
            if capital_flow > 0.1:
                step3_score = 25
                reasons.append(f"主力资金大幅净流入({capital_flow*100:.1f}%)")
            elif capital_flow > 0:
                step3_score = 20
                reasons.append(f"主力资金净流入({capital_flow*100:.1f}%)")
            else:
                step3_score = 5
                reasons.append("资金流向不理想")

            score += step3_score
            step_results.append({
                "step": 3, "name": "资金流向筛选", "score": step3_score,
                "passed": step3_score >= 20, "reason": reasons[-1]
            })

            # 步骤4: 量比筛选 (>1.7)
            volume_ratio = data.get("volume_ratio", 1.0)
            if volume_ratio > 1.7:
                step4_score = 15
                reasons.append(f"量比优秀({volume_ratio:.2f})，明显放量")
            elif volume_ratio > 1.5:
                step4_score = 12
                reasons.append(f"量比良好({volume_ratio:.2f})，温和放量")
            elif volume_ratio > 1.2:
                step4_score = 8
                reasons.append(f"量比适中({volume_ratio:.2f})")
            else:
                step4_score = 3
                reasons.append(f"量比偏低({volume_ratio:.2f})")

            score += step4_score
            step_results.append({
                "step": 4, "name": "成交量筛选", "score": step4_score,
                "passed": step4_score >= 12, "reason": reasons[-1]
            })

            # 步骤5: 市值筛选 (<200亿)
            market_cap = data.get("market_cap", 0)
            if market_cap < 100:
                step5_score = 10
                reasons.append(f"小盘股({market_cap:.1f}亿)，弹性好")
            elif market_cap < 200:
                step5_score = 8
                reasons.append(f"中小盘股({market_cap:.1f}亿)，符合要求")
            elif market_cap < 500:
                step5_score = 5
                reasons.append(f"中盘股({market_cap:.1f}亿)，略大")
            else:
                step5_score = 2
                reasons.append(f"大盘股({market_cap:.1f}亿)，不符合要求")

            score += step5_score
            step_results.append({
                "step": 5, "name": "市值筛选", "score": step5_score,
                "passed": step5_score >= 8, "reason": reasons[-1]
            })

            # 步骤6: 技术空间筛选 (5%~10%)
            tech_space = data.get("technical_space", 0)
            if 8 <= tech_space <= 12:
                step6_score = 10
                reasons.append(f"技术上涨空间优秀({tech_space:.1f}%)")
            elif 5 <= tech_space <= 15:
                step6_score = 8
                reasons.append(f"技术上涨空间良好({tech_space:.1f}%)")
            else:
                step6_score = 3
                reasons.append(f"技术空间一般({tech_space:.1f}%)")

            score += step6_score
            step_results.append({
                "step": 6, "name": "技术形态筛选", "score": step6_score,
                "passed": step6_score >= 8, "reason": reasons[-1]
            })

            # 最终评分
            final_score = min(int(score), 100)
            passed_steps = sum(1 for step in step_results if step["passed"])

            if passed_steps >= 4 and final_score >= 70:
                stock_info = {
                    "code": code, "name": data.get("name", f"股票{code}"),
                    "score": final_score, "passed_steps": passed_steps,
                    "current_price": data.get("current_price", 0),
                    "change_percent": data.get("change_percent", 0),
                    "selection_reasons": reasons, "step_results": step_results,
                    "strategy_name": self.strategy_name,
                    "strategy_version": self.strategy_version,
                    "selection_time": self.get_current_time().strftime("%Y-%m-%d %H:%M:%S"),
                    "overnight_strategy": True
                }
                selected_stocks.append(stock_info)

        selected_stocks.sort(key=lambda x: x["score"], reverse=True)
        return selected_stocks

    def calculate_overnight_entry_points(self, stock: Dict) -> Dict:
        """计算隔夜套利进场点位"""
        current_price = stock["current_price"]
        score = stock["score"]

        if score >= 90:
            entry_price = round(current_price * 1.005, 2)
            target_price = round(current_price * 1.08, 2)
            stop_loss = round(current_price * 0.97, 2)
            position = "重仓（不超过30%）"
        elif score >= 80:
            entry_price = round(current_price * 1.00, 2)
            target_price = round(current_price * 1.06, 2)
            stop_loss = round(current_price * 0.96, 2)
            position = "中等仓位（不超过20%）"
        else:
            entry_price = round(current_price * 0.995, 2)
            target_price = round(current_price * 1.05, 2)
            stop_loss = round(current_price * 0.95, 2)
            position = "轻仓（不超过10%）"

        return {
            "entry_strategy": "尾盘隔夜套利",
            "entry_price": entry_price,
            "entry_condition": f"达到{entry_price:.2f}元时进场",
            "target_price": target_price,
            "target_gain": round((target_price - current_price) / current_price * 100, 2),
            "stop_loss": stop_loss,
            "max_loss": round((current_price - stop_loss) / current_price * 100, 2),
            "risk_reward_ratio": round((target_price - entry_price) / (entry_price - stop_loss), 2),
            "position_suggestion": position,
            "holding_period": "隔夜（今日尾盘进场，明日冲高卖出）",
            "exit_strategy": "次日冲高时卖出，不贪不恋"
        }

    def generate_report(self, selected_stocks: List[Dict]) -> str:
        """生成杨永兴战法报告"""
        report_lines = []

        report_lines.append("# 杨永兴隔夜套利战法 - 尾盘选股报告")
        report_lines.append(f"## 生成时间: {self.get_current_time().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"## 策略作者: {self.strategy_author}")
        report_lines.append(f"## 历史业绩: {self.strategy_performance}")
        report_lines.append("")

        report_lines.append("## 一、核心理念")
        for key, value in self.core_principles.items():
            report_lines.append(f"- **{key}**: {value}")
        report_lines.append("")

        report_lines.append("## 二、六大选股步骤")
        for step in self.six_selection_steps:
            report_lines.append(f"{step['step']}. **{step['name']}**: {step['description']} - {step['criteria']}")
        report_lines.append("")

        if not selected_stocks:
            report_lines.append("## 三、选股结果: 无符合条件的股票")
            return "\n".join(report_lines)

        report_lines.append(f"## 三、选股结果: 共筛选出 {len(selected_stocks)} 只股票")
        report_lines.append("")

        for i, stock in enumerate(selected_stocks[:5], 1):
            entry_data = self.calculate_overnight_entry_points(stock)

            report_lines.append(f"### {i}. {stock['name']} ({stock['code']})")
            report_lines.append(f"- **综合评分**: {stock['score']}/100")
            report_lines.append(f"- **通过步骤**: {stock['passed_steps']}/6")
            report_lines.append(f"- **当前价格**: {stock['current_price']:.2f}元")
            report_lines.append(f"- **今日涨跌**: {stock['change_percent']:.2f}%")
            report_lines.append("")

            report_lines.append("#### 进场策略:")
            report_lines.append(f"- **策略**: {entry_data['entry_strategy']}")
            report_lines.append(f"- **进场价**: {entry_data['entry_price']:.2f}元")
            report_lines.append(f"- **目标价**: {entry_data['target_price']:.2f}元 (涨幅{entry_data['target_gain']:.1f}%)")
            report_lines.append(f"- **止损价**: {entry_data['stop_loss']:.2f}元")
            report_lines.append(f"- **仓位建议**: {entry_data['position_suggestion']}")
            report_lines.append("")

            report_lines.append("#### 选股步骤详情:")
            for step_result in stock["step_results"]:
                status = "✅" if step_result["passed"] else "❌"
                report_lines.append(f"{status} **步骤{step_result['step']} {step_result['name']}**: {step_result['reason']}")
            report_lines.append("")

            report_lines.append("---")
            report_lines.append("")

        return "\n".join(report_lines)

    def run_selection(self):
        """运行杨永兴战法选股"""
        print(f"开始执行杨永兴隔夜套利战法")
        print(f"策略作者: {self.strategy_author}")
        print(f"历史业绩: {self.strategy_performance}")
        print("=" * 60)

        if not self.is_yang_yongxing_time():
            print(f"当前时间不在杨永兴战法时间窗口内")
            return None

        # 模拟股票数据
        stock_data = {}
        for i in range(1, 11):
            code = f"600{i:03d}"
            stock_data[code] = {
                "code": code, "name": f"示例股{i}",
                "current_price": np.random.uniform(10, 50),
                "change_percent": np.random.uniform(2, 6),
                "capital_flow_ratio": np.random.uniform(0.05, 0.25),
                "volume_ratio": np.random.uniform(1.5, 2.5),
                "market_cap": np.random.uniform(50, 300),
                "technical_space": np.random.uniform(5, 12)
            }

        selected_stocks = self.apply_yang_yongxing_criteria(stock_data)

        # 保存结果
        timestamp = self.get_current_time().strftime("%Y%m%d_%H%M%S")
        json_path = os.path.join(self.output_dir, f"selection_{timestamp}.json")
        report_path = os.path.join(self.output_dir, f"report_{timestamp}.md")

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({"stocks": selected_stocks}, f, ensure_ascii=False, indent=2)

        report_content = self.generate_report(selected_stocks)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"选股完成: {len(selected_stocks)} 只股票")
        print(f"报告已保存: {report_path}")

        return {"selected_stocks": selected_stocks, "report_path": report_path}


def main():
    """主函数"""
    strategy = YangYongxingOvernightStrategy()
    result = strategy.run_selection()

    if result:
        print("\n✅ 杨永兴隔夜套利战法执行完成！")
    else:
        print("\n❌ 不在执行时间窗口内")


if __name__ == "__main__":
    main()
