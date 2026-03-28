# 飞书消息推送器

## 简介
通用的飞书机器人消息推送工具，支持文本、富文本、卡片等多种消息格式，提供错误处理和重试机制。

## 快速开始

### 安装
```bash
pip install -r requirements.txt
```

### 基本使用
```python
from feishu_messenger import FeishuMessenger

# 创建消息推送器（需要配置webhook地址）
messenger = FeishuMessenger("你的飞书webhook地址")

# 发送文本消息
result = messenger.send_text("这是一条测试消息")
print(f"发送结果: {result['success']}")
```

## 功能特性
- ✅ 多种消息格式（文本、富文本、卡片）
- ✅ 错误处理和自动重试
- ✅ 消息队列支持
- ✅ 模板消息
- ✅ 发送统计和监控

## 消息格式

### 1. 文本消息
```python
messenger.send_text("Hello, World!", at_all=True)
```

### 2. 富文本消息
```python
messenger.send_rich_text(
    title="重要通知",
    content="**加粗文本** *斜体文本*",
    at_all=False
)
```

### 3. 卡片消息
```python
card_config = {
    "header": {"title": {"tag": "plain_text", "content": "通知"}},
    "elements": [{"tag": "div", "text": {"tag": "lark_md", "content": "内容"}}]
}
messenger.send_card(card_config)
```

## 使用示例
运行示例代码：
```bash
python example_usage.py
```

## 高级功能

### 消息队列
```python
# 启用消息队列
messenger.enable_queue(max_size=100, flush_interval=10)

# 添加消息到队列
messenger.queue_text("消息1")
messenger.queue_text("消息2")

# 手动刷新队列
messenger.flush_queue()
```

### 模板消息
```python
template = """
# {{title}}
**时间**: {{time}}
**内容**: {{content}}
"""

data = {
    'title': '系统通知',
    'time': '2026-03-28 18:30:00',
    'content': '系统运行正常'
}

messenger.send_template(template, data, 'rich_text')
```

### 错误重试
```python
# 配置重试策略
messenger.configure_retry(
    max_retries=3,
    retry_delay=1.0,
    exponential_backoff=True
)
```

## 集成到项目

### 系统监控报警
```python
class SystemMonitor:
    def __init__(self):
        self.messenger = FeishuMessenger("监控webhook地址")
    
    def send_alert(self, level, message):
        if level == 'critical':
            self.messenger.send_text(f"🚨 严重报警: {message}", at_all=True)
        elif level == 'warning':
            self.messenger.send_text(f"⚠️ 警告: {message}")
```

### 日报自动推送
```python
class DailyReporter:
    def __init__(self):
        self.messenger = FeishuMessenger("日报webhook地址")
    
    def send_daily_report(self, report_data):
        content = f"# 每日报告\n\n**时间**: {report_data['date']}\n**内容**: {report_data['content']}"
        self.messenger.send_rich_text("每日报告", content)
```

## 配置说明
- 支持多个webhook负载均衡
- 可配置消息长度限制
- 支持速率限制
- 详细的发送统计

## 注意事项
1. 需要有效的飞书webhook地址
2. 消息长度有限制（约20,000字符）
3. 避免频繁发送，可能触发速率限制
4. 重要消息建议启用重试机制

## 许可证
MIT License