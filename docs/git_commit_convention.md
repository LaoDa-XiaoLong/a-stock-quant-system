# Git提交规范

## 提交信息格式
```
类型(范围): 描述

详细说明（可选）

关联Issue: #123
```

## 类型说明

### 主要类型
| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(monitor): 添加财报超预期监控` |
| `fix` | Bug修复 | `fix(api): 修复数据获取超时问题` |
| `docs` | 文档更新 | `docs(readme): 更新安装说明` |
| `style` | 代码格式 | `style(scripts): 统一代码缩进` |
| `refactor` | 代码重构 | `refactor(validator): 重构数据验证逻辑` |
| `test` | 测试相关 | `test(filter): 添加股票池筛选测试` |
| `chore` | 构建过程或辅助工具 | `chore(deps): 更新依赖版本` |
| `perf` | 性能优化 | `perf(fetcher): 优化数据获取性能` |
| `ci` | CI/CD相关 | `ci(github): 添加自动化测试` |
| `revert` | 回退提交 | `revert: 回退错误的功能提交` |

### 范围说明
范围表示修改的模块或功能区域：
- `monitor`: 财报监控系统
- `filter`: 股票池筛选
- `api`: 数据接口
- `skill`: Skill模块
- `scripts`: 脚本文件
- `strategies`: 交易策略
- `config`: 配置文件
- `docs`: 文档
- `deps`: 依赖管理

## 描述规范

### 基本要求
1. **使用中文**：便于团队理解
2. **简明扼要**：不超过50个字符
3. **使用祈使句**：如"添加"、"修复"、"更新"
4. **首字母小写**：不要使用句号结尾

### 示例
- ✅ `feat(monitor): 添加持仓股票优先分析功能`
- ✅ `fix(api): 修复飞书消息推送失败问题`
- ❌ `feat: 我添加了一个新功能`
- ❌ `fix: 修复了一些bug`

## 详细说明（可选）
当提交需要更多解释时，可以在空行后添加详细说明：
- 说明修改的原因
- 描述实现的关键点
- 列出不兼容的变更
- 提供测试信息

### 示例
```
feat(filter): 添加科技地缘政治维度分析

- 新增第六维度：科技地缘政治面（权重15%）
- 重点分析算力、电力、半导体产业链
- 添加美股-A股联动分析
- 更新权重分配公式

关联Issue: #45
```

## 关联Issue
使用以下格式关联Issue：
- `关联Issue: #123`
- `Close #123`
- `Fix #123, #124`

## 分支命名规范

### 分支类型
| 分支类型 | 格式 | 示例 |
|----------|------|------|
| 功能分支 | `feature/简短描述` | `feature/财报监控` |
| 修复分支 | `fix/问题描述` | `fix/数据验证错误` |
| 发布分支 | `release/版本号` | `release/v1.0.0` |
| 热修复分支 | `hotfix/紧急问题` | `hotfix/飞书推送失败` |

### 分支命名要求
1. **使用英文小写**：便于命令行操作
2. **使用连字符分隔单词**：如 `feature/stock-pool-filter`
3. **简明描述**：清晰表达分支目的
4. **避免特殊字符**：不要使用空格、中文、标点符号

## 工作流程

### 1. 开发新功能
```bash
# 从develop分支创建功能分支
git checkout develop
git pull origin develop
git checkout -b feature/财报监控优化

# 开发完成后提交
git add .
git commit -m "feat(monitor): 优化超预期算法"

# 推送到远程
git push origin feature/财报监控优化

# 创建Pull Request合并到develop
```

### 2. 修复Bug
```bash
# 从master分支创建修复分支
git checkout master
git pull origin master
git checkout -b fix/数据获取超时

# 修复后提交
git add .
git commit -m "fix(api): 修复数据获取超时问题"

# 推送到远程
git push origin fix/数据获取超时

# 创建Pull Request合并到master
```

### 3. 发布版本
```bash
# 从develop分支创建发布分支
git checkout develop
git pull origin develop
git checkout -b release/v1.0.0

# 版本号更新、文档更新等
git add .
git commit -m "chore(release): 准备v1.0.0发布"

# 合并到master和develop
git checkout master
git merge --no-ff release/v1.0.0
git tag -a v1.0.0 -m "版本v1.0.0"

git checkout develop
git merge --no-ff release/v1.0.0

# 删除发布分支
git branch -d release/v1.0.0
```

## 提交检查清单

### 提交前检查
- [ ] 代码通过所有测试
- [ ] 代码符合编码规范
- [ ] 文档已更新
- [ ] 提交信息格式正确
- [ ] 没有调试代码和临时文件

### 代码审查要点
- [ ] 功能实现正确
- [ ] 代码结构清晰
- [ ] 错误处理完善
- [ ] 性能考虑充分
- [ ] 安全性考虑充分

## 工具支持

### 1. 提交信息模板
创建 `.gitmessage` 文件：
```
# <类型>(<范围>): <描述>

# 详细说明（可选）

# 关联Issue: #<issue-number>
```

配置Git使用模板：
```bash
git config commit.template .gitmessage
```

### 2. 提交钩子（pre-commit）
创建 `.pre-commit-config.yaml`：
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.3.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
      
  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
```

### 3. 提交信息验证
使用commitlint验证提交信息格式。

## 常见问题

### Q: 提交信息写错了怎么办？
A: 使用 `git commit --amend` 修改最后一次提交。

### Q: 多个小改动如何提交？
A: 使用 `git add -p` 交互式添加，分多次提交。

### Q: 如何合并多个提交？
A: 使用 `git rebase -i` 交互式变基。

### Q: 提交后发现有问题怎么办？
A: 创建新的修复提交，不要修改历史提交。

## 最佳实践

1. **小步提交**：每次提交只完成一个小的功能或修复
2. **频繁提交**：避免长时间不提交
3. **描述清晰**：提交信息要能清晰表达修改内容
4. **关联Issue**：重要修改都要关联Issue
5. **代码审查**：重要修改必须经过代码审查
6. **测试先行**：先写测试，再实现功能

## 示例项目结构
```
.git/
├── hooks/                    # Git钩子
├── config                    # Git配置
├── logs/                    # 操作日志
└── refs/                    # 引用
```

通过规范的Git工作流，可以确保项目代码的质量和可维护性。