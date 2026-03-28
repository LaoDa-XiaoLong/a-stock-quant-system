# 数据质量验证器 Skill

## 概述
数据质量验证器是一个通用的数据质量检查和验证工具，用于确保财务数据、股票数据等各类数据的合理性和可靠性。

## 功能特性
- ✅ **多维度验证**：完整性、合理性、一致性、极端值检查
- ✅ **多源比对**：支持多个数据源比对，计算共识值
- ✅ **可配置规则**：支持自定义验证规则和阈值
- ✅ **质量评分**：自动计算数据质量分数（0-100分）
- ✅ **详细报告**：生成详细的验证报告和警告信息

## 安装要求
```bash
pip install pandas numpy
```

## 快速开始

### 基本使用
```python
from data_quality_validator import DataQualityValidator

# 创建验证器
validator = DataQualityValidator()

# 验证财务数据
financial_data = {
    'revenue_yoy': 0.15,      # 营收同比增长15%
    'profit_yoy': 0.12,       # 利润同比增长12%
    'gross_margin': 0.25,     # 毛利率25%
    'net_margin': 0.08,       # 净利率8%
    'debt_ratio': 0.45        # 负债率45%
}

result = validator.validate_financial_data('000001', '平安银行', financial_data)
print(f"数据质量分数: {result['overall_score']:.1f}")
print(f"是否合理: {result['is_reasonable']}")
```

### 多源数据比对
```python
# 比对多个数据源
comparison = validator.compare_multiple_sources('002352', '顺丰控股')
print(f"推荐数据源: {comparison['recommended_source']}")
print(f"共识营收增长率: {comparison['consensus'].get('revenue_yoy', 0):.1%}")
```

## 配置说明

### 数据质量阈值
默认数据质量阈值为**75分**（根据老大要求），低于此分数的数据将被标记为不合理。

### 合理性检查规则
内置的合理性规则包括：
- **营收增长率**：-50% 到 +500%
- **利润增长率**：-100% 到 +1000%
- **毛利率**：0% 到 80%
- **净利率**：-20% 到 50%
- **负债率**：0% 到 100%

### 自定义规则
```python
# 可以扩展或修改规则
validator.reasonability_rules['custom_metric'] = {
    'min': -0.3,
    'max': 2.0,
    'typical_min': -0.1,
    'typical_max': 1.0,
    'warning_threshold': 1.5
}
```

## 使用场景

### 1. 财报数据验证
```python
# 验证财报数据，防止夸张数据
financial_data = get_financial_report(stock_code)
validation = validator.validate_financial_data(stock_code, stock_name, financial_data)

if validation['is_reasonable']:
    # 数据质量合格，继续处理
    process_data(financial_data)
else:
    # 数据质量不合格，记录并跳过
    log_data_quality_issue(validation)
```

### 2. 多源数据整合
```python
# 从多个数据源获取数据，选择最佳数据
sources = {
    'akshare': get_data_from_akshare(stock_code),
    'eastmoney': get_data_from_eastmoney(stock_code),
    'sina': get_data_from_sina(stock_code)
}

comparison = validator.compare_multiple_sources(stock_code, stock_name)
best_source = comparison['recommended_source']
best_data = sources[best_source]
```

### 3. 数据质量监控
```python
# 批量验证数据质量
quality_scores = []
for stock in stock_list:
    data = get_stock_data(stock['code'])
    validation = validator.validate_financial_data(stock['code'], stock['name'], data)
    quality_scores.append(validation['overall_score'])

avg_quality = sum(quality_scores) / len(quality_scores)
print(f"平均数据质量分数: {avg_quality:.1f}")
```

## 输出格式

### 验证结果结构
```python
{
    'stock_code': '000001',
    'stock_name': '平安银行',
    'validation_time': '2026-03-28T17:53:28',
    'overall_score': 88.5,
    'is_reasonable': True,
    'warnings': ['毛利率超出典型范围'],
    'errors': [],
    'details': {
        'completeness': {'score': 100, 'missing_required': []},
        'reasonability': {'score': 85, 'warnings': [...]},
        'consistency': 90,
        'extreme_values': {'penalty': 0}
    }
}
```

### 比对结果结构
```python
{
    'stock_code': '002352',
    'stock_name': '顺丰控股',
    'comparison_time': '2026-03-28T17:53:28',
    'sources': {
        'akshare': {'revenue_yoy': 0.15, 'profit_yoy': 0.12, ...},
        'eastmoney': {'revenue_yoy': 0.18, 'profit_yoy': 0.10, ...}
    },
    'consensus': {'revenue_yoy': 0.165, 'profit_yoy': 0.11, ...},
    'discrepancies': [...],
    'recommended_source': 'eastmoney'
}
```

## 最佳实践

### 1. 阈值设置建议
- **生产环境**：75分阈值（确保数据可靠性）
- **测试环境**：60分阈值（允许更多数据通过）
- **开发环境**：50分阈值（快速测试）

### 2. 错误处理
```python
try:
    validation = validator.validate_financial_data(stock_code, stock_name, data)
except Exception as e:
    logger.error(f"数据验证失败: {e}")
    # 降级处理：使用基础验证或跳过
```

### 3. 性能优化
- 启用数据缓存减少重复验证
- 批量验证时使用多线程
- 定期清理旧的验证日志

## 集成示例

### 集成到财报监控系统
```python
class FinancialMonitor:
    def __init__(self):
        self.validator = DataQualityValidator()
    
    def analyze_stock(self, stock_code, stock_name):
        # 获取数据
        financial_data = self.get_financial_data(stock_code)
        
        # 验证数据质量
        validation = self.validator.validate_financial_data(stock_code, stock_name, financial_data)
        
        # 检查数据质量阈值
        if validation['overall_score'] < self.config['data_quality_threshold']:
            logger.warning(f"数据质量不合格: {validation['overall_score']:.1f}")
            return None
        
        # 继续分析...
        return self._process_valid_data(financial_data)
```

## 故障排除

### 常见问题
1. **验证分数过低**
   - 检查数据是否包含极端值
   - 确认数据格式是否正确
   - 查看详细警告信息

2. **多源比对差异大**
   - 检查数据源是否正常
   - 确认数据时间戳是否一致
   - 考虑增加数据源数量

3. **性能问题**
   - 启用缓存机制
   - 减少不必要的验证
   - 批量处理数据

## 更新日志

### v1.0.0 (2026-03-28)
- 初始版本发布
- 支持基本数据质量验证
- 支持多源数据比对
- 内置合理性检查规则

## 维护说明
- 定期更新合理性规则以适应市场变化
- 监控数据质量分数分布，调整阈值
- 收集用户反馈，优化验证逻辑

---

**开发者**: 量化小助理  
**最后更新**: 2026-03-28  
**适用场景**: 财务数据验证、股票数据分析、数据质量监控