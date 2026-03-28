# A股量化交易系统

## 项目概述
基于Python的A股量化交易系统，包含财报监控、股票池筛选、多因子分析、交易执行等功能。

## 项目状态
- **版本**: v1.0.0
- **状态**: 开发中
- **最后更新**: 2026-03-28

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

### 4. 开发工具
- 可靠文件编辑器（解决edit失败问题）
- 文件状态监控器
- 代码健康度检查
- 自动化测试框架

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
│   └── generate_daily_report.py        # 日报生成器
├── strategies/               # 交易策略
│   ├── simple_macd_strategy.py
│   └── stock_pool_filter_complete.py
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

### 定时任务
```bash
# 每日21:30运行财报监控
30 21 * * * cd /path/to/project && python scripts/final_financial_monitor.py
```

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

### v1.0.0 (2026-03-28)
- 财报监控系统完成
- 股票池筛选系统开发
- Skill模块体系建立
- Git版本控制集成
- 开发工具完善