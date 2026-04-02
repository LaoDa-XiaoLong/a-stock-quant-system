#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
尾盘选股法 Skill（修复版）
基于杨永兴隔夜套利战法实现
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TailEndSelection:
    """尾盘选股法"""
    
    def __init__(self, config_file: Optional[str] = None):
        """初始化选股器"""
        self.skill_name = "尾盘选股法"
        self.version = "v1.0"
        self.author = "量化小助理"
        self.created_date = "2026-04-01"
        
        # 基础目录
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.workspace_dir = os.path.dirname(os.path.dirname(self.base_dir))
        
        # 数据存储目录
        self.data_dir = os.path.join(self.workspace_dir, "data", "tail_end_selection")
        self.trades_dir = os.path.join(self.data_dir, "trades")
        self.reports_dir = os.path.join(self.data_dir, "reports", "daily")
        self.selection_dir = os.path.join(self.data_dir, "selection_results")
        self.logs_dir = os.path.join(self.data_dir, "logs")
        
        # 创建目录
        for directory in [self.data_dir, self.trades_dir, self.reports_dir, 
                         self.selection_dir, self.logs_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # 配置文件
        self.trades_file = os.path.join(self.trades_dir, "simulated_trades.json")
        self.portfolio_file = os.path.join(self.trades_dir, "simulated_portfolio.json")
        self.performance_file = os.path.join(self.trades_dir, "performance_summary.json")
        
        # 配置
        self.config = self._load_config(config_file)
        
        # 日志
        self.logger = self._setup_logger()
        
        # 初始化文件
        self._initialize_files()
        
        self.logger.info(f"{self.skill_name} {self.version} 初始化完成")
    
    def _load_config(self, config_file: Optional[str] = None) -> Dict:
        """加载配置"""
        default_config = {
            "strategy": {
                "name": "尾盘选股法",
                "version": "v1.0",
                "selection_time": "14:30",
                "report_time": "18:00",
                "selection_steps": {
                    "time_window": 20,
                    "price_change": 20,
                    "capital_flow": 25,
                    "volume_ratio": 15,
                    "market_cap": 10,
                    "tech_space": 10
                },
                "entry_strategy": {
                    "premium_grade": {"min_score": 90, "stop_loss": 0.97, "target_gain": 0.08},
                    "good_grade": {"min_score": 80, "stop_loss": 0.96, "target_gain": 0.06},
                    "normal_grade": {"min_score": 70, "stop_loss": 0.95, "target_gain": 0.05}
                }
            },
            "trading": {
                "initial_capital": 1000000,
                "max_position_percent": 0.1,
                "max_daily_loss": 0.05,
                "max_trade_loss": 0.02,
                "min_score": 70
            },
            "reporting": {
                "daily_report": True,
                "weekly_report": True,
                "monthly_report": True,
                "send_to_group": "A股数据分析群",
                "report_format": "markdown"
            }
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
                self.logger.info(f"从 {config_file} 加载配置")
            except Exception as e:
                self.logger.error(f"加载配置文件失败: {e}")
        
        # 保存配置
        config_path = os.path.join(self.data_dir, "config.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        
        return default_config
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger("TailEndSelection")
        logger.setLevel(logging.INFO)
        
        # 文件处理器
        log_file = os.path.join(self.logs_dir, f"execution_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _initialize_files(self):
        """初始化文件"""
        # 交易记录文件
        if not os.path.exists(self.trades_file):
            with open(self.trades_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "system_name": self.skill_name,
                    "strategy_name": self.config["strategy"]["name"],
                    "created_date": datetime.now().strftime("%Y-%m-%d"),
                    "total_trades": 0,
                    "active_trades": 0,
                    "closed_trades": 0,
                    "trades": []
                }, f, ensure_ascii=False, indent=2)
        
        # 投资组合文件
        if not os.path.exists(self.portfolio_file):
            with open(self.portfolio_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "portfolio_name": "尾盘选股投资组合",
                    "created_date": datetime.now().strftime("%Y-%m-%d"),
                    "total_capital": self.config["trading"]["initial_capital"],
                    "available_capital": self.config["trading"]["initial_capital"],
                    "invested_capital": 0,
                    "total_value": self.config["trading"]["initial_capital"],
                    "positions": [],
                    "performance": {
                        "total_return": 0,
                        "daily_return": 0,
                        "win_rate": 0,
                        "avg_win": 0,
                        "avg_loss": 0
                    }
                }, f, ensure_ascii=False, indent=2)
    
    def get_current_positions(self) -> Dict:
        """获取当前持仓情况"""
        try:
            with open(self.portfolio_file, 'r', encoding='utf-8') as f:
                portfolio = json.load(f)
            
            with open(self.trades_file, 'r', encoding='utf-8') as f:
                trades = json.load(f)
            
            return {
                "portfolio": portfolio,
                "trades": trades,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            self.logger.error(f"获取持仓失败: {e}")
            return {
                "portfolio": {},
                "trades": {},
                "error": str(e)
            }


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='尾盘选股法')
    parser.add_argument('--get-positions', action='store_true', help='获取当前持仓')
    
    args = parser.parse_args()
    
    selector = TailEndSelection()
    
    if args.get_positions:
        print("获取当前持仓情况...")
        positions = selector.get_current_positions()
        
        if "error" in positions:
            print(f"❌ 获取持仓失败: {positions['error']}")
            return
        
        portfolio = positions["portfolio"]
        trades = positions["trades"]
        
        print(f"\n📊 尾盘选股策略持仓情况")
        print(f"📅 更新时间: {positions['timestamp']}")
        print("=" * 60)
        
        print(f"💰 资金概览:")
        print(f"  初始资金: {portfolio.get('total_capital', 0):,.2f}元")
        print(f"  当前总资产: {portfolio.get('total_value', 0):,.2f}元")
        print(f"  已投资金额: {portfolio.get('invested_capital', 0):,.2f}元")
        print(f"  可用资金: {portfolio.get('available_capital', 0):,.2f}元")
        
        total_return = ((portfolio.get('total_value', 0) - portfolio.get('total_capital', 0)) / 
                       portfolio.get('total_capital', 1) * 100)
        print(f"  总收益率: {total_return:.2f}%")
        
        print(f"\n📈 交易统计:")
        print(f"  总交易笔数: {trades.get('total_trades', 0)}笔")
        print(f"  活跃交易: {trades.get('active_trades', 0)}笔")
        print(f"  已平仓交易: {trades.get('closed_trades', 0)}笔")
        
        positions_list = portfolio.get('positions', [])
        if positions_list:
            print(f"\n📋 当前持仓 ({len(positions_list)} 只股票):")
            print("=" * 60)
            
            total_market_value = 0
            total_unrealized_pnl = 0
            
            for i, pos in enumerate(positions_list, 1):
                pnl = pos.get('unrealized_pnl', 0)
                pnl_percent = pos.get('unrealized_pnl_percent', 0)
                pnl_emoji = "📈" if pnl > 0 else "📉"
                
                print(f"{i}. {pos.get('stock_name', '')} ({pos.get('stock_code', '')})")
                print(f"   持仓数量: {pos.get('shares', 0):,}股")
                print(f"   进场价格: {pos.get('entry_price', 0):.2f}元")
                print(f"   当前价格: {pos.get('current_price', 0):.2f}元")
                print(f"   浮动盈亏: {pnl_emoji} {pnl:,.2f}元 ({pnl_percent:.2f}%)")
                print(f"   持仓市值: {pos.get('market_value', 0):,.2f}元")
                print(f"   进场日期: {pos.get('entry_date', '')}")
                print()
                
                total_market_value += pos.get('market_value', 0)
                total_unrealized_pnl += pnl
            
            print("=" * 60)
            print(f"📊 持仓汇总:")
            print(f"  总持仓市值: {total_market_value:,.2f}元")
            print(f"  总浮动盈亏: {total_unrealized_pnl:,.2f}元")
        else:
            print("\n📭 当前无持仓")
        
        print(f"\n⏰ 下次执行时间:")
        print(f"  尾盘选股: 今日14:30")
        print(f"  每日报告: 今日18:00")
        print(f"  报告发送: 今日18:05 (A股数据分析群)")
        
    else:
        print("尾盘选股法 Skill")
        print(f"版本: {selector.version}")
        print(f"作者: {selector.author}")
        print(f"选股时间: {selector.config['strategy']['selection_time']}")
        print(f"报告时间: {selector.config['strategy']['report_time']}")
        print("")
        print("可用命令:")
        print("  --get-positions  获取当前持仓")


if __name__ == "__main__":
    main()