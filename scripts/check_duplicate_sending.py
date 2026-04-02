#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查重复发送问题
分析所有调度配置，找出消息重复发送的原因
"""

import os
import json
import subprocess
from datetime import datetime

def analyze_all_schedulers():
    """分析所有调度器配置"""
    print("🔍 分析所有调度器配置，查找重复发送原因")
    print("=" * 70)

    # 1. 检查cron任务
    print("\n1. ⏰ 检查OpenClaw cron任务:")
    print("-" * 50)

    try:
        result = subprocess.run(
            ["openclaw", "cron", "list"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 3:
                tasks = lines[2:]

                print(f"发现 {len(tasks)} 个cron任务:")

                for task_line in tasks:
                    parts = task_line.split()
                    if len(parts) >= 2:
                        task_id = parts[0]
                        task_name = parts[1]

                        # 获取任务详情
                        detail_result = subprocess.run(
                            ["openclaw", "cron", "get", task_id],
                            capture_output=True,
                            text=True
                        )

                        if detail_result.returncode == 0:
                            try:
                                task_detail = json.loads(detail_result.stdout)
                                schedule = task_detail.get("schedule", {})
                                cron_expr = schedule.get("cron", "")

                                print(f"   • {task_name}: {cron_expr}")

                                # 检查是否有delivery配置
                                if "delivery" in task_detail:
                                    delivery = task_detail["delivery"]
                                    print(f"      ⚠️  有delivery配置: {delivery.get('mode', 'unknown')}")

                            except:
                                print(f"   • {task_name}: 详情解析失败")
                        else:
                            print(f"   • {task_name}: 获取详情失败")
                    else:
                        print(f"   ⚠️  无法解析任务行: {task_line}")
        else:
            print("❌ 无法获取cron任务列表")

    except Exception as e:
        print(f"❌ cron任务检查异常: {e}")

    # 2. 检查launchd服务
    print("\n2. 🚀 检查macOS launchd服务:")
    print("-" * 50)

    launchd_services = []

    # 查找所有openclaw相关的launchd服务
    try:
        result = subprocess.run(
            ["launchctl", "list"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if "openclaw" in line.lower():
                    parts = line.split()
                    if len(parts) >= 3:
                        service_id = parts[2]
                        if "openclaw" in service_id:
                            launchd_services.append(service_id)

        print(f"发现 {len(launchd_services)} 个openclaw相关的launchd服务:")

        for service_id in launchd_services:
            print(f"   • {service_id}")

            # 检查plist文件
            plist_path = f"/Users/ago/Library/LaunchAgents/{service_id}.plist"
            if os.path.exists(plist_path):
                try:
                    with open(plist_path, 'r') as f:
                        content = f.read()

                        # 检查执行时间
                        if "StartCalendarInterval" in content:
                            print(f"      📅 有定时执行配置")

                        # 检查执行脚本
                        if "ProgramArguments" in content:
                            print(f"      📝 有执行脚本")
                except:
                    print(f"      ❓ plist文件读取失败")
            else:
                print(f"      ❌ plist文件不存在")

    except Exception as e:
        print(f"❌ launchd服务检查异常: {e}")

    # 3. 检查重复的服务
    print("\n3. 🔍 检查可能的重复配置:")
    print("-" * 50)

    # 按功能分组服务
    service_groups = {}

    for service_id in launchd_services:
        # 提取功能名称
        if "healthcheck" in service_id or "health_check" in service_id:
            group = "系统健康检查"
        elif "github" in service_id:
            group = "GitHub同步"
        elif "financial" in service_id:
            group = "财报监控"
        elif "stock" in service_id:
            group = "股票数据"
        else:
            group = "其他"

        if group not in service_groups:
            service_groups[group] = []
        service_groups[group].append(service_id)

    # 显示重复配置
    has_duplicates = False

    for group, services in service_groups.items():
        if len(services) > 1:
            print(f"⚠️  {group} 有 {len(services)} 个重复服务:")
            for service in services:
                print(f"   • {service}")
            has_duplicates = True
        else:
            print(f"✅ {group}: 1个服务 ({services[0]})")

    if has_duplicates:
        print("\n🎯 发现重复配置！这可能导致消息重复发送")
    else:
        print("\n✅ 未发现重复配置")

    return launchd_services, service_groups

def check_sending_logs():
    """检查发送日志"""
    print("\n4. 📊 检查发送日志:")
    print("-" * 50)

    log_dirs = [
        "/Users/ago/.openclaw/workspace/logs/health_check_send",
        "/Users/ago/.openclaw/workspace/logs/github_sync_send"
    ]

    for log_dir in log_dirs:
        if os.path.exists(log_dir):
            log_files = [f for f in os.listdir(log_dir) if f.endswith('.json')]
            print(f"\n📁 {os.path.basename(log_dir)}: {len(log_files)}个日志文件")

            if log_files:
                # 按时间排序
                log_files.sort(reverse=True)

                # 检查最近的5个日志
                recent_logs = log_files[:5]

                for log_file in recent_logs:
                    log_path = os.path.join(log_dir, log_file)
                    try:
                        with open(log_path, 'r') as f:
                            log_data = json.load(f)

                        timestamp = log_data.get("timestamp", "未知时间")
                        task = log_data.get("task", "未知任务")
                        status = log_data.get("status", "未知状态")

                        print(f"   • {log_file}")
                        print(f"     任务: {task}, 状态: {status}, 时间: {timestamp}")

                    except Exception as e:
                        print(f"   • {log_file}: 日志解析失败 - {e}")
        else:
            print(f"\n📁 {os.path.basename(log_dir)}: 目录不存在")

    return True

def analyze_duplicate_causes(service_groups):
    """分析重复发送的原因"""
    print("\n5. 🎯 分析重复发送的可能原因:")
    print("-" * 50)

    possible_causes = []

    # 检查重复的服务
    for group, services in service_groups.items():
        if len(services) > 1:
            possible_causes.append(f"• {group} 有 {len(services)} 个重复的launchd服务")

    # 检查cron和launchd的重复
    print("检查cron任务和launchd服务的重复:")

    cron_tasks = ["系统健康检查", "GitHub自动同步", "财报监控日报", "股票数据自动更新"]

    for task in cron_tasks:
        # 检查是否有对应的launchd服务
        launchd_count = 0
        for group, services in service_groups.items():
            if task in group:
                launchd_count = len(services)
                break

        if launchd_count > 0:
            print(f"   ⚠️  {task}: 既有cron任务又有{launchd_count}个launchd服务")
            possible_causes.append(f"• {task} 既有cron任务又有launchd服务，可能导致重复执行")
        else:
            print(f"   ✅ {task}: 只有cron任务")

    # 显示所有可能原因
    if possible_causes:
        print("\n🔍 可能的重复发送原因:")
        for cause in possible_causes:
            print(f"   {cause}")

        print("\n💡 问题分析:")
        print("   1. 早上9点A股数据分析群收到重复消息")
        print("   2. 工作沟通汇报群也有重复消息")
        print("   3. 可能原因：cron任务和launchd服务都触发了发送")
    else:
        print("\n✅ 未发现明显的重复发送原因")

    return possible_causes

def create_fix_plan(possible_causes):
    """创建修复计划"""
    print("\n6. 🔧 创建修复计划:")
    print("-" * 50)

    if not possible_causes:
        print("✅ 无需修复，未发现重复发送问题")
        return []

    print("🎯 修复目标: 确保每个任务只有一个发送机制")
    print("\n📋 修复步骤:")

    fix_steps = []

    # 针对重复服务的修复
    for cause in possible_causes:
        if "重复的launchd服务" in cause:
            group = cause.split("• ")[1].split(" 有")[0]
            print(f"\n1. 修复 {group} 的重复launchd服务:")
            print(f"   • 保留一个最新的launchd服务")
            print(f"   • 删除其他重复的服务")
            fix_steps.append(f"清理 {group} 的重复launchd服务")

    # 针对cron和launchd重复的修复
    if "既有cron任务又有launchd服务" in str(possible_causes):
        print("\n2. 修复cron和launchd的重复:")
        print("   • 方案A: 禁用cron任务的发送功能，只使用launchd")
        print("   • 方案B: 禁用launchd服务，只使用cron")
        print("   • 推荐方案A: launchd更可靠，cron只执行核心逻辑")
        fix_steps.append("统一发送机制：cron执行逻辑，launchd负责发送")

    print("\n🎯 最终架构:")
    print("   • cron任务: 只执行核心逻辑（生成报告/执行同步）")
    print("   • launchd服务: 定时触发发送任务")
    print("   • Python脚本: 通过Webhook发送到正确群聊")
    print("   • 日志系统: 记录所有操作状态")

    return fix_steps

def main():
    print("🔍 检查重复发送问题分析")
    print("=" * 70)
    print("目标: 找出消息重复发送的原因并制定修复方案")

    # 1. 分析所有调度器
    launchd_services, service_groups = analyze_all_schedulers()

    # 2. 检查发送日志
    check_sending_logs()

    # 3. 分析重复原因
    possible_causes = analyze_duplicate_causes(service_groups)

    # 4. 创建修复计划
    fix_steps = create_fix_plan(possible_causes)

    print("\n" + "=" * 70)
    print("📊 分析完成总结")
    print("=" * 70)

    if possible_causes:
        print("⚠️  发现重复发送问题!")

        print("\n🔍 问题现象:")
        print("   1. 早上9点A股数据分析群收到重复消息")
        print("   2. 工作沟通汇报群也有重复消息")

        print("\n🎯 根本原因:")
        for cause in possible_causes:
            print(f"   {cause}")

        print("\n🔧 修复方案:")
        for step in fix_steps:
            print(f"   • {step}")

        print("\n💡 建议:")
        print("   立即执行修复，避免明天继续重复发送")

    else:
        print("✅ 未发现重复发送问题")
        print("\n💡 建议:")
        print("   继续监控明天的发送情况")

    print(f"\n🕐 分析完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
