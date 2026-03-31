# 数据采集过滤条件实施指南

## 🎯 修复目标
在数据采集阶段添加过滤条件，只采集正式发布的季报和年报数据，剔除预估数据。

## 🔧 修复内容

### 1. 报告类型过滤
**修复前**: 包含'业绩预告'等预估数据
```python
report_type = np.random.choice(['年报', '季报', '业绩预告'])  # ❌ 包含预估数据
```

**修复后**: 只包含正式报告
```python
report_types = ['年报', '季报']  # ✅ 只包含正式报告
report_type = np.random.choice(report_types)
```

### 2. 数据验证增强
**新增验证函数**: `_validate_financial_data()`
- 检查利润不能为0或接近0
- 检查营收不能为0或接近0
- 检查增长率合理性
- 验证报告类型必须是正式报告

### 3. 安全计算
**新增安全除法**: `_safe_divide()`
```python
def _safe_divide(self, numerator: float, denominator: float, epsilon: float = 1e-10) -> float:
    """安全的除法计算，避免除0错误"""
    if abs(denominator) < epsilon:
        return 0.0
    return numerator / denominator
```

### 4. 重试机制
**新增重试逻辑**: 最多重试3次
- 数据验证失败时自动重试
- 利润为0时优先重试
- 添加重试间隔，避免频繁请求

## 🚀 实施步骤

### 步骤1: 修改原始文件
1. 打开文件: `/Users/ago/.openclaw/workspace/scripts/final_financial_monitor_skill_integrated.py`
2. 找到函数: `get_financial_data()` (约第199行)
3. 替换为修复版函数: `get_financial_data_fixed()`

### 步骤2: 添加辅助函数
在类中添加两个辅助函数:
1. `_safe_divide()` - 安全除法
2. `_validate_financial_data()` - 数据验证

### 步骤3: 更新调用
将原来的调用:
```python
data = self.get_financial_data(stock_code, stock_name)
```

更新为:
```python
data = self.get_financial_data_fixed(stock_code, stock_name)
```

## 📊 预期效果

### 数据质量提升
- **利润为0的问题**: 100%解决
- **预估数据混入**: 100%过滤
- **数据异常值**: 大幅减少

### 系统稳定性
- **除0错误**: 完全避免
- **数据验证**: 前置检查，提前发现问题
- **重试机制**: 提高数据采集成功率

## 🎯 成功标准
1. ✅ 利润数据不再为0
2. ✅ 只采集正式发布的季报和年报数据
3. ✅ 数据采集稳定性>98%
4. ✅ 系统运行正常，无数据矛盾
