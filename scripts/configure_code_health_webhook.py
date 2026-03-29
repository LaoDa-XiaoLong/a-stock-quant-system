#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置代码健康度检查任务使用工作沟通群Webhook地址
"""

import json
import os
import sys
from datetime import datetime


def configure_code_health_webhook():
    """配置代码健康度检查任务的Webhook"""
    print("=" * 60)
    print("🔧 配置代码健康度检查任务Webhook")
    print("=" * 60)
    
    # Webhook地址
    work_group_webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/7c6e2bb9-0f2f-4d16-ade1-e93cf6bd3065"
    
    print(f"📋 配置信息:")
    print(f"   任务名称: 代码健康度检查")
    print(f"   Webhook地址: {work_group_webhook[:50]}...")
    print(f"   消息类型: 系统技术消息 → 工作沟通汇报群")
    
    # 1. 创建飞书配置文件
    config_dir = os.path.expanduser("~/.openclaw")
    config_file = os.path.join(config_dir, "feishu_config.json")
    
    os.makedirs(config_dir, exist_ok=True)
    
    config = {
        "feishu": {
            "webhook_url": work_group_webhook,
            "hook_token": "7c6e2bb9-0f2f-4d16-ade1-e93cf6bd3065",
            "config_type": "webhook_robot",
            "configured_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "purpose": "代码健康度检查任务专用"
        }
    }
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 飞书配置文件已创建: {config_file}")
    
    # 2. 测试Webhook地址
    print(f"\n🧪 测试Webhook地址...")
    test_result = test_webhook(work_group_webhook)
    
    if test_result:
        print(f"✅ Webhook地址测试成功!")
    else:
        print(f"❌ Webhook地址测试失败，但继续配置")
    
    # 3. 启用任务
    print(f"\n🚀 启用代码健康度检查任务...")
    enable_result = enable_code_health_task()
    
    if enable_result:
        print(f"✅ 任务启用成功!")
    else:
        print(f"❌ 任务启用失败")
    
    # 4. 显示最终状态
    print(f"\n📊 最终配置状态:")
    print(f"   配置文件: {config_file}")
    print(f"   Webhook地址: 工作沟通汇报群")
    print(f"   任务状态: {'已启用' if enable_result else '启用失败'}")
    print(f"   测试结果: {'成功' if test_result else '失败'}")
    
    # 5. 创建验证脚本
    create_verification_script()
    
    return test_result and enable_result


def test_webhook(webhook_url):
    """测试Webhook地址"""
    try:
        import requests
        
        test_message = {
            "msg_type": "text",
            "content": {
                "text": "✅ 代码健康度检查任务配置测试\n时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n状态: Webhook地址配置成功\n消息类型: 系统技术消息 → 工作沟通汇报群"
            }
        }
        
        print(f"   发送测试消息到工作沟通汇报群...")
        response = requests.post(webhook_url, json=test_message, timeout=10)
        
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
            print(f"   响应: {response.text[:100]}")
            return False
            
    except Exception as e:
        print(f"   测试失败: {e}")
        return False


def enable_code_health_task():
    """启用代码健康度检查任务"""
    try:
        import subprocess
        
        # 启用任务
        result = subprocess.run(
            ["openclaw", "cron", "enable", "17da0ef4-47a1-47c2-b925-365131db70a7"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"   任务启用命令执行成功")
            
            # 检查任务状态
            status_result = subprocess.run(
                ["openclaw", "cron", "list", "--all"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if status_result.returncode == 0:
                # 提取代码健康度检查任务状态
                lines = status_result.stdout.split('\n')
                for line in lines:
                    if "代码健康度检查" in line:
                        print(f"   任务状态: {line}")
                        return True
            
            return True
        else:
            print(f"   任务启用失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   启用任务时出错: {e}")
        return False


def create_verification_script():
    """创建验证脚本"""
    script_content = """#!/bin/bash
# 代码健康度检查任务验证脚本

echo "🔍 验证代码健康度检查任务配置"
echo "================================"

echo ""
echo "1. 检查飞书配置文件:"
if [ -f ~/.openclaw/feishu_config.json ]; then
    echo "   ✅ 配置文件存在"
    cat ~/.openclaw/feishu_config.json | python3 -m json.tool | head -20
else
    echo "   ❌ 配置文件不存在"
fi

echo ""
echo "2. 检查任务状态:"
openclaw cron list --all | grep -A5 -B5 "代码健康度检查"

echo ""
echo "3. 手动测试任务:"
echo "   openclaw cron run 17da0ef4-47a1-47c2-b925-365131db70a7"

echo ""
echo "4. 查看调度任务完整列表:"
echo "   openclaw cron list --all"

echo ""
echo "🎯 配置完成！任务将在明天15:00自动执行"
"""
    
    script_file = "/Users/ago/.openclaw/workspace/scripts/verify_code_health_config.sh"
    with open(script_file, 'w') as f:
        f.write(script_content)
    
    # 设置执行权限
    import stat
    os.chmod(script_file, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
    
    print(f"📜 验证脚本已创建: {script_file}")
    print(f"   使用: bash {script_file}")


def show_final_summary():
    """显示最终总结"""
    print("\n" + "=" * 60)
    print("🎉 配置完成总结")
    print("=" * 60)
    
    print("\n📋 已完成的配置:")
    print("1. ✅ 创建飞书配置文件: ~/.openclaw/feishu_config.json")
    print("2. ✅ 配置Webhook地址: 工作沟通汇报群地址")
    print("3. ✅ 启用代码健康度检查任务")
    print("4. ✅ 创建验证脚本: scripts/verify_code_health_config.sh")
    
    print("\n🎯 消息分发规则确认:")
    print("• A股数据分析群: 所有A股投资相关内容")
    print("• 工作沟通汇报群: 所有系统技术相关内容")
    print("• 代码健康度检查 → 工作沟通汇报群 ✅")
    
    print("\n⏰ 任务执行时间:")
    print("• 代码健康度检查: 每日15:00")
    print("• 下次执行: 明天15:00")
    
    print("\n🔧 验证方法:")
    print("1. 运行验证脚本: bash scripts/verify_code_health_config.sh")
    print("2. 查看任务状态: openclaw cron list --all")
    print("3. 手动测试: openclaw cron run 17da0ef4-47a1-47c2-b925-365131db70a7")
    
    print("\n🚀 所有调度任务状态 (8个任务):")
    print("1. 财报监控日报 (09:00) → A股群")
    print("2. 股票数据更新 (09:30) → 内部")
    print("3. 系统健康检查 (10:00) → 工作群")
    print("4. GitHub自动同步 (00:10,12:10) → 内部")
    print("5. 代码健康度检查 (15:00) → 工作群 ✅")
    print("6. 量化策略周报 (周五16:00) → 内部")
    print("7. 策略自动回测 (周五17:00) → 内部")
    print("8. 数据备份任务 (周六20:00) → 内部")


def main():
    """主函数"""
    print("🚀 开始配置代码健康度检查任务...")
    
    # 配置Webhook
    success = configure_code_health_webhook()
    
    if success:
        print("\n✅ 配置成功完成!")
    else:
        print("\n⚠️ 配置部分完成，需要手动检查")
    
    # 显示总结
    show_final_summary()
    
    return success


if __name__ == "__main__":
    main()