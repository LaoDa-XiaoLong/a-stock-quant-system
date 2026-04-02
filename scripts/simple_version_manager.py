#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版版本管理器
快速实施版本管理基础功能
"""

import json
import os
import shutil
from datetime import datetime
import sys


class SimpleVersionManager:
    """简化版版本管理器"""

    def __init__(self):
        self.base_dir = "version_management"
        self.registry_file = os.path.join(self.base_dir, "version_registry.json")

        # 确保目录存在
        os.makedirs(self.base_dir, exist_ok=True)

        # 加载或创建注册表
        self.registry = self._load_registry()

        print("📦 简化版版本管理器初始化完成")

    def _load_registry(self):
        """加载版本注册表"""
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self._create_default_registry()
        else:
            return self._create_default_registry()

    def _create_default_registry(self):
        """创建默认注册表"""
        registry = {
            "metadata": {
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            },
            "categories": {}
        }
        self._save_registry(registry)
        return registry

    def _save_registry(self, registry=None):
        """保存注册表"""
        if registry is None:
            registry = self.registry

        registry["metadata"]["last_updated"] = datetime.now().isoformat()

        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, ensure_ascii=False, indent=2)

        return True

    def create_version(self, category, name, version, source_path, description=""):
        """创建新版本"""
        print(f"🚀 创建版本: {category}/{name}/{version}")

        # 创建类别目录
        category_dir = os.path.join(self.base_dir, category, name)
        os.makedirs(category_dir, exist_ok=True)

        # 创建版本目录
        version_dir = os.path.join(category_dir, version)
        os.makedirs(version_dir, exist_ok=True)

        # 复制文件
        try:
            if os.path.isfile(source_path):
                shutil.copy2(source_path, version_dir)
                print(f"  📄 复制文件: {os.path.basename(source_path)}")
            elif os.path.isdir(source_path):
                for item in os.listdir(source_path):
                    src = os.path.join(source_path, item)
                    dst = os.path.join(version_dir, item)
                    if os.path.isdir(src):
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src, dst)
                print(f"  📁 复制目录: {source_path}")
        except Exception as e:
            print(f"  ❌ 复制失败: {e}")
            return False

        # 创建版本信息
        version_info = {
            "version": version,
            "created": datetime.now().isoformat(),
            "description": description,
            "source": source_path,
            "active": False
        }

        # 保存版本信息
        info_file = os.path.join(version_dir, "version_info.json")
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(version_info, f, ensure_ascii=False, indent=2)

        # 更新注册表
        if category not in self.registry["categories"]:
            self.registry["categories"][category] = {}

        if name not in self.registry["categories"][category]:
            self.registry["categories"][category][name] = {
                "current": None,
                "versions": {}
            }

        # 添加版本信息
        self.registry["categories"][category][name]["versions"][version] = {
            "created": version_info["created"],
            "description": description,
            "path": version_dir,
            "active": False
        }

        # 如果是第一个版本，设置为当前
        if self.registry["categories"][category][name]["current"] is None:
            self.registry["categories"][category][name]["current"] = version
            self.registry["categories"][category][name]["versions"][version]["active"] = True

        # 保存注册表
        self._save_registry()

        print(f"  ✅ 版本创建成功")
        return True

    def switch_version(self, category, name, version):
        """切换版本"""
        print(f"🔄 切换版本: {category}/{name} → {version}")

        # 检查版本是否存在
        if (category not in self.registry["categories"] or
            name not in self.registry["categories"][category] or
            version not in self.registry["categories"][category][name]["versions"]):
            print(f"  ❌ 版本不存在")
            return False

        # 更新当前版本
        old_version = self.registry["categories"][category][name]["current"]
        self.registry["categories"][category][name]["current"] = version

        # 更新活跃状态
        if old_version:
            self.registry["categories"][category][name]["versions"][old_version]["active"] = False
        self.registry["categories"][category][name]["versions"][version]["active"] = True

        # 创建软链接
        self._create_symlink(category, name, version)

        # 保存注册表
        self._save_registry()

        print(f"  ✅ 版本切换成功: {old_version or '无'} → {version}")
        return True

    def _create_symlink(self, category, name, version):
        """创建当前版本软链接"""
        try:
            target_dir = os.path.join(self.base_dir, category, name)
            current_link = os.path.join(target_dir, "current")

            # 删除旧链接
            if os.path.exists(current_link):
                os.remove(current_link)

            # 创建新链接
            version_dir = os.path.join(target_dir, version)
            os.symlink(version_dir, current_link)

            print(f"  🔗 创建软链接: current → {version}")
            return True
        except Exception as e:
            print(f"  ⚠️  创建软链接失败: {e}")
            return False

    def list_versions(self, category=None, name=None):
        """列出版本"""
        print("📋 版本列表")
        print("=" * 60)

        if category is None:
            # 列出所有类别
            for cat, items in self.registry["categories"].items():
                print(f"\n📁 {cat}:")
                for item_name, data in items.items():
                    current = data.get("current", "无")
                    count = len(data.get("versions", {}))
                    print(f"  ├─ {item_name}: {count}个版本 (当前: {current})")

        elif name is None:
            # 列出类别下的所有项目
            if category in self.registry["categories"]:
                print(f"\n📁 {category}:")
                for item_name, data in self.registry["categories"][category].items():
                    current = data.get("current", "无")
                    count = len(data.get("versions", {}))
                    print(f"  ├─ {item_name}: {count}个版本 (当前: {current})")

        else:
            # 列出具体项目的所有版本
            if (category in self.registry["categories"] and
                name in self.registry["categories"][category]):

                data = self.registry["categories"][category][name]
                current = data.get("current", "无")
                versions = data.get("versions", {})

                print(f"\n📁 {category}/{name} (当前: {current})")
                print("-" * 40)

                for ver, info in versions.items():
                    active = "✅" if info.get("active", False) else "  "
                    created = info.get("created", "")[:10]
                    desc = info.get("description", "")[:40]
                    print(f"{active} {ver:8} {created} | {desc}")

    def get_current_version(self, category, name):
        """获取当前版本"""
        if (category in self.registry["categories"] and
            name in self.registry["categories"][category]):
            return self.registry["categories"][category][name]["current"]
        return None

    def get_version_path(self, category, name, version=None):
        """获取版本路径"""
        if version is None:
            version = self.get_current_version(category, name)

        if (category in self.registry["categories"] and
            name in self.registry["categories"][category] and
            version in self.registry["categories"][category][name]["versions"]):

            return self.registry["categories"][category][name]["versions"][version]["path"]

        return None


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python simple_version_manager.py <命令>")
        print("命令: list, create, switch")
        return 1

    vm = SimpleVersionManager()
    command = sys.argv[1]

    try:
        if command == "list":
            if len(sys.argv) == 2:
                vm.list_versions()
            elif len(sys.argv) == 3:
                vm.list_versions(category=sys.argv[2])
            elif len(sys.argv) == 4:
                vm.list_versions(category=sys.argv[2], name=sys.argv[3])

        elif command == "create":
            if len(sys.argv) != 6:
                print("用法: create <category> <name> <version> <source_path>")
                return 1

            category = sys.argv[2]
            name = sys.argv[3]
            version = sys.argv[4]
            source_path = sys.argv[5]

            vm.create_version(category, name, version, source_path)

        elif command == "switch":
            if len(sys.argv) != 5:
                print("用法: switch <category> <name> <version>")
                return 1

            category = sys.argv[2]
            name = sys.argv[3]
            version = sys.argv[4]

            vm.switch_version(category, name, version)

        else:
            print(f"未知命令: {command}")
            return 1

        return 0

    except Exception as e:
        print(f"错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
