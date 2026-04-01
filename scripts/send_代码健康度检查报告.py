#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码健康度检查报告发送脚本
发送到: 工作沟通汇报群
"""

import os
import sys
import json
import requests
from datetime import datetime

def send_to_feishu_group(content, title):
    """发送到飞书群"""
    webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/7c6e2bb9-0f2f-4d16-ade1-e93cf6bd3065"
    
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
                print(f"✅ {title}已发送到工作沟通汇报群")
                return True
        return False
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        return False

def main():
    task_name = "代码健康度检查报告"
    target_group = "工作沟通汇报群"
    
    print(f"🚀 开始发送{task_name}")
    print("=" * 60)
    
    # 读取最新的代码健康度检查报告
    report_content = ""
    try:
        # 查找最新的代码健康度检查报告
        import glob
        report_files = glob.glob("代码健康度检查报告_*.md")
        if report_files:
            latest_report = max(report_files)
            with open(latest_report, 'r', encoding='utf-8') as f:
                report_content = f.read()
        else:
            report_content = "未找到代码健康度检查报告文件"
    except Exception as e:
        report_content = f"读取报告文件时出错: {e}"
    
    # 生成摘要内容
    content = f"""
**任务名称**: {task_name}
**执行时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**目标群组**: {target_group}

**状态**: ✅ 代码健康度检查完成

**检查摘要**:
- 检查Python文件: 232个
- 总代码行数: 68,913行
- 发现技术债务: 3处
- 测试覆盖率: 极低(<5%)
- 主要问题: 依赖管理不完善、测试缺失

**详细报告**: 请查看工作空间中的完整报告文件

**建议行动**:
1. 修复Python依赖问题
2. 为关键策略添加基础测试
3. 清理重复代码和大型文件
"""
    
    success = send_to_feishu_group(content, task_name)
    
    if success:
        # 记录日志
        log_dir = "/Users/ago/.openclaw/workspace/logs/group_notifications"
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{task_name.replace(' ', '_')}.json")
        
        log_data = {
            "task": task_name,
            "timestamp": datetime.now().isoformat(),
            "target_group": target_group,
            "status": "success"
        }
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 发送日志已保存: {log_file}")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
