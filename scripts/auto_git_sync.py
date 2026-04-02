#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub自动同步脚本
自动检测变更并提交到GitHub
"""

import os
import subprocess
import json
from datetime import datetime
from pathlib import Path


class AutoGitSync:
    """GitHub自动同步器"""

    def __init__(self, workspace_dir=None):
        self.workspace_dir = workspace_dir or "/Users/ago/.openclaw/workspace"
        self.config_file = os.path.join(self.workspace_dir, ".auto_git_sync.json")
        self.config = self._load_config()

        print(f"🚀 GitHub自动同步器初始化")
        print(f"   工作空间: {self.workspace_dir}")
        print(f"   分支: {self.config.get('branch', 'develop')}")

    def _load_config(self):
        """加载配置"""
        default_config = {
            "enabled": True,
            "branch": "develop",
            "auto_commit": True,
            "auto_push": True,
            "commit_message_template": "auto: {timestamp} - {change_count} files changed",
            "schedule": "10 0,12 * * *",  # 每日00:10和12:10
            "last_check_time": None,
            "last_commit_hash": None,
            "exclude_patterns": [
                "*.log",
                "*.tmp",
                "*.bak",
                ".openclaw/*",
                "memory/*.md",
                "__pycache__/*",
                "*.pyc"
            ]
        }

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                # 合并配置
                default_config.update(user_config)
            except Exception as e:
                print(f"⚠️ 加载配置失败: {e}")

        return default_config

    def _save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"⚠️ 保存配置失败: {e}")

    def check_for_changes(self):
        """检查是否有变更"""
        print(f"\n🔍 检查Git变更...")

        try:
            # 切换到工作目录
            os.chdir(self.workspace_dir)

            # 检查git状态
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True
            )

            changes = result.stdout.strip()

            if changes:
                change_count = len(changes.split('\n'))
                print(f"✅ 发现 {change_count} 个变更")

                # 显示变更摘要
                print(f"\n📋 变更摘要:")
                for line in changes.split('\n')[:10]:  # 只显示前10个
                    if line:
                        status = line[:2]
                        file = line[3:]
                        print(f"  {status} {file}")

                if len(changes.split('\n')) > 10:
                    print(f"  ... 还有更多变更")

                return True, change_count, changes
            else:
                print(f"✅ 没有变更需要提交")
                return False, 0, ""

        except subprocess.CalledProcessError as e:
            print(f"❌ Git命令执行失败: {e}")
            return False, 0, ""
        except Exception as e:
            print(f"❌ 检查变更失败: {e}")
            return False, 0, ""

    def auto_commit(self, change_count):
        """自动提交变更"""
        if not self.config.get('auto_commit', True):
            print(f"⏸️  自动提交已禁用")
            return False

        print(f"\n💾 自动提交变更...")

        try:
            # 生成提交消息
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            commit_message = self.config['commit_message_template'].format(
                timestamp=timestamp,
                change_count=change_count
            )

            # 添加所有变更
            subprocess.run(["git", "add", "."], check=True)
            print(f"  ✅ 添加变更到暂存区")

            # 提交
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            print(f"  ✅ 提交: {commit_message}")

            # 获取提交哈希
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                check=True
            )
            commit_hash = result.stdout.strip()[:8]
            self.config['last_commit_hash'] = commit_hash

            print(f"  📝 提交哈希: {commit_hash}")

            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ 提交失败: {e}")
            return False

    def auto_push(self):
        """自动推送到远程"""
        if not self.config.get('auto_push', True):
            print(f"⏸️  自动推送已禁用")
            return False

        print(f"\n🚀 推送到GitHub...")

        try:
            branch = self.config.get('branch', 'develop')

            # 推送到远程
            result = subprocess.run(
                ["git", "push", "origin", branch],
                capture_output=True,
                text=True,
                check=True
            )

            print(f"✅ 推送成功到 {branch} 分支")

            # 更新配置
            self.config['last_check_time'] = datetime.now().isoformat()
            self._save_config()

            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ 推送失败: {e}")
            print(f"   错误输出: {e.stderr}")
            return False

    def run_sync(self):
        """运行同步"""
        print("=" * 60)
        print("🔄 GitHub自动同步")
        print("=" * 60)

        if not self.config.get('enabled', True):
            print("⏸️  自动同步已禁用")
            return False

        # 检查变更
        has_changes, change_count, changes = self.check_for_changes()

        if not has_changes:
            print(f"\n✅ 同步完成 - 没有变更")
            return True

        # 自动提交
        commit_success = self.auto_commit(change_count)
        if not commit_success:
            print(f"\n❌ 同步失败 - 提交错误")
            return False

        # 自动推送
        push_success = self.auto_push()
        if not push_success:
            print(f"\n❌ 同步失败 - 推送错误")
            return False

        print(f"\n🎉 同步成功!")
        print(f"   变更文件: {change_count} 个")
        print(f"   提交时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   分支: {self.config.get('branch', 'develop')}")

        return True

    def setup_cron_job(self):
        """设置定时任务"""
        print(f"\n⏰ 设置定时同步任务...")

        # 创建cron任务配置 - 改为每日两次：00:10和12:10
        cron_config = {
            "name": "GitHub自动同步",
            "schedule": "10 0,12 * * *",
            "command": f"cd {self.workspace_dir} && python3 scripts/auto_git_sync.py --check",
            "description": "每日00:10和12:10自动同步代码到GitHub"
        }

        cron_file = os.path.join(self.workspace_dir, ".github_auto_sync_cron.json")
        with open(cron_file, 'w') as f:
            json.dump(cron_config, f, indent=2)

        print(f"✅ 定时任务配置已保存: {cron_file}")
        print(f"\n📋 配置详情:")
        print(f"   检查间隔: 每{self.config['check_interval_minutes']}分钟")
        print(f"   工作目录: {self.workspace_dir}")
        print(f"   分支: {self.config.get('branch', 'develop')}")
        print(f"   自动提交: {'启用' if self.config.get('auto_commit') else '禁用'}")
        print(f"   自动推送: {'启用' if self.config.get('auto_push') else '禁用'}")

        # 创建OpenClaw调度任务
        self._create_openclaw_cron_job()

        return True

    def _create_openclaw_cron_job(self):
        """创建OpenClaw调度任务"""
        print(f"\n📅 创建OpenClaw调度任务...")

        # 这里可以集成OpenClaw的cron API
        # 目前先创建配置说明

        setup_guide = f"""
# 📅 GitHub自动同步 - OpenClaw调度配置

## 手动创建调度任务
```bash
openclaw cron add \\
  --name "GitHub自动同步" \\
  --schedule "*/{self.config['check_interval_minutes']} * * * *" \\
  --command "cd {self.workspace_dir} && python3 scripts/auto_git_sync.py --check" \\
  --description "自动同步代码变更到GitHub"
```

## 验证任务
```bash
# 查看所有任务
openclaw cron list --all

# 手动测试
cd {self.workspace_dir} && python3 scripts/auto_git_sync.py --check
```

## 配置说明
- 检查间隔: {self.config['check_interval_minutes']}分钟
- 工作分支: {self.config.get('branch', 'develop')}
- 自动提交: {'是' if self.config.get('auto_commit') else '否'}
- 自动推送: {'是' if self.config.get('auto_push') else '否'}
"""

        guide_file = os.path.join(self.workspace_dir, "docs/github_auto_sync_setup.md")
        with open(guide_file, 'w') as f:
            f.write(setup_guide)

        print(f"✅ 配置指南已保存: {guide_file}")

        return True

    def show_status(self):
        """显示状态"""
        print("=" * 60)
        print("📊 GitHub自动同步状态")
        print("=" * 60)

        print(f"\n🔧 配置状态:")
        print(f"   启用状态: {'✅ 已启用' if self.config.get('enabled') else '❌ 已禁用'}")
        print(f"   工作分支: {self.config.get('branch', 'develop')}")
        print(f"   自动提交: {'✅ 启用' if self.config.get('auto_commit') else '❌ 禁用'}")
        print(f"   自动推送: {'✅ 启用' if self.config.get('auto_push') else '❌ 禁用'}")
        print(f"   同步时间: {self.config.get('schedule', '10 0,12 * * *')} (每日00:10和12:10)")

        if self.config.get('last_check_time'):
            print(f"   最后检查: {self.config['last_check_time']}")

        if self.config.get('last_commit_hash'):
            print(f"   最后提交: {self.config['last_commit_hash']}")

        # 检查当前状态
        print(f"\n🔍 当前Git状态:")
        try:
            os.chdir(self.workspace_dir)

            # 分支信息
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                check=True
            )
            current_branch = branch_result.stdout.strip()
            print(f"   当前分支: {current_branch}")

            # 远程状态
            remote_result = subprocess.run(
                ["git", "remote", "-v"],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"   远程仓库: {remote_result.stdout.split()[1] if remote_result.stdout else '无'}")

            # 未提交变更
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True
            )
            pending_changes = len(status_result.stdout.strip().split('\n')) if status_result.stdout.strip() else 0
            print(f"   待提交变更: {pending_changes} 个")

        except Exception as e:
            print(f"   检查失败: {e}")

        print(f"\n🎯 使用说明:")
        print(f"   立即同步: python3 scripts/auto_git_sync.py --check")
        print(f"   设置定时: python3 scripts/auto_git_sync.py --setup")
        print(f"   查看状态: python3 scripts/auto_git_sync.py --status")

        return True


def main():
    """主函数"""
    import sys

    sync = AutoGitSync()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--check":
            # 检查并同步
            sync.run_sync()
        elif sys.argv[1] == "--setup":
            # 设置定时任务
            sync.setup_cron_job()
        elif sys.argv[1] == "--status":
            # 显示状态
            sync.show_status()
        elif sys.argv[1] == "--help":
            print("""
GitHub自动同步工具

使用方法:
  --check    检查并同步变更
  --setup    设置定时同步任务
  --status   显示当前状态
  --help     显示帮助信息

示例:
  python3 scripts/auto_git_sync.py --check
  python3 scripts/auto_git_sync.py --setup
  python3 scripts/auto_git_sync.py --status
""")
        else:
            print(f"❌ 未知参数: {sys.argv[1]}")
            print("使用 --help 查看帮助")
    else:
        # 默认运行同步
        sync.run_sync()


if __name__ == "__main__":
    main()
