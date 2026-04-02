#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全的飞书消息发送器
包含错误处理和降级策略
"""

import json
import time
import logging
from typing import Dict, Optional, Union
import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SafeFeishuSender:
    """安全的飞书消息发送器"""

    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url
        self.max_retries = 3
        self.retry_delay = 1.0

        # 统计信息
        self.stats = {
            'total_sent': 0,
            'success_count': 0,
            'failure_count': 0,
            'fallback_used': 0
        }

    def send_safely(self, message: str, message_type: str = 'text',
                   fallback_types: list = None) -> Dict:
        """
        安全发送消息，包含降级策略

        Args:
            message: 消息内容
            message_type: 首选消息类型 ('text', 'rich_text', 'card')
            fallback_types: 降级类型列表，默认 ['rich_text', 'text']

        Returns:
            发送结果
        """
        if fallback_types is None:
            fallback_types = ['rich_text', 'text']

        # 确保降级列表包含text作为最后手段
        if 'text' not in fallback_types:
            fallback_types.append('text')

        # 按优先级尝试发送
        types_to_try = [message_type] + [t for t in fallback_types if t != message_type]

        last_error = None
        for msg_type in types_to_try:
            try:
                if msg_type == 'text':
                    result = self._send_text(message)
                elif msg_type == 'rich_text':
                    result = self._send_rich_text("通知", message)
                elif msg_type == 'card':
                    result = self._send_simple_card("通知", message)
                else:
                    continue

                if result['success']:
                    if msg_type != message_type:
                        self.stats['fallback_used'] += 1
                        logger.info(f"使用降级策略: {message_type} -> {msg_type}")

                    return result

                last_error = result.get('error', '未知错误')

            except Exception as e:
                last_error = str(e)
                logger.warning(f"发送{msg_type}消息失败: {e}")

            # 重试延迟
            time.sleep(self.retry_delay)

        # 所有类型都失败
        self.stats['failure_count'] += 1
        return {
            'success': False,
            'error': f"所有消息类型都失败: {last_error}",
            'fallback_tried': True
        }

    def _send_text(self, text: str) -> Dict:
        """发送文本消息"""
        if not self.webhook_url:
            return {'success': False, 'error': '未配置webhook地址'}

        payload = {
            "msg_type": "text",
            "content": {
                "text": text
            }
        }

        return self._send_request(payload)

    def _send_rich_text(self, title: str, content: str) -> Dict:
        """发送富文本消息"""
        if not self.webhook_url:
            return {'success': False, 'error': '未配置webhook地址'}

        payload = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": title,
                        "content": [
                            [
                                {
                                    "tag": "text",
                                    "text": content
                                }
                            ]
                        ]
                    }
                }
            }
        }

        return self._send_request(payload)

    def _send_simple_card(self, title: str, content: str) -> Dict:
        """发送简化版卡片消息（避免400错误）"""
        if not self.webhook_url:
            return {'success': False, 'error': '未配置webhook地址'}

        # 使用最简单的卡片格式，避免复杂元素
        payload = {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": False  # 不使用宽屏模式，更兼容
                },
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": title[:50]  # 限制标题长度
                    }
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "plain_text",  # 使用纯文本，避免markdown解析问题
                            "content": content[:500]  # 限制内容长度
                        }
                    }
                ]
            }
        }

        return self._send_request(payload)

    def _send_request(self, payload: Dict) -> Dict:
        """发送HTTP请求"""
        headers = {'Content-Type': 'application/json'}

        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.webhook_url,
                    headers=headers,
                    data=json.dumps(payload, ensure_ascii=False),
                    timeout=10
                )

                self.stats['total_sent'] += 1

                if response.status_code == 200:
                    result = response.json()
                    if result.get('StatusCode') == 0:
                        self.stats['success_count'] += 1
                        return {
                            'success': True,
                            'status_code': response.status_code,
                            'response': result
                        }
                    else:
                        error_msg = result.get('msg', '未知错误')
                        return {
                            'success': False,
                            'status_code': response.status_code,
                            'error': f"飞书API错误: {error_msg}"
                        }
                elif response.status_code == 400:
                    # 特殊处理400错误
                    error_info = self._parse_400_error(response.text)
                    return {
                        'success': False,
                        'status_code': 400,
                        'error': f"HTTP 400错误: {error_info}",
                        'suggestion': '尝试使用文本或富文本消息'
                    }
                else:
                    return {
                        'success': False,
                        'status_code': response.status_code,
                        'error': f"HTTP错误: {response.status_code}"
                    }

            except requests.exceptions.Timeout:
                error_msg = f"请求超时 (尝试 {attempt + 1}/{self.max_retries})"
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # 指数退避
                else:
                    return {'success': False, 'error': error_msg}

            except Exception as e:
                return {'success': False, 'error': str(e)}

        return {'success': False, 'error': '所有重试都失败'}

    def _parse_400_error(self, response_text: str) -> str:
        """解析HTTP 400错误"""
        try:
            error_data = json.loads(response_text)
            return error_data.get('msg', '请求格式错误')
        except:
            return '请求格式错误（无法解析响应）'

    def get_stats(self) -> Dict:
        """获取统计信息"""
        total = self.stats['total_sent']
        success = self.stats['success_count']

        stats = self.stats.copy()
        stats['success_rate'] = success / total if total > 0 else 0
        stats['fallback_rate'] = self.stats['fallback_used'] / total if total > 0 else 0

        return stats


def example_usage():
    """使用示例"""
    print("安全飞书消息发送器示例")
    print("=" * 60)

    # 注意：需要配置webhook地址
    sender = SafeFeishuSender()

    # 测试消息
    test_message = "这是一条测试消息，如果卡片失败会自动降级到富文本或文本消息。"

    print("测试安全发送策略:")
    print(f"消息: {test_message[:50]}...")
    print("策略: 卡片 → 富文本 → 文本 (自动降级)")

    result = sender.send_safely(test_message, 'card')

    print(f"\n发送结果: {'✅ 成功' if result['success'] else '❌ 失败'}")
    if not result['success']:
        print(f"错误: {result.get('error', '未知错误')}")
        if 'suggestion' in result:
            print(f"建议: {result['suggestion']}")

    stats = sender.get_stats()
    print(f"\n统计信息:")
    print(f"  总发送数: {stats['total_sent']}")
    print(f"  成功数: {stats['success_count']}")
    print(f"  失败数: {stats['failure_count']}")
    print(f"  成功率: {stats['success_rate']:.0%}")
    print(f"  降级使用率: {stats['fallback_rate']:.0%}")

    print("\n" + "=" * 60)
    print("核心优势:")
    print("1. 自动降级: 卡片失败时自动尝试富文本，再失败尝试文本")
    print("2. 错误处理: 详细错误诊断和修复建议")
    print("3. 统计监控: 跟踪发送成功率和降级频率")
    print("4. 重试机制: 自动重试失败的消息")


if __name__ == "__main__":
    example_usage()
