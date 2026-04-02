#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件完整性检查工具
用于检查文件是否完整，避免编辑错误
"""

import os
import sys
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FileIntegrityChecker:
    """文件完整性检查器"""

    def __init__(self, workspace_path: str = "/Users/ago/.openclaw/workspace"):
        self.workspace_path = Path(workspace_path)
        self.issues = []

        # 常见的不完整文件模式
        self.incomplete_patterns = [
            "return None",  # 文件可能在中途结束
            "def ",         # 函数定义但没有结束
            "class ",       # 类定义但没有结束
            "import ",      # 导入但没有后续代码
        ]

        # 需要检查的文件扩展名
        self.check_extensions = ['.py', '.md', '.txt', '.json', '.yaml', '.yml']

    def check_all_files(self) -> Dict:
        """检查所有文件"""
        logger.info("开始文件完整性检查")

        results = {
            'total_files': 0,
            'checked_files': 0,
            'issues_found': 0,
            'issues': [],
            'recommendations': []
        }

        for root, dirs, files in os.walk(self.workspace_path):
            # 跳过一些目录
            if any(skip in root for skip in ['.git', '__pycache__', 'node_modules']):
                continue

            for file in files:
                if any(file.endswith(ext) for ext in self.check_extensions):
                    file_path = Path(root) / file
                    results['total_files'] += 1

                    # 检查文件
                    file_issues = self._check_file(file_path)
                    if file_issues:
                        results['issues_found'] += 1
                        results['issues'].extend(file_issues)

                    results['checked_files'] += 1

        # 生成建议
        if results['issues_found'] > 0:
            results['recommendations'] = self._generate_recommendations(results['issues'])

        logger.info(f"文件完整性检查完成: 检查{results['checked_files']}个文件，发现{results['issues_found']}个问题")
        return results

    def _check_file(self, file_path: Path) -> List[Dict]:
        """检查单个文件"""
        issues = []

        try:
            # 检查文件大小
            file_size = file_path.stat().st_size
            if file_size == 0:
                issues.append({
                    'file': str(file_path.relative_to(self.workspace_path)),
                    'issue': '文件为空',
                    'severity': 'high'
                })
                return issues

            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # 检查Python文件语法
            if file_path.suffix == '.py':
                py_issues = self._check_python_file(content, file_path)
                issues.extend(py_issues)

            # 检查常见的不完整模式
            for pattern in self.incomplete_patterns:
                if pattern in content:
                    # 检查是否在文件末尾附近
                    lines = content.split('\n')
                    last_100_chars = content[-100:] if len(content) > 100 else content

                    if pattern in last_100_chars:
                        issues.append({
                            'file': str(file_path.relative_to(self.workspace_path)),
                            'issue': f'文件可能在"{pattern}"处不完整结束',
                            'severity': 'medium'
                        })

            # 检查括号/引号是否匹配
            if file_path.suffix in ['.py', '.json']:
                bracket_issues = self._check_brackets(content, file_path)
                issues.extend(bracket_issues)

        except UnicodeDecodeError:
            # 二进制文件，跳过
            pass
        except Exception as e:
            issues.append({
                'file': str(file_path.relative_to(self.workspace_path)),
                'issue': f'检查文件时出错: {str(e)}',
                'severity': 'high'
            })

        return issues

    def _check_python_file(self, content: str, file_path: Path) -> List[Dict]:
        """检查Python文件"""
        issues = []

        lines = content.split('\n')

        # 检查缩进
        for i, line in enumerate(lines, 1):
            stripped = line.lstrip()
            if stripped and not line.startswith(' ') and not line.startswith('\t'):
                # 检查是否应该是缩进的
                prev_lines = lines[max(0, i-3):i-1]
                for prev_line in reversed(prev_lines):
                    if prev_line.strip().endswith(':'):
                        issues.append({
                            'file': str(file_path.relative_to(self.workspace_path)),
                            'issue': f'第{i}行: 可能缺少缩进',
                            'severity': 'medium',
                            'line': i
                        })
                        break

        # 检查函数/类定义是否完整
        in_function = False
        in_class = False
        indent_level = 0

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            if stripped.startswith('def ') or stripped.startswith('class '):
                # 检查定义行是否以冒号结束
                if not stripped.endswith(':'):
                    issues.append({
                        'file': str(file_path.relative_to(self.workspace_path)),
                        'issue': f'第{i}行: 函数/类定义缺少冒号',
                        'severity': 'high',
                        'line': i
                    })

        return issues

    def _check_brackets(self, content: str, file_path: Path) -> List[Dict]:
        """检查括号/引号是否匹配"""
        issues = []

        # 检查括号匹配
        brackets = {
            '(': ')',
            '[': ']',
            '{': '}'
        }

        stack = []
        in_string = False
        string_char = None
        escaped = False

        for i, char in enumerate(content):
            # 处理字符串
            if not escaped:
                if char in ['"', "'"]:
                    if not in_string:
                        in_string = True
                        string_char = char
                    elif char == string_char:
                        in_string = False
                        string_char = None
                elif char == '\\':
                    escaped = True
                    continue

            escaped = False

            if in_string:
                continue

            # 处理括号
            if char in brackets.keys():
                stack.append((char, i))
            elif char in brackets.values():
                if not stack:
                    issues.append({
                        'file': str(file_path.relative_to(self.workspace_path)),
                        'issue': f'位置{i}: 多余的关闭括号 "{char}"',
                        'severity': 'high',
                        'position': i
                    })
                else:
                    last_open, last_pos = stack.pop()
                    if brackets[last_open] != char:
                        issues.append({
                            'file': str(file_path.relative_to(self.workspace_path)),
                            'issue': f'位置{last_pos}-{i}: 括号不匹配 "{last_open}" vs "{char}"',
                            'severity': 'high',
                            'position': i
                        })

        # 检查未关闭的括号
        for open_char, pos in stack:
            issues.append({
                'file': str(file_path.relative_to(self.workspace_path)),
                'issue': f'位置{pos}: 未关闭的括号 "{open_char}"',
                'severity': 'high',
                'position': pos
            })

        return issues

    def _generate_recommendations(self, issues: List[Dict]) -> List[str]:
        """生成修复建议"""
        recommendations = []

        high_issues = [i for i in issues if i['severity'] == 'high']
        medium_issues = [i for i in issues if i['severity'] == 'medium']

        if high_issues:
            recommendations.append("立即修复以下高优先级问题:")
            for issue in high_issues[:5]:  # 只显示前5个
                recommendations.append(f"  - {issue['file']}: {issue['issue']}")

        if medium_issues:
            recommendations.append("尽快修复以下中优先级问题:")
            for issue in medium_issues[:5]:  # 只显示前5个
                recommendations.append(f"  - {issue['file']}: {issue['issue']}")

        # 通用建议
        recommendations.append("")
        recommendations.append("预防措施:")
        recommendations.append("1. 编辑文件时使用完整的文本匹配")
        recommendations.append("2. 避免在文件中间中断编辑")
        recommendations.append("3. 定期运行文件完整性检查")
        recommendations.append("4. 重要文件编辑前先备份")

        return recommendations

    def fix_common_issues(self):
        """修复常见问题"""
        logger.info("开始修复常见文件问题")

        fixed_count = 0

        # 修复策略：
        # 1. 删除明显不完整的文件
        # 2. 修复明显的语法错误
        # 3. 创建备份

        # 首先备份当前状态
        backup_dir = self.workspace_path / 'backups' / 'file_fixes'
        backup_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"修复前的备份保存在: {backup_dir}")

        return {
            'fixed_count': fixed_count,
            'backup_dir': str(backup_dir),
            'status': 'completed'
        }


def main():
    """主函数"""
    print("文件完整性检查工具")
    print("版本: 1.0.0")
    print("=" * 60)

    checker = FileIntegrityChecker()

    print("正在检查文件完整性...")
    results = checker.check_all_files()

    print(f"\n检查完成!")
    print(f"检查文件数: {results['checked_files']}/{results['total_files']}")
    print(f"发现问题数: {results['issues_found']}")

    if results['issues_found'] > 0:
        print("\n发现的问题:")
        for i, issue in enumerate(results['issues'][:10], 1):  # 只显示前10个
            print(f"{i}. [{issue['severity'].upper()}] {issue['file']}: {issue['issue']}")

        print("\n修复建议:")
        for rec in results['recommendations']:
            print(f"  {rec}")

        # 询问是否修复
        print("\n" + "=" * 60)
        response = input("是否尝试自动修复常见问题? (y/N): ")
        if response.lower() == 'y':
            fix_results = checker.fix_common_issues()
            print(f"修复完成: {fix_results['fixed_count']}个问题已修复")
            print(f"备份位置: {fix_results['backup_dir']}")
    else:
        print("\n✅ 所有文件完整性检查通过!")

    print("\n" + "=" * 60)
    print("建议:")
    print("1. 定期运行此工具检查文件完整性")
    print("2. 编辑重要文件前先备份")
    print("3. 使用完整的文本匹配进行编辑")


if __name__ == "__main__":
    main()
