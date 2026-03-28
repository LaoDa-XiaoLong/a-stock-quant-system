#!/usr/bin/env python3
"""
修复matplotlib中文字体显示问题
"""

import matplotlib
import matplotlib.pyplot as plt
import os
import platform

def check_and_fix_chinese_font():
    """检查和修复中文字体显示问题"""
    print("=" * 50)
    print("检查并修复matplotlib中文字体显示")
    print("=" * 50)
    
    # 检查当前系统
    system = platform.system()
    print(f"操作系统: {system}")
    
    # 获取matplotlib配置目录
    config_dir = matplotlib.get_configdir()
    print(f"matplotlib配置目录: {config_dir}")
    
    # 获取字体缓存目录
    cache_dir = matplotlib.get_cachedir()
    print(f"字体缓存目录: {cache_dir}")
    
    # 检查当前字体设置
    rc_params = plt.rcParams
    print(f"\n当前字体设置:")
    print(f"  font.sans-serif: {rc_params['font.sans-serif']}")
    print(f"  axes.unicode_minus: {rc_params['axes.unicode_minus']}")
    
    # 设置中文字体
    if system == 'Darwin':  # macOS
        # macOS系统字体
        font_names = [
            'Arial Unicode MS',  # macOS自带
            'PingFang SC',       # 苹方简体
            'Heiti SC',          # 黑体简体
            'Hiragino Sans GB',  # 冬青黑体简体中文
            'STHeiti',           # 华文黑体
            'SimHei',            # 黑体
            'Microsoft YaHei',   # 微软雅黑
            'DejaVu Sans'        # 备用
        ]
    elif system == 'Windows':
        # Windows系统字体
        font_names = [
            'Microsoft YaHei',   # 微软雅黑
            'SimHei',            # 黑体
            'KaiTi',             # 楷体
            'FangSong',          # 仿宋
            'DejaVu Sans'
        ]
    else:  # Linux
        # Linux系统字体
        font_names = [
            'DejaVu Sans',
            'WenQuanYi Micro Hei',  # 文泉驿微米黑
            'Noto Sans CJK SC',     # 思源黑体
            'SimHei',
            'Microsoft YaHei'
        ]
    
    # 更新matplotlib配置
    matplotlib.rcParams['font.sans-serif'] = font_names
    matplotlib.rcParams['axes.unicode_minus'] = False
    
    print(f"\n已更新字体设置:")
    print(f"  font.sans-serif: {matplotlib.rcParams['font.sans-serif']}")
    print(f"  axes.unicode_minus: {matplotlib.rcParams['axes.unicode_minus']}")
    
    # 创建matplotlibrc文件
    matplotlibrc_path = os.path.join(os.path.expanduser('~'), '.matplotlibrc')
    
    rc_content = f"""# 中文字体配置
font.sans-serif : {', '.join(font_names)}
axes.unicode_minus : False

# 其他优化设置
figure.dpi : 150
figure.figsize : [10, 6]
savefig.dpi : 300
savefig.bbox : tight
savefig.format : png
"""
    
    try:
        with open(matplotlibrc_path, 'w', encoding='utf-8') as f:
            f.write(rc_content)
        print(f"\n已创建配置文件: {matplotlibrc_path}")
    except Exception as e:
        print(f"创建配置文件失败: {e}")
    
    # 测试字体显示
    print("\n测试字体显示...")
    try:
        plt.figure(figsize=(8, 4))
        plt.text(0.5, 0.5, '中文字体测试: 你好世界', 
                fontsize=20, ha='center', va='center')
        plt.axis('off')
        
        # 保存测试图片
        test_dir = 'reports'
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)
        
        test_file = os.path.join(test_dir, 'chinese_font_test.png')
        plt.savefig(test_file, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"字体测试图片已保存: {test_file}")
        print("如果图片中的中文显示正常，则字体问题已解决")
        
    except Exception as e:
        print(f"字体测试失败: {e}")
    
    print("\n" + "=" * 50)
    print("字体修复完成")
    print("=" * 50)
    print("\n如果仍有乱码问题，请尝试:")
    print("1. 重启Python内核或重新运行脚本")
    print("2. 清除matplotlib缓存: rm -rf ~/.cache/matplotlib")
    print("3. 安装额外中文字体包")

def install_additional_fonts():
    """安装额外中文字体（如果需要）"""
    system = platform.system()
    
    print("\n" + "=" * 50)
    print("中文字体安装建议")
    print("=" * 50)
    
    if system == 'Darwin':  # macOS
        print("macOS系统建议:")
        print("1. 系统已自带多种中文字体")
        print("2. 可安装'思源黑体'获得更好效果")
        print("3. 下载地址: https://github.com/adobe-fonts/source-han-sans")
        
    elif system == 'Windows':
        print("Windows系统建议:")
        print("1. 系统已包含微软雅黑等中文字体")
        print("2. 可安装'思源黑体'或'方正字库'")
        
    else:  # Linux
        print("Linux系统建议:")
        print("1. 安装文泉驿字体:")
        print("   Ubuntu/Debian: sudo apt-get install fonts-wqy-microhei")
        print("   CentOS/RHEL: sudo yum install wqy-microhei-fonts")
        print("2. 或安装思源黑体:")
        print("   sudo apt-get install fonts-noto-cjk")
    
    print("\n安装后需要清除matplotlib缓存:")
    print("  rm -rf ~/.cache/matplotlib")

if __name__ == "__main__":
    check_and_fix_chinese_font()
    install_additional_fonts()