#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查工作群通知系统状态
"""

import os
import json
import subprocess
from datetime import datetime

def check_service_status():
    """检查服务状态"""
    print("🔍 检查工作群通知系统状态")
    print("=" * 60)

    # 1. 检查LaunchAgent状态
    print("1. 检查LaunchAgent服务状态...")
    try:
        result = subprocess.run(
            ["launchctl", "list", "com.openclaw.workgroup.notifications"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                pid_status = lines[1].split()
                if len(pid_status) >= 2:
                    pid = pid_status[0]
                    status = pid_status[1]
                    if pid != "-" and status == "0":
                        print(f"   ✅ 服务运行正常 (PID: {pid})")
                    else:
                        print(f"   ⚠️  服务未运行或异常")
            else:
                print("   ✅ 服务已加载")
        else:
            print("   ❌ 服务未找到")
    except Exception as e:
        print(f"   ❌ 检查失败: {e}")

    # 2. 检查配置文件
    print("\n2. 检查配置文件...")
    config_dir = "/Users/ago/.openclaw/workspace/config/cron_jobs"

    config_files = [
        ("health_check_send.json", "系统健康检查报告发送"),
        ("github_sync_send.json", "GitHub同步状态发送")
    ]

    all_configs_ok = True
    for filename, description in config_files:
        filepath = os.path.join(config_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print(f"   ✅ {description}: {config.get('schedule', '未知时间')}")
            except Exception as e:
                print(f"   ❌ {description}: 配置文件损坏 - {e}")
                all_configs_ok = False
        else:
            print(f"   ❌ {description}: 配置文件不存在")
            all_configs_ok = False

    # 3. 检查脚本文件
    print("\n3. 检查脚本文件...")
    script_files = [
        ("send_health_check_to_group.py", "健康检查报告发送脚本"),
        ("send_github_sync_status.py", "GitHub同步状态发送脚本"),
        ("setup_work_group_notifications.py", "通知系统设置脚本")
    ]

    all_scripts_ok = True
    for filename, description in script_files:
        filepath = os.path.join("/Users/ago/.openclaw/workspace/scripts", filename)
        if os.path.exists(filepath):
            print(f"   ✅ {description}: 存在")
        else:
            print(f"   ❌ {description}: 不存在")
            all_scripts_ok = False

    # 4. 检查日志目录
    print("\n4. 检查日志系统...")
    log_dirs = [
        "/Users/ago/.openclaw/workspace/logs/health_check_send",
        "/Users/ago/.openclaw/workspace/logs/github_sync_send"
    ]

    for log_dir in log_dirs:
        if os.path.exists(log_dir):
            # 统计日志文件数量
            log_files = [f for f in os.listdir(log_dir) if f.endswith('.json')]
            print(f"   ✅ {os.path.basename(log_dir)}: {len(log_files)}个日志文件")
        else:
            print(f"   ⚠️  {os.path.basename(log_dir)}: 目录不存在")

    # 5. 检查下次执行时间
    print("\n5. 下次执行时间...")
    now = datetime.now()

    # 健康检查报告 (10:00)
    health_check_time = now.replace(hour=10, minute=0, second=0, microsecond=0)
    if now > health_check_time:
        health_check_time = health_check_time.replace(day=now.day + 1)

    # GitHub同步状态 (12:10)
    github_sync_time = now.replace(hour=12, minute=10, second=0, microsecond=0)
    if now > github_sync_time:
        github_sync_time = github_sync_time.replace(day=now.day + 1)

    print(f"   📊 系统健康检查报告: {health_check_time.strftime('%Y-%m-%d %H:%M')}")
    print(f"   🔄 GitHub同步状态: {github_sync_time.strftime('%Y-%m-%d %H:%M')}")

    # 6. 总体状态评估
    print("\n" + "=" * 60)
    print("📋 总体状态评估")

    if all_configs_ok and all_scripts_ok:
        print("✅ 工作群通知系统状态: 正常")
        print("   所有组件就绪，等待定时执行")
    else:
        print("⚠️  工作群通知系统状态: 需要检查")
        print("   部分组件存在问题，请查看上述检查结果")

    print(f"\n🕐 当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print("💡 提示: 如需立即测试，可手动运行发送脚本")

def main():
    check_service_status()

if __name__ == "__main__":
    main()
