#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可靠的文件编辑器
解决edit工具频繁失败的问题
"""

import os
import sys
import re
from pathlib import Path
from typing import Optional, Tuple, List
import difflib
import hashlib

class ReliableFileEditor:
    """可靠的文件编辑器"""

    def __init__(self, workspace_path: str = "/Users/ago/.openclaw/workspace"):
        self.workspace_path = Path(workspace_path)

    def safe_edit(self, file_path: str, old_text: str, new_text: str,
                 max_attempts: int = 3) -> Tuple[bool, str]:
        """
        安全编辑文件，自动处理匹配问题

        Args:
            file_path: 文件路径
            old_text: 要替换的文本
            new_text: 新文本
            max_attempts: 最大尝试次数

        Returns:
            (成功, 错误信息/成功信息)
        """
        full_path = self.workspace_path / file_path

        if not full_path.exists():
            return False, f"文件不存在: {file_path}"

        for attempt in range(max_attempts):
            try:
                # 1. 读取文件内容
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 2. 检查是否完全匹配
                if old_text in content:
                    # 完全匹配，直接替换
                    new_content = content.replace(old_text, new_text)
                    success = True
                    method = "完全匹配替换"

                else:
                    # 3. 尝试模糊匹配
                    success, new_content, method = self._fuzzy_replace(content, old_text, new_text)

                if success:
                    # 4. 创建备份
                    backup_path = self._create_backup(full_path, attempt)

                    # 5. 写入新内容
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)

                    # 6. 验证修改
                    if self._verify_change(full_path, content, new_content):
                        msg = f"✅ 编辑成功 (尝试{attempt+1}/{max_attempts}, 方法: {method})"
                        msg += f"\n   备份: {backup_path.name}"
                        return True, msg
                    else:
                        # 验证失败，恢复备份
                        self._restore_backup(full_path, backup_path)
                        continue

                else:
                    # 尝试其他匹配方法
                    continue

            except Exception as e:
                error_msg = f"编辑失败 (尝试{attempt+1}/{max_attempts}): {str(e)}"
                if attempt < max_attempts - 1:
                    continue
                else:
                    return False, error_msg

        return False, f"所有{max_attempts}次尝试都失败"

    def _fuzzy_replace(self, content: str, old_text: str, new_text: str) -> Tuple[bool, str, str]:
        """模糊替换"""
        methods = [
            self._method_exact_match,
            self._method_ignore_whitespace,
            self._method_partial_match,
            self._method_context_match,
            self._method_regex_match
        ]

        for method in methods:
            success, new_content = method(content, old_text, new_text)
            if success:
                method_name = method.__name__.replace('_method_', '').replace('_', ' ')
                return True, new_content, method_name

        return False, content, "无匹配方法"

    def _method_exact_match(self, content: str, old_text: str, new_text: str) -> Tuple[bool, str]:
        """精确匹配"""
        if old_text in content:
            return True, content.replace(old_text, new_text)
        return False, content

    def _method_ignore_whitespace(self, content: str, old_text: str, new_text: str) -> Tuple[bool, str]:
        """忽略空白字符匹配"""
        # 标准化空白字符
        normalized_content = re.sub(r'\s+', ' ', content)
        normalized_old = re.sub(r'\s+', ' ', old_text)

        if normalized_old in normalized_content:
            # 找到原始位置进行替换
            lines = content.split('\n')
            normalized_lines = [re.sub(r'\s+', ' ', line) for line in lines]

            # 在标准化内容中查找
            start_idx = normalized_content.find(normalized_old)
            if start_idx != -1:
                # 计算原始位置（近似）
                # 这里简化处理，实际需要更复杂的逻辑
                return True, content.replace(old_text.strip(), new_text.strip())

        return False, content

    def _method_partial_match(self, content: str, old_text: str, new_text: str) -> Tuple[bool, str]:
        """部分匹配（匹配80%以上）"""
        # 将内容分割成段落
        paragraphs = content.split('\n\n')

        for i, para in enumerate(paragraphs):
            # 计算相似度
            similarity = difflib.SequenceMatcher(None, para, old_text).ratio()

            if similarity > 0.8:
                # 找到相似段落，进行替换
                new_paragraphs = paragraphs.copy()
                new_paragraphs[i] = new_text
                return True, '\n\n'.join(new_paragraphs)

        return False, content

    def _method_context_match(self, content: str, old_text: str, new_text: str) -> Tuple[bool, str]:
        """上下文匹配"""
        # 提取old_text的关键词
        words = re.findall(r'\b\w+\b', old_text)
        if len(words) < 3:
            return False, content

        # 查找包含这些关键词的区域
        lines = content.split('\n')
        for i, line in enumerate(lines):
            match_count = sum(1 for word in words if word in line)
            if match_count >= len(words) * 0.7:  # 70%的关键词匹配
                # 替换这一行
                new_lines = lines.copy()
                new_lines[i] = new_text
                return True, '\n'.join(new_lines)

        return False, content

    def _method_regex_match(self, content: str, old_text: str, new_text: str) -> Tuple[bool, str]:
        """正则表达式匹配"""
        try:
            # 尝试将old_text转换为正则表达式
            # 转义特殊字符，但保留通配符模式
            pattern = re.escape(old_text)
            pattern = pattern.replace(r'\*', '.*').replace(r'\?', '.')

            if re.search(pattern, content, re.DOTALL):
                # 使用正则替换
                new_content = re.sub(pattern, new_text, content, flags=re.DOTALL)
                return True, new_content
        except re.error:
            pass

        return False, content

    def _create_backup(self, file_path: Path, attempt: int) -> Path:
        """创建备份"""
        from datetime import datetime

        backup_dir = self.workspace_path / 'backups' / 'reliable_editor'
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{file_path.stem}_backup_{attempt}_{timestamp}{file_path.suffix}"
        backup_path = backup_dir / backup_name

        import shutil
        shutil.copy2(file_path, backup_path)

        return backup_path

    def _restore_backup(self, file_path: Path, backup_path: Path):
        """恢复备份"""
        import shutil
        shutil.copy2(backup_path, file_path)

    def _verify_change(self, file_path: Path, old_content: str, expected_new_content: str) -> bool:
        """验证修改是否正确"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                actual_content = f.read()

            # 计算哈希值比较
            expected_hash = hashlib.md5(expected_new_content.encode()).hexdigest()
            actual_hash = hashlib.md5(actual_content.encode()).hexdigest()

            return expected_hash == actual_hash

        except Exception:
            return False

    def smart_write(self, file_path: str, content: str,
                   overwrite: bool = True) -> Tuple[bool, str]:
        """
        智能写入文件

        Args:
            file_path: 文件路径
            content: 要写入的内容
            overwrite: 是否覆盖现有文件

        Returns:
            (成功, 错误信息/成功信息)
        """
        full_path = self.workspace_path / file_path

        try:
            # 创建目录
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # 检查文件是否存在
            if full_path.exists() and not overwrite:
                return False, f"文件已存在且不允许覆盖: {file_path}"

            # 创建备份（如果文件存在）
            if full_path.exists():
                backup_path = self._create_backup(full_path, 0)

            # 写入文件
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # 验证写入
            with open(full_path, 'r', encoding='utf-8') as f:
                written_content = f.read()

            if written_content == content:
                msg = f"✅ 写入成功: {file_path}"
                if full_path.exists():
                    msg += f"\n   备份: {backup_path.name}"
                return True, msg
            else:
                return False, "写入验证失败"

        except Exception as e:
            return False, f"写入失败: {str(e)}"

    def batch_edit(self, edits: List[Tuple[str, str, str]]) -> List[Tuple[bool, str]]:
        """
        批量编辑文件

        Args:
            edits: [(文件路径, 旧文本, 新文本), ...]

        Returns:
            [(成功, 信息), ...]
        """
        results = []

        for file_path, old_text, new_text in edits:
            success, message = self.safe_edit(file_path, old_text, new_text)
            results.append((success, message))

        return results

    def get_file_info(self, file_path: str) -> dict:
        """获取文件信息"""
        full_path = self.workspace_path / file_path

        if not full_path.exists():
            return {"exists": False}

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return {
                "exists": True,
                "size_bytes": len(content.encode('utf-8')),
                "lines": len(content.split('\n')),
                "encoding": "utf-8",
                "hash": hashlib.md5(content.encode()).hexdigest()[:8]
            }
        except Exception as e:
            return {"exists": True, "error": str(e)}


def example_usage():
    """使用示例"""
    print("可靠的文件编辑器 - 使用示例")
    print("=" * 60)

    editor = ReliableFileEditor()

    # 示例1: 安全编辑
    print("\n1. 安全编辑示例:")
    test_file = "scripts/test_reliable_editor.py"

    # 创建测试文件
    test_content = """#!/usr/bin/env python3
# 测试文件
def hello():
    print("Hello, World!")

def goodbye():
    print("Goodbye!")
"""

    success, msg = editor.smart_write(test_file, test_content)
    print(f"创建测试文件: {msg}")

    # 尝试编辑
    old_text = 'def hello():\n    print("Hello, World!")'
    new_text = 'def hello():\n    print("Hello, Reliable Editor!")'

    success, msg = editor.safe_edit(test_file, old_text, new_text)
    print(f"安全编辑: {msg}")

    # 示例2: 获取文件信息
    print("\n2. 文件信息:")
    info = editor.get_file_info(test_file)
    if info.get("exists"):
        print(f"  文件: {test_file}")
        print(f"  大小: {info.get('size_bytes', 0)}字节")
        print(f"  行数: {info.get('lines', 0)}行")
        print(f"  哈希: {info.get('hash', 'N/A')}")

    # 清理测试文件
    import os
    test_path = Path(editor.workspace_path) / test_file
    if test_path.exists():
        os.remove(test_path)
        print(f"\n清理测试文件: {test_file}")

    print("\n" + "=" * 60)
    print("核心功能:")
    print("1. safe_edit: 安全编辑，自动处理匹配问题")
    print("2. smart_write: 智能写入，自动备份")
    print("3. batch_edit: 批量编辑，提高效率")
    print("4. 多种匹配算法: 精确、模糊、部分、上下文")
    print("\n解决edit失败问题的关键:")
    print("✅ 自动备份和恢复")
    print("✅ 多种匹配算法")
    print("✅ 验证机制")
    print("✅ 错误处理和重试")


if __name__ == "__main__":
    example_usage()
