#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据自动更新状态发送脚本
发送到: A股数据分析群
"""

import os
import sys
import json
import requests
from datetime import datetime

def send_to_feishu_group(content, title):
    """发送到飞书群"""
    webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/fb95ec56-6ad7-4830-99c7-0eaa287e67e7"
    
    message = {
        "msg_type": "interactive",
        "card": {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"📊 {title}"
                },
                "template": "blue"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": content
                    }
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": f"发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        }
                    ]
                }
            ]
        }
    }
    
    try:
        response = requests.post(webhook_url, json=message, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                print(f"✅ {title}已发送到A股数据分析群")
                return True
        return False
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        return False

def main():
    print(f"🚀 开始发送{task['name']}")
    print("=" * 60)
    
    # 这里应该包含具体的业务逻辑
    # 例如：读取报告文件、生成内容等
    
    content = f"""
**任务名称**: 股票数据自动更新状态
**执行时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**目标群组**: A股数据分析群

**状态**: ✅ 任务执行完成
**详情**: 这是股票数据自动更新状态的示例内容，实际使用时需要替换为具体业务逻辑。

**下一步**: 检查具体业务数据并生成详细报告。
"""
    
    success = send_to_feishu_group(content, task['name'])
    
    if success:
        # 记录日志
        log_dir = "/Users/ago/.openclaw/workspace/logs/group_notifications"
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{task['name'].replace(' ', '_')}.json")
        
        log_data = {
            "task": task['name'],
            "timestamp": datetime.now().isoformat(),
            "target_group": task['target_group'],
            "status": "success"
        }
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 发送日志已保存: {log_file}")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
