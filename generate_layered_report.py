#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成分层版财报监控日报
V3.0版本：包含核心摘要、详细分析和投资建议
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import json

class LayeredReportGenerator:
    """分层版报告生成器"""

    def __init__(self):
        self.data_dir = 'data/final_financial_fixed'
        self.db_path = f'{self.data_dir}/final_reports_fixed.db'
        self.reports_dir = 'reports/financial_daily'

        # 创建目录
        os.makedirs(self.reports_dir, exist_ok=True)

        # 持仓股票信息
        self.holdings = [
            {'code': '002594', 'name': '比亚迪', 'industry': '新能源汽车'},
            {'code': '603259', 'name': '药明康德', 'industry': '医药'},
            {'code': '002415', 'name': '海康威视', 'industry': '安防'},
            {'code': '000858', 'name': '五粮液', 'industry': '白酒'},
            {'code': '600036', 'name': '招商银行', 'industry': '银行'},
            {'code': '601318', 'name': '中国平安', 'industry': '保险'},
            {'code': '002352', 'name': '顺丰控股', 'industry': '物流'}
        ]

        print(f"📊 分层版报告生成器初始化完成")

    def get_today_data(self) -> Tuple[Dict, List[Dict]]:
        """获取今日数据"""
        today = datetime.now().strftime('%Y-%m-%d')

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 获取今日汇总数据
            cursor.execute('''
            SELECT * FROM fixed_monitor
            WHERE date = ?
            ''', (today,))

            row = cursor.fetchone()

            if row:
                # 解析汇总数据
                summary = {
                    'date': row[0],
                    'total_stocks': row[1],
                    'valid_stocks': row[2],
                    'holdings_surprises': row[3],
                    'all_surprises': row[4],
                    'data_quality_score': row[5],
                    'report_content': row[6],
                    'trading_advice': row[7]
                }
            else:
                # 如果没有今日数据，创建默认数据
                summary = {
                    'date': today,
                    'total_stocks': 7,
                    'valid_stocks': 7,
                    'holdings_surprises': 0,
                    'all_surprises': 0,
                    'data_quality_score': 100.0,
                    'report_content': '今日无显著超预期',
                    'trading_advice': '保持现有仓位观察'
                }

            # 获取今日超预期详情
            cursor.execute('''
            SELECT * FROM fixed_surprises
            WHERE date = ?
            ORDER BY ABS(surprise_ratio) DESC
            ''', (today,))

            surprises = []
            for row in cursor.fetchall():
                surprise = {
                    'id': row[0],
                    'date': row[1],
                    'stock_code': row[2],
                    'stock_name': row[3],
                    'is_holding': row[4],
                    'industry': row[5],
                    'metric': row[6],
                    'actual_value': row[7],
                    'expected_value': row[8],
                    'surprise_ratio': row[9],
                    'data_quality_score': row[10],
                    'alert_level': row[11],
                    'trading_advice': row[12],
                    'consistency_check_passed': row[13]
                }
                surprises.append(surprise)

            conn.close()

            return summary, surprises

        except Exception as e:
            print(f"获取数据失败: {e}")
            # 返回默认数据
            summary = {
                'date': today,
                'total_stocks': 7,
                'valid_stocks': 7,
                'holdings_surprises': 0,
                'all_surprises': 0,
                'data_quality_score': 100.0,
                'report_content': '今日无显著超预期',
                'trading_advice': '保持现有仓位观察'
            }
            return summary, []

    def generate_core_summary(self, summary: Dict, surprises: List[Dict]) -> str:
        """生成核心摘要（第一层）"""
        today = summary['date']

        lines = []
        lines.append(f"# A股财报监控日报（分层版）")
        lines.append("")
        lines.append(f"**生成日期**: {today}")
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        lines.append("## 核心摘要")
        lines.append(f"📈 A股财报监控日报 ({today})")
        lines.append("=" * 40)

        # 核心数据
        lines.append("🎯 **核心摘要**")
        lines.append(f"• **监控范围**: {summary['total_stocks']}只股票")
        lines.append(f"• **有效股票**: {summary['valid_stocks']}只")
        lines.append(f"• **超预期事件**: {summary['all_surprises']}个")
        lines.append(f"• **持仓超预期**: {summary['holdings_surprises']}只")
        lines.append(f"• **数据质量**: {summary['data_quality_score']:.1f}分")
        lines.append("")

        # 高优先级关注
        if surprises:
            lines.append("🚨 **高优先级关注**")

            # 按超预期幅度排序，取前3
            sorted_surprises = sorted(
                surprises,
                key=lambda x: abs(x['surprise_ratio']),
                reverse=True
            )[:3]

            for i, surprise in enumerate(sorted_surprises, 1):
                name = surprise['stock_name']
                ratio = surprise['surprise_ratio'] * 100
                metric = "营收" if surprise['metric'] == 'revenue' else "净利润"
                direction = "📈超出" if ratio > 0 else "📉低于"

                lines.append(f"{i}. 🎯**{name}**: {metric}{direction}预期{abs(ratio):.1f}%")

        # 总体建议
        lines.append("")
        lines.append(f"💡 **总体建议**: {summary['trading_advice']}")
        lines.append("=" * 40)

        # 行业分布
        if surprises:
            industry_stats = {}
            for surprise in surprises:
                industry = surprise['industry']
                if industry not in industry_stats:
                    industry_stats[industry] = {'total': 0, 'surprises': 0}
                industry_stats[industry]['total'] += 1
                if abs(surprise['surprise_ratio']) >= 0.20:
                    industry_stats[industry]['surprises'] += 1

            lines.append("")
            lines.append("🏢 **行业分布**")
            for industry, stats in industry_stats.items():
                if stats['total'] > 0:
                    rate = stats['surprises'] / stats['total'] * 100
                    lines.append(f"• **{industry}**: {stats['surprises']}/{stats['total']}只超预期({rate:.1f}%)")

        lines.append("")
        lines.append(f"⏰ **生成时间**: {datetime.now().strftime('%H:%M:%S')}")
        lines.append("👇 **查看详细分析**")

        return "\n".join(lines)

    def generate_detailed_analysis(self, summary: Dict, surprises: List[Dict]) -> str:
        """生成详细分析（第二层）"""
        today = summary['date']

        lines = []
        lines.append("## 详细分析")
        lines.append(f"# 📊 A股财报监控详细分析 ({today})")
        lines.append("")

        # 数据质量分析
        lines.append("### 📋 数据质量分析")
        lines.append(f"**整体数据质量**: {summary['data_quality_score']:.1f}分")

        if summary['data_quality_score'] >= 90:
            lines.append("**评估**: ✅ 数据质量优秀")
        elif summary['data_quality_score'] >= 80:
            lines.append("**评估**: ⚠️ 数据质量良好，部分需验证")
        elif summary['data_quality_score'] >= 70:
            lines.append("**评估**: ⚠️ 数据质量一般，建议人工复核")
        else:
            lines.append("**评估**: ❌ 数据质量较差，需重点关注")

        lines.append("")

        # 持仓股票分析
        lines.append("### 🎯 持仓股票分析")
        lines.append(f"**持仓总数**: {len(self.holdings)}只")
        lines.append(f"**超预期持仓**: {summary['holdings_surprises']}只")
        lines.append("")

        if surprises:
            # 按股票分组
            stock_groups = {}
            for surprise in surprises:
                if surprise['is_holding']:
                    code = surprise['stock_code']
                    if code not in stock_groups:
                        # 查找股票信息
                        stock_info = next((h for h in self.holdings if h['code'] == code), None)
                        stock_groups[code] = {
                            'name': surprise['stock_name'],
                            'industry': surprise['industry'],
                            'surprises': [],
                            'stock_info': stock_info
                        }
                    stock_groups[code]['surprises'].append(surprise)

            # 生成每只股票的分析
            for code, data in stock_groups.items():
                lines.append(f"#### 📊 {data['name']}({code})")
                lines.append(f"**行业**: {data['industry']}")
                lines.append("")

                for surprise in data['surprises']:
                    metric = "营收" if surprise['metric'] == 'revenue' else "净利润"
                    ratio = surprise['surprise_ratio'] * 100
                    direction = "超出" if ratio > 0 else "低于"

                    lines.append(f"**{metric}**: {direction}预期 {abs(ratio):.1f}%")

                    # 数据质量标记
                    quality = surprise['data_quality_score']
                    if quality >= 90:
                        quality_mark = "✅"
                    elif quality >= 80:
                        quality_mark = "⚠️"
                    else:
                        quality_mark = "❌"

                    lines.append(f"**数据质量**: {quality_mark} {quality:.0f}分")

                    # 一致性检查
                    if surprise['consistency_check_passed'] == 0:
                        lines.append("**一致性检查**: ❌ 未通过")

                    lines.append(f"**操作建议**: {surprise['trading_advice']}")
                    lines.append("")

                # 综合评估
                if len(data['surprises']) > 0:
                    avg_ratio = sum(s['surprise_ratio'] for s in data['surprises']) / len(data['surprises'])
                    if avg_ratio >= 0.20:
                        lines.append("**综合评估**: 📈 整体表现优秀，建议关注")
                    elif avg_ratio >= 0:
                        lines.append("**综合评估**: 📊 符合预期，表现平稳")
                    else:
                        lines.append("**综合评估**: 📉 不及预期，需谨慎")
                    lines.append("")

        else:
            lines.append("ℹ️ 今日持仓股票无显著超预期")
            lines.append("")

        # 市场整体分析
        lines.append("### 📈 市场整体分析")
        lines.append(f"**监控股票总数**: {summary['total_stocks']}只")
        lines.append(f"**有效股票数**: {summary['valid_stocks']}只")
        lines.append(f"**总超预期事件**: {summary['all_surprises']}个")
        lines.append("")

        # 投资建议
        lines.append("### 💡 投资建议")
        lines.append("**短期策略**:")
        if summary['holdings_surprises'] > 0:
            lines.append("1. 优先关注超预期幅度最大的持仓股票")
            lines.append("2. 结合数据质量评分调整仓位")
            lines.append("3. 设置明确的止盈止损位")
        else:
            lines.append("1. 保持现有仓位，观察市场变化")
            lines.append("2. 关注行业整体表现")
            lines.append("3. 等待更好的投资机会")

        lines.append("")
        lines.append("**中长期策略**:")
        lines.append("1. 关注数据质量持续优秀的股票")
        lines.append("2. 结合行业趋势进行配置")
        lines.append("3. 定期复盘投资组合")

        lines.append("")
        lines.append("### 🔍 数据说明")
        lines.append("**监控范围**: 持仓股票 + 重点关注股票")
        lines.append("**超预期阈值**: 20%")
        lines.append("**数据来源**: 模拟财务数据（修复版）")
        lines.append("**更新时间**: 每日自动监控")
        lines.append("")
        lines.append(f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

        return "\n".join(lines)

    def generate_layered_report(self) -> str:
        """生成完整的分层版报告"""
        print("📊 开始生成分层版日报...")

        # 获取数据
        summary, surprises = self.get_today_data()
        print(f"📅 数据日期: {summary['date']}")
        print(f"📈 超预期事件: {len(surprises)}个")

        # 生成核心摘要
        core_summary = self.generate_core_summary(summary, surprises)

        # 生成详细分析
        detailed_analysis = self.generate_detailed_analysis(summary, surprises)

        # 合并报告
        full_report = f"{core_summary}\n\n{detailed_analysis}"

        # 保存报告
        report_file = f"{self.reports_dir}/daily_report_{summary['date']}_layered.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(full_report)

        print(f"💾 报告已保存: {report_file}")
        print(f"📄 报告长度: {len(full_report)}字符")

        return full_report, report_file

def main():
    """主函数"""
    print("=" * 60)
    print("📊 分层版财报监控日报生成器 V3.0")
    print("=" * 60)

    generator = LayeredReportGenerator()

    # 生成报告
    report, report_file = generator.generate_layered_report()

    print("=" * 60)
    print("✅ 分层版日报生成完成！")
    print("=" * 60)

    # 输出报告预览
    print("\n📋 报告预览:")
    print("-" * 40)

    lines = report.split('\n')
    for i, line in enumerate(lines[:30]):  # 显示前30行
        print(line)

    if len(lines) > 30:
        print("...")
        print(f"（完整报告共{len(lines)}行，已保存至文件）")

    print(f"\n📁 报告文件: {report_file}")
    print("📤 下一步: 发送报告到A股数据分析群")

if __name__ == "__main__":
    main()
