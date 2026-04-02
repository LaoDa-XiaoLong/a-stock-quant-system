#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置工作群通知定时任务
"""

import os
import json
import subprocess
from datetime import datetime
import sys

def setup_cron_jobs():
    """设置定时任务"""
    print("🔧 设置工作群通知定时任务")
    print("=" * 60)

    workspace = "/Users/ago/.openclaw/workspace"

    # 1. 系统健康检查报告发送任务 (10:00)
    health_check_cron = {
        "name": "系统健康检查报告发送",
        "schedule": "0 10 * * *",
        "command": f"cd {workspace} && python3 scripts/send_health_check_to_group.py",
        "description": "每天10:00发送系统健康检查报告到工作群",
        "enabled": True
    }

    # 2. GitHub同步状态发送任务 (12:10)
    github_sync_cron = {
        "name": "GitHub同步状态发送",
        "schedule": "10 12 * * *",
        "command": f"cd {workspace} && python3 scripts/send_github_sync_status.py",
        "description": "每天12:10发送GitHub同步状态到工作群",
        "enabled": True
    }

    # 保存配置
    config_dir = os.path.join(workspace, "config", "cron_jobs")
    os.makedirs(config_dir, exist_ok=True)

    health_check_file = os.path.join(config_dir, "health_check_send.json")
    github_sync_file = os.path.join(config_dir, "github_sync_send.json")

    with open(health_check_file, 'w', encoding='utf-8') as f:
        json.dump(health_check_cron, f, ensure_ascii=False, indent=2)

    with open(github_sync_file, 'w', encoding='utf-8') as f:
        json.dump(github_sync_cron, f, ensure_ascii=False, indent=2)

    print(f"✅ 定时任务配置已保存:")
    print(f"   1. 系统健康检查报告发送: {health_check_file}")
    print(f"      - 时间: 每天10:00")
    print(f"      - 命令: {health_check_cron['command'][:50]}...")

    print(f"   2. GitHub同步状态发送: {github_sync_file}")
    print(f"      - 时间: 每天12:10")
    print(f"      - 命令: {github_sync_cron['command'][:50]}...")

    # 3. 创建启动脚本
    startup_script = os.path.join(workspace, "scripts", "start_work_group_notifications.sh")
    startup_content = f"""#!/bin/bash
# 工作群通知启动脚本
# 自动启动定时任务

echo "🚀 启动工作群通知服务"
echo "=========================="

# 设置环境变量
export WORKSPACE="{workspace}"
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

# 检查Python环境
python3 --version

# 启动健康检查报告发送（立即测试）
echo "📊 测试系统健康检查报告发送..."
cd "$WORKSPACE" && python3 scripts/send_health_check_to_group.py

# 启动GitHub同步状态发送（立即测试）
echo "🔄 测试GitHub同步状态发送..."
cd "$WORKSPACE" && python3 scripts/send_github_sync_status.py

echo "✅ 工作群通知服务启动完成"
echo "定时任务配置:"
echo "  1. 系统健康检查报告发送: 每天10:00"
echo "  2. GitHub同步状态发送: 每天12:10"
"""

    with open(startup_script, 'w', encoding='utf-8') as f:
        f.write(startup_content)

    os.chmod(startup_script, 0o755)
    print(f"✅ 启动脚本已创建: {startup_script}")

    # 4. 创建系统LaunchAgent（macOS）
    if sys.platform == "darwin":
        launch_agent_dir = os.path.expanduser("~/Library/LaunchAgents")
        os.makedirs(launch_agent_dir, exist_ok=True)

        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openclaw.workgroup.notifications</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>{startup_script}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StartInterval</key>
    <integer>3600</integer>
    <key>StandardOutPath</key>
    <string>{workspace}/logs/workgroup_notifications.log</string>
    <key>StandardErrorPath</key>
    <string>{workspace}/logs/workgroup_notifications.error.log</string>
</dict>
</plist>
"""

        plist_file = os.path.join(launch_agent_dir, "com.openclaw.workgroup.notifications.plist")
        with open(plist_file, 'w', encoding='utf-8') as f:
            f.write(plist_content)

        print(f"✅ macOS LaunchAgent已创建: {plist_file}")
        print("   要启动服务，请运行: launchctl load " + plist_file)

    return True

def test_notifications():
    """测试通知功能"""
    print("\n🧪 测试通知功能")
    print("=" * 60)

    workspace = "/Users/ago/.openclaw/workspace"

    # 测试健康检查报告发送
    print("1. 测试系统健康检查报告发送...")
    result1 = subprocess.run(
        ["python3", "scripts/send_health_check_to_group.py"],
        cwd=workspace,
        capture_output=True,
        text=True
    )

    if result1.returncode == 0:
        print("   ✅ 健康检查报告发送测试成功")
    else:
        print(f"   ❌ 健康检查报告发送测试失败: {result1.stderr}")

    # 测试GitHub同步状态发送
    print("2. 测试GitHub同步状态发送...")
    result2 = subprocess.run(
        ["python3", "scripts/send_github_sync_status.py"],
        cwd=workspace,
        capture_output=True,
        text=True
    )

    if result2.returncode == 0:
        print("   ✅ GitHub同步状态发送测试成功")
    else:
        print(f"   ❌ GitHub同步状态发送测试失败: {result2.stderr}")

    return result1.returncode == 0 and result2.returncode == 0

def main():
    print("🔔 工作群通知系统设置")
    print("=" * 60)

    print("📋 配置内容:")
    print("   1. 系统健康检查报告发送 (10:00)")
    print("   2. GitHub同步状态发送 (12:10)")
    print("   3. 自动启动脚本")
    print("   4. macOS LaunchAgent服务")

    # 设置定时任务
    setup_cron_jobs()

    # 测试通知功能
    test_success = test_notifications()

    print("\n" + "=" * 60)
    if test_success:
        print("🎉 工作群通知系统设置完成!")
        print("   下次检查时间:")
        print("   - 系统健康检查报告: 明天10:00")
        print("   - GitHub同步状态: 明天12:10")
    else:
        print("⚠️  工作群通知系统设置完成，但测试中有警告")
        print("   请检查日志文件了解详情")

    print("\n📁 配置文件位置:")
    print(f"   - 定时任务配置: {os.path.join('/Users/ago/.openclaw/workspace', 'config', 'cron_jobs')}")
    print(f"   - 发送脚本: {os.path.join('/Users/ago/.openclaw/workspace', 'scripts')}")
    print(f"   - 日志文件: {os.path.join('/Users/ago/.openclaw/workspace', 'logs')}")

if __name__ == "__main__":
    main()
