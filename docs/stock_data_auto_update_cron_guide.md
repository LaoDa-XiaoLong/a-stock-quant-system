# 股票数据自动更新Cron任务配置指南

## 任务概述
**任务ID**: `cron:460a0986-c641-441e-9d7b-6c28f347a5c2`  
**任务名称**: 股票数据自动更新  
**版本**: v1.0  
**功能**: 每日自动获取A股数据并应用选股策略

## 已实现功能
### ✅ 核心功能
1. **实时数据获取**: 使用akshare获取A股实时行情
2. **选股策略筛选**: 多因子综合评分选股
3. **数据文件更新**: 自动更新本地数据文件
4. **报告生成**: 生成详细执行报告和日志

### ✅ 输出文件
```
data/
├── raw/spot_data_YYYYMMDD_HHMMSS.csv      # 实时行情数据
├── stock_list_simple.csv                  # 股票列表
└── stock_pool/screening_results_YYYYMMDD_HHMMSS.json  # 筛选结果

reports/
└── stock_update_report_YYYYMMDD_HHMMSS.md  # 执行报告

logs/
└── update_log_simple_YYYYMMDD.json         # 执行日志
```

## 脚本文件
### 主要脚本
- `scripts/simple_stock_update.py` - **推荐使用**，简化稳定版
- `scripts/stock_data_auto_update_v1.py` - 完整功能版（需要优化）

### 依赖包
```bash
pip install akshare pandas numpy
```

## Cron任务配置

### 方案一：使用OpenClaw Cron系统（推荐）
```json
{
  "name": "股票数据每日更新",
  "schedule": {
    "kind": "cron",
    "expr": "30 9 * * 1-5",  // 工作日09:30执行
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "执行股票数据自动更新任务（v1.0版）：1. 使用akshare获取最新A股数据 2. 应用选股策略筛选 3. 更新本地数据文件",
    "model": "deepseek/deepseek-chat"
  },
  "sessionTarget": "isolated",
  "delivery": {
    "mode": "announce",
    "channel": "feishu"  // 可根据需要调整
  },
  "enabled": true
}
```

### 方案二：Linux Crontab
```bash
# 编辑crontab
crontab -e

# 添加以下行（工作日09:30执行）
30 9 * * 1-5 cd /Users/ago/.openclaw/workspace && /usr/local/bin/python3 scripts/simple_stock_update.py >> logs/cron_stock_update.log 2>&1
```

### 方案三：多个执行时间点
```json
// 多个cron任务配置
[
  {
    "name": "开盘前数据更新",
    "schedule": {"kind": "cron", "expr": "45 8 * * 1-5", "tz": "Asia/Shanghai"},
    "payload": {"kind": "agentTurn", "message": "执行开盘前股票数据更新"},
    "enabled": true
  },
  {
    "name": "盘中数据更新",
    "schedule": {"kind": "cron", "expr": "30 11 * * 1-5", "tz": "Asia/Shanghai"},
    "payload": {"kind": "agentTurn", "message": "执行盘中股票数据更新"},
    "enabled": true
  },
  {
    "name": "收盘后数据更新",
    "schedule": {"kind": "cron", "expr": "15 15 * * 1-5", "tz": "Asia/Shanghai"},
    "payload": {"kind": "agentTurn", "message": "执行收盘后股票数据完整更新"},
    "enabled": true
  }
]
```

## 执行频率建议

### 高频更新（适合日内交易）
- **09:15** - 开盘前数据准备
- **11:30** - 午间数据更新
- **14:30** - 尾盘数据更新
- **15:15** - 收盘完整更新

### 常规更新（适合波段交易）
- **09:30** - 每日一次更新（当前配置）
- **15:15** - 收盘后完整更新

### 低频更新（适合价值投资）
- **周一09:30** - 周度更新
- **每月第一个交易日** - 月度更新

## 监控与告警

### 成功指标
1. ✅ 数据文件正常生成
2. ✅ 筛选结果非空
3. ✅ 执行时间＜60秒
4. ✅ 错误日志为空

### 失败处理
1. **重试机制**: 失败后自动重试1次
2. **降级策略**: akshare失败时使用模拟数据
3. **告警通知**: 连续失败时发送告警

### 监控命令
```bash
# 检查最近执行状态
tail -f logs/update_log_simple_$(date +%Y%m%d).json

# 检查数据文件
ls -lh data/raw/spot_data_$(date +%Y%m%d)*.csv

# 检查筛选结果
cat data/stock_pool/screening_results_$(date +%Y%m%d)*.json | jq '.total_stocks'
```

## 性能优化

### 当前性能
- **执行时间**: 35-40秒
- **数据量**: 约500KB/次
- **内存占用**: ＜100MB
- **网络请求**: 1次主要API调用

### 优化建议
1. **增量更新**: 只更新变化的数据
2. **并行处理**: 多只股票数据并行获取
3. **缓存机制**: 缓存股票列表等不变数据
4. **请求合并**: 减少API调用次数

## 故障排除

### 常见问题
1. **akshare连接失败**
   - 检查网络连接
   - 验证akshare版本
   - 尝试使用代理

2. **数据文件为空**
   - 检查API响应
   - 验证数据解析逻辑
   - 查看详细错误日志

3. **执行超时**
   - 增加超时时间
   - 优化数据获取逻辑
   - 减少获取股票数量

4. **内存不足**
   - 减少同时处理的股票数量
   - 优化数据存储格式
   - 增加系统内存

### 调试命令
```bash
# 手动测试脚本
cd /Users/ago/.openclaw/workspace
python3 scripts/simple_stock_update.py

# 查看详细日志
tail -n 100 logs/update_log_simple_$(date +%Y%m%d).json

# 检查依赖
python3 -c "import akshare; import pandas; print('依赖检查通过')"
```

## 版本升级

### v1.0 → v1.1 计划
1. **增加历史数据获取**
2. **完善选股策略因子**
3. **添加数据质量检查**
4. **优化错误处理机制**

### v1.1 → v2.0 计划
1. **多数据源支持**
2. **策略回测框架**
3. **实时监控面板**
4. **预警通知系统**

## 安全注意事项
1. **数据安全**: 定期备份重要数据文件
2. **API限制**: 遵守akshare等数据源的调用频率限制
3. **访问控制**: 确保数据文件访问权限适当
4. **错误隔离**: 单次失败不影响整体系统

## 联系支持
- **问题反馈**: 查看`logs/`目录下的错误日志
- **功能请求**: 提交到项目issue跟踪
- **紧急问题**: 直接联系系统管理员

---
**最后更新**: 2026-03-30  
**文档版本**: v1.0  
**维护者**: 量化小助理 📈