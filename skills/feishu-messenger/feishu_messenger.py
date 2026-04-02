#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书消息推送器
支持文本、富文本、卡片等多种消息格式
"""

import json
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
import requests
from queue import Queue
import hashlib
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MessageSendError(Exception):
    """消息发送异常"""
    pass


class FeishuMessenger:
    """飞书消息推送器"""

    def __init__(self, webhook_url: Union[str, List[str], Dict[str, str]] = None):
        """
        初始化消息推送器

        Args:
            webhook_url: 飞书webhook地址，可以是：
                - 字符串：单个webhook
                - 列表：多个webhook（负载均衡）
                - 字典：不同类型消息使用不同webhook
        """
        self.webhook_config = self._parse_webhook_config(webhook_url)

        # 消息队列
        self.message_queue = Queue()
        self.queue_enabled = False
        self.queue_max_size = 100
        self.flush_interval = 10  # 秒

        # 重试配置
        self.max_retries = 3
        self.retry_delay = 1.0
        self.exponential_backoff = True

        # 统计
        self.stats = {
            'total_sent': 0,
            'success_count': 0,
            'failure_count': 0,
            'total_response_time': 0.0,
            'failed_messages': []
        }

        # 限制配置
        self.limits = {
            'max_message_length': 20000,
            'max_daily_messages': 1000,
            'rate_limit_per_minute': 20,
            'daily_sent': 0,
            'last_reset_date': datetime.now().date()
        }

        # 调试模式
        self.debug_mode = False

        logger.info("飞书消息推送器初始化完成")

    def _parse_webhook_config(self, webhook_url) -> Dict:
        """解析webhook配置"""
        config = {'default': None, 'types': {}}

        if not webhook_url:
            return config

        if isinstance(webhook_url, str):
            config['default'] = webhook_url
            config['types']['text'] = webhook_url
            config['types']['rich_text'] = webhook_url
            config['types']['card'] = webhook_url

        elif isinstance(webhook_url, list):
            # 多个webhook，第一个作为默认
            if webhook_url:
                config['default'] = webhook_url[0]
                config['types']['text'] = webhook_url
                config['types']['rich_text'] = webhook_url
                config['types']['card'] = webhook_url

        elif isinstance(webhook_url, dict):
            config.update(webhook_url)
            if 'default' not in config and webhook_url:
                config['default'] = list(webhook_url.values())[0]

        return config

    def _get_webhook_url(self, message_type: str = 'text') -> Optional[str]:
        """获取webhook地址"""
        # 检查类型特定的webhook
        if message_type in self.webhook_config.get('types', {}):
            urls = self.webhook_config['types'][message_type]
            if isinstance(urls, list):
                # 负载均衡：轮询选择
                if not hasattr(self, '_url_index'):
                    self._url_index = {}
                if message_type not in self._url_index:
                    self._url_index[message_type] = 0

                idx = self._url_index[message_type]
                url = urls[idx]
                self._url_index[message_type] = (idx + 1) % len(urls)
                return url
            else:
                return urls

        # 使用默认webhook
        return self.webhook_config.get('default')

    def _check_limits(self) -> bool:
        """检查限制"""
        # 重置每日计数
        today = datetime.now().date()
        if today != self.limits['last_reset_date']:
            self.limits['daily_sent'] = 0
            self.limits['last_reset_date'] = today

        # 检查每日限制
        if self.limits['daily_sent'] >= self.limits['max_daily_messages']:
            logger.warning(f"达到每日消息限制: {self.limits['daily_sent']}/{self.limits['max_daily_messages']}")
            return False

        # 这里可以添加速率限制检查
        # ...

        return True

    def _update_stats(self, success: bool, response_time: float = 0.0):
        """更新统计"""
        self.stats['total_sent'] += 1
        self.limits['daily_sent'] += 1

        if success:
            self.stats['success_count'] += 1
            self.stats['total_response_time'] += response_time
        else:
            self.stats['failure_count'] += 1

    def _send_request(self, url: str, payload: Dict, message_type: str = 'text') -> Dict:
        """发送HTTP请求"""
        if not url:
            return {'success': False, 'error': '未配置webhook地址'}

        headers = {'Content-Type': 'application/json'}

        for attempt in range(self.max_retries):
            try:
                start_time = time.time()

                response = requests.post(
                    url,
                    headers=headers,
                    data=json.dumps(payload, ensure_ascii=False),
                    timeout=10
                )

                response_time = time.time() - start_time

                if response.status_code == 200:
                    result = response.json()
                    if result.get('StatusCode') == 0 or result.get('code') == 0:
                        return {
                            'success': True,
                            'status_code': response.status_code,
                            'response': result,
                            'response_time': response_time
                        }
                    else:
                        error_msg = result.get('msg', '未知错误')
                        return {
                            'success': False,
                            'status_code': response.status_code,
                            'error': f"飞书API错误: {error_msg}",
                            'response_time': response_time
                        }
                else:
                    return {
                        'success': False,
                        'status_code': response.status_code,
                        'error': f"HTTP错误: {response.status_code}",
                        'response_time': response_time
                    }

            except requests.exceptions.Timeout:
                error_msg = f"请求超时 (尝试 {attempt + 1}/{self.max_retries})"
                logger.warning(error_msg)

            except requests.exceptions.ConnectionError:
                error_msg = f"连接错误 (尝试 {attempt + 1}/{self.max_retries})"
                logger.warning(error_msg)

            except Exception as e:
                error_msg = f"请求异常: {str(e)} (尝试 {attempt + 1}/{self.max_retries})"
                logger.warning(error_msg)

            # 重试延迟
            if attempt < self.max_retries - 1:
                delay = self.retry_delay
                if self.exponential_backoff:
                    delay *= (2 ** attempt)  # 指数退避
                time.sleep(delay)

        return {
            'success': False,
            'error': f"所有重试都失败: {error_msg}",
            'status_code': None
        }

    def send_text(self, text: str, at_users: List[str] = None, at_all: bool = False) -> Dict:
        """
        发送文本消息

        Args:
            text: 消息文本
            at_users: 要@的用户ID列表
            at_all: 是否@所有人

        Returns:
            发送结果字典
        """
        # 检查限制
        if not self._check_limits():
            return {'success': False, 'error': '达到消息限制'}

        # 构建消息内容
        content = text

        # 添加@提醒
        if at_all:
            content += " <at user_id=\"all\">所有人</at>"
        elif at_users:
            for user_id in at_users:
                content += f" <at user_id=\"{user_id}\"></at>"

        # 构建payload
        payload = {
            "msg_type": "text",
            "content": {
                "text": content
            }
        }

        # 发送请求
        url = self._get_webhook_url('text')
        result = self._send_request(url, payload, 'text')

        # 更新统计
        self._update_stats(result['success'], result.get('response_time', 0))

        if self.debug_mode:
            logger.debug(f"发送文本消息: {text[:50]}..., 结果: {result['success']}")

        return result

    def send_rich_text(self, title: str, content: str, at_all: bool = False) -> Dict:
        """
        发送富文本消息

        Args:
            title: 消息标题
            content: 消息内容（支持markdown）
            at_all: 是否@所有人

        Returns:
            发送结果字典
        """
        # 检查限制
        if not self._check_limits():
            return {'success': False, 'error': '达到消息限制'}

        # 构建消息内容
        full_content = f"**{title}**\n\n{content}"

        if at_all:
            full_content += "\n\n<at user_id=\"all\">所有人</at>"

        # 构建payload
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
                                    "text": full_content
                                }
                            ]
                        ]
                    }
                }
            }
        }

        # 发送请求
        url = self._get_webhook_url('rich_text')
        result = self._send_request(url, payload, 'rich_text')

        # 更新统计
        self._update_stats(result['success'], result.get('response_time', 0))

        if self.debug_mode:
            logger.debug(f"发送富文本消息: {title}, 结果: {result['success']}")

        return result

    def send_card(self, card_config: Dict) -> Dict:
        """
        发送卡片消息

        Args:
            card_config: 卡片配置

        Returns:
            发送结果字典
        """
        # 检查限制
        if not self._check_limits():
            return {'success': False, 'error': '达到消息限制'}

        # 构建payload
        payload = {
            "msg_type": "interactive",
            "card": card_config
        }

        # 发送请求
        url = self._get_webhook_url('card')
        result = self._send_request(url, payload, 'card')

        # 更新统计
        self._update_stats(result['success'], result.get('response_time', 0))

        if self.debug_mode:
            logger.debug(f"发送卡片消息, 结果: {result['success']}")

        return result

    def send_template(self, template: str, data: Dict, message_type: str = 'text') -> Dict:
        """
        使用模板发送消息

        Args:
            template: 消息模板
            data: 模板数据
            message_type: 消息类型

        Returns:
            发送结果字典
        """
        # 简单模板替换
        message = template
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            message = message.replace(placeholder, str(value))

        # 条件处理（简单实现）
        import re
        condition_pattern = r'{%\s*if\s+(\w+)\s*%}(.*?){%\s*endif\s*%}'

        def replace_condition(match):
            var_name = match.group(1)
            content = match.group(2)
            if data.get(var_name):
                return content
            return ''

        message = re.sub(condition_pattern, replace_condition, message, flags=re.DOTALL)

        # 根据消息类型发送
        if message_type == 'rich_text':
            # 提取标题（第一行）
            lines = message.strip().split('\n')
            title = lines[0].strip('# ').strip() if lines else "消息"
            content = '\n'.join(lines[1:]) if len(lines) > 1 else ""
            return self.send_rich_text(title, content)
        else:
            return self.send_text(message)

    def queue_text(self, text: str, at_users: List[str] = None, at_all: bool = False):
        """添加文本消息到队列"""
        if not self.queue_enabled:
            logger.warning("消息队列未启用")
            return False

        if self.message_queue.qsize() >= self.queue_max_size:
            logger.warning(f"消息队列已满 ({self.message_queue.qsize()}/{self.queue_max_size})")
            return False

        message = {
            'type': 'text',
            'text': text,
            'at_users': at_users,
            'at_all': at_all,
            'timestamp': datetime.now().isoformat()
        }

        self.message_queue.put(message)
        logger.debug(f"消息添加到队列: {text[:30]}...")
        return True

    def flush_queue(self):
        """刷新消息队列"""
        if not self.queue_enabled:
            return

        messages = []
        while not self.message_queue.empty():
            messages.append(self.message_queue.get())

        if not messages:
            return

        logger.info(f"刷新消息队列: {len(messages)} 条消息")

        success_count = 0
        for msg in messages:
            try:
                if msg['type'] == 'text':
                    result = self.send_text(
                        msg['text'],
                        at_users=msg.get('at_users'),
                        at_all=msg.get('at_all', False)
                    )
                    if result['success']:
                        success_count += 1
                # 可以添加其他消息类型的处理
            except Exception as e:
                logger.error(f"处理队列消息失败: {e}")

        logger.info(f"队列刷新完成: {success_count}/{len(messages)} 成功")

    def enable_queue(self, max_size: int = 100, flush_interval: int = 10):
        """启用消息队列"""
        self.queue_enabled = True
        self.queue_max_size = max_size
        self.flush_interval = flush_interval

        # 启动自动刷新线程
        def auto_flush():
            while self.queue_enabled:
                time.sleep(self.flush_interval)
                try:
                    self.flush_queue()
                except Exception as e:
                    logger.error(f"自动刷新队列失败: {e}")

        thread = threading.Thread(target=auto_flush, daemon=True)
        thread.start()

        logger.info(f"启用消息队列: max_size={max_size}, flush_interval={flush_interval}s")

    def disable_queue(self):
        """禁用消息队列"""
        self.queue_enabled = False
        logger.info("禁用消息队列")

    def configure_retry(self, max_retries: int = 3, retry_delay: float = 1.0,
                       exponential_backoff: bool = True):
        """配置重试策略"""
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.exponential_backoff = exponential_backoff
        logger.info(f"配置重试策略: max_retries={max_retries}, delay={retry_delay}s, exponential={exponential_backoff}")

    def configure_limits(self, max_message_length: int = 20000,
                        max_daily_messages: int = 1000,
                        rate_limit_per_minute: int = 20):
        """配置消息限制"""
        self.limits['max_message_length'] = max_message_length
        self.limits['max_daily_messages'] = max_daily_messages
        self.limits['rate_limit_per_minute'] = rate_limit_per_minute
        logger.info(f"配置消息限制: max_length={max_message_length}, daily_max={max_daily_messages}, rate_limit={rate_limit_per_minute}/min")

    def get_send_stats(self) -> Dict:
        """获取发送统计"""
        total = self.stats['total_sent']
        success = self.stats['success_count']

        stats = {
            'total_sent': total,
            'success_count': success,
            'failure_count': self.stats['failure_count'],
            'success_rate': success / total if total > 0 else 0,
            'avg_response_time': self.stats['total_response_time'] / success if success > 0 else 0,
            'daily_sent': self.limits['daily_sent'],
            'daily_limit': self.limits['max_daily_messages'],
            'queue_size': self.message_queue.qsize() if self.queue_enabled else 0
        }

        return stats

    def reset_stats(self):
        """重置统计"""
        self.stats = {
            'total_sent': 0,
            'success_count': 0,
            'failure_count': 0,
            'total_response_time': 0.0,
            'failed_messages': []
        }
        logger.info("重置发送统计")

    def enable_debug(self, enabled: bool = True):
        """启用调试模式"""
        self.debug_mode = enabled
        log_level = logging.DEBUG if enabled else logging.INFO
        logger.setLevel(log_level)
        logger.info(f"{'启用' if enabled else '禁用'}调试模式")

    def test_connection(self) -> bool:
        """测试连接"""
        test_message = "飞书消息推送器连接测试"
        result = self.send_text(test_message)
