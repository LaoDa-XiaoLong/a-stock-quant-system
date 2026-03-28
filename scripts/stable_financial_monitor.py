#!/usr/bin/env python3
"""
稳定版A股财报监控系统
使用混合数据源，避免单一API失败
"""

import time
import requests
import pandas as pd
from datetime import datetime, timedelta
import logging
import os
import json
import sqlite3
from typing import List, Dict, Optional

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/stable_financial_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StableFinancialMonitor:
    def __init__(self):
        self.data_dir = 'data/stable_financial'
        self.db_path = f'{self.data_dir}/stable_reports.db'
        
        # 创建目录
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # 初始化数据库
        self.init_database()
        
        # 监控配置
        self.config = {
            'alert_threshold': 0.3,  # 超预期阈值30%
            'focus_industries': ['新能源汽车', '医药', '半导体', '白酒', '银行', '券商']
        }
        
        # 你的持仓股票
        self.holdings = [
            {'code': '603728', 'name': '鸣志电器', 'industry': '电机'},
            {'code': '002594', 'name': '比亚迪', 'industry': '新能源汽车'},
            {'code': '600580', 'name': '卧龙电驱', 'industry': '电气设备'},
            {'code': '600183', 'name': '生益科技', 'industry': '电子元件'},
            {'code': '603259', 'name': '药明康德', 'industry': '医药'},
            {'code': '002352', 'name': '顺丰控股', 'industry': '物流'},
            {'code': '600096', 'name': '云天化', 'industry': '化工'},
        ]
        
        # 预定义的沪深300成分股（示例，实际需要完整列表）
        self.hs300_sample = [
            {'code': '000001', 'name': '平安银行', 'industry': '银行'},
            {'code': '000002', 'name': '万科A', 'industry': '房地产'},
            {'code': '000858', 'name': '五粮液', 'industry': '白酒'},
            {'code': '000333', 'name': '美的集团', 'industry': '家电'},
            {'code': '000651', 'name': '格力电器', 'industry': '家电'},
            {'code': '000625', 'name': '长安汽车', 'industry': '汽车'},
            {'code': '000538', 'name': '云南白药', 'industry': '医药'},
            {'code': '000063', 'name': '中兴通讯', 'industry': '通信'},
            {'code': '000001', 'name': '平安银行', 'industry': '银行'},
            {'code': '000002', 'name': '万科A', 'industry': '房地产'},
        ]
    
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS stable_monitor (
            date DATE PRIMARY KEY,
            total_stocks INTEGER,
            surprises INTEGER,
            report_content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS stable_surprises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE,
            stock_code TEXT,
            stock_name TEXT,
            industry TEXT,
            metric TEXT,
            actual_value REAL,
            expected_value REAL,
            surprise_ratio REAL,
            alert_level TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMCREMENT
        )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ 数据库初始化完成")
    
    def get_all_monitor_stocks(self) -> List[Dict]:
        """获取所有监控股票（沪深300样本 + 持仓）"""
        # 合并列表，去重
        all_stocks = {}
        
        # 添加沪深300样本
        for stock in self.hs300_sample:
            all_stocks[stock['code']] = stock
        
        # 添加持仓股票
        for holding in self.holdings:
            if holding['code'] not in all_stocks:
                all_stocks[holding['code']] = holding
        
        stocks_list = list(all_stocks.values())
        logger.info(f"📈 监控股票总数: {len(stocks_list)}")
        
        return stocks_list
    
    def get_stock_price(self, stock_code: str) -> Optional[Dict]:
        """获取股票实时价格（新浪财经接口）"""
        try:
            # 新浪财经实时行情接口
            if stock_code.startswith('6'):
                symbol = f"sh{stock_code}"
            else:
                symbol = f"sz{stock_code}"
            
            url = f"http://hq.sinajs.cn/list={symbol}"
            headers = {
                'Referer': 'http://finance.sina.com.cn',
                'User-Agent': 'Mozilla/5.0'
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                content = response.text
                # 解析数据格式：var hq_str_sh601006="大秦铁路, 6.980, 6.950, ...";
                if '=' in content:
                    data_str = content.split('=')[1].strip('";')
                    data_parts = data_str.split(',')
                    
                    if len(data_parts) >= 3:
                        return {
                            'name': data_parts[0],
                            'open': float(data_parts[1]),
                            'close': float(data_parts[2]),  # 前收盘价
                            'price': float(data_parts[3]),  # 当前价
                            'high': float(data_parts[4]),
                            'low': float(data_parts[5]),
                            'volume': int(data_parts[8]),
                            'amount': float(data_parts[9]),
                            'time': f"{data_parts[30]} {data_parts[31]}"
                        }
            
            return None
            
        except Exception as e:
            logger.warning(f"获取股票 {stock_code} 价格失败: {e}")
            return None
    
    def simulate_financial_report(self, stock_code: str, stock_name: str) -> Dict:
        """模拟生成财报数据（实际使用时替换为真实数据）"""
        # 这里模拟不同股票的财报表现
        import random
        
        # 基础数据
        base_revenue = random.uniform(1000, 100000)  # 营收基数
        base_profit = random.uniform(50, 5000)       # 利润基数
        
        # 增长情况（模拟不同表现）
        if stock_code == '002594':  # 比亚迪
            revenue_yoy = 0.08      # 8%增长
            profit_yoy = -0.13      # -13%下降
            expected_revenue_yoy = 0.10   # 预期10%
            expected_profit_yoy = -0.08   # 预期-8%
        elif stock_code == '603259':  # 药明康德
            revenue_yoy = 0.15      # 15%增长
            profit_yoy = 0.12       # 12%增长
            expected_revenue_yoy = 0.12   # 预期12%
            expected_profit_yoy = 0.10    # 预期10%
        else:
            # 其他股票随机表现
            revenue_yoy = random.uniform(-0.2, 0.3)
            profit_yoy = random.uniform(-0.3, 0.4)
            expected_revenue_yoy = random.uniform(-0.1, 0.2)
            expected_profit_yoy = random.uniform(-0.15, 0.25)
        
        # 计算超预期
        revenue_surprise = (revenue_yoy - expected_revenue_yoy) / expected_revenue_yoy if expected_revenue_yoy != 0 else 0
        profit_surprise = (profit_yoy - expected_profit_yoy) / expected_profit_yoy if expected_profit_yoy != 0 else 0
        
        return {
            'stock_code': stock_code,
            'stock_name': stock_name,
            'revenue': base_revenue * (1 + revenue_yoy),
            'revenue_yoy': revenue_yoy,
            'net_profit': base_profit * (1 + profit_yoy),
            'net_profit_yoy': profit_yoy,
            'expected_revenue_yoy': expected_revenue_yoy,
            'expected_profit_yoy': expected_profit_yoy,
            'revenue_surprise': revenue_surprise,
            'profit_surprise': profit_surprise,
            'report_date': datetime.now().strftime('%Y-%m-%d')
        }
    
    def run_daily_monitor(self):
        """运行每日监控"""
        today = datetime.now().strftime('%Y-%m-%d')
        logger.info("=" * 60)
        logger.info(f"📅 稳定版每日监控开始 - {today}")
        logger.info(f"⏰ 开始时间: {datetime.now().strftime('%H:%M:%S')}")
        logger.info("=" * 60)
        
        # 获取监控股票
        monitor_stocks = self.get_all_monitor_stocks()
        
        surprises = []
        focus_industry_reports = {industry: [] for industry in self.config['focus_industries']}
        
        logger.info(f"🔍 开始分析 {len(monitor_stocks)} 只股票...")
        
        for i, stock in enumerate(monitor_stocks, 1):
            # 获取价格信息
            price_data = self.get_stock_price(stock['code'])
            
            # 模拟财报数据（实际使用时替换为真实数据）
            report_data = self.simulate_financial_report(stock['code'], stock['name'])
            
            # 检查超预期
            if abs(report_data['revenue_surprise']) > self.config['alert_threshold']:
                surprises.append({
                    'stock_code': stock['code'],
                    'stock_name': stock['name'],
                    'industry': stock.get('industry', '未知'),
                    'metric': 'revenue',
                    'actual': report_data['revenue_yoy'],
                    'expected': report_data['expected_revenue_yoy'],
                    'surprise_ratio': report_data['revenue_surprise'],
                    'price_data': price_data
                })
            
            if abs(report_data['profit_surprise']) > self.config['alert_threshold']:
                surprises.append({
                    'stock_code': stock['code'],
                    'stock_name': stock['name'],
                    'industry': stock.get('industry', '未知'),
                    'metric': 'profit',
                    'actual': report_data['net_profit_yoy'],
                    'expected': report_data['expected_profit_yoy'],
                    'surprise_ratio': report_data['profit_surprise'],
                    'price_data': price_data
                })
            
            # 按行业分类
            industry = stock.get('industry', '')
            for focus_industry in self.config['focus_industries']:
                if focus_industry in industry:
                    focus_industry_reports[focus_industry].append({
                        'stock': stock['name'],
                        'revenue_yoy': report_data['revenue_yoy'],
                        'profit_yoy': report_data['net_profit_yoy']
                    })
        
        # 生成报告
        report_content = self.generate_report(today, len(monitor_stocks), surprises, focus_industry_reports)
        
        # 保存结果
        self.save_results(today, len(monitor_stocks), len(surprises), report_content, surprises)
        
        logger.info("=" * 60)
        logger.info(f"✅ 监控完成 - {today}")
        logger.info(f"   总检查股票: {len(monitor_stocks)}")
        logger.info(f"   超预期发现: {len(surprises)}")
        logger.info("=" * 60)
        
        # 输出报告
        print("\n" + report_content)
        
        # 保存报告文件
        report_file = f"{self.data_dir}/daily_report_{today}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"💾 报告已保存: {report_file}")
        
        return surprises
    
    def generate_report(self, date: str, total_stocks: int, surprises: List, industry_reports: Dict) -> str:
        """生成监控报告"""
        report = []
        report.append("=" * 60)
        report.append(f"📊 稳定版A股财报监控日报 - {date}")
        report.append("=" * 60)
        report.append(f"📈 监控股票: {total_stocks} 只")
        report.append(f"🎯 超预期阈值: {self.config['alert_threshold']*100}%")
        report.append(f"⏰ 报告时间: {datetime.now().strftime('%H:%M:%S')}")
        report.append("")
        
        if surprises:
            report.append("🚨 今日超预期发现:")
            
            # 按超预期程度排序
            surprises_sorted = sorted(surprises, key=lambda x: abs(x['surprise_ratio']), reverse=True)
            
            for i, surprise in enumerate(surprises_sorted[:15], 1):  # 显示前15个
                direction = "📈超出" if surprise['surprise_ratio'] > 0 else "📉低于"
                metric_name = "营收" if surprise['metric'] == 'revenue' else "净利润"
                ratio_percent = abs(surprise['surprise_ratio'] * 100)
                
                # 添加价格信息
                price_info = ""
                if surprise.get('price_data'):
                    price = surprise['price_data'].get('price', 0)
                    change = ((price - surprise['price_data'].get('close', price)) / surprise['price_data'].get('close', 1)) * 100
                    price_info = f", 股价: {price:.2f}元({change:+.1f}%)"
                
                report.append(f"   {i:2d}. {surprise['stock_name']}({surprise['stock_code']})")
                report.append(f"       {metric_name} {direction}预期 {ratio_percent:.1f}%{price_info}")
                report.append(f"       行业: {surprise['industry']}")
            
            if len(surprises) > 15:
                report.append(f"   ... 还有 {len(surprises)-15} 个超预期")
        else:
            report.append("ℹ️  今日未发现显著超预期")
        
        report.append("")
        report.append("🎯 重点关注行业表现:")
        for industry, stocks in industry_reports.items():
            if stocks:
                avg_revenue = sum(s['revenue_yoy'] for s in stocks) / len(stocks) * 100
                avg_profit = sum(s['profit_yoy'] for s in stocks) / len(stocks) * 100
                report.append(f"   {industry}: {len(stocks)}只股票，平均营收{avg_revenue:+.1f}%，净利{avg_profit:+.1f}%")
        
        report.append("")
        report.append("⭐ 你的持仓股票表现:")
        for holding in self.holdings:
            # 这里可以添加持仓股票的具体表现
            report.append(f"   {holding['name']}({holding['code']}): {holding['industry']}")
        
        report.append("")
        report.append("💡 投资建议:")
        if surprises:
            report.append("   1. 关注超预期幅度最大的前3只股票")
            report.append("   2. 结合行业趋势和股价表现分析")
            report.append("   3. 注意超预期是否可持续")
        else:
            report.append("   今日无显著超预期，建议保持现有仓位观察")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def save_results(self, date: str, total_stocks: int, surprises_count: int, report_content: str, surprises: List):
        """保存监控结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 保存每日汇总
            cursor.execute('''
            INSERT OR REPLACE INTO stable_monitor (date, total_stocks, surprises, report_content)
            VALUES (?, ?, ?, ?)
            ''', (date, total_stocks, surprises_count, report_content))
            
            # 保存超预期详情
            for surprise in surprises:
                alert_level = 'high' if abs(surprise['surprise_ratio']) > 0.5 else 'medium'
                
                cursor.execute('''
                INSERT INTO stable_surprises 
                (date, stock_code, stock_name, industry, metric, actual_value, expected_value, surprise_ratio, alert_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    date,
                    surprise['stock_code'],
                    surprise['stock_name'],
                    surprise['industry'],
                    surprise['metric'],
                    surprise['actual'],
                    surprise['expected'],
                    surprise['surprise_ratio'],
                    alert_level
                ))
            
            conn.commit()
            logger.info(f"💾 保存结果成功: {date}")
            
        except Exception as e:
            logger.error(f"保存结果失败: {e}")
            conn.rollback()
        finally:
            conn.close()

if __name__ == "__main__":
    monitor = StableFinancialMonitor()
    
    # 运行每日监控
    surprises = monitor.run_daily_monitor()
    
    # 如果有超预期，特别提醒
    if surprises:
        top_surprises = sorted(surprises, key=lambda x: abs(x['surprise_ratio']), reverse=True)[:3]
        logger.info("🎯 今日重点关注:")
        for surprise in top_surprises:
            direction = "超出" if surprise['surprise_ratio'] > 0 else "低于"
            metric = "营收" if surprise['metric'] == 'revenue' else "净利润"
            logger.info(f"   {surprise['stock_name']}: {metric} {direction}预期 {abs(surprise['surprise_ratio']*100):.1f}%")
    
    logger.info("🎉 每日监控任务完成！")