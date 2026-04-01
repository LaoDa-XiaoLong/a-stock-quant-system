        # 生成报告
        report_lines = []
        report_lines.append("# 尾盘选股策略每日复盘报告")
        report_lines.append(f"## 报告日期: {datetime.now().strftime('%Y-%m-%d')}")
        report_lines.append(f"## 生成时间: 18:00")
        report_lines.append(f"## 策略名称: {self.strategy_name}")
        report_lines.append(f"## 策略版本: {self.strategy_version}")
        report_lines.append("")
        
        report_lines.append("## 一、今日策略执行情况")
        report_lines.append(f"- **执行时间**: 14:30")
        report_lines.append(f"- **选股结果**: 已执行，结果见今日选股报告")
        report_lines.append(f"- **交易记录**: 已更新")
        report_lines.append("")
        
        report_lines.append("## 二、投资组合概览")
        report_lines.append(f"- **初始资金**: 1,000,000元")
        report_lines.append(f"- **当前总资产**: {total_value:,.2f}元")
        report_lines.append(f"- **已投资金额**: {total_investment:,.2f}元")
        report_lines.append(f"- **可用资金**: {portfolio_data['available_capital']:,.2f}元")
        report_lines.append(f"- **总收益率**: {total_return:.2f}%")
        report_lines.append("")
        
        report_lines.append("## 三、持仓情况")
        if active_trades:
            report_lines.append(f"### 活跃持仓 ({len(active_trades)} 笔)")
            for trade in active_trades:
                pnl_percent = trade["unrealized_pnl_percent"]
                pnl_emoji = "📈" if pnl_percent > 0 else "📉"
                report_lines.append(f"#### {trade['stock_name']} ({trade['stock_code']})")
                report_lines.append(f"- **持仓数量**: {trade['shares']}股")
                report_lines.append(f"- **进场价格**: {trade['entry_price']:.2f}元")
                report_lines.append(f"- **当前价格**: {trade['current_price']:.2f}元")
                report_lines.append(f"- **目标价格**: {trade['target_price']:.2f}元")
                report_lines.append(f"- **止损价格**: {trade['stop_loss']:.2f}元")
                report_lines.append(f"- **浮动盈亏**: {pnl_emoji} {trade['unrealized_pnl']:.2f}元 ({pnl_percent:.2f}%)")
                report_lines.append(f"- **持有天数**: {trade['holding_days']}天")
                report_lines.append("")
        else:
            report_lines.append("### 活跃持仓: 无")
            report_lines.append("")
        
        report_lines.append("## 四、交易绩效统计")
        report_lines.append(f"- **总交易笔数**: {trades_data['total_trades']}笔")
        report_lines.append(f"- **活跃交易**: {len(active_trades)}笔")
        report_lines.append(f"- **已平仓交易**: {len(closed_trades)}笔")
        report_lines.append(f"- **胜率**: {win_rate:.1f}%")
        report_lines.append(f"- **平均盈利**: {avg_win:.2f}元" if winning_trades else "- **平均盈利**: 无盈利交易")
        report_lines.append(f"- **平均亏损**: {avg_loss:.2f}元" if losing_trades else "- **平均亏损**: 无亏损交易")
        report_lines.append("")
        
        if closed_trades:
            report_lines.append("### 最近平仓交易")
            for trade in closed_trades[-5:]:  # 最近5笔
                pnl_emoji = "📈" if trade["realized_pnl"] > 0 else "📉"
                report_lines.append(f"- {trade['stock_name']} ({trade['stock_code']}): {pnl_emoji} {trade['realized_pnl']:.2f}元 ({trade['exit_reason']})")
            report_lines.append("")
        
        report_lines.append("## 五、今日操作总结")
        report_lines.append("1. **策略执行**: 按计划在14:30执行尾盘选股")
        report_lines.append("2. **交易跟踪**: 持续监控持仓，检查止盈止损")
        report_lines.append("3. **风险控制**: 严格执行止损纪律")
        report_lines.append("4. **仓位管理**: 控制单只股票仓位不超过30%")
        report_lines.append("")
        
        report_lines.append("## 六、明日计划")
        report_lines.append("1. **继续跟踪**: 监控活跃持仓，执行止盈止损")
        report_lines.append("2. **策略执行**: 明日14:30继续执行尾盘选股")
        report_lines.append("3. **数据更新**: 更新股票数据，优化选股模型")
        report_lines.append("4. **复盘学习**: 总结今日经验，优化策略参数")
        report_lines.append("")
        
        report_lines.append("## 七、风险提示")
        report_lines.append("1. **市场风险**: 股市有风险，投资需谨慎")
        report_lines.append("2. **策略风险**: 历史表现不代表未来收益")
        report_lines.append("3. **执行风险**: 需要严格按时执行策略")
        report_lines.append("4. **数据风险**: 依赖准确的市场数据")
        report_lines.append("5. **隔夜风险**: 尾盘策略存在隔夜不确定性")
        
        report_content = "\n".join(report_lines)
        
        # 保存报告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(self.reports_dir, f"daily_report_{timestamp}.md")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # 保存绩效数据
        performance_data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_value": total_value,
            "total_return": total_return,
            "active_trades": len(active_trades),
            "closed_trades": len(closed_trades),
            "win_rate": win_rate,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "total_investment": total_investment,
            "available_capital": portfolio_data["available_capital"]
        }
        
        # 更新绩效文件
        if os.path.exists(self.performance_file):
            with open(self.performance_file, 'r', encoding='utf-8') as f:
                performance_history = json.load(f)
        else:
            performance_history = {"history": []}
        
        performance_history["history"].append(performance_data)
        
        with open(self.performance_file, 'w', encoding='utf-8') as f:
            json.dump(performance_history, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 每日复盘报告已生成: {report_file}")
        print(f"绩效数据已更新: {self.performance_file}")
        
        return report_file
    
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
30 14 * * * cd /Users/ago/.openclaw/workspace && python3 scripts/simulated_trading_system.py --execute-strategy >> logs/tail_end_strategy.log 2>&1

# 18:00 - 每日复盘报告
0 18 * * * cd /Users/ago/.openclaw/workspace && python3 scripts/simulated_trading_system.py --daily-report >> logs/daily_report.log 2>&1

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
        
        # 2. 执行今天的尾盘选股策略（如果时间合适）
        print("\n2. 执行今天的尾盘选股策略...")
        current_time = datetime.now()
        strategy_time = current_time.replace(hour=14, minute=30, second=0, microsecond=0)
        
        if current_time >= strategy_time:
            self.execute_today_strategy()
        else:
            time_diff = (strategy_time - current_time).total_seconds() / 60
            print(f"⏳ 还未到执行时间，距离14:30还有 {time_diff:.1f} 分钟")
        
        # 3. 跟踪活跃交易
        print("\n3. 跟踪活跃交易...")
        self.track_active_trades()
        
        # 4. 生成每日复盘报告（如果时间合适）
        print("\n4. 生成每日复盘报告...")
        report_time = current_time.replace(hour=18, minute=0, second=0, microsecond=0)
        
        if current_time >= report_time:
            self.generate_daily_report()
        else:
            time_diff = (report_time - current_time).total_seconds() / 60
            print(f"⏳ 还未到报告时间，距离18:00还有 {time_diff:.1f} 分钟")
        
        # 5. 设置每日执行计划
        print("\n5. 设置每日执行计划...")
        self.setup_daily_schedule()
        
        print("\n" + "=" * 60)
        print("✅ 模拟交易系统已成功设置!")
        print("=" * 60)
        
        # 显示系统状态
        trades_data = self.load_trades()
        portfolio_data = self.load_portfolio()
        
        print(f"\n📊 系统状态:")
        print(f"- 总交易笔数: {trades_data['total_trades']}")
        print(f"- 活跃交易: {trades_data['active_trades']}")
        print(f"- 已平仓交易: {trades_data['closed_trades']}")
        print(f"- 总投资额: {portfolio_data['invested_capital']:,.2f}元")
        print(f"- 总资产: {portfolio_data['total_value']:,.2f}元")
        print(f"- 可用资金: {portfolio_data['available_capital']:,.2f}元")
        
        print(f"\n📅 今日重要时间:")
        print(f"- 14:30: 尾盘选股策略执行")
        print(f"- 18:00: 每日复盘报告生成")
        
        print(f"\n📁 文件位置:")
        print(f"- 交易记录: {self.trades_file}")
        print(f"- 投资组合: {self.portfolio_file}")
        print(f"- 报告目录: {self.reports_dir}")
        print(f"- 日志目录: {self.logs_dir}")
        
        return True


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='尾盘选股策略模拟交易系统')
    parser.add_argument('--record-yesterday', action='store_true', help='记录昨天的模拟交易')
    parser.add_argument('--execute-strategy', action='store_true', help='执行今天的尾盘选股策略')
    parser.add_argument('--track-trades', action='store_true', help='跟踪活跃交易')
    parser.add_argument('--daily-report', action='store_true', help='生成每日复盘报告')
    parser.add_argument('--setup-schedule', action='store_true', help='设置每日执行计划')
    parser.add_argument('--full-system', action='store_true', help='运行完整系统')
    
    args = parser.parse_args()
    
    system = SimulatedTradingSystem()
    
    if args.record_yesterday:
        system.record_yesterday_trades()
    elif args.execute_strategy:
        system.execute_today_strategy()
    elif args.track_trades:
        system.track_active_trades()
    elif args.daily_report:
        system.generate_daily_report()
    elif args.setup_schedule:
        system.setup_daily_schedule()
    elif args.full_system:
        system.run_full_system()
    else:
        # 默认运行完整系统
        system.run_full_system()


if __name__ == "__main__":
    main()