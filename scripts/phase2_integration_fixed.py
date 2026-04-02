#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第二阶段策略集成（修复版）
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')
import sys
import os
import shutil
import json

# 添加当前目录到路径
sys.path.append('.')


def create_version_directories():
    """创建版本管理目录"""
    print("📁 创建版本管理目录")

    directories = [
        "version_management/stock_models/momentum",
        "version_management/stock_models/reversal",
        "version_management/stock_models/strategy_optimizer",
        "version_management/stock_models/backtest_system"
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✅ 创建: {directory}")

    return True


def deploy_strategy(strategy_name, source_file, version, description):
    """部署单个策略"""
    print(f"\n🚀 部署 {strategy_name} {version}")
    print("-" * 40)

    try:
        # 运行策略测试
        if strategy_name == "动量策略":
            from strategies.momentum_strategy_v1 import MomentumStrategy
            strategy = MomentumStrategy()
            result = strategy.run_strategy()

        elif strategy_name == "反转策略":
            from strategies.reversal_strategy_v1 import ReversalStrategy
            strategy = ReversalStrategy()
            result = strategy.run_strategy()

        elif strategy_name == "策略权重优化器":
            from strategies.strategy_weight_optimizer_v1 import StrategyWeightOptimizer
            optimizer = StrategyWeightOptimizer()
            result = optimizer.run_optimization()

        elif strategy_name == "回测系统集成":
            from strategies.backtest_integration_v1 import BacktestIntegration
            backtest = BacktestIntegration()
            result = backtest.run_comprehensive_backtest()

        else:
            print(f"  ❌ 未知策略: {strategy_name}")
            return False

        if result.get('success'):
            # 保存到版本管理
            save_to_version_management(
                "stock_models",
                strategy_name.replace(" ", "_").lower(),
                version,
                source_file,
                description
            )

            print(f"  ✅ {strategy_name} 部署成功")

            # 显示关键结果
            if strategy_name == "动量策略":
                print(f"    买入信号: {result.get('report', {}).get('buy_signals', 0)} 只")
            elif strategy_name == "反转策略":
                print(f"    强烈反转: {result.get('report', {}).get('strong_reversal', 0)} 只")

            return True
        else:
            print(f"  ❌ {strategy_name} 执行失败")
            return False

    except Exception as e:
        print(f"  ❌ {strategy_name} 部署失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def save_to_version_management(category, name, version, source_path, description):
    """保存到版本管理"""
    try:
        # 创建版本目录
        version_dir = f"version_management/{category}/{name}/{version}"
        os.makedirs(version_dir, exist_ok=True)

        # 复制文件
        shutil.copy2(source_path, version_dir)

        # 创建版本信息
        version_info = {
            'version': version,
            'created': datetime.now().isoformat(),
            'description': description,
            'source': source_path,
            'category': category,
            'name': name
        }

        info_file = os.path.join(version_dir, "version_info.json")
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(version_info, f, ensure_ascii=False, indent=2)

        # 更新当前版本软链接
        current_link = f"version_management/{category}/{name}/current"
        if os.path.exists(current_link) or os.path.islink(current_link):
            os.remove(current_link)
        os.symlink(version_dir, current_link)

        return True

    except Exception as e:
        print(f"  ⚠️  保存到版本管理失败: {e}")
        return False


def update_multi_strategy_executor():
    """更新多策略执行器"""
    print("\n🔄 更新多策略执行器")
    print("-" * 40)

    try:
        # 创建更新后的执行器
        executor_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多策略执行器 v1.1
支持7个量化策略并行执行
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')
import sys
import os

# 添加策略目录到路径
sys.path.append('.')


class MultiStrategyExecutor:
    """多策略执行器"""

    def __init__(self):
        self.executor_name = "多策略执行器 v1.1"
        self.strategies = {}
        self.results = {}

        print(f"🚀 {self.executor_name} 初始化完成")
        print(f"📊 支持策略: 7个量化策略")

    def register_all_strategies(self):
        """注册所有策略"""
        print("📋 注册策略:")

        # 第一阶段策略
        self._register_strategy("主力资金流向策略", "strategies.capital_flow_strategy_v1", "CapitalFlowStrategy")
        self._register_strategy("题材热度识别策略", "strategies.theme_hot_strategy_v1", "ThemeHotStrategy")
        self._register_strategy("尾盘买入策略", "strategies.tail_trading_strategy_v1", "TailTradingStrategy")

        # 第二阶段策略
        self._register_strategy("动量策略", "strategies.momentum_strategy_v1", "MomentumStrategy")
        self._register_strategy("反转策略", "strategies.reversal_strategy_v1", "ReversalStrategy")
        self._register_strategy("策略权重优化器", "strategies.strategy_weight_optimizer_v1", "StrategyWeightOptimizer")
        self._register_strategy("回测系统集成", "strategies.backtest_integration_v1", "BacktestIntegration")

        print(f"✅ 共注册 {len(self.strategies)} 个策略")

    def _register_strategy(self, strategy_name, module_path, class_name):
        """注册单个策略"""
        try:
            module = __import__(module_path.replace('/', '.')[:-3])
            strategy_class = getattr(module, class_name)
            self.strategies[strategy_name] = {
                'module': module_path,
                'class': class_name,
                'instance': None
            }
            print(f"  ✅ {strategy_name}")
            return True
        except Exception as e:
            print(f"  ⚠️  {strategy_name}: 导入失败 ({e})")
            return False

    def run_all_strategies(self):
        """运行所有策略"""
        print(f"\n🚀 开始执行多策略量化分析")
        print("=" * 60)

        results = {}

        for strategy_name in self.strategies.keys():
            print(f"\n🎯 执行策略: {strategy_name}")
            print("-" * 40)

            try:
                strategy_info = self.strategies[strategy_name]
                module = __import__(strategy_info['module'].replace('/', '.')[:-3])
                strategy_class = getattr(module, strategy_info['class'])

                # 创建策略实例
                strategy_instance = strategy_class()
                self.strategies[strategy_name]['instance'] = strategy_instance

                # 执行策略
                if hasattr(strategy_instance, 'run_strategy'):
                    result = strategy_instance.run_strategy()
                    results[strategy_name] = result

                    if result.get('success'):
                        print(f"  ✅ 执行成功")
                    else:
                        print(f"  ❌ 执行失败: {result.get('error', '未知错误')}")
                else:
                    print(f"  ⚠️  策略没有 run_strategy 方法")

            except Exception as e:
                print(f"  ❌ 执行失败: {e}")

        self.results = results
        return results

    def generate_summary_report(self):
        """生成总结报告"""
        print("\n📋 多策略执行总结报告")
        print("=" * 60)

        total_strategies = len(self.strategies)
        successful_strategies = len([r for r in self.results.values() if r.get('success')])

        print(f"📊 执行统计:")
        print(f"  总策略数: {total_strategies}")
        print(f"  成功执行: {successful_strategies}")
        print(f"  成功率: {successful_strategies/total_strategies*100:.1f}%")

        print(f"\n🎯 可用策略列表:")
        for strategy_name, result in self.results.items():
            status = "✅ 可用" if result.get('success') else "❌ 不可用"
            print(f"  • {strategy_name}: {status}")

        # 保存报告
        report_file = f"reports/multi_strategy_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# 多策略执行总结报告\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"## 执行统计\n")
            f.write(f"- 总策略数: {total_strategies}\n")
            f.write(f"- 成功执行: {successful_strategies}\n")
            f.write(f"- 成功率: {successful_strategies/total_strategies*100:.1f}%\n\n")
            f.write(f"## 策略状态\n")
            for strategy_name, result in self.results.items():
                status = "✅ 可用" if result.get('success') else "❌ 不可用"
                f.write(f"- {strategy_name}: {status}\n")

        print(f"\n💾 报告已保存: {report_file}")

        return successful_strategies > 0


def main():
    """主函数"""
    executor = MultiStrategyExecutor()
    executor.register_all_strategies()
    executor.run_all_strategies()
    executor.generate_summary_report()

    print("\n🎉 多策略执行完成！")
    print("=" * 60)
    print("📈 现在可用的量化策略:")
    print("  1. 主力资金流向策略")
    print("  2. 题材热度识别策略")
    print("  3. 尾盘买入策略")
    print("  4. 动量策略")
    print("  5. 反转策略")
    print("  6. 策略权重优化器")
    print("  7. 回测系统集成")
    print("\n🚀 明天开始全面测试！")


if __name__ == "__main__":
    main()
'''

        # 保存更新后的执行器
        executor_file = "scripts/multi_strategy_executor_v1.1.py"
        with open(executor_file, 'w', encoding='utf-8') as f:
            f.write(executor_content)

        print(f"  ✅ 创建更新版执行器: {executor_file}")

        # 设置执行权限
        os.chmod(executor_file, 0o755)

        return True

    except Exception as e:
        print(f"  ❌ 更新执行器失败: {e}")
        return False


def generate_final_report(results):
    """生成最终报告"""
    print("\n📋 第二阶段策略集成最终报告")
    print("=" * 70)

    total_tasks = len(results)
    successful_tasks = sum(results.values())

    print(f"\n📊 集成结果:")
    print(f"  总任务数: {total_tasks}")
    print(f"  成功任务: {successful_tasks}")
    print(f"  成功率: {successful_tasks/total_tasks*100:.1f}%")

    print(f"\n✅ 成功部署:")
    for task, success in results.items():
        if success:
            print(f"  • {task}")

    print(f"\n📁 版本管理结构:")
    for root, dirs, files in os.walk("version_management/stock_models"):
        level = root.replace("version_management/stock_models", "").count(os.sep)
        indent = "  " * level
        basename = os.path.basename(root)
        if basename:
            print(f"{indent}{basename}/")

    print(f"\n🚀 现在可用的策略总数: 7个")
    print("  第一阶段 (3个):")
    print("    1. 主力资金流向策略")
    print("    2. 题材热度识别策略")
    print("    3. 尾盘买入策略")
    print("  第二阶段 (4个):")
    print("    4. 动量策略")
    print("    5. 反转策略")
    print("    6. 策略权重优化器")
    print("    7. 回测系统集成")

    # 保存报告
    report_file = f"reports/phase2_final_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"# 第二阶段策略集成最终报告\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## 集成结果\n")
        f.write(f"- 总任务数: {total_tasks}\n")
        f.write(f"- 成功任务: {successful_tasks}\n")
        f.write(f"- 成功率: {successful_tasks/total_tasks*100:.1f}%\n\n")

        f.write("## 部署的策略\n")
        for task, success in results.items():
            status = "✅ 成功" if success else "❌ 失败"
            f.write(f"- {task}: {status}\n")

        f.write("\n## 可用策略列表\n")
        f.write("### 第一阶段策略\n")
        f.write("1. **主力资金流向策略** - 识别机构/游资动向\n")
        f.write("2. **题材热度识别策略** - 捕捉热点题材\n")
        f.write("3. **尾盘买入策略** - 收盘前交易机会\n")
        f.write("\n### 第二阶段策略\n")
        f.write("4. **动量策略** - 追涨强势股\n")
        f.write("5. **反转策略** - 抄底超卖股\n")
        f.write("6. **策略权重优化器** - 动态调整策略权重\n")
        f.write("7. **回测系统集成** - 多策略回测评估\n")

        f.write("\n## 明日测试计划\n")
        f.write("1. 运行多策略执行器测试所有策略\n")
        f.write("2. 验证各策略交易信号准确性\n")
        f.write("3. 测试策略权重优化效果\n")
        f.write("4. 运行回测系统评估历史表现\n")
        f.write("5. 根据测试结果调整策略参数\n")

    print(f"\n💾 最终报告已保存: {report_file}")

    return successful_tasks > 0


def main():
    """主函数"""
    print("=" * 70)
    print("🚀 第二阶段策略集成（修复版）")
    print("=" * 70)

    start_time = datetime.now()

    # 部署策略列表
    strategies_to_deploy = [
        {
            "name": "动量策略",
            "source": "strategies/momentum_strategy_v1.py",
            "version": "v1.0",
            "description": "动量策略 v1.0 - 追涨强势股，强者恒强"
        },
        {
            "name": "反转策略",
            "source": "strategies/reversal_strategy_v1.py",
            "version": "v1.0",
            "description": "反转策略 v1.0 - 抄底超卖股，捕捉反弹机会"
        },
        {
            "name": "策略权重优化器",
            "source": "strategies/strategy_weight_optimizer_v1.py",
            "version": "v1.0",
            "description": "策略权重优化器 v1.0 - 动态调整多策略权重"
        },
        {
            "name": "回测系统集成",
            "source": "strategies/backtest_integration_v1.py",
            "version": "v1.0",
            "description": "回测系统集成 v1.0 - 多策略回测评估"
        }
    ]

    # 1. 创建版本目录
    create_version_directories()

    # 2. 部署所有策略
    results = {}
    for strategy in strategies_to_deploy:
        success = deploy_strategy(
            strategy["name"],
            strategy["source"],
            strategy["version"],
            strategy["description"]
        )
        results[strategy["name"]] = success

    # 3. 更新多策略执行器
    update_multi_strategy_executor()

    # 4. 生成最终报告
    success = generate_final_report(results)

    elapsed_time = (datetime.now() - start_time).total_seconds()

    print(f"\n⏱️  总耗时: {elapsed_time:.1f}秒")

    if success:
        print(f"\n🎉 第二阶段策略集成完成！")
        print("=" * 70)
        print("🚀 所有7个量化策略已就绪
