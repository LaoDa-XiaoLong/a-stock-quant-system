#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终检查通知系统状态
"""

import os
import subprocess
from datetime import datetime

def print_header():
    print("🔔 工作群通知系统最终状态检查")
    print("=" * 70)

def check_current_time():
    """检查当前时间"""
    now = datetime.now()
    print(f"\n🕐 当前系统时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   时区: 北京时间 (GMT+8)")
    return now

def check_launchd_services():
    """检查launchd服务"""
    print("\n🔧 检查macOS launchd定时服务")
    print("-" * 50)

    services = [
        {
            "id": "com.openclaw.healthcheck.send",
            "name": "系统健康检查报告发送",
            "time": "10:00",
            "plist": "/Users/ago/Library/LaunchAgents/com.openclaw.healthcheck.send.plist"
        },
        {
            "id": "com.openclaw.githubsync.send",
            "name": "GitHub同步状态发送",
            "time": "12:10",
            "plist": "/Users/ago/Library/LaunchAgents/com.openclaw.githubsync.send.plist"
        }
    ]

    all_ok = True

    for service in services:
        print(f"\n📋 {service['name']} ({service['time']})")
        print(f"   Service ID: {service['id']}")

        # 检查是否已加载
        try:
            result = subprocess.run(
                ["launchctl", "list", service["id"]],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print(f"   ✅ 服务已加载到launchd系统")
            else:
                print(f"   ❌ 服务未加载")
                all_ok = False
                continue

        except Exception as e:
            print(f"   ❌ 检查失败: {e}")
            all_ok = False
            continue

        # 检查配置文件
        if os.path.exists(service["plist"]):
            print(f"   ✅ 配置文件存在")

            # 检查配置内容
            with open(service["plist"], 'r') as f:
                content = f.read()

            if "StartCalendarInterval" in content:
                # 提取时间配置
                import re
                hour_match = re.search(r'<key>Hour</key>\s*<integer>(\d+)</integer>', content)
                minute_match = re.search(r'<key>Minute</key>\s*<integer>(\d+)</integer>', content)

                if hour_match and minute_match:
                    hour = hour_match.group(1)
                    minute = minute_match.group(1).zfill(2)
                    print(f"   ✅ 定时配置: 每天 {hour}:{minute}")
                else:
                    print(f"   ⚠️  时间配置解析失败")
            else:
                print(f"   ❌ 未使用日历定时器")
                all_ok = False
        else:
            print(f"   ❌ 配置文件不存在")
            all_ok = False

    return all_ok

def calculate_next_executions(now):
    """计算下次执行时间"""
    print("\n⏰ 下次执行时间预测")
    print("-" * 50)

    # 健康检查报告 (10:00)
    health_check_time = now.replace(hour=10, minute=0, second=0, microsecond=0)
    if now > health_check_time:
        health_check_time = health_check_time.replace(day=now.day + 1)

    time_diff = health_check_time - now
    hours = time_diff.seconds // 3600
    minutes = (time_diff.seconds % 3600) // 60

    print(f"📊 系统健康检查报告:")
    print(f"   • 计划时间: 每天10:00")
    print(f"   • 下次执行: {health_check_time.strftime('%Y-%m-%d %H:%M')}")
    print(f"   • 距离现在: {hours}小时{minutes}分钟")

    # GitHub同步状态 (12:10)
    github_sync_time = now.replace(hour=12, minute=10, second=0, microsecond=0)
    if now > github_sync_time:
        github_sync_time = github_sync_time.replace(day=now.day + 1)

    time_diff = github_sync_time - now
    hours = time_diff.seconds // 3600
    minutes = (time_diff.seconds % 3600) // 60

    print(f"\n🔄 GitHub同步状态:")
    print(f"   • 计划时间: 每天12:10")
    print(f"   • 下次执行: {github_sync_time.strftime('%Y-%m-%d %H:%M')}")
    print(f"   • 距离现在: {hours}小时{minutes}分钟")

    return health_check_time, github_sync_time

def check_old_configs():
    """检查旧的错误配置"""
    print("\n🧹 检查旧的错误配置")
    print("-" * 50)

    old_plist = "/Users/ago/Library/LaunchAgents/com.openclaw.workgroup.notifications.plist"

    if os.path.exists(old_plist):
        print(f"❌ 发现旧的错误配置文件: {old_plist}")
        print(f"   这个配置会导致每小时发送，建议删除")

        # 检查是否还在运行
        try:
            result = subprocess.run(
                ["launchctl", "list", "com.openclaw.workgroup.notifications"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print(f"   ⚠️  旧服务仍在运行，建议卸载")
            else:
                print(f"   ✅ 旧服务未运行")
        except:
            pass
    else:
        print(f"✅ 旧的错误配置文件已清理")

def provide_management_commands():
    """提供管理命令"""
    print("\n🔧 系统管理命令参考")
    print("-" * 50)

    print("查看所有OpenClaw相关服务:")
    print("  launchctl list | grep openclaw")

    print("\n查看特定服务状态:")
    print("  launchctl list com.openclaw.healthcheck.send")
    print("  launchctl list com.openclaw.githubsync.send")

    print("\n手动触发测试发送:")
    print("  cd /Users/ago/.openclaw/workspace && python3 scripts/send_health_check_to_group.py")
    print("  cd /Users/ago/.openclaw/workspace && python3 scripts/send_github_sync_status.py")

    print("\n查看日志文件:")
    print("  tail -f /Users/ago/.openclaw/workspace/logs/health_check_send_launchd.log")
    print("  tail -f /Users/ago/.openclaw/workspace/logs/github_sync_send_launchd.log")

def main():
    print_header()

    # 检查当前时间
    now = check_current_time()

    # 检查launchd服务
    services_ok = check_launchd_services()

    # 计算下次执行时间
    calculate_next_executions(now)

    # 检查旧的错误配置
    check_old_configs()

    # 提供管理命令
    provide_management_commands()

    # 总结
    print("\n" + "=" * 70)
    print("📋 最终状态总结")
    print("=" * 70)

    if services_ok:
        print("✅ 工作群通知系统配置正确！")
        print("\n🎯 配置要点:")
        print("   1. 使用macOS launchd日历定时器，每天固定时间执行")
        print("   2. 两个独立服务，互不干扰")
        print("   3. 系统级可靠性，开机自动运行")
        print("   4. 完整的日志记录和错误处理")

        print("\n📅 执行计划:")
        print("   • 系统健康检查报告: 每天10:00")
        print("   • GitHub同步状态: 每天12:10")

        print("\n💡 提示:")
        print("   - 系统将在上述时间自动发送通知到工作群")
        print("   - 无需人工干预，完全自动化")
        print("   - 如有问题，可查看日志文件排查")
    else:
        print("⚠️  系统配置需要检查")
        print("   请查看上述详细检查结果，部分服务可能未正确配置")

    print(f"\n🕐 检查完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
