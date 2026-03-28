#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具使用修复脚本
用于修复常见的工具使用错误，特别是edit工具的问题
"""

import os
import re
import json
from typing import Dict, List, Optional
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ToolUsageFixer:
    """工具使用修复器"""
    
    def __init__(self):
        self.common_errors = {
            'edit_failed_exact_match': {
                'pattern': r'Could not find the exact text in (.+)\.',
                'solution': '使用更精确的匹配或先读取文件内容确认',
                'fix_method': 'read_and_verify'
            },
            'edit_failed_not_unique': {
                'pattern': r'Found (\d+) occurrences of the text in (.+)\.',
                'solution': '提供更多上下文使匹配文本唯一',
                'fix_method': 'make_text_unique'
            },
            'http_400_error': {
                'pattern': r'Create card request failed with HTTP 400',
                'solution': '简化消息格式或检查API权限',
                'fix_method': 'simplify_message_format'
            }
        }
        
        logger.info("工具使用修复器初始化完成")
    
    def analyze_error_log(self, error_log: str) -> List[Dict]:
        """分析错误日志"""
        errors = []
        
        for error_type, error_info in self.common_errors.items():
            pattern = error_info['pattern']
            matches = re.findall(pattern, error_log)
            
            for match in matches:
                if isinstance(match, tuple):
                    # 多个捕获组的情况
                    details = ' '.join([str(m) for m in match if m])
                else:
                    details = match
                
                errors.append({
                    'type': error_type,
                    'details': details,
                    'solution': error_info['solution'],
                    'fix_method': error_info['fix_method']
                })
        
        return errors
    
    def generate_fix_report(self, errors: List[Dict]) -> str:
        """生成修复报告"""
        if not errors:
            return "✅ 未发现需要修复的错误"
        
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("工具使用错误分析报告")
        report_lines.append(f"发现错误数量: {len(errors)}")
        report_lines.append("=" * 60)
        
        # 按错误类型分组
        error_groups = {}
        for error in errors:
            error_type = error['type']
            if error_type not in error_groups:
                error_groups[error_type] = []
            error_groups[error_type].append(error)
        
        # 输出每种错误的详细信息
        for error_type, error_list in error_groups.items():
            report_lines.append(f"\n📋 {error_type.replace('_', ' ').title()}:")
            report_lines.append(f"  数量: {len(error_list)}")
            report_lines.append(f"  解决方案: {error_list[0]['solution']}")
            
            # 显示前3个错误的详细信息
            for i, error in enumerate(error_list[:3]):
                report_lines.append(f"  {i+1}. {error['details']}")
            
            if len(error_list) > 3:
                report_lines.append(f"  ... 还有{len(error_list)-3}个类似错误")
        
        # 总体建议
        report_lines.append("\n💡 总体修复建议:")
        
        if any(e['type'] == 'edit_failed_exact_match' for e in errors):
            report_lines.append("1. 📝 文件编辑问题:")
            report_lines.append("   • 使用更精确的文本匹配")
            report_lines.append("   • 先读取文件内容确认要编辑的部分")
            report_lines.append("   • 考虑使用write工具替代复杂编辑")
            report_lines.append("   • 建立文件版本快照机制")
        
        if any(e['type'] == 'edit_failed_not_unique' for e in errors):
            report_lines.append("2. 🔍 文本不唯一问题:")
            report_lines.append("   • 提供更多上下文使匹配文本唯一")
            report_lines.append("   • 使用行号或特定标识符")
            report_lines.append("   • 考虑使用正则表达式匹配")
        
        if any(e['type'] == 'http_400_error' for e in errors):
            report_lines.append("3. 🌐 HTTP 400错误:")
            report_lines.append("   • 简化消息格式，避免复杂卡片")
            report_lines.append("   • 检查飞书API权限配置")
            report_lines.append("   • 使用纯文本消息替代卡片消息")
            report_lines.append("   • 建立消息格式验证机制")
        
        # 最佳实践
        report_lines.append("\n🚀 工具使用最佳实践:")
        report_lines.append("1. 精确匹配: 编辑前先确认文件内容和格式")
        report_lines.append("2. 唯一标识: 使用足够独特的文本进行匹配")
        report_lines.append("3. 简化操作: 复杂编辑分步进行，使用write工具")
        report_lines.append("4. 错误处理: 添加适当的错误处理和重试机制")
        report_lines.append("5. 日志记录: 详细记录工具使用情况便于调试")
        
        report_lines.append("\n" + "=" * 60)
        
        return '\n'.join(report_lines)
    
    def create_edit_helper_script(self) -> str:
        """创建编辑助手脚本"""
        script_content = '''#!/usr/bin/env python3
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
    lines = content.split('\\n')
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
                'context': '\\n'.join(context)
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
'''
        
        return script_content
    
    def create_best_practices_guide(self) -> str:
        """创建最佳实践指南"""
        guide = '''# 工具使用最佳实践指南

## 1. edit工具使用规范

### 基本原则
- **精确匹配**: 确保oldText与文件中的内容完全一致（包括空格、换行、缩进）
- **唯一性**: 确保匹配文本在文件中是唯一的
- **安全性**: 编辑前先备份或确认文件内容

### 推荐流程
1. **读取确认**: 先使用read工具读取文件内容
2. **文本验证**: 确认要编辑的文本存在且唯一
3. **精确复制**: 从文件中复制确切的文本（包括格式）
4. **执行编辑**: 使用edit工具进行编辑
5. **验证结果**: 编辑后读取文件确认修改正确

### 常见问题及解决方案

#### 问题1: "Could not find the exact text"
**原因**: 文本不匹配（空格、换行、缩进不一致）
**解决**:
```python
# 错误示例 - 缩进不一致
oldText = "def my_function():"
# 正确示例 - 从文件中精确复制
oldText = "    def my_function():"
```

#### 问题2: "Found X occurrences of the text"
**原因**: 文本不唯一
**解决**:
```python
# 错误示例 - 文本太通用
oldText = "import pandas"
# 正确示例 - 添加更多上下文
oldText = "import pandas as pd\\nimport numpy as np\\n"
```

## 2. write工具使用规范

### 何时使用write替代edit
- 创建新文件时
- 完全重写文件内容时
- 编辑内容较多或复杂时
- edit工具多次失败时

### 推荐用法
```python
# 先读取现有内容（如果需要保留部分）
with open('file.py', 'r') as f:
    existing_content = f.read()

# 修改内容
new_content = existing_content.replace('old', 'new')

# 使用write工具
write('file.py', new_content)
```

## 3. 错误处理最佳实践

### 预防性检查
```python
# 编辑前检查文件是否存在
if not os.path.exists(filepath):
    print(f"文件不存在: {filepath}")
    return

# 编辑前检查文本是否唯一
content = read(filepath)
occurrences = content.count(oldText)
if occurrences != 1:
    print(f"警告: 文本出现{occurrences}次，可能不唯一")
```

### 优雅降级
```python
try:
    # 尝试使用edit工具
    edit(filepath, oldText, newText)
except EditError as e:
    print(f"edit失败: {e}")
    # 降级到write工具
    content = read(filepath)
    new_content = content.replace(oldText, newText)
    write(filepath, new_content)
```

## 4. 性能优化建议

### 批量操作
```python
# 避免频繁的小编辑
# 不好: 多次edit调用
edit(file1, old1, new1)
edit(file2, old2, new2)
edit(file3, old3, new3)

# 好: 批量处理
updates = [
    (file1, old1, new1),
    (file2, old2, new2),
    (file3, old3, new3)
]
for filepath, old_text, new_text in updates:
    edit(filepath, old_text, new_text)
```

### 缓存机制
```python
# 缓存文件内容，避免重复读取
file_cache = {}

def get_file_content(filepath):
    if filepath not in file_cache:
        file_cache[filepath] = read(filepath)
    return file_cache[filepath]
```

## 5. 调试技巧

### 详细日志
```python
import logging

logging.basicConfig(level=logging.DEBUG)

def safe_edit(filepath, oldText, newText):
    logging.debug(f"编辑文件: {filepath}")
    logging.debug(f"旧文本长度: {len(oldText)}")
    logging.debug(f"新文本长度: {len(newText)}")
    
    try:
        edit(filepath, oldText, newText)
        logging.info("编辑成功")
    except Exception as e:
        logging.error(f"编辑失败: {e}")
        raise
```

### 验证机制
```python
def verify_edit(filepath, expected_old, expected_new):
    """验证编辑结果"""
    content = read(filepath)
    
    if expected_old in content:
        print(f"❌ 旧文本仍然存在")
        return False
    
    if expected_new not in content:
        print(f"❌ 新文本未找到")
        return False
    
    print("✅ 编辑验证通过")
    return True
```

## 6. 工具选择决策树

```
是否需要编辑文件？
    ├── 是 → 文件是否存在？
    │       ├── 是 → 要编辑的内容是否唯一？
    │       │       ├── 是 → 使用edit工具
    │       │       └── 否 → 添加更多上下文或使用write工具
    │       └── 否 → 使用write工具创建文件
    └── 否 → 不需要工具操作
```

## 7. 紧急修复流程

### 当edit工具频繁失败时
1. **立即停止**: 停止当前的编辑操作
2. **分析原因**: 查看错误日志，确定问题类型
3. **临时方案**: 使用write工具作为临时解决方案
4. **根本解决**: 分析根本原因，更新编辑策略
5. **预防措施**: 更新最佳实践指南，防止再次发生

## 总结

工具使用质量直接影响项目效率和稳定性。遵循最佳实践可以：
- 减少错误和失败
- 提高开发效率
- 增强代码可维护性
- 降低调试成本

记住：**预防优于修复**，在工具使用前多花一分钟检查，可以节省后续数小时的调试时间。
'''
        
        return guide


def main():
    """主函数"""
    print("工具使用修复器启动...")
    
    # 示例错误日志（从用户提供的信息）
    error_log = """
17:47:09 error [tools] edit failed: Could not find the exact text in scripts/data_quality_validator.py. The old text must match exactly including all whitespace and newlines.
17:47:09 error [tools] edit failed: Could not find the exact text in scripts/data_quality_validator.py. The old text must match exactly including all whitespace and newlines.
17:49:25 error [tools] edit failed: Could not find the exact text in scripts/final_financial_monitor_fixed.py. The old text must match exactly including all whitespace and newlines.
17:49:25 error [tools] edit failed: Could not find the exact text in scripts/final_financial_monitor_fixed.py. The old text must match exactly including all whitespace and newlines.
17:54:06 error gateway/channels/feishu feishu: streaming start failed: Error: Create card request failed with HTTP 400
18:01:16 error gateway/channels/feishu feishu: streaming start failed: Error: Create card request failed with HTTP 400
18:10:12 error [tools] edit failed: Found 14 occurrences of the text in skills/multi-source-fetcher/multi_source_fetcher.py. The text must be unique. Please provide more context to make it unique.
18:10:12 error [tools] edit failed: Found 14 occurrences of the text in skills/multi-source-fetcher/multi_source_fetcher.py. The text must be unique. Please provide more context to make it unique.
18:16:55 error [tools] edit failed: Could not find the exact text in skills/feishu-messenger/feishu_messenger.py. The old text must match exactly including all whitespace and newlines.
18:16:56 error [tools] edit failed: Could not find the exact text in skills/feishu-messenger/feishu_messenger.py. The old text must match exactly including all whitespace and newlines.
18:21:16 error gateway/channels/feishu feishu: streaming start failed: Error: Create card request failed with HTTP 400
"""
    
    fixer = ToolUsageFixer()
    
    # 分析错误日志
    errors = fixer.analyze_error_log(error_log)
    
    # 生成修复报告
    report = fixer.generate_fix_report(errors)
    print(report)
    
    # 创建编辑助手脚本
    print("\n" + "=" * 60)
    print("创建编辑助手脚本...")
    edit_helper = fixer.create_edit_helper_script()
    
    helper_path = "scripts/edit_helper.py"
    with open(helper_path, 'w', encoding='utf-8') as f:
        f.write(edit_helper)
    
    print(f"✅ 编辑助手脚本已保存: {helper_path}")
    print("用法: python3 scripts/edit_helper.py <文件路径> <要查找的文本>")
    
    # 创建最佳实践指南
    print("\n" + "=" * 60)
    print("创建最佳实践指南...")
    best_practices = fixer.create_best_practices_guide()
    
    guide_path = "docs/tool_usage_best_practices.md"
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(best_practices)
    
    print(f"✅ 最佳实践指南已保存: {guide_path}")
    
    # 总结
    print("\n" + "=" * 60)
    print("🎯 下一步行动:")
    print("1. 运行编辑助手脚本验证编辑参数")
    print("2. 阅读最佳实践指南，更新工具使用习惯")
    print("3. 实施错误预防措施，减少工具使用失败")
    print("4. 定期回顾和优化工具使用策略")
    print("=" * 60)


if __name__ == "__main__":
    main()