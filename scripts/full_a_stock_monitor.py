#!/usr/bin/env python3
"""
全A股上市公司财报监控系统
监控所有A股公司的年报、季报，发现超预期机会
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
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/full_a_stock_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FullAStockMonitor:
    def __init__(self):
        self.data_dir = 'data/full_a_stock'
        self.db_path = f'{self.data_dir}/a_stock_reports.db'

        # 创建目录
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs('logs', exist_ok=True)

        # 初始化数据库
        self.init_database()

        # 监控配置
        self.config = {
            'check_interval': 3600,  # 检查间隔（秒），1小时
            'max_workers': 10,       # 并发线程数
            'batch_size': 100,       # 每批处理的股票数量
            'alert_threshold': 0.3,  # 超预期阈值（30%）
        }

        # 重点关注行业（可根据需要调整）
        self.focus_industries = [
            '新能源汽车', '锂电池', '光伏', '半导体',
            '医药', '白酒', '银行', '券商',
            '人工智能', '云计算', '5G'
        ]

    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建股票基本信息表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS stocks (
            code TEXT PRIMARY KEY,
            name TEXT,
            industry TEXT,
            market_cap REAL,
            pe_ratio REAL,
            last_updated TIMESTAMP
        )
        ''')

        # 创建财报数据表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS financial_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_code TEXT,
            report_type TEXT,  -- annual, q1, q2, q3
            report_year INTEGER,
            report_date DATE,
            revenue REAL,
            revenue_yoy REAL,  -- 营收同比增长
            net_profit REAL,
            net_profit_yoy REAL,  -- 净利润同比增长
            eps REAL,  -- 每股收益
            roe REAL,  -- 净资产收益率
            gross_margin REAL,  -- 毛利率
            forecast_revenue REAL,  -- 预测营收
            forecast_profit REAL,  -- 预测净利润
            surprise_ratio REAL,  -- 超预期比例
            report_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (stock_code) REFERENCES stocks(code)
        )
        ''')

        # 创建超预期记录表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS surprises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_code TEXT,
            stock_name TEXT,
            report_type TEXT,
            report_date DATE,
            metric TEXT,  -- revenue, profit, eps等
            actual_value REAL,
            expected_value REAL,
            surprise_ratio REAL,
            alert_level TEXT,  -- high, medium, low
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        conn.commit()
        conn.close()
        logger.info("✅ 数据库初始化完成")

    def get_all_a_stocks(self):
        """获取所有A股股票列表"""
        # 这里可以使用akshare或tushare获取完整列表
        # 暂时使用示例数据
        stocks = [
            {'code': '002594', 'name': '比亚迪', 'industry': '新能源汽车'},
            {'code': '603728', 'name': '鸣志电器', 'industry': '电机'},
            {'code': '600580', 'name': '卧龙电驱', 'industry': '电气设备'},
            {'code': '600183', 'name': '生益科技', 'industry': '电子元件'},
            {'code': '603259', 'name': '药明康德', 'industry': '医药'},
            {'code': '002352', 'name': '顺丰控股', 'industry': '物流'},
            {'code': '600096', 'name': '云天化', 'industry': '化工'},
            # 可以继续添加更多股票
        ]

        # 保存到数据库
        conn = sqlite3.connect(self.db_path)
        for stock in stocks:
            conn.execute('''
            INSERT OR REPLACE INTO stocks (code, name, industry, last_updated)
            VALUES (?, ?, ?, ?)
            ''', (stock['code'], stock['name'], stock['industry'], datetime.now()))
        conn.commit()
        conn.close()

        logger.info(f"📊 加载了 {len(stocks)} 只股票")
        return stocks

    def check_single_stock_report(self, stock_code, stock_name):
        """检查单只股票的财报发布情况"""
        try:
            # 这里实现具体的财报检查逻辑
            # 可以调用多个数据源API

            # 示例：模拟检查比亚迪
            if stock_code == '002594':
                # 假设比亚迪刚刚发布年报
                report_data = {
                    'report_type': 'annual',
                    'report_year': 2025,
                    'report_date': '2026-03-27',
                    'revenue': 839362,  # 百万
                    'revenue_yoy': 0.08,  # 8%增长
                    'net_profit': 35011,  # 百万
                    'net_profit_yoy': -0.13,  # -13%下降
                    'eps': 3.84,
                    'forecast_revenue': 820000,  # 预测值
                    'forecast_profit': 38000,    # 预测值
                }

                # 计算超预期比例
                revenue_surprise = (report_data['revenue'] - report_data['forecast_revenue']) / report_data['forecast_revenue']
                profit_surprise = (report_data['net_profit'] - report_data['forecast_profit']) / report_data['forecast_profit']

                surprises = []
                if abs(revenue_surprise) > self.config['alert_threshold']:
                    surprises.append(('revenue', report_data['revenue'], report_data['forecast_revenue'], revenue_surprise))

                if abs(profit_surprise) > self.config['alert_threshold']:
                    surprises.append(('profit', report_data['net_profit'], report_data['forecast_profit'], profit_surprise))

                return stock_code, stock_name, report_data, surprises

            # 其他股票暂时返回空
            return stock_code, stock_name, None, []

        except Exception as e:
            logger.error(f"检查股票 {stock_code} 失败: {e}")
            return stock_code, stock_name, None, []

    def batch_check_reports(self, stocks_batch):
        """批量检查财报"""
        results = []

        with ThreadPoolExecutor(max_workers=self.config['max_workers']) as executor:
            futures = []
            for stock in stocks_batch:
                future = executor.submit(
                    self.check_single_stock_report,
                    stock['code'],
                    stock['name']
                )
                futures.append(future)

            for future in as_completed(futures):
                try:
                    result = future.result(timeout=10)
                    results.append(result)
                except Exception as e:
                    logger.error(f"批量检查失败: {e}")

        return results

    def save_report_data(self, stock_code, report_data):
        """保存财报数据到数据库"""
        if not report_data:
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
            INSERT INTO financial_reports
            (stock_code, report_type, report_year, report_date, revenue, revenue_yoy,
             net_profit, net_profit_yoy, eps, forecast_revenue, forecast_profit, surprise_ratio)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                stock_code,
                report_data['report_type'],
                report_data['report_year'],
                report_data['report_date'],
                report_data['revenue'],
                report_data['revenue_yoy'],
                report_data['net_profit'],
                report_data['net_profit_yoy'],
                report_data['eps'],
                report_data.get('forecast_revenue'),
                report_data.get('forecast_profit'),
                report_data.get('surprise_ratio', 0)
            ))

            conn.commit()
            logger.info(f"💾 保存 {stock_code} 财报数据成功")

        except Exception as e:
            logger.error(f"保存财报数据失败: {e}")
            conn.rollback()
        finally:
            conn.close()

    def save_surprise_alert(self, stock_code, stock_name, surprises):
        """保存超预期警报"""
        if not surprises:
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            for metric, actual, expected, ratio in surprises:
                # 确定警报级别
                abs_ratio = abs(ratio)
                if abs_ratio > 0.5:
                    alert_level = 'high'
                elif abs_ratio > 0.3:
                    alert_level = 'medium'
                else:
                    alert_level = 'low'

                cursor.execute('''
                INSERT INTO surprises
                (stock_code, stock_name, report_type, report_date, metric,
                 actual_value, expected_value, surprise_ratio, alert_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    stock_code,
                    stock_name,
                    'annual',  # 假设是年报
                    datetime.now().strftime('%Y-%m-%d'),
                    metric,
                    actual,
                    expected,
                    ratio,
                    alert_level
                ))

            conn.commit()
            logger.info(f"🚨 保存 {stock_code} 超预期警报: {len(surprises)} 条")

        except Exception as e:
            logger.error(f"保存警报失败: {e}")
            conn.rollback()
        finally:
            conn.close()

    def generate_daily_report(self):
        """生成每日监控报告"""
        conn = sqlite3.connect(self.db_path)

        # 获取今日发现的超预期
        today = datetime.now().strftime('%Y-%m-%d')
        surprises_df = pd.read_sql_query(f'''
        SELECT * FROM surprises
        WHERE DATE(created_at) = '{today}'
        ORDER BY alert_level DESC, abs(surprise_ratio) DESC
        LIMIT 20
        ''', conn)

        # 获取重点关注行业的财报
        focus_reports = []
        for industry in self.focus_industries[:5]:  # 只检查前5个行业
            df = pd.read_sql_query(f'''
            SELECT s.code, s.name, s.industry, fr.report_date, fr.revenue_yoy, fr.net_profit_yoy
            FROM financial_reports fr
            JOIN stocks s ON fr.stock_code = s.code
            WHERE s.industry LIKE '%{industry}%'
            AND fr.report_date >= DATE('now', '-30 days')
            ORDER BY fr.report_date DESC
            LIMIT 5
            ''', conn)

            if not df.empty:
                focus_reports.append((industry, df))

        conn.close()

        # 生成报告
        report = []
        report.append("=" * 60)
        report.append(f"📊 全A股财报监控日报 - {today}")
        report.append("=" * 60)

        if not surprises_df.empty:
            report.append("\n🚨 今日超预期发现:")
            for _, row in surprises_df.iterrows():
                direction = "超出" if row['surprise_ratio'] > 0 else "低于"
                report.append(f"   {row['stock_name']}({row['stock_code']}): "
                            f"{row['metric']} {direction}预期 {abs(row['surprise_ratio']*100):.1f}%")
        else:
            report.append("\nℹ️  今日未发现显著超预期")

        if focus_reports:
            report.append("\n🎯 重点关注行业最新财报:")
            for industry, df in focus_reports:
                report.append(f"\n   {industry}:")
                for _, row in df.iterrows():
                    report.append(f"     {row['name']}: 营收{row['revenue_yoy']*100:+.1f}%, "
                                f"净利{row['net_profit_yoy']*100:+.1f}%")

        report.append(f"\n⏰ 下次检查时间: {datetime.now() + timedelta(seconds=self.config['check_interval'])}")
        report.append("=" * 60)

        return "\n".join(report)

    def send_alert(self, message, level='info'):
        """发送警报（可扩展为飞书/微信推送）"""
        logger.info(f"📢 {level.upper()}警报: {message}")

        # 这里可以集成飞书、微信等推送
        # 例如：飞书机器人、企业微信、邮件等

        # 简单实现：保存到文件
        alert_file = f'{self.data_dir}/alerts_{datetime.now().strftime("%Y%m%d")}.txt'
        with open(alert_file, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now()} - {level} - {message}\n")

    def run_monitor(self):
        """运行监控主循环"""
        logger.info("=" * 60)
        logger.info("🚀 全A股财报监控系统启动")
        logger.info(f"📅 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"📊 监控范围: 全A股上市公司")
        logger.info(f"🎯 超预期阈值: {self.config['alert_threshold']*100}%")
        logger.info("=" * 60)

        # 获取股票列表
        stocks = self.get_all_a_stocks()

        cycle_count = 0

        while True:
            cycle_count += 1
            logger.info(f"\n🔄 第{cycle_count}轮监控开始")

            try:
                # 分批检查
                for i in range(0, len(stocks), self.config['batch_size']):
                    batch = stocks[i:i + self.config['batch_size']]
                    logger.info(f"  检查批次 {i//self.config['batch_size']+1}: "
                              f"{len(batch)} 只股票")

                    results = self.batch_check_reports(batch)

                    # 处理结果
                    for stock_code, stock_name, report_data, surprises in results:
                        if report_data:
                            self.save_report_data(stock_code, report_data)

                        if surprises:
                            self.save_surprise_alert(stock_code, stock_name, surprises)

                            # 发送即时警报
                            for metric, actual, expected, ratio in surprises:
                                direction = "超出" if ratio > 0 else "低于"
                                alert_msg = (f"🚨 {stock_name}({stock_code}) {metric} "
                                           f"{direction}预期 {abs(ratio*100):.1f}%")
                                self.send_alert(alert_msg, 'high' if abs(ratio) > 0.5 else 'medium')

                # 生成日报
                daily_report = self.generate_daily_report()
                logger.info(daily_report)

                # 保存日报
                report_file = f'{self.data_dir}/daily_report_{datetime.now().strftime("%Y%m%d")}.txt'
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(daily_report)

                logger.info(f"💤 等待 {self.config['check_interval']//3600} 小时后再次检查...")
                time.sleep(self.config['check_interval'])

            except KeyboardInterrupt:
                logger.info("\n👋 监控系统已停止")
                break
            except Exception as e:
                logger.error(f"❌ 监控出错: {e}")
                time.sleep(300)  # 出错后等待5分钟再试

if __name__ == "__main__":
    monitor = FullAStockMonitor()

    # 立即运行一次检查
    logger.info("立即运行首次检查...")

    # 这里可以添加立即检查比亚迪的代码
    stocks = monitor.get_all_a_stocks()
    byd_stock = [s for s in stocks if s['code'] == '002594'][0]

    stock_code, stock_name, report_data, surprises = monitor.check_single_stock_report(
        byd_stock['code'], byd_stock['name']
    )

    if surprises:
        logger.info(f"🎯 比亚迪发现超预期:")
        for metric, actual, expected, ratio in surprises:
            direction = "超出" if ratio > 0 else "低于"
            logger.info(f"   {metric}: {direction}预期 {abs(ratio*100):.1f}%")

    # 开始持续监控
    monitor.run_monitor()
