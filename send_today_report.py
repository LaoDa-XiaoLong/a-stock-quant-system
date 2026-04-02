#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发送今日财报监控日报到A股数据分析群
简化版本，直接发送分层版报告
"""

import os
import sys
from datetime import datetime

# 导入飞书发送器
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from scripts.safe_feishu_sender import SafeFeishuSender
    print("✅ 导入飞书发送器成功")
except ImportError:
    # 模拟发送器用于测试
    print("⚠️  使用模拟发送器")
    class SafeFeishuSender:
        def __init__(self, webhook_url):
            self.webhook_url = webhook_url

        def send_text(self, text):
            print(f"[模拟发送] 消息长度: {len(text)}字符")
            print(f"[模拟发送] 内容预览: {text[:200]}...")
            return True

        def send_markdown(self, title, content):
            print(f"[模拟发送Markdown] 标题: {title}")
            print(f"[模拟发送Markdown] 内容长度: {len(content)}字符")
            print(f"[模拟发送Markdown] 内容预览: {content[:200]}...")
            return True


class TodayReportSender:
    """今日报告发送器"""

    def __init__(self):
        # A股数据分析群webhook
        self.webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/fb95ec56-6ad7-4830-99c7-0eaa287e67e7"
        self.sender = SafeFeishuSender(self.webhook_url)

        # 报告文件路径
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.report_file = f"reports/financial_daily/daily_report_{self.today}_layered.md"

        print(f"📤 今日报告发送器初始化完成")
        print(f"📅 报告日期: {self.today}")
        print(f"📁 报告文件: {self.report_file}")

    def load_report(self) -> str:
        """加载报告内容"""
        if not os.path.exists(self.report_file):
            print(f"❌ 报告文件不存在: {self.report_file}")
            return None

        try:
            with open(self.report_file, 'r', encoding='utf-8') as f:
                content = f.read()

            print(f"✅ 加载报告成功: {len(content)}字符")
            return content
        except Exception as e:
            print(f"❌ 加载报告失败: {e}")
            return None

    def split_report_for_feishu(self, report_content: str) -> tuple:
        """将报告分割为适合飞书发送的部分"""
        if not report_content:
            return None, None

        # 查找核心摘要和详细分析的分隔点
        lines = report_content.split('\n')

        # 查找核心摘要结束位置（在"👇 **查看详细分析**"之前）
        core_end = 0
        for i, line in enumerate(lines):
            if "👇 **查看详细分析**" in line:
                core_end = i + 1
                break

        if core_end == 0:
            # 如果没有找到分隔点，使用前20行作为核心摘要
            core_end = min(20, len(lines))

        core_summary = '\n'.join(lines[:core_end])
        detailed_analysis = '\n'.join(lines[core_end:])

        print(f"📋 核心摘要: {len(core_summary)}字符")
        print(f"📋 详细分析: {len(detailed_analysis)}字符")

        return core_summary, detailed_analysis

    def send_core_summary(self, core_summary: str) -> bool:
        """发送核心摘要（第一层消息）"""
        if not core_summary:
            print("❌ 核心摘要为空")
            return False

        # 构建消息内容
        message = f"📈 A股财报监控日报 ({self.today}) - 核心摘要\n\n{core_summary}"

        print(f"📤 准备发送核心摘要...")
        print(f"📏 内容长度: {len(message)}字符")

        # 发送消息
        try:
            result = self.sender.send_safely(message, message_type='text')
            success = result.get('success', False)

            if success:
                print("✅ 核心摘要发送成功")
            else:
                print(f"❌ 核心摘要发送失败: {result.get('error', '未知错误')}")

            return success
        except Exception as e:
            print(f"❌ 发送核心摘要时发生异常: {e}")
            return False

    def send_detailed_analysis(self, detailed_analysis: str) -> bool:
        """发送详细分析（第二层消息）"""
        if not detailed_analysis:
            print("❌ 详细分析为空")
            return False

        # 构建消息内容
        message = f"📊 A股财报监控详细分析 ({self.today})\n\n{detailed_analysis}"

        print(f"📤 准备发送详细分析...")
        print(f"📏 内容长度: {len(message)}字符")

        # 发送消息
        try:
            result = self.sender.send_safely(message, message_type='text')
            success = result.get('success', False)

            if success:
                print("✅ 详细分析发送成功")
            else:
                print(f"❌ 详细分析发送失败: {result.get('error', '未知错误')}")

            return success
        except Exception as e:
            print(f"❌ 发送详细分析时发生异常: {e}")
            return False

    def send_full_report(self) -> bool:
        """发送完整报告"""
        print("=" * 60)
        print(f"📤 开始发送今日财报监控日报 ({self.today})")
        print("=" * 60)

        # 加载报告
        report_content = self.load_report()
        if not report_content:
            return False

        # 分割报告
        core_summary, detailed_analysis = self.split_report_for_feishu(report_content)

        if not core_summary:
            print("❌ 无法提取核心摘要")
            return False

        # 发送核心摘要
        print("\n1️⃣ 发送核心摘要...")
        success1 = self.send_core_summary(core_summary)

        # 等待一下
        import time
        time.sleep(2)

        # 发送详细分析
        print("\n2️⃣ 发送详细分析...")
        success2 = self.send_detailed_analysis(detailed_analysis)

        # 汇总结果
        print("\n" + "=" * 60)
        print("📊 发送结果汇总")
        print("=" * 60)
        print(f"✅ 核心摘要: {'成功' if success1 else '失败'}")
        print(f"✅ 详细分析: {'成功' if success2 else '失败'}")

        overall_success = success1 and success2
        if overall_success:
            print("🎉 完整报告发送成功！")
        else:
            print("⚠️  报告发送部分成功或失败")

        return overall_success


def main():
    """主函数"""
    print("=" * 60)
    print("📤 财报监控日报发送工具")
    print("=" * 60)
    print(f"🎯 目标: A股数据分析群")
    print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    sender = TodayReportSender()

    # 发送报告
    success = sender.send_full_report()

    print("=" * 60)
    if success:
        print("✅ 发送任务完成！")
    else:
        print("❌ 发送任务失败")
    print("=" * 60)

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
