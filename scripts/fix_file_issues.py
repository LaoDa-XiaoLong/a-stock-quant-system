#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复文件问题脚本
专门修复编辑错误导致的问题
"""

import os
import sys
from pathlib import Path
import re

def fix_python_file(file_path):
    """修复Python文件常见问题"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    fixed = False
    
    # 修复1: 函数定义缺少冒号
    lines = content.split('\n')
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('def ') or stripped.startswith('class '):
            if not stripped.endswith(':'):
                lines[i] = line + ':'
                fixed = True
                print(f"  修复: 第{i+1}行添加冒号")
    
    if fixed:
        content = '\n'.join(lines)
    
    # 修复2: 检查括号匹配
    brackets = {'(': ')', '[': ']', '{': '}'}
    stack = []
    
    for i, char in enumerate(content):
        if char in brackets.keys():
            stack.append((char, i))
        elif char in brackets.values():
            if stack:
                last_open, last_pos = stack.pop()
                if brackets[last_open] != char:
                    print(f"  警告: 位置{last_pos}的'{last_open}'与位置{i}的'{char}'不匹配")
    
    # 如果有未关闭的括号，在文件末尾添加
    if stack:
        for open_char, pos in stack:
            print(f"  警告: 位置{pos}的'{open_char}'未关闭")
        
        # 在文件末尾添加缺失的括号
        missing_closing = ''.join(brackets[open_char] for open_char, _ in reversed(stack))
        content = content.rstrip() + '\n' + missing_closing + '\n'
        fixed = True
        print(f"  修复: 在文件末尾添加'{missing_closing}'")
    
    if fixed and content != original_content:
        # 创建备份
        backup_path = file_path.with_suffix(file_path.suffix + '.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        
        # 写入修复后的内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  已修复并备份到: {backup_path.name}")
        return True
    
    return False

def check_file_completeness(file_path):
    """检查文件是否完整"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查Python文件是否以完整语句结束
    if file_path.suffix == '.py':
        lines = content.strip().split('\n')
        if lines:
            last_line = lines[-1].strip()
            # 如果最后一行是import语句，可能是正常的
            if last_line.startswith('import ') or last_line.startswith('from '):
                # 检查是否有后续代码
                has_code_after = False
                for line in lines:
                    if line.strip() and not (line.strip().startswith('import ') or line.strip().startswith('from ') or line.strip().startswith('#')):
                        has_code_after = True
                        break
                
                if not has_code_after:
                    print(f"  警告: 文件可能只包含import语句，没有实际代码")
                    return False
            
            # 检查常见的未完成模式
            incomplete_patterns = [
                r'def\s+\w+\(.*\)$',  # 函数定义没有冒号
                r'class\s+\w+\(.*\)$',  # 类定义没有冒号
                r'if\s+.*:$',  # if语句没有后续
                r'for\s+.*:$',  # for循环没有后续
                r'while\s+.*:$',  # while循环没有后续
                r'try:$',  # try语句没有后续
            ]
            
            for pattern in incomplete_patterns:
                if re.search(pattern, last_line):
                    print(f"  警告: 文件可能以未完成的语句结束: {last_line}")
                    return False
    
    return True

def main():
    """主函数"""
    print("文件问题修复工具")
    print("=" * 60)
    
    workspace = Path("/Users/ago/.openclaw/workspace")
    
    # 需要检查的文件列表（基于之前的错误报告）
    files_to_check = [
        workspace / "strategies" / "stock_pool_filter.py",
        workspace / "scripts" / "final_financial_monitor.py",
        workspace / "scripts" / "run_quant_analysis.py",
        workspace / "scripts" / "simple_data_fetcher.py",
        workspace / "scripts" / "test_us_stock_simple.py",
        workspace / "scripts" / "data_quality_validator.py",
    ]
    
    print("检查以下文件:")
    for file_path in files_to_check:
        if file_path.exists():
            print(f"\n检查: {file_path.relative_to(workspace)}")
            
            # 检查完整性
            if not check_file_completeness(file_path):
                print("  ⚠️  文件可能不完整")
            
            # 尝试修复Python文件
            if file_path.suffix == '.py':
                if fix_python_file(file_path):
                    print("  ✅ 已尝试修复")
                else:
                    print("  ✅ 文件看起来正常")
        else:
            print(f"\n❌ 文件不存在: {file_path.relative_to(workspace)}")
    
    print("\n" + "=" * 60)
    print("修复完成!")
    print("\n建议:")
    print("1. 编辑文件时确保操作完整")
    print("2. 使用'write'工具创建新文件，而不是多次'edit'")
    print("3. 复杂编辑前先备份文件")
    print("4. 定期运行文件完整性检查")

if __name__ == "__main__":
    main()