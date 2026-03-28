# 多源数据获取器 Skill

## 概述
多源数据获取器是一个通用的数据源管理和获取框架，支持从多个数据源获取数据，并提供故障转移、缓存和一致性检查功能。

## 功能特性
- ✅ **多数据源支持**：A股、美股、港股等市场数据
- ✅ **智能故障转移**：主数据源失败时自动切换到备用
- ✅ **数据缓存机制**：减少API调用，提高响应速度
- ✅ **一致性检查**：多个数据源比对，确保数据准确性
- ✅ **可扩展架构**：轻松添加新的数据源

## 安装要求
```bash
pip install pandas requests akshare yfinance
```

## 快速开始

### 基本使用
```python
from multi_source_fetcher import MultiSourceFetcher

# 创建数据获取器
fetcher = MultiSourceFetcher()

# 获取股票数据
stock_data = fetcher.get_stock_data('000001', '平安银行')
print(f"最新价格: {stock_data.get('price', 0)}")
print(f"数据来源: {stock_data.get('source', 'unknown')}")
```

### 多源数据比对
```python
# 从多个数据源获取并比对
comparison = fetcher.compare_sources('AAPL', '苹果公司')
print(f"推荐数据源: {comparison['recommended_source']}")
print(f"价格共识: {comparison['consensus_price']}")
```

## 数据源配置

### 内置数据源
1. **A股数据源**
   - `akshare`: 免费A股数据（推荐）
   - `sina_finance`: 新浪财经实时数据
   - `eastmoney`: 东方财富数据

2. **美股数据源**
   - `yfinance`: Yahoo Finance数据
   - `alpha_vantage`: Alpha Vantage API
   - `iex_cloud`: IEX Cloud数据

3. **港股数据源**
   - `akshare_hk`: akshare港股数据
   - `sina_hk`: 新浪港股数据

### 自定义数据源
```python
# 添加自定义数据源
class MyCustomSource:
    def get_stock_data(self, symbol, name):
        # 实现数据获取逻辑
        return {
            'price': 100.0,
            'volume': 1000000,
            'source': 'my_custom_source'
        }

fetcher.add_source('my_custom', MyCustomSource(), priority=2)
```

## 使用场景

### 1. A股数据获取
```python
# 获取A股股票数据
a_stock_data = fetcher.get_a_stock_data('000001', '平安银行')

# 获取实时行情
realtime_data = fetcher.get_realtime_price('600519', '贵州茅台')

# 获取历史数据
history_data = fetcher.get_history_data('002352', '顺丰控股', 
                                       start_date='2026-01-01',
                                       end_date='2026-03-28')
```

### 2. 美股数据获取
```python
# 获取美股数据
us_stock_data = fetcher.get_us_stock_data('AAPL', '苹果公司')

# 获取纳斯达克指数
nasdaq_data = fetcher.get_index_data('^IXIC', '纳斯达克')

# 获取中概股数据
china_concept_data = fetcher.get_us_stock_data('BABA', '阿里巴巴')
```

### 3. 数据质量保障
```python
# 启用数据质量检查
fetcher.enable_quality_check(True)

# 设置最小数据质量分数
fetcher.set_min_quality_score(75)

# 获取经过质量检查的数据
quality_data = fetcher.get_quality_checked_data('000001', '平安银行')
```

## 缓存配置

### 缓存策略
```python
# 配置缓存
fetcher.configure_cache(
    enabled=True,
    cache_dir='./data/cache',
    ttl_minutes={
        'realtime': 5,      # 实时数据缓存5分钟
        'daily': 60,        # 日线数据缓存60分钟
        'historical': 1440  # 历史数据缓存24小时
    }
)
```

### 缓存管理
```python
# 清理过期缓存
fetcher.clean_expired_cache()

# 获取缓存统计
cache_stats = fetcher.get_cache_stats()
print(f"缓存命中率: {cache_stats['hit_rate']:.1%}")
print(f"缓存大小: {cache_stats['size_mb']:.1f} MB")
```

## 错误处理

### 故障转移
```python
# 配置故障转移
fetcher.configure_failover(
    enabled=True,
    max_retries=3,
    retry_delay=1.0  # 秒
)

# 获取数据（自动故障转移）
try:
    data = fetcher.get_stock_data('000001', '平安银行')
except DataFetchError as e:
    print(f"所有数据源都失败了: {e}")
    # 使用最后一次成功的缓存数据
    cached_data = fetcher.get_cached_data('000001')
```

### 监控和报警
```python
# 设置数据源健康监控
fetcher.monitor_source_health()

# 获取数据源状态
source_status = fetcher.get_source_status()
for source, status in source_status.items():
    print(f"{source}: {'✅ 正常' if status['healthy'] else '❌ 异常'}")
```

## 性能优化

### 批量获取
```python
# 批量获取多个股票数据
symbols = ['000001', '000002', '002352', '600519']
batch_data = fetcher.batch_get_stock_data(symbols)

# 异步获取
async_data = await fetcher.async_get_stock_data('000001')
```

### 连接池管理
```python
# 配置连接池
fetcher.configure_connection_pool(
    max_connections=10,
    pool_timeout=30.0
)
```

## 集成示例

### 集成到交易系统
```python
class TradingSystem:
    def __init__(self):
        self.fetcher = MultiSourceFetcher()
        self.fetcher.configure_cache(enabled=True)
    
    def get_market_data(self, symbol, name):
        """获取市场数据，包含故障转移"""
        try:
            # 尝试从主数据源获取
            data = self.fetcher.get_stock_data(symbol, name)
            
            # 检查数据质量
            if self._check_data_quality(data):
                return data
            
            # 数据质量不合格，尝试其他数据源
            comparison = self.fetcher.compare_sources(symbol, name)
            return comparison['consensus_data']
            
        except Exception as e:
            logger.error(f"获取数据失败: {e}")
            # 返回缓存数据或默认值
            return self._get_fallback_data(symbol)
```

## 最佳实践

### 1. 数据源优先级设置
```python
# 根据可靠性设置优先级
fetcher.set_source_priority({
    'akshare': 1,      # 最高优先级
    'sina_finance': 2,
    'eastmoney': 3,
    'yfinance': 4      # 最低优先级
})
```

### 2. 定期数据源测试
```python
# 定期测试数据源可用性
test_results = fetcher.test_all_sources()
for source, result in test_results.items():
    if not result['success']:
        print(f"警告: 数据源 {source} 测试失败: {result['error']}")
```

### 3. 数据验证
```python
# 获取数据后验证
data = fetcher.get_stock_data('000001', '平安银行')

# 基本验证
if not data or 'price' not in data:
    print("数据获取失败或数据不完整")
    
# 合理性验证
if data['price'] <= 0:
    print(f"价格数据不合理: {data['price']}")
```

## 故障排除

### 常见问题
1. **所有数据源都失败**
   - 检查网络连接
   - 验证API密钥（如果需要）
   - 查看数据源状态

2. **数据不一致**
   - 启用数据一致性检查
   - 增加数据源数量
   - 手动指定数据源

3. **性能问题**
   - 启用缓存
   - 调整连接池大小
   - 减少API调用频率

## 更新日志

### v1.0.0 (2026-03-28)
- 初始版本发布
- 支持A股、美股多数据源
- 故障转移和缓存机制
- 数据一致性检查

## 维护说明
- 定期更新数据源配置
- 监控数据源可用性
- 根据市场变化调整数据源优先级

---

**开发者**: 量化小助理  
**最后更新**: 2026-03-28  
**适用场景**: 股票数据获取、市场数据监控、多源数据整合