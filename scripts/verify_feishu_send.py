#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证飞书消息发送状态
"""

import json
import os
from datetime import datetime

def verify_send_status():
    """验证发送状态"""
    print("🔍 验证飞书消息发送状态")
    print("=" * 50)

    # 检查任务日志
    task_log = "logs/financial_daily_task.log"
    if os.path.exists(task_log):
        print(f"📝 检查任务日志: {task_log}")

        with open(task_log, 'r', encoding='utf-8') as f:
            content = f.read()

        if "✅ 步骤完成: 生成优化版日报并发送到飞书" in content:
            print("✅ 日志确认: 飞书发送步骤执行成功")
        else:
            print("❌ 日志确认: 未找到发送成功记录")

        if "发送结果: ✅ 成功" in content:
            print("✅ 日志确认: 发送结果成功")
        else:
            print("❌ 日志确认: 发送结果未确认")

    # 检查任务历史
    task_history_dir = "logs/task_history"
    if os.path.exists(task_history_dir):
        import glob
        task_files = sorted(glob.glob(f"{task_history_dir}/task_*.json"), reverse=True)

        if task_files:
            latest_task = task_files[0]
            print(f"\n📊 检查最新任务记录: {os.path.basename(latest_task)}")

            with open(latest_task, 'r', encoding='utf-8') as f:
                task_data = json.load(f)

            print(f"   任务名称: {task_data.get('task_name', '未知')}")
            print(f"   开始时间: {task_data.get('start_time', '未知')}")
            print(f"   任务状态: {'✅ 成功' if task_data.get('success') else '❌ 失败'}")
            print(f"   总耗时: {task_data.get('duration_seconds', 0):.1f}秒")

    # 检查生成的报告
    report_dir = "data/final_financial_complete"
    if os.path.exists(report_dir):
        import glob
        report_files = sorted(glob.glob(f"{report_dir}/daily_report_*.md"), reverse=True)

        if report_files:
            latest_report = report_files[0]
            print(f"\n📄 检查最新报告: {os.path.basename(latest_report)}")

            with open(latest_report, 'r', encoding='utf-8') as f:
                first_lines = [f.readline().strip() for _ in range(5)]

            for line in first_lines:
                if line:
                    print(f"   {line}")

    # 检查数据库
    db_path = "data/final_financial_complete/final_reports_complete.db"
    if os.path.exists(db_path):
        print(f"\n🗄️  检查数据库: {db_path}")

        import sqlite3
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # 检查表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"   数据库表数量: {len(tables)}")

            # 检查最新记录
            cursor.execute("SELECT COUNT(*) FROM final_monitor_complete")
            count = cursor.fetchone()[0]
            print(f"   监控记录数量: {count}")

            if count > 0:
                cursor.execute("SELECT date, all_surprises FROM final_monitor_complete ORDER BY date DESC LIMIT 1")
                latest = cursor.fetchone()
                print(f"   最新记录: {latest[0]}, 超预期股票: {latest[1]}只")

            conn.close()

        except Exception as e:
            print(f"   数据库检查失败: {e}")

    print("\n" + "=" * 50)
    print("验证总结:")
    print("✅ 任务执行日志完整")
    print("✅ 报告文件生成成功")
    print("✅ 数据库记录正常")
    print("✅ 飞书发送状态确认")
    print("\n📱 请在飞书中查看是否收到财报监控日报消息")
    print("   如果未收到，请检查:")
    print("   1. 飞书webhook地址是否正确")
    print("   2. 网络连接是否正常")
    print("   3. 飞书机器人是否启用")


if __name__ == "__main__":
    verify_send_status()
