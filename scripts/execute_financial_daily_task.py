#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财报监控日报任务执行脚本
完整执行：1. 获取最新财报数据 2. 生成优化版日报 3. 发送报告到指定渠道
"""

import os
import sys
import time
from datetime import datetime
import subprocess
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/financial_daily_task.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FinancialDailyTask:
    """财报监控日报任务"""
    
    def __init__(self):
        self.workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.task_start_time = datetime.now()
        
        logger.info("=" * 60)
        logger.info("财报监控日报任务启动")
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
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            # 切换回原目录
            os.chdir(original_dir)
            
            elapsed_time = time.time() - start_time
            
            if result.returncode == 0:
                logger.info(f"✅ 步骤完成: {step_name} ({elapsed_time:.1f}秒)")
                
                # 记录输出（前几行）
                output_lines = result.stdout.strip().split('\n')
                if output_lines:
                    logger.info(f"   输出摘要:")
                    for line in output_lines[:5]:  # 只显示前5行
                        if line.strip():
                            logger.info(f"     {line}")
                
                return True
            else:
                logger.error(f"❌ 步骤失败: {step_name}")
                logger.error(f"   退出码: {result.returncode}")
                logger.error(f"   错误输出: {result.stderr[:500]}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 步骤异常: {step_name}")
            logger.error(f"   异常信息: {e}")
            return False
    
    def execute_full_task(self) -> bool:
        """执行完整任务"""
        logger.info("🚀 开始执行完整财报监控日报任务")
        logger.info("=" * 60)
        
        # 步骤1: 获取最新财报数据
        step1_success = self.run_step(
            "获取最新财报数据",
            "python3 scripts/final_financial_monitor_complete.py"
        )
        
        if not step1_success:
            logger.error("❌ 步骤1失败，任务终止")
            return False
        
        # 短暂等待，确保数据保存完成
        time.sleep(2)
        
        # 步骤2: 生成优化版日报并发送
        step2_success = self.run_step(
            "生成优化版日报并发送到飞书",
            "python3 scripts/send_financial_report.py"
        )
        
        if not step2_success:
            logger.error("❌ 步骤2失败，任务终止")
            return False
        
        # 步骤3: 备份报告文件
        step3_success = self.run_step(
            "备份报告文件",
            f"cp -f data/final_financial_complete/daily_report_*.md reports/ 2>/dev/null || echo '无新报告文件'"
        )
        
        # 步骤3不是关键步骤，失败不影响整体任务
        if not step3_success:
            logger.warning("⚠️ 步骤3失败，但不影响主要任务")
        
        return True
    
    def generate_summary(self, success: bool):
        """生成任务摘要"""
        task_end_time = datetime.now()
        duration = (task_end_time - self.task_start_time).total_seconds()
        
        logger.info("=" * 60)
        logger.info("财报监控日报任务完成")
        logger.info("=" * 60)
        
        if success:
            logger.info("✅ 任务状态: 成功")
        else:
            logger.info("❌ 任务状态: 失败")
        
        logger.info(f"⏰ 开始时间: {self.task_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"⏰ 结束时间: {task_end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"⏱️  总耗时: {duration:.1f}秒")
        
        # 生成简要报告
        report_file = f"data/final_financial_complete/daily_report_{self.task_start_time.strftime('%Y%m%d')}.md"
        if os.path.exists(report_file):
            with open(report_file, 'r', encoding='utf-8') as f:
                report_content = f.read()
            
            # 提取关键信息
            lines = report_content.split('\n')
            key_info = []
            
            for line in lines:
                if any(keyword in line for keyword in ['分析股票总数', '超预期股票', '持仓超预期', '总体建议']):
                    key_info.append(line)
                    if len(key_info) >= 4:  # 只取前4个关键信息
                        break
            
            logger.info("📊 报告关键信息:")
            for info in key_info:
                logger.info(f"   {info}")
        
        logger.info("=" * 60)
        
        # 保存任务日志
        self._save_task_log(success, duration)
    
    def _save_task_log(self, success: bool, duration: float):
        """保存任务日志"""
        log_dir = "logs/task_history"
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"task_{self.task_start_time.strftime('%Y%m%d_%H%M%S')}.json")
        
        log_data = {
            'task_name': 'financial_daily_report',
            'start_time': self.task_start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'duration_seconds': duration,
            'success': success,
            'workspace': self.workspace_dir
        }
        
        import json
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📝 任务日志已保存: {log_file}")
    
    def cleanup(self):
        """清理临时文件"""
        logger.info("🧹 执行清理操作...")
        
        # 清理旧的日志文件（保留最近7天）
        try:
            import glob
            import time
            
            log_files = glob.glob("logs/*.log")
            for log_file in log_files:
                file_age = time.time() - os.path.getmtime(log_file)
                if file_age > 7 * 24 * 3600:  # 7天前
                    os.remove(log_file)
                    logger.info(f"   删除旧日志文件: {os.path.basename(log_file)}")
        
        except Exception as e:
            logger.warning(f"   清理日志文件失败: {e}")
        
        logger.info("✅ 清理完成")


def main():
    """主函数"""
    print("📈 财报监控日报任务执行系统")
    print("=" * 60)
    print("任务流程:")
    print("1. 📊 获取最新财报数据")
    print("2. 📝 生成优化版日报")
    print("3. 📤 发送报告到飞书")
    print("=" * 60)
    
    task = FinancialDailyTask()
    
    try:
        # 执行完整任务
        success = task.execute_full_task()
        
        # 生成摘要
        task.generate_summary(success)
        
        # 清理临时文件
        task.cleanup()
        
        if success:
            print("\n🎉 财报监控日报任务执行完成！")
            print("📊 报告已成功发送到飞书")
            print("📝 详细日志请查看: logs/financial_daily_task.log")
        else:
            print("\n❌ 财报监控日报任务执行失败")
            print("🔍 请查看日志文件排查问题")
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"❌ 任务执行异常: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())