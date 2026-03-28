#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skill集成管理器
用于将新创建的Skill集成到现有系统中
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import shutil

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SkillIntegrationManager:
    """Skill集成管理器"""
    
    def __init__(self, workspace_path: str = "/Users/ago/.openclaw/workspace"):
        self.workspace_path = Path(workspace_path)
        self.skills_dir = self.workspace_path / 'skills'
        
        # 可用的Skill列表
        self.available_skills = {
            'data-quality-validator': {
                'name': '数据质量验证器',
                'description': '验证数据合理性，防止夸张数据',
                'priority': 1,
                'dependencies': ['numpy', 'pandas']
            },
            'multi-source-fetcher': {
                'name': '多源数据获取器',
                'description': '多数据源获取，故障转移，缓存',
                'priority': 2,
                'dependencies': ['pandas', 'numpy', 'requests']
            },
            'feishu-messenger': {
                'name': '飞书消息推送器',
                'description': '飞书消息推送，多种格式，错误重试',
                'priority': 3,
                'dependencies': ['requests']
            }
        }
        
        # 需要重构的现有系统
        self.systems_to_refactor = {
            '财报监控系统': {
                'path': 'scripts/final_financial_monitor.py',
                'skills_needed': ['data-quality-validator', 'feishu-messenger'],
                'priority': 1
            },
            '股票池筛选系统': {
                'path': 'strategies/stock_pool_filter.py',
                'skills_needed': ['data-quality-validator', 'multi-source-fetcher'],
                'priority': 2
            },
            '数据管道系统': {
                'path': 'scripts/a_share_data_pipeline.py',
                'skills_needed': ['multi-source-fetcher', 'data-quality-validator'],
                'priority': 3
            }
        }
    
    def analyze_integration_points(self) -> Dict:
        """分析集成点"""
        logger.info("开始分析Skill集成点")
        
        analysis = {
            'total_systems': len(self.systems_to_refactor),
            'integration_points': [],
            'estimated_effort': 0,
            'benefits': []
        }
        
        for system_name, system_info in self.systems_to_refactor.items():
            system_path = self.workspace_path / system_info['path']
            
            if not system_path.exists():
                logger.warning(f"系统文件不存在: {system_path}")
                continue
            
            # 分析文件内容
            with open(system_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            integration_point = {
                'system': system_name,
                'file': system_info['path'],
                'skills_needed': system_info['skills_needed'],
                'lines_of_code': len(content.split('\n')),
                'integration_opportunities': []
            }
            
            # 查找可能的集成机会
            for skill_id in system_info['skills_needed']:
                skill_info = self.available_skills.get(skill_id)
                if not skill_info:
                    continue
                
                # 简单分析：查找重复代码模式
                skill_keywords = self._get_skill_keywords(skill_id)
                matches = []
                
                for keyword in skill_keywords:
                    if keyword in content:
                        matches.append(keyword)
                
                if matches:
                    integration_point['integration_opportunities'].append({
                        'skill': skill_id,
                        'skill_name': skill_info['name'],
                        'matches_found': matches,
                        'estimated_lines_to_replace': len(matches) * 10  # 粗略估计
                    })
            
            analysis['integration_points'].append(integration_point)
            analysis['estimated_effort'] += len(integration_point['integration_opportunities']) * 2  # 小时
        
        # 计算收益
        total_lines_to_replace = sum(
            sum(opp['estimated_lines_to_replace'] for opp in point['integration_opportunities'])
            for point in analysis['integration_points']
        )
        
        analysis['benefits'] = [
            f"预计减少代码行数: {total_lines_to_replace}行",
            f"提高代码复用率: 预计提升30-50%",
            f"降低维护成本: 预计降低40-60%",
            f"提高系统稳定性: 使用经过验证的Skill模块"
        ]
        
        logger.info(f"集成点分析完成: 发现{len(analysis['integration_points'])}个集成机会")
        return analysis
    
    def _get_skill_keywords(self, skill_id: str) -> List[str]:
        """获取Skill关键词"""
        keywords_map = {
            'data-quality-validator': [
                'validate', 'quality', 'reasonable', 'score', 'threshold',
                '数据质量', '验证', '合理性', '分数', '阈值'
            ],
            'multi-source-fetcher': [
                'fetch', 'source', 'cache', 'fallback', 'multiple',
                '获取', '数据源', '缓存', '故障转移', '多源'
            ],
            'feishu-messenger': [
                'feishu', 'send', 'message', 'webhook', 'card',
                '飞书', '发送', '消息', '卡片', '通知'
            ]
        }
        return keywords_map.get(skill_id, [])
    
    def create_integration_plan(self, analysis: Dict) -> Dict:
        """创建集成计划"""
        logger.info("创建Skill集成计划")
        
        plan = {
            'phases': [],
            'timeline': {},
            'risks': [],
            'success_criteria': []
        }
        
        # 第一阶段：财报监控系统集成（优先级最高）
        phase1 = {
            'name': '财报监控系统Skill集成',
            'systems': ['财报监控系统'],
            'skills': ['data-quality-validator', 'feishu-messenger'],
            'tasks': [
                '备份现有系统',
                '集成数据质量验证器',
                '集成飞书消息推送器',
                '测试集成后的系统',
                '更新文档'
            ],
            'estimated_hours': 4,
            'priority': '高'
        }
        
        # 第二阶段：股票池筛选系统集成
        phase2 = {
            'name': '股票池筛选系统Skill集成',
            'systems': ['股票池筛选系统'],
            'skills': ['data-quality-validator', 'multi-source-fetcher'],
            'tasks': [
                '备份现有系统',
                '集成数据质量验证器',
                '集成多源数据获取器',
                '测试集成后的系统',
                '性能优化'
            ],
            'estimated_hours': 6,
            'priority': '中'
        }
        
        # 第三阶段：数据管道系统集成
        phase3 = {
            'name': '数据管道系统Skill集成',
            'systems': ['数据管道系统'],
            'skills': ['multi-source-fetcher', 'data-quality-validator'],
            'tasks': [
                '备份现有系统',
                '集成多源数据获取器',
                '集成数据质量验证器',
                '测试集成后的系统',
                '建立监控机制'
            ],
            'estimated_hours': 8,
            'priority': '中'
        }
        
        plan['phases'] = [phase1, phase2, phase3]
        
        # 时间线
        from datetime import datetime, timedelta
        today = datetime.now()
        
        plan['timeline'] = {
            'phase1_start': today.strftime('%Y-%m-%d'),
            'phase1_end': (today + timedelta(days=1)).strftime('%Y-%m-%d'),
            'phase2_start': (today + timedelta(days=2)).strftime('%Y-%m-%d'),
            'phase2_end': (today + timedelta(days=4)).strftime('%Y-%m-%d'),
            'phase3_start': (today + timedelta(days=5)).strftime('%Y-%m-%d'),
            'phase3_end': (today + timedelta(days=7)).strftime('%Y-%m-%d'),
            'total_duration': '7天'
        }
        
        # 风险
        plan['risks'] = [
            '现有系统依赖特定实现，集成可能破坏现有功能',
            'Skill模块可能有未发现的bug',
            '集成后性能可能下降（需要优化）',
            '团队需要时间适应新的架构'
        ]
        
        # 成功标准
        plan['success_criteria'] = [
            '所有集成系统通过测试',
            '代码行数减少20%以上',
            '系统性能不下降',
            '错误率降低30%以上',
            '开发效率提升25%以上'
        ]
        
        logger.info("集成计划创建完成")
        return plan
    
    def backup_system(self, system_path: str) -> bool:
        """备份系统"""
        source_path = self.workspace_path / system_path
        
        if not source_path.exists():
            logger.error(f"系统文件不存在: {source_path}")
            return False
        
        # 创建备份目录
        backup_dir = self.workspace_path / 'backups' / 'skill_integration'
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成备份文件名
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{source_path.stem}_{timestamp}{source_path.suffix}"
        backup_path = backup_dir / backup_name
        
        try:
            shutil.copy2(source_path, backup_path)
            logger.info(f"系统备份完成: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"备份失败: {e}")
            return False
    
    def generate_integration_template(self, system_name: str, skill_id: str) -> str:
        """生成集成模板"""
        templates = {
            'data-quality-validator': '''
# 数据质量验证器集成
from skills.data-quality-validator.data_quality_validator import DataQualityValidator

# 初始化验证器
validator = DataQualityValidator()
validator.set_quality_threshold(75)  # 设置质量阈值

# 在数据获取后验证
data = get_financial_data(stock_code)
validation_result = validator.validate_financial_data(stock_code, stock_name, data)

if validation_result['is_reasonable']:
    # 数据质量合格，继续处理
    process_data(data)
else:
    # 数据质量不合格，记录并跳过
    logger.warning(f"数据质量不合格: {validation_result['overall_score']:.1f}")
    save_low_quality_data(stock_code, data, validation_result)
''',
            'multi-source-fetcher': '''
# 多源数据获取器集成
from skills.multi-source-fetcher.complete_fetcher import MultiSourceFetcher

# 初始化获取器
fetcher = MultiSourceFetcher()
fetcher.configure_cache(enabled=True, cache_dir='./data/cache')

# 获取股票数据（带故障转移）
stock_data = fetcher.get_stock_data(symbol, name)
if stock_data:
    price = stock_data.get('price', 0)
    source = stock_data.get('source', 'unknown')
    logger.info(f"从{source}获取数据: {symbol} 价格={price}")
else:
    # 所有数据源都失败，使用缓存或默认值
    logger.warning(f"所有数据源都失败: {symbol}")
    stock_data = get_fallback_data(symbol)
''',
            'feishu-messenger': '''
# 飞书消息推送器集成
from skills.feishu-messenger.feishu_messenger import FeishuMessenger

# 初始化消息推送器
messenger = FeishuMessenger(webhook_url="你的飞书webhook地址")
messenger.configure_retry(max_retries=3, retry_delay=1.0)

# 安全发送消息（自动降级）
result = messenger.send_safely(
    message="系统通知内容",
    message_type='card',  # 首选卡片消息
    fallback_types=['rich_text', 'text']  # 降级策略
)

if result['success']:
    logger.info("消息发送成功")
else:
    logger.error(f"消息发送失败: {result.get('error', '未知错误')}")
'''
        }
        
        return templates.get(skill_id, '# 集成模板未找到')
    
    def create_refactoring_guide(self) -> str:
        """创建重构指南"""
        guide = """# Skill集成重构指南

## 重构原则
1. **渐进式重构**：一次只重构一个模块，确保系统稳定
2. **充分测试**：重构前后都要进行完整测试
3. **版本控制**：使用Git管理重构过程
4. **文档更新**：重构后更新相关文档

## 重构步骤

### 步骤1：准备工作
1. 备份现有系统
2. 分析集成点
3. 制定详细计划
4. 准备测试用例

### 步骤2：Skill集成
1. 导入Skill模块
2. 替换重复代码
3. 调整接口适配
4. 处理依赖关系

### 步骤3：测试验证
1. 单元测试：验证每个函数
2. 集成测试：验证模块间协作
3. 性能测试：确保性能不下降
4. 回归测试：确保现有功能正常

### 步骤4：优化调整
1. 性能优化
2. 错误处理完善
3. 日志记录优化
4. 配置管理优化

## 常见问题处理

### 问题1：Skill依赖冲突
**解决方案**：
1. 检查requirements.txt中的版本
2. 使用虚拟环境隔离
3. 调整导入顺序

### 问题2：性能下降
**解决方案**：
1. 使用缓存减少重复计算
2. 异步处理耗时操作
3. 批量处理数据

### 问题3：兼容性问题
**解决方案**：
1. 创建适配器模式
2. 保持向后兼容
3. 提供迁移工具

## 成功指标
1. ✅ 代码行数减少20%以上
2. ✅ 错误率降低30%以上
3. ✅ 开发效率提升25%以上
4. ✅ 系统性能不下降
5. ✅ 测试覆盖率不降低

## 后续维护
1. 定期更新Skill版本
2. 监控系统性能
3. 收集用户反馈
4. 持续优化改进
"""
        
        return guide


def main():
    """主函数"""
    print("Skill集成管理器")
    print("版本: 1.0.0")
    print("=" * 60)
    
    manager = SkillIntegrationManager()
    
    print("1. 分析Skill集成点...")
    analysis = manager.analyze_integration_points()
    
    print(f"\n分析结果:")
    print(f"  可重构系统: {analysis['total_systems']}个")
    print(f"  集成机会: {len(analysis['integration_points'])}个")
    print(f"  预计工作量: {analysis['estimated_effort']}小时")
    
    print("\n2. 创建集成计划...")
    plan = manager.create_integration_plan(analysis)
    
    print(f"\n集成计划概要:")
    print(f"  阶段数: {len(plan['phases'])}")
    print(f"  总时长: {plan['timeline']['total_duration']}")
    
    print("\n3. 生成重构指南...")
    guide = manager.create_refactoring_guide()
    
    # 保存指南
    guide_path = manager.workspace_path / 'docs' / 'skill_integration_guide.md'
    guide_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print(f"\n指南已保存: {guide_path.relative_to(manager.workspace_path)}")
    
    print("\n" + "=" * 60)
    print("下一步行动:")
    print("1. 查看详细分析报告")
    print("2. 开始第一阶段重构（财报监控系统）")
    print("3. 按照重构指南逐步实施")
    
    print("\n建议:")
    print("✅ 从高优先级系统开始")
    print("✅ 充分测试每个步骤")
    print("✅ 保持版本控制")
    print("✅ 及时更新文档")


if __name__ == "__main__":
    main()