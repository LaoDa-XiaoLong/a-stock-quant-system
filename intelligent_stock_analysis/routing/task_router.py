#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能任务路由系统
根据任务类型自动选择 V3.2 或 R1
"""

import re
from typing import Dict, List, Tuple
from datetime import datetime


class TaskRouter:
    """智能任务路由器"""

    def __init__(self):
        self.task_patterns = self._initialize_patterns()
        self.model_mapping = self._initialize_model_mapping()

        print("🚀 智能路由系统初始化完成")
        print(f"📊 支持任务类型: {len(self.task_patterns)} 种")

    def _initialize_patterns(self) -> Dict[str, Dict]:
        """初始化任务模式"""
        return {
            'realtime_query': {
                'keywords': ['涨了没', '当前价格', '实时数据', '最新股价', '今天', '现在', '实时', '当前'],
                'description': '实时查询类任务',
                'priority': 1,
                'examples': [
                    '今天茅台涨了没？',
                    '比亚迪当前价格是多少？',
                    '实时查看宁德时代股价'
                ]
            },
            'simple_qa': {
                'keywords': ['怎么样', '好不好', '可以买吗', '简单分析', '简要', '大概', '简单说'],
                'description': '简单问答类任务',
                'priority': 2,
                'examples': [
                    '宁德时代怎么样？',
                    '比亚迪可以买吗？',
                    '简单分析一下茅台'
                ]
            },
            'multi_step_tools': {
                'keywords': ['查PE后', '获取数据后', '先...再...', '然后', '接着', '之后'],
                'description': '多步工具调用任务',
                'priority': 3,
                'examples': [
                    '查一下PE后筛选同行业股票',
                    '获取财报数据后计算增长率',
                    '先看股价再看成交量'
                ]
            },
            'deep_analysis': {
                'keywords': ['深度分析', '财报解读', '详细分析', '全面分析', '深入研究', '深度'],
                'description': '深度分析类任务',
                'priority': 4,
                'examples': [
                    '深度分析宁德时代财报',
                    '详细解读茅台年报',
                    '全面分析比亚迪投资价值'
                ]
            },
            'valuation_comparison': {
                'keywords': ['对比', '比较', 'vs', ' versus', '哪个更好', '更有价值'],
                'description': '估值对比类任务',
                'priority': 5,
                'examples': [
                    '对比宁德时代和比亚迪',
                    '茅台vs五粮液哪个更好',
                    '比较一下这两只股票'
                ]
            },
            'strategy_validation': {
                'keywords': ['回测验证', '逻辑漏洞', '未来函数', '策略检验', '验证策略', '回测'],
                'description': '策略验证类任务',
                'priority': 6,
                'examples': [
                    '验证这个选股策略',
                    '检查策略是否有未来函数',
                    '回测验证动量策略'
                ]
            },
            'report_generation': {
                'keywords': ['生成报告', '完整分析', '详细研报', '结构化输出', '研报', '报告'],
                'description': '研报生成类任务',
                'priority': 7,
                'examples': [
                    '生成宁德时代深度研报',
                    '输出完整分析报告',
                    '结构化分析茅台'
                ]
            }
        }

    def _initialize_model_mapping(self) -> Dict[str, str]:
        """初始化模型映射"""
        return {
            'realtime_query': 'v32',
            'simple_qa': 'v32',
            'multi_step_tools': 'v32',
            'deep_analysis': 'r1',
            'valuation_comparison': 'r1',
            'strategy_validation': 'r1',
            'report_generation': 'r1',
            'default': 'v32'
        }

    def classify_task(self, user_query: str) -> Tuple[str, str, Dict]:
        """分类任务类型并选择模型"""
        print(f"\n📥 用户查询: {user_query}")

        # 清理查询
        cleaned_query = user_query.strip().lower()

        # 计算每个任务类型的匹配分数
        scores = {}
        for task_type, pattern_info in self.task_patterns.items():
            score = self._calculate_match_score(cleaned_query, pattern_info)
            scores[task_type] = score

        # 选择最高分的任务类型
        best_task = max(scores.items(), key=lambda x: x[1])
        task_type, score = best_task

        # 选择模型
        model = self.model_mapping.get(task_type, self.model_mapping['default'])

        # 构建结果
        result = {
            'task_type': task_type,
            'model': model,
            'confidence_score': score,
            'description': self.task_patterns[task_type]['description'],
            'timestamp': datetime.now().isoformat(),
            'all_scores': scores
        }

        print(f"🎯 路由结果: {task_type} → {model.upper()}")
        print(f"📊 置信度: {score:.2%}")

        return task_type, model, result

    def _calculate_match_score(self, query: str, pattern_info: Dict) -> float:
        """计算匹配分数"""
        score = 0.0

        # 关键词匹配
        keywords = pattern_info['keywords']
        for keyword in keywords:
            if keyword in query:
                score += 0.3  # 每个关键词加0.3分

        # 正则模式匹配
        patterns = self._get_patterns_for_task(pattern_info['description'])
        for pattern in patterns:
            if re.search(pattern, query, re.IGNORECASE):
                score += 0.5  # 模式匹配加0.5分

        # 长度权重（长查询更可能是深度分析）
        if len(query) > 50 and pattern_info['description'] in ['深度分析', '研报生成']:
            score += 0.4

        # 问题词检测
        question_words = ['为什么', '如何', '怎样', '哪些', '什么']
        if any(word in query for word in question_words) and pattern_info['description'] in ['深度分析', '策略验证']:
            score += 0.3

        # 确保分数在0-1之间
        return min(score, 1.0)

    def _get_patterns_for_task(self, task_description: str) -> List[str]:
        """获取任务的正则模式"""
        patterns = {
            '实时查询类任务': [
                r'(当前|现在|今天).*(价格|股价|涨跌)',
                r'(实时|最新).*(数据|信息)',
                r'.*涨了没.*',
                r'.*多少.*钱.*'
            ],
            '深度分析类任务': [
                r'(深度|详细|全面).*(分析|解读|研究)',
                r'(财报|年报|季报).*(分析|解读)',
                r'(投资价值|估值).*(分析|评估)',
                r'(竞争优势|风险).*(分析|评估)'
            ],
            '估值对比类任务': [
                r'(对比|比较|vs).*(和|与)',
                r'.*哪个.*更好.*',
                r'.*更有.*价值.*',
                r'(横向|纵向).*对比.*'
            ],
            '研报生成类任务': [
                r'(生成|输出|创建).*(报告|研报|分析)',
                r'(完整|详细|结构化).*(报告|分析|输出)',
                r'.*研报.*生成.*',
                r'.*报告.*输出.*'
            ]
        }

        return patterns.get(task_description, [])

    def get_routing_decision_tree(self) -> str:
        """获取路由决策树"""
        tree = """
📊 智能路由决策树
================================

用户提问 → 路由层分析 → 模型选择
    ↓
├── 实时查询类 → V3.2（快速响应 + 工具调用）
├── 简单问答类 → V3.2（成本优化）
├── 多步工具类 → V3.2（带思考的工具调用）
├── 深度分析类 → R1（逻辑推理 + 长文本）
├── 估值对比类 → R1（严谨推导 + 对比分析）
├── 策略验证类 → R1（逻辑验证 + 回测）
└── 研报生成类 → R1（131k tokens输出）

💡 设计原则:
• 实时性优先 → V3.2
• 成本敏感 → V3.2
• 深度推理 → R1
• 长文本输出 → R1
• 工具调用 → V3.2
"""
        return tree

    def test_routing_examples(self):
        """测试路由示例"""
        print("\n🧪 路由系统测试")
        print("=" * 50)

        test_cases = [
            "今天茅台涨了没？",
            "比亚迪可以买吗？",
            "查一下宁德时代的PE，然后筛选同行业股票",
            "深度分析宁德时代的最新财报",
            "对比一下宁德时代和比亚迪的投资价值",
            "验证这个动量策略是否有未来函数",
            "生成一份茅台深度研报"
        ]

        for query in test_cases:
            task_type, model, result = self.classify_task(query)
            print(f"📝 '{query[:30]}...' → {task_type} → {model.upper()}")

        print("\n✅ 路由测试完成")


def main():
    """主函数"""
    router = TaskRouter()

    # 显示路由决策树
    print(router.get_routing_decision_tree())

    # 测试路由系统
    router.test_routing_examples()

    # 交互式测试
    print("\n💬 交互式路由测试 (输入 'exit' 退出)")
    print("=" * 50)

    while True:
        try:
            user_input = input("\n请输入查询: ").strip()
            if user_input.lower() in ['exit', 'quit', '退出']:
                break

            if user_input:
                task_type, model, result = router.classify_task(user_input)
                print(f"  任务类型: {result['task_type']}")
                print(f"  选择模型: {model.upper()}")
                print(f"  置信度: {result['confidence_score']:.2%}")
                print(f"  描述: {result['description']}")

        except KeyboardInterrupt:
            print("\n\n👋 退出路由测试")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")


if __name__ == "__main__":
    main()
