
# 🔧 飞书token错误修复指南

## 问题描述
代码健康度检查任务执行失败，错误信息：
```
TypeError: Cannot destructure property 'tenant_access_token' of '(intermediate value)' as it is undefined.
```

## 问题原因
任务需要调用飞书API发送消息，但缺少有效的tenant_access_token配置。

## 临时解决方案（已实施）
✅ **暂时禁用该任务** - 避免重复错误

## 永久解决方案

### 方案1: 配置飞书token
1. 获取飞书tenant_access_token
2. 创建配置文件：`~/.openclaw/feishu_config.json`
3. 添加配置：
```json
{
  "feishu": {
    "tenant_access_token": "你的token",
    "app_id": "你的app_id",
    "app_secret": "你的app_secret"
  }
}
```

### 方案2: 修改任务逻辑
1. 修改代码健康度检查任务，不依赖飞书API
2. 改为本地日志记录或邮件通知
3. 重新启用任务

### 方案3: 使用其他通知方式
1. 配置邮件通知
2. 使用其他消息平台
3. 改为控制台输出

## 当前状态
- 任务已暂时禁用
- 不会影响其他任务执行
- 需要您配置飞书token后重新启用

## 配置步骤
1. 联系飞书管理员获取tenant_access_token
2. 创建配置文件
3. 重新启用任务：
```bash
openclaw cron enable 17da0ef4-47a1-47c2-b925-365131db70a7
```

## 验证方法
```bash
# 查看任务状态
openclaw cron list --all

# 手动测试任务
openclaw cron run 17da0ef4-47a1-47c2-b925-365131db70a7
```
