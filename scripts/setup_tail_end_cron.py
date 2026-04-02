#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置尾盘选股定时任务
"""

import os
import sys
import json
from datetime import datetime

def create_launchd_plist():
    """创建macOS launchd定时任务"""

    plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openclaw.tailend.selection</string>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>{os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts/auto_tail_end_selection.py')}</string>
        <string>run</string>
    </array>

    <key>StartCalendarInterval</key>
    <array>
        <dict>
            <key>Hour</key>
            <integer>14</integer>
            <key>Minute</key>
            <integer>30</integer>
        </dict>
        <dict>
            <key>Hour</key>
            <integer>14</integer>
            <key>Minute</key>
            <integer>45</integer>
        </dict>
        <dict>
            <key>Hour</key>
            <integer>15</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
    </array>

    <key>StandardOutPath</key>
    <string>{os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs/tail_end_selection_launchd.log')}</string>

    <key>StandardErrorPath</key>
    <string>{os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs/tail_end_selection_launchd.error.log')}</string>

    <key>WorkingDirectory</key>
    <string>{os.path.dirname(os.path.dirname(__file__))}</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>PYTHONPATH</key>
        <string>{os.path.dirname(os.path.dirname(__file__))}</string>
    </dict>

    <key>RunAtLoad</key>
    <false/>

    <key>KeepAlive</key>
    <false/>
</dict>
</plist>'''

    plist_path = os.path.expanduser("~/Library/LaunchAgents/com.openclaw.tailend.selection.plist")

    # 创建目录
    os.makedirs(os.path.dirname(plist_path), exist_ok=True)

    # 写入plist文件
    with open(plist_path, 'w', encoding='utf-8') as f:
        f.write(plist_content)

    print(f"✅ launchd plist文件已创建: {plist_path}")

    return plist_path

def create_cron_job():
    """创建cron定时任务"""

    workspace_dir = os.path.dirname(os.path.dirname(__file__))
    script_path = os.path.join(workspace_dir, "scripts/auto_tail_end_selection.py")

    cron_commands = [
        f"# 尾盘选股定时任务 - 创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"# 第一次选股: 14:30",
        f"30 14 * * * cd {workspace_dir} && /usr/local/bin/python3 {script_path} once >> {workspace_dir}/logs/tail_end_cron.log 2>&1",
        f"# 第二次选股: 14:45",
        f"45 14 * * * cd {workspace_dir} && /usr/local/bin/python3 {script_path} once >> {workspace_dir}/logs/tail_end_cron.log 2>&1",
        f"# 最终选股: 15:00",
        f"0 15 * * * cd {workspace_dir} && /usr/local/bin/python3 {script_path} once >> {workspace_dir}/logs/tail_end_cron.log 2>&1"
    ]

    cron_file = os.path.join(workspace_dir, "config/cron_tail_end_jobs.txt")

    with open(cron_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(cron_commands))

    print(f"✅ cron任务配置已保存: {cron_file}")
    print("\n手动添加到cron的方法:")
    print(f"1. 编辑crontab: crontab -e")
    print(f"2. 添加以下内容:")
    for cmd in cron_commands[1:]:  # 跳过注释行
        print(f"   {cmd}")

    return cron_file

def create_openclaw_cron():
    """创建OpenClaw cron任务"""

    workspace_dir = os.path.dirname(os.path.dirname(__file__))

    cron_config = {
        "name": "尾盘选股策略",
        "description": "每天尾盘时间（14:30, 14:45, 15:00）自动运行尾盘选股策略",
        "schedule": [
            {
                "time": "14:30",
                "command": f"cd {workspace_dir} && python3 scripts/auto_tail_end_selection.py once",
                "description": "第一次尾盘选股"
            },
            {
                "time": "14:45",
                "command": f"cd {workspace_dir} && python3 scripts/auto_tail_end_selection.py once",
                "description": "第二次尾盘选股"
            },
            {
                "time": "15:00",
                "command": f"cd {workspace_dir} && python3 scripts/auto_tail_end_selection.py once",
                "description": "最终尾盘选股"
            }
        ],
        "output": {
            "log_file": f"{workspace_dir}/logs/tail_end_openclaw_cron.log",
            "error_file": f"{workspace_dir}/logs/tail_end_openclaw_cron.error.log"
        },
        "notifications": {
            "enabled": True,
            "channel": "feishu",
            "target": "工作沟通汇报群",
            "format": "飞书卡片"
        }
    }

    config_file = os.path.join(workspace_dir, "config/openclaw_tail_end_cron.json")

    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(cron_config, f, ensure_ascii=False, indent=2)

    print(f"✅ OpenClaw cron配置已保存: {config_file}")

    return config_file

def setup_logging():
    """设置日志系统"""

    workspace_dir = os.path.dirname(os.path.dirname(__file__))
    log_dir = os.path.join(workspace_dir, "logs")

    # 创建日志目录
    os.makedirs(log_dir, exist_ok=True)

    # 创建日志配置文件
    log_config = {
        "tail_end_selection": {
            "log_file": os.path.join(log_dir, "tail_end_selection.log"),
            "level": "INFO",
            "max_size": "10MB",
            "backup_count": 5
        },
        "tail_end_cron": {
            "log_file": os.path.join(log_dir, "tail_end_cron.log"),
            "level": "INFO",
            "max_size": "10MB",
            "backup_count": 5
        },
        "tail_end_errors": {
            "log_file": os.path.join(log_dir, "tail_end_errors.log"),
            "level": "ERROR",
            "max_size": "5MB",
            "backup_count": 3
        }
    }

    config_file = os.path.join(workspace_dir, "config/tail_end_logging.json")

    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(log_config, f, ensure_ascii=False, indent=2)

    print(f"✅ 日志配置已保存: {config_file}")

    # 创建空日志文件
    for log_info in log_config.values():
        log_file = log_info["log_file"]
        if not os.path.exists(log_file):
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"# 尾盘选股策略日志文件 - 创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    return config_file

def create_quick_test_script():
    """创建快速测试脚本"""

    workspace_dir = os.path.dirname(os.path.dirname(__file__))

    test_script = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
尾盘选股策略快速测试脚本
"""

import sys
import os
sys.path.append("{workspace_dir}")

from scripts.auto_tail_end_selection import AutoTailEndSelection

def test_tail_end_selection():
    """测试尾盘选股"""
    print("🚀 快速测试尾盘选股策略...")
    print("=" * 60)

    auto_selector = AutoTailEndSelection()

    # 模拟尾盘时间运行
    import time
    from datetime import datetime

    original_get_time = auto_selector.selector.get_current_time

    def mock_tail_time():
        return datetime(2026, 4, 1, 14, 45, 0)

    auto_selector.selector.get_current_time = mock_tail_time

    try:
        print("运行单次尾盘选股...")
        auto_selector.run_once()

        print("\\n✅ 测试完成!")
        print("检查以下文件:")
        print(f"  1. 选股报告: {workspace_dir}/data/tail_end_selection/")
        print(f"  2. 投资组合: {workspace_dir}/data/investment_tracking/tail_end_portfolio.json")
        print(f"  3. 运行日志: {workspace_dir}/logs/tail_end_selection.log")

    finally:
        auto_selector.selector.get_current_time = original_get_time

if __name__ == "__main__":
    test_tail_end_selection()'''

    script_path = os.path.join(workspace_dir, "scripts/quick_test_tail_end.py")

    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(test_script)

    # 设置执行权限
    os.chmod(script_path, 0o755)

    print(f"✅ 快速测试脚本已创建: {script_path}")
    print(f"   运行命令: python3 {script_path}")

    return script_path

def main():
    """主函数"""
    print("设置尾盘选股定时任务系统")
    print("=" * 60)

    try:
        # 1. 设置日志系统
        print("\n1. 设置日志系统...")
        setup_logging()

        # 2. 创建launchd定时任务
        print("\n2. 创建macOS launchd定时任务...")
        plist_path = create_launchd_plist()

        # 3. 创建cron任务配置
        print("\n3. 创建cron定时任务配置...")
        cron_file = create_cron_job()

        # 4. 创建OpenClaw cron配置
        print("\n4. 创建OpenClaw cron配置...")
        openclaw_cron = create_openclaw_cron()

        # 5. 创建快速测试脚本
        print("\n5. 创建快速测试脚本...")
        test_script = create_quick_test_script()

        print("\n" + "=" * 60)
        print("✅ 尾盘选股定时任务系统设置完成!")
        print("\n下一步操作:")
        print("1. 测试策略: python3 scripts/quick_test_tail_end.py")
        print("2. 加载launchd任务:")
        print(f"   launchctl load {plist_path}")
        print("3. 或手动添加cron任务:")
        print(f"   crontab {cron_file}")
        print("\n定时执行时间:")
        print("  - 14:30: 第一次尾盘选股")
        print("  - 14:45: 第二次尾盘选股")
        print("  - 15:00: 最终尾盘选股")
        print("\n输出文件:")
        print("  - 选股报告: data/tail_end_selection/")
        print("  - 投资组合: data/investment_tracking/tail_end_portfolio.json")
        print("  - 运行日志: logs/tail_end_selection.log")

    except Exception as e:
        print(f"\n❌ 设置失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
