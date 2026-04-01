#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票池筛选系统
基于免费数据源，建立A股股票池筛选机制
"""

import pandas as pd
import numpy as np
import akshare as ak
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Tuple
import json
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StockPoolFilter:
    """股票池筛选器"""
    
    def __init__(self, config_path: str = "config/stock_pool_config.json"):
        """初始化筛选器"""
        self.config = self._load_config(config_path)
        self.cache_dir = "data/stock_pool"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 初始化筛选规则
        self.rules = self._init_rules()
        
        logger.info("股票池筛选系统初始化完成")
    
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        default_config = {
            "liquidity": {
                "min_daily_turnover": 10000000,  # 最小日成交额：1000万元
                "min_daily_volume": 1000000,      # 最小日成交量：100万股
                "min_market_cap": 5000000000,     # 最小市值：50亿元
                "max_market_cap": 1000000000000,  # 最大市值：1万亿元
            },
            "fundamental": {
                "min_pe": 0,                      # 最小PE（负值表示亏损）
                "max_pe": 100,                    # 最大PE
                "min_pb": 0.5,                    # 最小PB
                "max_pb": 10,                     # 最大PB
                "min_roe": 0,                     # 最小ROE
                "max_debt_ratio": 70,             # 最大资产负债率
            },
            "compliance": {
                "exclude_st": True,               # 排除ST股票
                "exclude_suspended": True,        # 排除停牌股票
                "exclude_delisting": True,        # 排除退市风险股票
            },
            "technical": {
                "price_stability_days": 20,       # 价格稳定性观察期
                "max_price_volatility": 0.5,      # 最大价格波动率
                "min_trading_days": 60,           # 最小交易天数
            },
            "industry": {
                "excluded_industries": [],        # 排除的行业
                "preferred_industries": [],       # 优先的行业
                "max_industry_concentration": 0.3, # 最大行业集中度
            }
        }
        
        # 如果配置文件存在，则加载
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                # 合并配置
                default_config.update(user_config)
                logger.info(f"已加载用户配置: {config_path}")
            except Exception as e:
                logger.warning(f"加载配置文件失败: {e}, 使用默认配置")
        
        return default_config
    
    def _init_rules(self) -> List[Dict]:
        """初始化筛选规则"""
        rules = [
            {
                "name": "流动性规则",
                "function": self._check_liquidity,
                "weight": 1.0,
                "required": True,
            },
            {
                "name": "基本面规则",
                "function": self._check_fundamental,
                "weight": 0.8,
                "required": True,
            },
            {
                "name": "合规性规则",
                "function": self._check_compliance,
                "weight": 1.0,
                "required": True,
            },
            {
                "name": "技术面规则",
                "function": self._check_technical,
                "weight": 0.6,
                "required": False,
            },
            {
                "name": "行业规则",
                "function": self._check_industry,
                "weight": 0.4,
                "required": False,
            },
        ]
        return rules
    
    def get_all_a_shares(self) -> pd.DataFrame:
        """获取所有A股股票列表"""
        cache_file = os.path.join(self.cache_dir, "all_a_shares.csv")
        
        # 检查缓存
        if os.path.exists(cache_file):
            cache_time = os.path.getmtime(cache_file)
            if datetime.now().timestamp() - cache_time < 86400:  # 24小时缓存
                logger.info("从缓存加载A股列表")
                return pd.read_csv(cache_file)
        
        logger.info("从akshare获取A股列表")
        try:
            # 获取A股列表
            stock_info = ak.stock_info_a_code_name()
            
            if stock_info.empty:
                logger.error("获取A股列表失败，返回空DataFrame")
                return pd.DataFrame()
            
            # 重命名列
            stock_info = stock_info.rename(columns={
                'code': 'symbol',
                'name': 'name'
            })
            
            # 添加市场类型
            stock_info['market'] = stock_info['symbol'].apply(
                lambda x: 'SH' if x.startswith('6') else 'SZ'
            )
            
            # 保存缓存
            stock_info.to_csv(cache_file, index=False, encoding='utf-8')
            logger.info(f"A股列表已保存到缓存: {cache_file}")
            
            return stock_info
            
        except Exception as e:
            logger.error(f"获取A股列表失败: {e}")
            # 返回示例数据
            return pd.DataFrame({
                'symbol': ['000001', '000002', '002352', '600580', '603728'],
                'name': ['平安银行', '万科A', '顺丰控股', '卧龙电驱', '鸣志电器'],
                'market': ['SZ', 'SZ', 'SZ', 'SH', 'SH']
            })
    
    def get_stock_details(self, symbol: str) -> Dict:
        """获取股票详细信息"""
        cache_file = os.path.join(self.cache_dir, f"{symbol}_details.json")
        
        # 检查缓存
        if os.path.exists(cache_file):
            cache_time = os.path.getmtime(cache_file)
            if datetime.now().timestamp() - cache_time < 3600:  # 1小时缓存
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        
        details = {
            'symbol': symbol,
            'name': '',
            'industry': '',
            'market_cap': 0,
            'pe_ratio': 0,
            'pb_ratio': 0,
            'roe': 0,
            'debt_ratio': 0,
            'daily_turnover': 0,
            'daily_volume': 0,
            'price': 0,
            'is_st': False,
            'is_suspended': False,
            'update_time': datetime.now().isoformat()
        }
        
        try:
            # 获取实时行情
            stock_zh_a_spot = ak.stock_zh_a_spot()
            if not stock_zh_a_spot.empty:
                stock_data = stock_zh_a_spot[stock_zh_a_spot['代码'] == symbol]
                if not stock_data.empty:
                    details['price'] = float(stock_data.iloc[0]['最新价'])
                    details['daily_turnover'] = float(stock_data.iloc[0]['成交额'])
                    details['daily_volume'] = float(stock_data.iloc[0]['成交量'])
                    details['name'] = stock_data.iloc[0]['名称']
            
            # 获取市值信息（示例，实际需要更多数据）
            # 这里简化处理，实际需要更多数据源
            
        except Exception as e:
            logger.warning(f"获取股票{symbol}详情失败: {e}")
        
        # 保存缓存
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(details, f, ensure_ascii=False, indent=2)
        
        return details
    
    def _check_liquidity(self, stock_details: Dict) -> Tuple[bool, str, float]:
        """检查流动性规则"""
        config = self.config['liquidity']
        
        issues = []
        score = 100
        
        # 检查成交额
        if stock_details['daily_turnover'] < config['min_daily_turnover']:
            issues.append(f"成交额不足: {stock_details['daily_turnover']:,.0f} < {config['min_daily_turnover']:,.0f}")
            score -= 30
        
        # 检查成交量
        if stock_details['daily_volume'] < config['min_daily_volume']:
            issues.append(f"成交量不足: {stock_details['daily_volume']:,.0f} < {config['min_daily_volume']:,.0f}")
            score -= 20
        
        # 检查市值（如果有数据）
        if stock_details['market_cap'] > 0:
            if stock_details['market_cap'] < config['min_market_cap']:
                issues.append(f"市值过小: {stock_details['market_cap']:,.0f} < {config['min_market_cap']:,.0f}")
                score -= 25
            if stock_details['market_cap'] > config['max_market_cap']:
                issues.append(f"市值过大: {stock_details['market_cap']:,.0f} > {config['max_market_cap']:,.0f}")
                score -= 15
        
        passed = len(issues) == 0
        message = "通过" if passed else "; ".join(issues)
        
        return passed, message, max(0, score)
    
    def _check_fundamental(self, stock_details: Dict) -> Tuple[bool, str, float]:
        """检查基本面规则"""
        config = self.config['fundamental']
        
        issues = []
        score = 100
        
        # 检查PE
        if stock_details['pe_ratio'] > 0:  # 正PE
            if stock_details['pe_ratio'] < config['min_pe']:
                issues.append(f"PE过低: {stock_details['pe_ratio']:.1f} < {config['min_pe']}")
                score -= 20
            if stock_details['pe_ratio'] > config['max_pe']:
                issues.append(f"PE过高: {stock_details['pe_ratio']:.1f} > {config['max_pe']}")
                score -= 30
        
        # 检查PB
        if stock_details['pb_ratio'] > 0:
            if stock_details['pb_ratio'] < config['min_pb']:
                issues.append(f"PB过低: {stock_details['pb_ratio']:.2f} < {config['min_pb']}")
                score -= 15
            if stock_details['pb_ratio'] > config['max_pb']:
                issues.append(f"PB过高: {stock_details['pb_ratio']:.2f} > {config['max_pb']}")
                score -= 25
        
        # 检查ROE
        if stock_details['roe'] < config['min_roe']:
            issues.append(f"ROE过低: {stock_details['roe']:.1f}% < {config['min_roe']}%")
            score -= 20
        
        # 检查负债率
        if stock_details['debt_ratio'] > config['max_debt_ratio']:
            issues.append(f"负债率过高: {stock_details['debt_ratio']:.1f}% > {config['max_debt_ratio']}%")
            score -= 25
        
        passed = len(issues) == 0
        message = "通过" if passed else "; ".join(issues)
        
        return passed, message, max(0, score)
    
    def _check_compliance(self, stock_details: Dict) -> Tuple[bool, str, float]:
        """检查合规性规则"""
        config = self.config['compliance']
        
        issues = []
        score = 100
        
        # 检查ST（简化处理）
        if config['exclude_st'] and stock_details['is_st']:
            issues.append("ST股票")
            score = 0  # 直接0分
        
        # 检查停牌（简化处理）
        if config['exclude_suspended'] and stock_details['is_suspended']:
            issues.append("停牌股票")
            score = 0
        
        passed = len(issues) == 0
        message = "通过" if passed else "; ".join(issues)
        
        return passed, message, score
    
    def _check_technical(self, stock_details: Dict) -> Tuple[bool, str, float]:
        """检查技术面规则（简化）"""
        # 这里简化处理，实际需要获取历史价格数据
        score = 80  # 默认分数
        message = "技术面检查（简化版）"
        
        return True, message, score
    
    def _check_industry(self, stock_details: Dict) -> Tuple[bool, str, float]:
        """检查行业规则"""
        config = self.config['industry']
        
        issues = []
        score = 100
        
        # 检查排除行业
        if stock_details['industry'] in config['excluded_industries']:
            issues.append(f"行业被排除: {stock_details['industry']}")
            score -= 50
        
        # 检查优先行业
        if stock_details['industry'] in config['preferred_industries']:
            score += 20  # 加分
        
        passed = True  # 行业规则不是必须的
        message = f"行业: {stock_details['industry']}" if stock_details['industry'] else "行业信息缺失"
        
        return passed, message, max(0, score)
    
    def filter_stock(self, symbol: str) -> Dict:
        """筛选单个股票"""
        logger.info(f"开始筛选股票: {symbol}")
        
        # 获取股票详情
        details = self.get_stock_details(symbol)
        
        results = {
            'symbol': symbol,
            'name': details['name'],
            'industry': details['industry'],
            'total_score': 0,
            'weighted_score': 0,
            'passed': True,
            'rule_results': [],
            'details': details
        }
        
        total_weight = 0
        weighted_score = 0
        
        # 应用所有规则
        for rule in self.rules:
            passed, message, score = rule['function'](details)
            
            rule_result = {
                'name': rule['name'],
                'passed': passed,
                'message': message,
                'raw_score': score,
                'weighted_score': score * rule['weight'],
                'weight': rule['weight'],
                'required': rule['required']
            }
            
            results['rule_results'].append(rule_result)
            
            # 计算总分
            results['total_score'] += score
            
            # 计算加权分
            if passed or not rule['required']:
                weighted_score += score * rule['weight']
                total_weight += rule['weight']
            else:
                # 必须规则未通过，整体不通过
                results['passed'] = False
            
            # 如果必须规则未通过，提前结束
            if rule['required'] and not passed:
                logger.info(f"股票{symbol}未通过必须规则: {rule['name']}")
                break
        
        # 计算加权平均分
        if total_weight > 0:
            results['weighted_score'] = weighted_score / total_weight
        else:
            results['weighted_score'] = 0
        
        # 设置通过阈值
        min_score = 60  # 最低60分
        results['passed'] = results['passed'] and results['weighted_score'] >= min_score
        
        logger.info(f"股票{symbol}筛选完成: 加权分={results['weighted_score']:.1f}, 通过={results['passed']}")
        
        return results
    
    def filter_stock_pool(self, symbols: List[str] = None,
                         max_stocks: int = 100) -> pd.DataFrame:
        """筛选股票池"""
        if symbols is None:
            # 获取所有A股
            all_stocks = self.get_all_a_shares()
            symbols = all_stocks['symbol'].tolist()
        
        logger.info(f"开始筛选股票")
