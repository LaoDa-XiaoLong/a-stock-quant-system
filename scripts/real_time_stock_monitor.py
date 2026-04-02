                    # 计算盈亏
                    if stock['current_position'] > 0:
                        profit_loss = (current_price - stock['entry_price']) * stock['current_position']
                        profit_loss_pct = (current_price - stock['entry_price']) / stock['entry_price'] * 100

                        stock['profit_loss'] = round(profit_loss, 2)
                        stock['profit_loss_pct'] = round(profit_loss_pct, 2)

                        # 记录价格变化
                        price_change = current_price - stock.get('last_price', current_price)
                        if price_change != 0:
                            change_symbol = "📈" if price_change > 0 else "📉"
                            self.log_message(f"   {change_symbol} 价格变化: {price_change:+.2f}元, 盈亏: {stock['profit_loss']:+.2f}元 ({stock['profit_loss_pct']:+.2f}%)")

                        stock['last_price'] = current_price

        # 检查止损止盈条件
        self.check_stop_loss_take_profit()

        # 保存更新
        self.save_portfolio()

        # 更新投资组合总览
        self.update_portfolio_summary()

        self.log_message("✅ 监控循环完成")
        self.log_message("=" * 50)

    def start_monitoring(self):
        """开始监控"""
        if self.monitoring:
            self.log_message("⚠️ 监控已在运行中")
            return

        self.monitoring = True
        self.log_message("🚀 启动实时股票监控")

        # 创建监控线程
        self.monitor_thread = threading.Thread(target=self._monitoring_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        self.log_message("✅ 监控线程已启动")

    def _monitoring_loop(self):
        """监控循环（在独立线程中运行）"""
        import schedule
        import time

        # 每3分钟执行一次监控
        schedule.every(self.monitor_interval).seconds.do(self.monitor_cycle)

        # 立即执行一次
        self.monitor_cycle()

        self.log_message(f"🔄 监控计划已设置，每{self.monitor_interval}秒执行一次")

        # 主循环
        while self.monitoring:
            schedule.run_pending()
            time.sleep(1)

    def stop_monitoring(self):
        """停止监控"""
        if not self.monitoring:
            self.log_message("⚠️ 监控未在运行")
            return

        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

        self.log_message("🛑 监控已停止")

    def generate_daily_summary(self):
        """生成每日总结"""
        today = datetime.now().strftime('%Y-%m-%d')
        summary_file = f'{self.tracking_dir}/daily_monitor_summary_{today}.md'

        # 加载最新的投资组合
        self.portfolio = self.load_portfolio()

        # 统计信息
        total_stocks = len(self.portfolio['stocks'])
        pending_stocks = len([s for s in self.portfolio['stocks'] if s['status'] == '待进场'])
        entered_stocks = len([s for s in self.portfolio['stocks'] if s['status'] == '已进场'])
        stopped_stocks = len([s for s in self.portfolio['stocks'] if s['status'] == '已止损'])
        profited_stocks = len([s for s in self.portfolio['stocks'] if s['status'] == '已止盈'])

        # 生成总结内容
        summary_content = f"""# 📈 实时监控每日总结
## 报告日期: {today}
## 生成时间: {datetime.now().strftime('%H:%M:%S')}

## 一、监控概况

### 📊 监控统计
- **监控股票总数**: {total_stocks}只
- **待进场股票**: {pending_stocks}只
- **已进场股票**: {entered_stocks}只
- **已止损股票**: {stopped_stocks}只
- **已止盈股票**: {profited_stocks}只

### 💰 投资组合总览
- **总投资金额**: {self.portfolio.get('total_investment', 0):.2f}元
- **当前市值**: {self.portfolio.get('current_value', 0):.2f}元
- **总盈亏金额**: {self.portfolio.get('total_profit_loss', 0):+.2f}元
- **总盈亏比例**: {self.portfolio.get('total_profit_loss_pct', 0):+.2f}%

## 二、股票状态详情

### 🟡 待进场股票
"""

        for stock in self.portfolio['stocks']:
            if stock['status'] == '待进场':
                summary_content += f"""
#### {stock['code']} {stock['name']}
- **综合评分**: {stock['score']}/100
- **当前价格**: {stock.get('current_price', 'N/A')}元
- **进场策略**:
  - 激进: {stock['entry_strategy']['激进进场']}元
  - 稳健: {stock['entry_strategy']['稳健进场']}元
  - 保守: {stock['entry_strategy']['保守进场']}元
- **风险控制**:
  - 止损: {stock['stop_loss']}元
  - 止盈: {stock['take_profit'][0]}元 / {stock['take_profit'][1]}元
"""

        summary_content += """
### 🟢 已进场股票
"""

        for stock in self.portfolio['stocks']:
            if stock['status'] == '已进场':
                profit_symbol = "📈" if stock.get('profit_loss', 0) >= 0 else "📉"
                summary_content += f"""
#### {stock['code']} {stock['name']} {profit_symbol}
- **进场价格**: {stock['entry_price']}元
- **当前价格**: {stock.get('current_price', 'N/A')}元
- **持仓数量**: {stock['current_position']}股
- **投资金额**: {stock['total_investment']:.2f}元
- **盈亏金额**: {stock.get('profit_loss', 0):+.2f}元
- **盈亏比例**: {stock.get('profit_loss_pct', 0):+.2f}%
- **进场类型**: {stock.get('entry_type', 'N/A')}
- **进场时间**: {stock.get('entry_time', 'N/A')}
"""

        summary_content += """
### 🔴 已结束股票（止损/止盈）
"""

        for stock in self.portfolio['stocks']:
            if stock['status'] in ['已止损', '已止盈']:
                status_emoji = "⚠️" if stock['status'] == '已止损' else "🎯"
                summary_content += f"""
#### {stock['code']} {stock['name']} {status_emoji}
- **进场价格**: {stock['entry_price']}元
- **出场价格**: {stock.get('exit_price', 'N/A')}元
- **出场原因**: {stock.get('exit_reason', 'N/A')}
- **出场时间**: {stock.get('exit_time', 'N/A')}
- **最终盈亏**: {stock.get('profit_loss', 0):+.2f}元
- **盈亏比例**: {stock.get('profit_loss_pct', 0):+.2f}%
"""

        # 读取今日交易记录
        trades_file = f'{self.tracking_dir}/trade_records_{datetime.now().strftime("%Y%m%d")}.json'
        if os.path.exists(trades_file):
            with open(trades_file, 'r', encoding='utf-8') as f:
                trades = json.load(f)

            summary_content += f"""
## 三、今日交易记录

今日共执行 {len(trades)} 笔交易：

| 时间 | 股票 | 操作 | 价格 | 数量 | 金额 | 备注 |
|------|------|------|------|------|------|------|
"""

            for trade in trades:
                summary_content += f"| {trade['timestamp']} | {trade['stock_code']} {trade['stock_name']} | {trade['action']} | {trade['price']}元 | {trade['quantity']}股 | {trade['amount']:.2f}元 | {trade.get('profit_loss', '')} |\n"

        summary_content += f"""
## 四、监控日志摘要

今日监控系统运行正常，每{self.monitor_interval}秒检查一次价格。
在交易时间内持续监控，非交易时间自动暂停。

## 五、明日计划

1. 继续监控待进场股票的进场机会
2. 跟踪已进场股票的止损止盈条件
3. 生成新的每日总结报告

---

*报告生成: 实时股票监控系统 v1.0*
*下次报告时间: {(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')} 收盘后*
"""

        # 写入文件
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)

        self.log_message(f"✅ 每日总结已生成: {summary_file}")

        return summary_file

def main():
    """主函数"""
    print("=" * 60)
    print("📈 实时股票监控和自动交易模拟系统")
    print("=" * 60)

    # 初始化监控系统
    monitor = RealTimeStockMonitor()

    # 检查当前时间
    current_time = datetime.now().strftime("%H:%M")
    print(f"🕐 当前时间: {current_time}")

    if monitor.is_trading_time():
        print("✅ 当前为交易时间，开始监控...")

        # 启动监控
        monitor.start_monitoring()

        print("\n💡 监控已启动，系统将在后台运行")
        print("   按 Ctrl+C 停止监控")

        try:
            # 保持主线程运行
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 接收到停止信号")
            monitor.stop_monitoring()
            print("✅ 监控已停止")

            # 生成当日总结
            print("\n📊 生成当日总结...")
            monitor.generate_daily_summary()

    else:
        print("⏸️ 当前为非交易时间")
        print("   交易时间: 09:30-11:30, 13:00-15:00 (周一至周五)")

        # 显示下次交易时间
        now = datetime.now()
        if now.hour < 9 or (now.hour == 9 and now.minute < 30):
            next_time = "09:30"
        elif now.hour < 13:
            next_time = "13:00"
        else:
            # 明天09:30
            tomorrow = now + timedelta(days=1)
            next_time = tomorrow.strftime("%Y-%m-%d 09:30")

        print(f"   ⏰ 下次交易时间: {next_time}")

        # 仍然生成当前状态报告
        print("\n📊 生成当前状态报告...")
        monitor.generate_daily_summary()

if __name__ == '__main__':
    main()
