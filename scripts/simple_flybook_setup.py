#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版飞书Webhook配置
"""

import json
import os
import sys


def main():
    print("=" * 60)
    print("🤖 飞书Webhook简化配置")
    print("=" * 60)

    print("\n🎯 推荐方案：使用自定义机器人（最简单）")
    print("   无需Tenant Access Token，只需Webhook地址")

    print("\n📋 操作步骤：")
    print("1. 打开'A股数据分析'飞书群")
    print("2. 点击右上角'...' → 设置 → 群机器人")
    print("3. 点击'添加机器人' → 选择'自定义机器人'")
    print("4. 设置名称：'代码健康检查机器人'")
    print("5. 点击'添加'，复制Webhook地址")

    print("\n🔗 Webhook地址格式：")
    print("https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")

    print("\n💡 提示：")
    print("• 创建机器人后立即生效")
    print("• 无需审批，免费使用")
    print("• 仅限当前群使用")

    # 直接询问Webhook地址
    print("\n" + "=" * 60)
    print("📝 请输入Webhook地址（或输入'skip'跳过）：")

    try:
        webhook_url = input("Webhook地址: ").strip()

        if webhook_url.lower() == 'skip':
            print("⏸️ 跳过配置")
            return

        # 验证格式
        if not webhook_url.startswith("https://open.feishu.cn/open-apis/bot/v2/hook/"):
            print("❌ 地址格式不正确")
            print("   正确格式：https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
            return

        # 创建配置
        config_dir = os.path.expanduser("~/.openclaw")
        config_file = os.path.join(config_dir, "feishu_config.json")

        os.makedirs(config_dir, exist_ok=True)

        config = {
            "feishu": {
                "webhook_url": webhook_url,
                "hook_token": webhook_url.split("/")[-1],
                "config_type": "webhook_robot",
                "configured_at": "2026-03-29"
            }
        }

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        print(f"✅ 配置文件已创建：{config_file}")

        # 测试配置
        print("\n🧪 测试配置...")
        test_result = test_webhook(webhook_url)

        if test_result:
            print("✅ 配置测试成功！")

            # 创建启用脚本
            create_enable_script()

            print("\n🎯 下一步：")
            print("1. 运行启用脚本：bash scripts/enable_code_health_check.sh")
            print("2. 或手动启用：openclaw cron enable 17da0ef4-47a1-47c2-b925-365131db70a7")
            print("3. 验证：openclaw cron list --all")
        else:
            print("❌ 配置测试失败，请检查地址")

    except KeyboardInterrupt:
        print("\n👋 用户取消")
    except Exception as e:
        print(f"❌ 错误：{e}")


def test_webhook(webhook_url):
    """测试Webhook"""
    try:
        import requests

        test_msg = {
            "msg_type": "text",
            "content": {
                "text": "✅ 飞书Webhook配置测试成功\n时间：2026-03-29 23:35\n系统：量化分析系统"
            }
        }

        response = requests.post(webhook_url, json=test_msg, timeout=10)

        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                return True
            else:
                print(f"   飞书API错误：{result}")
                return False
        else:
            print(f"   HTTP错误：{response.status_code}")
            return False

    except Exception as e:
        print(f"   测试失败：{e}")
        return False


def create_enable_script():
    """创建启用脚本"""
    script = """#!/bin/bash
echo "🚀 启用代码健康度检查任务..."
openclaw cron enable 17da0ef4-47a1-47c2-b925-365131db70a7

echo ""
echo "📋 任务状态："
openclaw cron list --all | grep -A3 -B3 "代码健康度检查"

echo ""
echo "🎯 任务已启用，将在明天15:00自动执行"
echo "💡 如需立即测试：openclaw cron run 17da0ef4-47a1-47c2-b925-365131db70a7"
"""

    script_file = "/Users/ago/.openclaw/workspace/scripts/enable_code_health_check.sh"
    with open(script_file, 'w') as f:
        f.write(script)

    # 设置权限
    import stat
    os.chmod(script_file, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)

    print(f"📜 启用脚本已创建：{script_file}")


if __name__ == "__main__":
    main()
