# 开发工作流规范

## 目标
解决频繁出现的文件编辑错误问题，建立可靠的开发工作流。

## 问题分析

### 频繁出现的错误
```
[tools] edit failed: Could not find the exact text in ...
```

### 根本原因
1. **文件内容不匹配**：edit要求精确匹配，容易失败
2. **并发操作冲突**：多个操作同时修改同一文件
3. **文件状态不确定**：无法保证操作间文件保持不变
4. **开发流程缺陷**：依赖多次edit而不是一次性write

## 解决方案

### 1. 使用可靠的文件编辑器

#### 核心原则
- **优先使用write**：创建新文件或完全重写
- **谨慎使用edit**：仅在必要时使用，且使用安全版本
- **自动备份**：所有操作前自动备份
- **验证机制**：操作后验证文件完整性

#### 可靠编辑器使用
```python
from scripts.reliable_file_editor import ReliableFileEditor

editor = ReliableFileEditor()

# 安全编辑（自动处理匹配问题）
success, message = editor.safe_edit(
    file_path="scripts/example.py",
    old_text="def old_function():",
    new_text="def new_function():",
    max_attempts=3
)

# 智能写入（推荐方式）
success, message = editor.smart_write(
    file_path="scripts/new_file.py",
    content="完整的文件内容",
    overwrite=True
)
```

### 2. 文件状态监控

#### 监控关键文件
```python
from scripts.file_state_monitor import FileStateMonitor

monitor = FileStateMonitor()

# 开始监控关键文件
monitor.start_monitoring([
    "scripts/final_financial_monitor.py",
    "strategies/stock_pool_filter.py",
    "scripts/a_share_data_pipeline.py"
])

# 安全执行操作
def my_operation():
    # 你的代码
    pass

success, result, error = monitor.safe_operation(
    file_path="scripts/example.py",
    operation="edit",
    callback=my_operation
)
```

### 3. 开发工作流规范

#### 工作流1：创建新文件
```
1. 使用editor.smart_write()创建完整文件
2. 一次性写入所有内容
3. 验证文件完整性
4. 记录创建日志
```

#### 工作流2：修改现有文件
```
1. 检查文件状态是否安全
2. 锁定文件（防止并发操作）
3. 读取完整文件内容
4. 在内存中修改
5. 使用editor.smart_write()写回
6. 解锁文件
7. 验证修改
```

#### 工作流3：复杂重构
```
1. 创建备份：editor._create_backup()
2. 分阶段修改，每阶段验证
3. 出现问题立即恢复备份
4. 记录所有修改步骤
```

### 4. 预防措施

#### 代码编辑规范
1. **避免频繁edit**：一次性完成复杂编辑
2. **使用完整匹配**：确保old_text完全匹配
3. **检查文件状态**：操作前确认文件未被修改
4. **启用监控**：对关键文件启用状态监控

#### 错误处理
1. **自动重试**：safe_edit自动重试3次
2. **备份恢复**：所有操作前自动备份
3. **状态验证**：操作后验证文件完整性
4. **错误日志**：详细记录所有错误

### 5. 工具集成

#### 集成到现有系统
```python
# 在现有系统中集成可靠编辑器
import sys
sys.path.append('scripts')

try:
    from reliable_file_editor import ReliableFileEditor
    EDITOR = ReliableFileEditor()
    USE_RELIABLE_EDITOR = True
except ImportError:
    USE_RELIABLE_EDITOR = False
    print("警告: 可靠编辑器不可用，使用标准编辑")

def safe_edit_file(file_path, old_text, new_text):
    if USE_RELIABLE_EDITOR:
        return EDITOR.safe_edit(file_path, old_text, new_text)
    else:
        # 回退到标准编辑（谨慎使用）
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            if old_text in content:
                new_content = content.replace(old_text, new_text)
                with open(file_path, 'w') as f:
                    f.write(new_content)
                return True, "编辑成功"
            else:
                return False, "文本不匹配"
        except Exception as e:
            return False, str(e)
```

### 6. 监控和报警

#### 监控配置
```yaml
监控文件:
  - scripts/*.py
  - strategies/*.py
  - skills/*/*.py

检查间隔: 1秒
锁定超时: 30秒
自动解锁: 是
日志级别: 详细
```

#### 报警规则
1. **文件锁定超时**：>30秒自动报警
2. **频繁编辑失败**：连续3次失败报警
3. **文件内容异常**：哈希值频繁变化报警
4. **并发操作冲突**：检测到冲突立即报警

### 7. 最佳实践

#### 开发实践
1. **小步提交**：频繁提交小改动，避免大范围edit
2. **版本控制**：使用Git管理所有修改
3. **代码审查**：重要修改前进行代码审查
4. **测试驱动**：修改前先写测试用例

#### 文件操作实践
1. **原子操作**：每个edit操作应该是原子的
2. **完整性检查**：操作前后检查文件完整性
3. **依赖管理**：明确文件间的依赖关系
4. **错误恢复**：设计完善的错误恢复机制

### 8. 故障排除

#### 常见问题解决

**问题1**: edit失败，文本不匹配
```
解决方案:
1. 使用editor.safe_edit()自动重试
2. 检查文件是否被其他进程修改
3. 使用完整文件路径，避免相对路径问题
4. 验证文本中的空格和换行符
```

**问题2**: 文件被锁定
```
解决方案:
1. 等待锁定超时（默认30秒）
2. 检查锁定进程是否异常
3. 手动解锁：monitor.unlock_file()
4. 重启监控服务
```

**问题3**: 并发操作冲突
```
解决方案:
1. 使用文件锁定机制
2. 实现操作队列
3. 增加操作间隔
4. 使用事务性文件操作
```

### 9. 性能优化

#### 监控优化
1. **选择性监控**：只监控关键文件
2. **调整间隔**：根据需求调整检查间隔
3. **内存优化**：定期清理状态缓存
4. **日志轮转**：自动清理旧日志

#### 编辑优化
1. **批量操作**：使用batch_edit减少IO
2. **内存操作**：在内存中完成复杂编辑
3. **缓存利用**：利用文件哈希缓存
4. **异步处理**：非关键操作异步执行

### 10. 实施计划

#### 第一阶段（立即实施）
1. ✅ 部署可靠文件编辑器
2. ✅ 部署文件状态监控器
3. ✅ 更新开发工作流文档
4. ✅ 培训团队成员

#### 第二阶段（一周内）
1. 集成到所有关键系统
2. 建立监控报警机制
3. 优化性能和稳定性
4. 收集使用反馈

#### 第三阶段（一个月内）
1. 自动化测试覆盖
2. 性能基准测试
3. 扩展监控范围
4. 持续优化改进

## 总结

通过实施可靠的文件编辑器、文件状态监控和规范的工作流，可以彻底解决频繁出现的edit失败问题。关键措施包括：

1. **预防为主**：通过监控和锁定防止问题发生
2. **自动恢复**：通过备份和重试自动处理问题
3. **规范流程**：通过工作流规范减少人为错误
4. **持续改进**：通过监控和反馈不断优化

这套方案不仅能解决当前的edit失败问题，还能提高整个开发流程的可靠性和效率。