#!/bin/bash
# 启动交易时间监控系统

echo "📈 启动实时股票监控系统"
echo "=" * 50

# 检查当前时间
CURRENT_TIME=$(date +"%H:%M")
WEEKDAY=$(date +"%u")  # 1=周一, 5=周五

echo "🕐 当前时间: $CURRENT_TIME"
echo "📅 星期: $WEEKDAY"

# 检查是否为交易日
if [ "$WEEKDAY" -ge 6 ]; then
    echo "⏸️ 非交易日（周六日），不启动监控"
    exit 0
fi

# 检查是否为交易时间
if [[ "$CURRENT_TIME" < "09:30" ]] || \
   [[ "$CURRENT_TIME" > "11:30" && "$CURRENT_TIME" < "13:00" ]] || \
   [[ "$CURRENT_TIME" > "15:00" ]]; then
    echo "⏸️ 非交易时间，不启动监控"
    echo "   交易时间: 09:30-11:30, 13:00-15:00"
    
    # 计算下次启动时间
    if [[ "$CURRENT_TIME" < "09:30" ]]; then
        NEXT_START="09:30"
    elif [[ "$CURRENT_TIME" > "11:30" && "$CURRENT_TIME" < "13:00" ]]; then
        NEXT_START="13:00"
    else
        NEXT_START="明天 09:30"
    fi
    
    echo "   ⏰ 下次启动时间: $NEXT_START"
    exit 0
fi

echo "✅ 当前为交易时间，启动监控系统..."

# 切换到工作目录
cd /Users/ago/.openclaw/workspace

# 检查是否已在运行
if pgrep -f "real_time_stock_monitor.py" > /dev/null; then
    echo "⚠️ 监控系统已在运行中"
    echo "   进程ID: $(pgrep -f "real_time_stock_monitor.py")"
    exit 0
fi

# 启动监控系统
echo "🚀 启动监控进程..."
nohup python3 scripts/real_time_stock_monitor.py > logs/trading_monitor.log 2>&1 &

# 等待进程启动
sleep 2

# 检查是否启动成功
if pgrep -f "real_time_stock_monitor.py" > /dev/null; then
    PID=$(pgrep -f "real_time_stock_monitor.py")
    echo "✅ 监控系统启动成功"
    echo "   进程ID: $PID"
    echo "   日志文件: logs/trading_monitor.log"
    echo "   监控日志: data/investment_tracking/monitor_log_$(date +%Y%m%d).log"
else
    echo "❌ 监控系统启动失败"
    echo "   请检查日志: logs/trading_monitor.log"
    exit 1
fi

echo ""
echo "📊 监控内容:"
echo "   1. 每3分钟获取5只股票的最新价格"
echo "   2. 当价格达到进场点位时自动模拟成交"
echo "   3. 持续跟踪已进场股票的盈亏情况"
echo "   4. 自动执行止损止盈操作"
echo "   5. 记录所有交易和价格变化"

echo ""
echo "🔍 查看状态:"
echo "   tail -f logs/trading_monitor.log"
echo "   tail -f data/investment_tracking/monitor_log_$(date +%Y%m%d).log"

echo ""
echo "🛑 停止监控:"
echo "   pkill -f \"real_time_stock_monitor.py\""

echo ""
echo "🎉 实时股票监控系统已启动！"