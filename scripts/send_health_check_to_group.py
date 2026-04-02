#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发送系统健康检查报告到工作群
"""

import os
import sys
import json
from datetime import datetime
import requests

def read_health_report():
    """读取最新的健康检查报告"""
    workspace = "/Users/ago/.openclaw/workspace"

    # 查找最新的健康检查报告
    import glob
    reports = glob.glob(os.path.join(workspace, "health_check_report_*.txt"))
    if not reports:
        return None

    # 按修改时间排序，获取最新的
    latest_report = max(reports, key=os.path.getmtime)

    with open(latest_report, 'r', encoding='utf-8') as f:
        content = f.read()

    return content, latest_report

def send_to_feishu_group(content, report_path):
    """发送到飞书工作群"""
    # 工作沟通汇报群Webhook地址
    webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/7c6e2bb9-0f2f-4d16-ade1-e93cf6bd3065"

    # 提取报告关键信息
    lines = content.split('\n')
    title = lines[0] if lines else "系统健康检查报告"

    # 提取检查时间
    check_time = "未知时间"
    for line in lines:
        if "检查时间:" in line:
            check_time = line.split("检查时间:")[1].strip()
            break

    # 提取健康状态
    health_status = "未知状态"
    for line in lines:
        if "整体健康状态:" in line:
            health_status = line.split("整体健康状态:")[1].strip()
            break

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
                    "content": f"📊 {title}"
                },
                "template": "green" if "良好" in health_status else "red"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**检查时间**: {check_time}\n**健康状态**: {health_status}\n**报告文件**: {os.path.basename(report_path)}"
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": "**报告摘要**:\n" + '\n'.join(lines[1:10]) + "\n\n**详细报告请查看附件文件**"
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
                print(f"✅ 健康检查报告已发送到工作群")
                print(f"   检查时间: {check_time}")
                print(f"   健康状态: {health_status}")
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
    print("📤 发送系统健康检查报告到工作群")
    print("=" * 50)

    # 读取报告
    result = read_health_report()
    if not result:
        print("❌ 未找到健康检查报告文件")
        return False

    content, report_path = result
    print(f"✅ 找到报告文件: {os.path.basename(report_path)}")
    print(f"   文件大小: {len(content)} 字符")

    # 发送到工作群
    success = send_to_feishu_group(content, report_path)

    if success:
        # 记录发送日志
        log_dir = "/Users/ago/.openclaw/workspace/logs/health_check_send"
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"send_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

        log_data = {
            "timestamp": datetime.now().isoformat(),
            "report_file": report_path,
            "send_status": "success",
            "check_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)

        print(f"✅ 发送日志已保存: {log_file}")

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
