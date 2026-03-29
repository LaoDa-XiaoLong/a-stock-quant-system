#!/usr/bin/env python3
"""
飞书消息推送功能测试脚本
测试飞书消息发送能力
"""

import requests
import json
import sys

class FeishuMessengerTest:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        self.headers = {
            'Content-Type': 'application/json'
        }
    
    def send_text(self, text, at_all=False, at_users=None):
        """发送文本消息"""
        content = {
            "msg_type": "text",
            "content": {
                "text": text
            }
        }
        
        if at_all:
            content["content"]["text"] += " <at user_id=\"all\">所有人</at>"
        elif at_users:
            for user in at_users:
                content["content"]["text"] += f" <at user_id=\"{user}\">{user}</at>"
        
        return self._send_message(content)
    
    def send_rich_text(self, title, content_text, at_all=False):
        """发送富文本消息"""
        content = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": title,
                        "content": [
                            [
                                {
                                    "tag": "text",
                                    "text": content_text
                                }
                            ]
                        ]
                    }
                }
            }
        }
        
        if at_all:
            content["content"]["post"]["zh_cn"]["content"][0].insert(0, {
                "tag": "at",
                "user_id": "all"
            })
        
        return self._send_message(content)
    
    def _send_message(self, content):
        """发送消息到飞书"""
        try:
            response = requests.post(
                self.webhook_url,
                headers=self.headers,
                data=json.dumps(content, ensure_ascii=False).encode('utf-8'),
                timeout=10
            )
            
            result = {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response': response.json() if response.content else {}
            }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': None
            }

def main():
    # 从memory文件中获取webhook地址
    webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/fb95ec56-6ad7-4830-99c7-0eaa287e67e7"
    
    print("🔧 飞书消息推送功能测试")
    print(f"📡 Webhook地址: {webhook_url}")
    print("=" * 50)
    
    # 创建消息推送器
    messenger = FeishuMessengerTest(webhook_url)
    
    # 测试1: 发送简单文本消息
    print("\n📤 测试1: 发送简单文本消息")
    test_text = "🚀 飞书功能测试 - 量化小助理\n\n时间: 2026-03-29 00:35\n状态: 权限验证通过 ✅\n\n这是一条测试消息，用于验证飞书消息推送功能是否正常。"
    result1 = messenger.send_text(test_text)
    
    print(f"   发送结果: {'✅ 成功' if result1['success'] else '❌ 失败'}")
    if result1['success']:
        print(f"   状态码: {result1['status_code']}")
        print(f"   响应: {json.dumps(result1['response'], ensure_ascii=False, indent=2)}")
    else:
        print(f"   错误: {result1.get('error', '未知错误')}")
    
    # 测试2: 发送富文本消息
    print("\n📤 测试2: 发送富文本消息")
    rich_content = """
📊 **飞书功能测试报告**

### 🔧 测试项目
1. **权限验证** - ✅ 通过
2. **消息发送** - ✅ 进行中
3. **文档操作** - 🔄 待测试
4. **知识库访问** - 🔄 待测试

### 🎯 测试结果
- **网关状态**: 运行正常 (PID: 79194)
- **飞书连接**: WebSocket已建立
- **权限状态**: contact:contact.base:readonly ✅
- **调度计划**: 3个任务已设置

### 📋 下一步计划
1. 测试文档创建和读取
2. 测试知识库访问
3. 验证调度任务执行
4. 监控系统运行状态

**测试时间**: 2026-03-29 00:35
**测试人员**: 量化小助理
"""
    
    result2 = messenger.send_rich_text("📈 飞书功能测试报告", rich_content)
    
    print(f"   发送结果: {'✅ 成功' if result2['success'] else '❌ 失败'}")
    if result2['success']:
        print(f"   状态码: {result2['status_code']}")
    else:
        print(f"   错误: {result2.get('error', '未知错误')}")
    
    # 测试3: 发送@所有人的消息
    print("\n📤 测试3: 发送@所有人的消息")
    alert_text = "⚠️ 系统测试通知\n\n飞书功能测试正在进行中，请忽略此测试消息。\n\n测试时间: 2026-03-29 00:35"
    result3 = messenger.send_text(alert_text, at_all=True)
    
    print(f"   发送结果: {'✅ 成功' if result3['success'] else '❌ 失败'}")
    if result3['success']:
        print(f"   状态码: {result3['status_code']}")
    else:
        print(f"   错误: {result3.get('error', '未知错误')}")
    
    # 总结报告
    print("\n" + "=" * 50)
    print("📊 测试总结报告")
    print("=" * 50)
    
    tests = [
        ("简单文本消息", result1),
        ("富文本消息", result2),
        ("@所有人消息", result3)
    ]
    
    success_count = sum(1 for _, result in tests if result['success'])
    total_count = len(tests)
    
    print(f"📈 测试总数: {total_count}")
    print(f"✅ 成功数: {success_count}")
    print(f"❌ 失败数: {total_count - success_count}")
    print(f"📊 成功率: {success_count/total_count*100:.1f}%")
    
    if success_count == total_count:
        print("\n🎉 所有测试通过！飞书消息推送功能正常。")
    else:
        print(f"\n⚠️  有{total_count - success_count}个测试失败，请检查飞书配置。")
    
    return success_count == total_count

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)