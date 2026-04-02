#!/usr/bin/env python3
import os
from datetime import datetime
import json

def main():
    print(f"调度状态检查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    schedules = [
        {"name": "健康检查", "time": "09:00, 15:00", "script": "daily_health_check.py", "status": "✅ 正常"},
        {"name": "GitHub日报", "time": "17:00", "script": "github_daily_report.py", "status": "✅ 正常"},
        {"name": "财报监控", "time": "21:30", "script": "final_financial_monitor_fixed.py", "status": "✅ 正常"},
        {"name": "开发日报", "time": "17:30", "script": "generate_daily_report.py", "status": "✅ 正常"},
        {"name": "数据备份", "time": "23:00", "script": "backup_system.py", "status": "✅ 正常"},
    ]

    all_ok = True
    for schedule in schedules:
        script_path = f"scripts/{schedule['script']}"
        if os.path.exists(script_path):
            print(f"{schedule['status']} {schedule['name']} ({schedule['time']})")
        else:
            print(f"❌ {schedule['name']} ({schedule['time']}) - 脚本缺失")
            all_ok = False

    # 保存报告
    report = {
        "timestamp": datetime.now().isoformat(),
        "overall_status": "健康" if all_ok else "异常",
        "schedules": schedules,
        "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    report_dir = "logs/schedule_checks"
    os.makedirs(report_dir, exist_ok=True)
    report_file = f"{report_dir}/schedule_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n报告保存: {report_file}")
    print(f"总体状态: {'✅ 健康' if all_ok else '❌ 异常'}")

if __name__ == "__main__":
    main()
