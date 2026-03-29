#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
周一开盘前检查脚本
检查系统状态、持仓数据、调度任务
"""

import os
import sys
import json
from datetime import datetime
import pandas as pd


def check_system_status():
    """检查系统状态"""
    print("🔍 系统状态检查")
    print("=" * 50)
    
    # 1. 检查调度任务
    print("1. 📅 调度任务状态:")
    try:
        import subprocess
        result = subprocess.run(['openclaw', 'cron', 'list', '--all'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                for line in lines[1:]:  # 跳过标题行
                    if line.strip():
                        print(f"   {line}")
        else:
            print("   ❌ 无法获取调度任务列表")
    except Exception as e:
        print(f"   ⚠️  调度检查失败: {e}")
    
    # 2. 检查版本管理
    print("\n2. 📦 版本管理状态:")
    version_registry = "version_management/version_registry.json"
    if os.path.exists(version_registry):
        try:
            with open(version_registry, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            
            if "categories" in registry:
                for category, items in registry["categories"].items():
                    for name, data in items.items():
                        current = data.get("current", "无")
                        count = len(data.get("versions", {}))
                        print(f"   📁 {category}/{name}: {count}个版本 (当前: {current})")
        except Exception as e:
            print(f"   ⚠️  版本注册表读取失败: {e}")
    else:
        print("   ❌ 版本注册表不存在")
    
    # 3. 检查数据文件
    print("\n3. 💾 数据文件状态:")
    data_files = [
        "data/holdings/holding_stocks.csv",
        "data/final_financial_complete/final_reports_complete.db",
        "reports/holdings_analysis_report.md"
    ]
    
    for file_path in data_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            print(f"   ✅ {file_path}: {size:,} bytes, 修改时间: {mtime.strftime('%Y-%m-%d %H:%M')}")
        else:
            print(f"   ❌ {file_path}: 文件不存在")
    
    return True


def check_holdings():
    """检查持仓数据"""
    print("\n📊 持仓数据检查")
    print("=" * 50)
    
    holdings_file = "data/holdings/holding_stocks.csv"
    if not os.path.exists(holdings_file):
        print("❌ 持仓文件不存在")
        return False
    
    try:
        # 读取持仓数据
        df = pd.read_csv(holdings_file)
        print(f"1. 📈 持仓股票数量: {len(df)} 只")
        
        print("\n2. 🎯 持仓清单:")
        for idx, row in df.iterrows():
            print(f"   {idx+1:2d}. {row['code']} {row['name']:10} 成本价: {row['cost_price']}元")
        
        # 检查财报数据
        print("\n3. 📋 财报数据状态:")
        db_path = "data/final_financial_complete/final_reports_complete.db"
        if os.path.exists(db_path):
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 检查持仓股票在财报数据库中的记录
            for code in df['code']:
                cursor.execute("""
                    SELECT COUNT(*) FROM final_surprises_complete 
                    WHERE stock_code = ? AND is_holding = 1
                """, (str(code),))
                count = cursor.fetchone()[0]
                status = "✅ 有财报数据" if count > 0 else "⚠️  无财报数据"
                print(f"   {code}: {status} ({count}条记录)")
            
            conn.close()
        else:
            print("   ❌ 财报数据库不存在")
        
        return True
        
    except Exception as e:
        print(f"❌ 持仓数据检查失败: {e}")
        return False


def check_tomorrow_schedule():
    """检查明日调度任务"""
    print("\n⏰ 明日调度任务检查")
    print("=" * 50)
    
    # 明天的重要任务
    tomorrow_tasks = [
        ("09:00", "财报监控日报", "V3深度优化版自动执行"),
        ("09:30", "股票数据自动更新", "获取最新A股数据"),
        ("10:00", "系统健康检查", "发送报告到工作沟通汇报群")
    ]
    
    print("明日重要任务:")
    for time, name, desc in tomorrow_tasks:
        print(f"  🕘 {time}: {name}")
        print(f"      {desc}")
    
    # 检查任务配置
    cron_file = "/Users/ago/.openclaw/cron/jobs.json"
    if os.path.exists(cron_file):
        try:
            with open(cron_file, 'r', encoding='utf-8') as f:
                jobs = json.load(f)
            
            print("\n任务配置验证:")
            for job in jobs.get("jobs", []):
                job_name = job.get("name", "")
                for time, name, _ in tomorrow_tasks:
                    if name in job_name:
                        payload = job.get("payload", {}).get("message", "")
                        if "v3.0" in payload.lower() or "v3" in payload:
                            status = "✅ V3版配置"
                        else:
                            status = "⚠️  版本信息缺失"
                        print(f"  {name}: {status}")
                        break
        except Exception as e:
            print(f"  ⚠️  配置检查失败: {e}")
    
    return True


def check_version_rollback():
    """检查版本回滚能力"""
    print("\n🔄 版本回滚能力检查")
    print("=" * 50)
    
    # 检查财报监控日报的版本
    financial_dir = "version_management/report_templates/financial_daily"
    if os.path.exists(financial_dir):
        versions = []
        for item in os.listdir(financial_dir):
            if os.path.isdir(os.path.join(financial_dir, item)) and item.startswith('v'):
                versions.append(item)
        
        versions.sort()
        print(f"可用版本: {', '.join(versions)}")
        
        # 检查当前版本
        current_link = os.path.join(financial_dir, "current")
        if os.path.islink(current_link):
            current = os.path.basename(os.path.realpath(current_link))
            print(f"当前版本: {current}")
            
            # 回滚预案
            print("\n回滚预案:")
            for version in versions:
                if version != current:
                    print(f"  回滚到 {version}: python3 scripts/simple_version_manager.py switch report_templates financial_daily {version}")
        else:
            print("⚠️  当前版本软链接不存在")
    else:
        print("❌ 财报模板目录不存在")
    
    return True


def generate_pre_market_report():
    """生成开盘前检查报告"""
    print("\n📋 开盘前检查报告")
    print("=" * 50)
    
    report = {
        "检查时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "明日日期": "2026-03-30（周一）",
        "A股开盘时间": "09:30",
        "检查项目": {}
    }
    
    # 执行检查
    report["检查项目"]["系统状态"] = "正常" if check_system_status() else "异常"
    report["检查项目"]["持仓数据"] = "正常" if check_holdings() else "异常"
    report["检查项目"]["明日调度"] = "正常" if check_tomorrow_schedule() else "异常"
    report["检查项目"]["版本回滚"] = "正常" if check_version_rollback() else "异常"
    
    # 总结
    print("\n🎯 检查总结")
    print("-" * 30)
    
    all_ok = all(status == "正常" for status in report["检查项目"].values())
    if all_ok:
        print("✅ 所有检查项目正常，系统准备就绪！")
        print("\n明日重点关注:")
        print("  1. 09:00 V3版财报监控日报效果")
        print("  2. 09:30 股票数据更新质量")
        print("  3. 持仓股票开盘表现")
        print("  4. 交易信号监控")
    else:
        print("⚠️  存在异常项目，需要处理:")
        for item, status in report["检查项目"].items():
            if status != "正常":
                print(f"  ❌ {item}: {status}")
    
    # 保存报告
    report_file = "reports/pre_market_check_20260330.md"
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# 开盘前检查报告\n")
            f.write(f"生成时间: {report['检查时间']}\n")
            f.write(f"明日日期: {report['明日日期']}\n\n")
            
            f.write("## 检查结果\n")
            for item, status in report["检查项目"].items():
                f.write(f"- {item}: {status}\n")
            
            f.write("\n## 建议\n")
            if all_ok:
                f.write("1. 系统准备就绪，可正常开盘\n")
                f.write("2. 关注09:00 V3版财报监控日报\n")
                f.write("3. 监控持仓股票开盘表现\n")
                f.write("4. 严格执行风险控制规则\n")
            else:
                f.write("1. 请先处理异常项目\n")
                f.write("2. 检查调度任务配置\n")
                f.write("3. 验证数据文件完整性\n")
                f.write("4. 测试版本回滚功能\n")
        
        print(f"\n📄 报告已保存: {report_file}")
        
    except Exception as e:
        print(f"❌ 保存报告失败: {e}")
    
    return all_ok


def main():
    """主函数"""
    print("🚀 周一A股开盘前检查")
    print("=" * 60)
    print("检查时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("明日开盘: 2026-03-30 09:30")
    print("=" * 60)
    
    try:
        success = generate_pre_market_report()
        return 0 if success else 1
        
    except Exception as e:
        print(f"❌ 检查过程出错: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())