# A股量化交易系统

## 项目概述
基于Python的A股量化交易系统，包含财报监控、股票池筛选、多因子分析、交易执行等功能。

## 项目状态
- **版本**: v2.0.0
- **状态**: 生产就绪
- **最后更新**: 2026-03-29
- **GitHub同步**: 每日00:10和12:10自动同步
- **AI模型**: DeepSeek-V3.2 + R1协同架构

## 核心功能

### 1. 财报监控系统
- 每日自动监控A股财报超预期情况
- 持仓股票优先分析
- 飞书自动推送日报
- 数据质量验证

### 2. 股票池筛选系统
- 多维度股票筛选（流动性、基本面、合规性）
- 规则引擎配置
- 实时数据更新
- 筛选报告生成

### 3. Skill模块体系
- **数据质量验证器**: 防止夸张数据，质量阈值75分
- **多源数据获取器**: 故障转移、缓存、一致性检查
- **飞书消息推送器**: 多种格式、错误重试、自动降级

### 4. 智能分析系统
- **V3.2+R1协同架构**: DeepSeek-V3.2实时查询 + R1深度分析
- **智能路由系统**: 7种任务类型自动选择最优模型
- **协同工作流**: V3.2数据采集 → R1深度分析 → 结构化报告
- **成本优化**: 相比全用R1节省40-60%成本

### 5. 量化策略体系
- **7个完整策略**: 主力资金、题材热度、尾盘买入、动量、反转、MACD趋势、选股策略
- **多策略并行框架**: 7个策略同时运行对比
- **具体点位输出**: 每个策略输出具体股票标的、入场点位、出场点位
- **动态优化系统**: 胜率-盈亏比平衡分析，目标70%胜率

### 6. 自动化管理系统
- **版本管理系统**: 核心功能版本化，一键回滚能力
- **GitHub自动同步**: 每日00:10和12:10自动提交和推送
- **调度任务系统**: 8个定时任务自动执行
- **错误隔离机制**: 问题任务不影响整体系统

## 项目结构

```
.
├── config/                    # 配置文件
│   ├── financial_monitor_config.json
│   └── example_config.json
├── data/                      # 数据目录
│   ├── final_financial/      # 财报数据
│   ├── quality_validation/   # 数据质量验证
│   └── stock_pool/          # 股票池数据
├── scripts/                  # 脚本目录
│   ├── final_financial_monitor.py      # 财报监控主程序
│   ├── stock_pool_filter_fixed.py      # 股票池筛选
│   ├── reliable_file_editor.py         # 可靠文件编辑器
│   ├── file_state_monitor.py           # 文件状态监控
│   ├── generate_daily_report.py        # 日报生成器
│   ├── multi_strategy_executor.py      # 多策略执行器
│   ├── auto_git_sync.py                # GitHub自动同步
│   ├── simple_version_manager.py       # 版本管理器
│   ├── pre_market_check.py             # 开盘前检查
│   └── setup_flybook_webhook.py        # 飞书Webhook配置
├── strategies/               # 交易策略
│   ├── simple_macd_strategy.py
│   ├── stock_pool_filter_complete.py
│   ├── capital_flow_strategy_v1.py      # 主力资金流向策略
│   ├── theme_hot_strategy_v1.py         # 题材热度识别策略
│   ├── momentum_strategy_v1.py          # 动量策略
│   ├── reversal_strategy_v1.py          # 反转策略
│   ├── strategy_weight_optimizer_v1.py  # 策略权重优化器
│   └── backtest_integration_v1.py       # 回测系统集成
├── intelligent_stock_analysis/ # V3.2+R1智能分析系统
│   ├── routing/               # 智能路由系统
│   ├── collectors/            # V3.2数据采集器
│   ├── analyzers/             # R1深度分析器
│   ├── workflows/             # 协同工作流引擎
│   ├── examples/              # 典型用例演示
│   ├── config/                # OpenClaw集成配置
│   └── run_demo.py            # 完整演示入口
├── version_management/        # 版本管理系统
│   ├── stock_models/          # 股票模型版本
│   ├── report_templates/      # 报告模板版本
│   └── version_registry.json  # 版本注册表
├── skills/                  # Skill模块
│   ├── data-quality-validator/
│   ├── multi-source-fetcher/
│   └── feishu-messenger/
├── docs/                    # 文档
│   ├── development_workflow.md
│   └── skill_integration_guide.md
├── templates/              # 模板文件
│   └── daily_work_report.md
├── reports/                # 报告输出
├── research/              # 研究报告
├── backups/               # 备份文件
└── logs/                  # 日志文件
```

## 技术栈

### 核心依赖
- **Python**: 3.8+
- **数据分析**: pandas, numpy
- **可视化**: matplotlib, seaborn
- **回测框架**: backtrader
- **数据源**: akshare, Alpha Vantage
- **消息推送**: 飞书开放平台API

### 开发工具
- **版本控制**: Git
- **代码质量**: pylint, black, mypy
- **测试框架**: pytest
- **文档**: Markdown, Sphinx

## 快速开始

### 1. 环境配置
```bash
# 克隆项目
git clone <repository-url>
cd a-stock-quant-system

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置文件
复制示例配置文件并修改：
```bash
cp config/example_config.json config/financial_monitor_config.json
# 编辑配置文件，添加API密钥等
```

### 3. 运行财报监控
```bash
python scripts/final_financial_monitor.py
```

### 4. 运行股票池筛选
```bash
python strategies/stock_pool_filter_fixed.py
```

## 开发指南

### 代码规范
- 遵循PEP 8编码规范
- 使用类型注解
- 函数和类必须有文档字符串
- 重要修改必须添加测试用例

### Git工作流
1. **主分支**: `master` - 稳定版本
2. **开发分支**: `develop` - 开发版本
3. **功能分支**: `feature/*` - 新功能开发
4. **修复分支**: `fix/*` - Bug修复

### 提交规范
```
类型(范围): 描述

详细说明（可选）

关联Issue: #123
```

**类型**:
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具

## 部署说明

### 定时任务系统
系统配置了8个自动调度任务：

#### 🕘 每日任务
1. **财报监控日报** (09:00) - V3深度优化版，发送到A股数据分析群
2. **股票数据自动更新** (09:30) - 获取最新A股数据
3. **系统健康检查** (10:00) - 监控系统状态，发送到工作沟通汇报群
4. **GitHub自动同步** (00:10, 12:10) - 每日两次自动代码同步
5. **代码健康度检查** (15:00) - 检查代码结构和性能指标

#### 📅 每周任务
6. **量化策略周报** (周五16:00) - 分析本周策略表现
7. **策略自动回测** (周五17:00) - 运行所有策略回测
8. **数据备份任务** (周六20:00) - 备份量化分析数据

### GitHub自动同步
- **同步时间**: 每日00:10和12:10（北京时间）
- **同步内容**: 自动检测代码变更并提交到GitHub
- **同步分支**: develop分支
- **配置脚本**: `scripts/auto_git_sync.py`

### 监控和日志
- 日志文件: `logs/` 目录
- 错误监控: 飞书消息推送
- 性能监控: 系统状态报告

## 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

- **项目维护者**: 量化小助理
- **问题反馈**: 通过GitHub Issues
- **文档**: [项目文档](docs/)

## 更新日志

### v2.0.0 (2026-03-29)
#### 🚀 核心架构升级
- **V3.2+R1智能分析系统**: DeepSeek-V3.2实时查询 + R1深度分析协同架构
- **智能路由系统**: 7种任务类型自动选择最优模型
- **协同工作流引擎**: V3.2数据采集 → R1深度分析完整流程

#### 📊 量化策略扩展
- **7个完整量化策略**: 主力资金、题材热度、尾盘买入、动量、反转、MACD趋势、选股策略
- **多策略并行框架**: 7个策略同时运行对比效果
- **具体点位输出**: 每个策略输出具体股票标的、入场点位、出场点位
- **动态优化系统**: 胜率-盈亏比平衡分析，目标70%胜率

#### 🔧 自动化管理系统
- **版本管理系统**: 核心功能版本化，支持一键回滚
- **GitHub自动同步**: 每日00:10和12:10自动代码同步
- **调度任务系统**: 8个定时任务自动执行
- **错误隔离机制**: 问题任务不影响整体系统

#### 🎯 明日测试计划
1. 09:00 - V3版财报监控日报自动执行验证
2. 09:30 - 股票数据自动更新
3. 10:00 - 系统健康检查报告
4. 15:00后 - V3.2+R1深度分析测试
5. 收盘后 - 7个量化策略复盘运行

### v1.0.0 (2026-03-28)
- 财报监控系统完成
- 股票池筛选系统开发
- Skill模块体系建立
- Git版本控制集成
- 开发工具完善