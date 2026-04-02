#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一监控系统
监控所有消息群通知任务的状态
"""

import os
import json
import subprocess
from datetime import datetime

def check_all_notifications():
    """检查所有通知任务状态"""
    print("🔍 消息群通知系统状态检查")
    print("=" * 70)

    # 检查launchd服务
    print("
1. 🔧 检查launchd定时服务:")
    print("-" * 40)

    launchd_services = [
        "com.openclaw.healthcheck.send",
        "com.openclaw.githubsync.send"
    ]

    # 动态发现其他服务
    launchd_dir = "/Users/ago/Library/LaunchAgents"
    if os.path.exists(launchd_dir):
        for file in os.listdir(launchd_dir):
            if file.startswith("com.openclaw.") and file.endswith(".send.plist"):
                service_id = file.replace(".plist", "")
                if service_id not in launchd_services:
                    launchd_services.append(service_id)

    for service_id in launchd_services:
        try:
            result = subprocess.run(
                ["launchctl", "list", service_id],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print(f"   ✅ {service_id}: 已加载")
            else:
                print(f"   ❌ {service_id}: 未加载")
        except:
            print(f"   ❓ {service_id}: 检查失败")

    # 检查脚本文件
    print("
2. 📝 检查发送脚本:")
    print("-" * 40)

    scripts_dir = "/Users/ago/.openclaw/workspace/scripts"
    send_scripts = [f for f in os.listdir(scripts_dir) if f.startswith("send_") and f.endswith(".py")]

    for script in send_scripts:
        script_path = os.path.join(scripts_dir, script)
        if os.path.exists(script_path):
            # 检查执行权限
            if os.access(script_path, os.X_OK):
                print(f"   ✅ {script}: 存在且可执行")
            else:
                print(f"   ⚠️  {script}: 存在但不可执行")
        else:
            print(f"   ❌ {script}: 不存在")

    # 检查日志文件
    print("
3. 📊 检查日志系统:")
    print("-" * 40)

    log_dirs = [
        "/Users/ago/.openclaw/workspace/logs/health_check_send",
        "/Users/ago/.openclaw/workspace/logs/github_sync_send",
        "/Users/ago/.openclaw/workspace/logs/group_notifications"
    ]

    for log_dir in log_dirs:
        if os.path.exists(log_dir):
            log_files = [f for f in os.listdir(log_dir) if f.endswith('.json')]
            print(f"   ✅ {os.path.basename(log_dir)}: {len(log_files)}个日志文件")
        else:
            print(f"   📁 {os.path.basename(log_dir)}: 目录不存在")

    # 检查下次执行时间
    print("
4. ⏰ 下次执行时间:")
    print("-" * 40)

    now = datetime.now()
    print(f"   当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")

    # 已知的定时任务
    scheduled_tasks = [
        ("系统健康检查报告", "10:00"),
        ("GitHub同步状态", "12:10"),
        ("财报监控日报", "09:00"),
        ("股票数据自动更新状态", "09:30"),
        ("代码健康度检查报告", "15:00")
    ]

    for task_name, task_time in scheduled_tasks:
        hour, minute = map(int, task_time.split(":"))
        task_datetime = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        if now > task_datetime:
            task_datetime = task_datetime.replace(day=now.day + 1)

        time_diff = task_datetime - now
        hours = time_diff.seconds // 3600
        minutes = (time_diff.seconds % 3600) // 60

        print(f"   • {task_name}: {task_datetime.strftime('%Y-%m-%d %H:%M')} "
              f"(距离现在: {hours}小时{minutes}分钟)")

    print("
" + "=" * 70)
    print("📋 监控检查完成")
    print(f"🕐 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    check_all_notifications()
