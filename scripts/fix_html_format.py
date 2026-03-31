#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML格式修复工具
自动修复脚本中的HTML格式问题
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple


class HtmlFormatFixer:
    """HTML格式修复器"""
    
    def __init__(self, workspace_dir: str = None):
        self.workspace_dir = workspace_dir or "/Users/ago/.openclaw/workspace"
        self.scripts_dir = os.path.join(self.workspace_dir, "scripts")
        
        # 需要修复的文件模式
        self.target_patterns = [
            "send_financial_report*.py",
            "*financial*.py",
            "*report*.py"
        ]
        
        # HTML标签修复规则
        self.fix_rules = [
            # <font color='green'>标签
            (
                r"<font\s+color\s*=\s*['\"]green['\"]\s*>([^<]+)</font>",
                lambda m: self._format_green(m.group(1))
            ),
            # <font color='red'>标签
            (
                r"<font\s+color\s*=\s*['\"]red['\"]\s*>([^<]+)</font>",
                lambda m: self._format_red(m.group(1))
            ),
            # <font color='blue'>标签
            (
                r"<font\s+color\s*=\s*['\"]blue['\"]\s*>([^<]+)</font>",
                lambda m: self._format_blue(m.group(1))
            ),
            # <font color='orange'>标签
            (
                r"<font\s+color\s*=\s*['\"]orange['\"]\s*>([^<]+)</font>",
                lambda m: self._format_orange(m.group(1))
            ),
            # <font color='gray'>标签
            (
                r"<font\s+color\s*=\s*['\"]gray['\"]\s*>([^<]+)</font>",
                lambda m: self._format_gray(m.group(1))
            ),
            # <font color='grey'>标签
            (
                r"<font\s+color\s*=\s*['\"]grey['\"]\s*>([^<]+)</font>",
                lambda m: self._format_gray(m.group(1))
            ),
            # 通用<font>标签（其他颜色）
            (
                r"<font\s+color\s*=\s*['\"]([^'\"]+)['\"]\s*>([^<]+)</font>",
                lambda m: self._format_generic(m.group(2), m.group(1))
            ),
            # 其他HTML标签
            (r"<b>([^<]+)</b>", r"**\1**"),      # 粗体 -> Markdown粗体
            (r"<i>([^<]+)</i>", r"*\1*"),        # 斜体 -> Markdown斜体
            (r"<u>([^<]+)</u>", r"\1"),          # 下划线 -> 移除（飞书不支持）
            (r"<strong>([^<]+)</strong>", r"**\1**"),  # 强调 -> Markdown粗体
            (r"<em>([^<]+)</em>", r"*\1*"),      # 强调 -> Markdown斜体
        ]
    
    def _format_green(self, content: str) -> str:
        """格式化绿色内容"""
        content = content.strip()
        
        # 根据内容类型添加不同的表情符号
        if '📈' in content or '+' in content or '超预期' in content:
            return f"🟢📈 {content.replace('📈', '').strip()}"
        elif '✅' in content or '推荐' in content or '成功' in content:
            return f"🟢✅ {content.replace('✅', '').strip()}"
        elif '💰' in content or '利润' in content:
            return f"🟢💰 {content.replace('💰', '').strip()}"
        else:
            return f"🟢 {content}"
    
    def _format_red(self, content: str) -> str:
        """格式化红色内容"""
        content = content.strip()
        
        if '📉' in content or '-' in content or '低于预期' in content:
            return f"🔴📉 {content.replace('📉', '').strip()}"
        elif '🚨' in content or '警报' in content or '减仓' in content:
            return f"🔴🚨 {content.replace('🚨', '').strip()}"
        elif '❌' in content or '失败' in content:
            return f"🔴❌ {content.replace('❌', '').strip()}"
        else:
            return f"🔴 {content}"
    
    def _format_blue(self, content: str) -> str:
        """格式化蓝色内容"""
        content = content.strip()
        
        if '📊' in content or '图表' in content or '数据' in content:
            return f"🔵📊 {content.replace('📊', '').strip()}"
        elif '🔍' in content or '观察' in content:
            return f"🔵🔍 {content.replace('🔍', '').strip()}"
        else:
            return f"🔵 {content}"
    
    def _format_orange(self, content: str) -> str:
        """格式化橙色内容"""
        content = content.strip()
        
        if '⚠️' in content or '警告' in content or '风险' in content:
            return f"🟡⚠️ {content.replace('⚠️', '').strip()}"
        else:
            return f"🟡 {content}"
    
    def _format_gray(self, content: str) -> str:
        """格式化灰色内容"""
        content = content.strip()
        
        if '📋' in content or '维持' in content or '现状' in content:
            return f"⚪📋 {content.replace('📋', '').strip()}"
        else:
            return f"⚪ {content}"
    
    def _format_generic(self, content: str, color: str) -> str:
        """格式化通用颜色内容"""
        content = content.strip()
        
        # 根据颜色选择表情符号
        color_map = {
            'yellow': '🟡',
            'purple': '🟣',
            'black': '⚫',
            'white': '⚪',
            'cyan': '🔵',
            'magenta': '🟣',
        }
        
        emoji = color_map.get(color.lower(), '')
        if emoji:
            return f"{emoji} {content}"
        else:
            return content  # 未知颜色，直接移除标签
    
    def find_files_to_fix(self) -> List[str]:
        """查找需要修复的文件"""
        files_to_fix = []
        
        for pattern in self.target_patterns:
            for file_path in Path(self.scripts_dir).glob(pattern):
                if file_path.is_file() and file_path.suffix == '.py':
                    # 检查文件是否包含HTML标签
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if any(tag in content for tag in ['<font', '<b>', '<i>', '<u>', '<strong>', '<em>']):
                            files_to_fix.append(str(file_path))
        
        return sorted(set(files_to_fix))
    
    def analyze_file(self, file_path: str) -> Dict:
        """分析文件中的HTML格式问题"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        
        # 检查各种HTML标签
        html_patterns = [
            (r'<font[^>]*>', 'font标签'),
            (r'<b>', '粗体标签'),
            (r'<i>', '斜体标签'),
            (r'<u>', '下划线标签'),
            (r'<strong>', '强调标签'),
            (r'<em>', '强调标签'),
        ]
        
        for pattern, tag_name in html_patterns:
            matches = list(re.finditer(pattern, content))
            if matches:
                # 获取上下文
                contexts = []
                for match in matches[:3]:  # 只显示前3个
                    start = max(0, match.start() - 20)
                    end = min(len(content), match.end() + 20)
                    context = content[start:end].replace('\n', ' ')
                    contexts.append(f"...{context}...")
                
                issues.append({
                    'tag': tag_name,
                    'count': len(matches),
                    'examples': contexts
                })
        
        return {
            'file': file_path,
            'issues': issues,
            'total_issues': sum(issue['count'] for issue in issues)
        }
    
    def fix_file(self, file_path: str, backup: bool = True) -> Tuple[bool, str]:
        """修复文件中的HTML格式问题"""
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # 创建备份
            if backup:
                backup_path = f"{file_path}.backup"
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
            
            # 应用修复规则
            fixed_content = original_content
            changes_made = []
            
            for pattern, replacement in self.fix_rules:
                # 统计修复前的匹配数
                matches_before = list(re.finditer(pattern, fixed_content))
                if not matches_before:
                    continue
                
                # 应用替换
                if callable(replacement):
                    # 使用函数进行替换
                    def replace_func(match):
                        return replacement(match)
                    fixed_content = re.sub(pattern, replace_func, fixed_content)
                else:
                    # 使用字符串进行替换
                    fixed_content = re.sub(pattern, replacement, fixed_content)
                
                # 统计修复后的匹配数
                matches_after = list(re.finditer(pattern, fixed_content))
                
                if len(matches_before) > len(matches_after):
                    changes_made.append({
                        'pattern': pattern[:50] + '...' if len(pattern) > 50 else pattern,
                        'fixed': len(matches_before) - len(matches_after),
                        'remaining': len(matches_after)
                    })
            
            # 如果没有变化，不写入文件
            if fixed_content == original_content:
                return False, "没有发现需要修复的HTML格式"
            
            # 写入修复后的内容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            # 生成报告
            report = f"修复完成: {len(changes_made)} 种问题被修复\n"
            for change in changes_made:
                report += f"  • {change['fixed']} 处 {change['pattern']}\n"
            
            if backup:
                report += f"\n备份文件: {file_path}.backup"
            
            return True, report
            
        except Exception as e:
            return False, f"修复失败: {e}"
    
    def generate_migration_report(self, files_to_fix: List[str]) -> str:
        """生成迁移报告"""
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("HTML格式修复迁移报告")
        report_lines.append("=" * 60)
        report_lines.append(f"扫描目录: {self.scripts_dir}")
        report_lines.append(f"发现文件: {len(files_to_fix)} 个")
        report_lines.append("")
        
        total_issues = 0
        for file_path in files_to_fix:
            analysis = self.analyze_file(file_path)
            total_issues += analysis['total_issues']
            
            report_lines.append(f"📄 {os.path.basename(file_path)}")
            report_lines.append(f"   路径: {file_path}")
            report_lines.append(f"   问题数: {analysis['total_issues']}")
            
            for issue in analysis['issues']:
                report_lines.append(f"   • {issue['tag']}: {issue['count']} 处")
                for example in issue['examples'][:1]:  # 只显示一个示例
                    report_lines.append(f"     示例: {example}")
            
            report_lines.append("")
        
        report_lines.append("=" * 60)
        report_lines.append(f"总计: {total_issues} 个HTML格式问题需要修复")
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)
    
    def run(self, dry_run: bool = False, backup: bool = True):
        """运行修复任务"""
        print("🔧 HTML格式修复工具")
        print("=" * 60)
        
        # 1. 查找需要修复的文件
        print("🔍 扫描文件中...")
        files_to_fix = self.find_files_to_fix()
        
        if not files_to_fix:
            print("✅ 没有发现需要修复的文件")
            return True
        
        print(f"📋 发现 {len(files_to_fix)} 个需要修复的文件")
        
        # 2. 生成迁移报告
        report = self.generate_migration_report(files_to_fix)
        print(report)
        
        if dry_run:
            print("🧪 干运行模式：只分析不修改")
            return True
        
        # 3. 确认是否继续（非交互模式自动继续）
        try:
            response = input("\n🚀 是否开始修复？(y/N): ").strip().lower()
            if response != 'y':
                print("❌ 用户取消操作")
                return False
        except EOFError:
            # 非交互模式，自动继续
            print("\n🚀 非交互模式，自动开始修复...")
        
        # 4. 执行修复
        print("\n🔄 开始修复文件...")
        results = []
        
        for file_path in files_to_fix:
            print(f"\n📄 处理: {os.path.basename(file_path)}")
            success, message = self.fix_file(file_path, backup)
            
            if success:
                print(f"  ✅ {message}")
            else:
                print(f"  ❌ {message}")
            
            results.append((file_path, success, message))
        
        # 5. 生成修复报告
        print("\n" + "=" * 60)
        print("📊 修复结果总结")
        print("=" * 60)
        
        success_count = sum(1 for _, success, _ in results if success)
        total_count = len(results)
        
        for file_path, success, message in results:
            filename = os.path.basename(file_path)
            status = "✅ 成功" if success else "❌ 失败"
            print(f"{status} - {filename}")
            if not success and message:
                print(f"    原因: {message}")
        
        print(f"\n🎯 总体成功率: {success_count}/{total_count} ({success_count/total_count*100:.0f}%)")
        
        # 6. 给出后续建议
        print("\n💡 后续步骤建议:")
        print("1. 运行测试验证修复效果:")
        print("   python scripts/test_feishu_format.py")
        print("2. 测试修复后的报告发送:")
        print("   python scripts/send_financial_report_fixed_format.py")
        print("3. 更新相关文档:")
        print("   docs/feishu_format_standard.md")
        print("4. 监控飞书消息显示效果")
        
        return success_count == total_count


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='HTML格式修复工具')
    parser.add_argument('--dry-run', action='store_true', help='干运行模式（只分析不修改）')
    parser.add_argument('--no-backup', action='store_true', help='不创建备份文件')
    parser.add_argument('--workspace', default='/Users/ago/.openclaw/workspace', help='工作空间目录')
    
    args = parser.parse_args()
    
    fixer = HtmlFormatFixer(args.workspace)
    success = fixer.run(
        dry_run=args.dry_run,
        backup=not args.no_backup
    )
    
    exit_code = 0 if success else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()