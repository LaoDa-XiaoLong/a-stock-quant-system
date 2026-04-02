#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财报监控日报发送脚本 - 修复版
使用正确的数据库表名
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import sqlite3

# 导入飞书发送器
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from safe_feishu_sender import SafeFeishuSender
except ImportError:
    # 模拟发送器用于测试
    class SafeFeishuSender:
        def __init__(self, webhook_url):
            self.webhook_url = webhook_url

        def send_text(self, text):
            print(f"[模拟发送] 消息长度: {len(text)}字符")
            print(f"[模拟发送] 内容预览: {text[:100]}...")
            return True


class FinancialReportSenderFixed:
    """修复版财报报告发送器"""

    def __init__(self, webhook_url: str = None):
        # A股数据分析群webhook
        self.webhook_url = webhook_url or "https://open.feishu.cn/open-apis/bot/v2/hook/fb95ec56-6ad7-4830-99c7-0eaa287e67e7"
        self.sender = SafeFeishuSender(self.webhook_url)
        self.data_dir = 'data/final_financial_complete'
        self.db_path = f'{self.data_dir}/final_reports_complete.db'

        print(f"📊 修复版财报报告发送器初始化完成")
        print(f"📡 目标群组: A股数据分析群")

    def get_today_report_data(self) -> Dict:
        """获取今日的报告数据"""
        if not os.path.exists(self.db_path):
            print(f"❌ 数据库文件不存在: {self.db_path}")
            return None

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 获取今日日期
            today = datetime.now().strftime('%Y-%m-%d')

            # 获取监控摘要
            cursor.execute('''
            SELECT date, total_stocks, valid_stocks, holdings_surprises, all_surprises,
                   data_quality_score, report_content, trading_advice
            FROM final_monitor_complete
            WHERE date = ?
            ORDER BY date DESC
            LIMIT 1
            ''', (today,))

            row = cursor.fetchone()
            if not row:
                print(f"❌ 今日({today})无监控数据")
                # 尝试获取最近的数据
                cursor.execute('''
                SELECT date, total_stocks, valid_stocks, holdings_surprises, all_surprises,
                       data_quality_score, report_content, trading_advice
                FROM final_monitor_complete
                ORDER BY date DESC
                LIMIT 1
                ''')
                row = cursor.fetchone()
                if not row:
                    print("❌ 数据库中无任何监控数据")
                    conn.close()
                    return None

            # 获取详细的股票数据
            cursor.execute('''
            SELECT stock_code, stock_name, is_holding, industry, metric,
                   actual_value, expected_value, surprise_ratio,
                   alert_level, data_quality_score, trading_advice
            FROM final_surprises_complete
            WHERE date = ?
            ORDER BY surprise_ratio DESC
            ''', (row['date'],))

            stocks = []
            for stock_row in cursor.fetchall():
                stocks.append(dict(stock_row))

            conn.close()

            # 构建完整报告数据
            report = dict(row)
            report['stocks'] = stocks
            report['holdings'] = [s for s in stocks if s['is_holding']]

            print(f"✅ 获取到 {report['date']} 的报告数据")
            print(f"   - 总股票数: {report['total_stocks']}")
            print(f"   - 持仓股票: {len(report['holdings'])}")
            print(f"   - 超预期股票: {report['all_surprises']}")

            return report

        except Exception as e:
            print(f"❌ 获取报告数据失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _format_percentage(self, value: float) -> str:
        """格式化百分比，添加颜色标记"""
        if value >= 0.20:  # ≥20%
            return f"🟢📈 +{value*100:.1f}%"
        elif value <= -0.20:  # ≤-20%
            return f"🔴📉 {value*100:.1f}%"
        else:  # -20% < value < 20%
            return f"🔵📊 {value*100:+.1f}%"

    def _get_trading_advice(self, stock: Dict) -> str:
        """根据股票数据生成交易建议"""
        surprise_ratio = stock.get('surprise_ratio', 0)

        if surprise_ratio >= 0.30:  # ≥30%
            return "🟢✅ 强烈推荐加仓"
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

    def generate_core_summary(self, report: Dict) -> str:
        """生成核心摘要（第一层消息）"""
        if not report:
            return "暂无报告数据"

        today = report.get('date', datetime.now().strftime('%Y-%m-%d'))

        lines = []
        lines.append(f"📈 A股财报监控日报 ({today}) - 修复版")
        lines.append("=" * 50)

        # 核心摘要
        lines.append("🎯 **核心摘要**")
        lines.append(f"• **监控范围**: {report.get('total_stocks', 0)}只股票")
        lines.append(f"• **超预期事件**: {report.get('all_surprises', 0)}个")
        lines.append(f"• **持仓股票**: {len(report.get('holdings', []))}只")
        lines.append(f"• **持仓超预期**: {report.get('holdings_surprises', 0)}只")
        lines.append(f"• **数据质量**: {report.get('data_quality_score', 0):.1f}分")

        # 高优先级关注
        holdings = report.get('holdings', [])
        if holdings:
            lines.append("")
            lines.append("🚨 **高优先级关注**")

            # 按超预期幅度排序
            sorted_holdings = sorted(
                holdings,
                key=lambda x: x.get('surprise_ratio', 0),
                reverse=True
            )[:3]

            for i, stock in enumerate(sorted_holdings, 1):
                name = stock['stock_name']
                ratio = stock.get('surprise_ratio', 0) * 100
                metric = stock.get('metric', '')

                if ratio >= 20:
                    lines.append(f"{i}. **{name}**: {metric}+{ratio:.1f}% 📈")
                elif ratio >= 0:
                    lines.append(f"{i}. {name}: {metric}+{ratio:.1f}%")
                else:
                    lines.append(f"{i}. {name}: {metric}{ratio:.1f}% 📉")

        # 总体建议
        lines.append("")
        lines.append(f"💡 **总体建议**: {report.get('trading_advice', '暂无建议')}")

        # 生成时间
        lines.append("")
        lines.append(f"⏰ 生成时间: {datetime.now().strftime('%H:%M:%S')}")
        lines.append("👇 查看详细综合分析")

        return "\n".join(lines)

    def generate_detailed_analysis(self, report: Dict) -> str:
        """生成详细综合分析（第二层消息）"""
        if not report:
            return "暂无详细数据"

        today = report.get('date', datetime.now().strftime('%Y-%m-%d'))

        lines = []
        lines.append(f"# 📊 A股财报监控详细综合分析 ({today})")
        lines.append("")

        # 持仓股票综合分析
        holdings = report.get('holdings', [])
        if holdings:
            lines.append("## 🎯 持仓股票综合分析")
            lines.append(f"**持仓总数**: {len(holdings)}只")
            lines.append(f"**超预期持仓**: {report.get('holdings_surprises', 0)}只")
            lines.append("")

            for stock in holdings:
                # 股票标题
                lines.append(f"### **{stock['stock_name']} ({stock['stock_code']})**")

                # 关键指标
                actual = stock.get('actual_value', 0)
                expected = stock.get('expected_value', 0)
                ratio = stock.get('surprise_ratio', 0)

                # 格式化数值
                if actual >= 1e8:  # 亿级别
                    actual_fmt = f"{actual/1e8:.1f}亿"
                    expected_fmt = f"{expected/1e8:.1f}亿"
                elif actual >= 1e4:  # 万级别
                    actual_fmt = f"{actual/1e4:.1f}万"
                    expected_fmt = f"{expected/1e4:.1f}万"
                else:
                    actual_fmt = f"{actual:.0f}"
                    expected_fmt = f"{expected:.0f}"

                lines.append(f"- **{stock['metric']}**：`{actual_fmt}` vs 预期 `{expected_fmt}` **{self._format_percentage(ratio)}**")

                # 行业信息
                industry = stock.get('industry', '未知')
                lines.append(f"- **行业**：{industry}")

                # 数据质量
                quality = stock.get('data_quality_score', 100)
                if quality >= 90:
                    lines.append(f"- **数据质量**：✅ {quality:.0f}分")
                elif quality >= 80:
                    lines.append(f"- **数据质量**：⚠️ {quality:.0f}分")
                else:
                    lines.append(f"- **数据质量**：❌ {quality:.0f}分")

                # 操作建议
                advice = self._get_trading_advice(stock)
                lines.append(f"- **操作建议**：{advice}")
                lines.append("")  # 段落间隔

        # 市场整体分析
        lines.append("## 📈 市场整体分析")

        # 超预期分布
        lines.append("### 超预期分布")
        lines.append(f"- **总超预期事件**: {report.get('all_surprises', 0)}个")
        lines.append(f"- **持仓超预期**: {report.get('holdings_surprises', 0)}/{len(holdings)}只")

        # 数据质量说明
        lines.append("")
        lines.append("## 🔍 数据质量说明")
        lines.append(f"**质量阈值**: 75分")
        lines.append(f"**平均分数**: {report.get('data_quality_score', 0):.1f}分")
        lines.append("**验证项目**: 完整性、合理性、一致性、极端值")

        # 生成时间
        lines.append("")
        lines.append(f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        lines.append("*修复版 - 使用正确的数据库表结构*")

        return "\n".join(lines)

    def send_report(self):
        """发送报告（分层发送）"""
        print("🚀 开始发送修复版财报监控报告...")

        # 1. 获取报告数据
        report = self.get_today_report_data()
        if not report:
            print("❌ 无法获取报告数据，停止发送")
            return False

        print(f"✅ 获取到 {report.get('date', '今日')} 的报告数据")

        # 2. 生成并发送核心摘要
        print("📤 发送核心摘要（第一层）...")
        core_summary = self.generate_core_summary(report)

        # 发送核心摘要到飞书
        result1 = self.sender.send_safely(core_summary, message_type='text')
        success1 = result1.get('success', False)
        if not success1:
            print("❌ 核心摘要发送失败")
            return False

        print("✅ 核心摘要发送成功")

        # 3. 等待3秒，然后发送详细分析
        import time
        time.sleep(3)

        print("📤 发送详细综合分析（第二层）...")
        detailed_analysis = self.generate_detailed_analysis(report)

        # 发送详细分析到飞书
        result2 = self.sender.send_safely(detailed_analysis, message_type='text')
        success2 = result2.get('success', False)
        if not success2:
            print("❌ 详细分析发送失败")
            return False

        print("✅ 详细分析发送成功")

        # 4. 任务完成
        print("🎉 修复版财报监控报告发送完成！")
        print("=" * 60)
        print(f"📅 报告日期: {report.get('date', '未知')}")
        print(f"📊 分析股票: {report.get('total_stocks', 0)}只")
        print(f"🎯 持仓股票: {len(report.get('holdings', []))}只")
        print(f"📈 超预期事件: {report.get('all_surprises', 0)}个")
        print(f"🔍 数据质量: {report.get('data_quality_score', 0):.1f}分")
        print("=" * 60)

        return True

    def run(self):
        """运行发送任务"""
        try:
            print("=" * 60)
            print("📈 A股财报监控日报发送任务 - 修复版")
            print("=" * 60)

            success = self.send_report()

            if success:
                print("✅ 修复版任务执行成功")
                return True
            else:
                print("❌ 修复版任务执行失败")
                return False

        except Exception as e:
            print(f"❌ 任务执行异常: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    # 创建修复版发送器实例
    sender = FinancialReportSenderFixed()

    # 运行发送任务
    success = sender.run()

    # 退出码
    sys.exit(0 if success else 1)
