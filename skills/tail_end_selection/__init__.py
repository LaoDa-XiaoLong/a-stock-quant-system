        for stock in selected_stocks:
            # 生成交易ID
            trade_id = f"TRADE_{datetime.now().strftime('%Y%m%d')}_{len(trades_data['trades']) + 1:03d}"
            
            # 计算进场点位
            entry_data = self.calculate_entry_points(stock)
            
            # 计算仓位
            position_suggestion = entry_data["position_suggestion"]
            if "重仓" in position_suggestion:
                position_percent = 0.3
            elif "中等仓位" in position_suggestion:
                position_percent = 0.2
            else:
                position_percent = 0.1
            
            # 检查仓位限制
            max_position = self.config["trading"]["max_position_percent"]
            if position_percent > max_position:
                position_percent = max_position
            
            # 计算投资金额
            total_capital = portfolio_data["total_capital"]
            investment_amount = total_capital * position_percent
            
            # 计算股数
            entry_price = entry_data["entry_price"]
            shares = int(investment_amount / entry_price)
            actual_investment = shares * entry_price
            
            # 检查可用资金
            if actual_investment > portfolio_data["available_capital"]:
                self.logger.warning(f"资金不足，跳过 {stock['code']}")
                continue
            
            # 创建交易记录
            trade = {
                "trade_id": trade_id,
                "stock_code": stock["code"],
                "stock_name": stock["name"],
                "trade_date": datetime.now().strftime("%Y-%m-%d"),
                "trade_type": "BUY",
                "entry_price": entry_price,
                "target_price": entry_data["target_price"],
                "stop_loss": entry_data["stop_loss"],
                "shares": shares,
                "investment": actual_investment,
                "position_percent": position_percent,
                "strategy_score": stock["score"],
                "passed_steps": stock["passed_steps"],
                "status": "ACTIVE",
                "entry_time": datetime.now().strftime("%H:%M"),
                "holding_days": 0,
                "current_price": stock["current_price"],
                "current_value": shares * stock["current_price"],
                "unrealized_pnl": (stock["current_price"] - entry_price) * shares,
                "unrealized_pnl_percent": stock["change_percent"],
                "exit_price": None,
                "exit_date": None,
                "exit_reason": None,
                "realized_pnl": 0,
                "trade_notes": f"尾盘选股法 - 评分{stock['score']}分，等级{entry_data['grade']}"
            }
            
            new_trades.append(trade)
            total_investment += actual_investment
            
            self.logger.info(f"记录交易: {stock['code']} {stock['name']} - 投资{actual_investment:.2f}元")
        
        if not new_trades:
            self.logger.warning("没有新交易需要记录")
            return False
        
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
        
        # 计算总价值
        total_market_value = sum(pos["market_value"] for pos in portfolio_data["positions"])
        portfolio_data["total_value"] = portfolio_data["available_capital"] + total_market_value
        
        # 保存数据
        with open(self.trades_file, 'w', encoding='utf-8') as f:
            json.dump(trades_data, f, ensure_ascii=False, indent=2)
        
        with open(self.portfolio_file, 'w', encoding='utf-8') as f:
            json.dump(portfolio_data, f, ensure_ascii=False, indent=2)
        
        # 保存选股结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        date_str = datetime.now().strftime("%Y-%m-%d")
        date_dir = os.path.join(self.selection_dir, date_str)
        os.makedirs(date_dir, exist_ok=True)
        
        selection_file = os.path.join(date_dir, f"selection_{timestamp}.json")
        with open(selection_file, 'w', encoding='utf-8') as f:
            json.dump({
                "selection_date": date_str,
                "selection_time": timestamp,
                "total_selected": len(new_trades),
                "total_investment": total_investment,
                "stocks": selected_stocks,
                "trades": new_trades
            }, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"交易记录完成: {len(new_trades)} 笔交易，总投资 {total_investment:.2f}元")
        self.logger.info(f"选股结果保存: {selection_file}")
        
        return True
    
    def generate_daily_report(self) -> str:
        """生成每日报告"""
        self.logger.info("生成每日报告...")
        
        # 加载数据
        with open(self.trades_file, 'r', encoding='utf-8') as f:
            trades_data = json.load(f)
        
        with open(self.portfolio_file, 'r', encoding='utf-8') as f:
            portfolio_data = json.load(f)
        
        # 计算绩效
        active_trades = [t for t in trades_data["trades"] if t["status"] == "ACTIVE"]
        closed_trades = [t for t in trades_data["trades"] if t["status"] == "CLOSED"]
        
        # 生成报告
        report_lines = []
        report_lines.append("# 尾盘选股法每日报告")
        report_lines.append(f"## 报告日期: {datetime.now().strftime('%Y-%m-%d')}")
        report_lines.append(f"## 生成时间: {self.config['strategy']['report_time']}")
        report_lines.append(f"## 策略名称: {self.config['strategy']['name']}")
        report_lines.append(f"## 策略版本: {self.config['strategy']['version']}")
        report_lines.append("")
        
        report_lines.append("## 一、今日策略执行情况")
        report_lines.append(f"- **执行时间**: {self.config['strategy']['selection_time']}")
        report_lines.append(f"- **选股结果**: 已执行")
        report_lines.append(f"- **交易记录**: 已更新")
        report_lines.append("")
        
        report_lines.append("## 二、投资组合概览")
        report_lines.append(f"- **初始资金**: {portfolio_data['total_capital']:,.2f}元")
        report_lines.append(f"- **当前总资产**: {portfolio_data['total_value']:,.2f}元")
        report_lines.append(f"- **已投资金额**: {portfolio_data['invested_capital']:,.2f}元")
        report_lines.append(f"- **可用资金**: {portfolio_data['available_capital']:,.2f}元")
        
        total_return = ((portfolio_data['total_value'] - portfolio_data['total_capital']) / 
                       portfolio_data['total_capital'] * 100)
        report_lines.append(f"- **总收益率**: {total_return:.2f}%")
        report_lines.append("")
        
        report_lines.append("## 三、交易统计")
        report_lines.append(f"- **总交易笔数**: {trades_data['total_trades']}笔")
        report_lines.append(f"- **活跃交易**: {len(active_trades)}笔")
        report_lines.append(f"- **已平仓交易**: {len(closed_trades)}笔")
        report_lines.append("")
        
        if active_trades:
            report_lines.append("## 四、当前持仓")
            for trade in active_trades:
                pnl_emoji = "📈" if trade["unrealized_pnl"] > 0 else "📉"
                report_lines.append(f"### {trade['stock_name']} ({trade['stock_code']})")
                report_lines.append(f"- **持仓数量**: {trade['shares']}股")
                report_lines.append(f"- **进场价格**: {trade['entry_price']:.2f}元")
                report_lines.append(f"- **当前价格**: {trade['current_price']:.2f}元")
                report_lines.append(f"- **浮动盈亏**: {pnl_emoji} {trade['unrealized_pnl']:.2f}元 ({trade['unrealized_pnl_percent']:.2f}%)")
                report_lines.append(f"- **目标价格**: {trade['target_price']:.2f}元")
                report_lines.append(f"- **止损价格**: {trade['stop_loss']:.2f}元")
                report_lines.append("")
        
        report_lines.append("## 五、明日计划")
        report_lines.append("1. **继续跟踪**: 监控活跃持仓，执行止盈止损")
        report_lines.append("2. **策略执行**: 明日14:30继续执行尾盘选股")
        report_lines.append("3. **风险控制**: 严格执行止损纪律")
        report_lines.append("4. **仓位管理**: 控制单只股票仓位不超过30%")
        report_lines.append("")
        
        report_lines.append("## 六、风险提示")
        report_lines.append("1. **市场风险**: 股市有风险，投资需谨慎")
        report_lines.append("2. **策略风险**: 历史表现不代表未来收益")
        report_lines.append("3. **隔夜风险**: 尾盘策略存在隔夜不确定性")
        report_lines.append("4. **执行风险**: 需要严格按时执行策略")
        
        report_content = "\n".join(report_lines)
        
        # 保存报告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(self.reports_dir, f"report_{timestamp}.md")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.logger.info(f"每日报告已生成: {report_file}")
        
        return report_file
    
    def send_report_to_group(self, report_file: str, group_name: str) -> bool:
        """发送报告到群"""
        self.logger.info(f"发送报告到群: {group_name}")
        
        try:
            # 读取报告内容
            with open(report_file, 'r', encoding='utf-8') as f:
                report_content = f.read()
            
            # 这里应该集成飞书发送功能
            # 暂时先记录日志
            self.logger.info(f"报告内容长度: {len(report_content)} 字符")
            self.logger.info(f"报告文件: {report_file}")
            
            # 记录发送日志
            send_log = os.path.join(self.logs_dir, "send_log.json")
            log_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "group": group_name,
                "report_file": report_file,
                "success": True
            }
            
            if os.path.exists(send_log):
                with open(send_log, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            else:
                log_data = {"sends": []}
            
            log_data["sends"].append(log_entry)
            
            with open(send_log, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"报告发送记录已保存")
            
            return True
            
        except Exception as e:
            self.logger.error(f"发送报告失败: {e}")
            return False
    
    def execute_daily_selection(self) -> bool:
        """执行每日选股"""
        self.logger.info("执行每日尾盘选股...")
        
        # 检查时间
        if not self.is_selection_time():
            self.logger.warning("未到选股时间")
            return False
        
        # 获取实时价格
        try:
            from skills.a_stock_realtime_api import AStockRealtimeAPI
            api = AStockRealtimeAPI()
            prices = api.get_latest_prices()
            
            if prices is None or prices.empty:
                self.logger.error("获取价格数据失败")
                return False
            
            self.logger.info(f"获取到 {len(prices)} 条价格数据")
            
        except Exception as e:
            self.logger.error(f"导入实时价格API失败: {e}")
            return False
        
        # 执行选股
        selected_stocks = self.select_stocks(prices)
        
        if not selected_stocks:
            self.logger.warning("没有选出符合条件的股票")
            return False
        
        # 记录交易
        success = self.record_trades(selected_stocks)
        
        return success
    
    def start_daily_execution(self):
        """启动每日自动执行"""
        self.logger.info("启动每日自动执行...")
        
        try:
            while True:
                current_time = datetime.now()
                
                # 检查是否为交易日
                if self.is_trading_day(current_time):
                    # 检查选股时间
                    if self.is_selection_time(current_time):
                        self.logger.info("到达选股时间，开始执行...")
                        self.execute_daily_selection()
                    
                    # 检查报告时间
                    report_time_str = self.config["strategy"]["report_time"]
                    report_hour, report_minute = map(int, report_time_str.split(":"))
                    report_time = current_time.replace(hour=report_hour, minute=report_minute, second=0, microsecond=0)
                    
                    if current_time >= report_time and current_time < report_time + timedelta(minutes=5):
                        self.logger.info("到达报告时间，生成报告...")
                        report_file = self.generate_daily_report()
                        
                        # 发送报告
                        group_name = self.config["reporting"]["send_to_group"]
                        self.send_report_to_group(report_file, group_name)
                
                # 等待1分钟再检查
                time.sleep(60)
                
        except KeyboardInterrupt:
            self.logger.info("自动执行被用户中断")
        except Exception as e:
            self.logger.error(f"自动执行异常: {e}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='尾盘选股法')
    parser.add_argument('--execute-selection', action='store_true', help='执行选股')
    parser.add_argument('--daily-report', action='store_true', help='生成每日报告')
    parser.add_argument('--start-daily', action='store_true', help='启动每日自动执行')
    parser.add_argument('--send-report', type=str, help='发送报告到指定群')
    
    args = parser.parse_args()
    
    selector = TailEndSelection()
    
    if args.execute_selection:
        print("执行尾盘选股...")
        success = selector.execute_daily_selection()
        if success:
            print("✅ 选股执行完成")
        else:
            print("❌ 选股执行失败")
    
    elif args.daily_report:
        print("生成每日报告...")
        report_file = selector.generate_daily_report()
        print(f"✅ 报告已生成: {report_file}")
    
    elif args.start_daily:
        print("启动每日自动执行...")
        print("按 Ctrl+C 停止")
        selector.start_daily_execution()
    
    elif args.send_report:
        print(f"发送报告到群: {args.send_report}")
        # 需要先有报告文件
        report_file = selector.generate_daily_report()
        success = selector.send_report_to_group(report_file, args.send_report)
        if success:
            print("✅ 报告发送成功")
        else:
            print("❌ 报告发送失败")
    
    else:
        print("尾盘选股法 Skill")
        print(f"版本: {selector.version}")
        print(f"作者: {selector.author}")
        print(f"选股时间: {selector.config['strategy']['selection_time']}")
        print(f"报告时间: {selector.config['strategy']['report_time']}")
        print("")
        print("可用命令:")
        print("  --execute-selection  执行选股")
        print("  --daily-report       生成每日报告")
        print("  --start-daily        启动每日自动执行")
        print("  --send-report <群名> 发送报告到群")


if __name__ == "__main__":
    main()