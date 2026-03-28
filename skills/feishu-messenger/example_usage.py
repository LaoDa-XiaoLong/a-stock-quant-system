#!/usr/bin/env python3
"""
飞书消息推送器使用示例
"""

import sys
import os
import time
from datetime import datetime

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from feishu_messenger import FeishuMessenger

def example_basic():
    """基础使用示例"""
    print("飞书消息推送器 - 基础使用示例")
    print("=" * 60)
    
    # 注意：需要替换为真实的webhook地址
    # 这里使用模拟模式，不实际发送
    webhook_url = None
    
    # 创建消息推送器
    messenger = FeishuMessenger(webhook_url)
    
    print("1. 功能演示（模拟模式）...")
    print("   注意: 未配置webhook地址，仅演示功能")
    
    # 发送文本消息（模拟）
    print("\n2. 文本消息示例:")
    print("   消息: '这是一条测试消息'")
    print("   结果: 模拟发送（需要配置webhook）")
    
    # 富文本消息示例
    print("\n3. 富文本消息示例:")
    print("   标题: '测试通知'")
    print("   内容: '**加粗文本** *斜体文本*'")
    print("   结果: 模拟发送（需要配置webhook）")
    
    return messenger

def example_advanced():
    """高级功能示例"""
    print("\n" + "=" * 60)
    print("飞书消息推送器 - 高级功能示例")
    print("=" * 60)
    
    messenger = FeishuMessenger()
    
    # 消息队列示例
    print("\n1. 消息队列功能:")
    messenger.enable_queue(max_size=10, flush_interval=5)
    
    for i in range(3):
        messenger.queue_text(f"队列测试消息 {i+1}")
        print(f"   添加到队列: 消息 {i+1}")
    
    print(f"   队列大小: {messenger.message_queue.qsize()}")
    
    # 配置演示
    print("\n2. 配置功能演示:")
    messenger.configure_retry(max_retries=3, retry_delay=1.0)
    messenger.configure_limits(max_daily_messages=1000, rate_limit_per_minute=20)
    print("   重试配置: 最大3次重试，延迟1秒")
    print("   限制配置: 每日1000条，每分钟20条")
    
    # 模板消息示例
    print("\n3. 模板消息示例:")
    template = """
# {{title}}
**时间**: {{time}}
**发送者**: {{sender}}

## 内容
{{content}}

{% if urgent %}
⚠️ **这是一条紧急消息**
{% endif %}
"""
    
    template_data = {
        'title': '系统通知',
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'sender': '量化小助理',
        'content': '系统运行正常，所有服务可用。',
        'urgent': False
    }
    
    print("   模板:", template[:50] + "...")
    print("   数据:", {k: v for k, v in template_data.items() if k != 'content'})
    print("   内容长度:", len(template_data['content']))
    
    # 统计功能
    print("\n4. 统计功能演示:")
    stats = messenger.get_send_stats()
    print(f"   总发送数: {stats['total_sent']} (模拟)")
    print(f"   队列大小: {stats['queue_size']}")
    print(f"   每日限制: {stats['daily_limit']}")
    
    return messenger

def example_integration():
    """集成示例"""
    print("\n" + "=" * 60)
    print("飞书消息推送器 - 集成示例")
    print("=" * 60)
    
    # 模拟一个监控系统
    class SystemMonitor:
        def __init__(self):
            # 这里应该使用真实的webhook地址
            self.messenger = FeishuMessenger()
            self.messenger.enable_queue()
        
        def send_alert(self, level, component, message):
            """发送系统报警"""
            if level == 'critical':
                title = "🚨 严重报警"
                content = f"**组件**: {component}\n**问题**: {message}\n\n需要立即处理！"
                at_all = True
            elif level == 'warning':
                title = "⚠️ 警告"
                content = f"**组件**: {component}\n**问题**: {message}\n\n请及时处理。"
                at_all = False
            else:
                title = "ℹ️ 通知"
                content = f"**组件**: {component}\n**信息**: {message}"
                at_all = False
            
            # 添加到队列
            self.messenger.queue_text(f"{title}: {component} - {message}")
            
            print(f"   报警添加到队列: {title} - {component}")
    
    # 测试监控系统
    monitor = SystemMonitor()
    
    print("\n模拟系统监控报警:")
    monitor.send_alert('info', '数据库', '备份完成')
    monitor.send_alert('warning', 'Web服务器', 'CPU使用率85%')
    monitor.send_alert('critical', '支付系统', '服务不可用')
    
    print(f"\n当前队列大小: {monitor.messenger.message_queue.qsize()}")
    
    return monitor

def main():
    """主函数"""
    print("飞书消息推送器使用示例")
    print("版本: 1.0.0")
    print("=" * 60)
    
    # 运行示例
    example_basic()
    example_advanced()
    example_integration()
    
    print("\n" + "=" * 60)
    print("示例运行完成")
    print("=" * 60)
    
    print("\n实际使用步骤:")
    print("1. 在飞书群中创建机器人，获取webhook地址")
    print("2. 初始化: messenger = FeishuMessenger('你的webhook地址')")
    print("3. 发送消息: messenger.send_text('Hello, World!')")
    print("4. 启用队列: messenger.enable_queue()")
    print("5. 查看统计: stats = messenger.get_send_stats()")
    
    print("\n注意事项:")
    print("1. 飞书消息有长度限制（约20,000字符）")
    print("2. 避免频繁发送，可能触发速率限制")
    print("3. 重要消息建议启用重试机制")
    print("4. 生产环境建议启用消息队列")

if __name__ == "__main__":
    main()