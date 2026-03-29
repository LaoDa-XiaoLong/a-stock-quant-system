#!/bin/bash
# 手动安装cron任务

echo "手动安装cron任务..."
echo "========================================="

# 创建cron条目
CRON_ENTRIES=(
    "# A股量化交易系统 - 每日调度配置"
    "# 生成时间: $(date)"
    ""
    "# 1. 系统健康检查 (每天9:00和15:00)"
    "0 9,15 * * * cd /Users/ago/.openclaw/workspace && python scripts/daily_health_check.py >> logs/health_check_\$(date +\\%Y\\%m\\%d).log 2>&1"
    ""
    "# 2. GitHub维护日报 (每天17:00)"
    "0 17 * * * cd /Users/ago/.openclaw/workspace && python scripts/github_daily_report.py >> logs/github_report_\$(date +\\%Y\\%m\\%d).log 2>&1"
    ""
    "# 3. A股财报监控日报 (每天21:30)"
    "30 21 * * * cd /Users/ago/.openclaw/workspace && python scripts/final_financial_monitor_fixed.py >> logs/financial_monitor_\$(date +\\%Y\\%m\\%d).log 2>&1"
    ""
    "# 4. 开发工作日报 (每天17:30)"
    "30 17 * * * cd /Users/ago/.openclaw/workspace && python scripts/generate_daily_report.py >> logs/daily_report_\$(date +\\%Y\\%m\\%d).log 2>&1"
    ""
    "# 5. 数据备份 (每天23:00)"
    "0 23 * * * cd /Users/ago/.openclaw/workspace && python scripts/backup_system.py >> logs/backup_\$(date +\\%Y\\%m\\%d).log 2>&1"
    ""
    "# 6. 调度状态检查 (每天8:00)"
    "0 8 * * * cd /Users/ago/.openclaw/workspace && python scripts/check_schedule_status.py >> logs/schedule_status_\$(date +\\%Y\\%m\\%d).log 2>&1"
)

# 创建cron文件
CRON_FILE="/tmp/quant_system_cron"
> $CRON_FILE
for entry in "${CRON_ENTRIES[@]}"; do
    echo "$entry" >> $CRON_FILE
done

echo "创建的cron文件内容:"
echo "========================================="
cat $CRON_FILE
echo "========================================="

echo ""
echo "安装方法:"
echo "1. 复制以上内容"
echo "2. 运行: crontab -e"
echo "3. 粘贴到文件末尾"
echo "4. 保存并退出"
echo ""
echo "或者运行: cat $CRON_FILE | crontab -"
echo ""
echo "检查当前cron: crontab -l"
echo "========================================="