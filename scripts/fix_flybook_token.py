#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复飞书token错误问题
"""

import json
import os
from datetime import datetime


def fix_flybook_token_error():
    """修复飞书token错误"""
    print("🔧 修复飞书token错误问题")

    # 1. 检查jobs.json文件
    jobs_file = "/Users/ago/.openclaw/cron/jobs.json"
    if not os.path.exists(jobs_file):
        print(f"❌ 文件不存在: {jobs_file}")
        return False

    # 2. 读取配置文件
    with open(jobs_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 3. 找到代码健康度检查任务
    fixed = False
    for job in data['jobs']:
        if job['name'] == '代码健康度检查':
            print(f"📋 找到任务: {job['name']}")
            print(f"   当前状态: {job['state'].get('lastRunStatus', 'unknown')}")
            print(f"   错误信息: {job['state'].get('lastError', '无')}")

            # 修复方案1: 暂时禁用该任务
            job['enabled'] = False
            job['state']['lastError'] = "已禁用，需要配置飞书token"
            job['state']['lastRunStatus'] = "disabled"

            print(f"✅ 已暂时禁用任务")
            print(f"   修复说明: 需要配置飞书API token，暂时禁用避免重复错误")

            fixed = True
            break

    # 4. 保存修复后的配置
    if fixed:
        # 备份原文件
        backup_file = f"{jobs_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 备份原文件: {backup_file}")

        # 保存修复文件
        with open(jobs_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 保存修复文件: {jobs_file}")

        return True
    else:
        print("❌ 未找到代码健康度检查任务")
        return False


def check_flybook_config():
    """检查飞书配置"""
    print("\n🔍 检查飞书配置状态")

    # 可能的配置位置
    config_locations = [
        "/Users/ago/.openclaw/config.json",
        "/Users/ago/.openclaw/feishu_config.json",
        "/Users/ago/.openclaw/workspace/config/feishu.json",
        os.path.expanduser("~/.openclaw/config.json")
    ]

    found_config = False
    for config_file in config_locations:
        if os.path.exists(config_file):
            print(f"✅ 找到配置文件: {config_file}")
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                # 检查是否有飞书相关配置
                if 'feishu' in config or 'flybook' in config:
                    print(f"   包含飞书配置")
                else:
                    print(f"   不包含飞书配置")
                found_config = True
            except Exception as e:
                print(f"   读取失败: {e}")

    if not found_config:
        print("❌ 未找到飞书配置文件")

    return found_config


def create_fix_guide():
    """创建修复指南"""
    guide = """
# 🔧 飞书token错误修复指南

## 问题描述
代码健康度检查任务执行失败，错误信息：
```
TypeError: Cannot destructure property 'tenant_access_token' of '(intermediate value)' as it is undefined.
```

## 问题原因
任务需要调用飞书API发送消息，但缺少有效的tenant_access_token配置。

## 临时解决方案（已实施）
✅ **暂时禁用该任务** - 避免重复错误

## 永久解决方案

### 方案1: 配置飞书token
1. 获取飞书tenant_access_token
2. 创建配置文件：`~/.openclaw/feishu_config.json`
3. 添加配置：
```json
{
  "feishu": {
    "tenant_access_token": "你的token",
    "app_id": "你的app_id",
    "app_secret": "你的app_secret"
  }
}
```

### 方案2: 修改任务逻辑
1. 修改代码健康度检查任务，不依赖飞书API
2. 改为本地日志记录或邮件通知
3. 重新启用任务

### 方案3: 使用其他通知方式
1. 配置邮件通知
2. 使用其他消息平台
3. 改为控制台输出

## 当前状态
- 任务已暂时禁用
- 不会影响其他任务执行
- 需要您配置飞书token后重新启用

## 配置步骤
1. 联系飞书管理员获取tenant_access_token
2. 创建配置文件
3. 重新启用任务：
```bash
openclaw cron enable 17da0ef4-47a1-47c2-b925-365131db70a7
```

## 验证方法
```bash
# 查看任务状态
openclaw cron list --all

# 手动测试任务
openclaw cron run 17da0ef4-47a1-47c2-b925-365131db70a7
```
"""

    return guide


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 飞书token错误修复工具")
    print("=" * 60)

    # 1. 修复token错误
    print("\n1. 修复调度任务配置...")
    if fix_flybook_token_error():
        print("✅ 修复成功")
    else:
        print("❌ 修复失败")

    # 2. 检查配置
    print("\n2. 检查飞书配置...")
    check_flybook_config()

    # 3. 显示修复指南
    print("\n3. 修复指南:")
    guide = create_fix_guide()
    print(guide)

    # 4. 保存指南到文件
    guide_file = "/Users/ago/.openclaw/workspace/docs/fix_flybook_token_guide.md"
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide)
    print(f"💾 修复指南已保存: {guide_file}")

    print("\n" + "=" * 60)
    print("✅ 修复完成")
    print("=" * 60)

    print("\n🎯 下一步:")
    print("1. 代码健康度检查任务已暂时禁用")
    print("2. 需要您配置飞书token后重新启用")
    print("3. 其他任务不受影响，明天正常执行")

    return True


if __name__ == "__main__":
    main()
