#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书消息格式转换器
将HTML格式转换为飞书兼容的格式
"""

import re
from typing import Dict, List, Optional, Tuple


class FeishuFormatter:
    """飞书消息格式转换器"""

    # 颜色到表情符号的映射
    COLOR_TO_EMOJI = {
        'green': '🟢',    # 绿色圆形
        'red': '🔴',      # 红色圆形
        'blue': '🔵',     # 蓝色圆形
        'orange': '🟡',   # 黄色圆形（替代橙色）
        'yellow': '🟡',   # 黄色圆形
        'gray': '⚪',     # 白色圆形（替代灰色）
        'grey': '⚪',      # 白色圆形（替代灰色）
    }

    # 指标到表情符号的映射
    METRIC_TO_EMOJI = {
        'revenue': '📈',      # 营收
        'profit': '💰',      # 利润
        'growth': '📊',      # 增长
        'warning': '⚠️',     # 警告
        'alert': '🚨',       # 警报
        'success': '✅',     # 成功
        'failure': '❌',     # 失败
        'observation': '🔍', # 观察
        'target': '🎯',      # 目标
        'hold': '📋',        # 持有
    }

    @staticmethod
    def convert_html_to_feishu(html_text: str) -> str:
        """
        将HTML格式转换为飞书兼容格式

        Args:
            html_text: 包含HTML标签的文本

        Returns:
            转换后的飞书兼容文本
        """
        if not html_text:
            return html_text

        # 保存原始文本用于调试
        original = html_text

        # 1. 处理<font color='color'>标签
        html_text = FeishuFormatter._convert_font_tags(html_text)

        # 2. 处理其他HTML标签
        html_text = FeishuFormatter._convert_other_html_tags(html_text)

        # 3. 清理多余的空白
        html_text = FeishuFormatter._cleanup_whitespace(html_text)

        # 记录转换（用于调试）
        if original != html_text:
            print(f"🔧 格式转换: {original[:50]}... → {html_text[:50]}...")

        return html_text

    @staticmethod
    def _convert_font_tags(text: str) -> str:
        """转换<font>标签"""
        # 匹配 <font color='color'>内容</font>
        pattern = r'<font\s+color\s*=\s*[\'"]([^\'"]+)[\'"]\s*>([^<]+)</font>'

        def replace_font(match):
            color = match.group(1).lower()
            content = match.group(2).strip()

            # 获取对应的表情符号
            emoji = FeishuFormatter.COLOR_TO_EMOJI.get(color, '')

            # 分析内容，添加适当的指标表情符号
            metric_emoji = ''
            if '📈' in content or '超预期' in content or '+' in content:
                metric_emoji = '📈'
            elif '📉' in content or '低于预期' in content or '亏损' in content:
                metric_emoji = '📉'
            elif '💰' in content or '利润' in content:
                metric_emoji = '💰'
            elif '⚠️' in content or '警告' in content or '风险' in content:
                metric_emoji = '⚠️'
            elif '🚨' in content or '警报' in content or '减仓' in content:
                metric_emoji = '🚨'
            elif '✅' in content or '成功' in content or '推荐' in content:
                metric_emoji = '✅'

            # 移除原内容中的表情符号（避免重复）
            content = content.replace('📈', '').replace('📉', '').replace('💰', '')
            content = content.replace('⚠️', '').replace('🚨', '').replace('✅', '')
            content = content.strip()

            # 构建新格式
            if emoji and metric_emoji:
                return f"{emoji}{metric_emoji} {content}"
            elif emoji:
                return f"{emoji} {content}"
            elif metric_emoji:
                return f"{metric_emoji} {content}"
            else:
                return content

        return re.sub(pattern, replace_font, text)

    @staticmethod
    def _convert_other_html_tags(text: str) -> str:
        """转换其他HTML标签"""
        # 移除所有HTML标签，但保留内容
        text = re.sub(r'<[^>]+>', '', text)

        # 转换常见的HTML实体
        html_entities = {
            '&lt;': '<',
            '&gt;': '>',
            '&amp;': '&',
            '&quot;': '"',
            '&#39;': "'",
            '&nbsp;': ' ',
        }

        for entity, char in html_entities.items():
            text = text.replace(entity, char)

        return text

    @staticmethod
    def _cleanup_whitespace(text: str) -> str:
        """清理多余的空白字符"""
        # 合并多个空白字符为单个空格
        text = re.sub(r'\s+', ' ', text)
        # 清理行首行尾空白
        text = text.strip()
        return text

    @staticmethod
    def format_percentage(value: float, use_emoji: bool = True) -> str:
        """
        格式化百分比，使用飞书兼容的格式

        Args:
            value: 百分比值（小数形式，如0.25表示25%）
            use_emoji: 是否使用表情符号

        Returns:
            格式化后的字符串
        """
        percentage = value * 100

        if use_emoji:
            if value >= 0.20:  # ≥20%
                return f"🟢📈 +{percentage:.1f}%"
            elif value <= -0.20:  # ≤-20%
                return f"🔴📉 {percentage:.1f}%"
            else:  # -20% < value < 20%
                return f"🔵📊 {percentage:+.1f}%"
        else:
            if value >= 0.20:  # ≥20%
                return f"📈 +{percentage:.1f}%"
            elif value <= -0.20:  # ≤-20%
                return f"📉 {percentage:.1f}%"
            else:  # -20% < value < 20%
                return f"📊 {percentage:+.1f}%"

    @staticmethod
    def get_trading_advice(surprise_ratio: float, use_emoji: bool = True) -> str:
        """
        根据超预期比例生成交易建议，使用飞书兼容格式

        Args:
            surprise_ratio: 超预期比例
            use_emoji: 是否使用表情符号

        Returns:
            交易建议字符串
        """
        if use_emoji:
            if surprise_ratio >= 0.30:  # ≥30%
                return "🟢✅🎯 强烈推荐加仓"
            elif surprise_ratio >= 0.20:  # ≥20%
                return "🟢✅ 考虑加仓"
            elif surprise_ratio >= 0.10:  # ≥10%
                return "🔵🔍 持有观察"
            elif surprise_ratio >= -0.10:  # -10% ~ 10%
                return "⚪📋 维持现状"
            elif surprise_ratio >= -0.20:  # -20% ~ -10%
                return "🟡⚠️ 关注风险"
            else:  # < -20%
                return "🔴🚨 考虑减仓"
        else:
            if surprise_ratio >= 0.30:  # ≥30%
                return "✅🎯 强烈推荐加仓"
            elif surprise_ratio >= 0.20:  # ≥20%
                return "✅ 考虑加仓"
            elif surprise_ratio >= 0.10:  # ≥10%
                return "🔍 持有观察"
            elif surprise_ratio >= -0.10:  # -10% ~ 10%
                return "📋 维持现状"
            elif surprise_ratio >= -0.20:  # -20% ~ -10%
                return "⚠️ 关注风险"
            else:  # < -20%
                return "🚨 考虑减仓"

    @staticmethod
    def create_markdown_section(title: str, content: str, level: int = 2) -> str:
        """
        创建Markdown格式的章节

        Args:
            title: 章节标题
            content: 章节内容
            level: 标题级别（1-3）

        Returns:
            Markdown格式的章节
        """
        if level == 1:
            header = f"# {title}"
        elif level == 2:
            header = f"## {title}"
        else:
            header = f"### {title}"

        return f"{header}\n\n{content}\n"

    @staticmethod
    def create_bullet_list(items: List[str], indent: int = 0) -> str:
        """
        创建Markdown无序列表

        Args:
            items: 列表项
            indent: 缩进级别（0-3）

        Returns:
            Markdown无序列表
        """
        indent_str = "  " * indent
        return "\n".join(f"{indent_str}- {item}" for item in items)

    @staticmethod
    def create_numbered_list(items: List[str], start: int = 1) -> str:
        """
        创建Markdown有序列表

        Args:
            items: 列表项
            start: 起始编号

        Returns:
            Markdown有序列表
        """
        return "\n".join(f"{start + i}. {item}" for i, item in enumerate(items))

    @staticmethod
    def create_card_payload(title: str, content: str, color: str = "blue") -> Dict:
        """
        创建飞书卡片消息的payload

        Args:
            title: 卡片标题
            content: 卡片内容（Markdown格式）
            color: 标题颜色（blue, green, red, orange, yellow, purple）

        Returns:
            卡片消息payload
        """
        return {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True
                },
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": title
                    },
                    "template": color
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": content
                        }
                    }
                ]
            }
        }


# 测试函数
def test_formatter():
    """测试格式转换器"""
    print("🧪 测试飞书格式转换器")
    print("=" * 60)

    formatter = FeishuFormatter()

    # 测试HTML转换
    test_cases = [
        ("<font color='green'>📈 +25.6%</font>", "🟢📈 +25.6%"),
        ("<font color='red'>📉 -18.2%</font>", "🔴📉 -18.2%"),
        ("<font color='blue'>📊 ±5.3%</font>", "🔵📊 ±5.3%"),
        ("<font color='orange'>⚠️ 关注风险</font>", "🟡⚠️ 关注风险"),
        ("<font color='green'>✅ 考虑加仓</font>", "🟢✅ 考虑加仓"),
        ("<font color='red'>🚨 考虑减仓</font>", "🔴🚨 考虑减仓"),
        ("<b>粗体文本</b>和<i>斜体文本</i>", "粗体文本和斜体文本"),
    ]

    print("📋 HTML转换测试:")
    for html, expected in test_cases:
        result = formatter.convert_html_to_feishu(html)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {html} → {result} (期望: {expected})")

    # 测试百分比格式化
    print("\n📊 百分比格式化测试:")
    test_values = [0.256, -0.182, 0.053, -0.053]
    for value in test_values:
        formatted = formatter.format_percentage(value)
        print(f"  {value:.3f} → {formatted}")

    # 测试交易建议
    print("\n💡 交易建议测试:")
    test_ratios = [0.35, 0.25, 0.15, 0.05, -0.05, -0.15, -0.25]
    for ratio in test_ratios:
        advice = formatter.get_trading_advice(ratio)
        print(f"  超预期{ratio*100:+.1f}% → {advice}")

    # 测试Markdown生成
    print("\n📝 Markdown生成测试:")
    section = formatter.create_markdown_section("测试章节", "这是章节内容")
    print(section)

    bullet_list = formatter.create_bullet_list(["项目1", "项目2", "项目3"])
    print("无序列表:")
    print(bullet_list)

    numbered_list = formatter.create_numbered_list(["第一步", "第二步", "第三步"])
    print("\n有序列表:")
    print(numbered_list)

    print("\n🎉 格式转换器测试完成！")


if __name__ == "__main__":
    test_formatter()
