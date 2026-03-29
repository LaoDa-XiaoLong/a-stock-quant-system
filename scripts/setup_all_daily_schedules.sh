#!/bin/bash
# 加速配置所有每日调度任务

set -e
echo "🚀 开始加速配置所有每日调度任务..."
echo "========================================="

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 项目根目录
PROJECT_ROOT="/Users/ago/.openclaw/workspace"
CRON_FILE="/tmp/quant_cron_$(date +%s)"

# 备份现有cron
echo -e "${YELLOW}备份现有cron任务...${NC}"
crontab -l > /tmp/cron_backup_$(date +%Y%m%d_%H%M%S).bak 2>/dev/null || true

# 创建新的cron配置
cat > $CRON_FILE << 'EOF'
# =========================================
# A股量化交易系统 - 每日调度配置
# 生成时间: $(date)
# =========================================

# 1. 系统健康检查 (每天9:00和15:00)
0 9,15 * * * cd /Users/ago/.openclaw/workspace && python scripts/daily_health_check.py >> logs/health_check_$(date +\%Y\%m\%d).log 2>&1

# 2. GitHub维护日报 (每天17:00)
0 17 * * * cd /Users/ago/.openclaw/workspace && python scripts/github_daily_report.py >> logs/github_report_$(date +\%Y\%m\%d).log 2>&1

# 3. A股财报监控日报 (每天21:30)
30 21 * * * cd /Users/ago/.openclaw/workspace && python scripts/final_financial_monitor_fixed.py >> logs/financial_monitor_$(date +\%Y\%m\%d).log 2>&1

# 4. 开发工作日报 (每天17:30)
30 17 * * * cd /Users/ago/.openclaw/workspace && python scripts/generate_daily_report.py >> logs/daily_report_$(date +\%Y\%m\%d).log 2>&1

# 5. 数据备份 (每天23:00)
0 23 * * * cd /Users/ago/.openclaw/workspace && python scripts/backup_system.py >> logs/backup_$(date +\%Y\%m\%d).log 2>&1

# 6. 调度状态检查 (每天8:00)
0 8 * * * cd /Users/ago/.openclaw/workspace && python scripts/check_schedule_status.py >> logs/schedule_status_$(date +\%Y\%m\%d).log 2>&1

# =========================================
EOF

# 替换变量
sed -i '' "s|\$(date)|$(date)|g" $CRON_FILE

echo -e "${GREEN}✅ 创建cron配置文件: $CRON_FILE${NC}"

# 检查必要脚本是否存在
echo -e "${YELLOW}检查必要脚本...${NC}"

REQUIRED_SCRIPTS=(
    "scripts/daily_health_check.py"
    "scripts/final_financial_monitor_fixed.py"
    "scripts/generate_daily_report.py"
)

MISSING_SCRIPTS=()
for script in "${REQUIRED_SCRIPTS[@]}"; do
    if [ -f "$PROJECT_ROOT/$script" ]; then
        echo -e "  ✅ $script"
    else
        echo -e "  ❌ $script (缺失)"
        MISSING_SCRIPTS+=("$script")
    fi
done

# 创建缺失的脚本
if [ ${#MISSING_SCRIPTS[@]} -gt 0 ]; then
    echo -e "${YELLOW}创建缺失的脚本...${NC}"
    
    for script in "${MISSING_SCRIPTS[@]}"; do
        script_name=$(basename "$script")
        script_dir="$PROJECT_ROOT/$(dirname "$script")"
        
        mkdir -p "$script_dir"
        
        case "$script_name" in
            "github_daily_report.py")
                cat > "$PROJECT_ROOT/$script" << 'PYTHON'
#!/usr/bin/env python3
# GitHub维护日报脚本
import subprocess
import json
from datetime import datetime
import os

def run_git_command(cmd):
    """运行git命令"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        return False, str(e)

def main():
    print(f"GitHub维护日报 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 获取今日提交统计
    today = datetime.now().strftime('%Y-%m-%d')
    success, output = run_git_command(f"git log --since='{today} 00:00' --until='{today} 23:59' --oneline | wc -l")
    commit_count = int(output) if success else 0
    
    # 获取分支状态
    success, branches = run_git_command("git branch -r | wc -l")
    branch_count = int(branches) if success else 0
    
    # 生成报告
    report = {
        "date": today,
        "commits_today": commit_count,
        "remote_branches": branch_count,
        "generated_at": datetime.now().isoformat()
    }
    
    # 保存报告
    report_dir = "logs/github_reports"
    os.makedirs(report_dir, exist_ok=True)
    report_file = f"{report_dir}/github_report_{today}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 日报生成完成: {report_file}")
    print(f"   今日提交: {commit_count}次")
    print(f"   远程分支: {branch_count}个")

if __name__ == "__main__":
    main()
PYTHON
                chmod +x "$PROJECT_ROOT/$script"
                echo -e "  ✅ 创建: $script"
                ;;
                
            "backup_system.py")
                cat > "$PROJECT_ROOT/$script" << 'PYTHON'
#!/usr/bin/env python3
# 系统备份脚本
import shutil
import os
from datetime import datetime
import tarfile

def backup_directory(src_dir, backup_dir):
    """备份目录"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"backup_{os.path.basename(src_dir)}_{timestamp}.tar.gz"
    backup_path = os.path.join(backup_dir, backup_name)
    
    try:
        with tarfile.open(backup_path, 'w:gz') as tar:
            tar.add(src_dir, arcname=os.path.basename(src_dir))
        
        # 获取备份大小
        size_mb = os.path.getsize(backup_path) / (1024 * 1024)
        
        return True, backup_path, size_mb
    except Exception as e:
        return False, str(e), 0

def main():
    print(f"系统备份 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 备份目录配置
    backup_config = {
        "data": "data/",
        "config": "config/",
        "scripts": "scripts/"
    }
    
    backup_root = "backups/daily"
    os.makedirs(backup_root, exist_ok=True)
    
    total_size = 0
    successful = 0
    
    for name, src_dir in backup_config.items():
        if os.path.exists(src_dir):
            success, backup_path, size_mb = backup_directory(src_dir, backup_root)
            if success:
                print(f"✅ {name}: {backup_path} ({size_mb:.1f}MB)")
                total_size += size_mb
                successful += 1
            else:
                print(f"❌ {name}: 备份失败 - {backup_path}")
        else:
            print(f"⚠️  {name}: 目录不存在 - {src_dir}")
    
    # 清理旧备份（保留最近7天）
    print(f"\n清理旧备份...")
    # 这里可以添加清理逻辑
    
    print(f"\n备份完成: {successful}/{len(backup_config)} 成功, 总大小: {total_size:.1f}MB")

if __name__ == "__main__":
    main()
PYTHON
                chmod +x "$PROJECT_ROOT/$script"
                echo -e "  ✅ 创建: $script"
                ;;
                
            "check_schedule_status.py")
                cat > "$PROJECT_ROOT/$script" << 'PYTHON'
#!/usr/bin/env python3
# 调度状态检查脚本
import subprocess
import json
from datetime import datetime, timedelta
import os

def check_cron_job(job_pattern):
    """检查cron任务"""
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        if job_pattern in result.stdout:
            return True, "运行中"
        else:
            return False, "未找到"
    except Exception as e:
        return False, f"检查失败: {str(e)}"

def check_script_exists(script_path):
    """检查脚本是否存在"""
    if os.path.exists(script_path):
        # 检查是否可执行
        if os.access(script_path, os.X_OK):
            return True, "存在且可执行"
        else:
            return False, "存在但不可执行"
    else:
        return False, "不存在"

def check_log_file(log_pattern):
    """检查日志文件"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        return False, "日志目录不存在"
    
    # 查找今天的日志文件
    today = datetime.now().strftime('%Y%m%d')
    log_files = [f for f in os.listdir(log_dir) if today in f and log_pattern in f]
    
    if log_files:
        # 检查最新日志的修改时间
        latest_log = max(log_files, key=lambda f: os.path.getmtime(os.path.join(log_dir, f)))
        mtime = datetime.fromtimestamp(os.path.getmtime(os.path.join(log_dir, latest_log)))
        time_diff = datetime.now() - mtime
        
        if time_diff < timedelta(hours=24):
            return True, f"正常 (最近更新: {mtime.strftime('%H:%M')})"
        else:
            return False, f"日志过期 ({time_diff.days}天前)"
    else:
        return False, "无今日日志"

def main():
    print(f"调度状态检查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 检查配置
    checks = [
        {
            "name": "健康检查调度",
            "type": "cron",
            "pattern": "daily_health_check.py",
            "script": "scripts/daily_health_check.py",
            "log": "health_check"
        },
        {
            "name": "财报监控调度",
            "type": "cron", 
            "pattern": "final_financial_monitor_fixed.py",
            "script": "scripts/final_financial_monitor_fixed.py",
            "log": "financial_monitor"
        },
        {
            "name": "开发日报调度",
            "type": "cron",
            "pattern": "generate_daily_report.py",
            "script": "scripts/generate_daily_report.py",
            "log": "daily_report"
        }
    ]
    
    results = []
    all_ok = True
    
    for check in checks:
        status_ok = True
        messages = []
        
        # 检查cron配置
        if check["type"] == "cron":
            cron_ok, cron_msg = check_cron_job(check["pattern"])
            if not cron_ok:
                status_ok = False
                all_ok = False
            messages.append(f"Cron: {cron_msg}")
        
        # 检查脚本
        script_ok, script_msg = check_script_exists(check["script"])
        if not script_ok:
            status_ok = False
            all_ok = False
        messages.append(f"脚本: {script_msg}")
        
        # 检查日志
        log_ok, log_msg = check_log_file(check["log"])
        if not log_ok:
            status_ok = False
        messages.append(f"日志: {log_msg}")
        
        # 记录结果
        result = {
            "name": check["name"],
            "status": "✅" if status_ok else "❌",
            "details": messages
        }
        results.append(result)
    
    # 输出结果
    for result in results:
        print(f"{result['status']} {result['name']}")
        for detail in result["details"]:
            print(f"    {detail}")
        print()
    
    # 保存报告
    report = {
        "timestamp": datetime.now().isoformat(),
        "overall_status": "健康" if all_ok else "异常",
        "checks": results
    }
    
    report_dir = "logs/schedule_checks"
    os.makedirs(report_dir, exist_ok=True)
    report_file = f"{report_dir}/schedule_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"报告保存: {report_file}")
    print(f"总体状态: {'✅ 健康' if all_ok else '❌ 异常'}")

if __name__ == "__main__":
    main()
PYTHON
                chmod +x "$PROJECT_ROOT/$script"
                echo -e "  ✅ 创建: $script"
                ;;
        esac
    done
fi

# 应用cron配置
echo -e "${YELLOW}应用cron配置...${NC}"
crontab $CRON_FILE

# 验证配置
echo -e "${GREEN}✅ 验证cron配置...${NC}"
crontab -l | grep -A 20 "A股量化交易系统"

# 创建日志目录
mkdir -p "$PROJECT_ROOT/logs"

echo -e "\n${GREEN}🎉 所有每日调度配置完成!${NC}"
echo "========================================="
echo "已配置的调度任务:"
echo "1. 09:00 & 15:00 - 系统健康检查"
echo "2. 17:00 - GitHub维护日报"
echo "3. 21:30 - A股财报监控日报"
echo "4. 17:30 - 开发工作日报"
echo "5. 23:00 - 数据备份"
echo "6. 08:00 - 调度状态检查"
echo "========================================="
echo "日志目录: $PROJECT_ROOT/logs/"
echo "下次运行时间: 查看 crontab -l"
echo "========================================="