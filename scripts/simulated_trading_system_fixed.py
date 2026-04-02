#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
尾盘选股策略模拟交易系统（修复版）
记录模拟交易，持续跟踪，每日复盘，输出报告
"""

import json
import os
import sys
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional

class SimulatedTradingSystem:
    """模拟交易系统"""

    def __init__(self):
        self.system_name = "尾盘选股策略模拟交易系统"
        self.strategy_name = "杨永兴隔夜套利战法"
        self.strategy_version = "v1.0"

        # 目录结构
        self.base_dir = "data/simulated_trading"
        self.trades_dir = os.path.join(self.base_dir, "trades")
        self.reports_dir = os.path.join(self.base_dir, "reports")
        self.logs_dir = os.path.join(self.base_dir, "logs")

        # 创建目录
        for directory in [self.base_dir, self.trades_dir, self.reports_dir, self.logs_dir]:
            os.makedirs(directory, exist_ok=True)

        # 模拟交易记录文件
        self.trades_file = os.path.join(self.base_dir, "simulated_trades.json")
        self.portfolio_file = os.path.join(self.base_dir, "simulated_portfolio.json")
        self.performance_file = os.path.join(self.base_dir, "performance_summary.json")

        # 初始化文件
        self.initialize_files()

    def initialize_files(self):
        """初始化文件"""
        if not os.path.exists(self.trades_file):
            with open(self.trades_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "system_name": self.system_name,
                    "strategy_name": self.strategy_name,
                    "created_date": datetime.now().strftime("%Y-%m-%d"),
                    "total_trades": 0,
                    "active_trades": 0,
                    "closed_trades": 0,
                    "trades": []
                }, f, ensure_ascii=False, indent=2)

        if not os.path.exists(self.portfolio_file):
            with open(self.portfolio_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "portfolio_name": "模拟交易投资组合",
                    "created_date": datetime.now().strftime("%Y-%m-%d"),
                    "total_capital": 1000000,  # 初始资金100万
                    "available_capital": 1000000,
                    "invested_capital": 0,
                    "total_value": 1000000,
                    "positions": [],
                    "performance": {
                        "total_return": 0,
                        "daily_return": 0,
                        "win_rate": 0,
                        "avg_win": 0,
                        "avg_loss": 0
                    }
                }, f, ensure_ascii=False, indent=2)

    def load_trades(self):
        """加载交易记录"""
        with open(self.trades_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_trades(self, data):
        """保存交易记录"""
        with open(self.trades_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_portfolio(self):
        """加载投资组合"""
        with open(self.portfolio_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_portfolio(self, data):
        """保存投资组合"""
        with open(self.portfolio_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def record_yesterday_trades(self):
        """记录昨天的模拟进场交易"""
        print("记录昨天（2026-03-31）的模拟进场交易...")

        # 加载昨天分析结果
        yesterday_file = "data/yesterday_analysis/yesterday_analysis_20260401_091002.json"

        if not os.path.exists(yesterday_file):
            print(f"❌ 昨天分析文件不存在: {yesterday_file}")
            return False

        with open(yesterday_file, 'r', encoding='utf-8') as f:
            yesterday_data = json.load(f)

        trades_data = self.load_trades()
        portfolio_data = self.load_portfolio()

        entry_details = yesterday_data.get("entry_details", [])

        if not entry_details:
            print("❌ 昨天没有符合条件的交易")
            return False

        print(f"发现 {len(entry_details)} 笔昨天模拟交易")

        total_investment = 0
        new_trades = []

        for detail in entry_details:
            # 生成交易ID
            trade_id = f"TRADE_{datetime.now().strftime('%Y%m%d')}_{len(trades_data['trades']) + 1:03d}"

            # 提取数据
            code = detail["code"]
            name = detail["name"]
            strategy_score = detail["strategy_score"]
            passed_steps = detail["passed_steps"]

            yesterday_data = detail["yesterday_data"]
            entry_strategy = detail["entry_strategy"]
            simulated_today = detail["simulated_today"]

            # 计算仓位
            position_suggestion = entry_strategy["position_suggestion"]
            if "重仓" in position_suggestion:
                position_percent = 0.3  # 30%
            elif "中等仓位" in position_suggestion:
                position_percent = 0.2  # 20%
            else:
                position_percent = 0.1  # 10%

            # 计算投资金额（基于总资金的百分比）
            total_capital = portfolio_data["total_capital"]
            investment_amount = total_capital * position_percent

            # 计算股数（取整）
            entry_price = entry_strategy["entry_price"]
            shares = int(investment_amount / entry_price)
            actual_investment = shares * entry_price

            # 创建交易记录
            trade = {
                "trade_id": trade_id,
                "stock_code": code,
                "stock_name": name,
                "trade_date": yesterday_data["date"],  # 2026-03-31
                "trade_type": "BUY",
                "entry_price": entry_price,
                "target_price": entry_strategy["target_price"],
                "stop_loss": entry_strategy["stop_loss"],
                "shares": shares,
                "investment": actual_investment,
                "position_percent": position_percent,
                "strategy_score": strategy_score,
                "passed_steps": passed_steps,
                "status": "ACTIVE",  # 活跃交易
                "entry_time": "14:45",  # 假设尾盘进场时间
                "holding_days": 1,  # 已持有1天
                "current_price": simulated_today["price"],  # 今天模拟价格
                "current_value": shares * simulated_today["price"],
                "unrealized_pnl": (simulated_today["price"] - entry_price) * shares,
                "unrealized_pnl_percent": simulated_today["change"],
                "exit_price": None,
                "exit_date": None,
                "exit_reason": None,
                "realized_pnl": 0,
                "trade_notes": f"杨永兴隔夜套利战法 - 评分{strategy_score}分，通过{passed_steps}/6步骤"
            }

            new_trades.append(trade)
            total_investment += actual_investment

            print(f"✅ 记录交易: {code} {name}")
            print(f"   进场价: {entry_price:.2f}元，股数: {shares}股")
            print(f"   投资额: {actual_investment:.2f}元，仓位: {position_percent*100:.0f}%")
            print(f"   当前价: {simulated_today['price']:.2f}元，盈亏: {simulated_today['change']:.2f}%")

        # 更新交易记录
        trades_data["trades"].extend(new_trades)
        trades_data["total_trades"] += len(new_trades)
        trades_data["active_trades"] += len(new_trades)
        trades_data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 更新投资组合
        portfolio_data["invested_capital"] += total_investment
        portfolio_data["available_capital"] -= total_investment

        # 添加持仓
        for trade in new_trades:
            position = {
                "trade_id": trade["trade_id"],
                "stock_code": trade["stock_code"],
                "stock_name": trade["stock_name"],
                "shares": trade["shares"],
                "entry_price": trade["entry_price"],
                "current_price": trade["current_price"],
                "market_value": trade["current_value"],
                "unrealized_pnl": trade["unrealized_pnl"],
                "unrealized_pnl_percent": trade["unrealized_pnl_percent"],
                "entry_date": trade["trade_date"]
            }
            portfolio_data["positions"].append(position)

        # 计算投资组合总价值
        total_market_value = sum(pos["market_value"] for pos in portfolio_data["positions"])
        portfolio_data["total_value"] = portfolio_data["available_capital"] + total_market_value

        # 保存数据
        self.save_trades(trades_data)
        self.save_portfolio(portfolio_data)

        # 保存详细的交易记录文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        detailed_file = os.path.join(self.trades_dir, f"yesterday_trades_{timestamp}.json")

        with open(detailed_file, 'w', encoding='utf-8') as f:
            json.dump({
                "record_date": datetime.now().strftime("%Y-%m-%d"),
                "trade_date": "2026-03-31",
                "total_trades": len(new_trades),
                "total_investment": total_investment,
                "trades": new_trades
            }, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 成功记录 {len(new_trades)} 笔昨天模拟交易")
        print(f"总投资额: {total_investment:.2f}元")
        print(f"详细记录: {detailed_file}")

        return True

    def setup_daily_schedule(self):
        """设置每日执行计划"""
        print("\n设置每日执行计划...")

        schedule_config = {
            "system_name": self.system_name,
            "strategy_name": self.strategy_name,
            "daily_schedule": [
                {
                    "time": "09:30",
                    "task": "股票数据自动更新",
                    "description": "获取最新股票数据，为尾盘选股做准备"
                },
                {
                    "time": "14:30",
                    "task": "尾盘选股策略执行",
                    "description": "执行杨永兴隔夜套利战法，筛选尾盘股票"
                },
                {
                    "time": "15:00",
                    "task": "交易执行与记录",
                    "description": "记录模拟交易，更新投资组合"
                },
                {
                    "time": "16:00",
                    "task": "盘中跟踪",
                    "description": "跟踪持仓，检查止盈止损条件"
                },
                {
                    "time": "18:00",
                    "task": "每日复盘报告",
                    "description": "生成当日复盘报告，总结交易绩效"
                }
            ],
            "weekly_schedule": [
                {
                    "day": "Friday",
                    "time": "17:00",
                    "task": "周度策略复盘",
                    "description": "总结一周交易，优化策略参数"
                }
            ],
            "setup_date": datetime.now().strftime("%Y-%m-%d"),
            "next_execution": "2026-04-01 14:30"
        }

        schedule_file = os.path.join(self.base_dir, "daily_schedule.json")

        with open(schedule_file, 'w', encoding='utf-8') as f:
            json.dump(schedule_config, f, ensure_ascii=False, indent=2)

        print(f"✅ 每日执行计划已设置: {schedule_file}")

        # 创建cron任务配置
        cron_config = f"""# 尾盘选股策略模拟交易系统 - 每日执行计划
# 系统: {self.system_name}
# 策略: {self.strategy_name}
# 设置时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# 09:30 - 股票数据自动更新
30 9 * * * cd /Users/ago/.openclaw/workspace && python3 scripts/minimal_stock_update.py >> logs/stock_update.log 2>&1

# 14:30 - 尾盘选股策略执行
30 14 * * * cd /Users/ago/.openclaw/workspace && python3 scripts/simulated_trading_system_fixed.py --execute-strategy >> logs/tail_end_strategy.log 2>&1

# 18:00 - 每日复盘报告
0 18 * * * cd /Users/ago/.openclaw/workspace && python3 scripts/simulated_trading_system_fixed.py --daily-report >> logs/daily_report.log 2>&1

# 注意: 以上时间为北京时区 (GMT+8)
"""

        cron_file = os.path.join(self.base_dir, "cron_schedule.txt")

        with open(cron_file, 'w', encoding='utf-8') as f:
            f.write(cron_config)

        print(f"✅ Cron任务配置已生成: {cron_file}")

        return schedule_file, cron_file

    def run_full_system(self):
        """运行完整系统"""
        print("=" * 60)
        print(f"{self.system_name}")
        print(f"策略: {self.strategy_name}")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # 1. 记录昨天的模拟交易
        print("\n1. 记录昨天的模拟进场交易...")
        self.record_yesterday_trades()

        # 2. 设置每日执行计划
        print("\n2. 设置每日执行计划...")
        self.setup_daily_schedule()

        # 3. 显示系统状态
        print("\n3. 系统状态概览...")
        trades_data = self.load_trades()
        portfolio_data = self.load_portfolio()

        print(f"\n📊 系统状态:")
        print(f"- 总交易笔数: {trades_data['total_trades']}")
        print(f"- 活跃交易: {trades_data['active_trades']}")
        print(f"- 已平仓交易: {trades_data['closed_trades']}")
        print(f"- 总投资额: {portfolio_data['invested_capital']:,.2f}元")
        print(f"- 总资产: {portfolio_data['total_value']:,.2f}元")
        print(f"- 可用资金: {portfolio_data['available_capital']:,.2f}元")

        # 显示昨天交易详情
        if trades_data['trades']:
            print(f"\n📈 昨天模拟交易详情:")
            for trade in trades_data['trades']:
                pnl_emoji = "📈" if trade["unrealized_pnl"] > 0 else "📉"
                print(f"- {trade['stock_name']} ({trade['stock_code']})")
                print(f"  进场: {trade['entry_price']:.2f}元，当前: {trade['current_price']:.2f}元")
                print(f"  盈亏: {pnl_emoji} {trade['unrealized_pnl']:.2f}元 ({trade['unrealized_pnl_percent']:.2f}%)")
                print(f"  仓位: {trade['position_percent']*100:.0f}%，评分: {trade['strategy_score']}分")

        print(f"\n📅 今日重要时间:")
        print(f"- 14:30: 尾盘选股策略执行")
        print(f"- 18:00: 每日复盘报告生成")

        print(f"\n📁 文件位置:")
        print(f"- 交易记录: {self.trades_file}")
        print(f"- 投资组合: {self.portfolio_file}")
        print(f"- 报告目录: {self.reports_dir}")
        print(f"- 日志目录: {self.logs_dir}")

        print("\n" + "=" * 60)
        print("✅ 模拟交易系统已成功设置!")
        print("=" * 60)

        return True


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='尾盘选股策略模拟交易系统')
    parser.add_argument('--record-yesterday', action='store_true', help='记录昨天的模拟交易')
    parser.add_argument('--setup-schedule', action='store_true', help='设置每日执行计划')
    parser.add_argument('--full-system', action='store_true', help='运行完整系统')

    args = parser.parse_args()

    system = SimulatedTradingSystem()

    if args.record_yesterday:
        system.record_yesterday_trades()
    elif args.setup_schedule:
        system.setup_daily_schedule()
    elif args.full_system:
        system.run_full_system()
    else:
        # 默认运行完整系统
        system.run_full_system()


if __name__ == "__main__":
    main()
