# Git配置和设置指南

## 1. 初始Git配置

### 设置用户信息
```bash
# 设置全局用户名和邮箱
git config --global user.name "你的名字"
git config --global user.email "你的邮箱@example.com"

# 查看配置
git config --list
```

### 设置默认编辑器
```bash
# 设置VSCode为默认编辑器
git config --global core.editor "code --wait"

# 设置Vim为默认编辑器
git config --global core.editor "vim"

# 设置nano为默认编辑器
git config --global core.editor "nano"
```

### 设置行尾处理
```bash
# Windows用户
git config --global core.autocrlf true

# Mac/Linux用户
git config --global core.autocrlf input

# 禁止自动转换
git config --global core.autocrlf false
```

## 2. SSH密钥配置（推荐）

### 生成SSH密钥
```bash
# 生成新的SSH密钥
ssh-keygen -t ed25519 -C "你的邮箱@example.com"

# 或者使用RSA
ssh-keygen -t rsa -b 4096 -C "你的邮箱@example.com"

# 查看公钥
cat ~/.ssh/id_ed25519.pub
```

### 添加到GitHub/GitLab
1. 复制公钥内容
2. 登录GitHub/GitLab
3. 进入 Settings → SSH and GPG keys
4. 点击 New SSH key
5. 粘贴公钥并保存

### 测试SSH连接
```bash
# GitHub
ssh -T git@github.com

# GitLab
ssh -T git@gitlab.com
```

## 3. 项目Git设置

### 初始化新项目
```bash
# 创建新目录并初始化Git
mkdir a-stock-quant-system
cd a-stock-quant-system
git init

# 添加远程仓库
git remote add origin git@github.com:用户名/a-stock-quant-system.git

# 或者使用HTTPS
git remote add origin https://github.com/用户名/a-stock-quant-system.git
```

### 克隆现有项目
```bash
# 使用SSH
git clone git@github.com:用户名/a-stock-quant-system.git

# 使用HTTPS
git clone https://github.com/用户名/a-stock-quant-system.git

# 克隆到指定目录
git clone git@github.com:用户名/a-stock-quant-system.git my-project
```

## 4. 分支策略

### 主分支
- `master`: 生产环境代码，只接受经过测试的代码
- `develop`: 开发分支，集成所有功能

### 支持分支
- `feature/*`: 新功能开发
- `release/*`: 版本发布准备
- `hotfix/*`: 紧急Bug修复
- `fix/*`: 普通Bug修复

### 创建分支
```bash
# 从develop创建功能分支
git checkout develop
git pull origin develop
git checkout -b feature/财报监控优化

# 从master创建修复分支
git checkout master
git pull origin master
git checkout -b fix/数据获取错误
```

## 5. 日常Git工作流

### 开发新功能
```bash
# 1. 更新本地develop分支
git checkout develop
git pull origin develop

# 2. 创建功能分支
git checkout -b feature/新功能名称

# 3. 开发代码并提交
git add .
git commit -m "feat(模块): 描述新功能"

# 4. 推送到远程
git push origin feature/新功能名称

# 5. 创建Pull Request
# 在GitHub/GitLab上创建PR，从feature分支合并到develop
```

### 修复Bug
```bash
# 1. 从master创建修复分支
git checkout master
git pull origin master
git checkout -b fix/问题描述

# 2. 修复并提交
git add .
git commit -m "fix(模块): 修复问题描述"

# 3. 推送到远程
git push origin fix/问题描述

# 4. 创建Pull Request
# 从fix分支合并到master和develop
```

## 6. 提交规范

### 提交信息模板
创建 `.gitmessage` 文件：
```
# <类型>(<范围>): <描述>

# 详细说明（可选）

# 关联Issue: #<issue-number>
```

启用模板：
```bash
git config commit.template .gitmessage
```

### 提交类型
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具

## 7. 高级Git操作

### 修改最后一次提交
```bash
# 修改提交信息
git commit --amend -m "新的提交信息"

# 添加文件到上次提交
git add 忘记的文件.py
git commit --amend --no-edit
```

### 合并多个提交
```bash
# 交互式变基（合并最近3次提交）
git rebase -i HEAD~3

# 在编辑器中，将pick改为squash或fixup
```

### 撤销更改
```bash
# 撤销工作区修改
git checkout -- 文件.py

# 撤销暂存区修改
git reset HEAD 文件.py

# 撤销提交（保留修改）
git reset --soft HEAD~1

# 撤销提交（丢弃修改）
git reset --hard HEAD~1
```

### 暂存修改
```bash
# 暂存当前修改
git stash

# 查看暂存列表
git stash list

# 恢复暂存
git stash pop

# 应用暂存但不删除
git stash apply

# 删除暂存
git stash drop
```

## 8. 标签管理

### 创建标签
```bash
# 创建轻量标签
git tag v1.0.0

# 创建附注标签
git tag -a v1.0.0 -m "版本1.0.0发布"

# 查看标签
git tag
git show v1.0.0
```

### 推送标签
```bash
# 推送单个标签
git push origin v1.0.0

# 推送所有标签
git push origin --tags
```

### 删除标签
```bash
# 删除本地标签
git tag -d v1.0.0

# 删除远程标签
git push origin --delete v1.0.0
```

## 9. 子模块管理

### 添加子模块
```bash
git submodule add https://github.com/用户名/子模块.git 路径/子模块
```

### 克隆包含子模块的项目
```bash
# 克隆并初始化子模块
git clone --recursive https://github.com/用户名/项目.git

# 或者克隆后初始化
git clone https://github.com/用户名/项目.git
cd 项目
git submodule update --init --recursive
```

### 更新子模块
```bash
# 更新所有子模块
git submodule update --remote --recursive

# 进入子模块目录更新
cd 路径/子模块
git pull origin master
```

## 10. Git钩子

### 创建pre-commit钩子
```bash
# 创建钩子文件
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# 运行代码检查
python -m pylint scripts/ --fail-under=8.0
if [ $? -ne 0 ]; then
    echo "代码检查失败，请修复问题后再提交"
    exit 1
fi
EOF

# 添加执行权限
chmod +x .git/hooks/pre-commit
```

### 使用pre-commit框架
```bash
# 安装pre-commit
pip install pre-commit

# 创建配置文件
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.3.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
EOF

# 安装钩子
pre-commit install
```

## 11. 问题排查

### 常见问题
```bash
# 1. 提交到错误分支
# 使用cherry-pick将提交移动到正确分支

# 2. 合并冲突
# 解决冲突后标记为已解决
git add 冲突文件.py
git commit

# 3. 忘记提交文件
git add 忘记的文件.py
git commit --amend --no-edit

# 4. 误删文件
git checkout -- 误删的文件.py
```

### 查看Git历史
```bash
# 查看提交历史
git log --oneline --graph --all

# 查看文件修改历史
git log -p 文件.py

# 查看谁修改了文件
git blame 文件.py
```

## 12. 性能优化

### 清理仓库
```bash
# 清理未跟踪文件
git clean -fd

# 压缩仓库
git gc --aggressive --prune=now

# 重新打包对象
git repack -a -d --depth=250 --window=250
```

### 大文件处理
```bash
# 使用Git LFS管理大文件
git lfs install
git lfs track "*.zip"
git lfs track "*.pdf"

# 查看大文件
git rev-list --objects --all | \
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
  sed -n 's/^blob //p' | \
  sort --numeric-sort --key=2 | \
  tail -10
```

## 13. 团队协作

### 代码审查流程
1. 创建功能分支并开发
2. 推送到远程仓库
3. 创建Pull Request
4. 团队成员审查代码
5. 根据反馈修改代码
6. 合并到目标分支

### 代码审查要点
- 功能实现是否正确
- 代码结构是否清晰
- 错误处理是否完善
- 性能考虑是否充分
- 安全性考虑是否充分

## 14. 备份和恢复

### 备份仓库
```bash
# 创建完整备份
git bundle create 备份文件.bundle --all

# 恢复备份
git clone 备份文件.bundle 恢复目录
```

### 镜像备份
```bash
# 创建镜像仓库
git clone --mirror https://github.com/用户名/项目.git
cd 项目.git
git remote set-url --push origin 备份地址
```

## 15. 最佳实践

### 开发实践
1. **小步提交**：每次提交只完成一个小的功能或修复
2. **频繁提交**：避免长时间不提交
3. **描述清晰**：提交信息要能清晰表达修改内容
4. **关联Issue**：重要修改都要关联Issue
5. **代码审查**：重要修改必须经过代码审查
6. **测试先行**：先写测试，再实现功能

### 分支管理
1. **保持分支简洁**：一个分支一个功能
2. **及时合并**：功能完成后及时合并
3. **定期清理**：删除已合并的分支
4. **保护主分支**：master分支只接受经过测试的代码

### 版本控制
1. **语义化版本**：使用语义化版本号
2. **标签发布**：每个版本都打标签
3. **发布说明**：每个版本都有发布说明
4. **回滚计划**：准备好回滚方案

通过规范的Git工作流，可以确保项目代码的质量和可维护性。