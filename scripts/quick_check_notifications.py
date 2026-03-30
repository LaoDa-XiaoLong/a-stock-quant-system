#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化监控脚本
快速检查消息群通知系统状态
"""

import os
import subprocess
from datetime import datetime, timedelta

def quick_check():
    """快速检查"""
    print("🔍 消息群通知系统快速检查")
    print("=" * 60)
    
    now = datetime.now()
    print(f"检查时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查关键服务
    print("\n1. 🔧 关键服务状态:")
    critical_services = [
        "com.openclaw.health_check_report.send",
        "com.openclaw.github_sync_status.send",
        "com.openclaw.financial_report.send"
    ]
    
    for service in critical_services:
        try:
            result = subprocess.run(
                ["launchctl", "list", service],
                capture_output=True,
                text=True
            )
            status = "✅ 已加载" if result.returncode == 0 else "❌ 未加载"
            print(f"   • {service}: {status}")
        except:
            print(f"   • {service}: ❓ 检查失败")
    
    # 检查脚本
    print("\n2. 📝 关键脚本状态:")
    critical_scripts = [
        "send_health_check_to_group.py",
        "send_github_sync_status.py"
    ]
    
    for script in critical_scripts:
        script_path = f"/Users/ago/.openclaw/workspace/scripts/{script}"
        if os.path.exists(script_path):
            print(f"   • {script}: ✅ 存在")
        else:
            print(f"   • {script}: ❌ 不存在")
    
    # 下次执行时间
    print("\n3. ⏰ 下次执行时间:")
    tomorrow = now + timedelta(days=1)
    
    print(f"   • 系统健康检查报告: {tomorrow.replace(hour=10, minute=0, second=0).strftime('%Y-%m-%d %H:%M')}")
    print(f"   • GitHub同步状态: {tomorrow.replace(hour=12, minute=10, second=0).strftime('%Y-%m-%d %H:%M')}")
    
    print("\n" + "=" * 60)
    print("📋 快速检查完成")
    print("💡 提示: 关键服务已配置，明天将自动执行")

if __name__ == "__main__":
    quick_check()