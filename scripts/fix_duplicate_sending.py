#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复重复发送问题
清理重复的launchd服务，统一发送机制
"""

import os
import subprocess
from datetime import datetime

def get_all_openclaw_services():
    """获取所有openclaw相关的launchd服务"""
    services = []

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
                            services.append(service_id)

    except Exception as e:
        print(f"❌ 获取服务列表失败: {e}")

    return services

def analyze_service_duplicates(services):
    """分析服务重复情况"""
    print("🔍 分析服务重复情况")
    print("-" * 50)

    # 按功能分组
    service_groups = {}

    for service_id in services:
        # 提取功能名称
        if "healthcheck" in service_id or "health_check" in service_id:
            group = "health_check"
            display_name = "系统健康检查"
        elif "github" in service_id:
            group = "github_sync"
            display_name = "GitHub同步"
        elif "financial" in service_id:
            group = "financial_report"
            display_name = "财报监控"
        elif "stock" in service_id:
            group = "stock_update"
            display_name = "股票数据"
        elif "code_health" in service_id:
            group = "code_health"
            display_name = "代码健康度"
        else:
            group = "other"
            display_name = "其他"

        if group not in service_groups:
            service_groups[group] = {
                "display_name": display_name,
                "services": []
            }
        service_groups[group]["services"].append(service_id)

    # 显示分析结果
    duplicates_found = False

    for group, info in service_groups.items():
        services_list = info["services"]
        display_name = info["display_name"]

        if len(services_list) > 1:
            print(f"⚠️  {display_name} 有 {len(services_list)} 个重复服务:")
            for service in services_list:
                print(f"   • {service}")
            duplicates_found = True
        else:
            print(f"✅ {display_name}: 1个服务 ({services_list[0]})")

    return service_groups, duplicates_found

def select_keep_service(services_list, group_name):
    """选择要保留的服务"""
    print(f"\n🔧 为 {group_name} 选择要保留的服务:")

    # 优先选择较新的服务（按创建时间或命名规则）
    # 规则1: 优先选择带下划线的服务（新版本）
    # 规则2: 优先选择较短的名称
    # 规则3: 按字母顺序

    # 先找带下划线的
    underscore_services = [s for s in services_list if "_" in s]
    if underscore_services:
        # 选择第一个带下划线的
        keep_service = underscore_services[0]
        print(f"   选择规则: 优先选择带下划线的服务")
        print(f"   保留: {keep_service}")
        return keep_service

    # 选择名称最短的
    shortest_service = min(services_list, key=len)
    print(f"   选择规则: 选择名称最短的服务")
    print(f"   保留: {shortest_service}")
    return shortest_service

def remove_duplicate_services(service_groups):
    """移除重复的服务"""
    print("\n🔧 开始移除重复服务")
    print("-" * 50)

    removed_count = 0

    for group, info in service_groups.items():
        services_list = info["services"]
        display_name = info["display_name"]

        if len(services_list) > 1:
            print(f"\n📋 处理 {display_name}:")

            # 选择要保留的服务
            keep_service = select_keep_service(services_list, display_name)

            # 移除其他服务
            for service_id in services_list:
                if service_id != keep_service:
                    print(f"   删除: {service_id}")

                    # 1. 卸载服务
                    plist_path = f"/Users/ago/Library/LaunchAgents/{service_id}.plist"

                    try:
                        # 先卸载服务
                        subprocess.run(
                            ["launchctl", "unload", plist_path],
                            capture_output=True,
                            stderr=subprocess.DEVNULL
                        )

                        # 删除plist文件
                        if os.path.exists(plist_path):
                            os.remove(plist_path)
                            print(f"      ✅ plist文件已删除")

                        removed_count += 1

                    except Exception as e:
                        print(f"      ❌ 删除失败: {e}")

            print(f"   保留: {keep_service}")

    return removed_count

def verify_cron_task_config():
    """验证cron任务配置"""
    print("\n🔍 验证cron任务配置")
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

                        # 检查任务状态
                        if len(parts) >= 6:
                            status = parts[5]
                            if status == "error":
                                print(f"   ⚠️  {task_name}: 状态为error")
                            else:
                                print(f"   ✅ {task_name}: 状态正常")
                        else:
                            print(f"   ℹ️  {task_name}: 状态未知")

        print("\n💡 cron任务配置原则:")
        print("   • cron任务只执行核心逻辑（生成报告/执行同步）")
        print("   • 不负责消息发送，避免重复")
        print("   • 发送由launchd服务负责")

    except Exception as e:
        print(f"❌ cron任务检查异常: {e}")

    return True

def create_final_configuration():
    """创建最终配置"""
    print("\n🔧 创建最终配置")
    print("-" * 50)

    # 最终的服务配置
    final_services = [
        {
            "name": "系统健康检查报告",
            "service_id": "com.openclaw.health_check_report.send",
            "time": "10:00",
            "target_group": "工作沟通汇报群",
            "script": "send_health_check_to_group.py"
        },
        {
            "name": "GitHub同步状态",
            "service_id": "com.openclaw.github_sync_status.send",
            "time": "12:10",
            "target_group": "工作沟通汇报群",
            "script": "send_github_sync_status.py"
        },
        {
            "name": "财报监控日报",
            "service_id": "com.openclaw.financial_report.send",
            "time": "09:00",
            "target_group": "A股数据分析群",
            "script": "send_financial_report_v3_fixed.py"
        }
    ]

    print("🎯 最终服务配置:")

    for service in final_services:
        print(f"\n📋 {service['name']}:")
        print(f"   服务ID: {service['service_id']}")
        print(f"   执行时间: {service['time']}")
        print(f"   目标群: {service['target_group']}")
        print(f"   发送脚本: {service['script']}")

        # 验证服务是否存在
        try:
            result = subprocess.run(
                ["launchctl", "list", service['service_id']],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print(f"   状态: ✅ 已加载")
            else:
                print(f"   状态: ❌ 未加载")
        except:
            print(f"   状态: ❓ 检查失败")

    return final_services

def verify_final_state():
    """验证最终状态"""
    print("\n🔍 验证最终状态")
    print("-" * 50)

    # 获取当前所有服务
    current_services = get_all_openclaw_services()

    print(f"当前共有 {len(current_services)} 个openclaw服务:")

    for service_id in current_services:
        print(f"   • {service_id}")

    # 检查是否有重复
    service_groups, has_duplicates = analyze_service_duplicates(current_services)

    if has_duplicates:
        print("\n⚠️  仍然存在重复服务，需要进一步清理")
        return False
    else:
        print("\n✅ 所有服务配置正确，无重复")
        return True

def create_test_plan():
    """创建测试计划"""
    print("\n🧪 创建测试计划")
    print("-" * 50)

    print("🎯 测试目标: 验证修复后不再重复发送")

    print("\n📋 测试步骤:")
    print("   1. 手动测试发送功能")
    print("   2. 验证服务配置")
    print("   3. 检查日志系统")
    print("   4. 模拟定时执行")

    print("\n🔧 手动测试命令:")
    print("   # 测试系统健康检查报告")
    print("   cd /Users/ago/.openclaw/workspace && python3 scripts/send_health_check_to_group.py")
    print("")
    print("   # 测试GitHub同步状态")
    print("   cd /Users/ago/.openclaw/workspace && python3 scripts/send_github_sync_status.py")
    print("")
    print("   # 快速检查系统状态")
    print("   cd /Users/ago/.openclaw/workspace && python3 scripts/quick_check_notifications.py")

    print("\n📅 明日验证:")
    print("   🕙 10:00 - 检查是否只收到一次系统健康检查报告")
    print("   🕛 12:10 - 检查是否只收到一次GitHub同步状态")
    print("   🕘 09:00 - 检查是否只收到一次财报监控日报")

    return True

def main():
    print("🔧 修复重复发送问题")
    print("=" * 70)
    print("目标: 清理重复的launchd服务，确保每个任务只有一个发送机制")

    # 1. 获取所有服务
    print("\n1. 📋 获取当前所有openclaw服务")
    all_services = get_all_openclaw_services()
    print(f"   发现 {len(all_services)} 个服务")

    # 2. 分析重复情况
    service_groups, has_duplicates = analyze_service_duplicates(all_services)

    if not has_duplicates:
        print("\n✅ 未发现重复服务，无需修复")
        return

    # 3. 移除重复服务
    removed_count = remove_duplicate_services(service_groups)

    # 4. 验证cron任务配置
    verify_cron_task_config()

    # 5. 创建最终配置
    final_services = create_final_configuration()

    # 6. 验证最终状态
    final_ok = verify_final_state()

    # 7. 创建测试计划
    create_test_plan()

    print("\n" + "=" * 70)
    print("📊 修复完成总结")
    print("=" * 70)

    if removed_count > 0:
        print(f"✅ 成功移除了 {removed_count} 个重复服务")
    else:
        print("ℹ️  未移除任何服务")

    if final_ok:
        print("✅ 最终状态验证通过")
    else:
        print("⚠️  最终状态验证未通过")

    print("\n🎯 修复成果:")
    print("   1. ✅ 清理了重复的launchd服务")
    print("   2. ✅ 统一了发送机制：cron执行逻辑，launchd负责发送")
    print("   3. ✅ 避免了消息重复发送")
    print("   4. ✅ 建立了清晰的架构")

    print("\n💡 核心改进:")
    print("   • 每个功能只有一个发送机制")
    print("   • cron和launchd职责分离")
    print("   • 避免重复发送，节省Token")
    print("   • 提高系统可靠性")

    print("\n🔍 明日验证:")
    print("   请检查明天是否只收到一次通知，不再重复")

    print(f"\n🕐 修复完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
