#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日复盘报告脚本
在交易日晚上18:00自动生成复盘报告
"""

import json
import os
import sys
from datetime import datetime, timedelta
import numpy as np

class DailyReviewReport:
    """每日复盘报告"""
    
    def __init__(self):
        self.base_dir = "data/simulated_trading"
        self.trades_file = os.path.join(self.base_dir, "simulated_trades.json")
        self.portfolio_file = os.path.join(self.base_dir, "simulated_portfolio.json")
        self.reports_dir = os.path.join(self.base_dir, "reports")
        
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def load_data(self):
        """加载数据"""
        with open(self.trades_file, 'r', encoding='utf-8') as f:
            trades_data = json.load(f)
        
        with open(self.portfolio_file, 'r', encoding='utf-8') as f:
            portfolio_data = json.load(f)
        
        return trades_data, portfolio_data
    
    def generate_report(self):
        """生成每日复盘报告"""
        print(f"生成每日复盘报告 ({datetime.now().strftime('%Y-%m-%d')} 18:00)...")
        
        trades_data, portfolio_data = self.load_data()
        
        # 计算绩效
        active_trades = [t for t in trades_data["trades"] if t["status"] == "ACTIVE"]
        closed_trades = [t for t in trades_data["trades"] if t["status"] == "CLOSED"]
        
        # 计算胜率
        winning_trades = [t for t in closed_trades if t["realized_pnl"] > 0]
        losing_trades = [t for t in closed_trades if t["realized_pnl"] <= 0]
        
        win_rate = len(winning_trades) / len(closed_trades) * 100 if closed_trades else 0
        avg_win = np.mean([t["realized_pnl"] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t["realized_pnl"] for t in losing_trades]) if losing_trades else 0
        
        # 总投资回报
        total_investment = portfolio_data["invested_capital"]
        total_value = portfolio_data["total_value"]
        total_return = ((total_value - 1000000) / 1000000 * 100)  # 相对于初始100万
        
        # 生成报告
        report_lines = []
        report_lines.append("# 尾盘选股策略每日复盘报告")
        report_lines.append(f"## 报告日期: {datetime.now().strftime('%Y-%m-%d')}")
        report_lines.append(f"## 生成时间: 18:00")
        report_lines.append(f"## 策略名称: 杨永兴隔夜套利战法")
        report_lines.append(f"## 策略版本: v1.0")
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
        
        print(f"✅ 每日复盘报告已生成: {report_file}")
        
        # 显示报告摘要
        print("\n📊 报告摘要:")
        print(f"- 当前总资产: {total_value:,.2f}元")
        print(f"- 总收益率: {total_return:.2f}%")
        print(f"- 活跃持仓: {len(active_trades)}笔")
        print(f"- 胜率: {win_rate:.1f}%")
        
        return report_file


def main():
    """主函数"""
    print("尾盘选股策略每日复盘报告系统")
    print("=" * 60)
    
    # 检查是否是交易日（周一至周五）
    today = datetime.now()
    if today.weekday() >= 5:  # 5=周六, 6=周日
        print("⏸️ 今天是周末，不生成复盘报告")
        return
    
    # 检查时间（应该在18:00之后）
    report_time = today.replace(hour=18, minute=0, second=0, microsecond=0)
    if today < report_time:
        time_diff = (report_time - today).total_seconds() / 60
        print(f"⏳ 还未到报告时间，距离18:00还有 {time_diff:.1f} 分钟")
        return
    
    # 生成报告
    reporter = DailyReviewReport()
    report_file = reporter.generate_report()
    
    print("\n" + "=" * 60)
    print("✅ 每日复盘报告生成完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()