#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试正确的飞书聊天ID格式
"""

import os
import json
import subprocess
from datetime import datetime

def test_with_webhook_token():
    """使用Webhook token作为聊天ID测试"""
    print("🧪 测试Webhook token作为聊天ID")
    print("=" * 60)
    
    # 工作沟通汇报群的Webhook token
    work_group_token = "7c6e2bb9-0f2f-4d16-ade1-e93cf6bd3065"
    
    # 测试不同的格式
    test_cases = [
        {
            "name": "格式1: chat: + token",
            "chat_id": f"chat:{work_group_token}",
            "description": "使用chat:前缀加上Webhook token"
        },
        {
            "name": "格式2: feishu: + token", 
            "chat_id": f"feishu:{work_group_token}",
            "description": "使用feishu:前缀加上Webhook token"
        },
        {
            "name": "格式3: 直接使用token",
            "chat_id": work_group_token,
            "description": "直接使用Webhook token，不加前缀"
        },
        {
            "name": "格式4: 现有配置格式",
            "chat_id": "chat:oc_9d6f8d5a6d6a4d6b8d5a6d6a4d6b8d5a",
            "description": "使用现有的配置格式"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n📋 测试: {test_case['name']}")
        print(f"   聊天ID: {test_case['chat_id']}")
        print(f"   描述: {test_case['description']}")
        
        # 创建测试任务
        test_message = f"测试聊天ID格式: {test_case['name']} - {datetime.now().strftime('%H:%M:%S')}"
        
        try:
            # 创建cron任务
            result = subprocess.run(
                ["openclaw", "cron", "add",
                 "--name", f"测试-{test_case['name']}",
                 "--cron", "*/2 * * * *",  # 每2分钟执行一次
                 "--message", test_message,
                 "--announce",
                 "--to", test_case['chat_id']],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # 解析任务ID
                import re
                task_id_match = re.search(r'"id":\s*"([^"]+)"', result.stdout)
                if task_id_match:
                    task_id = task_id_match.group(1)
                    print(f"   ✅ 任务创建成功: {task_id}")
                    
                    # 立即运行任务
                    run_result = subprocess.run(
                        ["openclaw", "cron", "run", task_id],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if run_result.returncode == 0:
                        print(f"   ✅ 任务运行已触发")
                        
                        # 等待几秒后检查结果
                        import time
                        time.sleep(3)
                        
                        # 检查运行结果
                        runs_result = subprocess.run(
                            ["openclaw", "cron", "runs", "--id", task_id],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        
                        if runs_result.returncode == 0:
                            runs_data = json.loads(runs_result.stdout)
                            if runs_data.get("entries"):
                                last_run = runs_data["entries"][0]
                                status = last_run.get("status", "unknown")
                                error = last_run.get("error", "")
                                
                                if status == "success":
                                    print(f"   🎉 任务执行成功!")
                                    test_case["result"] = "success"
                                else:
                                    print(f"   ❌ 任务执行失败: {error}")
                                    test_case["result"] = f"failed: {error}"
                            else:
                                print(f"   ⚠️  无运行记录")
                                test_case["result"] = "no runs"
                        else:
                            print(f"   ❌ 无法获取运行记录")
                            test_case["result"] = "cannot get runs"
                    else:
                        print(f"   ❌ 任务运行失败: {run_result.stderr}")
                        test_case["result"] = "run failed"
                else:
                    print(f"   ❌ 无法解析任务ID")
                    test_case["result"] = "cannot parse task id"
            else:
                print(f"   ❌ 任务创建失败: {result.stderr}")
                test_case["result"] = "creation failed"
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ 操作超时")
            test_case["result"] = "timeout"
        except Exception as e:
            print(f"   ❌ 异常: {e}")
            test_case["result"] = f"exception: {e}"
        
        # 清理测试任务
        if 'task_id' in locals():
            try:
                subprocess.run(
                    ["openclaw", "cron", "rm", task_id],
                    capture_output=True,
                    timeout=5
                )
                print(f"   🧹 测试任务已清理")
            except:
                pass
        
        results.append(test_case)
    
    return results

def analyze_results(results):
    """分析测试结果"""
    print("\n" + "=" * 60)
    print("📊 测试结果分析")
    print("=" * 60)
    
    success_count = 0
    failure_count = 0
    
    for result in results:
        if "success" in str(result.get("result", "")):
            success_count += 1
            status = "✅"
        else:
            failure_count += 1
            status = "❌"
        
        print(f"\n{status} {result['name']}")
        print(f"   聊天ID: {result['chat_id']}")
        print(f"   结果: {result.get('result', '未知')}")
    
    print("\n" + "=" * 60)
    print("🎯 结论:")
    
    if success_count > 0:
        print(f"✅ 找到 {success_count} 个有效的聊天ID格式")
        print("   建议使用成功的格式修复cron任务")
    else:
        print("❌ 所有测试格式都失败")
        print("   可能需要其他格式或配置")
    
    print(f"\n📋 成功: {success_count}, 失败: {failure_count}")

def check_manual_send():
    """检查手动发送是否工作"""
    print("\n🔍 检查手动发送功能")
    print("-" * 50)
    
    print("测试手动发送消息到工作群...")
    
    # 使用我们之前创建的发送脚本
    script_path = "/Users/ago/.openclaw/workspace/scripts/send_health_check_to_group.py"
    
    if os.path.exists(script_path):
        try:
            result = subprocess.run(
                ["python3", script_path],
                cwd="/Users/ago/.openclaw/workspace",
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("✅ 手动发送测试成功")
                print(f"   输出: {result.stdout[:100]}...")
            else:
                print("❌ 手动发送测试失败")
                print(f"   错误: {result.stderr}")
        except Exception as e:
            print(f"❌ 手动发送异常: {e}")
    else:
        print("❌ 发送脚本不存在")

def main():
    print("🔧 测试正确的飞书聊天ID格式")
    print("=" * 60)
    
    print("🎯 目标: 通过测试找出cron任务正确的聊天ID格式")
    print("      解决'Delivering to Feishu requires target'错误")
    
    # 测试不同的聊天ID格式
    results = test_with_webhook_token()
    
    # 分析结果
    analyze_results(results)
    
    # 检查手动发送
    check_manual_send()
    
    print("\n" + "=" * 60)
    print("💡 建议:")
    print("   1. 如果找到成功的格式，使用该格式修复所有cron任务")
    print("   2. 如果所有格式都失败，可能需要:")
    print("      • 查看OpenClaw飞书插件文档")
    print("      • 检查飞书群聊的实际ID")
    print("      • 使用Webhook方式而不是cron delivery")
    
    print(f"\n🕐 测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()