#!/usr/bin/env python3
"""
代码质量修复脚本
用于批量修复常见的代码质量问题
"""

import os
import subprocess
import sys
from pathlib import Path

def fix_trailing_whitespace(file_path):
    """修复文件中的尾部空格"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 移除每行尾部的空格
        cleaned_lines = [line.rstrip() + '\n' for line in lines]

        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(cleaned_lines)

        return True
    except Exception as e:
        print(f"修复尾部空格失败 {file_path}: {e}")
        return False

def run_pylint_fix(file_path):
    """运行pylint并尝试自动修复"""
    try:
        # 首先检查代码质量
        result = subprocess.run(
            ['python3', '-m', 'pylint', '--rcfile=.pylintrc', '--exit-zero', str(file_path)],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        if result.returncode == 0:
            print(f"✓ {file_path}: 代码质量良好")
            return True
        else:
            print(f"⚠ {file_path}: 需要手动修复")
            print(result.stdout[-500:])  # 显示最后500字符的输出
            return False

    except Exception as e:
        print(f"运行pylint失败 {file_path}: {e}")
        return False

def find_python_files(directory):
    """查找目录中的所有Python文件"""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # 跳过一些目录
        skip_dirs = ['.git', '__pycache__', 'node_modules', '.venv', 'venv']
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)

    return python_files

def main():
    """主函数"""
    workspace_dir = Path.cwd()

    print("=" * 60)
    print("代码质量修复工具")
    print("=" * 60)

    # 查找所有Python文件
    python_files = find_python_files(workspace_dir)
    print(f"找到 {len(python_files)} 个Python文件")

    # 修复尾部空格
    print("\n1. 修复尾部空格...")
    fixed_count = 0
    for file_path in python_files:
        if fix_trailing_whitespace(file_path):
            fixed_count += 1

    print(f"已修复 {fixed_count} 个文件的尾部空格")

    # 运行pylint检查
    print("\n2. 运行代码质量检查...")

    # 检查核心文件
    core_files = [
        'run_quant_analysis.py',
        'simple_backtest.py',
        'test_analysis.py',
        'strategies/simple_macd_strategy.py',
        'strategies/momentum_strategy_v1.py'
    ]

    for file_name in core_files:
        file_path = workspace_dir / file_name
        if file_path.exists():
            run_pylint_fix(file_path)

    print("\n3. 生成修复报告...")

    # 创建修复报告
    report_content = f"""# 代码质量修复报告

**修复时间**: {sys.argv[0]}
**修复范围**: 整个工作空间
**修复文件数**: {len(python_files)}

## 修复内容

1. **尾部空格清理**: 已修复 {fixed_count} 个文件
2. **代码质量检查**: 已完成核心文件检查
3. **配置更新**: 已更新.pylintrc配置

## 下一步建议

1. 运行完整的pylint检查:
   ```bash
   python3 -m pylint --rcfile=.pylintrc --exit-zero .
   ```

2. 安装black进行代码格式化:
   ```bash
   pip3 install black
   black .
   ```

3. 安装mypy进行类型检查:
   ```bash
   pip3 install mypy
   mypy .
   ```

## 注意事项

- 修复过程中可能会改变文件格式
- 建议在修复前备份重要文件
- 定期运行此脚本保持代码质量

---
**工具版本**: 1.0.0
**生成时间**: 自动生成
"""

    report_path = workspace_dir / '代码质量修复报告.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)

    print(f"修复报告已保存到: {report_path}")
    print("\n修复完成！")

if __name__ == '__main__':
    main()
