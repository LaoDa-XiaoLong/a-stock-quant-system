#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财报监控日报发送脚本
从监控结果生成优化版日报并发送到飞书
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List
import sqlite3

# 导入飞书发送器
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from safe_feishu_sender import SafeFeishuSender


class FinancialReportSender:
    """财报报告发送器"""
    
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or "https://open.feishu.cn/open-apis/bot/v2/hook/fb95ec56-6ad7-4830-99c7-0eaa287e67e7"
        self.sender = SafeFeishuSender(self.webhook_url)
        self.data_dir = 'data/final_financial_complete'
        self.db_path = f'{self.data_dir}/final_reports_complete.db'
        
        print(f"📊 财报报告发送器初始化完成")
        print(f"📡 Webhook地址: {self.webhook_url[:50]}...")
    
    def get_latest_report(self) -> Dict:
        """获取最新的监控报告"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取最新的监控结果
            cursor.execute('''
            SELECT date, total_stocks, valid_stocks, holdings_surprises, all_surprises,
                   data_quality_score, report_content, trading_advice
            FROM final_monitor_complete
            ORDER BY date DESC
            LIMIT 1
            ''')
            
            row = cursor.fetchone()
            
            if not row:
                print("❌ 未找到监控报告数据")
                return None
            
            # 获取超预期股票详情
            cursor.execute('''
            SELECT stock_code, stock_name, is_holding, industry, metric,
                   surprise_ratio, alert_level, trading_advice
            FROM final_surprises_complete
            WHERE date = ?
            ORDER BY surprise_ratio DESC
            ''', (row[0],))
            
            surprises = []
            for surprise_row in cursor.fetchall():
                surprises.append({
                    'code': surprise_row[0],
                    'name': surprise_row[1],
                    'is_holding': bool(surprise_row[2]),
                    'industry': surprise_row[3],
                    'metric': surprise_row[4],
                    'surprise_ratio': surprise_row[5],
                    'alert_level': surprise_row[6],
                    'advice': surprise_row[7]
                })
            
            conn.close()
            
            report = {
                'date': row[0],
                'total_stocks': row[1],
                'valid_stocks': row[2],
                'holdings_surprises': row[3],
                'all_surprises': row[4],
                'data_quality_score': row[5],
                'report_content': row[6],
                'trading_advice': row[7],
                'surprises': surprises
            }
            
            print(f"✅ 获取到 {report['date']} 的报告")
            print(f"   分析股票: {report['valid_stocks']}/{report['total_stocks']} 只")
            print(f"   超预期股票: {report['all_surprises']} 只")
            print(f"   持仓超预期: {report['holdings_surprises']} 只")
            
            return report
            
        except Exception as e:
            print(f"❌ 获取报告失败: {e}")
            return None
    
    def generate_optimized_report(self, report: Dict) -> str:
        """生成优化版日报（适合飞书显示）"""
        if not report:
            return "暂无报告数据"
        
        # 生成简洁版报告，适合飞书消息长度
        lines = []
        lines.append(f"📈 A股财报监控日报 ({report['date']})")
        lines.append("=" * 40)
        
        # 核心摘要（简洁版）
        lines.append("📊 核心摘要:")
        lines.append(f"• 分析: {report['valid_stocks']}/{report['total_stocks']}只")
        lines.append(f"• 超预期: {report['all_surprises']}只 ({report['all_surprises']/report['valid_stocks']*100:.1f}%)")
        lines.append(f"• 持仓超预期: {report['holdings_surprises']}只")
        lines.append(f"• 数据质量: {report['data_quality_score']:.1f}分")
        lines.append("")
        
        # 总体建议
        lines.append(f"💡 总体建议: {report['trading_advice']}")
        lines.append("")
        
        # 高优先级股票（最多3个，简洁显示）
        if report['surprises']:
            lines.append("🚨 高优先级关注（前3）:")
            
            # 按超预期幅度排序
            high_surprises = sorted(
                report['surprises'], 
                key=lambda x: x['surprise_ratio'], 
                reverse=True
            )[:3]  # 只显示前3个，避免消息过长
            
            for i, stock in enumerate(high_surprises, 1):
                holding_mark = "🎯" if stock['is_holding'] else ""
                alert_emoji = "⚠️" if stock['alert_level'] == '警报' else "🚨"
                
                # 简洁显示
                lines.append(
                    f"{i}. {holding_mark}{stock['code']} {stock['name'][:4]}"
                    f"({stock['metric']}超预期{stock['surprise_ratio']:.1%})"
                )
            
            lines.append("")
        
        # 持仓股票表现（简洁版）
        holdings = [s for s in report['surprises'] if s['is_holding']]
        if holdings:
            lines.append("🎯 持仓表现:")
            
            for stock in holdings[:3]:  # 最多显示3个持仓
                status = "📈" if stock['surprise_ratio'] > 0 else "📉"
                lines.append(
                    f"{status} {stock['code']}: {stock['metric']}超预期{stock['surprise_ratio']:.1%}"
                )
            
            if len(holdings) > 3:
                lines.append(f"...等{len(holdings)}只持仓股票")
            
            lines.append("")
        
        # 数据质量说明（简洁版）
        lines.append("🔍 数据说明:")
        lines.append("• 质量阈值: 75分")
        lines.append("• 极端数据: 校验后纳入")
        lines.append("• 多源验证: 确保准确")
        lines.append("")
        
        # 生成时间
        lines.append(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
        lines.append("📊 A股财报监控系统")
        
        return "\n".join(lines)
    
    def generate_rich_report(self, report: Dict) -> Dict:
        """生成富文本格式报告（用于飞书卡片）"""
        if not report:
            return None
        
        # 创建卡片消息
        card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"📈 A股财报监控日报 ({report['date']})"
                },
                "template": "blue" if report['all_surprises'] > 0 else "grey"
            },
            "elements": []
        }
        
        # 添加摘要部分
        card["elements"].append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**📊 核心摘要**\n"
                          f"• 分析股票: {report['valid_stocks']}/{report['total_stocks']} 只\n"
                          f"• 超预期股票: {report['all_surprises']} 只 ({report['all_surprises']/report['valid_stocks']*100:.1f}%)\n"
                          f"• 持仓超预期: {report['holdings_surprises']} 只\n"
                          f"• 数据质量: {report['data_quality_score']:.1f}分"
            }
        })
        
        # 添加总体建议
        card["elements"].append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**💡 总体建议**\n{report['trading_advice']}"
            }
        })
        
        # 添加高优先级股票
        if report['surprises']:
            high_surprises = sorted(
                report['surprises'], 
                key=lambda x: x['surprise_ratio'], 
                reverse=True
            )[:3]  # 只显示前3个
            
            stock_list = []
            for stock in high_surprises:
                holding_mark = "🎯" if stock['is_holding'] else ""
                alert_emoji = "⚠️" if stock['alert_level'] == '警报' else "🚨"
                
                stock_list.append(
                    f"{holding_mark}**{stock['code']} {stock['name']}** "
                    f"({stock['industry']})\n"
                    f"{alert_emoji} {stock['metric']}超预期{stock['surprise_ratio']:.1%}"
                )
            
            if stock_list:
                card["elements"].append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**🚨 高优先级关注**\n" + "\n".join(stock_list)
                    }
                })
        
        # 添加数据质量说明
        card["elements"].append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**🔍 数据质量说明**\n"
                          f"• 数据质量阈值: 75分（根据老大要求）\n"
                          f"• 极端数据: 先校验比对，通过后再纳入分析\n"
                          f"• 多源验证: 确保数据准确性"
            }
        })
        
        # 添加生成时间
        card["elements"].append({
            "tag": "note",
            "elements": [
                {
                    "tag": "plain_text",
                    "content": f"⏰ 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            ]
        })
        
        return card
    
    def send_report(self, report_type: str = 'auto'):
        """发送报告"""
        print("\n📤 开始发送财报监控日报")
        print("=" * 50)
        
        # 检查是否已经发送过今天的报告
        lock_file = f"data/final_financial/send_lock_{datetime.now().strftime('%Y-%m-%d')}.txt"
        if os.path.exists(lock_file):
            print("⚠️  今天的报告已经发送过，避免重复发送")
            print(f"   锁定文件: {lock_file}")
            return True
        
        # 获取最新报告
        report = self.get_latest_report()
        
        if not report:
            print("❌ 无法获取报告，发送失败")
            return False
        
        # 生成优化版报告
        text_report = self.generate_optimized_report(report)
        print("✅ 优化版日报生成完成")
        
        # 根据类型选择发送方式
        if report_type == 'text':
            # 发送文本消息
            print("📝 发送文本格式报告...")
            result = self.sender.send_safely(text_report, 'text')
            
        elif report_type == 'card':
            # 发送卡片消息
            print("🎴 发送卡片格式报告...")
            card_report = self.generate_rich_report(report)
            if card_report:
                card_payload = {
                    "msg_type": "interactive",
                    "card": card_report
                }
                result = self.sender._send_request(card_payload)
            else:
                result = {'success': False, 'error': '卡片生成失败'}
                
        else:  # auto模式，使用安全发送器
            print("🤖 使用自动模式发送（卡片→富文本→文本）...")
            result = self.sender.send_safely(text_report, 'card')
        
        # 显示结果
        print(f"\n📤 发送结果: {'✅ 成功' if result['success'] else '❌ 失败'}")
        
        if result['success']:
            print(f"📊 报告已发送到飞书")
            print(f"📅 报告日期: {report['date']}")
            print(f"📈 超预期股票: {report['all_surprises']} 只")
            
            # 创建发送锁文件，防止重复发送
            try:
                with open(lock_file, 'w') as f:
                    f.write(f"发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"报告日期: {report['date']}\n")
                    f.write(f"超预期股票: {report['all_surprises']} 只\n")
                print(f"🔒 已创建发送锁文件: {lock_file}")
            except Exception as e:
                print(f"⚠️  创建锁文件失败: {e}")
                
        else:
            print(f"❌ 错误: {result.get('error', '未知错误')}")
            if 'suggestion' in result:
                print(f"💡 建议: {result['suggestion']}")
        
        # 显示统计信息
        stats = self.sender.get_stats()
        print(f"\n📊 发送统计:")
        print(f"  总发送数: {stats['total_sent']}")
        print(f"  成功率: {stats['success_rate']:.0%}")
        print(f"  降级使用率: {stats['fallback_rate']:.0%}")
        
        return result['success']


def main():
    """主函数"""
    print("📈 财报监控日报发送系统")
    print("=" * 60)
    print("功能:")
    print("1. 获取最新财报监控数据")
    print("2. 生成优化版日报")
    print("3. 发送到飞书（支持自动降级）")
    print("=" * 60)
    
    # 创建发送器
    sender = FinancialReportSender()
    
    try:
        # 发送报告
        success = sender.send_report('auto')
        
        if success:
            print("\n✅ 财报监控日报任务完成")
        else:
            print("\n❌ 财报监控日报任务失败")
            
    except Exception as e:
        print(f"❌ 运行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()