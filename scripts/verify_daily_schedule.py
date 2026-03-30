#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证每日定时任务配置
"""

import os
import subprocess
from datetime import datetime

def check_launchd_jobs():
    """检查launchd定时任务"""
    print("🔍 检查每日定时任务配置")
    print("=" * 60)
    
    jobs = [
        ("com.openclaw.healthcheck.send", "系统健康检查报告发送", "10:00"),
        ("com.openclaw.githubsync.send", "GitHub同步状态发送", "12:10")
    ]
    
    all_ok = True
    
    for job_id, description, schedule_time in jobs:
        print(f"\n📋 {description} ({schedule_time})")
        print(f"   Job ID: {job_id}")
        
        # 检查是否已加载
        try:
            result = subprocess.run(
                ["launchctl", "list", job_id],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"   ✅ 任务已加载")
                
                # 检查plist文件
                plist_path = f"/Users/ago/Library/LaunchAgents/{job_id}.plist"
                if os.path.exists(plist_path):
                    print(f"   ✅ 配置文件存在: {plist_path}")
                    
                    # 检查文件内容
                    with open(plist_path, 'r') as f:
                        content = f.read()
                        if "StartCalendarInterval" in content:
                            print(f"   ✅ 使用日历定时器 (每天固定时间)")
                        else:
                            print(f"   ❌ 未找到日历定时器配置")
                            all_ok = False
                else:
                    print(f"   ❌ 配置文件不存在")
                    all_ok = False
            else:
                print(f"   ❌ 任务未加载或不存在")
                all_ok = False
                
        except Exception as e:
            print(f"   ❌ 检查失败: {e}")
            all_ok = False
    
    return all_ok

def check_next_execution():
    """计算下次执行时间"""
    print("\n⏰ 下次执行时间计算")
    print("=" * 60)
    
    now = datetime.now()
    print(f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 健康检查报告 (10:00)
    health_check_time = now.replace(hour=10, minute=0, second=0, microsecond=0)
    if now > health_check_time:
        health_check_time = health_check_time.replace(day=now.day + 1)
    
    time_diff = health_check_time - now
    hours = time_diff.seconds // 3600
    minutes = (time_diff.seconds % 3600) // 60
    
    print(f"\n📊 系统健康检查报告:")
    print(f"   计划时间: 每天10:00")
    print(f"   下次执行: {health_check_time.strftime('%Y-%m-%d %H:%M')}")
    print(f"   距离现在: {hours}小时{minutes}分钟")
    
    # GitHub同步状态 (12:10)
    github_sync_time = now.replace(hour=12, minute=10, second=0, microsecond=0)
    if now > github_sync_time:
        github_sync_time = github_sync_time.replace(day=now.day + 1)
    
    time_diff = github_sync_time - now
    hours = time_diff.seconds // 3600
    minutes = (time_diff.seconds % 3600) // 60
    
    print(f"\n🔄 GitHub同步状态:")
    print(f"   计划时间: 每天12:10")
    print(f"   下次执行: {github_sync_time.strftime('%Y-%m-%d %H:%M')}")
    print(f"   距离现在: {hours}小时{minutes}分钟")
    
    return health_check_time, github_sync_time

def check_log_files():
    """检查日志文件"""
    print("\n📝 日志文件检查")
    print("=" * 60)
    
    log_files = [
        ("/Users/ago/.openclaw/workspace/logs/health_check_send_launchd.log", "健康检查发送日志"),
        ("/Users/ago/.openclaw/workspace/logs/health_check_send_launchd.error.log", "健康检查错误日志"),
        ("/Users/ago/.openclaw/workspace/logs/github_sync_send_launchd.log", "GitHub同步发送日志"),
        ("/Users/ago/.openclaw/workspace/logs/github_sync_send_launchd.error.log", "GitHub同步错误日志")
    ]
    
    for log_path, description in log_files:
        if os.path.exists(log_path):
            size = os.path.getsize(log_path)
            print(f"   ✅ {description}: {log_path} ({size}字节)")
        else:
            print(f"   📄 {description}: 文件不存在 (首次运行后创建)")

def main():
    print("🔔 每日定时任务配置验证")
    print("=" * 60)
    
    # 检查launchd任务
    jobs_ok = check_launchd_jobs()
    
    # 计算下次执行时间
    check_next_execution()
    
    # 检查日志文件
    check_log_files()
    
    print("\n" + "=" * 60)
    print("📋 验证结果总结")
    
    if jobs_ok:
        print("✅ 所有定时任务配置正确")
        print("   系统将在以下时间自动发送:")
        print("   - 系统健康检查报告: 每天10:00")
        print("   - GitHub同步状态: 每天12:10")
        print("\n💡 提示: 定时任务使用macOS launchd系统，可靠性高")
    else:
        print("⚠️  部分配置需要检查")
        print("   请查看上述详细检查结果")
    
    print(f"\n🕐 验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()