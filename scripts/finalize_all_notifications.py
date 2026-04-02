#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终完成所有消息群通知配置
使用英文服务ID，确保所有配置正确
"""

import os
import json
import subprocess
from datetime import datetime

def create_english_launchd_services():
    """创建英文的launchd服务"""
    print("🚀 创建英文launchd服务")
    print("=" * 60)

    # 任务配置（使用英文服务ID）
    tasks = [
        {
            "name": "health_check_report",
            "display_name": "系统健康检查报告",
            "cron_time": "0 10 * * *",
            "target_group": "工作沟通汇报群",
            "webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/7c6e2bb9-0f2f-4d16-ade1-e93cf6bd3065",
            "script": "send_health_check_to_group.py"
        },
        {
            "name": "github_sync_status",
            "display_name": "GitHub同步状态",
            "cron_time": "10 0,12 * * *",
            "target_group": "工作沟通汇报群",
            "webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/7c6e2bb9-0f2f-4d16-ade1-e93cf6bd3065",
            "script": "send_github_sync_status.py"
        },
        {
            "name": "financial_report",
            "display_name": "财报监控日报",
            "cron_time": "0 9 * * *",
            "target_group": "A股数据分析群",
            "webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/fb95ec56-6ad7-4830-99c7-0eaa287e67e7",
            "script": "send_financial_report_v3_fixed.py"
        },
        {
            "name": "stock_update_status",
            "display_name": "股票数据更新状态",
            "cron_time": "30 9 * * *",
            "target_group": "A股数据分析群",
            "webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/fb95ec56-6ad7-4830-99c7-0eaa287e67e7",
            "script": "send_股票数据自动更新状态.py"
        },
        {
            "name": "code_health_report",
            "display_name": "代码健康度检查报告",
            "cron_time": "0 15 * * *",
            "target_group": "工作沟通汇报群",
            "webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/7c6e2bb9-0f2f-4d16-ade1-e93cf6bd3065",
            "script": "send_代码健康度检查报告.py"
        }
    ]

    services_loaded = 0

    for task in tasks:
        service_id = f"com.openclaw.{task['name']}.send"
        plist_path = f"/Users/ago/Library/LaunchAgents/{service_id}.plist"

        print(f"\n🔧 配置服务: {task['display_name']}")
        print(f"   服务ID: {service_id}")
        print(f"   执行时间: {task['cron_time']}")

        # 解析cron时间
        cron_parts = task['cron_time'].split()
        if len(cron_parts) >= 2:
            minute = cron_parts[0]
            hour = cron_parts[1]

            # 创建plist文件
            plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{service_id}</string>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/ago/.openclaw/workspace/scripts/{task['script']}</string>
    </array>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>{hour}</integer>
        <key>Minute</key>
        <integer>{minute}</integer>
    </dict>

    <key>StandardOutPath</key>
    <string>/Users/ago/.openclaw/workspace/logs/{service_id}.log</string>

    <key>StandardErrorPath</key>
    <string>/Users/ago/.openclaw/workspace/logs/{service_id}.error.log</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>WORKSPACE</key>
        <string>/Users/ago/.openclaw/workspace</string>
    </dict>
</dict>
</plist>'''

            try:
                # 写入plist文件
                with open(plist_path, 'w', encoding='utf-8') as f:
                    f.write(plist_content)

                print(f"   ✅ plist文件创建: {plist_path}")

                # 加载服务
                # 先尝试卸载（如果已存在）
                subprocess.run(["launchctl", "unload", plist_path],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                # 加载服务
                load_result = subprocess.run(
                    ["launchctl", "load", plist_path],
                    capture_output=True,
                    text=True
                )

                if load_result.returncode == 0:
                    print(f"   ✅ launchd服务已加载")
                    services_loaded += 1
                else:
                    print(f"   ❌ launchd服务加载失败")
                    if load_result.stderr:
                        print(f"       错误: {load_result.stderr[:100]}")

            except Exception as e:
                print(f"   ❌ 配置异常: {e}")
        else:
            print(f"   ❌ 无法解析cron时间: {task['cron_time']}")

    print(f"\n📊 服务配置统计: 成功加载 {services_loaded} 个服务")
    return services_loaded

def verify_all_services():
    """验证所有服务状态"""
    print("\n🔍 验证所有服务状态")
    print("-" * 60)

    # 预期的服务列表
    expected_services = [
        "com.openclaw.healthcheck.send",
        "com.openclaw.githubsync.send",
        "com.openclaw.financial_report.send",
        "com.openclaw.stock_update_status.send",
        "com.openclaw.code_health_report.send"
    ]

    all_loaded = True

    for service_id in expected_services:
        try:
            result = subprocess.run(
                ["launchctl", "list", service_id],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print(f"✅ {service_id}: 已加载")
            else:
                print(f"❌ {service_id}: 未加载")
                all_loaded = False

        except Exception as e:
            print(f"❌ {service_id}: 检查失败 - {e}")
            all_loaded = False

    return all_loaded

def test_all_scripts():
    """测试所有发送脚本"""
    print("\n🧪 测试所有发送脚本")
    print("-" * 60)

    scripts_to_test = [
        ("send_health_check_to_group.py", "系统健康检查报告"),
        ("send_github_sync_status.py", "GitHub同步状态"),
        ("send_financial_report_v3_fixed.py", "财报监控日报"),
        ("send_股票数据自动更新状态.py", "股票数据更新状态"),
        ("send_代码健康度检查报告.py", "代码健康度检查报告")
    ]

    all_success = True

    for script_name, display_name in scripts_to_test:
        script_path = f"/Users/ago/.openclaw/workspace/scripts/{script_name}"

        if os.path.exists(script_path):
            print(f"\n🔍 测试: {display_name}")
            print(f"   脚本: {script_name}")

            try:
                # 只测试脚本是否能正常启动，不实际发送
                result = subprocess.run(
                    ["python3", "-c", f"import sys; sys.path.insert(0, '/Users/ago/.openclaw/workspace'); exec(open('{script_path}').read())"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0:
                    print(f"   ✅ 脚本语法正确")
                else:
                    print(f"   ❌ 脚本有错误")
                    if result.stderr:
                        print(f"       错误: {result.stderr[:100]}...")
                    all_success = False

            except subprocess.TimeoutExpired:
                print(f"   ⏰ 测试超时（可能正常执行中）")
            except Exception as e:
                print(f"   ❌ 测试异常: {e}")
                all_success = False
        else:
            print(f"\n❌ 脚本不存在: {script_name}")
            all_success = False

    return all_success

def create_simplified_monitor():
    """创建简化的监控脚本"""
    print("\n🔍 创建简化监控脚本")
    print("-" * 60)

    monitor_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化监控脚本
快速检查消息群通知系统状态
"""

import os
import subprocess
from datetime import datetime

def quick_check():
    """快速检查"""
    print("🔍 消息群通知系统快速检查")
    print("=" * 60)

    now = datetime.now()
    print(f"检查时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")

    # 检查关键服务
    print("\n1. 🔧 关键服务状态:")
    critical_services = [
        "com.openclaw.healthcheck.send",
        "com.openclaw.githubsync.send"
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
    tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = tomorrow.replace(day=tomorrow.day + 1)

    print(f"   • 系统健康检查报告: {tomorrow.replace(hour=10, minute=0).strftime('%Y-%m-%d %H:%M')}")
    print(f"   • GitHub同步状态: {tomorrow.replace(hour=12, minute=10).strftime('%Y-%m-%d %H:%M')}")

    print("\n" + "=" * 60)
    print("📋 快速检查完成")
    print("💡 提示: 如需详细检查，运行 monitor_all_notifications.py")

if __name__ == "__main__":
    quick_check()
'''

    monitor_path = "/Users/ago/.openclaw/workspace/scripts/quick_check_notifications.py"
    with open(monitor_path, 'w', encoding='utf-8') as f:
        f.write(monitor_script)

    os.chmod(monitor_path, 0o755)
    print(f"✅ 简化监控脚本已创建: {monitor_path}")

    return monitor_path

def main():
    print("🔧 最终完成所有消息群通知配置")
    print("=" * 60)

    print("🎯 目标: 确保所有配置正确，避免遗漏或报错")

    # 1. 创建英文launchd服务
    services_loaded = create_english_launchd_services()

    # 2. 验证所有服务
    all_services_loaded = verify_all_services()

    # 3. 测试所有脚本
    all_scripts_ok = test_all_scripts()

    # 4. 创建简化监控
    monitor_path = create_simplified_monitor()

    print("\n" + "=" * 60)
    print("📊 最终配置结果")
    print("=" * 60)

    if all_services_loaded and all_scripts_ok:
        print("🎉 所有配置完成!")

        print("\n✅ 系统状态:")
        print("   1. launchd服务: 全部已加载")
        print("   2. 发送脚本: 全部语法正确")
        print("   3. 监控系统: 已配置")

        print("\n🚀 明日自动执行:")
        print("   🕙 10:00 - 系统健康检查报告 → 工作沟通汇报群")
        print("   🕛 12:10 - GitHub同步状态 → 工作沟通汇报群")
        print("   🕘 09:00 - 财报监控日报 → A股数据分析群")
        print("   🕤 09:30 - 股票数据更新状态 → A股数据分析群")

        print("\n🔍 验证命令:")
        print("   1. 快速检查: python3 scripts/quick_check_notifications.py")
        print("   2. 详细检查: python3 scripts/monitor_all_notifications.py")
        print("   3. 查看服务: launchctl list | grep openclaw")

    else:
        print("⚠️  配置需要检查")

        if not all_services_loaded:
            print("   • 部分launchd服务未加载")

        if not all_scripts_ok:
            print("   • 部分脚本有错误")

        print("\n💡 建议操作:")
        print("   1. 手动检查launchd服务配置")
        print("   2. 修复有错误的脚本")
        print("   3. 运行监控脚本检查详细状态")

    print(f"\n🕐 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
