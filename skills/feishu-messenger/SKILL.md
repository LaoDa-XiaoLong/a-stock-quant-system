# 飞书消息推送器 Skill

## 概述
飞书消息推送器是一个通用的飞书机器人消息推送工具，支持文本、富文本、卡片等多种消息格式，提供错误处理和重试机制。

## 功能特性
- ✅ **多种消息格式**：文本、富文本、卡片、图片等
- ✅ **错误处理和重试**：自动重试失败的消息
- ✅ **消息队列**：支持异步发送和批量发送
- ✅ **模板支持**：支持消息模板和变量替换
- ✅ **发送统计**：记录发送成功率和响应时间

## 安装要求
```bash
pip install requests
```

## 快速开始

### 基本使用
```python
from feishu_messenger import FeishuMessenger

# 创建消息推送器
messenger = FeishuMessenger(webhook_url="你的飞书webhook地址")

# 发送文本消息
result = messenger.send_text("这是一条测试消息")
print(f"发送结果: {result['success']}, 状态码: {result['status_code']}")

# 发送富文本消息
rich_result = messenger.send_rich_text(
    title="重要通知",
    content="**加粗文本** *斜体文本* [链接](https://example.com)",
    at_all=True
)
```

### 消息模板
```python
# 定义消息模板
template = """
# {{title}}
**时间**: {{time}}
**内容**: {{content}}

{% if urgent %}
⚠️ **紧急通知**
{% endif %}
"""

# 使用模板发送消息
data = {
    'title': '系统报警',
    'time': '2026-03-28 18:30:00',
    'content': '服务器CPU使用率超过90%',
    'urgent': True
}

result = messenger.send_template(template, data)
```

## 消息格式

### 1. 文本消息
```python
# 简单文本
messenger.send_text("Hello, World!")

# 带@提醒
messenger.send_text("请处理工单 @张三", at_users=["ou_123456"])

# @所有人
messenger.send_text("紧急会议通知", at_all=True)
```

### 2. 富文本消息
```python
# 富文本格式
messenger.send_rich_text(
    title="财报分析报告",
    content="""
## 今日财报监控结果

### 📊 统计摘要
- 分析股票: 12只
- 超预期股票: 7只
- 持仓超预期: 5只

### 🎯 重点关注
1. **000001 平安银行**: 营收超预期15%
2. **002352 顺丰控股**: 利润超预期20%

[查看详细报告](https://example.com/report)
""",
    at_all=False
)
```

### 3. 卡片消息
```python
# 交互式卡片
card_config = {
    "header": {
        "title": {
            "tag": "plain_text",
            "content": "交易建议"
        }
    },
    "elements": [
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "**000001 平安银行**\n建议: 买入\n理由: 财报超预期"
            }
        },
        {
            "tag": "action",
            "actions": [
                {
                    "tag": "button",
                    "text": {
                        "tag": "plain_text",
                        "content": "查看详情"
                    },
                    "type": "primary",
                    "url": "https://example.com/stock/000001"
                }
            ]
        }
    ]
}

messenger.send_card(card_config)
```

## 高级功能

### 消息队列
```python
# 启用消息队列
messenger.enable_queue(max_size=100, flush_interval=10)

# 添加消息到队列
messenger.queue_text("消息1")
messenger.queue_text("消息2")
messenger.queue_text("消息3")

# 手动刷新队列
messenger.flush_queue()

# 自动刷新（后台线程）
```

### 错误处理
```python
# 配置重试策略
messenger.configure_retry(
    max_retries=3,
    retry_delay=1.0,
    exponential_backoff=True
)

# 发送消息（自动重试）
try:
    result = messenger.send_text("重要消息")
    if not result['success']:
        print(f"发送失败: {result['error']}")
except MessageSendError as e:
    print(f"消息发送异常: {e}")
    
    # 保存到失败队列
    messenger.save_failed_message(e.message, e.error)
```

### 发送统计
```python
# 获取发送统计
stats = messenger.get_send_stats()
print(f"总发送数: {stats['total_sent']}")
print(f"成功数: {stats['success_count']}")
print(f"失败数: {stats['failure_count']}")
print(f"成功率: {stats['success_rate']:.1%}")
print(f"平均响应时间: {stats['avg_response_time']:.2f}秒")

# 重置统计
messenger.reset_stats()
```

## 使用场景

### 1. 系统监控报警
```python
class SystemMonitor:
    def __init__(self):
        self.messenger = FeishuMessenger(webhook_url="监控webhook")
    
    def send_alert(self, level, message, details=None):
        """发送系统报警"""
        if level == 'critical':
            title = "🚨 严重报警"
            at_all = True
        elif level == 'warning':
            title = "⚠️ 警告"
            at_all = False
        else:
            title = "ℹ️ 通知"
            at_all = False
        
        content = f"**{title}**\n\n{message}"
        if details:
            content += f"\n\n详情:\n```\n{details}\n```"
        
        return self.messenger.send_rich_text(title, content, at_all=at_all)
```

### 2. 日报自动推送
```python
class DailyReportSender:
    def __init__(self):
        self.messenger = FeishuMessenger(webhook_url="日报webhook")
        self.template = """
# {{date}} 工作日报

## 📊 今日完成
{{completed_tasks}}

## 🚀 进行中
{{in_progress_tasks}}

## 📋 明日计划
{{tomorrow_plan}}

## ⚠️ 问题与风险
{{issues}}
"""
    
    def send_daily_report(self, report_data):
        """发送日报"""
        return self.messenger.send_template(self.template, report_data)
```

### 3. 交易信号通知
```python
class TradingNotifier:
    def __init__(self):
        self.messenger = FeishuMessenger(webhook_url="交易webhook")
    
    def notify_trading_signal(self, signal):
        """通知交易信号"""
        color = "green" if signal['action'] == 'BUY' else "red"
        
        card = {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"{signal['action']} 信号 - {signal['symbol']}"
                },
                "template": color
            },
            "elements": [
                {
                    "tag": "div",
                    "fields": [
                        {"is_short": True, "text": {"tag": "lark_md", "content": f"**股票**\n{signal['symbol']}"}},
                        {"is_short": True, "text": {"tag": "lark_md", "content": f"**价格**\n{signal['price']:.2f}"}}
                    ]
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**理由**\n{signal['reason']}"
                    }
                }
            ]
        }
        
        return self.messenger.send_card(card)
```

## 配置说明

### Webhook配置
```python
# 单个webhook
messenger = FeishuMessenger(webhook_url="https://open.feishu.cn/open-apis/bot/v2/hook/xxx")

# 多个webhook（负载均衡）
messenger = FeishuMessenger(webhook_urls=[
    "https://open.feishu.cn/open-apis/bot/v2/hook/xxx1",
    "https://open.feishu.cn/open-apis/bot/v2/hook/xxx2"
])

# 不同消息类型使用不同webhook
messenger.configure_webhooks({
    'alert': 'https://.../alert',
    'report': 'https://.../report',
    'notification': 'https://.../notification'
})
```

### 消息限制
```python
# 配置消息限制
messenger.configure_limits(
    max_message_length=20000,      # 最大消息长度
    max_daily_messages=1000,       # 每日最大消息数
    rate_limit_per_minute=20       # 每分钟速率限制
)

# 检查限制
if messenger.check_limit('daily'):
    print("已达到每日消息限制")
```

## 最佳实践

### 1. 错误处理最佳实践
```python
def send_message_safely(messenger, message, retry_on_failure=True):
    """安全发送消息"""
    try:
        result = messenger.send_text(message)
        
        if not result['success']:
            logger.error(f"消息发送失败: {result['error']}")
            
            if retry_on_failure:
                # 延迟后重试
                time.sleep(2)
                result = messenger.send_text(message)
            
            return result
        
        return result
        
    except Exception as e:
        logger.error(f"消息发送异常: {e}")
        
        # 保存到本地文件，后续重试
        save_message_for_retry(message, str(e))
        
        return {'success': False, 'error': str(e)}
```

### 2. 性能优化
```python
# 启用消息队列减少API调用
messenger.enable_queue(max_size=50, flush_interval=30)

# 批量发送
messages = ["消息1", "消息2", "消息3"]
for msg in messages:
    messenger.queue_text(msg)

# 定时刷新
import threading
def auto_flush():
    while True:
        time.sleep(30)
        messenger.flush_queue()

thread = threading.Thread(target=auto_flush, daemon=True)
thread.start()
```

### 3. 监控和报警
```python
# 监控消息发送状态
def monitor_messenger(messenger):
    stats = messenger.get_send_stats()
    
    # 检查成功率
    if stats['success_rate'] < 0.95:
        send_alert(f"飞书消息发送成功率下降: {stats['success_rate']:.1%}")
    
    # 检查响应时间
    if stats['avg_response_time'] > 5.0:
        send_alert(f"飞书API响应时间过长: {stats['avg_response_time']:.1f}秒")
    
    # 检查失败队列
    failed_count = messenger.get_failed_count()
    if failed_count > 10:
        send_alert(f"失败消息队列积压: {failed_count}条")
```

## 故障排除

### 常见问题
1. **Webhook无效**
   - 检查webhook地址是否正确
   - 验证机器人是否有发送权限
   - 检查网络连接

2. **消息发送失败**
   - 检查消息内容是否包含敏感词
   - 验证消息格式是否正确
   - 查看飞书机器人配置

3. **速率限制**
   - 减少消息发送频率
   - 启用消息队列
   - 使用多个webhook负载均衡

### 调试模式
```python
# 启用调试模式
messenger.enable_debug(True)

# 查看详细日志
messenger.set_log_level('DEBUG')

# 测试连接
test_result = messenger.test_connection()
print(f"连接测试: {'成功' if test_result else '失败'}")
```

## 更新日志

### v1.0.0 (2026-03-28)
- 初始版本发布
- 支持文本、富文本、卡片消息
- 消息队列和错误重试
- 发送统计和监控

## 维护说明
- 定期检查webhook有效性
- 监控消息发送成功率
- 根据飞书API更新调整消息格式

---

**开发者**: 量化小助理  
**最后更新**: 2026-03-28  
**适用场景**: 系统报警、日报推送、交易通知、团队协作