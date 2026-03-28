#!/usr/bin/env python3
"""
每日A股财报监控系统
每天22点前运行，监控沪深300+持仓股票
"""

import time
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import os
import json
import sqlite3
import akshare as ak
from typing import List, Dict, Optional

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/daily_financial_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DailyFinancialMonitor:
    def __init__(self):
        self.data_dir = 'data/daily_financial'
        self.db_path = f'{self.data_dir}/daily_reports.db'
        self.report_time = '22:00'  # 每天22点前完成
        
        # 创建目录
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # 初始化数据库
        self.init_database()
        
        # 监控配置
        self.config = {
            'alert_threshold': 0.3,  # 超预期阈值30%
            'focus_industries': ['新能源汽车', '医药', '半导体', '白酒', '银行']
        }
        
        # 你的持仓股票
        self.holdings = [
            {'code': '603728', 'name': '鸣志电器'},
            {'code': '002594', 'name': '比亚迪'},
            {'code': '600580', 'name': '卧龙电驱'},
            {'code': '600183', 'name': '生益科技'},
            {'code': '603259', 'name': '药明康德'},
            {'code': '002352', 'name': '顺丰控股'},
            {'code': '600096', 'name': '云天化'},
        ]
    
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建监控记录表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_monitor (
            date DATE PRIMARY KEY,
            total_stocks INTEGER,
            new_reports INTEGER,
            surprises INTEGER,
            report_content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建超预期记录表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_surprises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE,
            stock_code TEXT,
            stock_name TEXT,
            report_type TEXT,
            metric TEXT,
            actual_value REAL,
            expected_value REAL,
            surprise_ratio REAL,
            industry TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ 数据库初始化完成")
    
    def get_hs300_stocks(self) -> List[Dict]:
        """获取沪深300成分股"""
        try:
            logger.info("📊 获取沪深300成分股...")
            
            # 使用akshare获取沪深300成分股
            hs300_df = ak.index_stock_cons_sina(symbol="hs300")
            
            stocks = []
            for _, row in hs300_df.iterrows():
                stocks.append({
                    'code': row['code'].replace('sh', '').replace('sz', ''),
                    'name': row['name']
                })
            
            logger.info(f"✅ 获取到 {len(stocks)} 只沪深300成分股")
            return stocks[:300]  # 确保不超过300只
            
        except Exception as e:
            logger.error(f"❌ 获取沪深300失败: {e}")
            # 返回示例数据
            return [
                {'code': '000001', 'name': '平安银行'},
                {'code': '000002', 'name': '万科A'},
                {'code': '000858', 'name': '五粮液'},
                {'code': '000333', 'name': '美的集团'},
                {'code': '000651', 'name': '格力电器'},
            ]
    
    def get_all_monitor_stocks(self) -> List[Dict]:
        """获取所有需要监控的股票（沪深300 + 持仓）"""
        hs300_stocks = self.get_hs300_stocks()
        
        # 合并列表，去重
        all_stocks = {stock['code']: stock for stock in hs300_stocks}
        
        # 添加持仓股票（如果不在沪深300中）
        for holding in self.holdings:
            if holding['code'] not in all_stocks:
                all_stocks[holding['code']] = holding
        
        stocks_list = list(all_stocks.values())
        logger.info(f"📈 总监控股票数: {len(stocks_list)} (沪深300: {len(hs300_stocks)}, 持仓: {len(self.holdings)})")
        
        return stocks_list
    
    def check_stock_report(self, stock_code: str, stock_name: str) -> Optional[Dict]:
        """检查单只股票的财报情况"""
        try:
            # 这里使用akshare获取财报信息
            # 注意：akshare的财报数据可能不是实时的
            
            # 获取最新财报日期
            stock_financial_df = ak.stock_financial_report_sina(stock=stock_code, symbol="年报")
            
            if not stock_financial_df.empty:
                latest_report = stock_financial_df.iloc[0]
                
                report_data = {
                    'stock_code': stock_code,
                    'stock_name': stock_name,
                    'report_type': 'annual',
                    'report_date': latest_report['公告日期'],
                    'revenue': latest_report.get('营业收入', 0),
                    'revenue_yoy': latest_report.get('营业收入同比增长', 0),
                    'net_profit': latest_report.get('净利润', 0),
                    'net_profit_yoy': latest_report.get('净利润同比增长', 0),
                    'eps': latest_report.get('每股收益', 0),
                }
                
                # 这里可以添加市场预期数据（需要其他数据源）
                # 暂时使用简单预测：历史平均增长
                report_data['expected_revenue_yoy'] = 0.1  # 假设预期增长10%
                report_data['expected_profit_yoy'] = 0.15  # 假设预期增长15%
                
                # 计算超预期
                revenue_surprise = (report_data['revenue_yoy'] - report_data['expected_revenue_yoy']) / report_data['expected_revenue_yoy']
                profit_surprise = (report_data['net_profit_yoy'] - report_data['expected_profit_yoy']) / report_data['expected_profit_yoy']
                
                report_data['revenue_surprise'] = revenue_surprise
                report_data['profit_surprise'] = profit_surprise
                
                return report_data
            
            return None
            
        except Exception as e:
            logger.warning(f"检查股票 {stock_code} 财报失败: {e}")
            return None
    
    def run_daily_check(self):
        """运行每日检查"""
        today = datetime.now().strftime('%Y-%m-%d')
        logger.info("=" * 60)
        logger.info(f"📅 每日财报监控开始 - {today}")
        logger.info(f"⏰ 开始时间: {datetime.now().strftime('%H:%M:%S')}")
        logger.info("=" * 60)
        
        # 获取监控股票列表
        monitor_stocks = self.get_all_monitor_stocks()
        
        new_reports = []
        surprises = []
        
        # 检查每只股票（可以优化为批量检查）
        logger.info(f"🔍 开始检查 {len(monitor_stocks)} 只股票...")
        
        for i, stock in enumerate(monitor_stocks, 1):
            if i % 50 == 0:
                logger.info(f"   已检查 {i}/{len(monitor_stocks)} 只股票")
            
            report_data = self.check_stock_report(stock['code'], stock['name'])
            
            if report_data:
                new_reports.append(report_data)
                
                # 检查是否超预期
                if abs(report_data.get('revenue_surprise', 0)) > self.config['alert_threshold']:
                    surprises.append({
                        'stock_code': stock['code'],
                        'stock_name': stock['name'],
                        'metric': 'revenue',
                        'actual': report_data['revenue_yoy'],
                        'expected': report_data['expected_revenue_yoy'],
                        'surprise_ratio': report_data['revenue_surprise']
                    })
                
                if abs(report_data.get('profit_surprise', 0)) > self.config['alert_threshold']:
                    surprises.append({
                        'stock_code': stock['code'],
                        'stock_name': stock['name'],
                        'metric': 'profit',
                        'actual': report_data['net_profit_yoy'],
                        'expected': report_data['expected_profit_yoy'],
                        'surprise_ratio': report_data['profit_surprise']
                    })
        
        # 生成报告
        report_content = self.generate_daily_report(today, len(monitor_stocks), len(new_reports), surprises)
        
        # 保存到数据库
        self.save_daily_result(today, len(monitor_stocks), len(new_reports), len(surprises), report_content)
        
        # 保存超预期记录
        for surprise in surprises:
            self.save_surprise_record(today, surprise)
        
        logger.info("=" * 60)
        logger.info(f"✅ 每日监控完成 - {today}")
        logger.info(f"   总检查股票: {len(monitor_stocks)}")
        logger.info(f"   新发现财报: {len(new_reports)}")
        logger.info(f"   超预期发现: {len(surprises)}")
        logger.info("=" * 60)
        
        # 输出报告
        print("\n" + report_content)
        
        # 保存报告到文件
        report_file = f"{self.data_dir}/daily_report_{today}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"💾 报告已保存到: {report_file}")
    
    def generate_daily_report(self, date: str, total_stocks: int, new_reports: int, surprises: List) -> str:
        """生成每日报告"""
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append(f"📊 A股财报监控日报 - {date}")
        report_lines.append("=" * 60)
        report_lines.append(f"📈 监控范围: 沪深300成分股 + 持仓股票")
        report_lines.append(f"📊 总监控股票: {total_stocks} 只")
        report_lines.append(f"📄 新发现财报: {new_reports} 份")
        report_lines.append(f"🎯 超预期阈值: {self.config['alert_threshold']*100}%")
        report_lines.append("")
        
        if surprises:
            report_lines.append("🚨 今日超预期发现:")
            
            # 按超预期程度排序
            surprises_sorted = sorted(surprises, key=lambda x: abs(x['surprise_ratio']), reverse=True)
            
            for surprise in surprises_sorted[:10]:  # 只显示前10个
                direction = "超出" if surprise['surprise_ratio'] > 0 else "低于"
                metric_name = "营收" if surprise['metric'] == 'revenue' else "净利润"
                report_lines.append(f"   {surprise['stock_name']}({surprise['stock_code']}): "
                                  f"{metric_name} {direction}预期 {abs(surprise['surprise_ratio']*100):.1f}%")
            
            if len(surprises) > 10:
                report_lines.append(f"   ... 还有 {len(surprises)-10} 个超预期")
        else:
            report_lines.append("ℹ️  今日未发现显著超预期")
        
        report_lines.append("")
        report_lines.append("🎯 重点关注行业今日表现:")
        for industry in self.config['focus_industries'][:3]:
            report_lines.append(f"   {industry}: 今日暂无数据")
        
        report_lines.append("")
        report_lines.append("⭐ 持仓股票今日表现:")
        for holding in self.holdings[:5]:  # 只显示前5个
            report_lines.append(f"   {holding['name']}({holding['code']}): 等待数据更新")
        
        report_lines.append("")
        report_lines.append(f"⏰ 报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)
    
    def save_daily_result(self, date: str, total_stocks: int, new_reports: int, surprises: int, report_content: str):
        """保存每日结果到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT OR REPLACE INTO daily_monitor (date, total_stocks, new_reports, surprises, report_content)
            VALUES (?, ?, ?, ?, ?)
            ''', (date, total_stocks, new_reports, surprises, report_content))
            
            conn.commit()
            logger.info(f"💾 保存每日监控结果: {date}")
            
        except Exception as e:
            logger.error(f"保存每日结果失败: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def save_surprise_record(self, date: str, surprise: Dict):
        """保存超预期记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO daily_surprises (date, stock_code, stock_name, metric, actual_value, expected_value, surprise_ratio)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                date,
                surprise['stock_code'],
                surprise['stock_name'],
                surprise['metric'],
                surprise['actual'],
                surprise['expected'],
                surprise['surprise_ratio']
            ))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"保存超预期记录失败: {e}")
            conn.rollback()
        finally:
            conn.close()

if __name__ == "__main__":
    monitor = DailyFinancialMonitor()
    
    # 运行每日检查
    monitor.run_daily_check()
    
    logger.info("🎉 每日监控任务完成！")
    logger.info("📅 明天22点前将再次运行")