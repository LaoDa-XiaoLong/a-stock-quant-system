# 数据质量验证器

## 简介
通用的数据质量验证工具，用于确保财务数据、股票数据等各类数据的合理性和可靠性。

## 快速开始

### 安装
```bash
pip install -r requirements.txt
```

### 基本使用
```python
from data_quality_validator import DataQualityValidator

# 创建验证器
validator = DataQualityValidator()

# 验证数据
data = {
    'revenue_yoy': 0.15,      # 营收同比增长15%
    'profit_yoy': 0.12,       # 利润同比增长12%
    'gross_margin': 0.25,     # 毛利率25%
    'net_margin': 0.08,       # 净利率8%
}

result = validator.validate_financial_data('000001', '平安银行', data)
print(f"数据质量分数: {result['overall_score']:.1f}")
print(f"是否合理: {result['is_reasonable']}")
```

## 功能特性
- ✅ 多维度验证（完整性、合理性、一致性、极端值）
- ✅ 多源数据比对
- ✅ 可配置的验证规则
- ✅ 详细的质量报告
- ✅ 75分质量阈值（可配置）

## 使用示例
运行示例代码：
```bash
python example_usage.py
```

## 集成到项目
```python
# 在数据获取后立即验证
financial_data = get_financial_data(stock_code)
validation = validator.validate_financial_data(stock_code, stock_name, financial_data)

if validation['is_reasonable']:
    # 数据质量合格，继续处理
    process_data(financial_data)
else:
    # 数据质量不合格，记录并跳过
    logger.warning(f"数据质量不合格: {validation['overall_score']:.1f}")
```

## 配置说明
默认数据质量阈值为75分，低于此分数的数据将被标记为不合理。

可以修改 `reasonability_rules` 来调整验证规则。

## 许可证
MIT License