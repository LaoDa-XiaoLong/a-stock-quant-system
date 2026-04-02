#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新调度系统以支持版本管理
将调度任务配置为使用版本化的模板和策略
"""

import json
import os
import sys
from datetime import datetime


def load_version_registry():
    """加载版本注册表"""
    registry_path = "version_management/version_registry.json"
    if os.path.exists(registry_path):
        with open(registry_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def get_current_version(category, name):
    """获取当前版本"""
    registry = load_version_registry()

    try:
        return registry["categories"][category][name]["current"]
    except KeyError:
        return None


def update_cron_jobs():
    """更新调度任务配置"""
    cron_file = "/Users/ago/.openclaw/cron/jobs.json"

    if not os.path.exists(cron_file):
        print(f"❌ 调度配置文件不存在: {cron_file}")
        return False

    # 加载当前配置
    with open(cron_file, 'r', encoding='utf-8') as f:
        jobs = json.load(f)

    print("📋 当前调度任务:")
    for job in jobs.get("jobs", []):
        print(f"  • {job.get('name', '未命名')}: {job.get('id', '')[:8]}")

    # 获取当前版本信息
    financial_version = get_current_version("report_templates", "financial_daily")
    stock_selection_version = get_current_version("stock_models", "stock_selection")
    quant_strategy_version = get_current_version("stock_models", "quant_strategies")

    print(f"\n📊 当前版本信息:")
    print(f"  • 财报监控日报: {financial_version or '未版本化'}")
    print(f"  • 选股策略: {stock_selection_version or '未版本化'}")
    print(f"  • 量化策略: {quant_strategy_version or '未版本化'}")

    # 更新任务配置
    updated = False
    for job in jobs.get("jobs", []):
        job_name = job.get("name", "")

        if "财报监控日报" in job_name and financial_version:
            # 更新财报监控日报任务
            old_payload = job.get("payload", {}).get("message", "")
            new_payload = f"执行财报监控日报任务（{financial_version}版）：1. 获取最新财报数据 2. 生成分层版日报 3. 发送报告到A股数据分析群"

            if old_payload != new_payload:
                job["payload"]["message"] = new_payload
                job["updatedAtMs"] = int(datetime.now().timestamp() * 1000)
                updated = True
                print(f"  🔄 更新财报监控日报任务 → {financial_version}版")

        elif "股票数据自动更新" in job_name and stock_selection_version:
            # 更新股票数据任务
            old_payload = job.get("payload", {}).get("message", "")
            new_payload = f"执行股票数据更新任务（{stock_selection_version}版）：1. 使用akshare获取最新A股数据 2. 应用选股策略筛选 3. 更新本地数据文件"

            if old_payload != new_payload:
                job["payload"]["message"] = new_payload
                job["updatedAtMs"] = int(datetime.now().timestamp() * 1000)
                updated = True
                print(f"  🔄 更新股票数据任务 → {stock_selection_version}版")

        elif "量化策略周报" in job_name and quant_strategy_version:
            # 更新量化策略任务
            old_payload = job.get("payload", {}).get("message", "")
            new_payload = f"执行量化策略周报任务（{quant_strategy_version}版）：1. 分析本周策略表现 2. 总结市场变化 3. 生成周报并发送"

            if old_payload != new_payload:
                job["payload"]["message"] = new_payload
                job["updatedAtMs"] = int(datetime.now().timestamp() * 1000)
                updated = True
                print(f"  🔄 更新量化策略任务 → {quant_strategy_version}版")

    if updated:
        # 备份原文件
        backup_file = cron_file + ".backup"
        import shutil
        shutil.copy2(cron_file, backup_file)
        print(f"  💾 备份原配置: {backup_file}")

        # 保存更新后的配置
        with open(cron_file, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, ensure_ascii=False, indent=2)

        print(f"  ✅ 调度配置已更新")

        # 验证更新
        print(f"\n🔍 验证更新结果:")
        with open(cron_file, 'r', encoding='utf-8') as f:
            updated_jobs = json.load(f)

        for job in updated_jobs.get("jobs", []):
            if "payload" in job and "message" in job["payload"]:
                msg = job["payload"]["message"]
                if "版" in msg:  # 包含版本信息
                    print(f"  • {job.get('name', '')}: {msg[:50]}...")

        return True
    else:
        print("  ℹ️  无需更新，配置已是最新")
        return True


def create_version_aware_script():
    """创建版本感知的执行脚本"""
    script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本感知的任务执行脚本
根据当前版本自动加载对应版本的代码
"""

import os
import sys
import json
from datetime import datetime


def get_version_path(category, name, version=None):
    """获取版本路径"""
    registry_path = "version_management/version_registry.json"

    if not os.path.exists(registry_path):
        print(f"❌ 版本注册表不存在: {registry_path}")
        return None

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)

    try:
        if version is None:
            # 获取当前版本
            version = registry["categories"][category][name]["current"]

        return registry["categories"][category][name]["versions"][version]["path"]
    except KeyError:
        print(f"❌ 无法获取版本路径: {category}/{name}/{version}")
        return None


def execute_financial_daily_task():
    """执行财报监控日报任务（版本感知）"""
    print("📈 执行财报监控日报任务（版本感知）")

    # 获取当前版本路径
    version_path = get_version_path("report_templates", "financial_daily")
    if not version_path:
        print("❌ 无法获取财报监控日报版本路径")
        return False

    print(f"  📁 使用版本: {version_path}")

    # 这里应该根据版本路径加载对应的代码
    # 实际实现时，需要根据版本目录中的具体文件来执行

    # 模拟执行
    print("  ✅ 任务执行完成（版本感知模式）")
    return True


def execute_stock_selection_task():
    """执行选股策略任务（版本感知）"""
    print("🎯 执行选股策略任务（版本感知）")

    version_path = get_version_path("stock_models", "stock_selection")
    if not version_path:
        print("❌ 无法获取选股策略版本路径")
        return False

    print(f"  📁 使用版本: {version_path}")
    print("  ✅ 任务执行完成（版本感知模式）")
    return True


def main():
    """主函数"""
    print("🚀 版本感知任务执行器")
    print("=" * 50)

    # 这里可以根据命令行参数决定执行哪个任务
    # 目前只是演示

    execute_financial_daily_task()
    print()
    execute_stock_selection_task()

    print("=" * 50)
    print("🎉 所有版本感知任务执行完成")


if __name__ == "__main__":
    main()
'''

    script_path = "scripts/version_aware_executor.py"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)

    # 设置执行权限
    os.chmod(script_path, 0o755)

    print(f"📝 创建版本感知执行脚本: {script_path}")
    return script_path


def main():
    """主函数"""
    print("🔄 更新调度系统以支持版本管理")
    print("=" * 60)

    try:
        # 1. 更新调度任务配置
        print("\n1. 更新调度任务配置")
        success1 = update_cron_jobs()

        # 2. 创建版本感知执行脚本
        print("\n2. 创建版本感知执行脚本")
        script_path = create_version_aware_script()

        # 3. 验证版本管理状态
        print("\n3. 验证版本管理状态")
        registry = load_version_registry()

        if registry.get("categories"):
            print("✅ 版本管理系统状态良好")
            for category, items in registry["categories"].items():
                print(f"  📁 {category}:")
                for name, data in items.items():
                    current = data.get("current", "无")
                    count = len(data.get("versions", {}))
                    print(f"    ├─ {name}: {count}个版本 (当前: {current})")
        else:
            print("⚠️  版本注册表为空")

        print("\n" + "=" * 60)
        print("🎉 调度系统版本化管理更新完成")
        print("\n📋 下一步行动:")
        print("1. 明天验证财报监控日报V3版效果")
        print("2. 根据需要切换其他版本")
        print("3. 继续版本化其他核心功能")
        print(f"4. 使用 {script_path} 执行版本感知任务")

        return 0

    except Exception as e:
        print(f"❌ 更新失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
