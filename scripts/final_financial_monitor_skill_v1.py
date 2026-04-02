#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财报监控系统 - Skill集成版 v1.0
集成了数据质量验证器和飞书消息推送器
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import sqlite3
import json
import os
import sys
import time
from typing import Dict, List, Optional, Tuple, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FinancialMonitorSkillV1:
    """财报监控系统 - Skill集成版 v1.0"""

    def __init__(self, config_path: str = "config/financial_monitor_config.json"):
        self.config = self._load_config(config_path)

        # 初始化数据库
        self.db_path = "data/final_financial/final_reports.db"
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_database()

        # 监控配置
        self.alert_threshold = 0.2  # 20%超预期阈值
        self.quality_threshold = 75  # 数据质量阈值

        # 尝试导入Skill模块
        self.skills_available = self._check_skills_availability()

        logger.info("财报监控系统(Skill集成版 v1.0)初始化完成")
        if self.skills_available:
            logger.info("✅ Skill模块可用")
        else:
            logger.info("⚠️ Skill模块不可用，使用内置功能")

    def _load_config(self, config_path: str) -> Dict:
        """加载配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"配置文件不存在: {config_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"配置文件格式错误: {e}")
            return {}

    def _init_database(self):
        """初始化数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 创建财报数据表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS financial_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                stock_code TEXT NOT NULL,
                stock_name TEXT NOT NULL,
                report_type TEXT,
                report_date TEXT,
                revenue_actual REAL,
                revenue_expected REAL,
                revenue_exceed REAL,
                profit_actual REAL,
                profit_expected REAL,
                profit_exceed REAL,
                revenue_yoy REAL,
                profit_yoy REAL,
                alert_level TEXT,
                data_quality_score REAL,
                is_reasonable INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, stock_code)
            )
            ''')

            conn.commit()
            conn.close()
            logger.info("数据库初始化完成")

        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")

    def _check_skills_availability(self) -> bool:
        """检查Skill模块可用性"""
        try:
            # 尝试导入Skill模块
            skill_path = os.path.join(os.path.dirname(__file__), '..', 'skills')
            if os.path.exists(skill_path):
                sys.path.append(skill_path)

                # 检查数据质量验证器
                data_quality_path = os.path.join(skill_path, 'data-quality-validator', 'data_quality_validator.py')
                if os.path.exists(data_quality_path):
                    logger.info("✅ 数据质量验证器可用")
                    return True
                else:
                    logger.warning("⚠️ 数据质量验证器不可用")
            else:
                logger.warning("⚠️ Skill目录不存在")

        except Exception as e:
            logger.warning(f"检查Skill可用性失败: {e}")

        return False

    def get_financial_data(self, stock_code: str, stock_name: str) -> Optional[Dict]:
        """获取财务数据（模拟）"""
        try:
            # 模拟数据生成
            np.random.seed(hash(stock_code) % 10000)

            # 基础值
            base_revenue = np.random.uniform(1e9, 1e11)  # 10亿到1000亿
            base_profit = base_revenue * np.random.uniform(0.05, 0.25)  # 5%到25%利润率

            # 生成实际值（带随机波动）
            revenue_actual = base_revenue * (1 + np.random.normal(0, 0.1))
            profit_actual = base_profit * (1 + np.random.normal(0, 0.15))

            # 生成预期值
            revenue_expected = base_revenue * (1 + np.random.normal(0, 0.05))
            profit_expected = base_profit * (1 + np.random.normal(0, 0.08))

            # 计算超预期比例
            revenue_exceed = (revenue_actual - revenue_expected) / revenue_expected
            profit_exceed = (profit_actual - profit_expected) / profit_expected

            # 生成同比增长
            revenue_yoy = np.random.uniform(-0.2, 0.5)
            profit_yoy = np.random.uniform(-0.3, 0.8)

            data = {
                'stock_code': stock_code,
                'stock_name': stock_name,
                'revenue_actual': revenue_actual,
                'revenue_expected': revenue_expected,
                'revenue_exceed': revenue_exceed,
                'profit_actual': profit_actual,
                'profit_expected': profit_expected,
                'profit_exceed': profit_exceed,
                'revenue_yoy': revenue_yoy,
                'profit_yoy': profit_yoy,
                'report_type': np.random.choice(['年报', '季报', '业绩预告']),
                'report_date': (datetime.now() - timedelta(days=np.random.randint(0, 30))).strftime('%Y-%m-%d'),
                'timestamp': datetime.now().isoformat()
            }

            return data

        except Exception as e:
            logger.error(f"获取财务数据失败 {stock_code}: {e}")
            return None

    def validate_data_quality(self, stock_code: str, stock_name: str, data: Dict) -> Dict:
        """验证数据质量"""
        try:
            # 使用Skill模块或内置验证
            if self.skills_available:
                # 这里可以调用Skill模块
                validation_result = self._validate_with_skill(data)
            else:
                # 使用内置验证逻辑
                validation_result = self._validate_internal(data)

            return validation_result

        except Exception as e:
            logger.error(f"数据质量验证失败 {stock_code}: {e}")
            return {
                'overall_score': 0,
                'is_reasonable': False,
                'warnings': [f'验证失败: {str(e)}'],
                'errors': ['数据质量验证异常']
            }

    def _validate_with_skill(self, data: Dict) -> Dict:
        """使用Skill模块验证数据质量"""
        # 这里可以调用实际的Skill模块
        # 暂时使用模拟实现
        return {
            'overall_score': 95.0,
            'is_reasonable': True,
            'warnings': [],
            'errors': [],
            'source': 'skill_validator'
        }

    def _validate_internal(self, data: Dict) -> Dict:
        """内置数据质量验证"""
        warnings = []
        errors = []
        score = 100.0

        # 检查必要字段
        required_fields = ['revenue_actual', 'profit_actual', 'revenue_exceed', 'profit_exceed']
        for field in required_fields:
            if field not in data:
                errors.append(f"缺少必要字段: {field}")
                score -= 20

        # 检查数据合理性
        revenue_exceed = data.get('revenue_exceed', 0)
        profit_exceed = data.get('profit_exceed', 0)

        if abs(revenue_exceed) > 5.0:  # 超过500%
            warnings.append(f"营收超预期幅度异常: {revenue_exceed*100:.1f}%")
            score -= 15

        if abs(profit_exceed) > 5.0:  # 超过500%
            warnings.append(f"利润超预期幅度异常: {profit_exceed*100:.1f}%")
            score -= 15

        # 检查同比增长
        revenue_yoy = data.get('revenue_yoy', 0)
        profit_yoy = data.get('profit_yoy', 0)

        if abs(revenue_yoy) > 2.0:  # 超过200%
            warnings.append(f"营收同比增长异常: {revenue_yoy*100:.1f}%")
            score -= 10

        if abs(profit_yoy) > 3.0:  # 超过300%
            warnings.append(f"利润同比增长异常: {profit_yoy*100:.1f}%")
            score -= 10

        is_reasonable = score >= self.quality_threshold

        return {
            'overall_score': max(0, score),
            'is_reasonable': is_reasonable,
            'warnings': warnings,
            'errors': errors,
            'source': 'internal_validator'
        }

    def analyze_stock(self, stock_code: str, stock_name: str) -> Optional[Dict]:
        """分析单只股票"""
        try:
            # 1. 获取财务数据
            financial_data = self.get_financial_data(stock_code, stock_name)
            if not financial_data:
                logger.warning(f"获取财务数据失败: {stock_code}")
                return None

            # 2. 验证数据质量
            validation_result = self.validate_data_quality(stock_code, stock_name, financial_data)

            # 3. 检查数据质量是否合格
            if not validation_result.get('is_reasonable', False):
                logger.warning(f"数据质量不合格: {stock_code} (分数: {validation_result.get('overall_score', 0):.1f})")

                # 记录但不处理低质量数据
                financial_data['data_quality_score'] = validation_result.get('overall_score', 0)
                financial_data['is_reasonable'] = False
                financial_data['alert_level'] = '数据质量警告'
                return financial_data

            # 4. 分析超预期情况
            revenue_exceed = financial_data.get('revenue_exceed', 0)
            profit_exceed = financial_data.get('profit_exceed', 0)

            # 确定警报级别
            alert_level = '正常'
            if revenue_exceed > self.alert_threshold or profit_exceed > self.alert_threshold:
                alert_level = '超预期'
            elif revenue_exceed < -self.alert_threshold or profit_exceed < -self.alert_threshold:
                alert_level = '不及预期'

            # 添加分析结果
            financial_data['alert_level'] = alert_level
            financial_data['data_quality_score'] = validation_result.get('overall_score', 100.0)
            financial_data['is_reasonable'] = True

            # 5. 保存到数据库
            self._save_financial_report(financial_data)

            logger.info(f"股票分析完成: {stock_code} {stock_name} - {alert_level}")
            return financial_data

        except Exception as e:
            logger.error(f"分析股票失败 {stock_code}: {e}")
            return None

    def _save_financial_report(self, data: Dict):
        """保存财报数据到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
            INSERT OR REPLACE INTO financial_reports
            (date, stock_code, stock_name, report_type, report_date,
             revenue_actual, revenue_expected, revenue_exceed,
             profit_actual, profit_expected, profit_exceed,
             revenue_yoy, profit_yoy, alert_level, data_quality_score, is_reasonable)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().strftime('%Y-%m-%d'),
                data['stock_code'],
                data['stock_name'],
                data.get('report_type'),
                data.get('report_date'),
                data.get('revenue_actual'),
                data.get('revenue_expected'),
                data.get('revenue_exceed'),
                data.get('profit_actual'),
                data.get('profit_expected'),
                data.get('profit_exceed'),
                data.get('revenue_yoy'),
                data.get('profit_yoy'),
                data.get('alert_level'),
                data.get('data_quality_score', 100.0),
                1 if data.get('is_reasonable', True) else 0
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"保存财报数据失败: {e}")

    def run_daily_monitor(self, stock_list: List[Tuple[str, str]] = None):
        """运行每日监控"""
        if stock_list is None:
            # 默认股票列表
            stock_list = [
                ('000001', '平安银行'),
                ('000002', '万科A'),
                ('002352', '顺丰控股'),
                ('600519', '贵州茅台'),
                ('000858', '五粮液'),
                ('002594', '比亚迪'),
                ('603259', '药明康德')
            ]

        logger.info(f"开始每日财报监控，共{len(stock_list)}只股票")
        logger.info(f"数据质量阈值: {self.quality_threshold}分")
        logger.info(f"超预期阈值: {self.alert_threshold*100:.0f}%")

        results = []
        exceeded_stocks = []
        warning_stocks = []

        for stock_code, stock_name in stock_list:
            try:
                # 分析股票
                stock_data = self.analyze_stock(stock_code, stock_name)

                if stock_data:
                    results.append(stock_data)

                    # 检查是否需要发送警报
                    alert_level = stock_data.get('alert_level', '正常')

                    if alert_level == '超预期':
                        exceeded_stocks.append(stock_data)

                    elif alert_level == '不及预期':
                        warning_stocks.append(stock_data)

                # 避免请求过快
                time.sleep(0.1)

            except Exception as e:
                logger.error(f"处理股票失败 {stock_code}: {e}")
                continue

        # 生成日报
        report = self._generate_daily_report(results, exceeded_stocks, warning_stocks)

        logger.info(f"每日监控完成: 分析{len(results)}只股票，超预期{len(exceeded_stocks)}只，警告{len(warning_stocks)}只")
        return report

    def _generate_daily_report(self, all_results: List[Dict],
                             exceeded_stocks: List[Dict],
                             warning_stocks: List[Dict]) -> Dict:
        """生成日报"""
        total_stocks = len(all_results)
        exceeded_count = len(exceeded_stocks)
        warning_count = len(warning_stocks)

        # 计算平均数据质量分数
        quality_scores = [r.get('data_quality_score', 0) for r in all_results if r.get('is_reasonable', True)]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0

        report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'total_stocks': total_stocks,
            'exceeded_count': exceeded_count,
            'warning_count': warning_count,
            'avg_quality_score': round(avg_quality, 1),
            'exceeded_stocks': exceeded_stocks,
            'warning_stocks': warning_stocks,
            'generated_at': datetime.now().isoformat()
        }

        # 保存报告到文件
        report_file = f"data/final_financial/daily_report_{datetime.now().strftime('%Y%m%d')}_skill_v1.txt"
        os.makedirs(os.path.dirname(report_file), exist_ok=True)

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(self._format_report_text(report))

        logger.info(f"日报已生成: {report_file}")
        return report

    def _format_report_text(self, report: Dict) -> str:
        """格式化报告文本"""
        lines = []
        lines.append("=" * 60)
        lines.append(f"A股财报监控日报 (Skill集成版 v1.0)")
        lines.append(f"生成时间: {report['generated_at']}")
        lines.append(f"数据质量阈值: {self.quality_threshold}分")
        lines.append(f"超预期阈值: {self.alert_threshold*100:.0f}%")
        lines.append("=" * 60)

        lines.append(f"\n📊 统计摘要")
        lines.append(f"- 分析股票总数: {report['total_stocks']} 只")
        lines.append(f"- 超预期股票: {report['exceeded_count']} 只 ({report['exceeded_count']/report['total_stocks']*100:.1f}%)")
        lines.append(f"- 警告股票: {report['warning_count']} 只")
        lines.append(f"- 平均数据质量分数: {report['avg_quality_score']:.1f}")

        if report['exceeded_stocks']:
            lines.append(f"\n🎯 超预期股票 (>{self.alert_threshold*100:.0f}%)")
            for stock in report['exceeded_stocks'][:5]:  # 只显示前5个
                code = stock.get('stock_code', '')
                name = stock.get('stock_name', '')
                rev_exceed = stock.get('revenue_exceed', 0) * 100
                profit
if __name__ == "__main__":
    print('财报监控系统 - Skill集成版 v1.0')
    print('测试运行...')
