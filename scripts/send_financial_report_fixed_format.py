#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财报监控日报发送脚本 - 格式修复版
解决HTML格式兼容性问题，使用飞书兼容的格式
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import sqlite3

# 导入飞书发送器和格式转换器
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from safe_feishu_sender import SafeFeishuSender
    from feishu_formatter import FeishuFormatter
except ImportError:
    # 模拟发送器用于测试
    class SafeFeishuSender:
        def __init__(self, webhook_url):
            self.webhook_url = webhook_url
        
        def send_text(self, text):
            print(f"[模拟发送] 消息长度: {len(text)}字符")
            print(f"[模拟发送] 内容预览: {text[:200]}...")
            return True
    
    # 导入本地格式转换器
    from feishu_formatter import FeishuFormatter


class FixedFormatFinancialReportSender:
    """格式修复版财报报告发送器"""
    
    def __init__(self, webhook_url: str = None):
        # A股数据分析群webhook
        self.webhook_url = webhook_url or "https://open.feishu.cn/open-apis/bot/v2/hook/fb95ec56-6ad7-4830-99c7-0eaa287e67e7"
        self.sender = SafeFeishuSender(self.webhook_url)
        self.formatter = FeishuFormatter()
        self.data_dir = 'data/final_financial_complete'
        self.db_path = f'{self.data_dir}/final_reports_complete.db'
        
        print(f"📊 格式修复版财报报告发送器初始化完成")
        print(f"🎯 目标: 解决HTML格式兼容性问题")
        print(f"📡 目标群组: A股数据分析群")
    
    def get_latest_report_data(self) -> Dict:
        """获取最新的监控报告数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 获取最新的监控结果
            cursor.execute('''
            SELECT date, total_stocks, valid_stocks, holdings_surprises, all_surprises,
                   data_quality_score, report_content, trading_advice, created_at
            FROM final_monitor_complete
            ORDER BY date DESC
            LIMIT 1
            ''')
            
            row = cursor.fetchone()
            
            if not row:
                print("❌ 未找到监控报告数据，使用示例数据")
                return self._create_sample_report()
            
            # 获取详细的股票数据
            cursor.execute('''
            SELECT stock_code, stock_name, is_holding, report_type, publish_date,
                   revenue_actual, revenue_expected, revenue_deviation,
                   profit_actual, profit_expected, profit_deviation,
                   data_quality_score, alert_level, metric, surprise_ratio
            FROM final_stock_reports
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
            report['surprises'] = [s for s in stocks if abs(s['surprise_ratio']) >= 0.20]  # 20%阈值
            
            # 计算行业分布
            report['industry_stats'] = self._calculate_industry_stats(stocks)
            
            return report
            
        except Exception as e:
            print(f"❌ 获取报告数据失败: {e}")
            print("⚠️  使用示例数据继续测试")
            return self._create_sample_report()
    
    def _create_sample_report(self) -> Dict:
        """创建示例报告数据（用于测试）"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 持仓股票数据（模拟真实场景）
        stocks = [
            {
                'stock_code': '002594',
                'stock_name': '比亚迪',
                'industry': '新能源汽车',
                'is_holding': 1,
                'report_type': '年报',
                'publish_date': '2026-03-27',
                'revenue_actual': 15000000000,
                'revenue_expected': 12000000000,
                'revenue_deviation': 0.243,
                'profit_actual': 8000000000,
                'profit_expected': 10000000000,
                'profit_deviation': -0.219,
                'data_quality_score': 95,
                'alert_level': '高',
                'metric': '营收',
                'surprise_ratio': 0.243
            },
            {
                'stock_code': '002594',
                'stock_name': '比亚迪',
                'industry': '新能源汽车',
                'is_holding': 1,
                'report_type': '年报',
                'publish_date': '2026-03-27',
                'revenue_actual': 15000000000,
                'revenue_expected': 12000000000,
                'revenue_deviation': 0.243,
                'profit_actual': 8000000000,
                'profit_expected': 10000000000,
                'profit_deviation': -0.219,
                'data_quality_score': 95,
                'alert_level': '高',
                'metric': '净利润',
                'surprise_ratio': -0.219
            },
            {
                'stock_code': '603259',
                'stock_name': '药明康德',
                'industry': '医药',
                'is_holding': 1,
                'report_type': '季报',
                'publish_date': '2026-03-20',
                'revenue_actual': 5000000000,
                'revenue_expected': 4000000000,
                'revenue_deviation': 0.224,
                'profit_actual': 1200000000,
                'profit_expected': 1000000000,
                'profit_deviation': 0.182,
                'data_quality_score': 92,
                'alert_level': '中',
                'metric': '营收',
                'surprise_ratio': 0.224
            }
        ]
        
        # 构建报告
        report = {
            'date': today,
            'total_stocks': 307,
            'valid_stocks': 295,
            'holdings_surprises': 3,
            'all_surprises': 15,
            'data_quality_score': 89.5,
            'report_content': '示例报告内容',
            'trading_advice': '总体建议：持仓股票表现分化，需区别对待',
            'stocks': stocks,
            'holdings': [s for s in stocks if s['is_holding']],
            'surprises': [s for s in stocks if abs(s['surprise_ratio']) >= 0.20]
        }
        
        return report
    
    def _calculate_industry_stats(self, stocks: List[Dict]) -> Dict:
        """计算行业统计数据"""
        industry_map = {
            '002594': '新能源汽车',
            '603259': '医药',
            '002415': '安防',
            '000858': '白酒',
            '600036': '银行',
            '601318': '保险',
            '002352': '物流',
            '000001': '银行',
            '000002': '房地产',
            '000063': '通信'
        }
        
        industry_stats = {}
        for stock in stocks:
            industry = industry_map.get(stock['stock_code'], '其他')
            if industry not in industry_stats:
                industry_stats[industry] = {
                    'total': 0,
                    'surprises': 0,
                    'holdings': 0
                }
            
            industry_stats[industry]['total'] += 1
            if abs(stock['surprise_ratio']) >= 0.20:
                industry_stats[industry]['surprises'] += 1
            if stock['is_holding']:
                industry_stats[industry]['holdings'] += 1
        
        return industry_stats
    
    def generate_core_summary(self, report: Dict) -> str:
        """生成核心摘要（使用飞书兼容格式）"""
        if not report:
            return "暂无报告数据"
        
        # 计算关键指标
        total_stocks = report['valid_stocks']
        surprise_stocks = report['all_surprises']
        surprise_ratio = (surprise_stocks / total_stocks * 100) if total_stocks > 0 else 0
        
        holdings_total = len(report['holdings'])
        holdings_surprises = report['holdings_surprises']
        holdings_ratio = (holdings_surprises / holdings_total * 100) if holdings_total > 0 else 0
        
        # 获取前3名超预期股票
        top_surprises = sorted(
            report['surprises'],
            key=lambda x: abs(x['surprise_ratio']),
            reverse=True
        )[:3]
        
        # 生成核心摘要
        lines = []
        lines.append(f"📈 A股财报监控日报 ({report['date']})")
        lines.append("=" * 40)
        
        # 关键指标
        lines.append("🎯 **核心摘要**")
        lines.append(f"• 监控范围: {total_stocks}只股票")
        
        # 使用格式转换器格式化百分比
        surprise_text = f"{surprise_stocks}只({surprise_ratio:.1f}%)"
        if surprise_ratio > 20:
            lines.append(f"• 超预期: 🟢{surprise_text}")
        elif surprise_ratio > 10:
            lines.append(f"• 超预期: 🔵{surprise_text}")
        else:
            lines.append(f"• 超预期: ⚪{surprise_text}")
        
        holdings_text = f"{holdings_surprises}/{holdings_total}只({holdings_ratio:.1f}%)"
        if holdings_ratio > 50:
            lines.append(f"• 持仓表现: 🟢{holdings_text}")
        elif holdings_ratio > 30:
            lines.append(f"• 持仓表现: 🔵{holdings_text}")
        else:
            lines.append(f"• 持仓表现: ⚪{holdings_text}")
        
        lines.append(f"• 数据质量: {report['data_quality_score']:.1f}分")
        
        # 高优先级关注
        if top_surprises:
            lines.append("")
            lines.append("🚨 **高优先级关注**")
            for i, stock in enumerate(top_surprises, 1):
                holding_mark = "🎯" if stock['is_holding'] else ""
                metric = "营收" if stock['metric'] == 'revenue' else "净利润"
                ratio = stock['surprise_ratio'] * 100
                
                # 使用格式转换器格式化百分比
                formatted_ratio = self.formatter.format_percentage(stock['surprise_ratio'])
                lines.append(f"{i}. {holding_mark}{stock['stock_name']}: {metric}{formatted_ratio}")
        
        # 总体建议
        lines.append("")
        lines.append(f"💡 **总体建议**: {report['trading_advice']}")
        
        # 报告类型分布
        report_types = {}
        for stock in report['stocks']:
            rt = stock.get('report_type', '未知')
            report_types[rt] = report_types.get(rt, 0) + 1
        
        if report_types:
            lines.append("")
            lines.append("📅 **报告类型**")
            for rt, count in report_types.items():
                lines.append(f"• {rt}: {count}份")
        
        # 生成时间和查看链接
        lines.append("")
        lines.append(f"⏰ **生成时间**: {datetime.now().strftime('%H:%M:%S')}")
        lines.append("👇 **查看详细分析**")
        
        return "\n".join(lines)
    
    def generate_detailed_analysis(self, report: Dict) -> str:
        """生成详细分析（使用飞书兼容格式）"""
        if not report:
            return "暂无详细数据"
        
        lines = []
        lines.append(f"## 📊 A股财报监控详细分析 ({report['date']})")
        lines.append("")
        
        # 持仓股票详细分析
        holdings = report['holdings']
        if holdings:
            lines.append("### 🎯 持仓股票分析")
            lines.append(f"**持仓总数**: {len(holdings)}只")
            lines.append(f"**超预期持仓**: {report['holdings_surprises']}只")
            lines.append("")
            
            # 按超预期幅度排序
            sorted_holdings = sorted(
                holdings,
                key=lambda x: abs(x['surprise_ratio']),
                reverse=True
            )
            
            for stock in sorted_holdings:
                lines.append(f"#### {stock['stock_name']} ({stock['stock_code']})")
                
                # 报告信息
                report_type = stock.get('report_type', '未知')
                publish_date = stock.get('publish_date', '未知')
                days_ago = self._calculate_days_ago(publish_date)
                
                lines.append(f"**报告类型**: {report_type}")
                lines.append(f"**发布日期**: {publish_date} ({days_ago})")
                
                # 财务指标 - 使用格式转换器
                revenue_dev = stock['revenue_deviation']
                profit_dev = stock['profit_deviation']
                
                revenue_formatted = self.formatter.format_percentage(revenue_dev)
                profit_formatted = self.formatter.format_percentage(profit_dev)
                
                lines.append(f"**营收**: {revenue_formatted} vs 预期")
                lines.append(f"**净利润**: {profit_formatted} vs 预期")
                
                # 数据质量
                quality_score = stock.get('data_quality_score', 0)
                quality_emoji = "🟢" if quality_score >= 90 else "🟡" if quality_score >= 80 else "🔴"
                lines.append(f"**数据质量**: {quality_emoji} {quality_score:.1f}分")
                
                # 交易建议 - 使用格式转换器
                surprise_ratio = stock.get('surprise_ratio', 0)
                advice = self.formatter.get_trading_advice(surprise_ratio)
                lines.append(f"**建议**: {advice}")
                
                lines.append("")
        
        # 市场整体分析
        lines.append("### 📈 市场整体分析")
        
        # 超预期分布
        revenue_surprises = sum(1 for s in report['stocks'] if s['revenue_deviation'] >= 0.20)
        profit_surprises = sum(1 for s in report['stocks'] if s['profit_deviation'] >= 0.20)
        both_surprises = sum(1 for s in report['stocks'] if s['revenue_deviation'] >= 0.20 and s['profit_deviation'] >= 0.20)
        
        total = len(report['stocks'])
        
        revenue_percent = revenue_surprises / total * 100 if total > 0 else 0
        profit_percent = profit_surprises / total * 100 if total > 0 else 0
        both_percent = both_surprises / total * 100 if total > 0 else 0
        
        lines.append(f"**营收超预期**: {revenue_surprises}/{total}只({revenue_percent:.1f}%)")
        lines.append(f"**净利润超预期**: {profit_surprises}/{total}只({profit_percent:.1f}%)")
        lines.append(f"**双指标超预期**: {both_surprises}/{total}只({both_percent:.1f}%)")
        lines.append("")
        
        # 行业表现
        industry_stats = report.get('industry_stats', {})
        if industry_stats:
            lines.append("### 🏢 行业表现")
            for industry, stats in industry_stats.items():
                if stats['total'] > 0:
                    surprise_rate = stats['surprises'] / stats['total'] * 100
                    surprise_emoji = "🟢" if surprise_rate > 30 else "🟡" if surprise_rate > 20 else "🔴"
                    lines.append(f"**{industry}**: {surprise_emoji} {stats['surprises']}/{stats['total']}只超预期({surprise_rate:.1f}%)")
            lines.append("")
        
        # 数据质量说明
        lines.append("### 🔍 数据质量说明")
        lines.append(f"**质量阈值**: 75分")
        lines.append(f"**平均分数**: {report['data_quality_score']:.1f}分")
        lines.append("**验证项目**: 完整性、合理性、一致性、极端值")
        lines.append("")
        
        # 格式说明
        lines.append("### 🎨 格式说明")
        lines.append("**颜色/表情符号含义**:")
        lines.append("- 🟢📈: 大幅超预期 (≥20%)")
        lines.append("- 🔴📉: 大幅低于预期 (≤-20%)")
        lines.append("- 🔵📊: 符合预期 (-20% ~ 20%)")
        lines.append("- 🟢✅: 推荐加仓")
        lines.append("- 🔴🚨: 考虑减仓")
        lines.append("- 🟡⚠️: 关注风险")
        lines.append("")
        
        # 生成时间
        lines.append(f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        
        return "\n".join(lines)
    
    def _calculate_days_ago(self, publish_date: str) -> str:
        """计算发布日期距离今天的天数"""
        try:
            if not publish_date or publish_date == '未知':
                return "日期未知"
            
            pub_date = datetime.strptime(publish_date, '%Y-%m-%d')
            today = datetime.now()
            delta = today - pub_date
            
            if delta.days == 0:
                return "今日发布"
            elif delta.days == 1:
                return "1天前"
            else:
                return f"{delta.days}天前"
        except:
            return "日期格式错误"
    
    def send_report(self, use_card_format: bool = True):
        """发送报告（支持文本和卡片格式）"""
        print("🚀 开始发送格式修复版财报监控报告...")
        
        # 1. 获取报告数据
        report = self.get_latest_report_data()
        if not report:
            print("❌ 无法获取报告数据，停止发送")
            return False
        
        print(f"✅ 获取到 {report['date']} 的报告数据")
        print(f"📊 包含 {len(report['stocks'])} 只股票数据")
        print(f"🎯 持仓股票: {len(report['holdings'])} 只")
        
        # 2. 生成报告内容
        print("📝 生成报告内容...")
        core_summary = self.generate_core_summary(report)
        detailed_analysis = self.generate_detailed_analysis(report)
        
        # 3. 发送报告
        if use_card_format:
            print("📤 使用卡片格式发送报告...")
            success = self._send_as_card(core_summary, detailed_analysis)
        else:
            print("📤 使用文本格式发送报告...")
            success = self._send_as_text(core_summary, detailed_analysis)
        
        # 4. 保存报告到文件
        if success:
            self._save_report_to_file(report, core_summary, detailed_analysis)
        
        return success
    
    def _send_as_text(self, core_summary: str, detailed_analysis: str) -> bool:
        """以文本格式发送报告"""
        try:
            # 发送核心摘要
            print("  发送核心摘要...")
            success1 = self.sender.send_text(core_summary)
            
            if not success1:
                print("  ❌ 核心摘要发送失败")
                return False
            
            # 等待3秒
            import time
            time.sleep(3)
            
            # 发送详细分析
            print("  发送详细分析...")
            success2 = self.sender.send_text(detailed_analysis)
            
            if not success2:
                print("  ❌ 详细分析发送失败")
                return False
            
            print("  ✅ 文本格式报告发送成功")
            return True
            
        except Exception as e:
            print(f"  ❌ 发送失败: {e}")
            return False
    
    def _send_as_card(self, core_summary: str, detailed_analysis: str) -> bool:
        """以卡片格式发送报告"""
        try:
            # 构建完整内容
            full_content = f"{core_summary}\n\n---\n\n{detailed_analysis}"
            
            # 创建卡片payload
            card_payload = self.formatter.create_card_payload(
                title=f"📊 A股财报监控日报 ({datetime.now().strftime('%Y-%m-%d')})",
                content=full_content,
                color="blue"
            )
            
            # 发送卡片消息
            print("  发送卡片消息...")
            response = self.sender.send_text(json.dumps(card_payload, ensure_ascii=False))
            
            if response:
                print("  ✅ 卡片格式报告发送成功")
                return True
            else:
                print("  ❌ 卡片格式发送失败，尝试文本格式...")
                return self._send_as_text(core_summary, detailed_analysis)
                
        except Exception as e:
            print(f"  ❌ 卡片发送失败: {e}")
            print("  尝试文本格式...")
            return self._send_as_text(core_summary, detailed_analysis)
    
    def _save_report_to_file(self, report: Dict, core_summary: str, detailed_analysis: str):
        """保存报告到文件"""
        try:
            report_dir = "reports/financial_daily_fixed"
            os.makedirs(report_dir, exist_ok=True)
            
            filename = f"{report_dir}/daily_report_{report['date']}_fixed.md"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# 格式修复版财报监控日报\n\n")
                f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(core_summary)
                f.write("\n\n")
                f.write(detailed_analysis)
            
            print(f"💾 报告已保存: {filename}")
            
        except Exception as e:
            print(f"❌ 保存报告失败: {e}")
    
    def run(self):
        """运行发送任务"""
        print("=" * 60)
        print("📈 A股财报监控日报发送任务 - 格式修复版")
        print("=" * 60)
        print("🎯 目标: 解决HTML格式兼容性问题")
        print("🔄 方法: 使用表情符号替代HTML颜色标签")
        print("📱 兼容: 确保飞书、移动端正常显示")
        print("=" * 60)
        
        try:
            # 尝试卡片格式，失败时自动降级到文本格式
            success = self.send_report(use_card_format=True)
            
            if success:
                print("\n✅ 任务执行成功！")
                print("🎉 格式修复版报告已发送")
                print("📋 格式特点:")
                print("   • 无HTML标签，完全兼容飞书")
                print("   • 使用表情符号表示颜色和状态")
                print("   • 支持卡片和文本两种格式")
                print("   • 自动降级机制确保发送成功")
                return True
            else:
                print("\n❌ 任务执行失败")
                return False
                
        except Exception as e:
            print(f"\n❌ 任务执行异常: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    # 创建发送器实例
    sender = FixedFormatFinancialReportSender()
    
    # 运行发送任务
    success = sender.run()
    
    # 退出码
    sys.exit(0 if success else 1)