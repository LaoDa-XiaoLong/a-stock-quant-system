#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书Webhook配置脚本
简化配置流程，只需提供Webhook地址
"""

import json
import os
import sys
from pathlib import Path


def setup_flybook_webhook():
    """配置飞书Webhook"""
    print("=" * 60)
    print("🚀 飞书Webhook配置工具")
    print("=" * 60)

    # 1. 显示配置说明
    print("\n📋 配置说明:")
    print("1. 在飞书群中创建自定义机器人")
    print("2. 获取Webhook地址")
    print("3. 在此输入Webhook地址")
    print("4. 系统自动创建配置文件")

    # 2. 获取Webhook地址
    print("\n🔗 请输入飞书Webhook地址:")
    print("格式: https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
    print("或直接粘贴完整地址")
    print("\n输入 'skip' 跳过配置，'test' 测试现有配置")

    webhook_url = input("\nWebhook地址: ").strip()

    if webhook_url.lower() == 'skip':
        print("⏸️  跳过配置")
        return False
    elif webhook_url.lower() == 'test':
        return test_existing_config()

    # 3. 验证Webhook地址格式
    if not webhook_url.startswith("https://open.feishu.cn/open-apis/bot/v2/hook/"):
        print(f"❌ Webhook地址格式不正确")
        print(f"   正确格式: https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
        return False

    # 4. 提取token
    hook_token = webhook_url.split("/")[-1]
    print(f"✅ 提取到token: {hook_token[:8]}...{hook_token[-8:]}")

    # 5. 创建配置文件
    config_dir = os.path.expanduser("~/.openclaw")
    config_file = os.path.join(config_dir, "feishu_config.json")

    # 确保目录存在
    os.makedirs(config_dir, exist_ok=True)

    # 创建配置
    config = {
        "feishu": {
            "webhook_url": webhook_url,
            "hook_token": hook_token,
            "config_type": "webhook_robot",
            "configured_at": "2026-03-29"
        }
    }

    # 保存配置
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"✅ 配置文件已创建: {config_file}")

    # 6. 显示配置内容
    print(f"\n📄 配置文件内容:")
    print(json.dumps(config, ensure_ascii=False, indent=2))

    # 7. 测试配置
    print(f"\n🧪 测试配置...")
    test_result = test_webhook_config(webhook_url)

    if test_result:
        print(f"✅ 配置测试成功!")

        # 8. 启用任务指南
        print(f"\n🎯 下一步操作:")
        print(f"1. 重新启用代码健康度检查任务:")
        print(f"   openclaw cron enable 17da0ef4-47a1-47c2-b925-365131db70a7")
        print(f"\n2. 验证任务状态:")
        print(f"   openclaw cron list --all")
        print(f"\n3. 手动测试任务:")
        print(f"   openclaw cron run 17da0ef4-47a1-47c2-b925-365131db70a7")

        # 9. 创建快速启用脚本
        create_enable_script()

        return True
    else:
        print(f"❌ 配置测试失败，请检查Webhook地址")
        return False


def test_webhook_config(webhook_url):
    """测试Webhook配置"""
    import requests

    try:
        # 简单的测试消息
        test_message = {
            "msg_type": "text",
            "content": {
                "text": "✅ 飞书Webhook配置测试成功\n时间: 2026-03-29 23:30\n系统: 量化分析系统"
            }
        }

        print(f"   发送测试消息到飞书群...")
        response = requests.post(
            webhook_url,
            json=test_message,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                print(f"   测试消息发送成功")
                return True
            else:
                print(f"   飞书API返回错误: {result}")
                return False
        else:
            print(f"   HTTP错误: {response.status_code}")
            print(f"   响应: {response.text}")
            return False

    except Exception as e:
        print(f"   测试失败: {e}")
        return False


def test_existing_config():
    """测试现有配置"""
    print("\n🔍 测试现有配置...")

    config_files = [
        os.path.expanduser("~/.openclaw/feishu_config.json"),
        "/Users/ago/.openclaw/feishu_config.json",
        "/Users/ago/.openclaw/config.json"
    ]

    found_config = False
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"✅ 找到配置文件: {config_file}")
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print(f"   配置内容: {json.dumps(config, ensure_ascii=False, indent=2)}")

                # 检查是否有Webhook配置
                if 'feishu' in config and 'webhook_url' in config['feishu']:
                    webhook_url = config['feishu']['webhook_url']
                    print(f"   找到Webhook地址: {webhook_url[:50]}...")

                    # 测试配置
                    print(f"\n🧪 测试现有配置...")
                    if test_webhook_config(webhook_url):
                        print(f"✅ 现有配置工作正常!")
                        return True
                    else:
                        print(f"❌ 现有配置测试失败")
                        return False

                found_config = True
            except Exception as e:
                print(f"   读取失败: {e}")

    if not found_config:
        print("❌ 未找到现有配置文件")

    return False


def create_enable_script():
    """创建快速启用脚本"""
    script_content = """#!/bin/bash
# 快速启用代码健康度检查任务

echo "🚀 启用代码健康度检查任务..."
openclaw cron enable 17da0ef4-47a1-47c2-b925-365131db70a7

echo "📋 查看任务状态..."
openclaw cron list --all | grep -A5 -B5 "代码健康度检查"

echo "🎯 任务已启用，将在明天15:00自动执行"
echo "💡 如需立即测试: openclaw cron run 17da0ef4-47a1-47c2-b925-365131db70a7"
"""

    script_file = "/Users/ago/.openclaw/workspace/scripts/enable_code_health_check.sh"
    with open(script_file, 'w') as f:
        f.write(script_content)

    # 设置执行权限
    import stat
    os.chmod(script_file, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)

    print(f"📜 快速启用脚本已创建: {script_file}")
    print(f"   使用: bash {script_file}")


def show_robot_creation_guide():
    """显示机器人创建指南"""
    guide = """
# 🤖 飞书自定义机器人创建指南

## 步骤1：打开飞书群
1. 打开"A股数据分析"飞书群
2. 点击右上角"..."更多按钮
3. 选择"设置"

## 步骤2：添加机器人
1. 在设置页面选择"群机器人"
2. 点击"添加机器人"
3. 选择"自定义机器人"

## 步骤3：配置机器人
1. 机器人名称: "代码健康检查机器人"
2. 描述: "自动检查代码健康度并发送报告"
3. 点击"添加"

## 步骤4：获取Webhook地址
1. 添加成功后，复制Webhook地址
2. 地址格式: https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
3. 保存地址用于配置

## 步骤5：安全设置（可选）
1. 自定义关键词: "代码检查"、"健康度"
2. IP白名单: 可不设置
3. 签名校验: 建议启用

## 注意事项
✅ 机器人创建后立即生效
✅ 无需审批，直接使用
✅ 免费，无使用限制
✅ 仅限当前群使用
"""

    print(guide)

    # 保存指南到文件
    guide_file = "/Users/ago/.openclaw/workspace/docs/flybook_robot_creation_guide.md"
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide)

    print(f"💾 指南已保存: {guide_file}")


def main():
    """主函数"""
    print("\n🎯 请选择操作:")
    print("1. 配置飞书Webhook（需要Webhook地址）")
    print("2. 查看机器人创建指南")
    print("3. 测试现有配置")
    print("4. 退出")

    try:
        choice = input("\n请选择 (1-4): ").strip()

        if choice == "1":
            setup_flybook_webhook()
        elif choice == "2":
            show_robot_creation_guide()
        elif choice == "3":
            test_existing_config()
        elif choice == "4":
            print("👋 退出")
        else:
            print("❌ 无效选择")

    except KeyboardInterrupt:
        print("\n👋 用户取消")
    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == "__main__":
    main()
