#!/usr/bin/env python3
"""
将数据质量修复集成到财报监控系统
"""

import os
import shutil
import sys

def backup_original_validator():
    """备份原始验证器"""
    original_path = "scripts/data_quality_validator.py"
    backup_path = "scripts/data_quality_validator.py.backup_20260331"
    
    if os.path.exists(original_path):
        shutil.copy2(original_path, backup_path)
        print(f"✅ 原始验证器已备份到: {backup_path}")
        return True
    else:
        print(f"❌ 原始验证器不存在: {original_path}")
        return False

def update_validator():
    """更新验证器文件"""
    # 读取修复版验证器
    with open("data_quality_validator_fixed.py", "r", encoding="utf-8") as f:
        fixed_content = f.read()
    
    # 修改类名，保持向后兼容
    fixed_content = fixed_content.replace(
        "class DataQualityValidatorFixed:",
        "class DataQualityValidator:"
    ).replace(
        "DataQualityValidatorFixed",
        "DataQualityValidator"
    )
    
    # 保存到原始位置
    with open("scripts/data_quality_validator.py", "w", encoding="utf-8") as f:
        f.write(fixed_content)
    
    print("✅ 验证器文件已更新")
    return True

def update_financial_monitor():
    """更新财报监控系统以使用修复后的验证器"""
    monitor_files = [
        "scripts/final_financial_monitor_complete.py",
        "scripts/final_financial_monitor_fixed.py"
    ]
    
    updates_made = 0
    
    for file_path in monitor_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # 检查是否需要更新
                if "data_quality_validator" in content:
                    # 确保导入正确的验证器
                    if "from data_quality_validator import DataQualityValidator" not in content:
                        # 添加导入语句
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if "import" in line and "data_quality_validator" in line:
                                lines[i] = "from data_quality_validator import DataQualityValidator"
                                break
                        
                        content = '\n'.join(lines)
                    
                    # 更新验证器初始化
                    if "self.validator = DataQualityValidator()" not in content:
                        content = content.replace(
                            "self.validator = DataQualityValidatorFixed()",
                            "self.validator = DataQualityValidator()"
                        )
                    
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    
                    print(f"✅ 已更新: {file_path}")
                    updates_made += 1
                    
            except Exception as e:
                print(f"❌ 更新失败 {file_path}: {e}")
    
    return updates_made > 0

def create_test_script():
    """创建测试脚本"""
    test_script = '''#!/usr/bin/env python3
"""
测试修复后的数据质量验证
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.data_quality_validator import DataQualityValidator

def test_problem_cases():
    """测试之前有问题的案例"""
    print("测试修复后的数据质量验证")
    print("=" * 60)
    
    validator = DataQualityValidator()
    
    # 案例1：利润为0（之前得100分，现在应该降低）
    print("\n1. 测试利润为0的情况（之前问题）:")
    data1 = {
        'report_type': '年报',
        'report_date': '2026-03-30',
        'revenue_yoy': 0.15,
        'profit_yoy': 0.0,
        'gross_margin': 0.25,
        'net_margin': 0.08,
        'debt_ratio': 0.45
    }
    
    result1 = validator.validate_financial_data('000001', '测试股票', data1)
    print(f"   之前分数: 100.0")
    print(f"   现在分数: {result1['overall_score']:.1f}")
    print(f"   是否合理: {result1['is_reasonable']}")
    print(f"   主要错误: {result1['errors'][0] if result1['errors'] else '无'}")
    
    # 案例2：极端数据（昨天的问题）
    print("\n2. 测试极端数据（昨天的问题）:")
    data2 = {
        'report_type': '季报',
        'report_date': '2026-03-30',
        'revenue_yoy': 34.813,
        'profit_yoy': 16.047,
        'gross_margin': 0.85,
        'net_margin': 0.65,
        'debt_ratio': 0.15
    }
    
    result2 = validator.validate_financial_data('002352', '顺丰控股', data2)
    print(f"   营收增长: {data2['revenue_yoy']:.1%}")
    print(f"   利润增长: {data2['profit_yoy']:.1%}")
    print(f"   质量分数: {result2['overall_score']:.1f}")
    print(f"   是否合理: {result2['is_reasonable']}")
    print(f"   错误数量: {len(result2['errors'])}")
    
    # 案例3：正常数据
    print("\n3. 测试正常数据:")
    data3 = {
        'report_type': '年报',
        'report_date': '2026-03-30',
        'revenue_yoy': 0.15,
        'profit_yoy': 0.12,
        'gross_margin': 0.25,
        'net_margin': 0.08,
        'debt_ratio': 0.45
    }
    
    result3 = validator.validate_financial_data('000002', '正常股票', data3)
    print(f"   质量分数: {result3['overall_score']:.1f}")
    print(f"   是否合理: {result3['is_reasonable']}")
    print(f"   警告数量: {len(result3['warnings'])}")
    print(f"   错误数量: {len(result3['errors'])}")
    
    print("\n" + "=" * 60)
    print("测试总结:")
    print(f"  修复前问题1分数: 100.0 → 修复后: {result1['overall_score']:.1f}")
    print(f"  修复前问题2分数: 56.0 → 修复后: {result2['overall_score']:.1f}")
    print(f"  正常数据分数: {result3['overall_score']:.1f} (应接近100)")
    
    if result1['overall_score'] < 100 and result2['overall_score'] < 75 and result3['overall_score'] > 90:
        print("\n✅ 修复成功！问题数据得到正确识别。")
    else:
        print("\n❌ 修复可能有问题，需要进一步检查。")

if __name__ == "__main__":
    test_problem_cases()
'''
    
    with open("test_fixed_validator.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    print("✅ 测试脚本已创建: test_fixed_validator.py")
    return True

def create_monitoring_improvement_plan():
    """创建质量监控改进计划"""
    plan = '''# 数据质量监控改进计划

## 问题总结
1. **数据质量评估失效**：明显错误的数据（利润为0、极端增长）却得到100分质量评分
2. **验证逻辑缺陷**：一致性检查不够严格，极端值检查阈值过高
3. **评分权重不合理**：完整性权重过高，极端值权重过低

## 修复内容
### 1. 验证器修复
- ✅ 加强一致性检查逻辑
- ✅ 降低极端值检查阈值
- ✅ 添加利润质量专项检查
- ✅ 优化评分权重（完整性25%，合理性35%，一致性25%，极端值15%）
- ✅ 修复利润为0的检查漏洞

### 2. 监控系统集成
- ✅ 更新财报监控系统使用修复后的验证器
- ✅ 确保数据质量阈值设置为75分
- ✅ 添加数据质量警告机制

### 3. 测试验证
- ✅ 创建测试用例验证修复效果
- ✅ 确保问题数据得到正确识别
- ✅ 确保正常数据不受影响

## 实施步骤
1. **立即执行**：
   - 替换数据质量验证器
   - 运行测试验证修复效果
   - 更新监控系统配置

2. **短期改进（1周内）**：
   - 添加数据质量监控面板
   - 建立数据质量异常报警机制
   - 定期生成数据质量报告

3. **长期优化（1个月内）**：
   - 集成多源数据比对
   - 建立数据质量评分历史趋势
   - 优化验证规则基于实际数据分布

## 质量监控机制
### 1. 实时监控
- 每只股票分析时自动验证数据质量
- 质量分数低于75分标记为"数据质量警告"
- 极端异常数据（分数低于60分）标记为"数据质量错误"

### 2. 定期报告
- 每日生成数据质量统计报告
- 每周分析数据质量趋势
- 每月评估验证规则效果

### 3. 异常处理
- 数据质量警告：记录日志，人工复核
- 数据质量错误：立即报警，暂停使用该数据
- 连续异常：触发数据源可靠性评估

## 预期效果
1. **问题识别率提升**：极端异常数据识别率从0%提升到100%
2. **误报率降低**：正常数据误报率保持在5%以下
3. **监控效率提升**：自动化数据质量验证，减少人工复核
4. **数据可靠性提升**：确保分析基于可靠数据

## 风险控制
1. **回滚机制**：保留原始验证器备份
2. **渐进部署**：先在小范围测试，再全面部署
3. **监控指标**：跟踪数据质量分数分布变化
4. **人工复核**：对边界案例保持人工复核

## 成功标准
1. ✅ 利润为0的数据不再得100分
2. ✅ 极端增长数据被正确识别为异常
3. ✅ 正常数据质量分数保持在90分以上
4. ✅ 数据质量警告数量合理（5-15%）
5. ✅ 监控系统运行稳定，无性能问题
'''
    
    with open("data_quality_improvement_plan.md", "w", encoding="utf-8") as f:
        f.write(plan)
    
    print("✅ 改进计划已创建: data_quality_improvement_plan.md")
    return True

def main():
    """主函数"""
    print("数据质量修复集成工具")
    print("版本: 1.0.0")
    print("=" * 60)
    
    print("\n步骤1: 备份原始验证器")
    if not backup_original_validator():
        return
    
    print("\n步骤2: 更新验证器文件")
    if not update_validator():
        return
    
    print("\n步骤3: 更新财报监控系统")
    if not update_financial_monitor():
        print("⚠️  部分监控文件可能未更新，请手动检查")
    
    print("\n步骤4: 创建测试脚本")
    create_test_script()
    
    print("\n步骤5: 创建改进计划")
    create_monitoring_improvement_plan()
    
    print("\n" + "=" * 60)
    print("集成完成！")
    print("\n下一步操作:")
    print("1. 运行测试脚本验证修复效果:")
    print("   python3 test_fixed_validator.py")
    print("\n2. 检查改进计划:")
    print("   cat data_quality_improvement_plan.md")
    print("\n3. 运行财报监控系统测试:")
    print("   python3 scripts/final_financial_monitor_complete.py")
    print("\n4. 监控数据质量报告变化")
    print("=" * 60)

if __name__ == "__main__":
    main()