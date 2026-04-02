#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
尾盘选股自动执行脚本
每天14:30-15:00自动运行尾盘选股策略
"""

import sys
import os
import time
import json
from datetime import datetime, timedelta
import schedule

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.tail_end_stock_selection import TailEndStockSelection

class AutoTailEndSelection:
    """尾盘选股自动执行器"""

    def __init__(self):
        self.selector = TailEndStockSelection()
        self.config_file = "config/tail_end_strategy_config.json"
        self.portfolio_file = "data/investment_tracking/tail_end_portfolio.json"
        self.log_file = "logs/tail_end_selection.log"

        # 创建日志目录
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

        # 加载配置
        self.load_config()

    def load_config(self):
        """加载配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            print(f"配置加载成功: {self.config['strategy_name']} {self.config['strategy_version']}")
        except Exception as e:
            print(f"配置加载失败: {e}")
            self.config = {}

    def log_message(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)

        print(log_entry.strip())

    def get_watchlist(self):
        """获取监控股票列表"""
        # 这里可以从配置文件、数据库或API获取股票列表
        # 暂时使用一个默认的A股股票列表

        # A股主要股票代码（示例）
        watchlist = [
            # 上证50成分股（部分）
            "600000", "600036", "600030", "600016", "600519",
            "600887", "600104", "600276", "600309", "600585",
            # 深证100成分股（部分）
            "000001", "000002", "000063", "000069", "000100",
            "000157", "000333", "000338", "000425", "000538",
            # 创业板权重股（部分）
            "300059", "300122", "300124", "300142", "300144",
            "300347", "300408", "300413", "300433", "300450"
        ]

        return watchlist

    def update_portfolio(self, selected_stocks: list):
        """更新投资组合"""
        try:
            # 加载现有投资组合
            if os.path.exists(self.portfolio_file):
                with open(self.portfolio_file, 'r', encoding='utf-8') as f:
                    portfolio = json.load(f)
            else:
                portfolio = {
                    "portfolio_name": "尾盘选股策略投资组合",
                    "strategy_name": "尾盘选股策略",
                    "strategy_version": "v1.0",
                    "created_date": datetime.now().strftime("%Y-%m-%d"),
                    "last_updated": "",
                    "stocks": [],
                    "total_stocks": 0,
                    "total_investment": 0,
                    "current_value": 0,
                    "total_profit_loss": 0,
                    "total_profit_loss_pct": 0
                }

            # 更新投资组合
            portfolio["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            portfolio["stocks"] = selected_stocks
            portfolio["total_stocks"] = len(selected_stocks)

            # 保存更新后的投资组合
            with open(self.portfolio_file, 'w', encoding='utf-8') as f:
                json.dump(portfolio, f, ensure_ascii=False, indent=2)

            self.log_message(f"投资组合已更新: {len(selected_stocks)} 只股票")

        except Exception as e:
            self.log_message(f"投资组合更新失败: {e}")

    def send_notification(self, result: dict):
        """发送通知（模拟函数）"""
        # 这里可以集成飞书、微信等通知渠道
        # 暂时只记录日志

        if result and result.get("selected_stocks"):
            selected_count = len(result["selected_stocks"])
            top_stocks = result["selected_stocks"][:3]

            notification = f"""
🎯 尾盘选股完成通知
====================
选股时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
策略名称: {self.config.get('strategy_name', '尾盘选股策略')}
筛选结果: 共选出 {selected_count} 只符合条件的股票

📈 前三推荐股票:
"""

            for i, stock in enumerate(top_stocks, 1):
                notification += f"{i}. {stock['name']} ({stock['code']}) - 评分: {stock['score']}分\n"

            notification += f"\n📊 详细报告: {result.get('report_path', '未生成')}"

            self.log_message(f"通知内容:\n{notification}")

    def run_selection_job(self):
        """运行选股任务"""
        current_time = datetime.now()

        self.log_message("开始执行尾盘选股任务...")

        # 检查是否是尾盘时间
        if not self.selector.is_tail_end_time(current_time):
            self.log_message(f"当前时间 {current_time.strftime('%H:%M:%S')} 不在尾盘选股时间窗口内")
            return

        try:
            # 获取监控列表
            watchlist = self.get_watchlist()
            self.log_message(f"获取到 {len(watchlist)} 只监控股票")

            # 运行选股策略
            result = self.selector.run_selection(watchlist)

            if result:
                # 更新投资组合
                self.update_portfolio(result["selected_stocks"])

                # 发送通知
                self.send_notification(result)

                self.log_message("尾盘选股任务执行完成!")
            else:
                self.log_message("尾盘选股未执行或执行失败")

        except Exception as e:
            self.log_message(f"尾盘选股任务执行失败: {e}")
            import traceback
            self.log_message(f"错误详情:\n{traceback.format_exc()}")

    def schedule_jobs(self):
        """调度任务"""
        # 每天14:30执行尾盘选股
        schedule.every().day.at("14:30").do(self.run_selection_job)

        # 每天14:45再次执行（双重保障）
        schedule.every().day.at("14:45").do(self.run_selection_job)

        # 每天15:00执行最终选股
        schedule.every().day.at("15:00").do(self.run_selection_job)

        self.log_message("尾盘选股任务调度已设置:")
        self.log_message("  - 14:30: 第一次选股")
        self.log_message("  - 14:45: 第二次选股")
        self.log_message("  - 15:00: 最终选股")

    def run_scheduler(self):
        """运行调度器"""
        self.log_message("启动尾盘选股自动调度器...")
        self.schedule_jobs()

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次

        except KeyboardInterrupt:
            self.log_message("调度器已停止")
        except Exception as e:
            self.log_message(f"调度器运行错误: {e}")

    def run_once(self):
        """运行一次（测试用）"""
        self.log_message("执行单次尾盘选股...")
        self.run_selection_job()


def main():
    """主函数"""
    print("尾盘选股自动执行系统")
    print("=" * 60)

    auto_selector = AutoTailEndSelection()

    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "run":
            # 运行调度器
            auto_selector.run_scheduler()
        elif sys.argv[1] == "once":
            # 运行一次
            auto_selector.run_once()
        elif sys.argv[1] == "test":
            # 测试模式
            print("测试模式 - 模拟尾盘时间运行")

            # 模拟尾盘时间
            import time
            original_get_time = auto_selector.selector.get_current_time

            def mock_tail_time():
                return datetime(2026, 4, 1, 14, 45, 0)

            auto_selector.selector.get_current_time = mock_tail_time

            try:
                auto_selector.run_once()
            finally:
                auto_selector.selector.get_current_time = original_get_time
        else:
            print(f"未知命令: {sys.argv[1]}")
            print("可用命令: run, once, test")
    else:
        print("请指定运行模式:")
        print("  python auto_tail_end_selection.py run   # 运行调度器")
        print("  python auto_tail_end_selection.py once  # 运行一次")
        print("  python auto_tail_end_selection.py test  # 测试模式")
        print("\n默认运行测试模式...")

        # 运行测试模式
        import time
        original_get_time = auto_selector.selector.get_current_time

        def mock_tail_time():
            return datetime(2026, 4, 1, 14, 45, 0)

        auto_selector.selector.get_current_time = mock_tail_time

        try:
            auto_selector.run_once()
        finally:
            auto_selector.selector.get_current_time = original_get_time


if __name__ == "__main__":
    main()
