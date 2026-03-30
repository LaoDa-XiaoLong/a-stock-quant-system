#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财报监控日报任务执行脚本 - V3.0版
完整执行：1. 获取最新财报数据 2. 生成分层版日报 3. 发送报告到A股数据分析群
"""

import os
import sys
import time
from datetime import datetime
import subprocess
import logging
from typing import Dict

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/financial_daily_v3.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FinancialDailyTaskV3:
    """财报监控日报任务V3.0版"""
    
    def __init__(self):
        self.workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.task_start_time = datetime.now()
        
        logger.info("=" * 60)
        logger.info("财报监控日报任务V3.0版启动")
        logger.info(f"开始时间: {self.task_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"工作目录: {self.workspace_dir}")
        logger.info("=" * 60)
    
    def run_step(self, step_name: str, command: str) -> bool:
        """运行单个步骤"""
        logger.info(f"▶️ 开始步骤: {step_name}")
        logger.info(f"   命令: {command}")
        
        start_time = time.time()
        
        try:
            # 切换到工作目录
            original_dir = os.getcwd()
            os.chdir(self.workspace_dir)
            
            # 执行命令
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            
            stdout, stderr = process.communicate()
            elapsed_time = time.time() - start_time
            
            # 切换回原目录
            os.chdir(original_dir)
            
            if process.returncode == 0:
                logger.info(f"✅ 步骤完成: {step_name} ({elapsed_time:.1f}秒)")
                
                # 输出摘要（最多5行）
                lines = stdout.strip().split('\n')
                if lines and lines[0]:
                    logger.info("   输出摘要:")
                    for line in lines[:5]:
                        if line.strip():
                            logger.info(f"      {line.strip()}")
                
                return True
            else:
                logger.error(f"❌ 步骤失败: {step_name}")
                logger.error(f"   退出码: {process.returncode}")
                if stderr.strip():
                    logger.error(f"   错误输出: {stderr.strip()}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 步骤异常: {step_name}")
            logger.error(f"   异常信息: {e}")
            return False
    
    def collect_task_info(self) -> Dict:
        """收集任务执行信息"""
        # 检查数据库文件
        db_path = os.path.join(self.workspace_dir, 'data/final_financial_complete/final_reports_complete.db')
        if not os.path.exists(db_path):
            return {}
        
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 获取今日数据
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
            SELECT date, total_stocks, valid_stocks, holdings_surprises, all_surprises,
                   data_quality_score, trading_advice
            FROM final_monitor_complete
            WHERE date = ?
            ORDER BY date DESC
            LIMIT 1
            ''', (today,))
            
            row = cursor.fetchone()
            if not row:
                # 获取最近的数据
                cursor.execute('''
                SELECT date, total_stocks, valid_stocks, holdings_surprises, all_surprises,
                       data_quality_score, trading_advice
                FROM final_monitor_complete
                ORDER BY date DESC
                LIMIT 1
                ''')
                row = cursor.fetchone()
            
            conn.close()
            
            if row:
                return {
                    'date': row[0],
                    'total_stocks': row[1],
                    'valid_stocks': row[2],
                    'holdings_surprises': row[3],
                    'all_surprises': row[4],
                    'data_quality_score': row[5],
                    'trading_advice': row[6]
                }
            
        except Exception as e:
            logger.warning(f"收集任务信息失败: {e}")
        
        return {}
    
    def save_task_history(self, success: bool, task_info: Dict):
        """保存任务历史记录"""
        try:
            import json
            history_dir = os.path.join(self.workspace_dir, 'logs/task_history')
            os.makedirs(history_dir, exist_ok=True)
            
            history_file = os.path.join(
                history_dir,
                f"task_v3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            task_record = {
                'task_name': '财报监控日报V3.0版',
                'start_time': self.task_start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'end_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'success': success,
                'task_info': task_info,
                'version': '3.0'
            }
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(task_record, f, ensure_ascii=False, indent=2)
            
            logger.info(f"📝 任务日志已保存: {history_file}")
            
        except Exception as e:
            logger.warning(f"保存任务历史失败: {e}")
    
    def run(self) -> bool:
        """运行完整任务"""
        logger.info("🚀 开始执行完整财报监控日报任务V3.0版")
        logger.info("=" * 60)
        
        # 步骤1: 获取最新财报数据
        step1_success = self.run_step(
            "获取最新财报数据",
            "python3 scripts/final_financial_monitor_complete.py"
        )
        
        if not step1_success:
            logger.error("❌ 步骤1失败，任务终止")
            return False
        
        # 步骤2: 生成分层版日报并发送到飞书
        step2_success = self.run_step(
            "生成分层版日报并发送到飞书",
            "python3 scripts/send_financial_report_fixed.py"
        )
        
        if not step2_success:
            logger.error("❌ 步骤2失败，任务终止")
            return False
        
        # 收集任务信息
        task_info = self.collect_task_info()
        
        # 保存任务历史
        self.save_task_history(True, task_info)
        
        # 任务完成
        task_end_time = datetime.now()
        elapsed_seconds = (task_end_time - self.task_start_time).total_seconds()
        
        logger.info("=" * 60)
        logger.info("财报监控日报任务V3.0版完成")
        logger.info("=" * 60)
        logger.info("✅ 任务状态: 成功")
        logger.info(f"⏰ 开始时间: {self.task_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"⏰ 结束时间: {task_end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"⏱️  总耗时: {elapsed_seconds:.1f}秒")
        
        if task_info:
            logger.info("📊 报告关键信息:")
            logger.info(f"   - 分析股票总数: {task_info.get('total_stocks', 0)} 只")
            logger.info(f"   - 超预期股票: {task_info.get('all_surprises', 0)} 只")
            if task_info.get('total_stocks', 0) > 0:
                surprise_rate = task_info.get('all_surprises', 0) / task_info['total_stocks'] * 100
                logger.info(f"   - 超预期比例: {surprise_rate:.1f}%")
            logger.info(f"   - 持仓超预期: {task_info.get('holdings_surprises', 0)} 只")
            logger.info(f"   - 数据质量分数: {task_info.get('data_quality_score', 0):.1f} 分")
        
        logger.info("=" * 60)
        
        return True


def main():
    """主函数"""
    print("📈 财报监控日报任务执行系统 - V3.0版")
    print("=" * 60)
    print("任务流程:")
    print("1. 📊 获取最新财报数据")
    print("2. 📝 生成分层版日报")
    print("3. 📤 发送报告到A股数据分析群")
    print("=" * 60)
    
    # 创建任务实例
    task = FinancialDailyTaskV3()
    
    # 执行任务
    success = task.run()
    
    # 输出结果
    if success:
        print("✅ 财报监控日报任务V3.0版执行成功")
        print("🎉 报告已发送到A股数据分析群")
        return 0
    else:
        print("❌ 财报监控日报任务V3.0版执行失败")
        print("🔍 请查看日志文件排查问题")
        return 1


if __name__ == "__main__":
    sys.exit(main())