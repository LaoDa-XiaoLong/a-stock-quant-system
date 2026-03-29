#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
协同工作流引擎
V3.2 和 R1 的协同工作流
"""

import time
from datetime import datetime
from typing import Dict, Any, Optional
import sys
import os

# 添加模块路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routing.task_router import TaskRouter
from collectors.v32_data_collector import V32DataCollector
from analyzers.r1_deep_analyzer_complete import R1DeepAnalyzerComplete


class CollaborativeWorkflow:
    """协同工作流引擎"""
    
    def __init__(self):
        self.workflow_name = "V3.2 + R1 协同工作流引擎 v1.0"
        self.router = TaskRouter()
        self.v32_collector = V32DataCollector()
        self.r1_analyzer = R1DeepAnalyzerComplete()
        
        self.performance_metrics = {
            'total_queries': 0,
            'v32_only': 0,
            'collaborative': 0,
            'avg_response_time': 0,
            'success_rate': 1.0
        }
        
        print(f"🚀 {self.workflow_name} 初始化完成")
        print(f"📊 组件: 路由系统 + V3.2采集器 + R1分析器")
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """处理用户查询"""
        self.performance_metrics['total_queries'] += 1
        start_time = time.time()
        
        print(f"\n" + "=" * 70)
        print(f"📥 处理用户查询: {user_query}")
        print("=" * 70)
        
        try:
            # 1. 路由决策
            print(f"\n1. 🎯 智能路由决策")
            task_type, model, routing_result = self.router.classify_task(user_query)
            print(f"   任务类型: {task_type}")
            print(f"   选择模型: {model.upper()}")
            print(f"   置信度: {routing_result['confidence_score']:.2%}")
            
            # 2. 根据模型选择处理流程
            if model == 'v32':
                # V3.2 单独处理
                self.performance_metrics['v32_only'] += 1
                result = self._process_with_v32(user_query, task_type)
                
            else:  # model == 'r1'
                # 协同工作流：V3.2采集 → R1分析
                self.performance_metrics['collaborative'] += 1
                result = self._process_collaborative_workflow(user_query, task_type)
            
            # 3. 计算性能指标
            processing_time = time.time() - start_time
            self.performance_metrics['avg_response_time'] = (
                self.performance_metrics['avg_response_time'] * (self.performance_metrics['total_queries'] - 1) + 
                processing_time
            ) / self.performance_metrics['total_queries']
            
            # 4. 添加元数据
            result['workflow_metadata'] = {
                'processing_time_seconds': round(processing_time, 2),
                'workflow_type': 'v32_only' if model == 'v32' else 'collaborative',
                'task_type': task_type,
                'model_used': model,
                'routing_confidence': routing_result['confidence_score'],
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"\n✅ 查询处理完成")
            print(f"   处理时间: {processing_time:.2f}秒")
            print(f"   工作流类型: {'V3.2单独处理' if model == 'v32' else 'V3.2+R1协同'}")
            
            return result
            
        except Exception as e:
            print(f"\n❌ 处理失败: {e}")
            import traceback
            traceback.print_exc()
            
            self.performance_metrics['success_rate'] = (
                self.performance_metrics['success_rate'] * (self.performance_metrics['total_queries'] - 1)
            ) / self.performance_metrics['total_queries']
            
            return {
                'error': str(e),
                'success': False,
                'workflow_metadata': {
                    'processing_time_seconds': round(time.time() - start_time, 2),
                    'error': True,
                    'timestamp': datetime.now().isoformat()
                }
            }
    
    def _process_with_v32(self, user_query: str, task_type: str) -> Dict[str, Any]:
        """V3.2 单独处理"""
        print(f"\n2. 🤖 V3.2 单独处理")
        
        # 模拟V3.2处理不同类型的查询
        if task_type == 'realtime_query':
            response = self._simulate_v32_realtime_query(user_query)
        elif task_type == 'simple_qa':
            response = self._simulate_v32_simple_qa(user_query)
        elif task_type == 'multi_step_tools':
            response = self._simulate_v32_multi_step(user_query)
        else:
            response = self._simulate_v32_general_query(user_query)
        
        result = {
            'success': True,
            'model': 'DeepSeek-V3.2',
            'response': response,
            'task_type': task_type,
            'processing_notes': 'V3.2快速处理，支持工具调用'
        }
        
        return result
    
    def _process_collaborative_workflow(self, user_query: str, task_type: str) -> Dict[str, Any]:
        """协同工作流处理"""
        print(f"\n2. 🔄 启动协同工作流: V3.2 → R1")
        
        # 第一步：V3.2 数据采集
        print(f"\n   第一步: V3.2 数据采集")
        
        # 提取股票代码（这里简化处理，实际需要NLP识别）
        stock_codes = self._extract_stock_codes(user_query)
        if not stock_codes:
            stock_codes = ['300750', '002594']  # 默认宁德时代和比亚迪
        
        # 确定需要采集的数据类型
        data_types = self._determine_data_types(task_type, user_query)
        
        print(f"     股票: {', '.join(stock_codes)}")
        print(f"     数据类型: {', '.join(data_types)}")
        
        # 采集数据
        collected_data = self.v32_collector.collect_realtime_data(stock_codes, data_types)
        
        # 第二步：准备R1分析数据包
        print(f"\n   第二步: 准备R1分析数据包")
        r1_input = self.v32_collector.prepare_for_r1_analysis(collected_data, user_query)
        
        # 第三步：R1深度分析
        print(f"\n   第三步: R1深度分析")
        r1_result = self.r1_analyzer.analyze_with_chain_of_thought(r1_input)
        
        # 构建最终结果
        result = {
            'success': True,
            'workflow': 'collaborative',
            'components': {
                'v32_data_collection': {
                    'stocks_analyzed': list(collected_data['stocks'].keys()),
                    'data_types_collected': data_types,
                    'collection_time': collected_data['collection_time']
                },
                'r1_analysis': {
                    'analysis_id': r1_result['analysis_id'],
                    'analysis_type': r1_result['analysis_type'],
                    'key_findings_count': len(r1_result['key_findings']),
                    'recommendations_count': len(r1_result['recommendations'])
                }
            },
            'analysis_result': r1_result,
            'task_type': task_type,
            'processing_notes': 'V3.2采集数据 + R1深度分析协同工作流'
        }
        
        return result
    
    def _extract_stock_codes(self, query: str) -> list:
        """提取股票代码（简化版）"""
        # 这里应该使用NLP技术，这里简化处理
        stock_mapping = {
            '宁德时代': '300750',
            '比亚迪': '002594',
            '茅台': '600519',
            '五粮液': '000858',
            '药明康德': '603259',
            '海康威视': '002415'
        }
        
        extracted_codes = []
        for name, code in stock_mapping.items():
            if name in query:
                extracted_codes.append(code)
        
        return extracted_codes
    
    def _determine_data_types(self, task_type: str, query: str) -> list:
        """确定需要采集的数据类型"""
        base_types = ['stock_price']
        
        if '财务' in query or '财报' in query:
            base_types.append('financial_data')
        
        if '估值' in query or 'pe' in query.lower() or 'pb' in query.lower():
            base_types.append('valuation_metrics')
        
        if '新闻' in query or '舆情' in query:
            base_types.append('news_sentiment')
        
        if '行业' in query or '对比' in query:
            base_types.append('industry_data')
        
        if '技术' in query or '指标' in query:
            base_types.append('technical_indicators')
        
        # 根据任务类型添加
        if task_type in ['deep_analysis', 'valuation_comparison', 'report_generation']:
            if 'financial_data' not in base_types:
                base_types.append('financial_data')
            if 'valuation_metrics' not in base_types:
                base_types.append('valuation_metrics')
        
        return list(set(base_types))  # 去重
    
    def _simulate_v32_realtime_query(self, query: str) -> str:
        """模拟V3.2实时查询响应"""
        responses = {
            '茅台': "贵州茅台(600519)当前价格 1850.5元，今日上涨 +2.3%，成交量 12.5万手。",
            '比亚迪': "比亚迪(002594)当前价格 105.8元，今日上涨 +1.8%，成交量 45.2万手。",
            '宁德时代': "宁德时代(300750)当前价格 210.5元，今日下跌 -0.8%，成交量 28.7万手。"
        }
        
        for stock, response in responses.items():
            if stock in query:
                return response
        
        return "查询成功，当前市场运行平稳。如需具体股票信息，请提供股票名称或代码。"
    
    def _simulate_v32_simple_qa(self, query: str) -> str:
        """模拟V3.2简单问答响应"""
        responses = {
            '可以买吗': "投资需谨慎，建议先分析公司基本面和估值水平。当前市场环境下，建议分批建仓，控制风险。",
            '怎么样': "需要具体分析。如果是问股票，请提供股票名称；如果是问市场，当前市场整体平稳，结构性机会存在。",
            '简单分析': "简单分析需要具体对象。例如分析某只股票，我会查看其基本面、估值、技术面等关键指标。"
        }
        
        for keyword, response in responses.items():
            if keyword in query:
                return response
        
        return "已收到您的查询。这是一个简单问答，V3.2可以快速处理。如需深度分析，请提供更详细的问题。"
    
    def _simulate_v32_multi_step(self, query: str) -> Dict[str, Any]:
        """模拟V3.2多步工具调用响应"""
        return {
            'response': "多步工具调用执行完成。",
            'steps_executed': [
                "1. 查询宁德时代PE比率：35.2倍",
                "2. 筛选同行业（新能源汽车）公司",
                "3. 计算行业平均PE：32.5倍",
                "4. 对比分析：宁德时代估值略高于行业平均，但基于技术领先性合理"
            ],
            'tools_used': ['股价查询', '行业筛选', '数据计算', '对比分析'],
            'execution_time': '2.3秒'
        }
    
    def _simulate_v32_general_query(self, query: str) -> str:
        """模拟V3.2通用查询响应"""
        return "V3.2处理完成。这是一个通用查询，已基于可用工具和数据提供响应。如需更深度分析，建议使用更详细的问题描述。"
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        return {
            'performance_metrics': self.performance_metrics,
            'efficiency_analysis': {
                'v32_ratio': self.performance_metrics['v32_only'] / max(self.performance_metrics['total_queries'], 1),
                'collaborative_ratio': self.performance_metrics['collaborative'] / max(self.performance_metrics['total_queries'], 1),
                'avg_response_time': self.performance_metrics['avg_response_time'],
                'estimated_cost_savings': '40-60% (相比全用R1)'
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def demonstrate_workflows(self):
        """演示工作流"""
        print("\n" + "=" * 70)
        print("🚀 协同工作流演示")
        print("=" * 70)
        
        test_cases = [
            {
                'query': "今天茅台涨了没？",
                'description': "实时查询 - V3.2单独处理"
            },
            {
                'query': "比亚迪可以买吗？",
                'description': "简单问答 - V3.2单独处理"
            },
            {
                'query': "查一下宁德时代的PE，然后筛选同行业股票",
                'description': "多步工具调用 - V3.2单独处理"
            },
            {
                'query': "深度分析宁德时代的最新财报",
                'description': "深度分析 - V3.2+R1协同"
            },
            {
                'query': "对比一下宁德时代和比亚迪的投资价值",
                'description': "对比分析 - V3.2+R1协同"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. 📝 测试用例: {test_case['description']}")
            print(f"   查询: {test_case['query']}")
            
            result = self.process_query(test_case['query'])
            
            if result.get('success'):
                print(f"   ✅ 处理成功")
                print(f"   模型: {result.get('model', '协同工作流')}")
                print(f"   时间: {result['workflow_metadata']['processing_time_seconds']}秒")
            else:
                print(f"   ❌ 处理失败")
            
            print()
        
        # 显示性能报告
        print("\n" + "=" * 70)
        print("📊 工作流性能报告")
        print("=" * 70)
        
        perf_report = self.get_performance_report()
        metrics = perf_report['performance_metrics']
        
        print(f"\n📈 处理统计:")
        print(f"   总查询数: {metrics['total_queries']}")
        print(f"   V3.2单独处理: {metrics['v32_only']} ({metrics['v32_only']/max(metrics['total_queries'],1)*100:.1f}%)")
        print(f"   协同工作流: {metrics['collaborative']} ({metrics['collaborative']/max(metrics['total_queries'],1)*100:.1f}%)")
        print(f"   平均响应时间: {metrics['avg_response_time']:.2f}秒")
        print(f"   成功率: {metrics['success_rate']*100:.1f}%")
        
        print(f"\n💰 成本优化分析:")
        print(f"   V3.2处理占比: {perf_report['efficiency_analysis']['v32_ratio']*100:.1f}%")
        print(f"   协同工作流占比: {perf_report['efficiency_analysis']['collaborative_ratio']*100:.1f}%")
        print(f"   预计成本节省: {perf_report['efficiency_analysis']['estimated_cost_savings']}")
        
        print(f"\n🎯 设计优势:")
        print(f"   1. 实时查询 → V3.2快速响应 (<2秒)")
        print(f"   2. 简单问答 → V3.2成本优化")
        print(f"   3. 深度分析 → V3.2+R1协同 (效果最优)")
        print(f"   4. 成本控制 → 按需使用合适模型")


def main():
    """主函数"""
    workflow = CollaborativeWorkflow()
    workflow.demonstrate_workflows()


if __name__ == "__main__":
    main()