# A股实时价格API Skill

## 技能概述
本技能提供A股市场实时价格数据获取功能，支持在交易日开盘期间每3分钟获取一次A股全部股票价格，并保存在本地文件。

## 技能作者
量化小助理

## 创建时间
2026-04-01

## 技能版本
v1.0

## 核心功能

### 1. 实时价格获取
- 获取A股全部股票实时价格
- 支持沪深两市股票
- 包含涨跌幅、成交量等关键数据

### 2. 定时数据更新
- 交易日开盘期间（09:30-15:00）每3分钟获取一次
- 自动识别交易日和非交易日
- 支持北京时区（GMT+8）

### 3. 数据存储
- 按日期和时间分层存储
- 支持CSV和JSON格式
- 完整的数据备份机制

### 4. 数据质量监控
- 数据完整性检查
- 异常数据处理
- 网络错误重试机制

## 使用方法

### 基本使用
```python
from skills.a_stock_realtime_api import AStockRealtimeAPI

# 创建API实例
api = AStockRealtimeAPI()

# 获取实时价格
prices = api.get_realtime_prices()

# 获取指定股票价格
stock_price = api.get_stock_price("600519")
```

### 定时任务
```python
# 启动3分钟间隔的数据获取
api.start_realtime_monitoring(interval_minutes=3)

# 停止监控
api.stop_realtime_monitoring()
```

### 数据查询
```python
# 查询历史价格
history = api.get_price_history("600519", "2026-04-01")

# 获取最新价格文件
latest_file = api.get_latest_price_file()
```

## 配置参数

### 数据源配置
```json
{
  "data_sources": {
    "primary": "akshare",
    "backup": "tushare",
    "fallback": "sina_finance"
  },
  "update_interval": 3,
  "trading_hours": {
    "start": "09:30",
    "end": "15:00"
  },
  "storage": {
    "base_dir": "data/realtime_prices",
    "format": "csv",
    "backup_days": 30
  }
}
```

### 股票范围配置
```json
{
  "stock_universe": {
    "include_all": true,
    "exclude_st": true,
    "exclude_suspended": true,
    "min_price": 1.0,
    "max_price": 1000.0
  }
}
```

## 文件结构

```
data/realtime_prices/
├── 2026-04-01/
│   ├── 09:30/
│   │   ├── prices_093000.csv
│   │   └── prices_093000.json
│   ├── 09:33/
│   │   ├── prices_093300.csv
│   │   └── prices_093300.json
│   └── ...
├── 2026-04-02/
│   └── ...
├── stock_list.csv
├── trading_calendar.json
└── monitoring_log.json
```

## 错误处理

### 网络错误
- 自动重试3次
- 切换备用数据源
- 记录错误日志

### 数据异常
- 价格异常值过滤
- 缺失数据处理
- 数据一致性检查

### 系统错误
- 磁盘空间检查
- 内存使用监控
- 进程健康检查

## 性能优化

### 数据压缩
- 使用gzip压缩历史数据
- 增量更新机制
- 数据分区存储

### 内存管理
- 分批获取大数据
- 及时释放内存
- 缓存优化

### 网络优化
- 并发请求控制
- 连接池管理
- 超时设置优化

## 监控与报警

### 系统监控
- 数据更新频率监控
- 数据完整性监控
- 系统资源监控

### 报警机制
- 数据更新失败报警
- 数据质量异常报警
- 系统异常报警

## 集成示例

### 与尾盘选股法集成
```python
from skills.a_stock_realtime_api import AStockRealtimeAPI
from strategies.tail_end_selection import TailEndSelectionStrategy

# 获取实时价格
api = AStockRealtimeAPI()
prices = api.get_latest_prices()

# 运行尾盘选股策略
strategy = TailEndSelectionStrategy()
selected_stocks = strategy.select_stocks(prices)

# 记录交易
strategy.record_trades(selected_stocks)
```

### 与报告系统集成
```python
from skills.a_stock_realtime_api import AStockRealtimeAPI
from reporting.daily_report import DailyReportGenerator

# 获取当日价格数据
api = AStockRealtimeAPI()
daily_data = api.get_daily_summary("2026-04-01")

# 生成日报
report = DailyReportGenerator()
report.generate(daily_data)
report.send_to_group("A股数据分析群")
```

## 维护指南

### 日常维护
1. 检查数据更新状态
2. 清理过期数据
3. 备份重要数据

### 故障排查
1. 检查网络连接
2. 验证API密钥
3. 查看错误日志

### 性能调优
1. 调整更新间隔
2. 优化数据存储
3. 改进错误处理

## 更新日志

### v1.0 (2026-04-01)
- 初始版本发布
- 支持akshare数据源
- 实现3分钟间隔更新
- 完整的数据存储系统

## 注意事项

1. **数据延迟**: 实时数据有1-2秒延迟
2. **API限制**: 注意数据源API调用限制
3. **存储空间**: 每日数据量约500MB
4. **网络要求**: 需要稳定的网络连接

## 技术支持

如有问题，请联系：
- 作者：量化小助理
- 创建时间：2026-04-01
- 最后更新：2026-04-01