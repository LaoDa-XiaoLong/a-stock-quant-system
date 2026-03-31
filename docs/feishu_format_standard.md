# 飞书消息格式规范

## 问题背景

在财报监控报告中，我们发现了以下格式问题：

1. **使用不兼容的HTML格式**：如 `<font color='green'>📈 +25.6%</font>`
2. **飞书支持有限**：飞书不完全支持HTML标签，可能导致显示异常
3. **颜色标记过多**：影响阅读体验和移动端显示

## 格式兼容性分析

### 飞书消息格式支持情况

| 格式类型 | 支持情况 | 建议 |
|---------|---------|------|
| HTML标签 | ❌ 不完全支持 | 避免使用 |
| Markdown | ✅ 部分支持 | 优先使用 |
| 表情符号 | ✅ 完全支持 | 推荐使用 |
| 卡片消息 | ✅ 完全支持 | 复杂格式使用 |

### 具体限制

1. **HTML标签**：
   - `<font>`、`<span>`、`<div>` 等标签可能无法正确解析
   - 颜色属性（color='green'）可能被忽略
   - 建议完全避免使用HTML标签

2. **Markdown支持**：
   - 支持：`**粗体**`、`*斜体*`、`~~删除线~~`
   - 支持：`[链接](url)`、`` `代码` ``
   - 不支持：复杂表格、数学公式
   - 建议：使用基本Markdown语法

3. **表情符号**：
   - 所有平台表情符号都支持
   - 可以替代颜色标记
   - 建议：使用表情符号表示状态和优先级

## 格式转换方案

### 1. 百分比格式化

**原HTML格式：**
```html
<font color='green'>📈 +25.6%</font>
<font color='red'>📉 -18.2%</font>
<font color='blue'>📊 ±5.3%</font>
```

**新飞书兼容格式：**
```
🟢📈 +25.6%    # 绿色圆形 + 上升箭头
🔴📉 -18.2%    # 红色圆形 + 下降箭头
🔵📊 ±5.3%     # 蓝色圆形 + 图表
```

### 2. 交易建议格式化

**原HTML格式：**
```html
<font color='green'>✅ 强烈推荐加仓</font>
<font color='green'>✅ 考虑加仓</font>
<font color='blue'>🔍 持有观察</font>
<font color='gray'>📋 维持现状</font>
<font color='orange'>⚠️ 关注风险</font>
<font color='red'>🚨 考虑减仓</font>
```

**新飞书兼容格式：**
```
🟢✅🎯 强烈推荐加仓
🟢✅ 考虑加仓
🔵🔍 持有观察
⚪📋 维持现状
🟡⚠️ 关注风险
🔴🚨 考虑减仓
```

### 3. 颜色到表情符号映射

| 颜色 | 表情符号 | 含义 |
|------|---------|------|
| 绿色 | 🟢 | 正面、成功、推荐 |
| 红色 | 🔴 | 负面、警告、危险 |
| 蓝色 | 🔵 | 中性、信息、观察 |
| 黄色 | 🟡 | 警告、注意、风险 |
| 白色 | ⚪ | 普通、默认、中性 |
| 橙色 | 🟡 | 使用黄色替代 |

### 4. 指标到表情符号映射

| 指标 | 表情符号 | 含义 |
|------|---------|------|
| 营收 | 📈 | 营收增长 |
| 利润 | 💰 | 利润相关 |
| 增长 | 📊 | 综合增长 |
| 警告 | ⚠️ | 需要关注 |
| 警报 | 🚨 | 紧急情况 |
| 成功 | ✅ | 操作成功 |
| 失败 | ❌ | 操作失败 |
| 观察 | 🔍 | 需要观察 |
| 目标 | 🎯 | 重点关注 |
| 持有 | 📋 | 维持现状 |

## 代码实现

### 格式转换器类

```python
class FeishuFormatter:
    """飞书消息格式转换器"""
    
    COLOR_TO_EMOJI = {
        'green': '🟢',
        'red': '🔴',
        'blue': '🔵',
        'orange': '🟡',
        'gray': '⚪',
    }
    
    @staticmethod
    def convert_html_to_feishu(html_text: str) -> str:
        """将HTML格式转换为飞书兼容格式"""
        # 转换逻辑...
    
    @staticmethod
    def format_percentage(value: float) -> str:
        """格式化百分比"""
        if value >= 0.20:
            return f"🟢📈 +{value*100:.1f}%"
        elif value <= -0.20:
            return f"🔴📉 {value*100:.1f}%"
        else:
            return f"🔵📊 {value*100:+.1f}%"
    
    @staticmethod
    def get_trading_advice(surprise_ratio: float) -> str:
        """生成交易建议"""
        if surprise_ratio >= 0.30:
            return "🟢✅🎯 强烈推荐加仓"
        elif surprise_ratio >= 0.20:
            return "🟢✅ 考虑加仓"
        # ... 其他条件
```

### 使用示例

```python
# 旧代码（有问题）
html_text = "<font color='green'>📈 +25.6%</font>"
advice = "<font color='green'>✅ 考虑加仓</font>"

# 新代码（兼容飞书）
formatter = FeishuFormatter()
feishu_text = formatter.convert_html_to_feishu(html_text)
# 结果: "🟢📈 +25.6%"

feishu_advice = formatter.get_trading_advice(0.25)
# 结果: "🟢✅ 考虑加仓"
```

## 报告结构规范

### 1. 核心摘要格式

```
📈 A股财报监控日报 (2026-03-31)
========================================
🎯 核心摘要
• 监控范围: 307只股票
• 超预期: 🟢45只(14.7%)
• 持仓表现: 🟢3/7只(42.9%)
• 数据质量: 89.5分

🚨 高优先级关注
1. 🎯比亚迪: 营收🟢📈 +24.3%
2. 🎯药明康德: 营收🟢📈 +22.4%
3. 贵州茅台: 利润🔴📉 -18.2%

💡 总体建议: 持仓股票表现分化，需区别对待
```

### 2. 详细分析格式

```
## 📊 A股财报监控详细分析 (2026-03-31)

### 🎯 持仓股票分析
**持仓总数**: 7只
**超预期持仓**: 3只

#### 比亚迪 (002594)
**报告类型**: 年报
**发布日期**: 2026-03-27 (4天前)
**营收**: 🟢📈 +24.3% vs 预期
**净利润**: 🔴📉 -21.9% vs 预期
**数据质量**: 🟢 95.0分
**建议**: 🟢✅ 考虑加仓
```

### 3. 卡片消息格式

对于复杂报告，建议使用卡片格式：

```json
{
  "msg_type": "interactive",
  "card": {
    "config": {
      "wide_screen_mode": true
    },
    "header": {
      "title": {
        "tag": "plain_text",
        "content": "📊 A股财报监控日报"
      },
      "template": "blue"
    },
    "elements": [
      {
        "tag": "div",
        "text": {
          "tag": "lark_md",
          "content": "**使用lark_md标签支持Markdown**\n\n📈 **关键指标**\n• 监控股票: 307只\n• 超预期: 🟢45只(14.7%)"
        }
      }
    ]
  }
}
```

## 最佳实践

### 1. 格式选择优先级

1. **首选**: 卡片消息 + `lark_md` 标签
2. **次选**: 纯文本 + 表情符号
3. **避免**: HTML标签

### 2. 消息长度控制

- 核心摘要: 不超过500字符
- 详细分析: 不超过2000字符
- 卡片消息: 不超过3000字符

### 3. 发送策略

```python
def send_report_safely():
    """安全发送报告"""
    try:
        # 1. 尝试卡片格式
        success = send_as_card()
        if success:
            return True
        
        # 2. 卡片失败时降级到文本格式
        success = send_as_text()
        if success:
            return True
        
        # 3. 文本失败时发送极简摘要
        return send_as_minimal()
        
    except Exception as e:
        log_error(e)
        return False
```

### 4. 测试验证

每次格式更新后，应运行测试：

```python
# 格式兼容性测试
python scripts/test_feishu_format.py

# 格式转换测试
python scripts/feishu_formatter.py
```

## 迁移计划

### 阶段1：立即修复（1天）
1. 创建格式转换器类
2. 修复主要报告脚本
3. 测试基本功能

### 阶段2：全面迁移（3天）
1. 更新所有报告生成脚本
2. 更新数据库存储格式
3. 更新历史数据转换

### 阶段3：优化完善（7天）
1. 添加格式验证
2. 优化移动端显示
3. 建立格式监控

## 监控指标

### 格式兼容性指标
- 消息发送成功率: >99%
- 格式转换准确率: >95%
- 用户反馈满意度: >4/5分

### 性能指标
- 格式转换时间: <100ms
- 消息发送时间: <5s
- 系统资源占用: <50MB

## 附录

### 常用表情符号速查

```
📈 上升趋势    📉 下降趋势    📊 图表数据
💰 利润相关    ⚠️  警告信息    🚨 紧急警报
✅ 成功标记    ❌ 失败标记    🔍 观察标记
🎯 目标标记    📋 持有标记    💡 建议标记

🟢 绿色圆形    🔴 红色圆形    🔵 蓝色圆形
🟡 黄色圆形    ⚪ 白色圆形    🟣 紫色圆形
```

### 飞书官方文档链接
- [Markdown组件文档](https://open.feishu.cn/document/common-capabilities/message-card/message-cards-content/using-markdown-tags)
- [卡片消息文档](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/im-v1/message/create)
- [消息格式限制](https://open.feishu.cn/document/ukTMukTMukTM/uUzNwUjL1cDM14SN3ATN)

---

**最后更新**: 2026-03-31  
**负责人**: 量化小助理  
**状态**: 正式发布