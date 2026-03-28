#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速健康检查脚本
简化版本，用于快速诊断当前问题
"""

import os
import sys
import subprocess
import json
from datetime import datetime

def check_system_resources():
    """快速检查系统资源"""
    print("🔍 检查系统资源...")
    
    results = {}
    
    try:
        # 检查磁盘空间
        cmd = "df -h / | tail -1"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            parts = result.stdout.strip().split()
            if len(parts) >= 5:
                results['disk'] = {
                    'total': parts[1],
                    'used': parts[2],
                    'free': parts[3],
                    'usage': parts[4]
                }
        
        # 检查内存
        cmd = "vm_stat | head -10"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            memory_info = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    memory_info[key.strip()] = value.strip()
            results['memory'] = memory_info
        
        # 检查进程数量
        cmd = "ps aux | wc -l"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            process_count = int(result.stdout.strip()) - 1  # 减去标题行
            results['process_count'] = process_count
        
        # 检查OpenClaw进程
        cmd = "ps aux | grep -E '(openclaw|node.*openclaw)' | grep -v grep | wc -l"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            openclaw_count = int(result.stdout.strip())
            results['openclaw_processes'] = openclaw_count
        
        return results
        
    except Exception as e:
        print(f"❌ 系统资源检查失败: {e}")
        return {'error': str(e)}

def check_openclaw_status():
    """检查OpenClaw状态"""
    print("🤖 检查OpenClaw状态...")
    
    try:
        cmd = "openclaw status --brief"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            return {
                'status': 'running',
                'output': result.stdout[:500]  # 只取前500字符
            }
        else:
            return {
                'status': 'error',
                'error': result.stderr[:200]
            }
            
    except Exception as e:
        return {
            'status': 'exception',
            'error': str(e)
        }

def check_project_files():
    """检查项目文件"""
    print("📁 检查项目文件...")
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    required_files = [
        'MEMORY.md',
        'USER.md',
        'IDENTITY.md',
        'SOUL.md',
        'AGENTS.md'
    ]
    
    results = {}
    missing_files = []
    
    for file_name in required_files:
        file_path = os.path.join(project_root, file_name)
        exists = os.path.exists(file_path)
        results[file_name] = exists
        if not exists:
            missing_files.append(file_name)
    
    return {
        'files': results,
        'missing_files': missing_files,
        'all_exist': len(missing_files) == 0
    }

def check_recent_errors():
    """检查最近错误"""
    print("🚨 检查最近错误...")
    
    # 这里可以检查错误日志文件
    # 目前先返回一个简单结果
    return {
        'tool_errors': '需要检查具体日志',
        'suggestions': [
            '使用更精确的edit工具匹配',
            '简化飞书消息格式',
            '优化工具使用流程'
        ]
    }

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 快速健康检查")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    all_results = {}
    
    # 运行各项检查
    all_results['system'] = check_system_resources()
    all_results['openclaw'] = check_openclaw_status()
    all_results['project'] = check_project_files()
    all_results['errors'] = check_recent_errors()
    
    # 生成报告
    print("\n" + "=" * 60)
    print("📊 检查结果摘要")
    print("=" * 60)
    
    # 系统资源
    print("\n💻 系统资源:")
    if 'disk' in all_results['system']:
        disk = all_results['system']['disk']
        print(f"   磁盘: {disk.get('usage', 'N/A')} 使用率")
        print(f"   可用: {disk.get('free', 'N/A')} 空闲")
    
    if 'process_count' in all_results['system']:
        count = all_results['system']['process_count']
        print(f"   进程数: {count}")
        if count > 500:
            print(f"   ⚠️ 进程数量较多 ({count})，可能影响性能")
    
    if 'openclaw_processes' in all_results['system']:
        count = all_results['system']['openclaw_processes']
        print(f"   OpenClaw进程: {count}")
    
    # OpenClaw状态
    print("\n🤖 OpenClaw状态:")
    status = all_results['openclaw'].get('status', 'unknown')
    if status == 'running':
        print("   ✅ OpenClaw运行正常")
    else:
        print(f"   ❌ OpenClaw状态: {status}")
        if 'error' in all_results['openclaw']:
            print(f"   错误: {all_results['openclaw']['error'][:100]}...")
    
    # 项目文件
    print("\n📁 项目文件:")
    project = all_results['project']
    if project['all_exist']:
        print("   ✅ 所有关键文件都存在")
    else:
        print(f"   ⚠️ 缺少 {len(project['missing_files'])} 个文件:")
        for file in project['missing_files']:
            print(f"      • {file}")
    
    # 错误和建议
    print("\n💡 建议:")
    errors = all_results['errors']
    for suggestion in errors.get('suggestions', []):
        print(f"   • {suggestion}")
    
    # 总体评估
    print("\n" + "=" * 60)
    print("🎯 立即行动建议:")
    
    issues_found = False
    
    # 检查进程数量
    if all_results['system'].get('process_count', 0) > 500:
        print("   1. 🔄 优化进程管理，减少不必要的进程")
        issues_found = True
    
    # 检查OpenClaw状态
    if all_results['openclaw'].get('status') != 'running':
        print("   2. 🛠️ 修复OpenClaw服务问题")
        issues_found = True
    
    # 检查项目文件
    if not all_results['project']['all_exist']:
        print("   3. 📝 补充缺失的项目文件")
        issues_found = True
    
    if not issues_found:
        print("   ✅ 系统状态良好，可以继续项目开发")
    
    print("\n" + "=" * 60)
    print("📋 详细报告已保存到: data/quick_health_check.json")
    
    # 保存详细结果
    output_dir = "data/health_checks"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"quick_health_check_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print("=" * 60)

if __name__ == "__main__":
    main()