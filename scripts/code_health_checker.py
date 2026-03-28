#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码健康度检查工具
用于定期检查项目代码质量、结构和性能
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any
import subprocess

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CodeHealthChecker:
    """代码健康度检查器"""
    
    def __init__(self, workspace_path: str = "/Users/ago/.openclaw/workspace"):
        self.workspace_path = Path(workspace_path)
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'overall_score': 0,
            'categories': {},
            'issues': [],
            'recommendations': []
        }
        
        # 检查配置
        self.config = {
            'max_file_size_mb': 1.0,      # 最大文件大小
            'max_directory_depth': 5,      # 最大目录深度
            'min_comment_ratio': 0.1,      # 最小注释比例
            'max_cyclomatic_complexity': 10,  # 最大圈复杂度
            'exclude_dirs': ['.git', '__pycache__', 'node_modules', '.venv'],
            'exclude_exts': ['.pyc', '.pyo', '.so', '.dll', '.exe']
        }
    
    def run_full_check(self) -> Dict:
        """运行完整检查"""
        logger.info("开始代码健康度检查")
        
        # 运行所有检查
        self._check_directory_structure()
        self._check_file_sizes()
        self._check_python_code_quality()
        self._check_skill_structure()
        self._check_performance_metrics()
        self._check_documentation()
        
        # 计算总体分数
        self._calculate_overall_score()
        
        # 生成报告
        report = self._generate_report()
        
        logger.info(f"代码健康度检查完成，总体分数: {self.results['overall_score']}/100")
        return report
    
    def _check_directory_structure(self):
        """检查目录结构"""
        category = 'directory_structure'
        score = 100
        issues = []
        recommendations = []
        
        # 检查必要目录是否存在
        required_dirs = ['scripts', 'strategies', 'data', 'docs', 'skills']
        missing_dirs = []
        
        for dir_name in required_dirs:
            dir_path = self.workspace_path / dir_name
            if not dir_path.exists():
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            score -= len(missing_dirs) * 10
            issues.append(f"缺少必要目录: {', '.join(missing_dirs)}")
            recommendations.append(f"创建缺失目录: {', '.join(missing_dirs)}")
        
        # 检查目录深度
        max_depth = 0
        for root, dirs, files in os.walk(self.workspace_path):
            depth = root.count(os.sep) - str(self.workspace_path).count(os.sep)
            max_depth = max(max_depth, depth)
        
        if max_depth > self.config['max_directory_depth']:
            score -= 20
            issues.append(f"目录深度过大: {max_depth}层")
            recommendations.append("考虑扁平化目录结构")
        
        self.results['categories'][category] = {
            'score': max(0, score),
            'issues': issues,
            'recommendations': recommendations
        }
    
    def _check_file_sizes(self):
        """检查文件大小"""
        category = 'file_sizes'
        score = 100
        issues = []
        recommendations = []
        large_files = []
        
        for root, dirs, files in os.walk(self.workspace_path):
            # 跳过排除目录
            dirs[:] = [d for d in dirs if d not in self.config['exclude_dirs']]
            
            for file in files:
                # 跳过排除扩展名
                if any(file.endswith(ext) for ext in self.config['exclude_exts']):
                    continue
                
                file_path = Path(root) / file
                try:
                    file_size_mb = file_path.stat().st_size / (1024 * 1024)
                    
                    if file_size_mb > self.config['max_file_size_mb']:
                        large_files.append({
                            'path': str(file_path.relative_to(self.workspace_path)),
                            'size_mb': round(file_size_mb, 2)
                        })
                except (OSError, PermissionError):
                    continue
        
        if large_files:
            score -= len(large_files) * 5
            issues.append(f"发现 {len(large_files)} 个过大文件")
            for file_info in large_files[:5]:  # 只显示前5个
                issues.append(f"  - {file_info['path']}: {file_info['size_mb']}MB")
            
            if len(large_files) > 5:
                issues.append(f"  ... 还有 {len(large_files) - 5} 个文件")
            
            recommendations.append("考虑拆分过大文件，提高可维护性")
        
        self.results['categories'][category] = {
            'score': max(0, score),
            'issues': issues,
            'recommendations': recommendations
        }
    
    def _check_python_code_quality(self):
        """检查Python代码质量"""
        category = 'python_code_quality'
        score = 100
        issues = []
        recommendations = []
        
        # 统计Python文件
        python_files = []
        for root, dirs, files in os.walk(self.workspace_path):
            dirs[:] = [d for d in dirs if d not in self.config['exclude_dirs']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        
        if not python_files:
            score = 0
            issues.append("未找到Python文件")
            self.results['categories'][category] = {
                'score': score,
                'issues': issues,
                'recommendations': recommendations
            }
            return
        
        # 检查基本质量指标
        total_lines = 0
        total_comments = 0
        files_with_issues = 0
        
        for py_file in python_files[:20]:  # 限制检查数量
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    total_lines += len(lines)
                    
                    # 统计注释行
                    comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
                    total_comments += comment_lines
                    
                    # 简单检查：是否有异常长的行
                    long_lines = sum(1 for line in lines if len(line) > 120)
                    if long_lines > 5:
                        files_with_issues += 1
                        issues.append(f"文件 {py_file.name} 有过长行 ({long_lines}行>120字符)")
                    
            except Exception as e:
                logger.warning(f"检查文件失败 {py_file}: {e}")
        
        # 计算注释比例
        if total_lines > 0:
            comment_ratio = total_comments / total_lines
            if comment_ratio < self.config['min_comment_ratio']:
                score -= 20
                issues.append(f"注释比例过低: {comment_ratio:.1%} (建议>{self.config['min_comment_ratio']:.0%})")
                recommendations.append("增加代码注释，提高可读性")
        
        if files_with_issues > 0:
            score -= files_with_issues * 5
            recommendations.append("优化代码格式，避免过长行")
        
        self.results['categories'][category] = {
            'score': max(0, score),
            'issues': issues,
            'recommendations': recommendations,
            'stats': {
                'python_files': len(python_files),
                'total_lines': total_lines,
                'comment_ratio': total_comments / total_lines if total_lines > 0 else 0
            }
        }
    
    def _check_skill_structure(self):
        """检查Skill结构"""
        category = 'skill_structure'
        score = 100
        issues = []
        recommendations = []
        
        skills_dir = self.workspace_path / 'skills'
        if not skills_dir.exists():
            score = 0
            issues.append("skills目录不存在")
            self.results['categories'][category] = {
                'score': score,
                'issues': issues,
                'recommendations': recommendations
            }
            return
        
        # 检查每个Skill的结构
        skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir()]
        
        if not skill_dirs:
            score = 50
            issues.append("skills目录为空")
            recommendations.append("开始创建Skill，提高代码复用性")
        else:
            required_files = ['SKILL.md', 'README.md']
            incomplete_skills = []
            
            for skill_dir in skill_dirs:
                missing_files = []
                for req_file in required_files:
                    if not (skill_dir / req_file).exists():
                        missing_files.append(req_file)
                
                if missing_files:
                    incomplete_skills.append({
                        'skill': skill_dir.name,
                        'missing': missing_files
                    })
            
            if incomplete_skills:
                score -= len(incomplete_skills) * 15
                for skill_info in incomplete_skills:
                    issues.append(f"Skill '{skill_info['skill']}' 缺少文件: {', '.join(skill_info['missing'])}")
                
                recommendations.append("完善Skill文档，确保每个Skill都有完整文档")
        
        self.results['categories'][category] = {
            'score': max(0, score),
            'issues': issues,
            'recommendations': recommendations,
            'stats': {
                'total_skills': len(skill_dirs),
                'skill_names': [d.name for d in skill_dirs]
            }
        }
    
    def _check_performance_metrics(self):
        """检查性能指标"""
        category = 'performance'
        score = 100
        issues = []
        recommendations = []
        
        # 检查工作区大小
        try:
            result = subprocess.run(
                ['du', '-sh', str(self.workspace_path)],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                size_str = result.stdout.split()[0]
                # 解析大小
                if 'G' in size_str:
                    size_gb = float(size_str.replace('G', ''))
                    if size_gb > 1.0:
                        score -= 20
                        issues.append(f"工作区过大: {size_str}")
                        recommendations.append("清理不必要的文件，优化存储")
                elif 'M' in size_str:
                    size_mb = float(size_str.replace('M', ''))
                    if size_mb > 500:
                        score -= 10
                        issues.append(f"工作区较大: {size_str}")
        except Exception as e:
            logger.warning(f"检查工作区大小失败: {e}")
        
        self.results['categories'][category] = {
            'score': max(0, score),
            'issues': issues,
            'recommendations': recommendations
        }
    
    def _check_documentation(self):
        """检查文档完整性"""
        category = 'documentation'
        score = 100
        issues = []
        recommendations = []
        
        # 检查核心文档文件
        core_docs = ['MEMORY.md', 'USER.md', 'SOUL.md', 'AGENTS.md', 'TOOLS.md']
        missing_docs = []
        
        for doc_file in core_docs:
            if not (self.workspace_path / doc_file).exists():
                missing_docs.append(doc_file)
        
        if missing_docs:
            score -= len(missing_docs) * 20
            issues.append(f"缺少核心文档: {', '.join(missing_docs)}")
            recommendations.append("创建缺失的核心文档文件")
        
        # 检查项目文档目录
        docs_dir = self.workspace_path / 'docs'
        if docs_dir.exists():
            doc_files = list(docs_dir.glob('*.md'))
            if not doc_files:
                score -= 10
                issues.append("docs目录为空")
                recommendations.append("添加项目文档到docs目录")
        else:
            score -= 15
            issues.append("缺少docs目录")
            recommendations.append("创建docs目录用于存放项目文档")
        
        self.results['categories'][category] = {
            'score': max(0, score),
            'issues': issues,
            'recommendations': recommendations
        }
    
    def _calculate_overall_score(self):
        """计算总体分数"""
        if not self.results['categories']:
            self.results['overall_score'] = 0
            return
        
        total_score = 0
        weight_config = {
            'directory_structure': 0.15,
            'file_sizes': 0.10,
            'python_code_quality': 0.25,
            'skill_structure': 0.20,
            'performance': 0.15,
            'documentation': 0.15
        }
        
        for category, data in self.results['categories'].items():
            weight = weight_config.get(category, 0.1)
            total_score += data['score'] * weight
        
        self.results['overall_score'] = round(total_score, 1)
    
    def _generate_report(self) -> Dict:
        """生成检查报告"""
        report = {
            'summary': {
                'timestamp': self.results['timestamp'],
                'overall_score': self.results['overall_score'],
                'health_level': self._get_health_level(self.results['overall_score']),
                'total_issues': sum(len(cat['issues']) for cat in self.results['categories'].values()),
                'total_recommendations': sum(len(cat['recommendations']) for cat in self.results['categories'].values())
            },
            'categories': self.results['categories'],
            'top_issues': [],
            'top_recommendations': []
        }
        
        # 收集所有问题和建议
        all_issues = []
        all_recommendations = []
        
        for category, data in self.results['categories'].items():
            for issue in data['issues']:
                all_issues.append(f"[{category}] {issue}")
            for rec in data['recommendations']:
                all_recommendations.append(f"[{category}] {rec}")
        
        report['top_issues'] = all_issues[:10]  # 最多显示10个问题
        report['top_recommendations'] = all_recommendations[:10]  # 最多显示10个建议
        
        return report
    
    def _get_health_level(self, score: float) -> str:
        """获取健康等级"""
        if score >= 90:
            return "优秀 🟢"
        elif score >= 75:
            return "良好 🟡"
        elif score >= 60:
            return "一般 🟠"
        else:
            return "需要改进 🔴"
    
    def save_report(self, report: Dict, output_path: str = None):
        """保存检查报告"""
        if output_path is None:
            output_path = self.workspace_path / 'reports' / 'code_health_report.json'
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"检查报告已保存: {output_path}")
        
        # 同时生成简化版文本报告
        text_report_path = output_path.with_suffix('.txt')
        self._generate_text_report(report, text_report_path)
    
    def _generate_text_report(self, report: Dict, output_path: Path):
        """生成文本格式报告"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("代码健康度检查报告\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"检查时间: {report['summary']['timestamp']}\n")
            f.write(f"总体分数: {report['summary']['overall_score']}/100\n")
            f.write(f"健康等级: {report['summary']['health_level']}\n")
            f.write(f"发现问题: {report['summary']['total_issues']} 个\n")
            f.write(f"改进建议: {report['summary']['total_recommendations']} 条\n\n")
            
            f.write("=" * 60 + "\n")
            f.write("各维度检查结果\n")
            f.write("=" * 60 + "\n\n")
            
            for category, data in report['categories'].items():
                f.write(f"【{category.replace('_', ' ').title()}】\n")
                f.write(f"  分数: {data['score']}/100\n")
                
                if data.get('stats'):
                    for stat_name, stat_value in data['stats'].items():
                        if isinstance(stat_value, float):
                            f.write(f"  {stat_name}: {stat_value:.2f}\n")
                        else:
                            f.write(f"  {stat_name}: {stat_value}\n")
                
                if data['issues']:
                    f.write("  问题:\n")
                    for issue in data['issues'][:3]:  # 最多显示3个问题
                        f.write(f"    • {issue}\n")
                
                if data['recommendations']:
                    f.write("  建议:\n")
                    for rec in data['recommendations'][:3]:  # 最多显示3个建议
                        f.write(f"    • {rec}\n")
                
                f.write("\n")
            
            if report['top_issues']:
                f.write("=" * 60 + "\n")
                f.write("重点关注问题\n")
                f.write("=" * 60 + "\n\n")
                for i, issue in enumerate(report['top_issues'], 1):
                    f.write(f"{i}. {issue}\n")
            
            if report['top_recommendations']:
                f.write("\n" + "=" * 60 + "\n")
                f.write("优先改进建议\n")
                f.write("=" * 60 + "\n\n")
                for i, rec in enumerate(report['top_recommendations'], 1):
                    f.write(f"{i}. {rec}\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("后续行动计划\n")
            f.write("=" * 60 + "\n\n")
            
            health_level = report['summary']['health_level']
            if "优秀" in health_level:
                f.write("✅ 代码健康度优秀，继续保持！\n")
                f.write("建议：\n")
                f.write("1. 定期运行检查，防止质量下降\n")
                f.write("2. 继续Skill沉淀，提高复用性\n")
                f.write("3. 完善测试覆盖，确保稳定性\n")
            elif "良好" in health_level:
                f.write("🟡 代码健康度良好，有改进空间\n")
                f.write("建议：\n")
                f.write("1. 处理重点关注问题\n")
                f.write("2. 实施优先改进建议\n")
                f.write("3. 建立定期检查机制\n")
            elif "一般" in health_level:
                f.write("🟠 代码健康度一般，需要改进\n")
                f.write("建议：\n")
                f.write("1. 立即处理严重问题\n")
                f.write("2. 制定代码重构计划\n")
                f.write("3. 加强代码审查流程\n")
            else:
                f.write("🔴 代码健康度需要紧急改进\n")
                f.write("建议：\n")
                f.write("1. 暂停新功能开发，专注代码质量\n")
                f.write("2. 制定紧急重构计划\n")
                f.write("3. 建立质量门禁，防止进一步恶化\n")


def main():
    """主函数"""
    print("代码健康度检查工具")
    print("版本: 1.0.0")
    print("=" * 60)
    
    # 创建检查器
    checker = CodeHealthChecker()
    
    # 运行检查
    print("正在检查代码健康度...")
    report = checker.run_full_check()
    
    # 显示结果
    print(f"\n检查完成！总体分数: {report['summary']['overall_score']}/100")
    print(f"健康等级: {report['summary']['health_level']}")
    print(f"发现问题: {report['summary']['total_issues']} 个")
    print(f"改进建议: {report['summary']['total_recommendations']} 条")
    
    # 保存报告
    checker.save_report(report)
    
    # 显示重点关注问题
    if report['top_issues']:
        print("\n重点关注问题:")
        for i, issue in enumerate(report['top_issues'][:5], 1):
            print(f"  {i}. {issue}")
    
    # 显示优先建议
    if report['top_recommendations']:
        print("\n优先改进建议:")
        for i, rec in enumerate(report['top_recommendations'][:5], 1):
            print(f"  {i}. {rec}")
    
    print("\n" + "=" * 60)
    print("详细报告已保存到:")
    print("  - reports/code_health_report.json")
    print("  - reports/code_health_report.txt")
    print("\n建议定期运行此工具监控代码健康度变化。")


if __name__ == "__main__":
    main()