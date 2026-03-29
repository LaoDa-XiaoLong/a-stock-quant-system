#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财报监控日报发送脚本 - 优化版
基于新版模板设计，避免信息截断，提升阅读体验
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import sqlite3

# 导入飞书发送器
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from safe_feishu_sender import SafeFeishuSender


class OptimizedFinancialReportSender:
    """优化版财报报告发送器"""
    
    def __init__(self, webhook_url: str = None):
        # A股数据分析群webhook
        self.webhook_url = webhook_url or "https://open.feishu.cn/open-apis/bot/v2/hook/fb95ec56-6ad7-4830-99c7-0eaa287e67e7"
        self.sender = SafeFeishuSender(self.webhook_url)
        self.data_dir = 'data/final_financial_complete'
        self.db_path = f'{self.data_dir}/final_reports_complete.db'
        
        print(f"📊 优化版财报报告发送器初始化完成")
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
                print("❌ 未找到监控报告数据")
                return None
            
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
            return None
    
    def _calculate_industry_stats(self, stocks: List[Dict]) -> Dict:
        """计算行业统计数据"""
        # 简化的行业映射（实际应根据股票代码映射到具体行业）
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
        """生成核心摘要（第一层消息）"""
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
        lines.append("🎯 核心摘要")
        lines.append(f"• 监控范围: {total_stocks}只股票")
        lines.append(f"• 超预期: {surprise_stocks}只({surprise_ratio:.1f}%)")
        lines.append(f"• 持仓表现: {holdings_surprises}/{holdings_total}只超预期({holdings_ratio:.1f}%)")
        lines.append(f"• 数据质量: {report['data_quality_score']:.1f}分")
        
        # 高优先级关注
        if top_surprises:
            lines.append("")
            lines.append("🚨 高优先级关注")
            for i, stock in enumerate(top_surprises, 1):
                holding_mark = "🎯" if stock['is_holding'] else ""
                metric = stock['metric']
                ratio = stock['surprise_ratio'] * 100
                lines.append(f"{i}. {holding_mark}{stock['stock_name']}: {metric}+{ratio:.1f}%")
        
        # 总体建议
        lines.append("")
        lines.append(f"💡 总体建议: {report['trading_advice']}")
        
        # 报告类型分布
        report_types = {}
        for stock in report['stocks']:
            rt = stock.get('report_type', '未知')
            report_types[rt] = report_types.get(rt, 0) + 1
        
        if report_types:
            lines.append("")
            lines.append("📅 报告类型")
            for rt, count in report_types.items():
                lines.append(f"• {rt}: {count}份")
        
        # 生成时间和查看链接
        lines.append("")
        lines.append(f"⏰ 生成时间: {datetime.now().strftime('%H:%M:%S')}")
        lines.append("👇 查看详细分析")
        
        return "\n".join(lines)
    
    def generate_detailed_analysis(self, report: Dict) -> str:
        """生成详细分析（第二层消息或附件）"""
        if not report:
            return "暂无详细数据"
        
        lines = []
        lines.append(f"# 📊 A股财报监控详细分析 ({report['date']})")
        lines.append("")
        
        # 持仓股票详细分析
        holdings = report['holdings']
        if holdings:
            lines.append("## 🎯 持仓股票分析")
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
                lines.append(f"### {stock['stock_name']} ({stock['stock_code']})")
                
                # 报告信息
                report_type = stock.get('report_type', '未知')
                publish_date = stock.get('publish_date', '未知')
                days_ago = self._calculate_days_ago(publish_date)
                
                lines.append(f"**报告类型**: {report_type}")
                lines.append(f"**发布日期**: {publish_date} ({days_ago})")
                
                # 财务指标
                revenue_dev = stock['revenue_deviation'] * 100
                profit_dev = stock['profit_deviation'] * 100
                
                lines.append(f"**营收**: {revenue_dev:+.1f}% vs 预期")
                lines.append(f"**净利润**: {profit_dev:+.1f}% vs 预期")
                
                # 交易建议
                if revenue_dev >= 20 or profit_dev >= 20:
                    lines.append("**建议**: 📈 考虑加仓（超预期显著）")
                elif revenue_dev <= -20 or profit_dev <= -20:
                    lines.append("**建议**: ⚠️ 关注风险（不及预期）")
                else:
                    lines.append("**建议**: 📊 持有观察（符合预期）")
                
                lines.append("")
        
        # 市场整体分析
        lines.append("## 📈 市场整体分析")
        
        # 超预期分布
        revenue_surprises = sum(1 for s in report['stocks'] if s['revenue_deviation'] >= 0.20)
        profit_surprises = sum(1 for s in report['stocks'] if s['profit_deviation'] >= 0.20)
        both_surprises = sum(1 for s in report['stocks'] if s['revenue_deviation'] >= 0.20 and s['profit_deviation'] >= 0.20)
        
        total = len(report['stocks'])
        lines.append(f"**营收超预期**: {revenue_surprises}/{total}只({revenue_surprises/total*100:.1f}%)")
        lines.append(f"**净利润超预期**: {profit_surprises}/{total}只({profit_surprises/total*100:.1f}%)")
        lines.append(f"**双指标超预期**: {both_surprises}/{total}只({both_surprises/total*100:.1f}%)")
        lines.append("")
        
        # 行业表现
        industry_stats = report.get('industry_stats', {})
        if industry_stats:
            lines.append("## 🏢 行业表现")
            for industry, stats in industry_stats.items():
                if stats['total'] > 0:
                    surprise_rate = stats['surprises'] / stats['total'] * 100
                    lines.append(f"**{industry}**: {stats['surprises']}/{stats['total']}只超预期({surprise_rate:.1f}%)")
            lines.append("")
        
        # 数据质量说明
        lines.append("## 🔍 数据质量说明")
        lines.append(f"**质量阈值**: 75分")
        lines.append(f"**平均分数**: {report['data_quality_score']:.1f}分")
        lines.append("**验证项目**: 完整性、合理性、一致性、极端值")
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
    
    def send_layered_report(self):
        """分层发送报告（推荐方案）"""
        print("🚀 开始分层发送财报监控报告...")
        
        # 1. 获取报告数据
        report = self.get_latest_report_data()
        if not report:
            print("❌ 无法获取报告数据，停止发送")
            return False
        
        print(f"✅ 获取到 {report['date']} 的报告数据")
        
        # 2. 生成并发送核心摘要
        print("📤 发送核心摘要...")
        core_summary = self.generate_core_summary(report)
        
        # 发送核心摘要到飞书
        success1 = self.sender.send_text(core_summary)
        if not success1:
            print("❌ 核心摘要发送失败")
            return False
        
        print("✅ 核心摘要发送成功")
        
        # 3. 等待5秒，然后发送详细分析
        import time
        time.sleep(5)
        
        print("📤 发送详细分析...")
        detailed_analysis = self.generate_detailed_analysis(report)
        
        # 发送详细分析
        success2 = self.sender.send_text(detailed_analysis)
        if not success2:
            print("❌ 详细分析发送失败")
            return False
        
        print("✅ 详细分析发送成功")
        
        # 4. 保存完整报告到文件
        self._save_full_report(report)
        
        print("🎉 财报监控报告分层发送完成！")
        return True
    
    def _save_full_report(self, report: Dict):
        """保存完整报告到文件"""
        try:
            report_dir = "reports/financial_daily"
            os.makedirs(report_dir, exist_ok=True)
            
            filename = f"{report_dir}/daily_report_{report['date']}_full.md"
            
            with open(filename, 'w', encoding='utf-8') as f:
                # 写入核心摘要
                f.write(self.generate_core_summary(report))
                f.write("\n\n")
                
                # 写入详细分析
                f.write(self.generate_detailed_analysis(report))
            
            print(f"💾 完整报告已保存: {filename}")
            
        except Exception as e:
            print(f"❌ 保存报告失败: {e}")
    
    def run(self):
        """运行发送任务"""
        print("=" * 60)
        print("📈 A股财报监控日报发送任务 - 优化版")
        print("=" * 60)
        
        try:
            # 使用分层发送方案
            success = self.send_layered_report()
            
            if success:
                print("✅ 任务执行成功！")
                return True
            else:
                print("❌ 任务执行失败")
                return False
                
        except Exception as e:
            print(f"❌ 任务执行异常: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    # 创建发送器实例
    sender = OptimizedFinancialReportSender()
    
    # 运行发送任务
    success = sender.run()
    
    # 退出码
    sys.exit(0 if success else 1)