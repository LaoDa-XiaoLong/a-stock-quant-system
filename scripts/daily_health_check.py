#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日健康检查脚本
综合检查系统资源、工具使用、项目健康度等
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List
import logging

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DailyHealthChecker:
    """每日健康检查器"""

    def __init__(self, output_dir: str = "data/health_checks"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # 检查项配置
        self.check_items = {
            'system_resources': {
                'name': '系统资源检查',
                'weight': 0.3,
                'description': '检查CPU、内存、磁盘等系统资源使用情况'
            },
            'openclaw_status': {
                'name': 'OpenClaw状态检查',
                'weight': 0.25,
                'description': '检查OpenClaw服务运行状态'
            },
            'project_structure': {
                'name': '项目结构检查',
                'weight': 0.2,
                'description': '检查项目目录结构和文件组织'
            },
            'code_quality': {
                'name': '代码质量检查',
                'weight': 0.15,
                'description': '检查代码质量和规范符合度'
            },
            'tool_usage': {
                'name': '工具使用检查',
                'weight': 0.1,
                'description': '检查工具使用情况和错误统计'
            }
        }

        logger.info("每日健康检查器初始化完成")

    def run_all_checks(self) -> Dict:
        """运行所有检查"""
        logger.info("开始每日健康检查")

        results = {
            'timestamp': datetime.now().isoformat(),
            'overall_score': 0,
            'overall_status': 'unknown',
            'check_results': {},
            'alerts': [],
            'recommendations': []
        }

        total_weight = 0
        weighted_score = 0

        # 运行各项检查
        for check_id, check_config in self.check_items.items():
            logger.info(f"运行检查: {check_config['name']}")

            try:
                check_result = self._run_single_check(check_id)
                results['check_results'][check_id] = check_result

                # 计算加权分数
                weight = check_config['weight']
                score = check_result.get('score', 0)

                total_weight += weight
                weighted_score += score * weight

                # 收集报警和建议
                if check_result.get('alerts'):
                    results['alerts'].extend(check_result['alerts'])

                if check_result.get('recommendations'):
                    results['recommendations'].extend(check_result['recommendations'])

            except Exception as e:
                logger.error(f"检查 {check_id} 失败: {e}")
                results['check_results'][check_id] = {
                    'status': 'error',
                    'score': 0,
                    'error': str(e)
                }

        # 计算总体分数
        if total_weight > 0:
            results['overall_score'] = weighted_score / total_weight

        # 确定总体状态
        results['overall_status'] = self._determine_overall_status(results)

        # 保存检查结果
        self._save_check_results(results)

        # 生成报告
        report = self._generate_report(results)
        results['report'] = report

        logger.info(f"每日健康检查完成，总体分数: {results['overall_score']:.1f}, 状态: {results['overall_status']}")

        return results

    def _run_single_check(self, check_id: str) -> Dict:
        """运行单个检查"""
        if check_id == 'system_resources':
            return self._check_system_resources()
        elif check_id == 'openclaw_status':
            return self._check_openclaw_status()
        elif check_id == 'project_structure':
            return self._check_project_structure()
        elif check_id == 'code_quality':
            return self._check_code_quality()
        elif check_id == 'tool_usage':
            return self._check_tool_usage()
        else:
            return {
                'status': 'skipped',
                'score': 0,
                'message': f'未知检查项: {check_id}'
            }

    def _check_system_resources(self) -> Dict:
        """检查系统资源"""
        try:
            # 导入系统资源监控器
            from system_resource_monitor import SystemResourceMonitor

            monitor = SystemResourceMonitor()
            results = monitor.check_all_resources()

            # 转换为检查结果格式
            score = 100
            if results['overall_status'] == 'critical':
                score = 40
            elif results['overall_status'] == 'warning':
                score = 70

            check_result = {
                'status': results['overall_status'],
                'score': score,
                'details': results['details'],
                'alerts': results.get('alerts', []),
                'recommendations': results.get('summary', {}).get('recommendations', [])
            }

            return check_result

        except Exception as e:
            logger.error(f"系统资源检查失败: {e}")
            return {
                'status': 'error',
                'score': 0,
                'error': str(e)
            }

    def _check_openclaw_status(self) -> Dict:
        """检查OpenClaw状态"""
        try:
            import subprocess

            # 运行openclaw status命令
            cmd = "openclaw status"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            status_info = {
                'command_success': result.returncode == 0,
                'output_length': len(result.stdout),
                'error_length': len(result.stderr)
            }

            # 解析状态信息
            score = 100
            alerts = []
            recommendations = []

            if result.returncode != 0:
                score = 30
                alerts.append({
                    'level': 'critical',
                    'message': 'OpenClaw状态检查命令失败'
                })
                recommendations.append("检查OpenClaw服务是否正常运行")

            # 检查关键信息
            output = result.stdout.lower()

            if 'error' in output:
                score = min(score, 70)
                alerts.append({
                    'level': 'warning',
                    'message': 'OpenClaw状态输出包含错误信息'
                })

            if 'gateway' in output and 'running' in output:
                # 网关运行正常
                pass
            else:
                score = min(score, 60)
                alerts.append({
                    'level': 'warning',
                    'message': 'OpenClaw网关可能未正常运行'
                })
                recommendations.append("检查OpenClaw网关服务状态")

            return {
                'status': 'normal' if score >= 80 else 'warning' if score >= 60 else 'critical',
                'score': score,
                'details': status_info,
                'alerts': alerts,
                'recommendations': recommendations
            }

        except Exception as e:
            logger.error(f"OpenClaw状态检查失败: {e}")
            return {
                'status': 'error',
                'score': 0,
                'error': str(e)
            }

    def _check_project_structure(self) -> Dict:
        """检查项目结构"""
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

            # 检查关键目录是否存在
            required_dirs = [
                'scripts',
                'data',
                'docs',
                'strategies',
                'reports'
            ]

            required_files = [
                'MEMORY.md',
                'USER.md',
                'IDENTITY.md',
                'SOUL.md',
                'AGENTS.md'
            ]

            dir_checks = {}
            file_checks = {}

            # 检查目录
            missing_dirs = []
            for dir_name in required_dirs:
                dir_path = os.path.join(project_root, dir_name)
                exists = os.path.exists(dir_path) and os.path.isdir(dir_path)
                dir_checks[dir_name] = exists
                if not exists:
                    missing_dirs.append(dir_name)

            # 检查文件
            missing_files = []
            for file_name in required_files:
                file_path = os.path.join(project_root, file_name)
                exists = os.path.exists(file_path) and os.path.isfile(file_path)
                file_checks[file_name] = exists
                if not exists:
                    missing_files.append(file_name)

            # 计算分数
            total_items = len(required_dirs) + len(required_files)
            missing_items = len(missing_dirs) + len(missing_files)

            if total_items > 0:
                score = (1 - missing_items / total_items) * 100
            else:
                score = 100

            alerts = []
            recommendations = []

            if missing_dirs:
                alerts.append({
                    'level': 'warning',
                    'message': f'缺少{len(missing_dirs)}个关键目录: {", ".join(missing_dirs)}'
                })
                recommendations.append("创建缺失的项目目录")

            if missing_files:
                alerts.append({
                    'level': 'warning',
                    'message': f'缺少{len(missing_files)}个关键文件: {", ".join(missing_files)}'
                })
                recommendations.append("创建缺失的项目文件")

            return {
                'status': 'normal' if score >= 90 else 'warning' if score >= 70 else 'critical',
                'score': score,
                'details': {
                    'dir_checks': dir_checks,
                    'file_checks': file_checks,
                    'missing_dirs': missing_dirs,
                    'missing_files': missing_files
                },
                'alerts': alerts,
                'recommendations': recommendations
            }

        except Exception as e:
            logger.error(f"项目结构检查失败: {e}")
            return {
                'status': 'error',
                'score': 0,
                'error': str(e)
            }

    def _check_code_quality(self) -> Dict:
        """检查代码质量"""
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            scripts_dir = os.path.join(project_root, 'scripts')

            # 检查Python文件
            python_files = []
            if os.path.exists(scripts_dir):
                for root, dirs, files in os.walk(scripts_dir):
                    for file in files:
                        if file.endswith('.py'):
                            python_files.append(os.path.join(root, file))

            quality_checks = {
                'total_python_files': len(python_files),
                'files_with_issues': 0,
                'issues_found': 0
            }

            alerts = []
            recommendations = []

            if not python_files:
                score = 100  # 没有Python文件，视为正常
                alerts.append({
                    'level': 'info',
                    'message': '未找到Python文件进行检查'
                })
            else:
                # 简单检查：文件大小、编码、基本结构
                issues = []
                for py_file in python_files[:10]:  # 只检查前10个文件
                    try:
                        with open(py_file, 'r', encoding='utf-8') as f:
                            content = f.read()

                        # 检查文件大小
                        if len(content) > 100000:  # 超过100KB
                            issues.append(f'{os.path.basename(py_file)}: 文件过大 ({len(content)} 字符)')

                        # 检查是否有shebang
                        if not content.startswith('#!/usr/bin/env python'):
                            issues.append(f'{os.path.basename(py_file)}: 缺少shebang或编码声明')

                        # 检查是否有基本文档
                        if '"""' not in content[:500] and "'''" not in content[:500]:
                            issues.append(f'{os.path.basename(py_file)}: 缺少文档字符串')

                    except UnicodeDecodeError:
                        issues.append(f'{os.path.basename(py_file)}: 编码问题，可能不是UTF-8')
                    except Exception as e:
                        issues.append(f'{os.path.basename(py_file)}: 读取失败 - {str(e)}')

                quality_checks['issues_found'] = len(issues)
                quality_checks['files_with_issues'] = len([i for i in issues if i])

                # 计算分数
                if len(python_files) > 0:
                    score = max(0, 100 - (len(issues) * 10))
                else:
                    score = 100

                if issues:
                    alerts.append({
                        'level': 'warning',
                        'message': f'发现{len(issues)}个代码质量问题'
                    })
                    recommendations.append("修复发现的代码质量问题")
                    recommendations.append("考虑使用pylint或flake8进行代码检查")

            return {
                'status': 'normal' if score >= 80 else 'warning' if score >= 60 else 'critical',
                'score': score,
                'details': quality_checks,
                'alerts': alerts,
                'recommendations': recommendations
            }

        except Exception as e:
            logger.error(f"代码质量检查失败: {e}")
            return {
                'status': 'error',
                'score': 0,
                'error': str(e)
            }

    def _check_tool_usage(self) -> Dict:
        """检查工具使用情况"""
        try:
            # 这里可以检查工具使用日志
            # 目前先返回一个基本检查结果

            # 检查是否有工具使用错误日志
            error_log_path = os.path.join(self.output_dir, '..', 'tool_errors.json')

            tool_checks = {
                'error_log_exists': os.path.exists(error_log_path)
            }

            score = 100
            alerts = []
            recommendations = []

            if tool_checks['error_log_exists']:
                try:
                    with open(error_log_path, 'r', encoding='utf-8') as f:
                        error_data = json.load(f)

                    error_count = len(error_data.get('errors', []))
                    if error_count > 0:
                        score = max(60, 100 - (error_count * 5))
                        alerts.append({
                            'level': 'warning',
                            'message': f'发现{error_count}个工具使用错误'
                        })
                        recommendations.append("查看工具使用错误日志，优化工具使用方式")
                        recommendations.append("运行工具使用修复脚本进行分析")
                except:
                    pass

            return {
                'status': 'normal' if score >= 80 else 'warning' if score >= 60 else 'critical',
                'score': score,
                'details': tool_checks,
                'alerts': alerts,
                'recommendations': recommendations
            }

        except Exception as e:
            logger.error(f"工具使用检查失败: {e}")
            return {
                'status': 'error',
                'score': 0,
                'error': str(e)
            }

    def _determine_overall_status(self, results: Dict) -> str:
        """确定总体状态"""
        score = results.get('overall_score', 0)

        if score >= 80:
            return 'excellent'
        elif score >= 70:
            return 'good'
        elif score >= 60:
            return 'fair'
        elif score >= 40:
            return 'poor'
        else:
            return 'critical'

    def _save_check_results(self, results: Dict):
        """保存检查结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"daily_health_check_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        logger.debug(f"每日健康检查结果已保存: {filepath}")

        # 同时保存到每日汇总文件
        daily_file = f"daily_health_summary_{datetime.now().strftime('%Y%m%d')}.json"
        daily_path = os.path.join(self.output_dir, daily_file)

        daily_summary = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'overall_score': results['overall_score'],
            'overall_status': results['overall_status'],
            'check_count': len(results['check_results']),
            'alert_count': len(results.get('alerts', [])),
            'recommendation_count': len(results.get('recommendations', []))
        }

        with open(daily_path, 'w', encoding='utf-8') as f:
            json.dump(daily_summary, f, ensure_ascii=False, indent=2)

    def _generate_report(self, results: Dict) -> str:
        """生成人类可读的报告"""
        report_lines = []

        # 标题
        report_lines.append("=" * 70)
        report_lines.append("📊 每日健康检查报告")
        report_lines.append(f"生成时间: {results['timestamp']}")
        report_lines.append(f"总体评分: {results['overall_score']:.1f}/100")
        report_lines.append(f"总体状态: {results['overall_status'].upper()}")
        report_lines.append("=" * 70)

        # 各项检查结果
        report_lines.append("\n🔍 检查项详情:")

        status_emojis = {
            'excellent': '🏆',
            'good': '✅',
            'fair': '⚠️',
            'poor': '🔶',
            'critical': '🚨',
            'error': '❌',
            'unknown': '❓'
        }

        for check_id, check_result in results['check_results'].items():
            check_config = self.check_items.get(check_id, {})
            check_name = check_config.get('name', check_id)

            status = check_result.get('status', 'unknown')
            score = check_result.get('score', 0)
            emoji = status_emojis.get(status, '❓')

            report_lines.append(f"\n{emoji} {check_name}:")
            report_lines.append(f"   状态: {status} | 分数: {score:.1f}/100")

            # 显示简要详情
            details = check_result.get('details', {})
            if isinstance(details, dict):
                for key, value in list(details.items())[:2]:  # 只显示前2个详情
                    report_lines.append(f"   {key}: {value}")

        # 报警信息
        if results.get('alerts'):
            report_lines.append(f"\n🚨 报警信息 ({len(results['alerts'])}个):")

            # 按级别分组
            critical_alerts = [a for a in results['alerts'] if a.get('level') == 'critical']
            warning_alerts = [a for a in results['alerts'] if a.get('level') == 'warning']
            info_alerts = [a for a in results['alerts'] if a.get('level') == 'info']

            if critical_alerts:
                report_lines.append("   🔴 严重报警:")
                for alert in critical_alerts[:3]:  # 只显示前3个
                    report_lines.append(f"      • {alert.get('message', '未知报警')}")

            if warning_alerts:
                report_lines.append("   🟡 警告:")
                for alert in warning_alerts[:3]:  # 只显示前3个
                    report_lines.append(f"      • {alert.get('message', '未知警告')}")

            if info_alerts:
                report_lines.append("   🔵 信息:")
                for alert in info_alerts[:2]:  # 只显示前2个
                    report_lines.append(f"      • {alert.get('message', '未知信息')}")

        # 建议
        if results.get('recommendations'):
            report_lines.append(f"\n💡 改进建议 ({len(results['recommendations'])}条):")
            for i, rec in enumerate(results['recommendations'][:5]):  # 只显示前5条
                report_lines.append(f"   {i+1}. {rec}")

        # 总体评估
        report_lines.append("\n📈 总体评估:")

        score = results['overall_score']
        if score >= 90:
            report_lines.append("   🎉 优秀！项目健康状况非常好，继续保持！")
        elif score >= 80:
            report_lines.append("   👍 良好！项目运行正常，有些小问题需要注意。")
        elif score >= 70:
            report_lines.append("   🤔 一般！项目有一些问题需要关注和改进。")
        elif score >= 60:
            report_lines.append("   ⚠️ 需改进！项目存在较多问题，建议优先处理。")
        else:
            report_lines.append("   🚨 紧急！项目健康状况不佳，需要立即处理！")

        # 下一步行动
        report_lines.append("\n🎯 下一步行动:")

        if results['overall_status'] in ['critical', 'poor']:
            report_lines.append("   1. 🔴 立即处理严重报警")
            report_lines.append("   2. 🛠️ 修复发现的主要问题")
            report_lines.append("   3. 📋 制定改进计划")
        elif results['overall_status'] == 'fair':
            report_lines.append("   1. ⚠️ 处理警告级别的问题")
            report_lines.append("   2. 📊 分析问题根本原因")
            report_lines.append("   3. 🔄 实施预防措施")
        else:
            report_lines.append("   1. ✅ 继续保持良好状态")
            report_lines.append("   2. 📈 寻找优化机会")
            report_lines.append("   3. 🚀 规划下一步发展")

        report_lines.append("\n" + "=" * 70)

        return '\n'.join(report_lines)


def main():
    """主函数"""
    print("每日健康检查启动...")

    checker = DailyHealthChecker()

    try:
        # 运行所有检查
        results = checker.run_all_checks()

        # 生成并显示报告
        report = checker._generate_report(results)
        print(report)

        # 根据状态决定退出码
        status = results['overall_status']
        if status in ['critical', 'poor']:
            sys.exit(1)
        elif status == 'fair':
            sys.exit(2)
        else:
            sys.exit(0)

    except Exception as e:
        logger.error(f"每日健康检查失败: {e}")
        print(f"❌ 每日健康检查失败: {e}")
        sys.exit(3)


if __name__ == "__main__":
    main()
