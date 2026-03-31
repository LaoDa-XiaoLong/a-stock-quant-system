#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复后的建议生成模块
解决基于错误数据给出投资建议的风险问题
"""

from typing import Dict, Tuple, Optional
import math

class FixedAdviceGenerator:
    """修复后的建议生成器"""
    
    def __init__(self):
        # 配置参数
        self.min_data_quality = 80  # 最低数据质量分数
        self.max_surprise_ratio = 1.0  # 最大超预期比例
        self.min_valid_value = 1  # 最小有效数值
        self.required_fields = ['actual_value', 'expected_value', 'surprise_ratio', 'data_quality_score']
        
        # 建议阈值配置
        self.advice_thresholds = {
            'strong_buy': 0.30,      # 强烈推荐加仓
            'buy': 0.20,            # 考虑加仓
            'hold': 0.10,           # 持有观察
            'neutral': -0.10,       # 维持现状
            'caution': -0.20,       # 关注风险
            # 低于-0.20为考虑减仓
        }
        
        # 风险提示模板
        self.risk_warnings = {
            'data_quality_low': "⚠️ 数据质量较低({score}分)，建议谨慎参考",
            'value_zero': "🚨 数据异常：{field}为0，建议核实原始数据",
            'extreme_ratio': "⚠️ 超预期比例异常({ratio:.1f}%)，可能存在数据错误",
            'missing_field': "❌ 数据不完整：缺失{field}字段"
        }
        
        # 核实建议模板
        self.verification_suggestions = [
            "建议核实财报原始数据",
            "建议关注公司官方公告",
            "建议结合其他信息源验证",
            "建议等待下个报告期确认"
        ]
    
    def validate_data(self, stock: Dict) -> Tuple[bool, str, Optional[str]]:
        """数据验证前置检查
        
        Args:
            stock: 股票数据字典
            
        Returns:
            Tuple[是否有效, 验证消息, 风险级别]
        """
        # 1. 检查数据完整性
        for field in self.required_fields:
            if field not in stock:
                return False, f"缺失必要字段: {field}", "high"
        
        # 2. 检查数值有效性
        if stock['actual_value'] == 0:
            return False, "实际值为0，数据异常", "critical"
        if stock['expected_value'] == 0:
            return False, "预期值为0，数据异常", "critical"
        
        # 3. 检查数据质量
        if stock['data_quality_score'] < self.min_data_quality:
            return False, f"数据质量分数过低: {stock['data_quality_score']}", "medium"
        
        # 4. 检查超预期比例合理性
        if math.isinf(stock['surprise_ratio']) or math.isnan(stock['surprise_ratio']):
            return False, "超预期比例计算错误(无穷大或NaN)", "critical"
        
        if abs(stock['surprise_ratio']) > self.max_surprise_ratio:
            return False, f"超预期比例异常: {stock['surprise_ratio']}", "high"
        
        # 5. 检查数值范围合理性
        if stock['actual_value'] < 0 or stock['expected_value'] < 0:
            return False, "数值为负，数据异常", "high"
        
        return True, "数据验证通过", None
    
    def calculate_surprise_ratio(self, actual: float, expected: float) -> float:
        """安全计算超预期比例
        
        Args:
            actual: 实际值
            expected: 预期值
            
        Returns:
            超预期比例，异常时返回0
        """
        try:
            if expected == 0:
                return 0.0  # 避免除零错误
            return (actual - expected) / expected
        except Exception:
            return 0.0
    
    def get_risk_level(self, stock: Dict) -> str:
        """获取风险等级
        
        Args:
            stock: 股票数据
            
        Returns:
            风险等级: low/medium/high/critical
        """
        data_quality = stock.get('data_quality_score', 100)
        surprise_ratio = stock.get('surprise_ratio', 0)
        
        if data_quality < 70:
            return "critical"
        elif data_quality < 80:
            return "high"
        elif data_quality < 90:
            return "medium"
        elif abs(surprise_ratio) > 0.5:
            return "high"
        else:
            return "low"
    
    def get_trading_advice(self, stock: Dict) -> str:
        """修复后的交易建议生成
        
        Args:
            stock: 股票数据字典
            
        Returns:
            格式化后的交易建议
        """
        # 数据验证
        is_valid, message, risk_level = self.validate_data(stock)
        if not is_valid:
            return self._format_error_advice(message, risk_level)
        
        surprise_ratio = stock['surprise_ratio']
        data_quality = stock['data_quality_score']
        risk_level = self.get_risk_level(stock)
        
        # 根据数据质量和风险等级调整建议强度
        quality_factor = data_quality / 100.0
        risk_factor = self._get_risk_factor(risk_level)
        
        # 调整后的阈值
        adjusted_thresholds = {
            key: value * quality_factor * risk_factor
            for key, value in self.advice_thresholds.items()
        }
        
        # 生成建议
        if surprise_ratio >= adjusted_thresholds['strong_buy']:
            advice = "强烈推荐加仓"
            color = "green"
            icon = "✅"
        elif surprise_ratio >= adjusted_thresholds['buy']:
            advice = "考虑加仓"
            color = "green"
            icon = "✅"
        elif surprise_ratio >= adjusted_thresholds['hold']:
            advice = "持有观察"
            color = "blue"
            icon = "🔍"
        elif surprise_ratio >= adjusted_thresholds['neutral']:
            advice = "维持现状"
            color = "gray"
            icon = "📋"
        elif surprise_ratio >= adjusted_thresholds['caution']:
            advice = "关注风险"
            color = "orange"
            icon = "⚠️"
        else:
            advice = "考虑减仓"
            color = "red"
            icon = "🚨"
        
        # 添加风险提示
        risk_note = self._get_risk_note(risk_level, data_quality)
        if risk_note:
            advice = f"{advice} {risk_note}"
        
        # 添加核实建议（高风险时）
        if risk_level in ["high", "critical"]:
            verification = self._get_verification_suggestion()
            advice = f"{advice}\n{verification}"
        
        return f"<font color='{color}'>{icon} {advice}</font>"
    
    def _format_error_advice(self, message: str, risk_level: str) -> str:
        """格式化错误建议"""
        colors = {
            "critical": "red",
            "high": "orange",
            "medium": "yellow",
            "low": "blue"
        }
        color = colors.get(risk_level, "red")
        
        icons = {
            "critical": "🚨",
            "high": "⚠️",
            "medium": "🔍",
            "low": "ℹ️"
        }
        icon = icons.get(risk_level, "⚠️")
        
        return f"<font color='{color}'>{icon} {message}</font>"
    
    def _get_risk_factor(self, risk_level: str) -> float:
        """获取风险调整因子"""
        factors = {
            "critical": 0.5,   # 高风险时建议强度减半
            "high": 0.7,       # 较高风险时建议强度降低30%
            "medium": 0.9,     # 中等风险时建议强度降低10%
            "low": 1.0         # 低风险时正常强度
        }
        return factors.get(risk_level, 1.0)
    
    def _get_risk_note(self, risk_level: str, data_quality: float) -> str:
        """获取风险说明"""
        if risk_level == "critical":
            return f"(数据质量: {data_quality}分，高风险)"
        elif risk_level == "high":
            return f"(数据质量: {data_quality}分，较高风险)"
        elif risk_level == "medium":
            return f"(数据质量: {data_quality}分)"
        else:
            return ""
    
    def _get_verification_suggestion(self) -> str:
        """获取核实建议"""
        import random
        return random.choice(self.verification_suggestions)
    
    def generate_comprehensive_analysis(self, stock: Dict) -> str:
        """生成综合分析
        
        Args:
            stock: 股票数据
            
        Returns:
            格式化后的综合分析
        """
        lines = []
        
        # 数据验证状态
        is_valid, message, risk_level = self.validate_data(stock)
        
        lines.append("### 📊 数据质量分析")
        if is_valid:
            lines.append(f"✅ 数据验证通过")
            lines.append(f"- 数据质量分数: {stock['data_quality_score']}分")
            lines.append(f"- 风险等级: {risk_level}")
        else:
            lines.append(f"❌ 数据验证失败: {message}")
            lines.append(f"- 风险等级: {risk_level}")
        
        # 关键指标
        lines.append("\n### 📈 关键指标")
        actual = stock.get('actual_value', 0)
        expected = stock.get('expected_value', 0)
        ratio = stock.get('surprise_ratio', 0)
        
        # 格式化数值
        if actual >= 1e8:
            actual_fmt = f"{actual/1e8:.1f}亿"
            expected_fmt = f"{expected/1e8:.1f}亿"
        elif actual >= 1e4:
            actual_fmt = f"{actual/1e4:.1f}万"
            expected_fmt = f"{expected/1e4:.1f}万"
        else:
            actual_fmt = f"{actual:.0f}"
            expected_fmt = f"{expected:.0f}"
        
        lines.append(f"- 实际值: {actual_fmt}")
        lines.append(f"- 预期值: {expected_fmt}")
        lines.append(f"- 超预期比例: {ratio*100:+.1f}%")
        
        # 交易建议
        lines.append("\n### 💡 交易建议")
        advice = self.get_trading_advice(stock)
        lines.append(advice)
        
        # 风险提示
        if risk_level in ["high", "critical"]:
            lines.append("\n### ⚠️ 风险提示")
            lines.append("1. 数据质量需要进一步核实")
            lines.append("2. 建议结合其他信息源验证")
            lines.append("3. 谨慎参考当前建议")
        
        return "\n".join(lines)


# 测试函数
def test_fixed_advice_generator():
    """测试修复后的建议生成器"""
    print("=" * 70)
    print("🧪 测试修复后的建议生成器")
    print("=" * 70)
    
    generator = FixedAdviceGenerator()
    
    test_cases = [
        {
            'name': '正常高质量数据',
            'stock': {
                'actual_value': 15000000000,
                'expected_value': 12000000000,
                'surprise_ratio': 0.25,
                'data_quality_score': 95
            },
            'expected': '考虑加仓'
        },
        {
            'name': '利润为0的错误数据',
            'stock': {
                'actual_value': 0,
                'expected_value': 10000000000,
                'surprise_ratio': -1.0,
                'data_quality_score': 100
            },
            'expected': '数据异常警告'
        },
        {
            'name': '预期值为0的错误数据',
            'stock': {
                'actual_value': 5000000000,
                'expected_value': 0,
                'surprise_ratio': float('inf'),
                'data_quality_score': 100
            },
            'expected': '数据异常警告'
        },
        {
            'name': '低质量数据',
            'stock': {
                'actual_value': 5000000000,
                'expected_value': 4000000000,
                'surprise_ratio': 0.25,
                'data_quality_score': 75
            },
            'expected': '数据质量警告'
        },
        {
            'name': '极端超预期比例',
            'stock': {
                'actual_value': 10000000000,
                'expected_value': 1000000,
                'surprise_ratio': 99.0,
                'data_quality_score': 100
            },
            'expected': '超预期比例异常'
        },
        {
            'name': '中等质量数据',
            'stock': {
                'actual_value': 8000000000,
                'expected_value': 7000000000,
                'surprise_ratio': 0.15,
                'data_quality_score': 85
            },
            'expected': '持有观察'
        }
    ]
    
    for test in test_cases:
        print(f"\n📊 测试: {test['name']}")
        print(f"   数据: {test['stock']}")
        
        advice = generator.get_trading_advice(test['stock'])
        print(f"   建议: {advice}")
        
        # 验证建议
        if test['expected'] in advice:
            print(f"   ✅ 符合预期")
        else:
            print(f"   ❌ 不符合预期")
        
        # 显示综合分析
        if "警告" not in advice and "异常" not in advice:
            analysis = generator.generate_comprehensive_analysis(test['stock'])
            print(f"   综合分析预览: {analysis[:100]}...")
    
    print("\n" + "=" * 70)
    print("✅ 测试完成！")
    print("=" * 70)


if __name__ == "__main__":
    test_fixed_advice_generator()