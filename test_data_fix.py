#!/usr/bin/env python3
"""
测试数据错误修复方案
"""

import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataFixTester:
    """测试数据修复方案"""
    
    def test_original_problem(self):
        """测试原始问题：利润为0但增长率显示为正"""
        print("测试原始问题：利润为0但增长率显示为正")
        print("=" * 60)
        
        # 模拟中国平安的数据问题
        china_pingan_data = {
            'profit_yoy': -0.0,  # 利润为-0
            'expected_profit_yoy': -0.0,  # 预期也为-0
            'revenue_yoy': 0.1,
            'expected_revenue_yoy': 0.08
        }
        
        # 模拟招商银行的数据问题
        china_merchants_data = {
            'profit_yoy': 0.0,  # 利润为0
            'expected_profit_yoy': 0.0,  # 预期也为0
            'revenue_yoy': 0.12,
            'expected_revenue_yoy': 0.09
        }
        
        # 计算超预期比例（原始方法，有问题）
        def calculate_surprise_original(actual, expected):
            if expected != 0:
                return (actual - expected) / abs(expected)
            else:
                return 0
        
        print("中国平安:")
        print(f"  利润: {china_pingan_data['profit_yoy']}")
        print(f"  预期利润: {china_pingan_data['expected_profit_yoy']}")
        print(f"  原始计算增长率: {calculate_surprise_original(china_pingan_data['profit_yoy'], china_pingan_data['expected_profit_yoy'])*100:.1f}%")
        
        print("\n招商银行:")
        print(f"  利润: {china_merchants_data['profit_yoy']}")
        print(f"  预期利润: {china_merchants_data['expected_profit_yoy']}")
        print(f"  原始计算增长率: {calculate_surprise_original(china_merchants_data['profit_yoy'], china_merchants_data['expected_profit_yoy'])*100:.1f}%")
        
        print("\n问题分析:")
        print("1. 当利润和预期都为0时，除法运算可能产生NaN或inf")
        print("2. 浮点数-0和0在比较时可能有问题")
        print("3. 增长率计算需要保护除0操作")
    
    def test_fixed_calculation(self):
        """测试修复后的计算方法"""
        print("\n\n测试修复后的计算方法")
        print("=" * 60)
        
        def calculate_surprise_fixed(actual, expected, epsilon=0.001):
            """修复后的增长率计算方法"""
            # 处理浮点数-0的问题
            actual = 0.0 if abs(actual) < epsilon else actual
            expected = 0.0 if abs(expected) < epsilon else expected
            
            # 保护除0操作
            if abs(expected) < epsilon:
                return 0.0  # 预期为0时，增长率为0
            
            return (actual - expected) / max(abs(expected), epsilon)
        
        # 测试用例
        test_cases = [
            ("中国平安", -0.0, -0.0),
            ("招商银行", 0.0, 0.0),
            ("正常情况1", 0.15, 0.10),
            ("正常情况2", -0.05, 0.02),
            ("边缘情况", 0.001, 0.0005),
        ]
        
        for name, actual, expected in test_cases:
            ratio = calculate_surprise_fixed(actual, expected)
            print(f"{name}:")
            print(f"  实际: {actual}, 预期: {expected}")
            print(f"  增长率: {ratio*100:.1f}%")
            print(f"  是否有效: {'是' if abs(ratio) < 1000 else '否（异常）'}")
            print()
    
    def test_data_generation_fix(self):
        """测试修复后的数据生成"""
        print("\n\n测试修复后的数据生成")
        print("=" * 60)
        
        def generate_realistic_profit_data():
            """生成更真实的利润数据"""
            # 行业基准参数
            industry_params = {
                '银行': {'min': -0.05, 'max': 0.15, 'typical': 0.08},
                '保险': {'min': -0.1, 'max': 0.2, 'typical': 0.10},
                '新能源汽车': {'min': -0.2, 'max': 0.5, 'typical': 0.15},
                '医药': {'min': 0.03, 'max': 0.3, 'typical': 0.12},
            }
            
            # 生成实际利润增长率
            industry = random.choice(list(industry_params.keys()))
            params = industry_params[industry]
            
            # 使用更合理的分布，避免极端值
            profit_yoy = random.uniform(params['min'], params['max'])
            
            # 生成预期值，围绕实际值波动
            expected_profit_yoy = profit_yoy * random.uniform(0.8, 1.2)
            
            # 确保不为0
            if abs(profit_yoy) < 0.01:
                profit_yoy = 0.01 if profit_yoy >= 0 else -0.01
            
            if abs(expected_profit_yoy) < 0.01:
                expected_profit_yoy = 0.01 if expected_profit_yoy >= 0 else -0.01
            
            return {
                'industry': industry,
                'profit_yoy': profit_yoy,
                'expected_profit_yoy': expected_profit_yoy,
                'surprise_ratio': (profit_yoy - expected_profit_yoy) / max(abs(expected_profit_yoy), 0.01)
            }
        
        # 生成测试数据
        print("生成10组测试数据:")
        for i in range(10):
            data = generate_realistic_profit_data()
            print(f"{i+1}. {data['industry']}:")
            print(f"   利润增长率: {data['profit_yoy']*100:+.1f}%")
            print(f"   预期增长率: {data['expected_profit_yoy']*100:+.1f}%")
            print(f"   超预期比例: {data['surprise_ratio']*100:+.1f}%")
            print(f"   是否有效: {'是' if abs(data['surprise_ratio']) < 10 else '否（异常）'}")
            print()
    
    def test_consistency_check(self):
        """测试数据一致性检查"""
        print("\n\n测试数据一致性检查")
        print("=" * 60)
        
        def check_profit_consistency(profit_yoy, expected_profit_yoy, surprise_ratio, epsilon=0.001):
            """检查利润数据一致性"""
            issues = []
            
            # 检查1: 利润接近0但增长率异常
            if abs(profit_yoy) < epsilon and abs(expected_profit_yoy) < epsilon:
                if abs(surprise_ratio) > 0.1:  # 增长率超过10%
                    issues.append(f"利润接近0但增长率显示为{surprise_ratio*100:.1f}%")
            
            # 检查2: 增长率计算是否与原始数据匹配
            calculated_ratio = (profit_yoy - expected_profit_yoy) / max(abs(expected_profit_yoy), epsilon)
            if abs(calculated_ratio - surprise_ratio) > 0.01:  # 差异超过1%
                issues.append(f"增长率计算不一致: 存储={surprise_ratio*100:.1f}%, 重新计算={calculated_ratio*100:.1f}%")
            
            # 检查3: 符号是否一致
            if profit_yoy * expected_profit_yoy < 0:  # 实际和预期符号相反
                issues.append(f"利润增长方向不一致: 实际{profit_yoy*100:+.1f}%, 预期{expected_profit_yoy*100:+.1f}%")
            
            return issues
        
        # 测试用例
        test_cases = [
            ("中国平安问题", -0.0, -0.0, 0.368),
            ("招商银行问题", 0.0, 0.0, 0.340),
            ("正常数据", 0.15, 0.10, 0.50),
            ("负增长", -0.10, -0.05, -1.00),
        ]
        
        for name, profit, expected, ratio in test_cases:
            issues = check_profit_consistency(profit, expected, ratio)
            print(f"{name}:")
            print(f"  利润: {profit}, 预期: {expected}, 增长率: {ratio*100:.1f}%")
            if issues:
                print(f"  发现问题: {len(issues)}个")
                for issue in issues:
                    print(f"    - {issue}")
            else:
                print("  数据一致")
            print()
    
    def run_all_tests(self):
        """运行所有测试"""
        print("数据错误修复方案测试")
        print("=" * 60)
        
        self.test_original_problem()
        self.test_fixed_calculation()
        self.test_data_generation_fix()
        self.test_consistency_check()
        
        print("\n" + "=" * 60)
        print("测试完成")
        print("\n修复方案总结:")
        print("1. ✅ 修复除0保护: 在增长率计算中添加epsilon保护")
        print("2. ✅ 修复数据生成: 确保利润数据不为0")
        print("3. ✅ 增强数据验证: 添加一致性检查")
        print("4. ✅ 改进数据质量: 使用更合理的行业参数")
        print("\n实施建议:")
        print("1. 立即更新数据生成函数")
        print("2. 部署数据一致性检查")
        print("3. 重新运行监控系统验证修复效果")
        print("4. 建立定期数据质量审计机制")

if __name__ == "__main__":
    tester = DataFixTester()
    tester.run_all_tests()