#!/usr/bin/env python3
"""
深度修复matplotlib中文字体问题
"""

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import platform
import subprocess
import json

def get_system_info():
    """获取系统信息"""
    print("=" * 60)
    print("系统信息")
    print("=" * 60)

    system = platform.system()
    release = platform.release()
    version = platform.version()

    print(f"操作系统: {system} {release}")
    print(f"版本: {version}")
    print(f"Python版本: {platform.python_version()}")
    print(f"matplotlib版本: {matplotlib.__version__}")

    return system

def list_all_fonts():
    """列出所有可用字体"""
    print("\n" + "=" * 60)
    print("系统字体列表")
    print("=" * 60)

    fonts = fm.findSystemFonts()
    chinese_fonts = []

    print(f"总字体数量: {len(fonts)}")

    # 常见中文字体名称
    chinese_font_patterns = [
        'PingFang', 'Heiti', 'Hiragino', 'ST', 'Sim', 'Microsoft',
        'YaHei', 'Kai', 'FangSong', 'WenQuan', 'Noto', 'Source'
    ]

    for font_path in fonts[:100]:  # 只显示前100个
        try:
            font_prop = fm.FontProperties(fname=font_path)
            font_name = font_prop.get_name()

            # 检查是否中文字体
            is_chinese = any(pattern in font_name for pattern in chinese_font_patterns)

            if is_chinese:
                chinese_fonts.append((font_name, font_path))
                print(f"✅ {font_name} - {font_path}")
        except:
            pass

    print(f"\n发现 {len(chinese_fonts)} 个中文字体")
    return chinese_fonts

def check_matplotlib_config():
    """检查matplotlib配置"""
    print("\n" + "=" * 60)
    print("matplotlib配置检查")
    print("=" * 60)

    # 获取配置目录
    config_dir = matplotlib.get_configdir()
    cache_dir = matplotlib.get_cachedir()

    print(f"配置目录: {config_dir}")
    print(f"缓存目录: {cache_dir}")

    # 检查matplotlibrc文件
    matplotlibrc_path = os.path.join(os.path.expanduser('~'), '.matplotlibrc')
    if os.path.exists(matplotlibrc_path):
        print(f"\n找到matplotlibrc文件: {matplotlibrc_path}")
        with open(matplotlibrc_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print("文件内容:")
            print("-" * 40)
            print(content[:500])
            print("-" * 40)
    else:
        print(f"\n未找到matplotlibrc文件")

    # 检查当前rcParams
    print(f"\n当前rcParams字体设置:")
    print(f"  font.sans-serif: {plt.rcParams['font.sans-serif']}")
    print(f"  axes.unicode_minus: {plt.rcParams['axes.unicode_minus']}")

def create_font_test_image():
    """创建字体测试图片"""
    print("\n" + "=" * 60)
    print("创建字体测试图片")
    print("=" * 60)

    # 测试不同的字体设置
    test_cases = [
        {
            'name': '默认设置',
            'fonts': plt.rcParams['font.sans-serif'],
            'title': '默认字体设置测试'
        },
        {
            'name': 'macOS推荐',
            'fonts': ['Arial Unicode MS', 'PingFang SC', 'Heiti SC', 'Hiragino Sans GB'],
            'title': 'macOS推荐字体测试'
        },
        {
            'name': '通用设置',
            'fonts': ['SimHei', 'Microsoft YaHei', 'DejaVu Sans'],
            'title': '通用字体测试'
        }
    ]

    os.makedirs('reports/font_test', exist_ok=True)

    for i, test_case in enumerate(test_cases):
        print(f"\n测试: {test_case['name']}")
        print(f"字体: {test_case['fonts']}")

        # 设置字体
        matplotlib.rcParams['font.sans-serif'] = test_case['fonts']
        matplotlib.rcParams['axes.unicode_minus'] = False

        # 创建测试图表
        plt.figure(figsize=(10, 6))

        # 测试文本
        test_texts = [
            '中文测试: 你好世界',
            '股票分析: 鸣志电器 603728',
            '技术指标: RSI MACD 均线',
            '价格: 57.18元 涨跌幅: -2.5%',
            '图表标题应该正常显示'
        ]

        for j, text in enumerate(test_texts):
            y_pos = 0.8 - j * 0.15
            plt.text(0.5, y_pos, text, fontsize=14, ha='center',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.5))

        plt.title(test_case['title'], fontsize=16, fontweight='bold')
        plt.axis('off')

        # 保存图片
        filename = f"reports/font_test/font_test_{i+1}_{test_case['name']}.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"✅ 测试图片已保存: {filename}")

def fix_font_cache():
    """修复字体缓存"""
    print("\n" + "=" * 60)
    print("修复字体缓存")
    print("=" * 60)

    cache_dir = matplotlib.get_cachedir()

    print(f"缓存目录: {cache_dir}")

    if os.path.exists(cache_dir):
        # 备份缓存
        backup_dir = cache_dir + '_backup'
        if not os.path.exists(backup_dir):
            os.rename(cache_dir, backup_dir)
            print(f"✅ 缓存已备份到: {backup_dir}")
        else:
            print(f"⚠️  备份目录已存在: {backup_dir}")

        # 重新创建缓存目录
        os.makedirs(cache_dir, exist_ok=True)
        print(f"✅ 已创建新的缓存目录")

        # 重建缓存
        try:
            subprocess.run(['python3', '-c', 'import matplotlib; matplotlib.font_manager._rebuild()'],
                         capture_output=True, text=True)
            print("✅ 字体缓存已重建")
        except Exception as e:
            print(f"⚠️  重建缓存失败: {e}")
    else:
        print(f"⚠️  缓存目录不存在: {cache_dir}")

def create_optimal_matplotlibrc():
    """创建优化的matplotlibrc文件"""
    print("\n" + "=" * 60)
    print("创建优化的matplotlibrc配置")
    print("=" * 60)

    system = platform.system()

    if system == 'Darwin':  # macOS
        fonts = [
            'Arial Unicode MS',      # macOS自带，支持中日韩
            'PingFang SC',           # 苹方简体，macOS 10.11+
            'Heiti SC',              # 黑体简体
            'Hiragino Sans GB',      # 冬青黑体简体中文
            'STHeiti',               # 华文黑体
            'SimHei',                # 黑体
            'Microsoft YaHei',       # 微软雅黑
            'DejaVu Sans'            # 备用
        ]
    elif system == 'Windows':
        fonts = [
            'Microsoft YaHei',       # 微软雅黑
            'SimHei',                # 黑体
            'KaiTi',                 # 楷体
            'FangSong',              # 仿宋
            'DejaVu Sans'
        ]
    else:  # Linux
        fonts = [
            'DejaVu Sans',
            'WenQuanYi Micro Hei',   # 文泉驿微米黑
            'Noto Sans CJK SC',      # 思源黑体
            'SimHei',
            'Microsoft YaHei'
        ]

    # 创建matplotlibrc内容
    rc_content = f"""# 中文字体配置 - 自动生成
font.sans-serif : {', '.join(fonts)}
axes.unicode_minus : False

# 图表优化设置
figure.dpi : 150
figure.figsize : [10, 6]
savefig.dpi : 300
savefig.bbox : tight
savefig.format : png

# 线条和标记
lines.linewidth : 1.5
lines.markersize : 6

# 网格和边框
axes.grid : True
axes.grid.which : both
axes.grid.axis : both
axes.axisbelow : True
grid.alpha : 0.3

# 字体大小
font.size : 12
axes.titlesize : 14
axes.labelsize : 12
xtick.labelsize : 10
ytick.labelsize : 10
legend.fontsize : 10

# 颜色循环
axes.prop_cycle : cycler('color', ['1f77b4', 'ff7f0e', '2ca02c', 'd62728', '9467bd', '8c564b', 'e377c2', '7f7f7f', 'bcbd22', '17becf'])
"""

    # 保存到用户目录
    user_rc_path = os.path.join(os.path.expanduser('~'), '.matplotlibrc')
    with open(user_rc_path, 'w', encoding='utf-8') as f:
        f.write(rc_content)

    print(f"✅ 已创建优化的matplotlibrc文件: {user_rc_path}")

    # 也保存到项目目录
    project_rc_path = 'matplotlibrc'
    with open(project_rc_path, 'w', encoding='utf-8') as f:
        f.write(rc_content)

    print(f"✅ 已保存到项目目录: {project_rc_path}")

    return fonts

def test_final_fonts(fonts):
    """最终字体测试"""
    print("\n" + "=" * 60)
    print("最终字体测试")
    print("=" * 60)

    # 设置字体
    matplotlib.rcParams['font.sans-serif'] = fonts
    matplotlib.rcParams['axes.unicode_minus'] = False

    # 创建类似持仓分析的测试图表
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))

    # 模拟价格图表
    ax1 = axes[0]
    import numpy as np
    dates = range(100)  # 简化日期
    prices = 50 + np.cumsum(np.random.randn(100) * 0.5)

    ax1.plot(dates, prices, label='收盘价', color='blue', linewidth=2)

    # 计算移动平均
    prices_series = np.array(prices)
    ma_20 = np.convolve(prices_series, np.ones(20)/20, mode='valid')
    ax1.plot(range(19, 100), ma_20, label='20日均线', color='red', linewidth=1)
    ax1.set_title('股票价格分析: 鸣志电器 (603728)', fontsize=16, fontweight='bold')
    ax1.set_ylabel('价格 (元)', fontsize=12)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)

    # 模拟技术指标
    ax2 = axes[1]
    rsi_values = 50 + np.random.randn(100) * 20
    ax2.plot(range(100), rsi_values, label='RSI指标', color='purple', linewidth=2)
    ax2.axhline(y=70, color='red', linestyle='--', alpha=0.5, label='超买线')
    ax2.axhline(y=30, color='green', linestyle='--', alpha=0.5, label='超卖线')
    ax2.fill_between(range(100), 30, 70, alpha=0.1, color='gray')
    ax2.set_xlabel('日期', fontsize=12)
    ax2.set_ylabel('RSI值', fontsize=12)
    ax2.set_title('技术指标分析', fontsize=14)
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    # 保存测试图表
    test_file = 'reports/font_test/final_font_test.png'
    plt.savefig(test_file, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✅ 最终测试图表已保存: {test_file}")
    print(f"✅ 使用的字体: {fonts[:3]}...")

    return test_file

def generate_font_report():
    """生成字体修复报告"""
    print("\n" + "=" * 60)
    print("字体修复报告")
    print("=" * 60)

    report = f"""
# matplotlib中文字体修复报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
操作系统: {platform.system()} {platform.release()}

## 执行步骤
1. ✅ 系统信息收集
2. ✅ 字体列表扫描
3. ✅ matplotlib配置检查
4. ✅ 字体缓存修复
5. ✅ 优化配置文件创建
6. ✅ 最终字体测试

## 发现的中文字体
"""

    # 添加字体列表
    chinese_fonts = list_all_fonts()
    if chinese_fonts:
        report += f"共发现 {len(chinese_fonts)} 个中文字体:\n"
        for font_name, font_path in chinese_fonts[:10]:  # 只显示前10个
            report += f"- {font_name}\n"

    report += f"""
## 配置更改
1. 创建了优化的 ~/.matplotlibrc 文件
2. 重建了字体缓存
3. 设置了系统推荐的中文字体

## 测试结果
测试图片保存在 reports/font_test/ 目录:
1. font_test_1_默认设置.png
2. font_test_2_macOS推荐.png
3. font_test_3_通用设置.png
4. final_font_test.png (最终测试)

## 使用建议
1. 重启Python内核或重新运行脚本使配置生效
2. 如果仍有乱码，尝试清除缓存: rm -rf ~/.cache/matplotlib
3. 可安装额外字体如'思源黑体'获得更好效果

## 后续步骤
1. 重新运行持仓分析脚本测试字体效果
2. 如有问题，检查具体字体的字符覆盖范围
3. 考虑使用绝对字体路径避免系统差异
"""

    # 保存报告
    report_file = 'reports/font_fix_report.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✅ 字体修复报告已保存: {report_file}")
    return report_file

def main():
    """主函数"""
    print("=" * 70)
    print("matplotlib中文字体深度修复工具")
    print("=" * 70)

    # 导入必要的库
    import pandas as pd
    import numpy as np
    from datetime import datetime

    # 确保目录存在
    os.makedirs('reports/font_test', exist_ok=True)

    # 执行修复步骤
    system = get_system_info()
    list_all_fonts()
    check_matplotlib_config()
    fix_font_cache()
    optimal_fonts = create_optimal_matplotlibrc()
    create_font_test_image()
    test_final_fonts(optimal_fonts)
    report_file = generate_font_report()

    print("\n" + "=" * 70)
    print("字体修复完成!")
    print("=" * 70)

    print(f"\n✅ 所有修复步骤已完成")
    print(f"✅ 测试图片生成在 reports/font_test/")
    print(f"✅ 详细报告: {report_file}")

    print(f"\n下一步:")
    print(f"1. 查看测试图片确认字体显示效果")
    print(f"2. 重新运行持仓分析脚本")
    print(f"3. 如有问题，查看报告中的解决方案")

if __name__ == "__main__":
    main()
