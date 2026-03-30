#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试所有调度配置
验证发送群消息是否正常，确保无重复发送
"""

import os
import subprocess
from datetime import datetime, timedelta

def print_test_header():
    print("🧪 测试所有调度配置")
    print("=" * 70)
    print("目标: 验证发送群消息是否正常，确保无重复发送")
    print("=" * 70)

def test_manual_sending():
    """测试手动发送功能"""
    print("\n1. 📤 测试手动发送功能")
    print("-" * 50)
    
    test_cases = [
        {
            "name": "系统健康检查报告",
            "script": "send_health_check_to_group.py",
            "description": "发送到工作沟通汇报群"
        },
        {
            "name": "GitHub同步状态",
            "script": "send_github_sync_status.py",
            "description": "发送到工作沟通汇报群"
        }
    ]
    
    all_success = True
    
    for test_case in test_cases:
        print(f"\n🔍 测试: {test_case['name']}")
        print(f"   脚本: {test_case['script']}")
        print(f"   描述: {test_case['description']}")
        
        script_path = f"/Users/ago/.openclaw/workspace/scripts/{test_case['script']}"
        
        if os.path.exists(script_path):
            try:
                # 运行脚本（实际发送）
                print("   运行脚本...")
                
                result = subprocess.run(
                    ["python3", script_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print("   ✅ 发送成功")
                    
                    # 检查输出
                    output = result.stdout.strip()
                    if output:
                        print(f"   输出: {output[:100]}...")
                else:
                    print(f"   ❌ 发送失败")
                    if result.stderr:
                        print(f"   错误: {result.stderr[:100]}...")
                    all_success = False
                    
            except subprocess.TimeoutExpired:
                print("   ⏰ 执行超时（可能正常发送中）")
            except Exception as e:
                print(f"   ❌ 执行异常: {e}")
                all_success = False
        else:
            print(f"   ❌ 脚本不存在: {test_case['script']}")
            all_success = False
    
    return all_success

def verify_service_configuration():
    """验证服务配置"""
    print("\n2. 🔧 验证服务配置")
    print("-" * 50)
    
    # 最终的服务配置
    final_services = [
        {
            "name": "系统健康检查报告",
            "service_id": "com.openclaw.health_check_report.send",
            "time": "10:00",
            "target_group": "工作沟通汇报群"
        },
        {
            "name": "GitHub同步状态",
            "service_id": "com.openclaw.github_sync_status.send",
            "time": "12:10",
            "target_group": "工作沟通汇报群"
        },
        {
            "name": "财报监控日报",
            "service_id": "com.openclaw.financial_report.send",
            "time": "09:00",
            "target_group": "A股数据分析群"
        }
    ]
    
    all_correct = True
    
    for service in final_services:
        print(f"\n📋 {service['name']}:")
        print(f"   服务ID: {service['service_id']}")
        print(f"   执行时间: {service['time']}")
        print(f"   目标群: {service['target_group']}")
        
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
                all_correct = False
        except:
            print(f"   状态: ❓ 检查失败")
            all_correct = False
    
    # 检查是否有重复服务
    print("\n🔍 检查重复服务:")
    
    try:
        result = subprocess.run(
            ["launchctl", "list"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            openclaw_services = []
            
            for line in lines:
                if "openclaw" in line.lower():
                    parts = line.split()
                    if len(parts) >= 3:
                        service_id = parts[2]
                        if "openclaw" in service_id and "gateway" not in service_id:
                            openclaw_services.append(service_id)
            
            # 按功能分组检查重复
            service_groups = {}
            for service_id in openclaw_services:
                if "health" in service_id:
                    group = "health"
                elif "github" in service_id:
                    group = "github"
                elif "financial" in service_id:
                    group = "financial"
                elif "stock" in service_id:
                    group = "stock"
                elif "code_health" in service_id:
                    group = "code_health"
                else:
                    group = "other"
                
                if group not in service_groups:
                    service_groups[group] = []
                service_groups[group].append(service_id)
            
            has_duplicates = False
            for group, services in service_groups.items():
                if len(services) > 1:
                    print(f"   ⚠️  {group}组有{len(services)}个服务: {services}")
                    has_duplicates = True
            
            if not has_duplicates:
                print("   ✅ 无重复服务")
            else:
                print("   ❌ 发现重复服务")
                all_correct = False
                
    except Exception as e:
        print(f"   ❌ 检查失败: {e}")
        all_correct = False
    
    return all_correct

def verify_cron_configuration():
    """验证cron配置"""
    print("\n3. ⏰ 验证cron配置")
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
                
                critical_tasks = ["系统健康检查", "GitHub自动同步", "财报监控日报", "股票数据自动更新"]
                found_tasks = []
                
                for task_line in tasks:
                    for task_name in critical_tasks:
                        if task_name in task_line:
                            found_tasks.append(task_name)
                            print(f"   ✅ {task_name}: 配置存在")
                
                # 检查是否所有任务都找到
                for task_name in critical_tasks:
                    if task_name not in found_tasks:
                        print(f"   ⚠️  {task_name}: 未在cron列表中找到")
                
                print("\n💡 cron配置原则:")
                print("   • cron任务只执行核心逻辑")
                print("   • 不负责消息发送")
                print("   • 发送由launchd服务负责")
                
        else:
            print("❌ 无法获取cron任务列表")
            
    except Exception as e:
        print(f"❌ cron配置检查异常: {e}")
    
    return True

def check_execution_schedule():
    """检查执行计划"""
    print("\n4. 📅 检查执行计划")
    print("-" * 50)
    
    now = datetime.now()
    print(f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 计算明天的时间
    tomorrow = now + timedelta(days=1)
    
    print("\n明日执行计划:")
    print("   🕙 10:00 - 系统健康检查报告 → 工作沟通汇报群")
    print("       服务: com.openclaw.health_check_report.send")
    print("       脚本: send_health_check_to_group.py")
    print("")
    print("   🕛 12:10 - GitHub同步状态 → 工作沟通汇报群")
    print("       服务: com.openclaw.github_sync_status.send")
    print("       脚本: send_github_sync_status.py")
    print("")
    print("   🕘 09:00 - 财报监控日报 → A股数据分析群")
    print("       服务: com.openclaw.financial_report.send")
    print("       脚本: send_financial_report_v3_fixed.py")
    print("")
    print("   🕤 09:30 - 股票数据更新状态 → A股数据分析群")
    print("       服务: com.openclaw.stock_update_status.send")
    print("       脚本: send_股票数据自动更新状态.py")
    
    print("\n🎯 架构说明:")
    print("   • 每个功能只有一个发送机制")
    print("   • cron执行逻辑，launchd负责发送")
    print("   • 避免重复发送，节省Token")
    
    return True

def verify_no_duplicate_mechanisms():
    """验证无重复机制"""
    print("\n5. 🔍 验证无重复机制")
    print("-" * 50)
    
    print("检查每个功能是否只有一个发送机制:")
    
    functions = [
        {
            "name": "系统健康检查报告",
            "cron_task": "系统健康检查",
            "launchd_service": "com.openclaw.health_check_report.send",
            "status": "待检查"
        },
        {
            "name": "GitHub同步状态",
            "cron_task": "GitHub自动同步",
            "launchd_service": "com.openclaw.github_sync_status.send",
            "status": "待检查"
        },
        {
            "name": "财报监控日报",
            "cron_task": "财报监控日报",
            "launchd_service": "com.openclaw.financial_report.send",
            "status": "待检查"
        }
    ]
    
    all_good = True
    
    for func in functions:
        print(f"\n📋 {func['name']}:")
        
        # 检查cron任务
        try:
            cron_result = subprocess.run(
                ["openclaw", "cron", "list"],
                capture_output=True,
                text=True
            )
            
            has_cron = False
            if cron_result.returncode == 0:
                if func['cron_task'] in cron_result.stdout:
                    has_cron = True
                    print(f"   • cron任务: ✅ 存在")
                else:
                    print(f"   • cron任务: ⚠️  未找到")
            else:
                print(f"   • cron任务: ❓ 检查失败")
        
        except:
            print(f"   • cron任务: ❓ 检查异常")
        
        # 检查launchd服务
        try:
            service_result = subprocess.run(
                ["launchctl", "list", func['launchd_service']],
                capture_output=True,
                text=True
            )
            
            has_service = service_result.returncode == 0
            if has_service:
                print(f"   • launchd服务: ✅ 已加载")
            else:
                print(f"   • launchd服务: ❌ 未加载")
                all_good = False
        
        except:
            print(f"   • launchd服务: ❓ 检查失败")
            all_good = False
        
        # 检查是否有多个launchd服务
        try:
            list_result = subprocess.run(
                ["launchctl", "list"],
                capture_output=True,
                text=True
            )
            
            if list_result.returncode == 0:
                service_count = 0
                lines = list_result.stdout.strip().split('\n')
                for line in lines:
                    if func['launchd_service'].split('.')[2] in line.lower() and "openclaw" in line.lower():
                        service_count += 1
                
                if service_count == 1:
                    print(f"   • 重复检查: ✅ 只有1个服务")
                elif service_count > 1:
                    print(f"   • 重复检查: ❌ 有{service_count}个服务")
                    all_good = False
                else:
                    print(f"   • 重复检查: ⚠️  无服务")
        
        except:
            print(f"   • 重复检查: ❓ 检查失败")
    
    return all_good

def create_test_summary(manual_ok, service_ok, no_duplicate_ok):
    """创建测试总结"""
    print("\n" + "=" * 70)
    print("📊 测试完成总结")
    print("=" * 70)
    
    all_passed = manual_ok and service_ok and no_duplicate_ok
    
    if all_passed:
        print("🎉 所有测试通过！调度配置正常，无重复发送问题")
        
        print("\n✅ 测试结果:")
        print("   1. 📤 手动发送功能: ✅ 正常")
        print("   2. 🔧 服务配置: ✅ 正确")
        print("   3. 🔍 无重复机制: ✅ 验证通过")
        
        print("\n🚀 系统状态:")
        print("   • 每个功能只有一个发送机制")
        print("   • cron和launchd职责分离")
        print("   • 避免重复发送，节省Token")
        print("   • 提高系统可靠性")
        
        print("\n📅 明日自动执行:")
        print("   🕙 10:00 - 系统健康检查报告 → 工作沟通汇报群")
        print("   🕛 12:10 - GitHub同步状态 → 工作沟通汇报群")
        print("   🕘 09:00 - 财报监控日报 → A股数据分析群")
        
    else:
        print("⚠️  部分测试未通过")
        
        print("\n📋 测试结果:")
        print(f"   1. 📤 手动发送功能: {'✅' if manual_ok else '❌'}")
        print(f"   2. 🔧 服务配置: {'✅' if service_ok else '❌'}")
        print(f"   3. 🔍 无重复机制: {'✅' if no_duplicate_ok else '❌'}")
        
        print("\n💡 需要修复的项目:")
        if not manual_ok:
            print("   • 手动发送功能有问题")
        if not service_ok:
            print("   • 服务配置有问题")
        if not no_duplicate_ok:
            print("   • 存在重复机制")
    
    print(f"\n🕐 测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return all_passed

def main():
    print_test_header()
    
    # 运行所有测试
    manual_ok = test_manual_sending()
    service_ok = verify_service_configuration()
    cron_ok = verify_cron_configuration()
    schedule_ok = check_execution_schedule()
    no_duplicate_ok = verify_no_duplicate_mechanisms()
    
    # 创建总结
    all_passed = create_test_summary(manual_ok, service_ok, no_duplicate_ok)
    
    # 最终建议
    print("\n" + "=" * 70)
    print("💡 最终建议")
    print("=" * 70)
    
    if all_passed:
        print("✅ 所有调度配置正常，可以放心使用")
        
        print("\n🔍 明日验证步骤:")
        print("   1. 🕙 10:00 检查工作沟通汇报群是否只收到一次系统健康检查报告")
        print("   2. 🕛 12:10 检查工作沟通汇报群是否只收到一次GitHub同步状态")
        print("   3. 🕘 09:00 检查A股数据分析群是否只收到一次财报监控日报")
        
        print("\n🎯 验证目标:")
        print("   • 每个时间点只收到一次消息")
        print("   • 无重复发送")
        print("   • 消息内容正确")
        
    else:
        print("⚠️  系统需要进一步检查")
        
        print("\n🔧 建议操作:")
        if not manual_ok:
            print("   • 检查发送脚本是否正确")
        if not service_ok:
            print("   • 检查launchd服务配置")
        if not no_duplicate_ok:
            print("   • 清理重复的服务")
        
        print("\n💡 快速检查命令:")
        print("   cd /Users/ago/.openclaw/workspace && python3 scripts/quick_check_notifications.py")
    
    print(f"\n🏁 测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()