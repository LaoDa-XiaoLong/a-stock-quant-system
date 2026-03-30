#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
找出正确的飞书聊天ID格式
"""

import os
import json
import subprocess
from datetime import datetime

def test_chat_id_format():
    """测试聊天ID格式"""
    print("🔍 测试飞书聊天ID格式")
    print("=" * 60)
    
    # 可能的聊天ID格式
    test_formats = [
        # 格式1: 直接使用Webhook token作为聊天ID的一部分
        "chat:7c6e2bb9-0f2f-4d16-ade1-e93cf6bd3065",
        
        # 格式2: 使用简化的ID
        "chat:work_group",
        "chat:stock_group",
        
        # 格式3: 使用现有的ID但去掉前缀
        "chat:9d6f8d5a6d6a4d6b8d5a6d6a4d6b8d5a",
        
        # 格式4: 使用不同的前缀
        "feishu:7c6e2bb9-0f2f-4d16-ade1-e93cf6bd3065",
        "group:7c6e2bb9-0f2f-4d16-ade1-e93cf6bd3065",
    ]
    
    print("📋 测试的聊天ID格式:")
    for fmt in test_formats:
        print(f"   • {fmt}")
    
    return test_formats

def check_existing_configs():
    """检查现有配置"""
    print("\n🔧 检查现有配置")
    print("-" * 50)
    
    # 检查cron配置
    cron_config_path = "/Users/ago/.openclaw/cron/jobs.json"
    if os.path.exists(cron_config_path):
        with open(cron_config_path, 'r') as f:
            config = json.load(f)
        
        print("📋 cron任务配置中的聊天ID:")
        for job in config.get("jobs", []):
            delivery = job.get("delivery", {})
            target = delivery.get("target", "未配置")
            name = job.get("name", "未知任务")
            print(f"   • {name}: {target}")
    
    # 检查脚本中的Webhook地址
    print("\n📋 脚本中的Webhook地址:")
    scripts_to_check = [
        "/Users/ago/.openclaw/workspace/scripts/generate_daily_report.py",
        "/Users/ago/.openclaw/workspace/scripts/send_financial_report_v3_fixed.py",
        "/Users/ago/.openclaw/workspace/scripts/send_health_check_to_group.py"
    ]
    
    for script_path in scripts_to_check:
        if os.path.exists(script_path):
            with open(script_path, 'r') as f:
                content = f.read()
                import re
                webhooks = re.findall(r'https://open\.feishu\.cn/open-apis/bot/v2/hook/[a-f0-9\-]+', content)
                if webhooks:
                    print(f"   • {os.path.basename(script_path)}: {webhooks[0][:50]}...")

def analyze_problem():
    """分析问题"""
    print("\n🔍 问题分析")
    print("-" * 50)
    
    print("🎯 已知信息:")
    print("   1. ✅ 昨天测试时收到了消息 → Webhook地址正确")
    print("   2. ❌ cron任务发送失败 → 聊天ID配置错误")
    print("   3. 🔍 需要找出正确的聊天ID格式")
    
    print("\n📊 可能的原因:")
    print("   1. 聊天ID格式错误（前缀不对）")
    print("   2. 使用了错误的聊天ID（不是Webhook token）")
    print("   3. OpenClaw需要特殊的聊天ID格式")
    
    print("\n💡 解决方案:")
    print("   1. 测试不同的聊天ID格式")
    print("   2. 查看OpenClaw文档确认正确格式")
    print("   3. 使用正确的格式修复cron任务")

def check_openclaw_docs():
    """检查OpenClaw文档"""
    print("\n📚 检查OpenClaw文档")
    print("-" * 50)
    
    print("搜索OpenClaw文档中的聊天ID格式...")
    
    # 尝试获取帮助信息
    try:
        result = subprocess.run(
            ["openclaw", "cron", "add", "--help"],
            capture_output=True,
            text=True
        )
        
        # 查找聊天ID相关的说明
        if "chatId" in result.stdout or "to" in result.stdout:
            lines = result.stdout.split('\n')
            for line in lines:
                if "chat" in line.lower() or "to" in line.lower():
                    print(f"   📝 {line.strip()}")
    except:
        print("   ⚠️  无法获取OpenClaw帮助信息")
    
    print("\n💡 根据OpenClaw CLI帮助，--to参数应该接受:")
    print("   • E.164号码（电话）")
    print("   • Telegram chatId")
    print("   • Discord channel/user")
    print("   • 可能也支持飞书聊天ID")

def create_test_cron_job():
    """创建测试cron任务"""
    print("\n🧪 创建测试cron任务")
    print("-" * 50)
    
    # 创建一个简单的测试任务
    test_message = "测试cron任务聊天ID配置 - " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("创建测试任务...")
    try:
        # 先创建一个不带delivery的任务
        result = subprocess.run(
            ["openclaw", "cron", "add", 
             "--name", "聊天ID测试任务",
             "--cron", "* * * * *",  # 每分钟执行，用于测试
             "--message", test_message,
             "--announce"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ 测试任务创建成功（不带--to参数）")
            print(f"   输出: {result.stdout[:100]}...")
            
            # 尝试解析任务ID
            import re
            task_id_match = re.search(r'"id":\s*"([^"]+)"', result.stdout)
            if task_id_match:
                task_id = task_id_match.group(1)
                print(f"   任务ID: {task_id}")
                return task_id
        else:
            print("❌ 测试任务创建失败")
            print(f"   错误: {result.stderr}")
            
    except Exception as e:
        print(f"❌ 创建测试任务异常: {e}")
    
    return None

def main():
    print("🔧 查找正确的飞书聊天ID格式")
    print("=" * 60)
    
    print("🎯 目标: 找出cron任务正确的聊天ID配置格式")
    print("      解决'Delivering to Feishu requires target'错误")
    
    # 测试聊天ID格式
    test_formats = test_chat_id_format()
    
    # 检查现有配置
    check_existing_configs()
    
    # 分析问题
    analyze_problem()
    
    # 检查OpenClaw文档
    check_openclaw_docs()
    
    # 创建测试cron任务
    task_id = create_test_cron_job()
    
    print("\n" + "=" * 60)
    print("📋 下一步行动:")
    print("   1. 需要确定正确的飞书聊天ID格式")
    print("   2. 使用正确格式修复所有cron任务")
    print("   3. 测试修复后的任务")
    
    if task_id:
        print(f"\n💡 测试任务ID: {task_id}")
        print("   可以手动运行测试: openclaw cron run " + task_id)
    
    print(f"\n🕐 分析完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()