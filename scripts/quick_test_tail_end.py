#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
尾盘选股策略快速测试脚本
"""

import sys
import os
sys.path.append("")

from scripts.auto_tail_end_selection import AutoTailEndSelection

def test_tail_end_selection():
    """测试尾盘选股"""
    print("🚀 快速测试尾盘选股策略...")
    print("=" * 60)
    
    auto_selector = AutoTailEndSelection()
    
    # 模拟尾盘时间运行
    import time
    from datetime import datetime
    
    original_get_time = auto_selector.selector.get_current_time
    
    def mock_tail_time():
        return datetime(2026, 4, 1, 14, 45, 0)
    
    auto_selector.selector.get_current_time = mock_tail_time
    
    try:
        print("运行单次尾盘选股...")
        auto_selector.run_once()
        
        print("\n✅ 测试完成!")
        print("检查以下文件:")
        print(f"  1. 选股报告: /data/tail_end_selection/")
        print(f"  2. 投资组合: /data/investment_tracking/tail_end_portfolio.json")
        print(f"  3. 运行日志: /logs/tail_end_selection.log")
        
    finally:
        auto_selector.selector.get_current_time = original_get_time

if __name__ == "__main__":
    test_tail_end_selection()