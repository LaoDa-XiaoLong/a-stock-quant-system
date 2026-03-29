#!/bin/bash
# 最终cron配置

echo "最终cron配置安装..."
echo "========================================="

# 创建cron配置
CRON_CONTENT="# A股量化交易系统 - 每日调度配置
# 生成时间: $(date)

# 1. 系统健康检查 (每天9:00和15:00)
0 9,15 * * * cd /Users/ago/.openclaw/workspace && python3 scripts/daily_health_check.py >> logs/health_check_\$(date +\\%Y\\%m\\%d).log 2>&1

# 2. GitHub维护日报 (每天17:00)
0 17 * * * cd /Users/ago/.openclaw/workspace && python3 scripts/github_daily_report.py >> logs/github_report_\$(date +\\%Y\\%m\\%d).log 2>&1

# 3. A股财报监控日报 (每天21:30)
30 21 * * * cd /Users/ago/.openclaw/workspace && python3 scripts/final_financial_monitor_fixed.py >> logs/financial_monitor_\$(date +\\%Y\\%m\\%d).log 2>&1

# 4. 开发工作日报 (每天17:30)
30 17 * * * cd /Users/ago/.openclaw/workspace && python3 scripts/generate_daily_report.py >> logs/daily_report_\$(date +\\%Y\\%m\\%d).log 2>&1

# 5. 数据备份 (每天23:00)
0 23 * * * cd /Users/ago/.openclaw/workspace && python3 scripts/backup_system.py >> logs/backup_\$(date +\\%Y\\%m\\%d).log 2>&1

# 6. 调度状态检查 (每天8:00)
0 8 * * * cd /Users/ago/.openclaw/workspace && python3 scripts/check_schedule_status.py >> logs/schedule_status_\$(date +\\%Y\\%m\\%d).log 2>&1"

# 保存到文件
echo "$CRON_CONTENT" > /tmp/final_quant_cron

echo "cron配置内容:"
echo "========================================="
cat /tmp/final_quant_cron
echo "========================================="

echo ""
echo "安装说明:"
echo "1. 运行: crontab -e"
echo "2. 粘贴以上内容"
echo "3. 保存退出 (:wq)"
echo ""
echo "或者运行: cat /tmp/final_quant_cron | crontab -"
echo ""
echo "验证安装: crontab -l"
echo "========================================="
echo "✅ 所有每日调度脚本已准备就绪!"
echo "   6个调度任务，使用python3执行"
echo "   日志输出到 logs/ 目录"
echo "   下次运行时间按配置执行"