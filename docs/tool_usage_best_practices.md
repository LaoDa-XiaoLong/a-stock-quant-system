# 工具使用最佳实践指南

## 1. edit工具使用规范

### 基本原则
- **精确匹配**: 确保oldText与文件中的内容完全一致（包括空格、换行、缩进）
- **唯一性**: 确保匹配文本在文件中是唯一的
- **安全性**: 编辑前先备份或确认文件内容

### 推荐流程
1. **读取确认**: 先使用read工具读取文件内容
2. **文本验证**: 确认要编辑的文本存在且唯一
3. **精确复制**: 从文件中复制确切的文本（包括格式）
4. **执行编辑**: 使用edit工具进行编辑
5. **验证结果**: 编辑后读取文件确认修改正确

### 常见问题及解决方案

#### 问题1: "Could not find the exact text"
**原因**: 文本不匹配（空格、换行、缩进不一致）
**解决**:
```python
# 错误示例 - 缩进不一致
oldText = "def my_function():"
# 正确示例 - 从文件中精确复制
oldText = "    def my_function():"
```

#### 问题2: "Found X occurrences of the text"
**原因**: 文本不唯一
**解决**:
```python
# 错误示例 - 文本太通用
oldText = "import pandas"
# 正确示例 - 添加更多上下文
oldText = "import pandas as pd\nimport numpy as np\n"
```

## 2. write工具使用规范

### 何时使用write替代edit
- 创建新文件时
- 完全重写文件内容时
- 编辑内容较多或复杂时
- edit工具多次失败时

### 推荐用法
```python
# 先读取现有内容（如果需要保留部分）
with open('file.py', 'r') as f:
    existing_content = f.read()

# 修改内容
new_content = existing_content.replace('old', 'new')

# 使用write工具
write('file.py', new_content)
```

## 3. 错误处理最佳实践

### 预防性检查
```python
# 编辑前检查文件是否存在
if not os.path.exists(filepath):
    print(f"文件不存在: {filepath}")
    return

# 编辑前检查文本是否唯一
content = read(filepath)
occurrences = content.count(oldText)
if occurrences != 1:
    print(f"警告: 文本出现{occurrences}次，可能不唯一")
```

### 优雅降级
```python
try:
    # 尝试使用edit工具
    edit(filepath, oldText, newText)
except EditError as e:
    print(f"edit失败: {e}")
    # 降级到write工具
    content = read(filepath)
    new_content = content.replace(oldText, newText)
    write(filepath, new_content)
```

## 4. 性能优化建议

### 批量操作
```python
# 避免频繁的小编辑
# 不好: 多次edit调用
edit(file1, old1, new1)
edit(file2, old2, new2)
edit(file3, old3, new3)

# 好: 批量处理
updates = [
    (file1, old1, new1),
    (file2, old2, new2),
    (file3, old3, new3)
]
for filepath, old_text, new_text in updates:
    edit(filepath, old_text, new_text)
```

### 缓存机制
```python
# 缓存文件内容，避免重复读取
file_cache = {}

def get_file_content(filepath):
    if filepath not in file_cache:
        file_cache[filepath] = read(filepath)
    return file_cache[filepath]
```

## 5. 调试技巧

### 详细日志
```python
import logging

logging.basicConfig(level=logging.DEBUG)

def safe_edit(filepath, oldText, newText):
    logging.debug(f"编辑文件: {filepath}")
    logging.debug(f"旧文本长度: {len(oldText)}")
    logging.debug(f"新文本长度: {len(newText)}")
    
    try:
        edit(filepath, oldText, newText)
        logging.info("编辑成功")
    except Exception as e:
        logging.error(f"编辑失败: {e}")
        raise
```

### 验证机制
```python
def verify_edit(filepath, expected_old, expected_new):
    """验证编辑结果"""
    content = read(filepath)
    
    if expected_old in content:
        print(f"❌ 旧文本仍然存在")
        return False
    
    if expected_new not in content:
        print(f"❌ 新文本未找到")
        return False
    
    print("✅ 编辑验证通过")
    return True
```

## 6. 工具选择决策树

```
是否需要编辑文件？
    ├── 是 → 文件是否存在？
    │       ├── 是 → 要编辑的内容是否唯一？
    │       │       ├── 是 → 使用edit工具
    │       │       └── 否 → 添加更多上下文或使用write工具
    │       └── 否 → 使用write工具创建文件
    └── 否 → 不需要工具操作
```

## 7. 紧急修复流程

### 当edit工具频繁失败时
1. **立即停止**: 停止当前的编辑操作
2. **分析原因**: 查看错误日志，确定问题类型
3. **临时方案**: 使用write工具作为临时解决方案
4. **根本解决**: 分析根本原因，更新编辑策略
5. **预防措施**: 更新最佳实践指南，防止再次发生

## 总结

工具使用质量直接影响项目效率和稳定性。遵循最佳实践可以：
- 减少错误和失败
- 提高开发效率
- 增强代码可维护性
- 降低调试成本

记住：**预防优于修复**，在工具使用前多花一分钟检查，可以节省后续数小时的调试时间。
