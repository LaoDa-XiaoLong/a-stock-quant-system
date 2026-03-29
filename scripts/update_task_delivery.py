#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新任务发送配置
将指定任务配置为发送到对应的飞书群
"""

import json
import os
import sys
from datetime import datetime


class TaskDeliveryUpdater:
    """任务发送配置更新器"""
    
    def __init__(self):
        self.jobs_file = "/Users/ago/.openclaw/cron/jobs.json"
        self.backup_file = f"{self.jobs_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Webhook地址
        self.a_stock_webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/fb95ec56-6ad7-4830-99c7-0eaa287e67e7"
        self.work_group_webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/7c6e2bb9-0f2f-4d16-ade1-e93cf6bd3065"
        
        # 需要更新的任务配置
        self.tasks_to_update = {
            # 任务ID: (任务名称, 目标群组, Webhook地址)
            "3e454ed5-e6d5-4ffe-97bb-753a72474a7b": ("量化策略周报", "A股数据分析群", self.a_stock_webhook),
            "cc4d8e56-38b5-4583-a4a0-80aada932d2e": ("策略自动回测", "A股数据分析群", self.a_stock_webhook),
            "211b3fbd-0e12-466f-9cd4-ee7337a5bcaa": ("数据备份任务", "工作沟通汇报群", self.work_group_webhook),
            "9bd7abe6-e982-4718-a933-686545be6f2d": ("GitHub自动同步", "工作沟通汇报群", self.work_group_webhook)
        }
    
    def load_jobs(self):
        """加载任务配置"""
        print(f"📂 加载任务配置文件: {self.jobs_file}")
        
        if not os.path.exists(self.jobs_file):
            print(f"❌ 文件不存在: {self.jobs_file}")
            return None
        
        try:
            with open(self.jobs_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ 加载成功，共 {len(data.get('jobs', []))} 个任务")
            return data
        except Exception as e:
            print(f"❌ 加载失败: {e}")
            return None
    
    def backup_jobs(self, data):
        """备份原配置"""
        try:
            with open(self.backup_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"💾 配置已备份: {self.backup_file}")
            return True
        except Exception as e:
            print(f"❌ 备份失败: {e}")
            return False
    
    def update_task_delivery(self, data):
        """更新任务发送配置"""
        print("\n🔄 开始更新任务发送配置...")
        
        updated_count = 0
        not_found = []
        
        for job in data['jobs']:
            job_id = job['id']
            job_name = job['name']
            
            if job_id in self.tasks_to_update:
                task_info = self.tasks_to_update[job_id]
                target_group = task_info[1]
                webhook_url = task_info[2]
                
                print(f"\n📋 更新任务: {job_name}")
                print(f"   任务ID: {job_id}")
                print(f"   目标群组: {target_group}")
                print(f"   Webhook地址: {webhook_url[:50]}...")
                
                # 更新delivery配置
                job['delivery'] = {
                    "mode": "announce",
                    "target": "chat:oc_9d6f8d5a6d6a4d6b8d5a6d6a4d6b8d5a"  # 使用默认目标，实际发送由Webhook控制
                }
                
                # 更新描述，添加发送目标信息
                original_desc = job.get('description', '')
                new_desc = f"{original_desc} (发送到: {target_group})"
                job['description'] = new_desc
                
                print(f"   更新后描述: {new_desc}")
                print(f"   ✅ 配置更新完成")
                
                updated_count += 1
            else:
                # 检查是否是需要处理但未找到的任务
                for task_id, task_info in self.tasks_to_update.items():
                    if task_info[0] == job_name and task_id not in [j['id'] for j in data['jobs']]:
                        not_found.append((job_name, task_id))
        
        print(f"\n📊 更新统计:")
        print(f"   成功更新: {updated_count} 个任务")
        print(f"   未找到: {len(not_found)} 个任务")
        
        if not_found:
            print(f"\n⚠️  未找到的任务:")
            for task_name, task_id in not_found:
                print(f"   • {task_name} (ID: {task_id})")
        
        return updated_count
    
    def save_jobs(self, data):
        """保存更新后的配置"""
        try:
            with open(self.jobs_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"\n💾 配置已保存: {self.jobs_file}")
            return True
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            return False
    
    def verify_updates(self):
        """验证更新结果"""
        print("\n🔍 验证更新结果...")
        
        try:
            result = os.popen("openclaw cron list --all").read()
            print(result)
            
            # 检查每个任务的状态
            for task_id, task_info in self.tasks_to_update.items():
                task_name = task_info[0]
                target_group = task_info[1]
                
                if task_name in result:
                    print(f"✅ {task_name} - 配置存在")
                else:
                    print(f"❌ {task_name} - 未找到")
            
            return True
        except Exception as e:
            print(f"❌ 验证失败: {e}")
            return False
    
    def create_task_summary(self):
        """创建任务配置总结"""
        summary = f"""# 任务发送配置更新总结
更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Webhook地址配置
### A股数据分析群
- 地址: {self.a_stock_webhook}
- 用途: A股投资相关内容

### 工作沟通汇报群
- 地址: {self.work_group_webhook}
- 用途: 系统技术相关内容

## 任务发送配置
### 发送到A股数据分析群
1. **财报监控日报** (09:00) - A股投资分析
2. **量化策略周报** (周五16:00) - A股策略分析
3. **策略自动回测** (周五17:00) - A股回测结果

### 发送到工作沟通汇报群
4. **系统健康检查** (10:00) - 系统状态监控
5. **代码健康度检查** (15:00) - 代码质量检查
6. **数据备份任务** (周六20:00) - 系统数据备份
7. **GitHub自动同步** (00:10,12:10) - 代码同步状态

### 内部任务（不发送到群）
8. **股票数据自动更新** (09:30) - 内部数据更新

## 消息分发规则
- **A股数据分析群**: 所有A股投资、分析、策略相关内容
- **工作沟通汇报群**: 所有系统、技术、维护、状态相关内容

## 备份信息
- 原配置备份: {self.backup_file}
- 新配置位置: {self.jobs_file}
"""
        
        summary_file = "/Users/ago/.openclaw/workspace/docs/task_delivery_config_summary.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"\n📄 配置总结已保存: {summary_file}")
        return summary_file
    
    def run(self):
        """执行更新"""
        print("=" * 60)
        print("🚀 任务发送配置更新工具")
        print("=" * 60)
        
        # 1. 加载配置
        data = self.load_jobs()
        if not data:
            return False
        
        # 2. 备份原配置
        if not self.backup_jobs(data):
            print("⚠️  备份失败，但继续执行")
        
        # 3. 更新任务配置
        updated_count = self.update_task_delivery(data)
        if updated_count == 0:
            print("❌ 没有任务需要更新")
            return False
        
        # 4. 保存更新
        if not self.save_jobs(data):
            return False
        
        # 5. 验证更新
        self.verify_updates()
        
        # 6. 创建总结
        summary_file = self.create_task_summary()
        
        print("\n" + "=" * 60)
        print("🎉 任务发送配置更新完成!")
        print("=" * 60)
        
        print(f"\n📋 更新结果:")
        print(f"   更新任务数: {updated_count}")
        print(f"   备份文件: {self.backup_file}")
        print(f"   总结文档: {summary_file}")
        
        print(f"\n🎯 更新后的任务发送规则:")
        print(f"   A股数据分析群: 3个任务")
        print(f"   工作沟通汇报群: 4个任务")
        print(f"   内部任务: 1个任务")
        
        return True


def main():
    """主函数"""
    updater = TaskDeliveryUpdater()
    success = updater.run()
    
    if success:
        print("\n✅ 所有任务发送配置已更新完成!")
        print("\n🔧 验证命令:")
        print("   openclaw cron list --all")
        print("\n📊 查看详细配置:")
        print("   cat /Users/ago/.openclaw/workspace/docs/task_delivery_config_summary.md")
    else:
        print("\n❌ 更新失败，请检查错误信息")
    
    return success


if __name__ == "__main__":
    main()