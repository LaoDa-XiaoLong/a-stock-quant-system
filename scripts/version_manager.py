#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本管理工具
用于管理股票模型、报告模板等核心功能的版本
支持：创建版本、切换版本、对比版本、回滚版本
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, List, Optional
import sys


class VersionManager:
    """版本管理器"""

    def __init__(self, base_dir: str = "version_management"):
        self.base_dir = base_dir
        self.registry_path = os.path.join(base_dir, "version_registry.json")

        # 确保目录存在
        os.makedirs(base_dir, exist_ok=True)

        # 加载或创建版本注册表
        self.registry = self._load_registry()

        print(f"📦 版本管理器初始化完成")
        print(f"📁 基础目录: {base_dir}")
        print(f"📋 注册表: {self.registry_path}")

    def _load_registry(self) -> Dict:
        """加载版本注册表"""
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ 加载注册表失败: {e}")
                return self._create_default_registry()
        else:
            return self._create_default_registry()

    def _create_default_registry(self) -> Dict:
        """创建默认注册表"""
        registry = {
            "version_registry": {
                "stock_models": {},
                "report_templates": {},
                "data_sources": {},
                "utils": {}
            },
            "metadata": {
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_versions": 0
            }
        }

        # 保存注册表
        self._save_registry(registry)
        return registry

    def _save_registry(self, registry: Dict = None):
        """保存版本注册表"""
        if registry is None:
            registry = self.registry

        try:
            # 更新元数据
            registry["metadata"]["last_updated"] = datetime.now().isoformat()

            with open(self.registry_path, 'w', encoding='utf-8') as f:
                json.dump(registry, f, ensure_ascii=False, indent=2)

            print(f"💾 版本注册表已保存: {self.registry_path}")
            return True
        except Exception as e:
            print(f"❌ 保存注册表失败: {e}")
            return False

    def create_category(self, category: str, subcategory: str, description: str = ""):
        """创建版本管理类别"""
        if category not in self.registry["version_registry"]:
            print(f"❌ 无效的类别: {category}")
            print(f"   可用类别: {list(self.registry['version_registry'].keys())}")
            return False

        if subcategory not in self.registry["version_registry"][category]:
            self.registry["version_registry"][category][subcategory] = {
                "current": None,
                "versions": {},
                "description": description
            }
            print(f"✅ 创建类别: {category}/{subcategory}")
            return self._save_registry()
        else:
            print(f"ℹ️  类别已存在: {category}/{subcategory}")
            return True

    def create_version(self, category: str, subcategory: str, version: str,
                      source_path: str, author: str = "小龙",
                      description: str = "", performance: Dict = None):
        """创建新版本"""
        # 检查类别是否存在
        if category not in self.registry["version_registry"]:
            print(f"❌ 类别不存在: {category}")
            return False

        if subcategory not in self.registry["version_registry"][category]:
            print(f"❌ 子类别不存在: {category}/{subcategory}")
            print(f"   请先使用 create_category 创建")
            return False

        # 检查源路径是否存在
        if not os.path.exists(source_path):
            print(f"❌ 源路径不存在: {source_path}")
            return False

        # 创建版本目录
        version_dir = os.path.join(self.base_dir, category, subcategory, version)
        os.makedirs(version_dir, exist_ok=True)

        # 复制文件到版本目录
        try:
            if os.path.isfile(source_path):
                # 单个文件
                shutil.copy2(source_path, version_dir)
                print(f"📄 复制文件: {source_path} → {version_dir}")
            elif os.path.isdir(source_path):
                # 整个目录
                for item in os.listdir(source_path):
                    s = os.path.join(source_path, item)
                    d = os.path.join(version_dir, item)
                    if os.path.isdir(s):
                        shutil.copytree(s, d, dirs_exist_ok=True)
                    else:
                        shutil.copy2(s, d)
                print(f"📁 复制目录: {source_path} → {version_dir}")
        except Exception as e:
            print(f"❌ 复制文件失败: {e}")
            return False

        # 创建版本信息文件
        version_info = {
            "version": version,
            "created": datetime.now().isoformat(),
            "author": author,
            "description": description,
            "source_path": source_path,
            "version_path": version_dir,
            "performance": performance or {},
            "active": False
        }

        info_path = os.path.join(version_dir, "version_info.json")
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(version_info, f, ensure_ascii=False, indent=2)

        # 更新注册表
        self.registry["version_registry"][category][subcategory]["versions"][version] = {
            "created": version_info["created"],
            "author": author,
            "description": description,
            "performance": performance or {},
            "active": False,
            "path": version_dir
        }

        # 如果是第一个版本，设置为当前版本
        if self.registry["version_registry"][category][subcategory]["current"] is None:
            self.registry["version_registry"][category][subcategory]["current"] = version
            self.registry["version_registry"][category][subcategory]["versions"][version]["active"] = True

        # 更新元数据
        self.registry["metadata"]["total_versions"] += 1

        print(f"✅ 创建版本: {category}/{subcategory}/{version}")
        print(f"   📝 {description}")

        return self._save_registry()

    def switch_version(self, category: str, subcategory: str, version: str):
        """切换到指定版本"""
        # 检查版本是否存在
        if not self._version_exists(category, subcategory, version):
            print(f"❌ 版本不存在: {category}/{subcategory}/{version}")
            return False

        # 更新当前版本
        old_version = self.registry["version_registry"][category][subcategory]["current"]
        self.registry["version_registry"][category][subcategory]["current"] = version

        # 更新活跃状态
        if old_version:
            self.registry["version_registry"][category][subcategory]["versions"][old_version]["active"] = False
        self.registry["version_registry"][category][subcategory]["versions"][version]["active"] = True

        print(f"🔄 切换版本: {category}/{subcategory}")
        print(f"   {old_version or '无'} → {version}")

        # 创建软链接（可选）
        self._create_symlink(category, subcategory, version)

        return self._save_registry()

    def _version_exists(self, category: str, subcategory: str, version: str) -> bool:
        """检查版本是否存在"""
        try:
            return version in self.registry["version_registry"][category][subcategory]["versions"]
        except KeyError:
            return False

    def _create_symlink(self, category: str, subcategory: str, version: str):
        """创建当前版本软链接"""
        try:
            category_dir = os.path.join(self.base_dir, category, subcategory)
            current_link = os.path.join(category_dir, "current")

            # 删除旧链接（如果存在）
            if os.path.exists(current_link) or os.path.islink(current_link):
                os.remove(current_link)

            # 创建新链接
            version_dir = os.path.join(category_dir, version)
            os.symlink(version_dir, current_link)

            print(f"🔗 创建软链接: current → {version}")
            return True
        except Exception as e:
            print(f"⚠️  创建软链接失败: {e}")
            return False

    def list_versions(self, category: str = None, subcategory: str = None):
        """列出所有版本"""
        print("📋 版本列表")
        print("=" * 60)

        if category is None:
            # 列出所有类别
            for cat, subcats in self.registry["version_registry"].items():
                print(f"\n📁 {cat}:")
                for subcat, data in subcats.items():
                    current = data.get("current", "无")
                    count = len(data.get("versions", {}))
                    print(f"  ├─ {subcat}: {count}个版本 (当前: {current})")
        elif subcategory is None:
            # 列出类别下的所有子类别
            if category in self.registry["version_registry"]:
                print(f"\n📁 {category}:")
                for subcat, data in self.registry["version_registry"][category].items():
                    current = data.get("current", "无")
                    count = len(data.get("versions", {}))
                    print(f"  ├─ {subcat}: {count}个版本 (当前: {current})")
            else:
                print(f"❌ 类别不存在: {category}")
        else:
            # 列出子类别的所有版本
            if (category in self.registry["version_registry"] and
                subcategory in self.registry["version_registry"][category]):

                data = self.registry["version_registry"][category][subcategory]
                current = data.get("current", "无")
                versions = data.get("versions", {})

                print(f"\n📁 {category}/{subcategory} (当前: {current})")
                print("-" * 40)

                for ver, info in versions.items():
                    active = "✅" if info.get("active", False) else "  "
                    created = info.get("created", "")[:10]
                    desc = info.get("description", "")[:50]
                    print(f"{active} {ver:8} {created} | {desc}")
            else:
                print(f"❌ 子类别不存在: {category}/{subcategory}")

    def compare_versions(self, category: str, subcategory: str, version1: str, version2: str):
        """比较两个版本"""
        if not self._version_exists(category, subcategory, version1):
            print(f"❌ 版本不存在: {version1}")
            return False

        if not self._version_exists(category, subcategory, version2):
            print(f"❌ 版本不存在: {version2}")
            return False

        v1_info = self.registry["version_registry"][category][subcategory]["versions"][version1]
        v2_info = self.registry["version_registry"][category][subcategory]["versions"][version2]

        print(f"📊 版本对比: {category}/{subcategory}")
        print("=" * 60)

        # 基本信息对比
        print(f"\n🔍 基本信息:")
        print(f"  {version1:8} | {version2:8}")
        print(f"  {'─'*9}+{'─'*9}")
        print(f"  创建: {v1_info.get('created', '')[:10]:10} | {v2_info.get('created', '')[:10]:10}")
        print(f"  作者: {v1_info.get('author', ''):10} | {v2_info.get('author', ''):10}")

        # 描述对比
        print(f"\n📝 版本描述:")
        print(f"  {version1}: {v1_info.get('description', '')}")
        print(f"  {version2}: {v2_info.get('description', '')}")

        # 性能对比（如果有）
        if v1_info.get('performance') and v2_info.get('performance'):
            print(f"\n📈 性能对比:")
            perf1 = v1_info['performance']
            perf2 = v2_info['performance']

            metrics = set(list(perf1.keys()) + list(perf2.keys()))
            for metric in metrics:
                val1 = perf1.get(metric, 'N/A')
                val2 = perf2.get(metric, 'N/A')

                # 尝试数值比较
                try:
                    if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                        diff = val2 - val1
                        diff_str = f"{diff:+.2f}"
                        if diff > 0:
                            diff_str = f"📈 {diff_str}"
                        elif diff < 0:
                            diff_str = f"📉 {diff_str}"
                        else:
                            diff_str = f"📊 {diff_str}"

                        print(f"  {metric:15}: {val1:
