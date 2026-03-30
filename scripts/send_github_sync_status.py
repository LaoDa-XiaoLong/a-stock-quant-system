#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发送GitHub同步状态到工作群
"""

import os
import sys
import json
import subprocess
from datetime import datetime
import requests

def check_github_sync():
    """检查GitHub同步状态"""
    workspace = "/Users/ago/.openclaw/workspace"
    
    # 运行GitHub同步检查
    try:
        result = subprocess.run(
            ["python3", "scripts/auto_git_sync.py", "--check"],
            cwd=workspace,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout
        return_code = result.returncode
        
        # 解析输出
        sync_status = "未知"
        changes = "无变更"
        
        if "没有变更需要提交" in output:
            sync_status = "✅ 同步完成 - 没有变更"
        elif "变更已提交" in output or "变更已推送" in output:
            sync_status = "✅ 同步完成 - 有变更"
            # 提取变更信息
            for line in output.split('\n'):
                if "变更:" in line or "changes:" in line:
                    changes = line.split(":")[1].strip()
                    break
        elif "错误" in output or "失败" in output or "error" in output.lower():
            sync_status = "❌ 同步失败"
            changes = output[-200:]  # 取最后200字符作为错误信息
        
        return {
            "status": sync_status,
            "changes": changes,
            "output": output[:500],  # 只取前500字符
            "return_code": return_code,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except subprocess.TimeoutExpired:
        return {
            "status": "❌ 同步超时",
            "changes": "检查超时（30秒）",
            "output": "",
            "return_code": -1,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {
            "status": f"❌ 检查异常: {str(e)}",
            "changes": "无法执行同步检查",
            "output": "",
            "return_code": -1,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

def send_to_feishu_group(sync_info):
    """发送到飞书工作群"""
    # 工作沟通汇报群Webhook地址
    webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/7c6e2bb9-0f2f-4d16-ade1-e93cf6bd3065"
    
    # 根据状态选择颜色
    status = sync_info["status"]
    template = "green" if "✅" in status else "red"
    
    # 创建飞书消息
    message = {
        "msg_type": "interactive",
        "card": {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "🔄 GitHub同步状态报告"
                },
                "template": template
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**检查时间**: {sync_info['timestamp']}\n**同步状态**: {status}\n**变更情况**: {sync_info['changes']}"
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": "**检查结果**:\n```\n" + sync_info['output'][:300] + "\n```"
                    }
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": f"自动检查时间: {datetime.now().strftime('%H:%M')}"
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
                print(f"✅ GitHub同步状态已发送到工作群")
                print(f"   同步状态: {status}")
                print(f"   变更情况: {sync_info['changes']}")
                return True
            else:
                print(f"❌ 发送失败: {result}")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 发送异常: {e}")
        return False

def main():
    print("🔄 检查并发送GitHub同步状态到工作群")
    print("=" * 50)
    
    # 检查GitHub同步状态
    print("🔍 检查GitHub同步状态...")
    sync_info = check_github_sync()
    
    print(f"✅ 同步状态检查完成")
    print(f"   状态: {sync_info['status']}")
    print(f"   变更: {sync_info['changes']}")
    
    # 发送到工作群
    success = send_to_feishu_group(sync_info)
    
    if success:
        # 记录发送日志
        log_dir = "/Users/ago/.openclaw/workspace/logs/github_sync_send"
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"send_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "sync_info": sync_info,
            "send_status": "success"
        }
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 发送日志已保存: {log_file}")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)