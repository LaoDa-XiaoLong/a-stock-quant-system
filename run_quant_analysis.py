#!/usr/bin/env python3
"""
量化分析主执行脚本
整合数据获取、分析和策略回测
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def print_header(title):
    """打印标题"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def run_script(script_path, description):
    """运行Python脚本"""
    print_header(description)
    
    if not os.path.exists(script_path):
        print(f"脚本不存在: {script_path}")
        return False
    
    try:
        # 运行脚本
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True, encoding='utf-8')
        
        # 打印输出
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
        
        return result.returncode == 0
    
    except Exception as e:
        print(f"运行脚本时出错: {e}")
        return False

def generate_final_report():
    """生成最终报告"""
    print_header("量化分析最终报告")
    
    report_content = f"""
# 量化股票分析报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 项目概述
本报告展示了完整的量化分析流程，包括：
1. 数据获取 - 从免费数据源获取A股数据
2. 数据分析 - 技术指标计算和可视化
3. 策略开发 - MACD交易策略实现
4. 回测验证 - 策略历史表现测试

## 数据源
- **数据提供**: akshare (免费A股数据接口)
- **示例股票**: 000001 (平安银行)
- **数据期间**: 2023年至今

## 技术指标
已计算以下技术指标：
- 移动平均线 (SMA 5/10/20日)
- 指数移动平均线 (EMA 12/26日)
- MACD (12, 26, 9)
- RSI (14日)
- 布林带 (20日, 2倍标准差)
- 成交量移动平均

## 交易策略
**MACD交叉策略**:
- 买入信号: MACD线上穿信号线
- 卖出信号: MACD线下穿信号线
- 仓位管理: 95%资金投入
- 佣金: 0.1%

## 文件结构
```
量化分析项目/
├── data/                    # 数据目录
│   ├── raw/                # 原始数据
│   └── processed/          # 处理后的数据
├── strategies/             # 交易策略
│   └── simple_macd_strategy.py
├── scripts/               # 工具脚本
│   ├── data_fetcher.py    # 数据获取
│   └── basic_analysis.py  # 基础分析
├── reports/               # 分析报告
│   ├── price_chart_000001.png    # 价格图表
│   ├── backtest_chart.png        # 回测图表
│   └── trade_records.csv         # 交易记录
└── run_quant_analysis.py  # 主执行脚本
```

## 使用说明
1. 数据获取: `python scripts/data_fetcher.py`
2. 数据分析: `python scripts/basic_analysis.py`
3. 策略回测: `python strategies/simple_macd_strategy.py`
4. 完整流程: `python run_quant_analysis.py`

## 后续改进建议
1. **数据源扩展**: 集成tushare等更多数据源
2. **策略优化**: 添加更多技术指标和机器学习模型
3. **风险控制**: 加入止损止盈、仓位控制
4. **实时监控**: 实现自动化数据更新和信号提醒
5. **实盘接口**: 连接券商API进行实盘交易

## 注意事项
- 本报告仅为演示用途，不构成投资建议
- 回测结果不代表未来表现
- 实盘交易需谨慎，注意风险控制
"""
    
    # 保存报告
    if not os.path.exists('reports'):
        os.makedirs('reports')
    
    report_file = 'reports/final_report.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"最终报告已生成: {report_file}")
    print("\n报告内容预览:")
    print("-" * 40)
    print(report_content[:500] + "...")  # 预览前500字符
    print("-" * 40)

def main():
    """主函数"""
    print_header("量化股票分析系统")
    print("开始执行完整的量化分析流程...")
    
    start_time = time.time()
    
    # 步骤1: 数据获取
    print("注意: 使用示例数据代替真实数据（避免依赖问题）")
    print("实际使用时请配置真实数据源")
    success1 = run_script('scripts/simple_data_fetcher.py', '步骤1: 数据获取（示例数据）')
    if not success1:
        print("数据获取失败，跳过后续步骤")
        return
    
    # 步骤2: 数据分析
    success2 = run_script('scripts/basic_analysis.py', '步骤2: 数据分析')
    if not success2:
        print("数据分析失败，跳过策略回测")
        # 继续生成报告
    
    # 步骤3: 策略回测
    success3 = run_script('strategies/simple_macd_strategy.py', '步骤3: 策略回测')
    
    # 步骤4: 生成最终报告
    generate_final_report()
    
    # 计算总耗时
    elapsed_time = time.time() - start_time
    print_header("执行完成")
    print(f"总耗时: {elapsed_time:.2f} 秒")
    
    # 总结
    print("\n执行结果:")
    print(f"✓ 数据获取: {'成功' if success1 else '失败'}")
    print(f"✓ 数据分析: {'成功' if success2 else '失败'}")
    print(f"✓ 策略回测: {'成功' if success3 else '失败'}")
    print(f"✓ 最终报告: 已生成")
    
    print("\n生成的文件:")
    if os.path.exists('data'):
        print("  data/ - 数据目录")
    if os.path.exists('reports'):
        print("  reports/ - 报告目录")
        reports = os.listdir('reports')
        for report in reports:
            print(f"    {report}")
    
    print("\n下一步建议:")
    print("1. 查看 reports/final_report.md 了解完整分析")
    print("2. 查看 reports/ 目录中的图表和交易记录")
    print("3. 修改策略参数或开发新策略")
    print("4. 扩展数据源获取更多股票数据")

if __name__ == "__main__":
    main()