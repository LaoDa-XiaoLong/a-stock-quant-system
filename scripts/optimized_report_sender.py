#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化版财报日报发送器 - 适配现有数据库结构
生成分层版日报（核心摘要+详细分析）并发送到A股数据分析群
"""

import json
import os
import sys
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import requests
import time

class OptimizedReportSender:
    """优化版报告发送器"""
    
    def __init__(self):
        # A股数据分析群webhook
        self.webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/fb95ec56-6ad7-4830-99c7-0eaa287e67e7"
        self.db_path = 'data/final_financial/final_reports.db'
        
        print(f"📊 优化版财报日报发送器初始化完成")
        print(f"📡 目标群组: A股数据分析群")
    
    def get_latest_report_data(self) -> Dict:
        """获取最新的监控报告数据（适配现有表结构）"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 获取最新的监控结果
            cursor.execute('''
            SELECT date, total_stocks, holdings_surprises, all_surprises, report_content, trading_advice
            FROM final_monitor
            ORDER BY date DESC
            LIMIT 1
            ''')
            
            row = cursor.fetchone()
            
            if not row:
                print("❌ 未找到监控报告数据")
                return None
            
            # 获取详细的股票数据
            cursor.execute('''
            SELECT date, stock_code, stock_name, is_holding, industry, metric,
                   actual_value, expected_value, surprise_ratio, alert_level, trading_advice
            FROM final_surprises
            WHERE date = ?
            ORDER BY ABS(surprise_ratio) DESC
            ''', (row['date'],))
            
            stocks = []
            for stock_row in cursor.fetchall():
                stocks.append(dict(stock_row))
            
            conn.close()
            
            # 构建完整报告数据
            report = dict(row)
            report['stocks'] = stocks
            report['holdings'] = [s for s in stocks if s['is_holding'] == 1]
            report['surprises'] = [s for s in stocks if abs(s['surprise_ratio']) >= 0.20]  # 20%阈值
            
            # 计算行业分布
            report['industry_stats'] = self._calculate_industry_stats(stocks)
            
            print(f"✅ 获取到 {report['date']} 的报告数据")
            print(f"   总股票数: {report['total_stocks']}")
            print(f"   持仓超预期: {report['holdings_surprises']}")
            print(f"   总超预期: {report['all_surprises']}")
            
            return report
            
        except Exception as e:
            print(f"❌ 获取报告数据失败: {e}")
            return None
    
    def _calculate_industry_stats(self, stocks: List[Dict]) -> Dict:
        """计算行业统计数据"""
        industry_stats = {}
        for stock in stocks:
            industry = stock.get('industry', '其他')
            if industry not in industry_stats:
                industry_stats[industry] = {
                    'total': 0,
                    'surprises': 0,
                    'holdings': 0
                }
            
            industry_stats[industry]['total'] += 1
            if abs(stock.get('surprise_ratio', 0)) >= 0.20:
                industry_stats[industry]['surprises'] += 1
            if stock.get('is_holding') == 1:
                industry_stats[industry]['holdings'] += 1
        
        return industry_stats
    
    def generate_core_summary(self, report: Dict) -> str:
        """生成核心摘要（第一层消息）"""
        if not report:
            return "暂无报告数据"
        
        # 计算关键指标
        total_stocks = report['total_stocks']
        surprise_stocks = report['all_surprises']
        surprise_ratio = (surprise_stocks / total_stocks * 100) if total_stocks > 0 else 0
        
        holdings_total = len(report['holdings'])
        holdings_surprises = report['holdings_surprises']
        holdings_ratio = (holdings_surprises / holdings_total * 100) if holdings_total > 0 else 0
        
        # 获取前3名超预期股票
        top_surprises = sorted(
            report['surprises'],
            key=lambda x: abs(x.get('surprise_ratio', 0)),
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
        
        # 高优先级关注
        if top_surprises:
            lines.append("")
            lines.append("🚨 高优先级关注")
            for i, stock in enumerate(top_surprises, 1):
                holding_mark = "🎯" if stock.get('is_holding') == 1 else ""
                metric = stock.get('metric', '未知')
                ratio = stock.get('surprise_ratio', 0) * 100
                direction = "📈超出" if ratio > 0 else "📉低于"
                lines.append(f"{i}. {holding_mark}{stock.get('stock_name', '未知')}: {metric}{direction}预期{abs(ratio):.1f}%")
        
        # 总体建议
        lines.append("")
        lines.append(f"💡 总体建议: {report.get('trading_advice', '保持现有仓位观察')}")
        
        # 行业分布
        industry_stats = report.get('industry_stats', {})
        if industry_stats:
            lines.append("")
            lines.append("🏢 行业分布")
            for industry, stats in industry_stats.items():
                if stats['total'] > 0:
                    surprise_rate = stats['surprises'] / stats['total'] * 100
                    lines.append(f"• {industry}: {stats['surprises']}/{stats['total']}只超预期({surprise_rate:.1f}%)")
        
        # 生成时间和查看链接
        lines.append("")
        lines.append(f"⏰ 生成时间: {datetime.now().strftime('%H:%M:%S')}")
        lines.append("👇 查看详细分析")
        
        return "\n".join(lines)
    
    def generate_detailed_analysis(self, report: Dict) -> str:
        """生成详细分析（第二层消息）"""
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
                key=lambda x: abs(x.get('surprise_ratio', 0)),
                reverse=True
            )
            
            for stock in sorted_holdings:
                lines.append(f"### {stock.get('stock_name', '未知')} ({stock.get('stock_code', '未知')})")
                
                # 基本信息
                industry = stock.get('industry', '未知')
                metric = stock.get('metric', '未知')
                ratio = stock.get('surprise_ratio', 0) * 100
                direction = "超出" if ratio > 0 else "低于"
                
                lines.append(f"**行业**: {industry}")
                lines.append(f"**指标**: {metric}")
                lines.append(f"**超预期**: {direction}预期 {abs(ratio):.1f}%")
                
                # 实际值 vs 预期值
                actual = stock.get('actual_value', 0)
                expected = stock.get('expected_value', 0)
                if metric == 'revenue':
                    lines.append(f"**实际营收增长**: {actual*100:+.1f}%")
                    lines.append(f"**预期营收增长**: {expected*100:+.1f}%")
                else:  # profit
                    lines.append(f"**实际净利润增长**: {actual*100:+.1f}%")
                    lines.append(f"**预期净利润增长**: {expected*100:+.1f}%")
                
                # 警报级别
                alert_level = stock.get('alert_level', '正常')
                lines.append(f"**警报级别**: {alert_level}")
                
                # 交易建议
                trading_advice = stock.get('trading_advice', '')
                if trading_advice:
                    lines.append(f"**交易建议**: {trading_advice}")
                
                lines.append("")
        
        # 市场整体分析
        lines.append("## 📈 市场整体分析")
        
        # 超预期分布
        revenue_surprises = sum(1 for s in report['stocks'] if s.get('metric') == 'revenue' and abs(s.get('surprise_ratio', 0)) >= 0.20)
        profit_surprises = sum(1 for s in report['stocks'] if s.get('metric') == 'profit' and abs(s.get('surprise_ratio', 0)) >= 0.20)
        total = len(report['stocks'])
        
        lines.append(f"**营收超预期**: {revenue_surprises}/{total}只({revenue_surprises/total*100:.1f}%)")
        lines.append(f"**净利润超预期**: {profit_surprises}/{total}只({profit_surprises/total*100:.1f}%)")
        lines.append("")
        
        # 行业表现
        industry_stats = report.get('industry_stats', {})
        if industry_stats:
            lines.append("## 🏢 行业表现")
            for industry, stats in industry_stats.items():
                if stats['total'] > 0:
                    surprise_rate = stats['surprises'] / stats['total'] * 100
                    holding_mark = "🎯" if stats['holdings'] > 0 else ""
                    lines.append(f"**{holding_mark}{industry}**: {stats['surprises']}/{stats['total']}只超预期({surprise_rate:.1f}%)")
            lines.append("")
        
        # 数据说明
        lines.append("## 🔍 数据说明")
        lines.append("**监控范围**: 沪深300成分股 + 持仓股票")
        lines.append("**超预期阈值**: 20%")
        lines.append("**数据来源**: 模拟财务数据（实际应使用真实财报数据）")
        lines.append("**更新时间**: 每日自动监控")
        lines.append("")
        
        # 生成时间
        lines.append(f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        
        return "\n".join(lines)
    
    def send_to_feishu(self, content: str, title: str = None) -> bool:
        """发送消息到飞书"""
        try:
            if not title:
                title = "A股财报监控日报"
            
            # 构建飞书消息格式
            message = {
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
                        "template": "blue"
                    },
                    "elements": [
                        {
                            "tag": "div",
                            "text": {
                                "tag": "lark_md",
                                "content": content[:2000]  # 限制长度
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
                                    "content": f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                                }
                            ]
                        }
                    ]
                }
            }
            
            # 发送请求
            response = requests.post(
                self.webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ 飞书消息发送成功: {title}")
                return True
            else:
                print(f"❌ 飞书消息发送失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 飞书消息发送异常: {e}")
            return False
    
    def send_layered_report(self) -> bool:
        """分层发送报告"""
        print("🚀 开始分层发送财报监控报告...")
        
        # 1. 获取报告数据
        report = self.get_latest_report_data()
        if not report:
            print("❌ 无法获取报告数据，停止发送")
            return False
        
        # 2. 生成并发送核心摘要
        print("📤 发送核心摘要...")
        core_summary = self.generate_core_summary(report)
        
        # 发送核心摘要到飞书
        success1 = self.send_to_feishu(core_summary, f"📈 A股财报监控日报 - {report['date']}")
        if not success1:
            print("❌ 核心摘要发送失败")
            return False
        
        print("✅ 核心摘要发送成功")
        
        # 3. 等待3秒，然后发送详细分析
        time.sleep(3)
        
        print("📤 发送详细分析...")
        detailed_analysis = self.generate_detailed_analysis(report)
        
        # 发送详细分析
        success2 = self.send_to_feishu(detailed_analysis, f"📊 详细分析 - {report['date']}")
        if not success2:
            print("❌ 详细分析发送失败")
            return False
        
        print("✅ 详细分析发送成功")
        
        # 4. 保存完整报告到文件
        self._save_full_report(report, core_summary, detailed_analysis)
        
        print("🎉 财报监控报告分层发送完成！")
        return True
    
    def _save_full_report(self, report: Dict, core_summary: str, detailed_analysis: str):
        """保存完整报告到文件"""
        try:
            report_dir = "reports/financial_daily"
            os.makedirs(report_dir, exist_ok=True)
            
            filename = f"{report_dir}/daily_report_{report['date']}_layered.md"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# A股财报监控日报（分层版）\n\n")
                f.write(f"**生成日期**: {report['date']}\n")
                f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write("## 核心摘要\n")
                f.write(core_summary)
                f.write("\n\n")
                
                f.write("## 详细分析\n")
                f.write(detailed_analysis)
            
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
    sender = OptimizedReportSender()
    
    # 运行发送任务
    success = sender.run()
    
    # 退出码
    sys.exit(0 if success else 1)