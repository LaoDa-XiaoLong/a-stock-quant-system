# 尾盘选股法 Skill

## 技能概述
本技能基于"杨永兴隔夜套利战法"实现尾盘选股策略，每日基于真实价格运行策略进场，记录进场价格和仓位，并将交易记录保存在本地，每日汇报到"A股数据分析群"。

## 技能作者
量化小助理

## 创建时间
2026-04-01

## 技能版本
v1.0

## 核心功能

### 1. 尾盘选股策略
- 基于杨永兴隔夜套利战法
- 六大选股步骤科学筛选
- 基于真实价格数据执行

### 2. 交易记录管理
- 完整记录每笔模拟交易
- 实时跟踪持仓状态
- 自动检查止盈止损

### 3. 每日自动执行
- 交易日14:30自动执行选股
- 交易日18:00自动生成报告
- 自动发送报告到A股数据分析群

### 4. 绩效统计分析
- 胜率统计
- 平均盈亏分析
- 投资组合绩效跟踪

## 使用方法

### 基本使用
```python
from skills.tail_end_selection import TailEndSelection

# 创建选股实例
selector = TailEndSelection()

# 运行尾盘选股
selected_stocks = selector.run_selection()

# 记录交易
selector.record_trades(selected_stocks)
```

### 定时任务
```python
# 启动每日自动执行
selector.start_daily_execution()

# 生成每日报告
report = selector.generate_daily_report()

# 发送报告到群
selector.send_report_to_group(report, "A股数据分析群")
```

### 交易查询
```python
# 查询活跃交易
active_trades = selector.get_active_trades()

# 查询历史交易
history = selector.get_trade_history("2026-04-01")

# 获取绩效统计
performance = selector.get_performance_summary()
```

## 配置参数

### 策略配置
```json
{
  "strategy": {
    "name": "尾盘选股法",
    "version": "v1.0",
    "selection_time": "14:30",
    "report_time": "18:00",
    "selection_steps": {
      "time_window": 20,
      "price_change": 20,
      "capital_flow": 25,
      "volume_ratio": 15,
      "market_cap": 10,
      "tech_space": 10
    },
    "entry_strategy": {
      "premium_grade": {"min_score": 90, "stop_loss": 0.97, "target_gain": 0.08},
      "good_grade": {"min_score": 80, "stop_loss": 0.96, "target_gain": 0.06},
      "normal_grade": {"min_score": 70, "stop_loss": 0.95, "target_gain": 0.05}
    }
  }
}
```

### 交易配置
```json
{
  "trading": {
    "initial_capital": 1000000,
    "max_position_percent": 0.3,
    "max_daily_loss": 0.05,
    "max_trade_loss": 0.02,
    "min_score": 70
  }
}
```

### 报告配置
```json
{
  "reporting": {
    "daily_report": true,
    "weekly_report": true,
    "monthly_report": true,
    "send_to_group": "A股数据分析群",
    "report_format": "markdown"
  }
}
```

## 文件结构

```
data/tail_end_selection/
├── trades/
│   ├── simulated_trades.json          # 所有交易记录
│   ├── simulated_portfolio.json       # 投资组合状态
│   └── performance_summary.json       # 绩效历史
├── reports/
│   ├── daily/
│   │   ├── report_20260401.md
│   │   └── report_20260402.md
│   ├── weekly/
│   │   └── report_week_14.md
│   └── monthly/
│       └── report_202604.md
├── selection_results/
│   ├── 2026-04-01/
│   │   ├── selection_143000.json
│   │   └── selection_143000.md
│   └── 2026-04-02/
│       └── ...
└── logs/
    ├── execution_20260401.log
    └── execution_20260402.log
```

## 选股步骤

### 1. 时间筛选 (20分)
- 14:30之后进场
- 尾盘时段风险已释放

### 2. 涨跌幅筛选 (20分)
- 3%~5%涨幅为最佳
- 适度上涨，有冲劲但不过热

### 3. 资金流向筛选 (25分)
- 主力资金净流入
- 大单资金持续流入

### 4. 成交量筛选 (15分)
- 量比>1.7为最佳
- 放量明显，有资金关注

### 5. 市值筛选 (10分)
- 市值<200亿为最佳
- 中小盘股，弹性好

### 6. 技术形态筛选 (10分)
- 5%~10%涨幅空间
- 有继续上涨的技术空间

## 进场策略

### 评分等级
- **优质股 (≥90分)**: 激进进场，止损3%，目标8%
- **良好股 (80-89分)**: 稳健进场，止损4%，目标6%
- **一般股 (70-79分)**: 保守进场，止损5%，目标5%

### 仓位管理
- 重仓: 不超过总资金的30%
- 中等仓位: 不超过总资金的20%
- 轻仓: 不超过总资金的10%

## 风险控制

### 止损策略
- 严格执行止损纪律
- 达到止损价立即平仓
- 避免情绪化交易

### 仓位控制
- 单只股票不超过总资金的30%
- 总仓位根据市场环境调整
- 分散投资降低风险

### 资金管理
- 保留足够备用资金
- 分批进场降低风险
- 及时止盈锁定利润

## 集成示例

### 与实时价格API集成
```python
from skills.a_stock_realtime_api import AStockRealtimeAPI
from skills.tail_end_selection import TailEndSelection

# 获取实时价格
api = AStockRealtimeAPI()
prices = api.get_latest_prices()

# 运行尾盘选股
selector = TailEndSelection()
selected = selector.select_stocks(prices)

# 记录交易
selector.record_trades(selected)
```

### 与报告系统集成
```python
from skills.tail_end_selection import TailEndSelection
from reporting.feishu_sender import FeishuSender

# 生成每日报告
selector = TailEndSelection()
report = selector.generate_daily_report()

# 发送到飞书群
sender = FeishuSender()
sender.send_to_group(report, "A股数据分析群")
```

### 定时任务配置
```python
# 每日14:30执行选股
30 14 * * 1-5 python3 -m skills.tail_end_selection --execute-selection

# 每日18:00生成报告
0 18 * * 1-5 python3 -m skills.tail_end_selection --daily-report
```

## 维护指南

### 日常维护
1. 检查交易记录完整性
2. 验证价格数据准确性
3. 监控策略执行状态

### 策略优化
1. 定期回顾策略绩效
2. 调整选股参数
3. 优化风险控制规则

### 故障排查
1. 检查数据源连接
2. 验证交易记录文件
3. 查看执行日志

## 更新日志

### v1.0 (2026-04-01)
- 初始版本发布
- 基于杨永兴战法实现
- 完整的交易记录系统
- 自动报告生成功能

## 注意事项

1. **模拟交易**: 当前为模拟交易系统
2. **数据延迟**: 实时价格有轻微延迟
3. **策略风险**: 历史表现不代表未来收益
4. **执行纪律**: 需要严格按时执行

## 技术支持

如有问题，请联系：
- 作者：量化小助理
- 创建时间：2026-04-01
- 最后更新：2026-04-01