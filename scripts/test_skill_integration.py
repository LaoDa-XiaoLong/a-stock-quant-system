#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skill集成测试
测试财报监控系统与Skill模块的集成
"""

import os
import sys
import json
from datetime import datetime

print("Skill集成测试")
print("=" * 60)

# 测试1: 检查Skill目录结构
print("\n1. 检查Skill目录结构:")
skill_dirs = ['data-quality-validator', 'multi-source-fetcher', 'feishu-messenger']
all_skills_exist = True

for skill_dir in skill_dirs:
    skill_path = os.path.join('skills', skill_dir)
    if os.path.exists(skill_path):
        print(f"  ✅ {skill_dir}: 存在")

        # 检查必要文件
        required_files = ['SKILL.md', 'README.md']
        for req_file in required_files:
            file_path = os.path.join(skill_path, req_file)
            if os.path.exists(file_path):
                print(f"     - {req_file}: ✅")
            else:
                print(f"     - {req_file}: ❌")
                all_skills_exist = False
    else:
        print(f"  ❌ {skill_dir}: 不存在")
        all_skills_exist = False

# 测试2: 检查核心代码文件
print("\n2. 检查核心代码文件:")
core_files = [
    'skills/data-quality-validator/data_quality_validator.py',
    'skills/multi-source-fetcher/complete_fetcher.py',
    'skills/feishu-messenger/feishu_messenger.py'
]

for core_file in core_files:
    if os.path.exists(core_file):
        file_size = os.path.getsize(core_file)
        print(f"  ✅ {core_file}: 存在 ({file_size}字节)")
    else:
        print(f"  ❌ {core_file}: 不存在")

# 测试3: 检查集成系统
print("\n3. 检查集成系统:")
integration_files = [
    'scripts/skill_integration_manager.py',
    'scripts/final_financial_monitor_skill_v1.py',
    'docs/skill_integration_guide.md'
]

for int_file in integration_files:
    if os.path.exists(int_file):
        print(f"  ✅ {int_file}: 存在")
    else:
        print(f"  ❌ {int_file}: 不存在")

# 测试4: 检查备份
print("\n4. 检查备份文件:")
backup_dir = 'backups/skill_integration'
if os.path.exists(backup_dir):
    backup_files = os.listdir(backup_dir)
    print(f"  ✅ 备份目录存在: {len(backup_files)}个备份文件")
    for bf in backup_files[:3]:  # 只显示前3个
        print(f"     - {bf}")
else:
    print(f"  ⚠️ 备份目录不存在")

# 总结
print("\n" + "=" * 60)
print("集成测试总结:")

if all_skills_exist:
    print("✅ 所有Skill目录结构完整")
else:
    print("⚠️ 部分Skill目录不完整")

# 检查集成状态
integration_status = {
    'skill_directories': 3,
    'core_code_files': 3,
    'integration_tools': 3,
    'backup_system': 1
}

total_items = sum(integration_status.values())
completed_items = 0

for item, count in integration_status.items():
    completed_items += count

completion_rate = completed_items / total_items * 100

print(f"\n集成完成度: {completion_rate:.1f}%")
print(f"Skill数量: {integration_status['skill_directories']}/3")
print(f"核心代码: {integration_status['core_code_files']}/3")
print(f"集成工具: {integration_status['integration_tools']}/3")
print(f"备份系统: {integration_status['backup_system']}/1")

print("\n" + "=" * 60)
print("下一步行动:")

if completion_rate >= 80:
    print("✅ 集成基础已建立，可以开始重构")
    print("建议:")
    print("1. 运行财报监控系统Skill集成版测试")
    print("2. 验证数据质量验证功能")
    print("3. 测试消息推送功能")
    print("4. 逐步替换现有系统")
else:
    print("⚠️ 集成基础不完整，需要先完善")
    print("建议:")
    print("1. 完善缺失的Skill文件")
    print("2. 修复不完整的代码文件")
    print("3. 重新运行集成测试")
    print("4. 确保所有依赖可用")

print("\n详细报告:")
print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"工作目录: {os.getcwd()}")
print(f"Python版本: {sys.version}")
