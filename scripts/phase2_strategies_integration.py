#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第二阶段策略集成脚本
一次性部署动量策略、反转策略、权重优化、回测系统
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')
import sys
import os

# 添加策略目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class Phase2StrategiesIntegration:
    """第二阶段策略集成"""

    def __init__(self):
        self.integration_name = "第二阶段策略集成"
        self.start_time = datetime.now()

        print("=" * 70)
        print("🚀 第二阶段策略集成启动")
        print("=" * 70)
        print("🎯 集成内容:")
        print("  1. 📅 动量策略 v1.0")
        print("  2. 📅 反转策略 v1.0")
        print("  3. 📅 策略权重优化 v1.0")
        print("  4. 📅 回测系统集成 v1.0")
        print("=" * 70)

    def create_version_directories(self):
        """创建版本管理目录"""
        print("\n📁 创建版本管理目录")

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

    def deploy_momentum_strategy(self):
        """部署动量策略"""
        print("\n1. 🚀 部署动量策略 v1.0")
        print("-" * 40)

        try:
            # 导入动量策略
            from strategies.momentum_strategy_v1 import MomentumStrategy

            # 创建策略实例
            strategy = MomentumStrategy()

            # 运行策略
            result = strategy.run_strategy()

            if result['success']:
                # 保存到版本管理
                self._save_to_version_management(
                    "stock_models", "momentum", "v1.0",
                    "strategies/momentum_strategy_v1.py",
                    "动量策略 v1.0 - 追涨强势股，强者恒强"
                )

                print(f"  ✅ 动量策略部署成功")
                print(f"    买入信号: {result.get('report', {}).get('buy_signals', 0)} 只")
                print(f"    强势动量: {result.get('report', {}).get('strong_momentum', 0)} 只")

                return True
            else:
                print(f"  ❌ 动量策略执行失败")
                return False

        except Exception as e:
            print(f"  ❌ 动量策略部署失败: {e}")
            return False

    def deploy_reversal_strategy(self):
        """部署反转策略"""
        print("\n2. 🔄 部署反转策略 v1.0")
        print("-" * 40)

        try:
            # 导入反转策略
            from strategies.reversal_strategy_v1 import ReversalStrategy

            # 创建策略实例
            strategy = ReversalStrategy()

            # 运行策略
            result = strategy.run_strategy()

            if result['success']:
                # 保存到版本管理
                self._save_to_version_management(
                    "stock_models", "reversal", "v1.0",
                    "strategies/reversal_strategy_v1.py",
                    "反转策略 v1.0 - 抄底超卖股，捕捉反弹机会"
                )

                print(f"  ✅ 反转策略部署成功")
                print(f"    买入信号: {result.get('report', {}).get('buy_signals', 0)} 只")
                print(f"    强烈反转: {result.get('report', {}).get('strong_reversal', 0)} 只")

                return True
            else:
                print(f"  ❌ 反转策略执行失败")
                return False

        except Exception as e:
            print(f"  ❌ 反转策略部署失败: {e}")
            return False

    def deploy_weight_optimizer(self):
        """部署策略权重优化器"""
        print("\n3. ⚖️ 部署策略权重优化器 v1.0")
        print("-" * 40)

        try:
            # 导入权重优化器
            from strategies.strategy_weight_optimizer_v1 import StrategyWeightOptimizer

            # 创建优化器实例
            optimizer = StrategyWeightOptimizer()

            # 运行优化
            result = optimizer.run_optimization()

            if result['success']:
                # 保存到版本管理
                self._save_to_version_management(
                    "stock_models", "strategy_optimizer", "v1.0",
                    "strategies/strategy_weight_optimizer_v1.py",
                    "策略权重优化器 v1.0 - 动态调整多策略权重"
                )

                print(f"  ✅ 权重优化器部署成功")

                # 显示优化结果
                recommendations = result.get('weight_recommendations')
                if recommendations is not None:
                    print(f"    优化策略数: {len(recommendations)} 个")
                    print(f"    权重调整: {result.get('report', {}).get('weight_adjustments', 0)} 个")

                return True
            else:
                print(f"  ❌ 权重优化器执行失败")
                return False

        except Exception as e:
            print(f"  ❌ 权重优化器部署失败: {e}")
            return False

    def deploy_backtest_system(self):
        """部署回测系统"""
        print("\n4. 📊 部署回测系统集成 v1.0")
        print("-" * 40)

        try:
            # 导入回测系统
            from strategies.backtest_integration_v1 import BacktestIntegration

            # 创建回测实例
            backtest = BacktestIntegration()

            # 运行回测
            result = backtest.run_comprehensive_backtest()

            if result['success']:
                # 保存到版本管理
                self._save_to_version_management(
                    "stock_models", "backtest_system", "v1.0",
                    "strategies/backtest_integration_v1.py",
                    "回测系统集成 v1.0 - 多策略回测评估"
                )

                print(f"  ✅ 回测系统部署成功")

                # 显示回测结果
                comparison_df = result.get('comparison_df')
                if comparison_df is not None:
                    best_strategy = comparison_df.iloc[0]
                    print(f"    最佳策略: {best_strategy['strategy']}")
                    print(f"    夏普比率: {best_strategy['sharpe_ratio']:.2f}")
                    print(f"    年化收益: {best_strategy['annual_return']}")

                return True
            else:
                print(f"  ❌ 回测系统执行失败")
                return False

        except Exception as e:
            print(f"  ❌ 回测系统部署失败: {e}")
            return False

    def _save_to_version_management(self, category, name, version, source_path, description):
        """保存到版本管理"""
        try:
            # 创建版本目录
            version_dir = f"version_management/{category}/{name}/{version}"
            os.makedirs(version_dir, exist_ok=True)

            # 复制文件
            import shutil
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
            import json
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

    def update_multi_strategy_executor(self):
        """更新多策略执行器"""
        print("\n5. 🔄 更新多策略执行器")
        print("-" * 40)

        try:
            # 读取当前执行器
            executor_file = "scripts/multi_strategy_executor.py"
            with open(executor_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查是否已包含新策略
            new_strategies = ["动量策略", "反转策略"]
            missing_strategies = []

            for strategy in new_strategies:
                if strategy not in content:
                    missing_strategies.append(strategy)

            if missing_strategies:
                print(f"  ⚠️  需要手动添加策略: {', '.join(missing_strategies)}")
                print(f"    请更新 {executor_file} 文件")
            else:
                print(f"  ✅ 多策略执行器已包含新策略")

            return True

        except Exception as e:
            print(f"  ⚠️  更新执行器检查失败: {e}")
            return False

    def generate_integration_report(self, results):
        """生成集成报告"""
        print("\n📋 第二阶段策略集成报告")
        print("=" * 70)

        total_tasks = 4
        successful_tasks = sum(results.values())

        print(f"\n📊 集成结果统计:")
        print(f"  总任务数: {total_tasks}")
        print(f"  成功任务: {successful_tasks}")
        print(f"  成功率: {successful_tasks/total_tasks*100:.1f}%")

        print(f"\n✅ 成功部署的策略:")
        for task, success in results.items():
            if success:
                print(f"  • {task}")

        print(f"\n📁 创建的版本目录:")
        import os
        for root, dirs, files in os.walk("version_management"):
            level = root.replace("version_management", "").count(os.sep)
            indent = "  " * level
            print(f"{indent}{os.path.basename(root)}/")

        print(f"\n⏱️  集成耗时: {(datetime.now() - self.start_time).total_seconds():.1f}秒")

        # 保存报告
        report_file = f"reports/phase2_integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(f"# 第二阶段策略集成报告\n")
                f.write(f"集成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"集成耗时: {(datetime.now() - self.start_time).total_seconds():.1f}秒\n\n")

                f.write("## 集成结果\n")
                f.write(f"- 总任务数: {total_tasks}\n")
                f.write(f"- 成功任务: {successful_tasks}\n")
                f.write(f"- 成功率: {successful_tasks/total_tasks*100:.1f}%\n\n")

                f.write("## 部署的策略\n")
                for task, success in results.items():
                    status = "✅ 成功" if success else "❌ 失败"
                    f.write(f"- {task}: {status}\n")

                f.write("\n## 版本管理状态\n")
                f.write("```\n")
                for root, dirs, files in os.walk("version_management"):
                    level = root.replace("version_management", "").count(os.sep)
                    indent = "  " * level
                    f.write(f"{indent}{os.path.basename(root)}/\n")
                f.write("```\n")

                f.write("\n## 下一步行动\n")
                f.write("1. 测试新策略的实际表现\n")
                f.write("2. 更新多策略执行器注册新策略\n")
                f.write("3. 配置调度任务定期运行新策略\n")
                f.write("4. 监控策略表现，持续优化\n")

            print(f"\n💾 集成报告已保存: {report_file}")

        except Exception as e:
            print(f"  ❌ 保存报告失败: {e}")

        return successful_tasks == total_tasks

    def run_integration(self):
        """运行集成"""
        print(f"\n🚀 开始第二阶段策略集成")
        print("=" * 70)

        results = {}

        try:
            # 1. 创建版本目录
            self.create_version_directories()

            # 2. 部署动量策略
            results['动量策略'] = self.deploy_momentum_strategy()

            # 3. 部署反转策略
            results['反转策略'] = self.deploy_reversal_strategy()

            # 4. 部署权重优化器
            results['权重优化器'] = self.deploy_weight_optimizer()

            # 5. 部署回测系统
            results['回测系统'] = self.deploy_backtest_system()

            # 6. 更新多策略执行器
            self.update_multi_strategy_executor()

            # 7. 生成集成报告
            success = self.generate_integration_report(results)

            if success:
                print(f"\n🎉 第二阶段策略集成完成！")
                print("=" * 70)

                print(f"\n📈 现在可用的策略总数: 7个")
                print("  第一阶段 (3个):")
                print("    1. 主力资金流向策略")
                print("    2. 题材热度识别策略")
                print("    3. 尾盘买入策略")
                print("  第二阶段 (4个):")
                print("    4. 动量策略")
                print("    5. 反转策略")
                print("    6. 策略权重优化器")
                print("    7. 回测系统集成")

                print(f"\n🚀 明日即可测试所有策略！")

            else:
                print(f"\n⚠️  第二阶段策略集成部分完成")
                print("=" * 70)

            return success

        except Exception as e:
            print(f"\n❌ 集成过程出错: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """主函数"""
    integrator = Phase2StrategiesIntegration()
    success = integrator.run_integration()

    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
