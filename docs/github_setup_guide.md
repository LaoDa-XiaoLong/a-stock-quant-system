# GitHub仓库配置指南

## 1. 创建GitHub仓库

### 步骤1: 登录GitHub
1. 访问 https://github.com
2. 登录你的GitHub账户
3. 如果没有账户，点击"Sign up"注册

### 步骤2: 创建新仓库
1. 点击右上角"+"图标，选择"New repository"
2. 填写仓库信息：
   - **Repository name**: `a-stock-quant-system`
   - **Description**: `A股量化交易系统 - 财报监控、股票池筛选、多因子分析`
   - **Visibility**: `Public` (推荐) 或 `Private`
   - **Initialize with README**: ❌ 不要勾选（我们已有README）
   - **Add .gitignore**: ❌ 不要勾选（我们已有.gitignore）
   - **Choose a license**: ❌ 不要选择（我们已有LICENSE）
3. 点击"Create repository"

### 步骤3: 获取远程仓库地址
创建成功后，你会看到以下信息：
```
Quick setup — if you've done this kind of thing before

Get started by creating a new file or uploading an existing file. We recommend every repository include a README, LICENSE, and .gitignore.

…or create a new repository on the command line
echo "# a-stock-quant-system" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin git@github.com:你的用户名/a-stock-quant-system.git
git push -u origin main

…or push an existing repository from the command line
git remote add origin git@github.com:你的用户名/a-stock-quant-system.git
git branch -M main
git push -u origin main

…or import code from another repository
You can initialize this repository with code from a Subversion, Mercurial, or TFS project.
```

**重要**: 复制SSH地址：`git@github.com:你的用户名/a-stock-quant-system.git`

## 2. 配置SSH密钥到GitHub

### 步骤1: 查看现有SSH密钥
```bash
# 查看SSH密钥
cat ~/.ssh/id_rsa.pub

# 如果没有密钥，生成新的
ssh-keygen -t rsa -b 4096 -C "你的邮箱@example.com"
```

### 步骤2: 复制公钥
```bash
# 复制公钥到剪贴板（Mac）
pbcopy < ~/.ssh/id_rsa.pub

# Linux
cat ~/.ssh/id_rsa.pub | xclip -selection clipboard

# 或者手动复制
cat ~/.ssh/id_rsa.pub
```

### 步骤3: 添加到GitHub
1. 登录GitHub
2. 点击右上角头像 → Settings
3. 左侧菜单选择"SSH and GPG keys"
4. 点击"New SSH key"
5. 填写信息：
   - **Title**: `MacBook Pro` (或其他描述)
   - **Key type**: `Authentication Key`
   - **Key**: 粘贴复制的公钥
6. 点击"Add SSH key"

### 步骤4: 测试SSH连接
```bash
ssh -T git@github.com
```
应该看到：
```
Hi 你的用户名! You've successfully authenticated, but GitHub does not provide shell access.
```

## 3. 连接本地仓库到GitHub

### 步骤1: 添加远程仓库
```bash
cd /Users/ago/.openclaw/workspace

# 添加远程仓库（使用你的SSH地址）
git remote add origin git@github.com:你的用户名/a-stock-quant-system.git

# 查看远程仓库
git remote -v
```

### 步骤2: 推送代码到GitHub
```bash
# 推送develop分支
git push -u origin develop

# 推送master分支
git checkout master
git push -u origin master

# 推送所有分支和标签
git push --all origin
git push --tags origin
```

### 步骤3: 设置默认分支
1. 在GitHub仓库页面
2. 点击"Settings" → "Branches"
3. 在"Default branch"部分，点击"Switch to another branch"
4. 选择`develop`作为默认分支
5. 点击"Update"

## 4. GitHub功能配置

### 4.1 分支保护规则
1. 进入仓库 → Settings → Branches
2. 点击"Add branch protection rule"
3. 配置规则：
   - **Branch name pattern**: `master`
   - **Protect matching branches**: ✅
   - **Require pull request reviews before merging**: ✅
   - **Required approving reviews**: 1
   - **Require status checks to pass before merging**: ✅
   - **Require branches to be up to date before merging**: ✅
   - **Include administrators**: ✅
   - **Restrict who can push to matching branches**: ✅

### 4.2 GitHub Actions配置
创建 `.github/workflows/ci.yml`:
```yaml
name: CI

on:
  push:
    branches: [ develop, master ]
  pull_request:
    branches: [ develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python -m pytest tests/ -v
    
    - name: Code quality check
      run: |
        python -m pylint scripts/ --fail-under=8.0
```

### 4.3 Issue模板
创建 `.github/ISSUE_TEMPLATE/bug_report.md`:
```markdown
---
name: Bug报告
about: 报告系统Bug
title: '[BUG] '
labels: bug
assignees: ''

---

**Bug描述**
清晰简洁地描述Bug是什么

**重现步骤**
1. 进入 '...'
2. 点击 '....'
3. 滚动到 '....'
4. 看到错误

**期望行为**
清晰简洁地描述你期望发生什么

**截图**
如果适用，添加截图帮助说明问题

**环境信息**
- 系统: [如: macOS 12.0]
- Python版本: [如: 3.8.6]
- 版本: [如: v1.0.0]

**附加信息**
添加关于问题的任何其他信息
```

### 4.4 Pull Request模板
创建 `.github/PULL_REQUEST_TEMPLATE.md`:
```markdown
## 描述
请描述这个PR做了什么

## 相关Issue
关联的Issue编号: #123

## 测试
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 手动测试通过

## 截图
如果适用，添加截图

## 检查清单
- [ ] 我的代码遵循项目的代码规范
- [ ] 我已经对自己的代码进行了自我审查
- [ ] 我已经添加了必要的测试
- [ ] 我已经更新了相关文档
- [ ] 我的修改没有引入新的警告
```

## 5. 团队协作设置

### 5.1 添加协作者
1. 进入仓库 → Settings → Collaborators
2. 点击"Add people"
3. 输入协作者的GitHub用户名或邮箱
4. 选择权限级别：
   - **Read**: 只能查看
   - **Triage**: 可以管理Issue和PR
   - **Write**: 可以推送代码
   - **Maintain**: 可以管理仓库设置
   - **Admin**: 完全控制

### 5.2 项目看板
1. 进入仓库 → Projects
2. 点击"New project"
3. 选择"Board"模板
4. 添加列：待办、进行中、代码审查、测试中、完成
5. 连接Issue和PR到看板

### 5.3 Wiki启用
1. 进入仓库 → Settings → Features
2. 启用"Wikis"
3. 点击"Wiki"标签开始编辑

## 6. 安全设置

### 6.1 安全扫描
1. 进入仓库 → Security → Code scanning
2. 点击"Set up code scanning"
3. 选择"Default"配置
4. 启用自动扫描

### 6.2 依赖检查
1. 进入仓库 → Security → Dependabot alerts
2. 启用"Dependabot alerts"
3. 配置自动更新

### 6.3 秘密扫描
1. 进入仓库 → Settings → Security & analysis
2. 启用"Secret scanning"
3. 配置自定义模式

## 7. 自动化部署

### 7.1 部署到服务器
创建 `.github/workflows/deploy.yml`:
```yaml
name: Deploy

on:
  push:
    branches: [ master ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to server
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd /opt/a-stock-quant-system
          git pull origin master
          pip install -r requirements.txt
          systemctl restart quant-monitor
```

### 7.2 环境变量配置
1. 进入仓库 → Settings → Secrets → Actions
2. 点击"New repository secret"
3. 添加必要的密钥：
   - `HOST`: 服务器地址
   - `USERNAME`: 服务器用户名
   - `SSH_KEY`: SSH私钥
   - `FEISHU_WEBHOOK`: 飞书Webhook地址

## 8. 监控和分析

### 8.1 流量分析
1. 进入仓库 → Insights → Traffic
2. 查看访问统计、引用来源、热门内容

### 8.2 贡献者统计
1. 进入仓库 → Insights → Contributors
2. 查看贡献者活动和提交统计

### 8.3 代码频率
1. 进入仓库 → Insights → Code frequency
2. 查看代码添加和删除趋势

## 9. 备份和恢复

### 9.1 定期备份
```bash
# 创建备份
git bundle create backup-$(date +%Y%m%d).bundle --all

# 恢复备份
git clone backup-20260328.bundle restored-repo
```

### 9.2 镜像备份
```bash
# 创建镜像
git clone --mirror git@github.com:用户名/a-stock-quant-system.git

# 推送到备份位置
cd a-stock-quant-system.git
git remote add backup git@backup-server:backup/a-stock-quant-system.git
git push backup --mirror
```

## 10. 故障排除

### 常见问题

#### Q1: SSH连接失败
```bash
# 检查SSH配置
ssh -vT git@github.com

# 重新生成密钥
ssh-keygen -t rsa -b 4096 -C "你的邮箱"
```

#### Q2: 推送被拒绝
```bash
# 拉取最新代码
git pull origin develop --rebase

# 强制推送（谨慎使用）
git push origin develop --force
```

#### Q3: 合并冲突
```bash
# 查看冲突文件
git status

# 解决冲突后
git add 冲突文件.py
git commit -m "fix: 解决合并冲突"
```

#### Q4: 忘记添加文件
```bash
# 添加到上次提交
git add 忘记的文件.py
git commit --amend --no-edit
```

## 11. 最佳实践

### 开发实践
1. **小步提交**: 每次提交只完成一个小的功能
2. **描述清晰**: 提交信息要能清晰表达修改内容
3. **关联Issue**: 重要修改都要关联Issue
4. **代码审查**: 所有PR都要经过代码审查
5. **测试先行**: 先写测试，再实现功能

### 分支管理
1. **保持分支简洁**: 一个分支一个功能
2. **及时合并**: 功能完成后及时合并
3. **定期清理**: 删除已合并的分支
4. **保护主分支**: master分支只接受经过测试的代码

### 版本控制
1. **语义化版本**: 使用语义化版本号
2. **标签发布**: 每个版本都打标签
3. **发布说明**: 每个版本都有发布说明
4. **回滚计划**: 准备好回滚方案

## 12. 联系支持

### GitHub支持
- **文档**: https://docs.github.com
- **社区**: https://github.community
- **状态**: https://www.githubstatus.com
- **安全**: https://github.com/security

### 本地支持
如果你遇到问题，可以通过以下方式联系：
1. 在当前聊天窗口@我
2. 在工作群发送问题
3. 创建GitHub Issue

通过完整的GitHub配置，项目将具备：
✅ 版本控制 ✅ 团队协作 ✅ 自动化测试  
✅ 持续集成 ✅ 安全扫描 ✅ 部署自动化