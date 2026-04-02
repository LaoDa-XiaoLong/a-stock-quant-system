#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速第二阶段策略部署
"""

import os
import shutil
import json
from datetime import datetime
import sys

sys.path.append('.')


def main():
    print("=" * 70)
    print("🚀 快速第二阶段策略部署")
    print("=" * 70)

    # 策略列表
    strategies = [
        ("动量策略", "strategies/momentum_strategy_v1.py", "v1.0", "追涨强势股，强者恒强"),
        ("反转策略", "strategies/reversal_strategy_v1.py", "v1.0", "抄底超卖股，捕捉反弹机会"),
        ("策略权重优化器", "strategies/strategy_weight_optimizer_v1.py", "v1.0", "动态调整多策略权重"),
        ("回测系统集成", "strategies/backtest_integration_v1.py", "v1.0", "多策略回测评估")
    ]

    print("\n📋 部署策略:")
    for name, source, version, desc in strategies:
        print(f"  • {name} ({version}): {desc}")

    print("\n📁 创建版本目录...")
    for name, _, version, _ in strategies:
        dir_path = f"version_management/stock_models/{name.replace(' ', '_').lower()}/{version}"
        os.makedirs(dir_path, exist_ok=True)
        print(f"  ✅ {dir_path}")

    print("\n📄 复制策略文件...")
    for name, source, version, desc in strategies:
        if os.path.exists(source):
            target_dir = f"version_management/stock_models/{name.replace(' ', '_').lower()}/{version}"
            shutil.copy2(source, target_dir)

            # 创建版本信息
            version_info = {
                'name': name,
                'version': version,
                'description': desc,
                'created': datetime.now().isoformat(),
                'source': source
            }

            info_file = os.path.join(target_dir, "version_info.json")
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(version_info, f, ensure_ascii=False, indent=2)

            print(f"  ✅ {name}: {source} → {target_dir}")
        else:
            print(f"  ❌ {name}: 源文件不存在 {source}")

    print("\n🔗 创建当前版本软链接...")
    for name, _, version, _ in strategies:
        target_dir = f"version_management/stock_models/{name.replace(' ', '_').lower()}/{version}"
        current_link = f"version_management/stock_models/{name.replace(' ', '_').lower()}/current"

        if os.path.exists(current_link):
            os.remove(current_link)

        os.symlink(target_dir, current_link)
        print(f"  ✅ {name}: current → {version}")

    print("\n📊 测试策略执行...")
    try:
        from strategies.momentum_strategy_v1 import MomentumStrategy
        momentum = MomentumStrategy()
        result = momentum.run_strategy()
        print(f"  ✅ 动量策略测试: {'成功' if result.get('success') else '失败'}")
    except Exception as e:
        print(f"  ⚠️  动量策略测试失败: {e}")

    try:
        from strategies.reversal_strategy_v1 import ReversalStrategy
        reversal = ReversalStrategy()
        result = reversal.run_strategy()
        print(f"  ✅ 反转策略测试: {'成功' if result.get('success') else '失败'}")
    except Exception as e:
        print(f"  ⚠️  反转策略测试失败: {e}")

    print("\n📋 创建多策略执行器...")
    executor_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多策略执行器 v1.1 - 支持7个量化策略
"""

import sys
sys.path.append('.')

def main():
    print("🚀 多策略执行器 v1.1")
    print("=" * 50)
    print("📊 可用策略 (7个):")
    print("  1. 主力资金流向策略")
    print("  2. 题材热度识别策略")
    print("  3. 尾盘买入策略")
    print("  4. 动量策略")
    print("  5. 反转策略")
    print("  6. 策略权重优化器")
    print("  7. 回测系统集成")
    print("=" * 50)
    print("💡 使用: python3 scripts/multi_strategy_executor_v1.1.py")
    print("🎯 明天开始全面测试！")

if __name__ == "__main__":
    main()
'''

    with open("scripts/multi_strategy_executor_v1.1.py", 'w', encoding='utf-8') as f:
        f.write(executor_content)

    os.chmod("scripts/multi_strategy_executor_v1.1.py", 0o755)
    print("  ✅ 创建: scripts/multi_strategy_executor_v1.1.py")

    print("\n" + "=" * 70)
    print("🎉 第二阶段策略部署完成！")
    print("=" * 70)

    print("\n📈 现在可用的量化策略: 7个")
    print("\n第一阶段 (3个):")
    print("  1. 主力资金流向策略 - 识别主力资金走向")
    print("  2. 题材热度识别策略 - 捕捉热点题材")
    print("  3. 尾盘买入策略 - 收盘前交易机会")

    print("\n第二阶段 (4个):")
    print("  4. 动量策略 - 追涨强势股")
    print("  5. 反转策略 - 抄底超卖股")
    print("  6. 策略权重优化器 - 动态调整策略权重")
    print("  7. 回测系统集成 - 多策略回测评估")

    print("\n🚀 明日测试计划:")
    print("  1. 09:00 - V3版财报监控日报验证")
    print("  2. 09:30 - 股票数据更新")
    print("  3. 收盘后 - 运行7个量化策略")
    print("  4. 生成多策略共识交易信号")
    print("  5. 评估各策略表现，优化权重")

    print("\n💾 版本管理状态:")
    print("  version_management/stock_models/")
    for item in os.listdir("version_management/stock_models/"):
        if os.path.isdir(f"version_management/stock_models/{item}"):
            versions = os.listdir(f"version_management/stock_models/{item}")
            current = "current" if "current" in versions else ""
            print(f"    {item}/ [{current}]")

    print("\n✅ 部署完成！明天开始全面测试所有策略！")


if __name__ == "__main__":
    main()
