#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试杨永兴战法
"""

import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.yang_yongxing_fixed import YangYongxingOvernightStrategy

def main():
    print("测试杨永兴隔夜套利战法")
    print("=" * 60)
    
    strategy = YangYongxingOvernightStrategy()
    
    # 模拟尾盘时间
    import time
    original_get_time = strategy.get_current_time
    
    def mock_tail_time():
        return datetime(2026, 4, 1, 14, 45, 0)
    
    strategy.get_current_time = mock_tail_time
    
    try:
        print("运行杨永兴战法...")
        result = strategy.run_selection()
        
        if result:
            print(f"\n✅ 选股成功!")
            print(f"选出 {len(result['selected_stocks'])} 只股票")
            print(f"报告文件: {result['report_path']}")
            
            # 显示前3只股票
            if result['selected_stocks']:
                print("\n前3只推荐股票:")
                for i, stock in enumerate(result['selected_stocks'][:3], 1):
                    print(f"{i}. {stock['name']} ({stock['code']})")
                    print(f"   评分: {stock['score']}分 | 通过步骤: {stock['passed_steps']}/6")
                    print(f"   价格: {stock['current_price']:.2f}元 | 涨跌: {stock['change_percent']:.2f}%")
        else:
            print("\n❌ 选股失败")
            
    finally:
        strategy.get_current_time = original_get_time
    
    print("\n" + "=" * 60)
    print("测试完成!")

if __name__ == "__main__":
    main()