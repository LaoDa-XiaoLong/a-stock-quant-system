#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
尾盘选股法 Skill（真实价格版）
基于杨永兴隔夜套利战法实现，使用真实价格
"""

import os
import sys
import json
import time
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TailEndSelectionRealPrice:
    """尾盘选股法（真实价格版）"""
    
    def __init__(self, config_file: Optional[str] = None):
        """初始化选股器"""
        self.skill_name = "尾盘选股法（真实价格版）"
        self.version = "v1.0"
        self.author = "量化小助理"
        self.created_date = "2026-04-02"
        
        # 基础目录
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.workspace_dir = os.path.dirname(os.path.dirname(self.base_dir))
        
        # 数据存储目录
        self.data_dir = os.path.join(self.workspace_dir, "data", "tail_end_selection_real")
        self.trades_dir = os.path.join(self.data_dir, "trades")
        self.reports_dir = os.path.join(self.data_dir, "reports", "daily")
        self.selection_dir = os.path.join(self.data_dir, "selection_results")
        self.logs_dir = os.path.join(self.data_dir, "logs")
        
        # 创建目录
        for directory in [self.data_dir, self.trades_dir, self.reports_dir, 
                         self.selection_dir, self.logs_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # 配置文件
        self.config_file = config_file or os.path.join(self.base_dir, "config.json")
        self.trades_file = os.path.join(self.trades_dir, "real_trades.json")
        self.portfolio_file = os.path.join(self.trades_dir, "real_portfolio.json")
        self.performance_file = os.path.join(self.trades_dir, "performance_summary.json")
        
        # 加载配置
        self.config = self.load_config()
        
        # 初始化日志
        self.setup_logging()
        
        # 股票代码到中文名称映射
        self.stock_name_map = {
            '600016': '民生银行',
            '600519': '贵州茅台',
            '600585': '海螺水泥',
            '600036': '招商银行',
            '000006': '深振业A',
            '000009': '中国宝安',
            '000010': '美丽生态',
            '000011': '深物业A',
            '000020': '深华发Ａ',
            '000004': '*ST国华',
            '000027': '深圳能源'
        }
        
        # 投资参数
        self.initial_capital = 1000000.0  # 初始资金100万
        self.max_position_percent = self.config.get('max_position_percent', 0.1)  # 单只股票最大仓位10%
        self.stop_loss_percent = self.config.get('stop_loss_percent', 0.05)  # 止损5%
        self.take_profit_percent = self.config.get('take_profit_percent', 0.08)  # 止盈8%
        
        # 价格源配置
        self.use_real_prices = self.config.get('use_real_prices', True)
        self.price_source = self.config.get('price_source', 'sina_finance')
        
        self.logger.info(f"✅ {self.skill_name} {self.version} 初始化完成")
        self.logger.info(f"💰 初始资金: {self.initial_capital}元")
        self.logger.info(f"🎯 单只股票最大仓位: {self.max_position_percent*100}%")
        self.logger.info(f"📈 价格源: {'真实价格' if self.use_real_prices else '模拟价格'} ({self.price_source})")
    
    def load_config(self) -> Dict:
        """加载配置文件"""
        default_config = {
            "skill_name": "尾盘选股法",
            "version": "1.0",
            "use_real_prices": True,
            "price_source": "sina_finance",
            "max_position_percent": 0.1,
            "stop_loss_percent": 0.05,
            "take_profit_percent": 0.08,
            "selection_time_window": "14:30-15:00",
            "monitoring_interval": 180,
            "report_time": "18:00",
            "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 合并配置，确保有默认值
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception as e:
                print(f"❌ 加载配置文件失败: {e}")
                return default_config
        else:
            # 创建默认配置
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            return default_config
    
    def setup_logging(self):
        """设置日志"""
        log_file = os.path.join(self.logs_dir, f"tail_end_selection_{datetime.now().strftime('%Y%m%d')}.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.skill_name)
    
    def get_real_stock_price(self, stock_code: str) -> Optional[Dict]:
        """获取真实股票价格"""
        if not self.use_real_prices:
            # 使用模拟价格
            return self.get_simulated_price(stock_code)
        
        try:
            # 判断市场
            if stock_code.startswith('6'):
                market_code = f"sh{stock_code}"
            elif stock_code.startswith('0') or stock_code.startswith('3'):
                market_code = f"sz{stock_code}"
            else:
                self.logger.warning(f"无法识别股票代码: {stock_code}")
                return None
            
            # 新浪财经API
            url = f"http://hq.sinajs.cn/list={market_code}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Referer': 'http://finance.sina.com.cn'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                content = response.text
                if '="' in content:
                    data_str = content.split('="')[1].split('"')[0]
                    data_parts = data_str.split(',')
                    if len(data_parts) > 1:
                        current_price = float(data_parts[3])
                        yesterday_close = float(data_parts[2])
                        
                        if yesterday_close > 0:
                            change_percent = (current_price - yesterday_close) / yesterday_close * 100
                        else:
                            change_percent = 0.0
                        
                        stock_name = data_parts[0]
                        if stock_code in self.stock_name_map:
                            stock_name = self.stock_name_map[stock_code]
                        
                        return {
                            'code': stock_code,
                            'name': stock_name,
                            'current_price': round(current_price, 2),
                            'yesterday_close': round(yesterday_close, 2),
                            'change_percent': round(change_percent, 2),
                            'high': float(data_parts[4]),
                            'low': float(data_parts[5]),
                            'volume': int(data_parts[8]),
                            'amount': float(data_parts[9]),
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'price_source': self.price_source
                        }
        except Exception as e:
            self.logger.error(f"获取股票 {stock_code} 价格失败: {e}")
        
        return None
    
    def get_simulated_price(self, stock_code: str) -> Dict:
        """获取模拟价格（备用）"""
        import random
        
        # 基础价格
        base_prices = {
            '600016': 32.0, '600519': 1600.0, '600585': 28.0,
            '600036': 35.0, '000006': 9.0, '000009': 8.5,
            '000010': 4.0, '000011': 40.0, '000020': 16.0,
            '000004': 4.5, '000027': 7.0
        }
        
        base_price = base_prices.get(stock_code, 10.0)
        
        # 添加随机波动
        fluctuation = random.uniform(-0.02, 0.02)  # ±2%
        current_price = base_price * (1 + fluctuation)
        
        stock_name = self.stock_name_map.get(stock_code, f"股票{stock_code}")
        
        return {
            'code': stock_code,
            'name': stock_name,
            'current_price': round(current_price, 2),
            'yesterday_close': round(base_price, 2),
            'change_percent': round(fluctuation * 100, 2),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'price_source': 'simulated'
        }
    
    def calculate_entry_points(self, stock_data: Dict) -> Dict:
        """计算进场点位"""
        current_price = stock_data['current_price']
        
        return {
            '激进进场': round(current_price * 0.99, 2),  # 下跌1%
            '稳健进场': round(current_price * 0.97, 2),  # 下跌3%
            '保守进场': round(current_price * 0.95, 2),  # 下跌5%
            '尾盘追涨': round(current_price * 1.01, 2)   # 上涨1%
        }
    
    def calculate_risk_control(self, stock_data: Dict, entry_price: float) -> Dict:
        """计算风险控制点位"""
        return {
            '止损位': round(entry_price * (1 - self.stop_loss_percent), 2),
            '第一止盈': round(entry_price * (1 + self.take_profit_percent), 2),
            '第二止盈': round(entry_price * (1 + self.take_profit_percent * 1.5), 2),
            '风险收益比': round(self.take_profit_percent / self.stop_loss_percent, 2)
        }
    
    def calculate_position_size(self, stock_data: Dict, available_capital: float) -> Dict:
        """计算仓位大小"""
        current_price = stock_data['current_price']
        
        # 单只股票最大投资额
        max_investment = available_capital * self.max_position_percent
        
        # 计算可买股数
        max_shares = int(max_investment / current_price)
        
        # 实际投资额
        actual_investment = max_shares * current_price
        
        # 仓位建议
        if actual_investment >= max_investment * 0.8:
            position_suggestion = "重仓"
        elif actual_investment >= max_investment * 0.5:
            position_suggestion = "中等仓位"
        else:
            position_suggestion = "轻仓"
        
        return {
            'max_investment': round(max_investment, 2),
            'max_shares': max_shares,
            'actual_investment': round(actual_investment, 2),
            'position_suggestion': position_suggestion,
            'position_percent': round(actual_investment / available_capital * 100, 2)
        }
    
    def execute_selection(self, stock_codes: List[str]) -> Dict:
        """执行尾盘选股"""
        self.logger.info(f"🎯 开始执行尾盘选股，股票池: {len(stock_codes)} 只")
        
        selected_stocks = []
        
        for stock_code in stock_codes:
            # 获取真实价格
            stock_data = self.get_real_stock_price(stock_code)
            if not stock_data:
                continue
            
            # 计算进场点位
            entry_points = self.calculate_entry_points(stock_data)
            
            # 计算风险控制
            aggressive_entry = entry_points['激进进场']
            risk_control = self.calculate_risk_control(stock_data, aggressive_entry)
            
            # 计算综合评分 (简单示例)
            score = self.calculate_score(stock_data)
            
            # 添加到选股结果
            selected_stock = {
                **stock_data,
                'entry_points': entry_points,
                'risk_control': risk_control,
                'score': score,
                'selection_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'selection_reason': self.get_selection_reason(stock_data, score)
            }
            
            selected_stocks.append(selected_stock)
            
            # 避免请求过快
            time.sleep(0.3)
        
        # 按评分排序
        selected_stocks.sort(key=lambda x: x['score'], reverse=True)
        
        # 保存选股结果
        result = {
            'selection_time': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'strategy_name': self.skill_name,
            'strategy_version': self.version,
            'total_selected': len(selected_stocks),
            'stocks': selected_stocks,
            'config': {
                'use_real_prices': self.use_real_prices,
                'price_source': self.price_source,
                'max_position_percent': self.max_position_percent,
                'stop_loss_percent': self.stop_loss_percent,
                'take_profit_percent': self.take_profit_percent
            }
        }
        
        # 保存结果
        result_file = os.path.join(self.selection_dir, f"selection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"✅ 尾盘选股完成，选出 {len(selected_stocks)} 只股票")
        self.logger.info(f"💾 结果保存到: {result_file}")
        
        return result
    
    def calculate_score(self, stock_data: Dict) -> int:
        """计算股票综合评分 (0-100)"""
        score = 50  # 基础分
        
        # 价格因素 (5-20元最佳)
        price = stock_data['current_price']
        if 5 <= price <= 20:
            score += 20
        elif 20 < price <= 50:
            score += 10
        elif price > 50:
            score += 5
        
        # 涨跌因素 (小幅波动最佳)
        change = abs(stock_data['change_percent'])
        if 0 <= change <= 3:
            score += 15
        elif 3 < change <= 8:
            score += 5
        else:
            score -= 5
        
        # 成交量因素
        volume = stock_data.get('volume', 0)
        if volume > 1000000:  # 100万股以上
            score += 15
        
        # 确保分数在0-100之间
        return max(0, min(100, score))
    
    def get_selection_reason(self, stock_data: Dict, score: int) -> List[str]:
        """获取选股理由"""
        reasons = []
        
        price = stock_data['current_price']
        change = stock_data['change_percent']
        
        # 价格理由
        if 5 <= price <= 20:
            reasons.append("价格适中")
        elif price < 5:
            reasons.append("低价股")
        else:
            reasons.append("价格合理")
        
        # 涨跌理由
        if -3 <= change <= 3:
            reasons.append("波动适中")
        elif change < -3:
            reasons.append("超跌有反弹机会")
        else:
            reasons.append("趋势向上")
        
        # 评分理由
        if score >= 80:
            reasons.append("综合评分优秀")
        elif score >= 60:
            reasons.append("综合评分良好")
        else:
            reasons.append("综合评分一般")
        
        return reasons
    
    def generate_report(self, selection_result: Dict) -> str:
        """生成选股报告"""
        report = f"""# {self.skill_name} 选股报告
## 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
## 策略版本: {self.version}
## 价格来源: {'真实价格' if self.use_real_prices else '模拟价格'} ({self.price_source})
## 选股时间窗口: {self.config.get('selection_time_window', '14:30-15:00')}

## 选股结果: 共筛选出 {selection_result['total_selected']} 只股票

"""
        
        for i, stock in enumerate(selection_result['stocks'], 1):
            report += f"""### {i}. {stock['name']} ({stock['code']})
