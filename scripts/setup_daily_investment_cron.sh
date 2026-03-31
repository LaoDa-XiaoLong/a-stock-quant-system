#!/bin/bash
# 设置每日投资报告定时任务

echo "📅 设置每日投资报告定时任务"
echo "=" * 50

# 创建plist文件
PLIST_FILE="$HOME/Library/LaunchAgents/com.openclaw.daily_investment_report.plist"

cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openclaw.daily_investment_report</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/ago/.openclaw/workspace/scripts/daily_investment_report.py</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>/Users/ago/.openclaw/workspace</string>
    
    <key>StandardOutPath</key>
    <string>/Users/ago/.openclaw/workspace/logs/daily_investment_report.log</string>
    
    <key>StandardErrorPath</key>
    <string>/Users/ago/.openclaw/workspace/logs/daily_investment_report.error.log</string>
    
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>16</integer>
        <key>Minute</key>
        <integer>0</integer>
        <key>Weekday</key>
        <integer>1</integer>
    </dict>
    
    <key>RunAtLoad</key>
    <false/>
    
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
EOF

echo "✅ 创建plist文件: $PLIST_FILE"

# 创建日志目录
mkdir -p /Users/ago/.openclaw/workspace/logs

# 加载任务
launchctl unload "$PLIST_FILE" 2>/dev/null
launchctl load "$PLIST_FILE"

echo "✅ 加载launchd任务"

# 检查状态
echo ""
echo "🔍 任务状态:"
launchctl list | grep openclaw

echo ""
echo "📅 执行时间:"
echo "  每周一至周五 16:00 (收盘后)"
echo "  下次执行: 明天16:00"

echo ""
echo "📁 相关文件:"
echo "  1. $PLIST_FILE - launchd配置文件"
echo "  2. /Users/ago/.openclaw/workspace/scripts/daily_investment_report.py - 报告脚本"
echo "  3. /Users/ago/.openclaw/workspace/logs/daily_investment_report.log - 输出日志"
echo "  4. /Users/ago/.openclaw/workspace/data/investment_tracking/ - 报告目录"

echo ""
echo "💡 手动运行:"
echo "  cd /Users/ago/.openclaw/workspace && python3 scripts/daily_investment_report.py"

echo ""
echo "🎉 每日投资报告定时任务设置完成！"