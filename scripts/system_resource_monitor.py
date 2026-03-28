#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统资源监控脚本
用于监控CPU、内存、磁盘等系统资源使用情况
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from typing import Dict, List, Optional
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemResourceMonitor:
    """系统资源监控器"""
    
    def __init__(self, output_dir: str = "data/system_monitor"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 阈值配置
        self.thresholds = {
            'cpu_usage': 80.0,      # CPU使用率阈值（%）
            'memory_usage': 85.0,   # 内存使用率阈值（%）
            'disk_usage': 90.0,     # 磁盘使用率阈值（%）
            'process_count': 500,   # 进程数量阈值
            'open_files': 10000,    # 打开文件数阈值
        }
        
        # 报警级别
        self.alert_levels = {
            'critical': 90.0,
            'warning': 80.0,
            'normal': 60.0
        }
        
        logger.info("系统资源监控器初始化完成")
    
    def check_all_resources(self) -> Dict:
        """检查所有系统资源"""
        logger.info("开始系统资源检查")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'normal',
            'alerts': [],
            'warnings': [],
            'details': {}
        }
        
        # 1. 检查CPU使用率
        cpu_info = self._check_cpu_usage()
        results['details']['cpu'] = cpu_info
        self._add_alert_if_needed(results, 'cpu', cpu_info['usage_percent'])
        
        # 2. 检查内存使用情况
        memory_info = self._check_memory_usage()
        results['details']['memory'] = memory_info
        self._add_alert_if_needed(results, 'memory', memory_info['usage_percent'])
        
        # 3. 检查磁盘使用情况
        disk_info = self._check_disk_usage()
        results['details']['disk'] = disk_info
        self._add_alert_if_needed(results, 'disk', disk_info['usage_percent'])
        
        # 4. 检查进程情况
        process_info = self._check_processes()
        results['details']['processes'] = process_info
        self._add_alert_if_needed(results, 'processes', process_info['count_percent'])
        
        # 5. 检查OpenClaw进程
        openclaw_info = self._check_openclaw_processes()
        results['details']['openclaw'] = openclaw_info
        
        # 6. 检查网络连接
        network_info = self._check_network_connections()
        results['details']['network'] = network_info
        
        # 7. 检查系统负载
        load_info = self._check_system_load()
        results['details']['load'] = load_info
        
        # 确定总体状态
        results['overall_status'] = self._determine_overall_status(results)
        
        # 保存检查结果
        self._save_check_result(results)
        
        # 生成摘要报告
        summary = self._generate_summary(results)
        results['summary'] = summary
        
        logger.info(f"系统资源检查完成，总体状态: {results['overall_status']}")
        
        return results
    
    def _check_cpu_usage(self) -> Dict:
        """检查CPU使用率"""
        try:
            # macOS使用top命令获取CPU使用率
            cmd = "top -l 1 | grep 'CPU usage'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            cpu_info = {
                'usage_percent': 0.0,
                'user_percent': 0.0,
                'system_percent': 0.0,
                'idle_percent': 0.0,
                'status': 'unknown'
            }
            
            if result.returncode == 0:
                output = result.stdout.strip()
                # 解析类似 "CPU usage: 5.0% user, 2.0% sys, 93.0% idle" 的输出
                import re
                patterns = [
                    r'user\s*([\d.]+)%',
                    r'sys\s*([\d.]+)%',
                    r'idle\s*([\d.]+)%'
                ]
                
                user_match = re.search(patterns[0], output)
                sys_match = re.search(patterns[1], output)
                idle_match = re.search(patterns[2], output)
                
                if user_match and sys_match:
                    user_percent = float(user_match.group(1))
                    sys_percent = float(sys_match.group(1))
                    cpu_info['user_percent'] = user_percent
                    cpu_info['system_percent'] = sys_percent
                    cpu_info['usage_percent'] = user_percent + sys_percent
                    
                    if idle_match:
                        cpu_info['idle_percent'] = float(idle_match.group(1))
            
            # 确定状态
            if cpu_info['usage_percent'] >= self.thresholds['cpu_usage']:
                cpu_info['status'] = 'critical'
            elif cpu_info['usage_percent'] >= self.alert_levels['warning']:
                cpu_info['status'] = 'warning'
            else:
                cpu_info['status'] = 'normal'
            
            return cpu_info
            
        except Exception as e:
            logger.error(f"检查CPU使用率失败: {e}")
            return {
                'usage_percent': 0.0,
                'status': 'error',
                'error': str(e)
            }
    
    def _check_memory_usage(self) -> Dict:
        """检查内存使用情况"""
        try:
            # macOS使用vm_stat获取内存信息
            cmd = "vm_stat"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            memory_info = {
                'total_mb': 0,
                'used_mb': 0,
                'free_mb': 0,
                'usage_percent': 0.0,
                'status': 'unknown'
            }
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                stats = {}
                
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().replace('.', '')
                        value = value.strip().replace('.', '')
                        stats[key] = int(value) if value.isdigit() else 0
                
                # 计算内存使用情况（简化计算）
                page_size = 16384  # 16KB
                
                if 'Pagesfree' in stats and 'Pagesactive' in stats and 'Pageswireddown' in stats:
                    free_pages = stats.get('Pagesfree', 0)
                    active_pages = stats.get('Pagesactive', 0)
                    wired_pages = stats.get('Pageswireddown', 0)
                    speculative_pages = stats.get('Pagesspeculative', 0)
                    
                    total_pages = free_pages + active_pages + wired_pages + speculative_pages
                    
                    memory_info['total_mb'] = total_pages * page_size / 1024 / 1024
                    memory_info['free_mb'] = free_pages * page_size / 1024 / 1024
                    memory_info['used_mb'] = memory_info['total_mb'] - memory_info['free_mb']
                    
                    if memory_info['total_mb'] > 0:
                        memory_info['usage_percent'] = (memory_info['used_mb'] / memory_info['total_mb']) * 100
            
            # 确定状态
            if memory_info['usage_percent'] >= self.thresholds['memory_usage']:
                memory_info['status'] = 'critical'
            elif memory_info['usage_percent'] >= self.alert_levels['warning']:
                memory_info['status'] = 'warning'
            else:
                memory_info['status'] = 'normal'
            
            return memory_info
            
        except Exception as e:
            logger.error(f"检查内存使用情况失败: {e}")
            return {
                'usage_percent': 0.0,
                'status': 'error',
                'error': str(e)
            }
    
    def _check_disk_usage(self) -> Dict:
        """检查磁盘使用情况"""
        try:
            # 使用df命令获取磁盘信息
            cmd = "df -h /"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            disk_info = {
                'total_gb': 0,
                'used_gb': 0,
                'free_gb': 0,
                'usage_percent': 0.0,
                'status': 'unknown'
            }
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 2:
                    # 解析第二行（第一行是标题）
                    parts = lines[1].split()
                    if len(parts) >= 5:
                        # 解析类似 "926Gi 11Gi 124Gi 9%" 的输出
                        total_str = parts[1]
                        used_str = parts[2]
                        free_str = parts[3]
                        usage_str = parts[4].replace('%', '')
                        
                        # 转换单位
                        def parse_size(size_str):
                            if 'Gi' in size_str:
                                return float(size_str.replace('Gi', ''))
                            elif 'Ti' in size_str:
                                return float(size_str.replace('Ti', '')) * 1024
                            elif 'Mi' in size_str:
                                return float(size_str.replace('Mi', '')) / 1024
                            else:
                                return 0.0
                        
                        disk_info['total_gb'] = parse_size(total_str)
                        disk_info['used_gb'] = parse_size(used_str)
                        disk_info['free_gb'] = parse_size(free_str)
                        disk_info['usage_percent'] = float(usage_str)
            
            # 确定状态
            if disk_info['usage_percent'] >= self.thresholds['disk_usage']:
                disk_info['status'] = 'critical'
            elif disk_info['usage_percent'] >= self.alert_levels['warning']:
                disk_info['status'] = 'warning'
            else:
                disk_info['status'] = 'normal'
            
            return disk_info
            
        except Exception as e:
            logger.error(f"检查磁盘使用情况失败: {e}")
            return {
                'usage_percent': 0.0,
                'status': 'error',
                'error': str(e)
            }
    
    def _check_processes(self) -> Dict:
        """检查进程情况"""
        try:
            # 使用ps命令获取进程数量
            cmd = "ps aux | wc -l"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            process_info = {
                'count': 0,
                'count_percent': 0.0,
                'status': 'unknown'
            }
            
            if result.returncode == 0:
                count = int(result.stdout.strip())
                process_info['count'] = count
                
                # 计算相对于阈值的百分比
                if self.thresholds['process_count'] > 0:
                    process_info['count_percent'] = (count / self.thresholds['process_count']) * 100
            
            # 确定状态
            if process_info['count_percent'] >= 100:
                process_info['status'] = 'critical'
            elif process_info['count_percent'] >= 80:
                process_info['status'] = 'warning'
            else:
                process_info['status'] = 'normal'
            
            return process_info
            
        except Exception as e:
            logger.error(f"检查进程情况失败: {e}")
            return {
                'count': 0,
                'count_percent': 0.0,
                'status': 'error',
                'error': str(e)
            }
    
    def _check_openclaw_processes(self) -> Dict:
        """检查OpenClaw进程"""
        try:
            cmd = "ps aux | grep -E '(openclaw|node.*openclaw)' | grep -v grep"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            openclaw_info = {
                'process_count': 0,
                'processes': [],
                'total_cpu_percent': 0.0,
                'total_memory_mb': 0.0,
                'status': 'unknown'
            }
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if lines and lines[0]:
                    openclaw_info['process_count'] = len(lines)
                    
                    for line in lines:
                        parts = line.split()
                        if len(parts) >= 10:
                            process = {
                                'pid': parts[1],
                                'cpu_percent': float(parts[2]),
                                'memory_mb': float(parts[5]) / 1024,  # 转换为MB
                                'command': ' '.join(parts[10:])
                            }
                            openclaw_info['processes'].append(process)
                            openclaw_info['total_cpu_percent'] += process['cpu_percent']
                            openclaw_info['total_memory_mb'] += process['memory_mb']
            
            # 确定状态
            if openclaw_info['process_count'] == 0:
                openclaw_info['status'] = 'error'
            elif openclaw_info['total_cpu_percent'] > 50:
                openclaw_info['status'] = 'warning'
            else:
                openclaw_info['status'] = 'normal'
            
            return openclaw_info
            
        except Exception as e:
            logger.error(f"检查OpenClaw进程失败: {e}")
            return {
                'process_count': 0,
                'status': 'error',
                'error': str(e)
            }
    
    def _check_network_connections(self) -> Dict:
        """检查网络连接"""
        try:
            cmd = "netstat -an | grep ESTABLISHED | wc -l"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            network_info = {
                'established_connections': 0,
                'status': 'unknown'
            }
            
            if result.returncode == 0:
                network_info['established_connections'] = int(result.stdout.strip())
            
            # 确定状态
            if network_info['established_connections'] > 1000:
                network_info['status'] = 'warning'
            else:
                network_info['status'] = 'normal'
            
            return network_info
            
        except Exception as e:
            logger.error(f"检查网络连接失败: {e}")
            return {
                'established_connections': 0,
                'status': 'error',
                'error': str(e)
            }
    
    def _check_system_load(self) -> Dict:
        """检查系统负载"""
        try:
            cmd = "sysctl -n vm.loadavg"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            load_info = {
                'load_1min': 0.0,
                'load_5min': 0.0,
                'load_15min': 0.0,
                'status': 'unknown'
            }
            
            if result.returncode == 0:
                # 解析类似 "{ 1.23 0.98 0.76 }" 的输出
                import re
                numbers = re.findall(r'[\d.]+', result.stdout)
                if len(numbers) >= 3:
                    load_info['load_1min'] = float(numbers[0])
                    load_info['load_5min'] = float(numbers[1])
                    load_info['load_15min'] = float(numbers[2])
            
            # 确定状态（基于1分钟负载）
            cpu_count = os.cpu_count() or 4
            load_per_cpu = load_info['load_1min'] / cpu_count
            
            if load_per_cpu > 2.0:
                load_info['status'] = 'critical'
            elif load_per_cpu > 1.0:
                load_info['status'] = 'warning'
            else:
                load_info['status'] = 'normal'
            
            return load_info
            
        except Exception as e:
            logger.error(f"检查系统负载失败: {e}")
            return {
                'load_1min': 0.0,
                'status': 'error',
                'error': str(e)
            }
    
    def _add_alert_if_needed(self, results: Dict, resource_type: str, usage_percent: float):
        """根据需要添加报警"""
        if usage_percent >= self.thresholds.get(f'{resource_type}_usage', 90.0):
            results['alerts'].append({
                'resource': resource_type,
                'usage_percent': usage_percent,
                'threshold': self.thresholds.get(f'{resource_type}_usage', 90.0),
                'level': 'critical',
                'message': f'{resource_type}使用率过高: {usage_percent:.1f}%'
            })
        elif usage_percent >= self.alert_levels['warning']:
            results['warnings'].append({
                'resource': resource_type,
                'usage_percent': usage_percent,
                'threshold': self.alert_levels['warning'],
                'level': 'warning',
                'message': f'{resource_type}使用率较高: {usage_percent:.1f}%'
            })
    
    def _determine_overall_status(self, results: Dict) -> str:
        """确定总体状态"""
        if results['alerts']:
            return 'critical'
        elif results['warnings']:
            return 'warning'
        else:
            return 'normal'
    
    def _save_check_result(self, results: Dict):
        """保存检查结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"system_check_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.debug(f"系统检查结果已保存: {filepath}")
        
        # 同时保存到每日汇总文件
        daily_file = f"daily_summary_{datetime.now().strftime('%Y%m%d')}.json"
        daily_path = os.path.join(self.output_dir, daily_file)
        
        daily_data = {}
        if os.path.exists(daily_path):
            with open(daily_path, 'r', encoding='utf-8') as f:
                daily_data = json.load(f)
        
        if 'checks' not in daily_data:
            daily_data['checks'] = []
        
        daily_data['checks'].append({
            'timestamp': results['timestamp'],
            'overall_status': results['overall_status'],
            'alert_count': len(results['alerts']),
            'warning_count': len(results['warnings'])
        })
        
        with open(daily_path, 'w', encoding='utf-8') as f:
            json.dump(daily_data, f, ensure_ascii=False, indent=2)
    
    def _generate_summary(self, results: Dict) -> Dict:
        """生成摘要报告"""
        summary = {
            'timestamp': results['timestamp'],
            'overall_status': results['overall_status'],
            'resource_status': {},
            'key_metrics': {},
            'recommendations': []
        }
        
        # 资源状态
        for resource, info in results['details'].items():
            if isinstance(info, dict) and 'status' in info:
                summary['resource_status'][resource] = info['status']
        
        # 关键指标
        cpu_info = results['details'].get('cpu', {})
        memory_info = results['details'].get('memory', {})
        disk_info = results['details'].get('disk', {})
        
        summary['key_metrics'] = {
            'cpu_usage_percent': cpu_info.get('usage_percent', 0),
            'memory_usage_percent': memory_info.get('usage_percent', 0),
            'disk_usage_percent': disk_info.get('usage_percent', 0),
            'process_count': results['details'].get('processes', {}).get('count', 0),
            'established_connections': results['details'].get('network', {}).get('established_connections', 0)
        }
        
        # 生成建议
        if results['overall_status'] == 'critical':
            summary['recommendations'].append("⚠️ 系统状态严重，建议立即检查")
        
        if cpu_info.get('usage_percent', 0) > 80:
            summary['recommendations'].append("💻 CPU使用率较高，建议检查高CPU进程")
        
        if memory_info.get('usage_percent', 0) > 80:
            summary['recommendations'].append("🧠 内存使用率较高，建议检查内存泄漏")
        
        if disk_info.get('usage_percent', 0) > 85:
            summary['recommendations'].append("💾 磁盘空间紧张，建议清理无用文件")
        
        if len(results['alerts']) > 0:
            summary['recommendations'].append(f"🚨 有{len(results['alerts'])}个严重报警需要处理")
        
        if len(results['warnings']) > 0:
            summary['recommendations'].append(f"⚠️ 有{len(results['warnings'])}个警告需要注意")
        
        if not summary['recommendations']:
            summary['recommendations'].append("✅ 系统状态良好，无需特别操作")
        
        return summary
    
    def generate_human_readable_report(self, results: Dict) -> str:
        """生成人类可读的报告"""
        summary = results.get('summary', {})
        
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("系统资源监控报告")
        report_lines.append(f"生成时间: {results['timestamp']}")
        report_lines.append(f"总体状态: {results['overall_status'].upper()}")
        report_lines.append("=" * 60)
        
        # 关键指标
        report_lines.append("\n📊 关键指标:")
        metrics = summary.get('key_metrics', {})
        report_lines.append(f"  CPU使用率: {metrics.get('cpu_usage_percent', 0):.1f}%")
        report_lines.append(f"  内存使用率: {metrics.get('memory_usage_percent', 0):.1f}%")
        report_lines.append(f"  磁盘使用率: {metrics.get('disk_usage_percent', 0):.1f}%")
        report_lines.append(f"  进程数量: {metrics.get('process_count', 0)}")
        report_lines.append(f"  网络连接数: {metrics.get('established_connections', 0)}")
        
        # 资源状态
        report_lines.append("\n🔧 资源状态:")
        for resource, status in summary.get('resource_status', {}).items():
            emoji = "✅" if status == 'normal' else "⚠️" if status == 'warning' else "🚨"
            report_lines.append(f"  {emoji} {resource}: {status}")
        
        # OpenClaw进程信息
        openclaw_info = results['details'].get('openclaw', {})
        if openclaw_info.get('process_count', 0) > 0:
            report_lines.append(f"\n🤖 OpenClaw进程: {openclaw_info['process_count']}个")
            report_lines.append(f"  总CPU使用: {openclaw_info.get('total_cpu_percent', 0):.1f}%")
            report_lines.append(f"  总内存使用: {openclaw_info.get('total_memory_mb', 0):.1f} MB")
        
        # 报警和警告
        if results.get('alerts'):
            report_lines.append(f"\n🚨 严重报警 ({len(results['alerts'])}个):")
            for alert in results['alerts'][:3]:  # 只显示前3个
                report_lines.append(f"  • {alert['message']}")
        
        if results.get('warnings'):
            report_lines.append(f"\n⚠️ 警告 ({len(results['warnings'])}个):")
            for warning in results['warnings'][:3]:  # 只显示前3个
                report_lines.append(f"  • {warning['message']}")
        
        # 建议
        report_lines.append("\n💡 建议:")
        for rec in summary.get('recommendations', []):
            report_lines.append(f"  {rec}")
        
        report_lines.append("\n" + "=" * 60)
        
        return '\n'.join(report_lines)


def main():
    """主函数"""
    print("系统资源监控器启动...")
    
    monitor = SystemResourceMonitor()
    
    try:
        # 执行系统检查
        results = monitor.check_all_resources()
        
        # 生成并显示报告
        report = monitor.generate_human_readable_report(results)
        print(report)
        
        # 根据状态决定退出码
        if results['overall_status'] == 'critical':
            sys.exit(1)
        elif results['overall_status'] == 'warning':
            sys.exit(2)
        else:
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"系统检查失败: {e}")
        print(f"❌ 系统检查失败: {e}")
        sys.exit(3)


if __name__ == "__main__":
    main()