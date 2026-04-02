#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书API测试工具
用于诊断和修复飞书API错误
"""

import json
import requests
import logging
from typing import Dict, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FeishuAPITester:
    """飞书API测试器"""

    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url
        self.test_results = []

    def test_connection(self) -> Dict:
        """测试连接"""
        if not self.webhook_url:
            return {
                'success': False,
                'error': '未提供webhook地址',
                'recommendation': '请在飞书群中创建机器人并获取webhook地址'
            }

        # 测试1: 简单文本消息
        test_payload = {
            "msg_type": "text",
            "content": {
                "text": "飞书API连接测试 - 如果收到此消息说明连接正常"
            }
        }

        try:
            response = requests.post(
                self.webhook_url,
                headers={'Content-Type': 'application/json'},
                data=json.dumps(test_payload, ensure_ascii=False),
                timeout=10
            )

            result = {
                'test': '文本消息发送',
                'status_code': response.status_code,
                'success': response.status_code == 200
            }

            if response.status_code == 200:
                response_data = response.json()
                result['response'] = response_data
                if response_data.get('StatusCode') == 0:
                    result['message'] = '✅ 连接测试成功'
                else:
                    result['message'] = f'❌ API返回错误: {response_data.get("msg", "未知错误")}'
                    result['success'] = False
            else:
                result['message'] = f'❌ HTTP错误: {response.status_code}'
                result['response_text'] = response.text[:200]

            self.test_results.append(result)
            return result

        except Exception as e:
            error_result = {
                'test': '文本消息发送',
                'success': False,
                'error': str(e),
                'message': '❌ 连接测试失败'
            }
            self.test_results.append(error_result)
            return error_result

    def test_card_message(self) -> Dict:
        """测试卡片消息"""
        if not self.webhook_url:
            return {
                'success': False,
                'error': '未提供webhook地址'
            }

        # 使用最简单的卡片格式
        test_card = {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True
                },
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": "测试卡片"
                    },
                    "template": "blue"
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": "这是一个测试卡片消息"
                        }
                    },
                    {
                        "tag": "action",
                        "actions": [
                            {
                                "tag": "button",
                                "text": {
                                    "tag": "plain_text",
                                    "content": "测试按钮"
                                },
                                "type": "default"
                            }
                        ]
                    }
                ]
            }
        }

        try:
            response = requests.post(
                self.webhook_url,
                headers={'Content-Type': 'application/json'},
                data=json.dumps(test_card, ensure_ascii=False),
                timeout=10
            )

            result = {
                'test': '卡片消息发送',
                'status_code': response.status_code,
                'success': response.status_code == 200
            }

            if response.status_code == 200:
                response_data = response.json()
                result['response'] = response_data
                if response_data.get('StatusCode') == 0:
                    result['message'] = '✅ 卡片消息测试成功'
                else:
                    result['message'] = f'❌ 卡片API错误: {response_data.get("msg", "未知错误")}'
                    result['success'] = False
            elif response.status_code == 400:
                result['message'] = '❌ HTTP 400错误: 请求格式错误'
                result['response_text'] = response.text[:500]
                result['diagnosis'] = self._diagnose_400_error(response.text)
            else:
                result['message'] = f'❌ HTTP错误: {response.status_code}'
                result['response_text'] = response.text[:200]

            self.test_results.append(result)
            return result

        except Exception as e:
            error_result = {
                'test': '卡片消息发送',
                'success': False,
                'error': str(e),
                'message': '❌ 卡片消息测试失败'
            }
            self.test_results.append(error_result)
            return error_result

    def _diagnose_400_error(self, response_text: str) -> str:
        """诊断HTTP 400错误"""
        diagnosis = []

        try:
            error_data = json.loads(response_text)

            if 'code' in error_data:
                diagnosis.append(f"错误代码: {error_data['code']}")

            if 'msg' in error_data:
                diagnosis.append(f"错误信息: {error_data['msg']}")

            # 常见错误模式
            error_msg = error_data.get('msg', '').lower()

            if 'invalid' in error_msg and 'json' in error_msg:
                diagnosis.append("可能原因: JSON格式无效")
                diagnosis.append("建议: 检查JSON格式，确保没有语法错误")

            elif 'missing' in error_msg:
                diagnosis.append("可能原因: 缺少必要字段")
                diagnosis.append("建议: 检查卡片配置是否完整")

            elif 'field' in error_msg:
                diagnosis.append("可能原因: 字段值无效")
                diagnosis.append("建议: 检查字段类型和取值范围")

            elif 'permission' in error_msg:
                diagnosis.append("可能原因: 权限不足")
                diagnosis.append("建议: 检查机器人是否有发送卡片消息的权限")

        except json.JSONDecodeError:
            diagnosis.append("响应不是有效的JSON格式")
            diagnosis.append(f"原始响应: {response_text[:100]}...")

        return '\n'.join(diagnosis)

    def test_rich_text(self) -> Dict:
        """测试富文本消息"""
        if not self.webhook_url:
            return {
                'success': False,
                'error': '未提供webhook地址'
            }

        # 使用简单的富文本格式
        test_rich = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": "测试富文本",
                        "content": [
                            [
                                {
                                    "tag": "text",
                                    "text": "这是一个测试富文本消息\n\n支持**加粗**和*斜体*"
                                }
                            ]
                        ]
                    }
                }
            }
        }

        try:
            response = requests.post(
                self.webhook_url,
                headers={'Content-Type': 'application/json'},
                data=json.dumps(test_rich, ensure_ascii=False),
                timeout=10
            )

            result = {
                'test': '富文本消息发送',
                'status_code': response.status_code,
                'success': response.status_code == 200
            }

            if response.status_code == 200:
                response_data = response.json()
                result['response'] = response_data
                if response_data.get('StatusCode') == 0:
                    result['message'] = '✅ 富文本消息测试成功'
                else:
                    result['message'] = f'❌ 富文本API错误: {response_data.get("msg", "未知错误")}'
                    result['success'] = False
            else:
                result['message'] = f'❌ HTTP错误: {response.status_code}'
                result['response_text'] = response.text[:200]

            self.test_results.append(result)
            return result

        except Exception as e:
            error_result = {
                'test': '富文本消息发送',
                'success': False,
                'error': str(e),
                'message': '❌ 富文本消息测试失败'
            }
            self.test_results.append(error_result)
            return error_result

    def run_all_tests(self) -> Dict:
        """运行所有测试"""
        logger.info("开始飞书API测试")

        results = {
            'connection': self.test_connection(),
            'rich_text': self.test_rich_text(),
            'card': self.test_card_message(),
            'summary': {}
        }

        # 计算摘要
        total_tests = 3
        passed_tests = sum(1 for test in [results['connection'], results['rich_text'], results['card']]
                          if test.get('success', False))

        results['summary'] = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': passed_tests / total_tests if total_tests > 0 else 0,
            'overall_status': '✅ 全部通过' if passed_tests == total_tests else '⚠️ 部分失败' if passed_tests > 0 else '❌ 全部失败'
        }

        logger.info(f"飞书API测试完成: {passed_tests}/{total_tests} 通过")
        return results


def main():
    """主函数"""
    print("飞书API测试工具")
    print("版本: 1.0.0")
    print("=" * 60)

    # 注意：这里需要真实的webhook地址
    # 由于安全原因，不在代码中硬编码
    webhook_url = None

    print("当前配置:")
    print(f"  Webhook地址: {'未配置' if not webhook_url else '已配置（隐藏）'}")
    print("\n测试说明:")
    print("1. 文本消息测试 - 基础连接测试")
    print("2. 富文本消息测试 - 格式化消息测试")
    print("3. 卡片消息测试 - 交互式卡片测试（之前报错的项目）")

    if not webhook_url:
        print("\n❌ 未配置webhook地址，无法进行测试")
        print("\n配置步骤:")
        print("1. 在飞书群中添加'群机器人'")
        print("2. 选择'自定义机器人'")
        print("3. 获取webhook地址")
        print("4. 在代码中配置webhook_url变量")
        return

    print("\n开始测试...")
    tester = FeishuAPITester(webhook_url)
    results = tester.run_all_tests()

    print("\n测试结果:")
    print("=" * 60)

    for test_name, test_result in results.items():
        if test_name == 'summary':
            continue

        print(f"\n{test_result.get('test', test_name)}:")
        print(f"  状态: {test_result.get('message', 'N/A')}")
        print(f"  状态码: {test_result.get('status_code', 'N/A')}")

        if not test_result.get('success', False):
            if 'error' in test_result:
                print(f"  错误: {test_result['error']}")
            if 'diagnosis' in test_result:
                print(f"  诊断: {test_result['diagnosis']}")

    print("\n" + "=" * 60)
    print("测试摘要:")
    summary = results['summary']
    print(f"  总测试数: {summary['total_tests']}")
    print(f"  通过数: {summary['passed_tests']}")
    print(f"  成功率: {summary['success_rate']:.0%}")
    print(f"  总体状态: {summary['overall_status']}")

    print("\n" + "=" * 60)
    print("建议:")

    if summary['passed_tests'] == summary['total_tests']:
        print("✅ 所有测试通过，飞书API连接正常")
    elif results['card'].get('status_code') == 400:
        print("⚠️ 卡片消息测试失败 (HTTP 400)")
        print("可能原因:")
        print("1. 卡片格式不符合飞书API要求")
        print("2. 机器人没有发送卡片消息的权限")
        print("3. 卡片包含无效字段或值")
        print("\n临时解决方案:")
        print("1. 暂时使用文本或富文本消息")
        print("2. 简化卡片格式，移除复杂元素")
        print("3. 检查飞书机器人权限设置")
    else:
        print("⚠️ 部分测试失败，请检查:")
        print("1. Webhook地址是否正确")
        print("2. 网络连接是否正常")
        print("3. 飞书机器人是否启用")


if __name__ == "__main__":
    main()
