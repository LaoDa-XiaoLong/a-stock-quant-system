#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书消息格式兼容性测试
测试不同格式在飞书中的显示效果
"""

import json
import requests
from datetime import datetime

class FeishuFormatTester:
    """飞书格式测试器"""
    
    def __init__(self, webhook_url: str = None):
        # 使用测试webhook（实际使用时需要替换）
        self.webhook_url = webhook_url or "https://open.feishu.cn/open-apis/bot/v2/hook/fb95ec56-6ad7-4830-99c7-0eaa287e67e7"
        
    def test_html_format(self):
        """测试HTML格式"""
        print("🧪 测试HTML格式...")
        
        # 测试包含HTML标签的消息
        html_content = """
🚨 测试HTML格式兼容性

1. 使用<font color='green'>绿色字体</font>
2. 使用<font color='red'>红色字体</font>
3. 使用<font color='blue'>蓝色字体</font>
4. 使用<b>粗体标签</b>
5. 使用<i>斜体标签</i>
6. 使用<u>下划线标签</u>

预期：飞书可能无法正确解析HTML标签
"""
        
        return self._send_text_message("HTML格式测试", html_content)
    
    def test_markdown_format(self):
        """测试Markdown格式"""
        print("🧪 测试Markdown格式...")
        
        # 测试Markdown格式
        md_content = """
🚨 测试Markdown格式兼容性

1. 使用**粗体文本**
2. 使用*斜体文本*
3. 使用~~删除线文本~~
4. 使用`行内代码`
5. 使用[链接](https://example.com)

```python
# 代码块示例
def test():
    print("Hello Feishu")
```

- 无序列表项1
- 无序列表项2

1. 有序列表项1
2. 有序列表项2

> 引用文本

预期：飞书应该能正确解析Markdown
"""
        
        return self._send_text_message("Markdown格式测试", md_content)
    
    def test_emoji_format(self):
        """测试表情符号格式"""
        print("🧪 测试表情符号格式...")
        
        # 测试表情符号
        emoji_content = """
🎯 测试表情符号格式兼容性

📈 上升趋势: +25.6%
📉 下降趋势: -18.2%
💰 利润相关: 净利润增长
⚠️  警告信息: 需要关注
🚨 紧急警报: 大幅不及预期
✅ 成功标记: 操作成功
❌ 失败标记: 操作失败
🔍 观察标记: 需要观察
🎯 目标标记: 重点关注

颜色替代方案：
🟢 绿色圆形表示正面
🔴 红色圆形表示负面
🟡 黄色圆形表示中性
🔵 蓝色圆形表示信息

预期：表情符号应该能正常显示
"""
        
        return self._send_text_message("表情符号格式测试", emoji_content)
    
    def test_combined_format(self):
        """测试组合格式（推荐方案）"""
        print("🧪 测试组合格式（推荐方案）...")
        
        # 推荐的消息格式
        recommended_content = """
📊 财报监控日报格式优化方案

🎯 **核心原则**
1. 避免HTML标签（飞书不完全支持）
2. 优先使用Markdown格式
3. 使用表情符号替代颜色
4. 保持简洁清晰的排版

📈 **百分比格式化方案**
- 正面: 📈 +25.6% (使用上升箭头+绿色圆形)
- 负面: 📉 -18.2% (使用下降箭头+红色圆形)  
- 中性: 📊 ±5.3% (使用图表+蓝色圆形)

💡 **交易建议格式化方案**
- 强烈推荐: ✅🎯 强烈推荐加仓
- 考虑加仓: ✅ 考虑加仓
- 持有观察: 🔍 持有观察
- 关注风险: ⚠️ 关注风险
- 考虑减仓: 🚨 考虑减仓

📋 **排版建议**
1. 使用Markdown标题（## 二级标题）
2. 使用无序列表（- 项目）
3. 使用代码块展示数据
4. 使用分割线分隔章节

🔄 **格式转换示例**
原HTML格式: <font color='green'>📈 +25.6%</font>
新格式: 🟢📈 +25.6%

原HTML格式: <font color='red'>🚨 考虑减仓</font>
新格式: 🔴🚨 考虑减仓

✅ **优势**
1. 完全兼容飞书
2. 跨平台一致显示
3. 无需特殊解析
4. 移动端友好
"""
        
        return self._send_text_message("推荐格式方案", recommended_content)
    
    def test_card_format(self):
        """测试卡片格式"""
        print("🧪 测试卡片格式...")
        
        # 构建卡片消息
        card_payload = {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True
                },
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": "📊 卡片格式测试"
                    },
                    "template": "blue"
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",  # 使用飞书Markdown
                            "content": """
**卡片消息格式测试**

🎯 **使用lark_md标签的优势**
- 支持Markdown语法
- 更好的格式控制
- 飞书原生支持

📈 **百分比显示**
- 正面: **+25.6%** 🟢
- 负面: **-18.2%** 🔴
- 中性: **±5.3%** 🔵

💡 **建议使用卡片格式**
1. 格式更丰富
2. 支持颜色模板
3. 支持交互元素
4. 移动端优化
"""
                        }
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "note",
                        "elements": [
                            {
                                "tag": "plain_text",
                                "content": f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            }
                        ]
                    }
                ]
            }
        }
        
        return self._send_card_message(card_payload)
    
    def _send_text_message(self, title: str, content: str) -> bool:
        """发送文本消息"""
        try:
            # 构建消息
            message = f"**{title}**\n\n{content}"
            
            payload = {
                "msg_type": "text",
                "content": {
                    "text": message
                }
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            success = response.status_code == 200
            print(f"  {'✅' if success else '❌'} {title}: {'成功' if success else f'失败 ({response.status_code})'}")
            
            if not success and response.text:
                print(f"    错误信息: {response.text[:200]}")
            
            return success
            
        except Exception as e:
            print(f"  ❌ {title}: 异常 - {e}")
            return False
    
    def _send_card_message(self, payload: dict) -> bool:
        """发送卡片消息"""
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            success = response.status_code == 200
            print(f"  {'✅' if success else '❌'} 卡片格式测试: {'成功' if success else f'失败 ({response.status_code})'}")
            
            if not success and response.text:
                print(f"    错误信息: {response.text[:200]}")
            
            return success
            
        except Exception as e:
            print(f"  ❌ 卡片格式测试: 异常 - {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("🧪 飞书消息格式兼容性测试")
        print("=" * 60)
        
        results = []
        
        # 运行测试
        results.append(("HTML格式", self.test_html_format()))
        results.append(("Markdown格式", self.test_markdown_format()))
        results.append(("表情符号格式", self.test_emoji_format()))
        results.append(("组合格式", self.test_combined_format()))
        results.append(("卡片格式", self.test_card_format()))
        
        # 输出总结
        print("\n" + "=" * 60)
        print("📊 测试结果总结")
        print("=" * 60)
        
        success_count = sum(1 for _, success in results if success)
        total_count = len(results)
        
        for test_name, success in results:
            status = "✅ 通过" if success else "❌ 失败"
            print(f"{status} - {test_name}")
        
        print(f"\n🎯 总体成功率: {success_count}/{total_count} ({success_count/total_count*100:.0f}%)")
        
        # 给出建议
        print("\n💡 格式优化建议:")
        print("1. 避免使用HTML标签（<font>, <b>, <i>等）")
        print("2. 优先使用Markdown格式（**粗体**, *斜体*等）")
        print("3. 使用表情符号替代颜色标记")
        print("4. 对于复杂格式，使用卡片消息（lark_md）")
        print("5. 保持消息简洁，避免过度格式化")
        
        return all(success for _, success in results)


if __name__ == "__main__":
    tester = FeishuFormatTester()
    
    # 运行测试
    all_passed = tester.run_all_tests()
    
    # 退出码
    exit_code = 0 if all_passed else 1
    print(f"\n退出码: {exit_code}")
    exit(exit_code)