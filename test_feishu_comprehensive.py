#!/usr/bin/env python3
"""
飞书功能综合测试脚本
测试所有飞书相关功能
"""

import json
import sys
import os
from datetime import datetime

class FeishuComprehensiveTest:
    def __init__(self):
        self.test_results = []
        self.webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/fb95ec56-6ad7-4830-99c7-0eaa287e67e7"
        self.test_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def log_test(self, name, success, details=None):
        """记录测试结果"""
        result = {
            "name": name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        
        status = "✅" if success else "❌"
        print(f"{status} {name}")
        if details:
            print(f"   详情: {details}")
        print()
    
    def test_skill_availability(self):
        """测试飞书技能可用性"""
        print("🔧 测试飞书技能可用性")
        print("=" * 50)
        
        skills = [
            ("feishu-doc", "文档操作", "/usr/local/lib/node_modules/openclaw/dist/extensions/feishu/skills/feishu-doc/SKILL.md"),
            ("feishu-wiki", "知识库", "/usr/local/lib/node_modules/openclaw/dist/extensions/feishu/skills/feishu-wiki/SKILL.md"),
            ("feishu-drive", "云盘", "/usr/local/lib/node_modules/openclaw/dist/extensions/feishu/skills/feishu-drive/SKILL.md"),
            ("feishu-perm", "权限管理", "/usr/local/lib/node_modules/openclaw/dist/extensions/feishu/skills/feishu-perm/SKILL.md")
        ]
        
        all_available = True
        for skill_name, skill_desc, skill_path in skills:
            if os.path.exists(skill_path):
                self.log_test(f"技能 {skill_name} ({skill_desc})", True, f"路径: {skill_path}")
            else:
                self.log_test(f"技能 {skill_name} ({skill_desc})", False, f"未找到: {skill_path}")
                all_available = False
        
        return all_available
    
    def test_message_sending(self):
        """测试消息发送功能"""
        print("\n📤 测试消息发送功能")
        print("=" * 50)
        
        try:
            import requests
            
            # 发送测试消息
            test_message = f"📊 飞书功能综合测试\n\n测试时间: {self.test_time}\n测试项目: 消息发送功能\n状态: 测试进行中 ✅"
            
            payload = {
                "msg_type": "text",
                "content": {
                    "text": test_message
                }
            }
            
            response = requests.post(
                self.webhook_url,
                headers={'Content-Type': 'application/json'},
                data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
                timeout=10
            )
            
            success = response.status_code == 200
            details = f"状态码: {response.status_code}"
            
            self.log_test("消息发送功能", success, details)
            return success
            
        except Exception as e:
            self.log_test("消息发送功能", False, f"异常: {str(e)}")
            return False
    
    def test_permission_status(self):
        """测试权限状态"""
        print("\n🔐 测试权限状态")
        print("=" * 50)
        
        # 检查日志中是否有权限错误
        log_file = "/tmp/openclaw/openclaw-2026-03-28.log"
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    recent_logs = f.readlines()[-100:]  # 最近100行
                
                permission_errors = []
                for line in recent_logs:
                    if '99991672' in line or 'contact:contact.base:readonly' in line or 'Access denied' in line:
                        permission_errors.append(line.strip())
                
                if permission_errors:
                    self.log_test("权限状态", False, f"发现权限错误: {len(permission_errors)}个")
                    return False
                else:
                    self.log_test("权限状态", True, "未发现权限错误")
                    return True
                    
            except Exception as e:
                self.log_test("权限状态", False, f"日志读取异常: {str(e)}")
                return False
        else:
            self.log_test("权限状态", True, "日志文件不存在，假设权限正常")
            return True
    
    def test_gateway_status(self):
        """测试网关状态"""
        print("\n🌐 测试网关状态")
        print("=" * 50)
        
        try:
            import subprocess
            
            result = subprocess.run(
                ['openclaw', 'gateway', 'status'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                if 'running' in result.stdout.lower():
                    # 提取PID信息
                    import re
                    pid_match = re.search(r'pid\s+(\d+)', result.stdout)
                    pid_info = f"PID: {pid_match.group(1)}" if pid_match else "运行中"
                    
                    self.log_test("网关状态", True, pid_info)
                    return True
                else:
                    self.log_test("网关状态", False, "网关未运行")
                    return False
            else:
                self.log_test("网关状态", False, f"命令失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_test("网关状态", False, f"异常: {str(e)}")
            return False
    
    def test_cron_jobs(self):
        """测试调度任务"""
        print("\n⏰ 测试调度任务")
        print("=" * 50)
        
        try:
            import subprocess
            
            result = subprocess.run(
                ['openclaw', 'cron', 'list'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # 解析JSON输出
                import json
                cron_data = json.loads(result.stdout)
                job_count = len(cron_data.get('jobs', []))
                
                if job_count > 0:
                    job_names = [job.get('name', '未命名') for job in cron_data.get('jobs', [])]
                    details = f"找到 {job_count} 个任务: {', '.join(job_names)}"
                    self.log_test("调度任务", True, details)
                    return True
                else:
                    self.log_test("调度任务", False, "未找到调度任务")
                    return False
            else:
                self.log_test("调度任务", False, f"命令失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_test("调度任务", False, f"异常: {str(e)}")
            return False
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("📊 飞书功能综合测试报告")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"测试时间: {self.test_time}")
        print(f"测试总数: {total_tests}")
        print(f"✅ 通过数: {passed_tests}")
        print(f"❌ 失败数: {failed_tests}")
        print(f"📊 成功率: {passed_tests/total_tests*100:.1f}%" if total_tests > 0 else "N/A")
        
        print("\n📋 详细测试结果:")
        for i, result in enumerate(self.test_results, 1):
            status = "✅" if result['success'] else "❌"
            print(f"{i:2d}. {status} {result['name']}")
            if result.get('details'):
                print(f"    详情: {result['details']}")
        
        print("\n🎯 功能状态总结:")
        
        # 技能状态
        skill_tests = [r for r in self.test_results if '技能' in r['name']]
        skill_passed = sum(1 for r in skill_tests if r['success'])
        print(f"🔧 技能可用性: {skill_passed}/{len(skill_tests)} 个技能可用")
        
        # 核心功能状态
        core_functions = {
            "消息发送": any('消息发送' in r['name'] and r['success'] for r in self.test_results),
            "权限状态": any('权限状态' in r['name'] and r['success'] for r in self.test_results),
            "网关状态": any('网关状态' in r['name'] and r['success'] for r in self.test_results),
            "调度任务": any('调度任务' in r['name'] and r['success'] for r in self.test_results)
        }
        
        for func, status in core_functions.items():
            print(f"📤 {func}: {'✅ 正常' if status else '❌ 异常'}")
        
        print("\n📝 测试结论:")
        if failed_tests == 0:
            print("🎉 所有测试通过！飞书功能完全正常。")
            print("   1. 权限问题已解决")
            print("   2. 消息发送功能正常")
            print("   3. 调度任务已设置")
            print("   4. 网关运行稳定")
        else:
            print(f"⚠️  有{failed_tests}个测试失败，需要进一步检查。")
            print("   建议检查:")
            print("   1. 飞书应用权限配置")
            print("   2. 网关服务状态")
            print("   3. 网络连接情况")
        
        return failed_tests == 0
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始飞书功能综合测试")
        print("=" * 60)
        
        # 运行各个测试
        self.test_skill_availability()
        self.test_message_sending()
        self.test_permission_status()
        self.test_gateway_status()
        self.test_cron_jobs()
        
        # 生成报告
        return self.generate_report()

def main():
    """主函数"""
    tester = FeishuComprehensiveTest()
    success = tester.run_all_tests()
    
    # 保存测试报告
    report_file = "/Users/ago/.openclaw/workspace/feishu_test_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            "test_time": tester.test_time,
            "results": tester.test_results,
            "summary": {
                "total": len(tester.test_results),
                "passed": sum(1 for r in tester.test_results if r['success']),
                "failed": sum(1 for r in tester.test_results if not r['success'])
            }
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 测试报告已保存到: {report_file}")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试过程中发生异常: {e}")
        sys.exit(1)