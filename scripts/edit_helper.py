#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
编辑助手 - 帮助安全地使用edit工具
"""

import os
import re
import sys

def read_file_safely(filepath: str, lines_before: int = 5, lines_after: int = 5) -> str:
    """安全地读取文件内容，显示上下文"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 如果文件太大，只显示部分
        if len(content) > 10000:
            return f"文件过大 ({len(content)} 字符)，建议直接查看文件"
        
        return content
    except Exception as e:
        return f"读取文件失败: {e}"

def find_text_with_context(content: str, search_text: str, context_lines: int = 3) -> list:
    """查找文本并显示上下文"""
    lines = content.split('\n')
    matches = []
    
    for i, line in enumerate(lines):
        if search_text in line:
            start = max(0, i - context_lines)
            end = min(len(lines), i + context_lines + 1)
            
            context = []
            for j in range(start, end):
                prefix = '>>> ' if j == i else '    '
                context.append(f"{prefix}{lines[j]}")
            
            matches.append({
                'line_number': i + 1,
                'context': '\n'.join(context)
            })
    
    return matches

def verify_edit_parameters(filepath: str, old_text: str) -> dict:
    """验证编辑参数"""
    result = {
        'is_valid': False,
        'issues': [],
        'suggestions': [],
        'matches': []
    }
    
    # 1. 检查文件是否存在
    if not os.path.exists(filepath):
        result['issues'].append(f"文件不存在: {filepath}")
        return result
    
    # 2. 读取文件内容
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        result['issues'].append(f"无法读取文件: {e}")
        return result
    
    # 3. 查找匹配
    matches = find_text_with_context(content, old_text)
    
    if not matches:
        result['issues'].append(f"未找到文本: {old_text}")
        result['suggestions'].append("检查文本是否完全匹配（包括空格和换行）")
        result['suggestions'].append("尝试使用更短的匹配文本")
    elif len(matches) > 1:
        result['issues'].append(f"找到{len(matches)}个匹配，文本不唯一")
        result['suggestions'].append("提供更多上下文使文本唯一")
        result['suggestions'].append("考虑使用行号或特定标识符")
        
        # 显示前3个匹配
        for i, match in enumerate(matches[:3]):
            result['matches'].append(f"匹配 #{i+1} (第{match['line_number']}行):")
            result['matches'].append(match['context'])
    else:
        result['is_valid'] = True
        result['suggestions'].append("✅ 文本匹配成功，可以安全编辑")
        result['matches'].append(f"找到匹配 (第{matches[0]['line_number']}行):")
        result['matches'].append(matches[0]['context'])
    
    return result

def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("用法: python edit_helper.py <文件路径> <要查找的文本>")
        print("示例: python edit_helper.py script.py 'def test_function'")
        sys.exit(1)
    
    filepath = sys.argv[1]
    search_text = sys.argv[2]
    
    print(f"🔍 检查编辑参数:")
    print(f"   文件: {filepath}")
    print(f"   文本: '{search_text}'")
    print()
    
    result = verify_edit_parameters(filepath, search_text)
    
    if result['is_valid']:
        print("✅ 验证通过，可以安全编辑")
    else:
        print("❌ 验证失败，发现问题:")
        for issue in result['issues']:
            print(f"   • {issue}")
    
    print()
    
    if result['suggestions']:
        print("💡 建议:")
        for suggestion in result['suggestions']:
            print(f"   {suggestion}")
    
    print()
    
    if result['matches']:
        print("📄 匹配结果:")
        for match in result['matches']:
            print(match)

if __name__ == "__main__":
    main()
