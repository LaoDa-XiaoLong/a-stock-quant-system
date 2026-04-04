# 📅 Cron任务配置：股票数据自动更新

## 任务信息
- **任务ID**: cron:460a0986-c641-441e-9d7b-6c28f347a5c2
- **任务名称**: 股票数据自动更新
- **版本**: v1.0 (已完成) + v1.1高效版 (已开发)
- **状态**: ✅ 已成功执行并验证

## 文件结构

### 核心脚本
```
.
├── cron_stock_data_update.py          # v1.0标准版本 (已验证)
├── cron_stock_data_update_fast.py     # v1.1高效版本 (已开发)
├── test_akshare_update.py             # akshare功能测试
├── test_code_matching.py              # 代码匹配逻辑测试
└── CRON_TASK_CONFIG.md               # 本配置文件
```

### 生成的数据文件
```
data/
├── stock_pool/
│   ├── selected_stocks_20260404_093101.csv    # 详细筛选结果
│   ├── latest_selected.csv                    # 最新简化结果
│   ├── update_record_20260404_093101.json     # 更新记录
│   └── cron_update_20260404.log               # 运行日志
├── stock_list_updated.csv                     # 更新的股票列表
└── reports/
    └── stock_update_report_20260404_093101.md # 详细报告
```

### 文档文件
```
.
├── 股票数据自动更新任务执行总结_2026-04-04.md     # 执行总结
├── 股票数据自动更新任务最终总结_2026-04-04.md     # 最终总结
└── 任务完成报告_股票数据自动更新.md               # 任务完成报告
```

## 配置说明

### 标准版本 (v1.0)
```bash
# 执行命令
python3 cron_stock_data_update.py

# 配置参数 (在脚本中修改)
config = {
    'max_stocks': 100,           # 最大处理股票数
    'min_turnover': 10000000,    # 最小成交额
    'price_range': (5, 500),     # 价格范围
    'change_limit': 5,           # 涨跌幅限制
    'use_real_data': True,       # 是否使用真实数据
}
```

### 高效版本 (v1.1)
```bash
# 执行命令
python3 cron_stock_data_update_fast.py

# 配置参数 (在脚本中修改)
config = {
    'max_stocks': 100,           # 最大处理股票数
    'min_turnover': 10000000,    # 最小成交额
    'price_range': (5, 500),     # 价格范围
    'change_limit': 5,           # 涨跌幅限制
    'use_real_data': True,       # 是否使用真实数据
    'retry_count': 2,            # 重试次数
    'retry_delay': 1,            # 重试延迟(秒)
    'cache_ttl': 300,            # 缓存有效期(秒)
    'batch_size': 50,            # 批量处理大小
}
```

## Cron配置示例

### 基础配置 (每小时执行)
```bash
# 编辑crontab
crontab -e

# 添加以下配置
# 交易时间每小时执行一次 (周一至周五 9:00-15:00)
0 9-15 * * 1-5 cd /Users/ago/.openclaw/workspace && /usr/local/bin/python3 cron_stock_data_update.py >> /tmp/stock_cron.log 2>&1

# 每天收盘后执行详细分析
30 15 * * 1-5 cd /Users/ago/.openclaw/workspace && /usr/local/bin/python3 cron_stock_data_update.py --full-analysis >> /tmp/stock_cron_daily.log 2>&1
```

### 高级配置 (使用高效版本)
```bash
# 使用高效版本，降低系统负载
0 9,10,13,14 * * 1-5 cd /Users/ago/.openclaw/workspace && /usr/local/bin/python3 cron_stock_data_update_fast.py >> /tmp/stock_cron_fast.log 2>&1

# 周末进行数据清理和维护
0 8 * * 6 cd /Users/ago/.openclaw/workspace && /usr/local/bin/python3 -c "import os; [os.remove(f) for f in os.listdir('data/stock_pool') if f.endswith('.csv') and 'latest' not in f and os.path.getmtime(f) < time.time()-604800]"
```

## 执行时间建议

### 最佳执行时间
| 时间 | 目的 | 建议版本 |
|------|------|----------|
| 09:30 | 开盘数据获取 | 标准版 |
| 10:30 | 盘中监控 | 高效版 |
| 13:00 | 午盘分析 | 高效版 |
| 14:00 | 尾盘选股 | 高效版 |
| 15:30 | 收盘总结 | 标准版 |

### 特殊日期处理
```bash
# 节假日不执行
# 需要手动维护节假日列表
0 9-15 * * 1-5 [ ! -f /tmp/holiday.today ] && cd /Users/ago/.openclaw/workspace && /usr/local/bin/python3 cron_stock_data_update.py
```

## 监控与维护

### 日志监控
```bash
# 查看最近执行日志
tail -f /tmp/stock_cron.log

# 查看错误日志
grep -i error /tmp/stock_cron.log

# 查看执行时间
grep "任务完成，总耗时" /tmp/stock_cron.log
```

### 文件监控
```bash
# 检查文件是否正常生成
ls -la data/stock_pool/latest_selected.csv

# 检查文件更新时间
stat data/stock_pool/latest_selected.csv

# 检查文件大小
du -sh data/stock_pool/*.csv
```

### 性能监控
```bash
# 监控Python进程
ps aux | grep cron_stock_data_update

# 监控内存使用
top -pid $(pgrep -f cron_stock_data_update)

# 监控执行时间
time python3 cron_stock_data_update.py
```

## 故障排除

### 常见问题
1. **akshare连接失败**
   ```bash
   # 测试akshare连接
   python3 test_akshare_update.py
   
   # 更新akshare
   pip install --upgrade akshare
   ```

2. **权限问题**
   ```bash
   # 检查文件权限
   ls -la cron_stock_data_update.py
   
   # 添加执行权限
   chmod +x cron_stock_data_update.py
   ```

3. **Python环境问题**
   ```bash
   # 检查Python版本
   python3 --version
   
   # 检查依赖
   pip list | grep akshare
   ```

4. **磁盘空间不足**
   ```bash
   # 检查磁盘空间
   df -h .
   
   # 清理旧文件
   find data/stock_pool -name "*.csv" -mtime +7 -delete
   ```

### 错误代码
| 代码 | 含义 | 解决方法 |
|------|------|----------|
| 0 | 成功执行 | - |
| 1 | 一般错误 | 查看日志文件 |
| 2 | 数据获取失败 | 检查网络连接 |
| 3 | 文件写入失败 | 检查磁盘权限 |
| 4 | 配置错误 | 检查config字典 |

## 升级与扩展

### 版本升级
1. **备份当前配置**
   ```bash
   cp cron_stock_data_update.py cron_stock_data_update.py.backup
   cp config.json config.json.backup
   ```

2. **测试新版本**
   ```bash
   python3 cron_stock_data_update_fast.py --test
   ```

3. **切换版本**
   ```bash
   # 修改crontab中的脚本路径
   # 从 cron_stock_data_update.py 改为 cron_stock_data_update_fast.py
   ```

### 功能扩展
1. **添加新数据源**
   - 修改`get_stock_data()`方法
   - 添加新的API接口调用
   - 实现数据格式转换

2. **添加新筛选策略**
   - 修改`apply_selection_strategy()`方法
   - 添加新的评分维度
   - 调整权重参数

3. **添加新报告格式**
   - 修改`generate_report()`方法
   - 添加HTML/PDF输出
   - 添加图表生成

## 安全注意事项

### 数据安全
1. **定期备份**
   ```bash
   # 备份数据文件
   tar -czf stock_data_backup_$(date +%Y%m%d).tar.gz data/
   
   # 备份配置文件
   cp cron_stock_data_update.py ~/backups/
   ```

2. **访问控制**
   ```bash
   # 设置文件权限
   chmod 600 data/stock_pool/*.csv
   chmod 644 cron_stock_data_update.py
   ```

3. **日志轮转**
   ```bash
   # 设置日志轮转
   logrotate -f /etc/logrotate.d/stock_cron
   ```

### 系统安全
1. **限制执行权限**
   ```bash
   # 创建专用用户
   sudo useradd -r -s /bin/false stockcron
   
   # 设置文件所有权
   sudo chown -R stockcron:stockcron /path/to/workspace
   ```

2. **网络隔离**
   ```bash
   # 限制网络访问
   iptables -A OUTPUT -p tcp --dport 443 -m owner --uid-owner stockcron -j ACCEPT
   iptables -A OUTPUT -m owner --uid-owner stockcron -j DROP
   ```

## 联系与支持

### 问题反馈
1. **查看日志**: `data/stock_pool/cron_update_*.log`
2. **检查配置**: 本配置文件中的相关设置
3. **测试功能**: 运行测试脚本验证功能

### 紧急恢复
1. **停止任务**
   ```bash
   # 停止所有相关进程
   pkill -f cron_stock_data_update
   ```

2. **恢复备份**
   ```bash
   # 恢复数据文件
   tar -xzf stock_data_backup_最新日期.tar.gz
   
   # 恢复配置文件
   cp ~/backups/cron_stock_data_update.py .
   ```

3. **重新启动**
   ```bash
   # 手动测试
   python3 cron_stock_data_update.py
   
   # 重新启用cron
   crontab -e
   ```

---
**配置维护**: 量化小助理 📈  
**最后更新**: 2026-04-04  
**状态**: ✅ 任务已成功配置并验证