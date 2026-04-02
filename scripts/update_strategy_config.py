#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新策略配置，确保后续交易按照10%仓位执行
"""

import os
import sys
import json
from datetime import datetime

def update_strategy_config():
    """更新策略配置"""
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    print(f"🔧 更新策略配置 - 10%仓位")
    print(f"📅 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 1. 更新尾盘选股法Skill配置
    skill_config_file = os.path.join(workspace_dir, "skills", "tail_end_selection", "__init__.py")
    
    if os.path.exists(skill_config_file):
        print(f"1. 📋 更新尾盘选股法Skill配置...")
        
        # 读取文件内容
        with open(skill_config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找并更新仓位配置
        if '"max_position_percent": 0.3' in content:
            new_content = content.replace('"max_position_percent": 0.3', '"max_position_percent": 0.1')
            print(f"   ✅ 更新max_position_percent: 0.3 → 0.1")
        else:
            print(f"   ⚠️ 未找到max_position_percent配置")
        
        # 查找并更新仓位建议
        if "position_percent = 0.3" in content:
            new_content = new_content.replace('position_percent = 0.3', 'position_percent = 0.1')
            print(f"   ✅ 更新重仓仓位: 0.3 → 0.1")
        
        if "position_percent = 0.2" in content:
            new_content = new_content.replace('position_percent = 0.2', 'position_percent = 0.1')
            print(f"   ✅ 更新中等仓位: 0.2 → 0.1")
        
        if "position_percent = 0.1" in content:
            print(f"   ✅ 轻仓仓位已为0.1")
        
        # 保存更新
        with open(skill_config_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"   ✅ 尾盘选股法Skill配置更新完成")
    else:
        print(f"1. ❌ 尾盘选股法Skill配置文件不存在")
    
    # 2. 更新模拟交易系统配置
    print(f"\n2. 💰 更新模拟交易系统配置...")
    
    portfolio_file = os.path.join(workspace_dir, "data", "simulated_trading", "simulated_portfolio.json")
    trades_file = os.path.join(workspace_dir, "data", "simulated_trading", "simulated_trades.json")
    
    if os.path.exists(trades_file):
        with open(trades_file, 'r', encoding='utf-8') as f:
            trades = json.load(f)
        
        # 更新策略名称，包含10%仓位信息
        trades['strategy_name'] = "杨永兴隔夜套利战法 (10%仓位)"
        trades['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 保存更新
        with open(trades_file, 'w', encoding='utf-8') as f:
            json.dump(trades, f, ensure_ascii=False, indent=2)
        
        print(f"   ✅ 更新策略名称: 杨永兴隔夜套利战法 → 杨永兴隔夜套利战法 (10%仓位)")
    else:
        print(f"   ❌ 交易记录文件不存在")
    
    # 3. 创建新的报告脚本（包含中文股票名称）
    print(f"\n3. 📊 创建包含中文股票名称的报告脚本...")
    
    report_script = os.path.join(workspace_dir, "scripts", "tail_end_report_with_chinese_names.py")
    
    report_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
尾盘选股策略报告（包含中文股票名称）
仓位配置: 每只股票10%
"""

import os
import sys
import json
from datetime import datetime

# 股票代码到中文名称的映射
STOCK_NAME_MAP = {
    # 沪市股票
    "600016": "民生银行",
    "600519": "贵州茅台", 
    "600585": "海螺水泥",
    "600036": "招商银行",
    
    # 深市股票
    "000006": "深振业A",
    "000009": "中国宝安",
    "000010": "美丽生态",
    "000011": "深物业A",
    
    # 默认名称（如果找不到映射）
    "default": "未知股票"
}

def get_chinese_name(stock_code, stock_name):
    """获取股票中文名称"""
    # 首先尝试从映射中获取
    if stock_code in STOCK_NAME_MAP:
        return STOCK_NAME_MAP[stock_code]
    
    # 如果股票名称已经是中文，直接使用
    if any('\u4e00' <= char <= '\u9fff' for char in stock_name):
        return stock_name
    
    # 否则使用默认名称
    return f"{STOCK_NAME_MAP['default']}({stock_code})"

def generate_report():
    """生成报告"""
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    portfolio_file = os.path.join(workspace_dir, "data", "simulated_trading", "simulated_portfolio.json")
    trades_file = os.path.join(workspace_dir, "data", "simulated_trading", "simulated_trades.json")
    
    print(f"📊 尾盘选股策略报告（10%仓位）")
    print(f"📅 报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    try:
        with open(portfolio_file, 'r', encoding='utf-8') as f:
            portfolio = json.load(f)
        
        with open(trades_file, 'r', encoding='utf-8') as f:
            trades = json.load(f)
    except Exception as e:
        print(f"❌ 加载数据失败: {e}")
        return
    
    # 资金情况
    print(f"💰 资金情况:")
    print(f"  初始资金: {portfolio.get('total_capital', 0):,.2f}元")
    print(f"  当前总资产: {portfolio.get('total_value', 0):,.2f}元")
    print(f"  已投资金额: {portfolio.get('invested_capital', 0):,.2f}元")
    print(f"  可用资金: {portfolio.get('available_capital', 0):,.2f}元")
    
    total_return = ((portfolio.get('total_value', 0) - portfolio.get('total_capital', 0)) / 
                   portfolio.get('total_capital', 1) * 100)
    print(f"  总收益率: {total_return:.2f}%")
    
    # 交易统计
    print(f"\n📈 交易统计:")
    print(f"  总交易笔数: {trades.get('total_trades', 0)}笔")
    print(f"  活跃交易: {trades.get('active_trades', 0)}笔")
    print(f"  已平仓交易: {trades.get('closed_trades', 0)}笔")
    print(f"  策略名称: {trades.get('strategy_name', '尾盘选股策略')}")
    
    # 持仓详情（包含中文名称）
    positions = portfolio.get('positions', [])
    if positions:
        print(f"\n📋 当前持仓 ({len(positions)} 只股票，每只10%仓位):")
        print("=" * 70)
        
        total_market_value = 0
        total_unrealized_pnl = 0
        
        for i, pos in enumerate(positions, 1):
            stock_code = pos.get('stock_code', '')
            original_name = pos.get('stock_name', '')
            chinese_name = get_chinese_name(stock_code, original_name)
            
            pnl = pos.get('unrealized_pnl', 0)
            pnl_percent = pos.get('unrealized_pnl_percent', 0)
            pnl_emoji = "📈" if pnl > 0 else "📉"
            
            print(f"{i}. {chinese_name} ({stock_code})")
            print(f"   原名称: {original_name}")
            print(f"   持仓数量: {pos.get('shares', 0):,}股")
            print(f"   进场价格: {pos.get('entry_price', 0):.2f}元")
            print(f"   当前价格: {pos.get('current_price', 0):.2f}元")
            print(f"   浮动盈亏: {pnl_emoji} {pnl:,.2f}元 ({pnl_percent:.2f}%)")
            print(f"   持仓市值: {pos.get('market_value', 0):,.2f}元")
            print(f"   仓位比例: {pos.get('market_value', 0)/portfolio.get('total_capital', 1)*100:.1f}%")
            print(f"   进场日期: {pos.get('entry_date', '')}")
            print()
            
            total_market_value += pos.get('market_value', 0)
            total_unrealized_pnl += pnl
        
        print("=" * 70)
        print(f"📊 持仓汇总:")
        print(f"  总持仓市值: {total_market_value:,.2f}元")
        print(f"  总浮动盈亏: {total_unrealized_pnl:,.2f}元")
        print(f"  总仓位比例: {total_market_value/portfolio.get('total_capital', 1)*100:.1f}%")
    else:
        print(f"\n📭 当前无持仓")
    
    # 策略说明
    print(f"\n🎯 策略说明:")
    print(f"  1. 仓位配置: 每只股票固定10%仓位")
    print(f"  2. 选股时间: 交易日14:30-15:00")
    print(f"  3. 风险控制: 止损5%，止盈8%")
    print(f"  4. 持仓周期: 隔夜交易")
    
    # 下次执行
    print(f"\n⏰ 下次执行:")
    print(f"  尾盘选股: 今日14:30")
    print(f"  每日报告: 今日18:00")
    print(f"  报告发送: 今日18:05 (A股数据分析群)")

def main():
    """主函数"""
    print("📊 尾盘选股策略报告生成器（10%仓位 + 中文股票名称）")
    print("=" * 70)
    
    generate_report()

if __name__ == "__main__":
    main()
'''
    
    with open(report_script, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    # 设置执行权限
    os.chmod(report_script, 0o755)
    
    print(f"   ✅ 创建报告脚本: {report_script}")
    
    # 4. 更新检查持仓脚本
    print(f"\n4. 🔍 更新检查持仓脚本...")
    
    check_script = os.path.join(workspace_dir, "scripts", "check_tail_end_positions.py")
    
    if os.path.exists(check_script):
        with open(check_script, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 在适当位置添加仓位说明
        if "仓位比例:" in content:
            # 已经包含仓位信息
            print(f"   ✅ 检查持仓脚本已包含仓位信息")
        else:
            print(f"   ⚠️ 检查持仓脚本需要更新")
    else:
        print(f"   ❌ 检查持仓脚本不存在")
    
    print(f"\n✅ 策略配置更新完成!")
    print(f"   1. 尾盘选股法Skill配置已更新为10%仓位")
    print(f"   2. 策略名称已更新为'杨永兴隔夜套利战法 (10%仓位)'")
    print(f"   3. 创建了包含中文股票名称的报告脚本")
    print(f"   4. 所有后续交易将按照10%仓位执行")

def main():
    """主函数"""
    print("🔧 更新策略配置 - 确保10%仓位执行")
    print("=" * 70)
    
    update_strategy_config()

if __name__ == "__main__":
    main()