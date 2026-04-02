#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本管理CLI工具
简化版命令行界面
"""

import sys
import os
from version_manager import VersionManager


def print_help():
    """打印帮助信息"""
    print("📦 版本管理CLI工具")
    print("=" * 60)
    print("用法: python version_cli.py <命令> [参数]")
    print("\n可用命令:")
    print("  list [category] [subcategory]     列出版本")
    print("  create <category> <subcategory> <version> <source_path>")
    print("  switch <category> <subcategory> <version>  切换版本")
    print("  compare <category> <subcategory> <ver1> <ver2> 对比版本")
    print("  info <category> <subcategory>     查看详细信息")
    print("  help                              显示帮助")
    print("\n示例:")
    print("  python version_cli.py list")
    print("  python version_cli.py list stock_models")
    print("  python version_cli.py list stock_models stock_selection")
    print("  python version_cli.py create stock_models stock_selection v1.0 strategies/stock_pool_filter.py")
    print("  python version_cli.py switch stock_models stock_selection v1.1")
    print("  python version_cli.py compare stock_models stock_selection v1.0 v1.1")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print_help()
        return 1

    command = sys.argv[1]

    # 初始化版本管理器
    vm = VersionManager()

    try:
        if command == "list":
            if len(sys.argv) == 2:
                vm.list_versions()
            elif len(sys.argv) == 3:
                vm.list_versions(category=sys.argv[2])
            elif len(sys.argv) == 4:
                vm.list_versions(category=sys.argv[2], subcategory=sys.argv[3])
            else:
                print("❌ 参数错误")
                print_help()

        elif command == "create":
            if len(sys.argv) != 6:
                print("❌ 参数错误，需要5个参数")
                print("用法: create <category> <subcategory> <version> <source_path>")
                return 1

            category = sys.argv[2]
            subcategory = sys.argv[3]
            version = sys.argv[4]
            source_path = sys.argv[5]

            # 先创建类别（如果不存在）
            vm.create_category(category, subcategory, f"{subcategory}版本管理")

            # 创建版本
            success = vm.create_version(
                category=category,
                subcategory=subcategory,
                version=version,
                source_path=source_path,
                author="小龙",
                description=f"{subcategory} {version} 版本"
            )

            if success:
                print(f"✅ 版本创建成功: {category}/{subcategory}/{version}")
            else:
                print(f"❌ 版本创建失败")

        elif command == "switch":
            if len(sys.argv) != 5:
                print("❌ 参数错误，需要4个参数")
                print("用法: switch <category> <subcategory> <version>")
                return 1

            category = sys.argv[2]
            subcategory = sys.argv[3]
            version = sys.argv[4]

            success = vm.switch_version(category, subcategory, version)
            if success:
                print(f"✅ 版本切换成功: {category}/{subcategory} → {version}")
            else:
                print(f"❌ 版本切换失败")

        elif command == "compare":
            if len(sys.argv) != 6:
                print("❌ 参数错误，需要5个参数")
                print("用法: compare <category> <subcategory> <ver1> <ver2>")
                return 1

            category = sys.argv[2]
            subcategory = sys.argv[3]
            ver1 = sys.argv[4]
            ver2 = sys.argv[5]

            vm.compare_versions(category, subcategory, ver1, ver2)

        elif command == "info":
            if len(sys.argv) != 4:
                print("❌ 参数错误，需要3个参数")
                print("用法: info <category> <subcategory>")
                return 1

            category = sys.argv[2]
            subcategory = sys.argv[3]

            vm.list_versions(category, subcategory)

        elif command == "help":
            print_help()

        else:
            print(f"❌ 未知命令: {command}")
            print_help()
            return 1

        return 0

    except Exception as e:
        print(f"❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
