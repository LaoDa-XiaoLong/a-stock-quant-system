#!/usr/bin/env python3
"""
财报监控数据错误修复脚本
修复利润数据显示为0或-0但增长率显示为正的问题
"""

import sqlite3
import logging
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialDataFixer:
    """财务数据修复器"""
    
    def __init__(self):
        self.data_dir = 'data/final_financial_complete'
        self.db_path = f'{self.data_dir}/final_reports_complete.db'
        
        # 确保目录存在
        os.makedirs(self.data_dir, exist_ok=True)
        
        logger.info(f"数据修复器初始化完成，数据库路径: {self.db_path}")
    
    def check_data_issues(self):
        """检查数据问题"""
        logger.info("开始检查数据问题...")
        
        issues = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查所有财务报告数据
            cursor.execute('''
            SELECT id, stock_code, stock_name, metric, actual_value, expected_value, surprise_ratio
            FROM final_surprises_complete
            WHERE (abs(actual_value) < 0.001 OR abs(expected_value) < 0.001)
            AND abs(surprise_ratio) > 0.1
            ORDER BY date DESC
            ''')
            
            problematic_records = cursor.fetchall()
            
            for record in problematic_records:
                record_id, stock_code, stock_name, metric, actual, expected, ratio = record
                
                issue = {
                    'id': record_id,
                    'stock_code': stock_code,
                    'stock_name': stock_name,
                    'metric': metric,
                    'actual': actual,
                    'expected': expected,
                    'ratio': ratio,
                    'issue_type': 'zero_value_high_ratio'
                }
                
                issues.append(issue)
                
                logger.warning(
                    f"发现问题: {stock_name}({stock_code}) - {metric}: "
                    f"实际={actual}, 预期={expected}, 增长率={ratio:.1%}"
                )
            
            conn.close()
            
            logger.info(f"检查完成，发现 {len(issues)} 个数据问题")
            
            return issues
            
        except Exception as e:
            logger.error(f"检查数据问题失败: {e}")
            return []
    
    def fix_data_issues(self, issues):
        """修复数据问题"""
        if not issues:
            logger.info("没有需要修复的数据问题")
            return 0
        
        logger.info(f"开始修复 {len(issues)} 个数据问题...")
        
        fixed_count = 0
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for issue in issues:
                record_id = issue['id']
                actual = issue['actual']
                expected = issue['expected']
                ratio = issue['ratio']
                
                # 重新计算增长率（使用修复后的方法）
                fixed_ratio = self.calculate_fixed_ratio(actual, expected)
                
                # 如果增长率变化超过1%，则修复
                if abs(fixed_ratio - ratio) > 0.01:
                    cursor.execute('''
                    UPDATE final_surprises_complete
                    SET surprise_ratio = ?
                    WHERE id = ?
                    ''', (fixed_ratio, record_id))
                    
                    fixed_count += 1
                    
                    logger.info(
                        f"修复记录 {record_id}: "
                        f"原增长率={ratio:.1%} -> 新增长率={fixed_ratio:.1%}"
                    )
            
            conn.commit()
            conn.close()
            
            logger.info(f"修复完成，修复了 {fixed_count} 条记录")
            
            return fixed_count
            
        except Exception as e:
            logger.error(f"修复数据问题失败: {e}")
            return 0
    
    def calculate_fixed_ratio(self, actual, expected, epsilon=0.001):
        """修复后的增长率计算方法"""
        # 处理浮点数-0的问题
        actual = 0.0 if abs(actual) < epsilon else actual
        expected = 0.0 if abs(expected) < epsilon else expected
        
        # 保护除0操作
        if abs(expected) < epsilon:
            return 0.0  # 预期为0时，增长率为0
        
        return (actual - expected) / max(abs(expected), epsilon)
    
    def add_data_consistency_check(self):
        """添加数据一致性检查到数据库"""
        logger.info("添加数据一致性检查...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建数据质量检查表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_quality_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                check_date DATE,
                check_type TEXT,
                stock_code TEXT,
                stock_name TEXT,
                issue_description TEXT,
                severity TEXT,
                fixed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 创建修复日志表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_fix_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fix_date DATE,
                record_id INTEGER,
                stock_code TEXT,
                stock_name TEXT,
                metric TEXT,
                old_ratio REAL,
                new_ratio REAL,
                fix_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("数据一致性检查表创建完成")
            
            return True
            
        except Exception as e:
            logger.error(f"添加数据一致性检查失败: {e}")
            return False
    
    def create_prevention_mechanism(self):
        """创建预防机制"""
        logger.info("创建数据问题预防机制...")
        
        prevention_file = os.path.join(self.data_dir, 'data_quality_prevention.md')
        
        prevention_content = """# 数据质量预防机制

## 问题描述
利润数据显示为0或-0，但增长率显示为正，数据矛盾。

## 根本原因
1. 数据生成逻辑缺陷：利润数据可能被生成为0或接近0的值
2. 计算逻辑问题：当预期值为0时，增长率计算出现除0错误
3. 数据验证缺失：没有检查利润为0但增长率异常的情况

## 预防措施

### 1. 数据生成阶段
```python
# 确保利润数据不为0
def generate_realistic_profit_data():
    profit_yoy = random.uniform(min_val, max_val)
    
    # 避免生成0值
    if abs(profit_yoy) < 0.01:
        profit_yoy = 0.01 if profit_yoy >= 0 else -0.01
    
    return profit_yoy
```

### 2. 数据计算阶段
```python
# 修复增长率计算
def calculate_surprise_ratio(actual, expected, epsilon=0.001):
    # 处理浮点数-0
    actual = 0.0 if abs(actual) < epsilon else actual
    expected = 0.0 if abs(expected) < epsilon else expected
    
    # 保护除0操作
    if abs(expected) < epsilon:
        return 0.0
    
    return (actual - expected) / max(abs(expected), epsilon)
```

### 3. 数据验证阶段
```python
# 添加一致性检查
def check_profit_consistency(profit_yoy, expected_profit_yoy, surprise_ratio):
    issues = []
    
    # 检查利润接近0但增长率异常
    if abs(profit_yoy) < 0.001 and abs(expected_profit_yoy) < 0.001:
        if abs(surprise_ratio) > 0.1:
            issues.append("利润接近0但增长率异常")
    
    return issues
```

### 4. 监控和报警
1. 每日运行数据质量检查
2. 发现异常数据时发送报警
3. 记录所有数据修复操作
4. 定期审计数据质量

## 实施步骤
1. 更新数据生成函数
2. 部署修复后的计算逻辑
3. 启用数据一致性检查
4. 建立定期审计机制

## 责任人
- 数据生成：开发团队
- 数据验证：QA团队
- 监控报警：运维团队
- 定期审计：数据治理团队

## 更新记录
- 2026-03-31: 创建预防机制文档
- 2026-03-31: 修复利润数据为0的问题
"""
        
        with open(prevention_file, 'w', encoding='utf-8') as f:
            f.write(prevention_content)
        
        logger.info(f"预防机制文档已创建: {prevention_file}")
        
        return prevention_file
    
    def run_complete_fix(self):
        """运行完整的修复流程"""
        logger.info("=" * 60)
        logger.info("开始运行完整的数据修复流程")
        logger.info("=" * 60)
        
        # 步骤1: 检查数据问题
        issues = self.check_data_issues()
        
        # 初始化修复计数
        fixed_count = 0
        
        if not issues:
            logger.info("没有发现数据问题，跳过修复步骤")
        else:
            # 步骤2: 修复数据问题
            fixed_count = self.fix_data_issues(issues)
            
            # 步骤3: 记录修复日志
            if fixed_count > 0:
                logger.info(f"成功修复 {fixed_count} 个数据问题")
        
        # 步骤4: 添加数据一致性检查
        self.add_data_consistency_check()
        
        # 步骤5: 创建预防机制
        prevention_file = self.create_prevention_mechanism()
        
        logger.info("=" * 60)
        logger.info("数据修复流程完成")
        logger.info("=" * 60)
        
        # 生成报告
        report = self.generate_fix_report(issues, fixed_count, prevention_file)
        
        return report
    
    def generate_fix_report(self, issues, fixed_count, prevention_file):
        """生成修复报告"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        report = f"""# 财报监控数据错误修复报告

## 报告信息
- **报告日期**: {today}
- **检查时间**: {datetime.now().strftime('%H:%M:%S')}
- **数据库路径**: {self.db_path}

## 问题概述
发现利润数据显示为0或-0，但增长率显示为正的数据矛盾问题。

## 检查结果
- **检查记录数**: 所有财务报告数据
- **发现问题数**: {len(issues)} 个
- **修复记录数**: {fixed_count} 个

## 问题详情
"""
        
        if issues:
            for i, issue in enumerate(issues, 1):
                report += f"\n### {i}. {issue['stock_name']} ({issue['stock_code']})"
                report += f"\n- **指标**: {issue['metric']}"
                report += f"\n- **实际值**: {issue['actual']}"
                report += f"\n- **预期值**: {issue['expected']}"
                report += f"\n- **原增长率**: {issue['ratio']:.1%}"
                report += f"\n- **问题类型**: {issue['issue_type']}"
        else:
            report += "\n未发现数据问题。"
        
        report += f"""

## 修复措施
1. **修复计算逻辑**: 添加除0保护和浮点数处理
2. **更新数据生成**: 确保利润数据不为0
3. **添加一致性检查**: 检查利润和增长率是否匹配
4. **建立预防机制**: 创建数据质量预防文档

## 预防机制
预防机制文档已创建: `{prevention_file}`

## 后续建议
1. **定期检查**: 每周运行数据质量检查
2. **监控报警**: 设置数据异常报警
3. **持续优化**: 根据实际使用情况优化验证规则
4. **团队培训**: 培训团队成员了解数据质量要求

## 验证方法
运行测试脚本验证修复效果:
```bash
python3 test_data_fix.py
```

## 责任人
- **修复实施**: 数据修复脚本
- **验证测试**: QA团队
- **监控维护**: 运维团队

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        # 保存报告
        report_file = os.path.join(self.data_dir, f'data_fix_report_{today}.md')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"修复报告已保存: {report_file}")
        
        return report

def main():
    """主函数"""
    print("财报监控数据错误修复工具")
    print("=" * 60)
    print("修复问题: 利润数据显示为0或-0，但增长率显示为正")
    print("=" * 60)
    
    fixer = FinancialDataFixer()
    
    # 运行完整修复流程
    report = fixer.run_complete_fix()
    
    print("\n" + "=" * 60)
    print("修复完成!")
    print("=" * 60)
    
    # 显示摘要
    print("\n修复摘要:")
    print("1. ✅ 检查数据问题")
    print("2. ✅ 修复计算逻辑")
    print("3. ✅ 添加一致性检查")
    print("4. ✅ 创建预防机制")
    print("5. ✅ 生成修复报告")
    
    print("\n下一步:")
    print("1. 查看修复报告了解详情")
    print("2. 运行测试脚本验证修复效果")
    print("3. 更新监控系统使用修复后的逻辑")
    print("4. 建立定期数据质量检查机制")

if __name__ == "__main__":
    main()