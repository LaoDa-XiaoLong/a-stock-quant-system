#!/usr/bin/env python3
# 每周代码质量检查
import subprocess
import json
from datetime import datetime
import os

def run_check(command, check_name):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return {
            "name": check_name,
            "success": result.returncode == 0,
            "output": result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout,
            "error": result.stderr
        }
    except Exception as e:
        return {"name": check_name, "success": False, "error": str(e)}

def main():
    print(f"🔧 每周代码质量检查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    checks = [
        ("python -m pylint scripts/ --fail-under=7.0", "Pylint代码规范"),
        ("python -m black --check scripts/", "Black代码格式"),
        ("python -m mypy scripts/ --ignore-missing-imports", "Mypy类型检查"),
        ("python -m pytest tests/ -v", "Pytest单元测试"),
    ]

    results = []
    all_passed = True

    for cmd, name in checks:
        print(f"正在检查: {name}...")
        result = run_check(cmd, name)
        results.append(result)

        if result["success"]:
            print(f"  ✅ {name}: 通过")
        else:
            print(f"  ❌ {name}: 失败")
            all_passed = False

    # 保存报告
    report = {
        "date": datetime.now().strftime('%Y-%m-%d'),
        "overall_status": "通过" if all_passed else "失败",
        "checks": results,
        "generated_at": datetime.now().isoformat()
    }

    report_dir = "reports/code_quality"
    os.makedirs(report_dir, exist_ok=True)
    report_file = f"{report_dir}/weekly_code_quality_{datetime.now().strftime('%Y%m%d')}.json"

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n📋 报告保存: {report_file}")
    print(f"总体状态: {'✅ 全部通过' if all_passed else '❌ 有检查失败'}")

if __name__ == "__main__":
    main()
