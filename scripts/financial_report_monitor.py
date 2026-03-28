#!/usr/bin/env python3
"""
A股持仓股票财报监控系统
监控比亚迪等持仓公司的年报、季报发布情况
"""

import time
import requests
import pandas as pd
from datetime import datetime, timedelta
import logging
import os
import json

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/financial_report.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 持仓股票列表
HOLDINGS = [
    {'code': '603728', 'name': '鸣志电器'},
    {'code': '002594', 'name': '比亚迪'},  # 重点关注
    {'code': '600580', 'name': '卧龙电驱'},
    {'code': '600183', 'name': '生益科技'},
    {'code': '603259', 'name': '药明康德'},
    {'code': '002352', 'name': '顺丰控股'},
    {'code': '600096', 'name': '云天化'},
]

# A股财报披露时间规定
REPORT_SCHEDULE = {
    'annual': {'start': '01-01', 'end': '04-30'},      # 年报：1月1日-4月30日
    'midterm': {'start': '07-01', 'end': '08-30'},     # 中报：7月1日-8月30日
    'q1': {'start': '04-01', 'end': '04-30'},          # 一季报：4月1日-4月30日
    'q3': {'start': '10-01', 'end': '10-31'},          # 三季报：10月1日-10月31日
}

class FinancialReportMonitor:
    def __init__(self):
        self.data_dir = 'data/financial_reports'
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # 比亚迪2025年年报预计发布时间
        self.byd_annual_expected = '2026-03-27'  # 根据moomoo预测
        
    def check_byd_annual_report(self):
        """检查比亚迪年报是否已发布"""
        logger.info("🔍 检查比亚迪2025年年报发布状态")
        
        today = datetime.now().strftime('%Y-%m-%d')
        expected_date = self.byd_annual_expected
        
        if today == expected_date:
            logger.info(f"📅 今天是比亚迪年报预计发布日: {today}")
            return self.fetch_byd_report()
        elif today > expected_date:
            logger.info(f"⏰ 已过比亚迪年报预计发布日: {expected_date}")
            return self.fetch_byd_report()
        else:
            days_left = (datetime.strptime(expected_date, '%Y-%m-%d') - datetime.now()).days
            logger.info(f"⏳ 距离比亚迪年报预计发布还有 {days_left} 天")
            return None
    
    def fetch_byd_report(self):
        """尝试获取比亚迪年报数据"""
        try:
            # 尝试从东方财富获取比亚迪最新公告
            url = f"http://data.eastmoney.com/notices/getdata.ashx"
            params = {
                'StockCode': '002594',
                'CodeType': '1',
                'PageIndex': '1',
                'PageSize': '10'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ 成功获取比亚迪公告数据，共{len(data)}条")
                
                # 查找年报相关公告
                annual_reports = []
                for item in data:
                    if '年报' in item.get('NOTICETITLE', ''):
                        annual_reports.append({
                            'title': item.get('NOTICETITLE'),
                            'date': item.get('NOTICEDATE'),
                            'url': item.get('Url')
                        })
                
                if annual_reports:
                    latest = annual_reports[0]
                    logger.info(f"🎉 发现比亚迪年报: {latest['title']} ({latest['date']})")
                    return latest
                else:
                    logger.info("ℹ️  未找到比亚迪年报公告")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ 获取比亚迪公告失败: {e}")
        
        return None
    
    def get_report_schedule(self):
        """获取当前财报季的时间表"""
        today = datetime.now()
        current_year = today.year
        
        schedule = []
        
        # 检查各报告期
        for report_type, dates in REPORT_SCHEDULE.items():
            start_date = datetime.strptime(f"{current_year}-{dates['start']}", '%Y-%m-%d')
            end_date = datetime.strptime(f"{current_year}-{dates['end']}", '%Y-%m-%d')
            
            if start_date <= today <= end_date:
                status = "进行中"
            elif today < start_date:
                days = (start_date - today).days
                status = f"还有{days}天开始"
            else:
                status = "已结束"
            
            schedule.append({
                '报告类型': report_type,
                '开始时间': start_date.strftime('%Y-%m-%d'),
                '结束时间': end_date.strftime('%Y-%m-%d'),
                '状态': status
            })
        
        return schedule
    
    def monitor_all_holdings(self):
        """监控所有持仓股票的财报情况"""
        logger.info("=" * 60)
        logger.info("📊 A股持仓股票财报监控系统启动")
        logger.info(f"📅 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        # 检查比亚迪年报
        byd_report = self.check_byd_annual_report()
        
        if byd_report:
            logger.info("🚨 比亚迪年报相关发现:")
            logger.info(f"   标题: {byd_report['title']}")
            logger.info(f"   日期: {byd_report['date']}")
            logger.info(f"   链接: {byd_report['url']}")
            
            # 保存发现
            self.save_finding(byd_report)
            
            # 这里可以添加自动解读逻辑
            self.analyze_byd_report(byd_report)
        
        # 显示当前财报季时间表
        schedule = self.get_report_schedule()
        logger.info("\n📅 当前财报季时间表:")
        for item in schedule:
            logger.info(f"   {item['报告类型']}: {item['开始时间']} 至 {item['结束时间']} ({item['状态']})")
    
    def save_finding(self, report_data):
        """保存发现的重要财报信息"""
        file_path = f"{self.data_dir}/findings_{datetime.now().strftime('%Y%m%d')}.json"
        
        findings = []
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                findings = json.load(f)
        
        findings.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'stock': '比亚迪(002594)',
            'data': report_data
        })
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(findings, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 发现已保存到: {file_path}")
    
    def analyze_byd_report(self, report_data):
        """比亚迪财报分析框架（待完善）"""
        logger.info("\n🧠 比亚迪财报分析要点:")
        logger.info("1. 营收增长: 关注同比增速，是否超预期")
        logger.info("2. 净利润: 关注盈利能力和成本控制")
        logger.info("3. 毛利率: 反映产品竞争力和定价能力")
        logger.info("4. 研发投入: 技术领先性的重要指标")
        logger.info("5. 海外业务: 增长引擎和国际化进展")
        logger.info("6. 现金流: 企业经营健康状况")
        logger.info("7. 未来展望: 管理层对行业的判断")
        
        # 这里可以添加具体的分析逻辑
        # 例如：对比历史数据、行业平均、券商预测等
    
    def run_daily_monitor(self):
        """每日监控主循环"""
        logger.info("🚀 开始每日财报监控")
        
        while True:
            try:
                self.monitor_all_holdings()
                
                # 每天检查一次（实际可以根据需要调整频率）
                logger.info(f"\n⏰ 下次检查时间: 24小时后")
                time.sleep(86400)  # 24小时
                
            except KeyboardInterrupt:
                logger.info("\n👋 监控系统已停止")
                break
            except Exception as e:
                logger.error(f"❌ 监控出错: {e}")
                time.sleep(3600)  # 出错后等待1小时再试

if __name__ == "__main__":
    monitor = FinancialReportMonitor()
    
    # 立即运行一次检查
    monitor.monitor_all_holdings()
    
    # 如果要持续监控，取消下面这行的注释
    # monitor.run_daily_monitor()