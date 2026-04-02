#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码健康度检查定时任务
用于定期自动运行代码健康度检查
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
import schedule

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from code_health_checker import CodeHealthChecker

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CodeHealthMonitor:
    """代码健康度监控器"""

    def __init__(self, workspace_path: str = "/Users/ago/.openclaw/workspace"):
        self.workspace_path = Path(workspace_path)
        self.checker = CodeHealthChecker(workspace_path)
        self.history_file = self.workspace_path / 'reports' / 'code_health_history.json'

        # 加载历史记录
        self.history = self._load_history()

        # 报警配置
        self.alert_config = {
            'score_threshold': 70,      # 分数阈值
            'score_drop_threshold': 10, # 分数下降阈值
            'issue_increase_threshold': 5,  # 问题增加阈值
            'alert_channels': ['log', 'file']  # 报警渠道
        }

    def _load_history(self) -> Dict:
        """加载历史记录"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载历史记录失败: {e}")

        return {
            'checks': [],
            'trends': {},
            'last_check': None
        }

    def _save_history(self):
        """保存历史记录"""
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存历史记录失败: {e}")

    def run_check(self) -> Dict:
        """运行一次检查"""
        logger.info("开始定期代码健康度检查")

        # 运行检查
        report = self.checker.run_full_check()

        # 保存报告
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.workspace_path / 'reports' / f'code_health_{timestamp}.json'
        self.checker.save_report(report, report_file)

        # 更新历史记录
        check_record = {
            'timestamp': report['summary']['timestamp'],
            'score': report['summary']['overall_score'],
            'health_level': report['summary']['health_level'],
            'total_issues': report['summary']['total_issues'],
            'report_file': str(report_file.relative_to(self.workspace_path))
        }

        self.history['checks'].append(check_record)
        self.history['last_check'] = check_record

        # 只保留最近30次检查
        if len(self.history['checks']) > 30:
            self.history['checks'] = self.history['checks'][-30:]

        # 分析趋势
        self._analyze_trends()

        # 检查是否需要报警
        self._check_alerts(report)

        # 保存历史记录
        self._save_history()

        logger.info(f"定期检查完成，分数: {report['summary']['overall_score']}/100")
        return report

    def _analyze_trends(self):
        """分析趋势"""
        checks = self.history['checks']
        if len(checks) < 2:
            return

        recent_checks = checks[-10:]  # 最近10次检查

        # 计算分数趋势
        scores = [c['score'] for c in recent_checks]
        if len(scores) >= 2:
            score_change = scores[-1] - scores[0]
            avg_score = sum(scores) / len(scores)

            self.history['trends']['score'] = {
                'current': scores[-1],
                'average': round(avg_score, 1),
                'change': round(score_change, 1),
                'trend': '上升' if score_change > 0 else '下降' if score_change < 0 else '稳定'
            }

        # 计算问题趋势
        issues = [c['total_issues'] for c in recent_checks]
        if len(issues) >= 2:
            issue_change = issues[-1] - issues[0]

            self.history['trends']['issues'] = {
                'current': issues[-1],
                'change': issue_change,
                'trend': '减少' if issue_change < 0 else '增加' if issue_change > 0 else '稳定'
            }

    def _check_alerts(self, report: Dict):
        """检查是否需要报警"""
        current_score = report['summary']['overall_score']
        current_issues = report['summary']['total_issues']

        alerts = []

        # 检查分数阈值
        if current_score < self.alert_config['score_threshold']:
            alerts.append(f"代码健康度分数低于阈值: {current_score} < {self.alert_config['score_threshold']}")

        # 检查分数下降
        if len(self.history['checks']) >= 2:
            last_score = self.history['checks'][-2]['score']
            score_drop = last_score - current_score

            if score_drop > self.alert_config['score_drop_threshold']:
                alerts.append(f"代码健康度分数显著下降: {last_score} → {current_score} (下降{score_drop:.1f})")

        # 检查问题增加
        if len(self.history['checks']) >= 2:
            last_issues = self.history['checks'][-2]['total_issues']
            issue_increase = current_issues - last_issues

            if issue_increase > self.alert_config['issue_increase_threshold']:
                alerts.append(f"代码问题显著增加: {last_issues} → {current_issues} (增加{issue_increase})")

        # 发送报警
        if alerts:
            self._send_alerts(alerts, report)

    def _send_alerts(self, alerts: List[str], report: Dict):
        """发送报警"""
        alert_message = "🚨 代码健康度报警\n\n"
        alert_message += f"检查时间: {report['summary']['timestamp']}\n"
        alert_message += f"当前分数: {report['summary']['overall_score']}/100\n"
        alert_message += f"健康等级: {report['summary']['health_level']}\n\n"

        alert_message += "报警原因:\n"
        for i, alert in enumerate(alerts, 1):
            alert_message += f"{i}. {alert}\n"

        alert_message += "\n重点关注问题:\n"
        for i, issue in enumerate(report['top_issues'][:3], 1):
            alert_message += f"{i}. {issue}\n"

        # 记录到日志
        logger.warning(alert_message)

        # 保存到文件
        alert_file = self.workspace_path / 'reports' / 'code_health_alerts.txt'
        with open(alert_file, 'a', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write(alert_message)
            f.write("=" * 60 + "\n\n")

        logger.info(f"代码健康度报警已记录: {alert_file}")

    def get_summary_report(self) -> Dict:
        """获取摘要报告"""
        if not self.history['checks']:
            return {'status': 'no_checks', 'message': '尚未进行代码健康度检查'}

        last_check = self.history['last_check']
        trends = self.history.get('trends', {})

        summary = {
            'last_check': last_check['timestamp'],
            'current_score': last_check['score'],
            'current_health': last_check['health_level'],
            'total_issues': last_check['total_issues'],
            'trends': trends,
            'check_count': len(self.history['checks']),
            'status': 'healthy' if last_check['score'] >= self.alert_config['score_threshold'] else 'needs_attention'
        }

        return summary

    def run_daily_check(self):
        """每日检查任务"""
        logger.info("执行每日代码健康度检查")
        return self.run_check()

    def run_weekly_summary(self):
        """每周摘要任务"""
        logger.info("生成每周代码健康度摘要")

        summary = self.get_summary_report()

        # 生成周报
        weekly_report = {
            'week_start': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            'week_end': datetime.now().strftime('%Y-%m-%d'),
            'summary': summary,
            'weekly_checks': self.history['checks'][-7:] if len(self.history['checks']) >= 7 else self.history['checks']
        }

        # 保存周报
        weekly_file = self.workspace_path / 'reports' / f'code_health_weekly_{datetime.now().strftime("%Y%m%d")}.json'
        weekly_file.parent.mkdir(parents=True, exist_ok=True)

        with open(weekly_file, 'w', encoding='utf-8') as f:
            json.dump(weekly_report, f, ensure_ascii=False, indent=2)

        logger.info(f"每周摘要已保存: {weekly_file}")

        return weekly_report


def setup_schedule():
    """设置定时任务"""
    monitor = CodeHealthMonitor()

    # 每日检查（上午9点）
    schedule.every().day.at("09:00").do(monitor.run_daily_check)

    # 每周摘要（周一上午10点）
    schedule.every().monday.at("10:00").do(monitor.run_weekly_summary)

    logger.info("代码健康度监控定时任务已设置")
    logger.info("  - 每日检查: 09:00")
    logger.info("  - 每周摘要: 周一 10:00")

    return monitor


def run_once():
    """运行一次检查"""
    print("运行单次代码健康度检查")
    print("=" * 60)

    monitor = CodeHealthMonitor()
    report = monitor.run_check()

    summary = monitor.get_summary_report()

    print(f"\n检查完成！")
    print(f"当前分数: {summary['current_score']}/100")
    print(f"健康等级: {summary['current_health']}")
    print(f"发现问题: {summary['total_issues']} 个")

    if 'trends' in summary and 'score' in summary['trends']:
        trend = summary['trends']['score']
        print(f"分数趋势: {trend['trend']} ({trend['change']:+0.1f})")

    print(f"\n历史检查次数: {summary['check_count']}")
    print(f"状态: {'✅ 健康' if summary['status'] == 'healthy' else '⚠️ 需要关注'}")

    # 显示最近3次检查
    if monitor.history['checks']:
        print("\n最近检查记录:")
        for check in monitor.history['checks'][-3:]:
            date_str = check['timestamp'].split('T')[0]
            print(f"  {date_str}: {check['score']}/100 ({check['health_level']})")


def run_scheduled():
    """运行定时任务"""
    print("启动代码健康度监控定时任务")
    print("=" * 60)

    monitor = setup_schedule()

    # 显示当前状态
    summary = monitor.get_summary_report()
    if summary['status'] != 'no_checks':
        print(f"当前状态: {summary['current_score']}/100 ({summary['current_health']})")

    print("\n定时任务运行中...")
    print("按 Ctrl+C 停止")

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    except KeyboardInterrupt:
        print("\n定时任务已停止")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='代码健康度监控工具')
    parser.add_argument('--mode', choices=['once', 'schedule'], default='once',
                       help='运行模式: once(单次检查) 或 schedule(定时任务)')

    args = parser.parse_args()

    if args.mode == 'once':
        run_once()
    else:
        run_scheduled()
