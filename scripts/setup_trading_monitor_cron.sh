#!/bin/bash
# 设置交易时间监控定时任务

echo "📅 设置交易时间监控定时任务"
echo "=" * 50

# 创建plist文件
PLIST_FILE="$HOME/Library/LaunchAgents/com.openclaw.trading_monitor.plist"

cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openclaw.trading_monitor</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Users/ago/.openclaw/workspace/scripts/start_trading_monitor.sh</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>/Users/ago/.openclaw/workspace</string>
    
    <key>StandardOutPath</key>
    <string>/Users/ago/.openclaw/workspace/logs/trading_monitor_cron.log</string>
    
    <key>StandardErrorPath</key>
    <string>/Users/ago/.openclaw/workspace/logs/trading_monitor_cron.error.log</string>
    
    <key>StartCalendarInterval</key>
    <array>
        <!-- 上午交易时间开始 -->
        <dict>
            <key>Hour</key>
            <integer>9</integer>
            <key>Minute</key>
            <integer>29</integer>
            <key>Weekday</key>
            <integer>1</integer>
        </dict>
        <dict>
            <key>Hour</key>
            <integer>9</integer>
            <key>Minute</key>
            <integer>29</integer>
            <key>Weekday</key>
            <integer>2</integer>
        </dict>
        <dict>
            <key>Hour</key>
            <integer>9</integer>
            <key>Minute</key>
            <integer>29</integer>
            <key>Weekday</key>
            <integer>3</integer>
        </dict>
        <dict>
            <key>Hour</key>
            <integer>9</integer>
            <key>Minute</key>
            <integer>29</integer>
            <key>Weekday</key>
            <integer>4</integer>
        </dict>
        <dict>
            <key>Hour</key>
            <integer>9</integer>
            <key>Minute</key>
            <integer>29</integer>
            <key>Weekday</key>
            <integer>5</integer>
        </dict>
        
        <!-- 下午交易时间开始 -->
        <dict>
            <key>Hour</key>
            <integer>12</integer>
            <key>Minute</key>
            <integer>59</integer>
            <key>Weekday</key>
            <integer>1</integer>
        </dict>
        <dict>
            <key>Hour</key>
            <integer>12</integer>
            <key>Minute</key>
            <integer>59</integer>
            <key>Weekday</key>
            <integer>2</integer>
        </dict>
        <dict>
            <key>Hour</key>
            <integer>12</integer>
            <key>Minute</key>
            <integer>59</integer>
            <key>Weekday</key>
            <integer>3</integer>
        </dict>
        <dict>
            <key>Hour</key>
            <integer>12</integer>
            <key>Minute</key>
            <integer>59</integer>
            <key>Weekday</key>
            <integer>4</integer>
        </dict>
        <dict>
            <key>Hour</key>
            <integer>12</integer>
            <key>Minute</key>
            <integer>59</integer>
            <key>Weekday</key>
            <integer>5</integer>
        </dict>
    </array>
    
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
launchctl list | grep openclaw.trading_monitor

echo ""
echo "📅 执行时间:"
echo "   周一至周五:"
echo "     - 上午: 09:29 (交易开始前1分钟)"
echo "     - 下午: 12:59 (交易开始前1分钟)"
echo ""
echo "💡 监控系统会在交易时间自动启动，非交易时间自动停止"

echo ""
echo "📁 相关文件:"
echo "  1. $PLIST_FILE - launchd配置文件"
echo "  2. /Users/ago/.openclaw/workspace/scripts/real_time_stock_monitor.py - 监控主程序"
echo "  3. /Users/ago/.openclaw/workspace/scripts/start_trading_monitor.sh - 启动脚本"
echo "  4. /Users/ago/.openclaw/workspace/logs/trading_monitor.log - 监控日志"
echo "  5. /Users/ago/.openclaw/workspace/data/investment_tracking/ - 数据目录"

echo ""
echo "🔧 手动操作:"
echo "  启动监控: bash scripts/start_trading_monitor.sh"
echo "  停止监控: pkill -f \"real_time_stock_monitor.py\""
echo "  查看日志: tail -f logs/trading_monitor.log"

echo ""
echo "🎉 交易时间监控定时任务设置完成！"
echo ""
echo "⚠️ 注意: 系统将在明天交易时间自动启动监控"
echo "   今天如需测试，请手动运行: bash scripts/start_trading_monitor.sh"