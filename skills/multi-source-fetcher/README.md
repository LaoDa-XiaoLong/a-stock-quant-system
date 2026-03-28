# 多源数据获取器

## 简介
通用的数据源管理和获取框架，支持从多个数据源获取股票数据，提供故障转移、缓存和一致性检查功能。

## 快速开始

### 安装
```bash
pip install -r requirements.txt
```

### 基本使用
```python
from multi_source_fetcher import MultiSourceFetcher

# 创建获取器
fetcher = MultiSourceFetcher()

# 获取股票数据
stock_data = fetcher.get_stock_data('000001', '平安银行')
print(f"最新价格: {stock_data.get('price', 0)}")
print(f"数据来源: {stock_data.get('source', 'unknown')}")
```

## 功能特性
- ✅ 多数据源支持（A股、美股、港股）
- ✅ 智能故障转移
- ✅ 数据缓存机制
- ✅ 一致性检查
- ✅ 可扩展架构

## 内置数据源
1. **A股数据源**
   - akshare（推荐）
   - 新浪财经实时数据
   - 模拟数据源（测试用）

2. **美股数据源**
   - Yahoo Finance
   - 模拟数据源（测试用）

## 使用示例
运行示例代码：
```bash
python complete_fetcher.py
```

## 高级功能

### 多源数据比对
```python
# 比较多个数据源
comparison = fetcher.compare_sources('000001', '平安银行')
print(f"推荐数据源: {comparison['recommended_source']}")
print(f"价格共识: {comparison['consensus'].get('price', 0):.2f}")
```

### 缓存配置
```python
# 配置缓存
fetcher.configure_cache(
    enabled=True,
    cache_dir='./data/cache',
    ttl_config={'realtime': 300, 'daily': 3600}
)
```

### 批量获取
```python
# 批量获取多个股票
symbols = ['000001', '000002', '002352']
batch_data = fetcher.batch_get_stock_data(symbols)
```

## 集成到项目
```python
class TradingSystem:
    def __init__(self):
        self.fetcher = MultiSourceFetcher()
        self.fetcher.configure_cache(enabled=True)
    
    def get_market_data(self, symbol, name):
        """获取市场数据，包含故障转移"""
        try:
            data = self.fetcher.get_stock_data(symbol, name)
            if data:
                return data
        except Exception as e:
            logger.error(f"获取数据失败: {e}")
        
        # 返回缓存数据或默认值
        return self._get_fallback_data(symbol)
```

## 配置说明
- 默认启用缓存，减少API调用
- 支持自定义数据源优先级
- 可配置重试策略和超时时间

## 许可证
MIT License