
# 📅 GitHub自动同步 - OpenClaw调度配置

## 手动创建调度任务
```bash
openclaw cron add \
  --name "GitHub自动同步" \
  --schedule "*/30 * * * *" \
  --command "cd /Users/ago/.openclaw/workspace && python3 scripts/auto_git_sync.py --check" \
  --description "自动同步代码变更到GitHub"
```

## 验证任务
```bash
# 查看所有任务
openclaw cron list --all

# 手动测试
cd /Users/ago/.openclaw/workspace && python3 scripts/auto_git_sync.py --check
```

## 配置说明
- 检查间隔: 30分钟
- 工作分支: develop
- 自动提交: 是
- 自动推送: 是
