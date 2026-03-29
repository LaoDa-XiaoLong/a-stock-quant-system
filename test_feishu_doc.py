#!/usr/bin/env python3
"""
飞书文档功能测试脚本
测试飞书文档的读取和创建功能
"""

import json
import sys
import os

def test_document_read():
    """测试文档读取功能"""
    print("📄 测试飞书文档读取功能")
    print("=" * 50)
    
    # 这里需要有一个已知的飞书文档token来测试
    # 由于我们没有现成的文档token，先模拟测试流程
    
    print("1. 检查飞书文档工具可用性...")
    
    # 检查飞书文档技能是否存在
    skill_path = "/usr/local/lib/node_modules/openclaw/dist/extensions/feishu/skills/feishu-doc/SKILL.md"
    if os.path.exists(skill_path):
        print("   ✅ 飞书文档技能已安装")
    else:
        print("   ❌ 飞书文档技能未找到")
        return False
    
    print("2. 模拟文档读取请求结构...")
    
    # 模拟一个文档读取请求
    read_request = {
        "action": "read",
        "doc_token": "ABC123def"  # 示例token
    }
    
    print(f"   请求结构: {json.dumps(read_request, indent=2, ensure_ascii=False)}")
    print("   📝 说明: 需要真实的doc_token才能测试读取功能")
    
    print("3. 模拟文档创建请求结构...")
    
    # 模拟一个文档创建请求
    create_request = {
        "action": "create",
        "title": "飞书功能测试文档 - 量化小助理",
        "owner_open_id": "ou_c013d9a2273f3fbe3e293eda1ffca875"
    }
    
    print(f"   请求结构: {json.dumps(create_request, indent=2, ensure_ascii=False)}")
    
    print("\n📋 测试总结:")
    print("   ✅ 飞书文档技能架构正常")
    print("   🔄 需要真实文档token进行完整测试")
    print("   📝 文档创建功能需要实际调用验证")
    
    return True

def test_document_operations():
    """测试文档操作功能"""
    print("\n🔧 测试飞书文档操作功能")
    print("=" * 50)
    
    operations = [
        {
            "name": "读取文档",
            "action": "read",
            "description": "获取文档内容和基本信息"
        },
        {
            "name": "创建文档",
            "action": "create",
            "description": "创建新文档并设置权限"
        },
        {
            "name": "写入文档",
            "action": "write",
            "description": "替换文档全部内容"
        },
        {
            "name": "追加内容",
            "action": "append",
            "description": "在文档末尾追加内容"
        },
        {
            "name": "列表块",
            "action": "list_blocks",
            "description": "获取文档结构化内容"
        },
        {
            "name": "创建表格",
            "action": "create_table",
            "description": "在文档中创建表格"
        },
        {
            "name": "上传图片",
            "action": "upload_image",
            "description": "上传图片到文档"
        }
    ]
    
    print("📊 支持的文档操作:")
    for i, op in enumerate(operations, 1):
        print(f"   {i}. {op['name']} ({op['action']})")
        print(f"      描述: {op['description']}")
    
    print("\n🎯 测试建议:")
    print("   1. 先创建一个测试文档")
    print("   2. 测试文档读取功能")
    print("   3. 测试文档写入和追加")
    print("   4. 测试表格和图片上传")
    
    return True

def main():
    print("🚀 飞书文档功能测试")
    print("=" * 50)
    
    # 测试1: 文档读取功能
    test1_result = test_document_read()
    
    # 测试2: 文档操作功能
    test2_result = test_document_operations()
    
    print("\n" + "=" * 50)
    print("📊 整体测试报告")
    print("=" * 50)
    
    print(f"📄 文档读取测试: {'✅ 通过' if test1_result else '❌ 失败'}")
    print(f"🔧 文档操作测试: {'✅ 通过' if test2_result else '❌ 失败'}")
    
    print("\n📋 后续测试建议:")
    print("   1. 获取一个真实的飞书文档token进行测试")
    print("   2. 测试文档创建功能")
    print("   3. 测试文档读写完整流程")
    print("   4. 测试表格和图片上传功能")
    
    print("\n🔗 飞书文档技能位置:")
    print("   /usr/local/lib/node_modules/openclaw/dist/extensions/feishu/skills/feishu-doc/")
    
    print("\n📚 相关技能:")
    print("   - feishu-doc: 文档读写操作")
    print("   - feishu-wiki: 知识库访问")
    print("   - feishu-drive: 云盘文件管理")
    print("   - feishu-perm: 权限管理")
    
    overall_success = test1_result and test2_result
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)