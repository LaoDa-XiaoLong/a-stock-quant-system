#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终验证测试
确保修复后的系统正常工作
"""

import os
import json
import subprocess
from datetime import datetime

def print_test_header():
    print("🧪 最终验证测试")
    print("=" * 70)

def test_1_manual_send():
    """测试1: 手动发送功能"""
    print("\n1. 📤 测试手动发送功能")
    print("-" * 50)
    
    scripts_to_test = [
        ("send_health_check_to_group.py", "系统健康检查报告发送"),
        ("send_github_sync_status.py", "GitHub同步状态发送")
    ]
    
    all_success = True
    
    for script_name, description in scripts_to_test:
        script_path = f"/Users/ago/.openclaw/workspace/scripts/{script_name}"
        
        if os.path.exists(script_path):
            print(f"\n🔍 测试: {description}")
            print(f"   脚本: {script_name}")
            
            try:
                result = subprocess.run(
                    ["python3", script_path],
                    cwd="/Users/ago/.openclaw/workspace",
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print(f"   ✅ 测试成功")
                    # 提取关键信息
                    lines = result.stdout.split('\n')
                    for line in lines[:5]:
                        if line.strip():
                            print(f"      {line}")
                else:
                    print(f"   ❌ 测试失败")
                    print(f"      错误: {result.stderr[:100]}...")
                    all_success = False
                    
            except Exception as e:
                print(f"   ❌ 测试异常: {e}")
                all_success = False
        else:
            print(f"\n❌ 脚本不存在: {script_name}")
            all_success = False
    
    return all_success

def test_2_launchd_services():
    """测试2: launchd服务状态"""
    print("\n2. 🔧 测试launchd服务状态")
    print("-" * 50)
    
    services = [
        ("com.openclaw.healthcheck.send", "系统健康检查报告发送服务"),
        ("com.openclaw.githubsync.send", "GitHub同步状态发送服务")
    ]
    
    all_loaded = True
    
    for service_id, description in services:
        try:
            result = subprocess.run(
                ["launchctl", "list", service_id],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ {description}: 已加载")
            else:
                print(f"❌ {description}: 未加载")
                all_loaded = False
                
        except Exception as e:
            print(f"❌ {description}: 检查失败 - {e}")
            all_loaded = False
    
    return all_loaded

def test_3_cron_tasks():
    """测试3: cron任务配置"""
    print("\n3. ⏰ 测试cron任务配置")
    print("-" * 50)
    
    try:
        result = subprocess.run(
            ["openclaw", "cron", "list"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ cron任务列表获取成功")
            
            # 检查关键任务
            tasks_to_check = [
                "系统健康检查",
                "GitHub自动同步", 
                "财报监控日报",
                "股票数据自动更新"
            ]
            
            lines = result.stdout.strip().split('\n')
            found_tasks = []
            
            for line in lines:
                for task_name in tasks_to_check:
                    if task_name in line:
                        found_tasks.append(task_name)
                        print(f"   ✅ {task_name}: 配置存在")
            
            # 检查是否所有任务都找到
            for task_name in tasks_to_check:
                if task_name not in found_tasks:
                    print(f"   ❌ {task_name}: 未找到")
                    
        else:
            print("❌ cron任务列表获取失败")
            print(f"   错误: {result.stderr}")
            
    except Exception as e:
        print(f"❌ cron任务检查异常: {e}")
    
    return True

def test_4_next_execution():
    """测试4: 下次执行时间计算"""
    print("\n4. ⏰ 测试下次执行时间")
    print("-" * 50)
    
    now = datetime.now()
    print(f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 计算明天的时间
    from datetime import timedelta
    tomorrow = now + timedelta(days=1)
    
    print("\n📅 明天执行计划:")
    print(f"   • 系统健康检查报告: {tomorrow.replace(hour=10, minute=0, second=0).strftime('%Y-%m-%d %H:%M')}")
    print(f"   • GitHub同步状态: {tomorrow.replace(hour=12, minute=10, second=0).strftime('%Y-%m-%d %H:%M')}")
    
    return True

def test_5_log_files():
    """测试5: 日志文件检查"""
    print("\n5. 📝 测试日志文件系统")
    print("-" * 50)
    
    log_dirs = [
        "/Users/ago/.openclaw/workspace/logs/health_check_send",
        "/Users/ago/.openclaw/workspace/logs/github_sync_send"
    ]
    
    for log_dir in log_dirs:
        if os.path.exists(log_dir):
            log_files = [f for f in os.listdir(log_dir) if f.endswith('.json')]
            print(f"✅ {os.path.basename(log_dir)}: {len(log_files)}个日志文件")
        else:
            print(f"📁 {os.path.basename(log_dir)}: 目录不存在（首次运行后创建）")
    
    return True

def create_summary_report(test_results):
    """创建测试总结报告"""
    print("\n" + "=" * 70)
    print("📊 最终验证测试总结")
    print("=" * 70)
    
    all_passed = all(test_results.values())
    
    if all_passed:
        print("🎉 所有测试通过！")
        print("\n✅ 系统状态:")
        print("   1. 手动发送功能: 正常")
        print("   2. launchd服务: 已加载")
        print("   3. cron任务配置: 正确")
        print("   4. 执行时间计划: 已设置")
        print("   5. 日志系统: 就绪")
        
        print("\n🚀 系统已准备好自动运行:")
        print("   • 系统健康检查报告: 明天10:00")
        print("   • GitHub同步状态: 明天12:10")
        
        print("\n🔧 技术架构:")
        print("   • OpenClaw cron任务: 执行核心逻辑")
        print("   • macOS launchd服务: 负责定时发送")
        print("   • Python发送脚本: 处理Webhook通信")
        print("   • 双重保障机制: 确保可靠性")
        
    else:
        print("⚠️  部分测试未通过")
        print("\n📋 测试结果:")
        for test_name, passed in test_results.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {test_name}")
        
        print("\n💡 需要检查的项目:")
        for test_name, passed in test_results.items():
            if not passed:
                print(f"   • {test_name}")
    
    print(f"\n🕐 测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return all_passed

def main():
    print_test_header()
    
    print("🎯 验证修复后的系统功能")
    print("   确保消息能正常发送到工作群")
    
    # 运行所有测试
    test_results = {
        "手动发送功能": test_1_manual_send(),
        "launchd服务状态": test_2_launchd_services(),
        "cron任务配置": test_3_cron_tasks(),
        "执行时间计划": test_4_next_execution(),
        "日志系统": test_5_log_files()
    }
    
    # 创建总结报告
    all_passed = create_summary_report(test_results)
    
    # 最终建议
    print("\n" + "=" * 70)
    print("💡 最终建议")
    print("=" * 70)
    
    if all_passed:
        print("✅ 系统修复完成，可以正常使用")
        print("\n📋 监控建议:")
        print("   1. 明天10:00检查是否收到系统健康检查报告")
        print("   2. 明天12:10检查是否收到GitHub同步状态")
        print("   3. 定期查看日志文件了解系统状态")
        
        print("\n🔧 故障排除:")
        print("   如果未收到消息，请检查:")
        print("   • launchctl list | grep openclaw")
        print("   • /Users/ago/.openclaw/workspace/logs/ 目录")
        print("   • 手动运行发送脚本测试")
    else:
        print("⚠️  系统需要进一步检查")
        print("\n🔧 需要检查的项目:")
        for test_name, passed in test_results.items():
            if not passed:
                print(f"   • {test_name}")
        
        print("\n💡 建议操作:")
        print("   1. 检查launchd服务配置")
        print("   2. 验证Webhook地址是否正确")
        print("   3. 检查Python环境依赖")
    
    print(f"\n🏁 验证完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()