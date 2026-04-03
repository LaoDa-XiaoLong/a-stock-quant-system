#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据自动更新脚本 v1.0
功能：
1. 使用akshare获取最新A股数据
2. 应用选股策略筛选
3. 更新本地数据文件
4. 生成更新报告
"""

import pandas as pd
import numpy as np
import akshare as ak
from datetime import datetime, timedelta
import logging
import json
import os
import sys
from typing import Dict, List, Optional
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"data/stock_pool/update_log_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StockDataUpdater:
    """股票数据自动更新器"""
    
    def __init__(self, config_path: str = "config/stock_pool_config.json"):
        """初始化更新器"""
        self.config = self._load_config(config_path)
        self.data_dir = "data"
        self.stock_pool_dir = os.path.join(self.data_dir, "stock_pool")
        self.raw_data_dir = os.path.join(self.data_dir, "raw")
        
        # 创建必要的目录
        os.makedirs(self.stock_pool_dir, exist_ok=True)
        os.makedirs(self.raw_data_dir, exist_ok=True)
        
        # 初始化数据缓存
        self.cache = {}
        
        logger.info("股票数据自动更新器初始化完成")
        logger.info(f"数据目录: {self.data_dir}")
        logger.info(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        default_config = {
            "update": {
                "max_retries": 3,
                "retry_delay": 2,
                "timeout": 30,
                "batch_size": 50
            },
            "data_sources": {
                "use_cache": True,
                "cache_expiry_hours": 24
            },
            "output": {
                "generate_report": True,
                "update_summary": True,
                "backup_old_data": True
            }
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
                logger.info(f"已加载配置文件: {config_path}")
            except Exception as e:
                logger.warning(f"加载配置文件失败: {e}, 使用默认配置")
        
        return default_config
    
    def get_all_a_shares(self) -> pd.DataFrame:
        """获取所有A股股票列表"""
        cache_file = os.path.join(self.stock_pool_dir, "all_a_shares_latest.csv")
        
        # 检查缓存
        if self.config["data_sources"]["use_cache"] and os.path.exists(cache_file):
            cache_time = os.path.getmtime(cache_file)
            cache_age_hours = (datetime.now().timestamp() - cache_time) / 3600
            
            if cache_age_hours < self.config["data_sources"]["cache_expiry_hours"]:
                logger.info(f"从缓存加载A股列表 (缓存时间: {cache_age_hours:.1f}小时)")
                try:
                    return pd.read_csv(cache_file)
                except Exception as e:
                    logger.warning(f"读取缓存失败: {e}")
        
        logger.info("从akshare获取最新A股列表...")
        
        for retry in range(self.config["update"]["max_retries"]):
            try:
                # 获取A股代码和名称
                stock_info = ak.stock_info_a_code_name()
                
                if stock_info.empty:
                    logger.error("获取的A股列表为空")
                    continue
                
                # 重命名列
                stock_info = stock_info.rename(columns={
                    'code': 'symbol',
                    'name': 'name'
                })
                
                # 添加市场信息
                stock_info['market'] = stock_info['symbol'].apply(
                    lambda x: 'SH' if x.startswith('6') else 'SZ'
                )
                
                # 添加获取时间
                stock_info['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # 保存到缓存
                stock_info.to_csv(cache_file, index=False, encoding='utf-8')
                logger.info(f"A股列表已保存到缓存: {cache_file}")
                logger.info(f"获取到 {len(stock_info)} 只A股股票")
                
                return stock_info
                
            except Exception as e:
                logger.error(f"获取A股列表失败 (尝试 {retry+1}/{self.config['update']['max_retries']}): {e}")
                if retry < self.config["update"]["max_retries"] - 1:
                    time.sleep(self.config["update"]["retry_delay"])
        
        logger.error("获取A股列表失败，使用备用数据")
        return self._get_fallback_stock_list()
    
    def _get_fallback_stock_list(self) -> pd.DataFrame:
        """获取备用股票列表"""
        fallback_file = os.path.join(self.data_dir, "stock_list_latest.csv")
        
        if os.path.exists(fallback_file):
            logger.info(f"使用备用股票列表: {fallback_file}")
            try:
                df = pd.read_csv(fallback_file)
                df['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                return df
            except Exception as e:
                logger.warning(f"读取备用文件失败: {e}")
        
        # 创建基本的股票列表
        logger.info("创建基本股票列表")
        basic_stocks = [
            {'symbol': '000001', 'name': '平安银行', 'market': 'SZ'},
            {'symbol': '000002', 'name': '万科A', 'market': 'SZ'},
            {'symbol': '002352', 'name': '顺丰控股', 'market': 'SZ'},
            {'symbol': '600580', 'name': '卧龙电驱', 'market': 'SH'},
            {'symbol': '603728', 'name': '鸣志电器', 'market': 'SH'},
            {'symbol': '300750', 'name': '宁德时代', 'market': 'SZ'},
            {'symbol': '600519', 'name': '贵州茅台', 'market': 'SH'},
            {'symbol': '000858', 'name': '五粮液', 'market': 'SZ'},
            {'symbol': '002415', 'name': '海康威视', 'market': 'SZ'},
            {'symbol': '601318', 'name': '中国平安', 'market': 'SH'},
        ]
        
        df = pd.DataFrame(basic_stocks)
        df['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return df
    
    def get_stock_real_time_data(self, symbol: str) -> Optional[Dict]:
        """获取股票实时数据"""
        cache_key = f"realtime_{symbol}"
        
        # 检查内存缓存
        if cache_key in self.cache:
            cache_time = self.cache[cache_key].get('cache_time', 0)
            if time.time() - cache_time < 60:  # 1分钟缓存
                return self.cache[cache_key]['data']
        
        for retry in range(self.config["update"]["max_retries"]):
            try:
                # 获取实时行情
                stock_zh_a_spot = ak.stock_zh_a_spot()
                
                if stock_zh_a_spot.empty:
                    logger.warning(f"实时行情数据为空")
                    continue
                
                # 查找指定股票
                stock_data = stock_zh_a_spot[stock_zh_a_spot['代码'] == symbol]
                
                if stock_data.empty:
                    logger.warning(f"未找到股票 {symbol} 的实时数据")
                    return None
                
                # 提取数据
                data = {
                    'symbol': symbol,
                    'name': stock_data.iloc[0]['名称'],
                    'price': float(stock_data.iloc[0]['最新价']),
                    'change': float(stock_data.iloc[0]['涨跌幅']),
                    'change_amount': float(stock_data.iloc[0]['涨跌额']),
                    'volume': float(stock_data.iloc[0]['成交量']),
                    'turnover': float(stock_data.iloc[0]['成交额']),
                    'amplitude': float(stock_data.iloc[0]['振幅']),
                    'high': float(stock_data.iloc[0]['最高']),
                    'low': float(stock_data.iloc[0]['最低']),
                    'open': float(stock_data.iloc[0]['今开']),
                    'close': float(stock_data.iloc[0]['昨收']),
                    'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # 更新缓存
                self.cache[cache_key] = {
                    'data': data,
                    'cache_time': time.time()
                }
                
                return data
                
            except Exception as e:
                logger.error(f"获取股票{symbol}实时数据失败 (尝试 {retry+1}/{self.config['update']['max_retries']}): {e}")
                if retry < self.config["update"]["max_retries"] - 1:
                    time.sleep(self.config["update"]["retry_delay"])
        
        return None
    
    def get_stock_basic_info(self, symbol: str) -> Optional[Dict]:
        """获取股票基本信息"""
        cache_file = os.path.join(self.stock_pool_dir, f"{symbol}_basic_info.json")
        
        # 检查文件缓存
        if self.config["data_sources"]["use_cache"] and os.path.exists(cache_file):
            cache_time = os.path.getmtime(cache_file)
            cache_age_hours = (datetime.now().timestamp() - cache_time) / 3600
            
            if cache_age_hours < self.config["data_sources"]["cache_expiry_hours"]:
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    logger.warning(f"读取缓存文件失败: {e}")
        
        # 基本信息模板
        basic_info = {
            'symbol': symbol,
            'name': '',
            'industry': '',
            'area': '',
            'fullname': '',
            'enname': '',
            'market': 'SH' if symbol.startswith('6') else 'SZ',
            'listing_date': '',
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            # 尝试获取股票基本信息
            stock_info = ak.stock_individual_info_em(symbol=symbol)
            
            if not stock_info.empty:
                # 提取信息
                for _, row in stock_info.iterrows():
                    key = row['item']
                    value = row['value']
                    
                    if key == '股票简称':
                        basic_info['name'] = value
                    elif key == '所属行业':
                        basic_info['industry'] = value
                    elif key == '所属地域':
                        basic_info['area'] = value
                    elif key == '公司全称':
                        basic_info['fullname'] = value
                    elif key == '英文名称':
                        basic_info['enname'] = value
                    elif key == '上市时间':
                        basic_info['listing_date'] = value
            
            # 保存到缓存
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(basic_info, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.warning(f"获取股票{symbol}基本信息失败: {e}")
        
        return basic_info
    
    def update_stock_data_batch(self, symbols: List[str]) -> pd.DataFrame:
        """批量更新股票数据"""
        logger.info(f"开始批量更新股票数据，共{len(symbols)}只股票")
        
        results = []
        
        for i, symbol in enumerate(symbols, 1):
            if i % 10 == 0:
                logger.info(f"更新进度: {i}/{len(symbols)}")
            
            try:
                # 获取实时数据
                realtime_data = self.get_stock_real_time_data(symbol)
                
                if realtime_data is None:
                    logger.warning(f"股票{symbol}实时数据获取失败，跳过")
                    continue
                
                # 获取基本信息
                basic_info = self.get_stock_basic_info(symbol)
                
                # 合并数据
                stock_data = {**basic_info, **realtime_data}
                
                # 计算技术指标（简化版）
                stock_data['volume_ratio'] = 1.0  # 默认值
                stock_data['turnover_rate'] = 0.0  # 默认值
                
                results.append(stock_data)
                
                # 小批量保存
                if i % self.config["update"]["batch_size"] == 0:
                    self._save_batch_data(results[-self.config["update"]["batch_size"]:])
                
            except Exception as e:
                logger.error(f"更新股票{symbol}数据失败: {e}")
                continue
        
        # 保存剩余数据
        if results:
            self._save_batch_data(results)
        
        # 转换为DataFrame
        df = pd.DataFrame(results)
        
        logger.info(f"批量更新完成: 成功{len(df)}只，失败{len(symbols)-len(df)}只")
        
        return df
    
    def _save_batch_data(self, batch_data: List[Dict]):
        """保存批量数据"""
        if not batch_data:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch_file = os.path.join(self.raw_data_dir, f"stock_batch_{timestamp}.json")
        
        try:
            with open(batch_file, 'w', encoding='utf-8') as f:
                json.dump(batch_data, f, ensure_ascii=False, indent=2)
            logger.debug(f"批量数据已保存: {batch_file}")
        except Exception as e:
            logger.error(f"保存批量数据失败: {e}")
    
    def apply_stock_selection_strategy(self, stock_data: pd.DataFrame) -> pd.DataFrame:
        """应用选股策略筛选"""
        logger.info("开始应用选股策略筛选")
        
        if stock_data.empty:
            logger.warning("股票数据为空，无法应用筛选策略")
            return pd.DataFrame()
        
        # 复制数据以避免修改原数据
        filtered_data = stock_data.copy()
        
        # 1. 流动性筛选
        min_turnover = 10000000  # 最小成交额1000万
        filtered_data = filtered_data[filtered_data['turnover'] >= min_turnover]
        logger.info(f"流动性筛选后: {len(filtered_data)}只")
        
        # 2. 价格筛选（排除过高和过低的股票）
        filtered_data = filtered_data[(filtered_data['price'] >= 5) & (filtered_data['price'] <= 500)]
        logger.info(f"价格筛选后: {len(filtered_data)}只")
        
        # 3. 涨跌幅筛选（排除涨跌停和大幅波动的股票）
        filtered_data = filtered_data[(filtered_data['change'] >= -5) & (filtered_data['change'] <= 5)]
        logger.info(f"涨跌幅筛选后: {len(filtered_data)}只")
        
        # 4. 振幅筛选（排除波动过大的股票）
        filtered_data = filtered_data[filtered_data['amplitude'] <= 10]
        logger.info(f"振幅筛选后: {len(filtered_data)}只")
        
        # 5. 计算综合评分
        filtered_data = self._calculate_composite_score(filtered_data)
        
        # 6. 按评分排序
        filtered_data = filtered_data.sort_values('composite_score', ascending=False)
        
        logger.info(f"选股策略筛选完成: 总共{len(stock_data)}只，筛选后{len(filtered_data)}只")
        
        return filtered_data
    
    def _calculate_composite_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算综合评分"""
        df = df.copy()
        
        # 初始化评分
        df['composite_score'] = 50  # 基础分
        
        # 1. 流动性评分 (0-20分)
        if 'turnover' in df.columns:
            max_turnover = df['turnover'].max()
            if max_turnover > 0:
                df['liquidity_score'] = (df['turnover'] / max_turnover) * 20
                df['composite_score'] += df['liquidity_score']
        
        # 2. 稳定性评分 (0-15分)
        if 'amplitude' in df.columns:
            df['stability_score'] = 15 - (df['amplitude'] / 10 * 15).clip(0, 15)
            df['composite_score'] += df['stability_score']
        
        # 3. 活跃度评分 (0-15分)
        if 'volume' in df.columns:
            max_volume = df['volume'].max()
            if max_volume > 0:
                df['activity_score'] = (df['volume'] / max_volume) * 15
                df['composite_score'] += df['activity_score']
        
        # 确保评分在合理范围内
        df['composite_score'] = df['composite_score'].clip(0, 100)
        
        return df
    
    def update_local_data_files(self, filtered_stocks: pd.DataFrame):
        """更新本地数据文件"""
        logger.info("开始更新本地数据文件")
        
        timestamp = datetime.now().strftime("%Y%m%d")
        
        # 1. 备份旧数据（如果配置了备份）
        if self.config["output"]["backup_old_data"]:
            self._backup_old_data()
        
        # 2. 更新股票列表文件
        stock_list_file = os.path.join(self.data_dir, "stock_list_latest.csv")
        
        if os.path.exists(stock_list_file):
            backup_file = os.path.join(self.data_dir, f"stock_list_backup_{timestamp}.csv")
            os.rename(stock_list_file, backup_file)
            logger.info(f"已备份旧股票列表: {backup_file}")
        
        # 保存精简的股票列表
        if not filtered_stocks.empty:
            simple_list = filtered_stocks[['symbol', 'name', 'market', 'price', 'change', 'composite_score']].copy()
            simple_list.to_csv(stock_list_file, index=False, encoding='utf-8')
            logger.info(f"已更新股票列表文件: {stock_list_file}")
        
        # 3. 更新股票池文件
        stock_pool_file = os.path.join(self.stock_pool_dir, f"selected_stocks_{timestamp}.csv")
        
        if not filtered_stocks.empty:
            filtered_stocks.to_csv(stock_pool_file, index=False, encoding='utf-8')
            logger.info(f"已更新股票池文件: {stock_pool_file}")
        
        # 4. 更新今日数据文件
        today_data_file = os.path.join(self.stock_pool_dir, f"today_stock_data_{timestamp}.json")
        
        if not filtered_stocks.empty:
            today_data = filtered_stocks.to_dict('records')
            with open(today_data_file, 'w', encoding='utf-8') as f:
                json.dump(today_data, f, ensure_ascii=False, indent=2)
            logger.info(f"已保存今日数据文件: {today_data_file}")
        
        # 5. 更新历史记录
        self._update_history_record(filtered_stocks)
        
        logger.info("本地数据文件更新完成")
    
    def _backup_old_data(self):
        """备份旧数据"""
        backup_dir = os.path.join(self.data_dir, "backup", datetime.now().strftime("%Y%m"))
        os.makedirs(backup_dir, exist_ok=True)
        
        # 备份股票列表
        stock_list_file = os.path.join(self.data_dir, "stock_list_latest.csv")
        if os.path.exists(stock_list_file):
            backup_file = os.path.join(backup_dir, f"stock_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            import shutil
            shutil.copy2(stock_list_file, backup_file)
            logger.debug(f"已备份股票列表: {backup_file}")
    
    def _update_history_record(self, filtered_stocks: pd.DataFrame):
        """更新历史记录"""
        history_file = os.path.join(self.stock_pool_dir, "update_history.json")
        
        history_data = []
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
            except Exception as e:
                logger.warning(f"读取历史记录失败: {e}")
        
        # 添加新记录
        new_record = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_stocks': len(filtered_stocks) if not filtered_stocks.empty else 0,
            'top_stocks': []
        }
        
        if not filtered_stocks.empty:
            top_10 = filtered_stocks.head(10)
            for _, row in top_10.iterrows():
                new_record['top_stocks'].append({
                    'symbol': row['symbol'],
                    'name': row['name'],
                    'score': float(row.get('composite_score', 0)),
                    'price': float(row.get('price', 0))
                })
        
        history_data.append(new_record)
        
        # 只保留最近30天的记录
        if len(history_data) > 30:
            history_data = history_data[-30:]
        
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, ensure_ascii=False, indent=2)
            logger.info(f"已更新历史记录: {history_file}")
        except Exception as e:
            logger.error(f"保存历史记录失败: {e}")
    
    def generate_update_report(self, all_stocks: pd.DataFrame, filtered_stocks: pd.DataFrame) -> str:
        """生成更新报告"""
        logger.info("开始生成更新报告")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report_lines = []
        
        report_lines.append("# 股票数据自动更新报告")
        report_lines.append(f"## 生成时间: {timestamp}")
        report_lines.append(f"## 版本: v1.0")
        report_lines.append("")
        
        # 总体统计
        report_lines.append("## 📊 总体统计")
        report_lines.append(f"- 获取股票总数: {len(all_stocks)} 只")
        report_lines.append(f"- 筛选后股票数: {len(filtered_stocks)} 只")
        report_lines.append(f"- 筛选比例: {len(filtered_stocks)/len(all_stocks)*100:.1f}%")
        report_lines.append("")
        
        if not filtered_stocks.empty:
            # 评分分布
            report_lines.append("## 📈 评分分布")
            score_stats = filtered_stocks['composite_score'].describe()
            report_lines.append(f"- 平均评分: {score_stats['mean']:.1f}")
            report_lines.append(f"- 最高评分: {score_stats['max']:.1f}")
            report_lines.append(f"- 最低评分: {score_stats['min']:.1f}")
            report_lines.append(f"- 中位数: {score_stats['50%']:.1f}")
            report_lines.append("")
            
            # 价格分布
            report_lines.append("## 💰 价格分布")
            price_stats = filtered_stocks['price'].describe()
            report_lines.append(f"- 平均价格: {price_stats['mean']:.2f} 元")
            report_lines.append(f"- 最高价格: {price_stats['max']:.2f} 元")
            report_lines.append(f"- 最低价格: {price_stats['min']:.2f} 元")
            report_lines.append("")
            
            # 涨跌幅分布
            report_lines.append("## 📉 涨跌幅分布")
            change_stats = filtered_stocks['change'].describe()
            report_lines.append(f"- 平均涨跌幅: {change_stats['mean']:.2f}%")
            report_lines.append(f"- 最大涨幅: {change_stats['max']:.2f}%")
            report_lines.append(f"- 最大跌幅: {change_stats['min']:.2f}%")
            report_lines.append("")
            
            # 前10名股票
            report_lines.append("## 🏆 前10名推荐股票")
            report_lines.append("| 排名 | 代码 | 名称 | 价格 | 涨跌幅 | 综合评分 |")
            report_lines.append("|------|------|------|------|--------|----------|")
            
            top_10 = filtered_stocks.head(10)
            for i, (_, row) in enumerate(top_10.iterrows(), 1):
                change_icon = "📈" if row['change'] > 0 else "📉" if row['change'] < 0 else "➖"
                report_lines.append(
                    f"| {i} | {row['symbol']} | {row['name']} | "
                    f"{row['price']:.2f} | {change_icon} {row['change']:.2f}% | "
                    f"{row['composite_score']:.1f} |"
                )
            
            report_lines.append("")
            
            # 市场分布
            report_lines.append("## 🏛️ 市场分布")
            market_counts = filtered_stocks['market'].value_counts()
            for market, count in market_counts.items():
                market_name = "上海主板" if market == 'SH' else "深圳主板"
                report_lines.append(f"- {market_name}: {count}只 ({count/len(filtered_stocks)*100:.1f}%)")
            
            report_lines.append("")
        
        # 更新详情
        report_lines.append("## 🔄 更新详情")
        report_lines.append(f"- 开始时间: {timestamp}")
        report_lines.append(f"- 数据来源: akshare")
        report_lines.append(f"- 筛选策略: 流动性 + 价格 + 波动性 + 综合评分")
        report_lines.append(f"- 数据目录: {self.data_dir}")
        report_lines.append("")
        
        # 文件更新
        report_lines.append("## 💾 文件更新")
        report_lines.append(f"- 股票列表: `data/stock_list_latest.csv`")
        report_lines.append(f"- 股票池: `data/stock_pool/selected_stocks_*.csv`")
        report_lines.append(f"- 今日数据: `data/stock_pool/today_stock_data_*.json`")
        report_lines.append(f"- 更新日志: `data/stock_pool/update_log_*.log`")
        report_lines.append("")
        
        # 下次更新建议
        next_update = (datetime.now() + timedelta(hours=1)).strftime("%H:%M")
        report_lines.append("## ⏰ 下次更新建议")
        report_lines.append(f"- 建议下次更新时间: {next_update}")
        report_lines.append(f"- 建议更新频率: 每小时一次（交易时间）")
        report_lines.append(f"- 建议检查时间: 09:30, 10:30, 13:00, 14:00")
        report_lines.append("")
        
        report_lines.append("---")
        report_lines.append("*报告由股票数据自动更新系统 v1.0 生成*")
        
        report_content = "\n".join(report_lines)
        
        # 保存报告文件
        report_file = os.path.join(self.stock_pool_dir, f"update_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"更新报告已保存: {report_file}")
        
        return report_content
    
    def run_full_update(self, sample_mode: bool = False, max_stocks: int = 100):
        """运行完整更新流程"""
        logger.info("=" * 60)
        logger.info("开始股票数据自动更新流程")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        try:
            # 1. 获取所有A股股票
            logger.info("步骤1: 获取A股股票列表")
            all_stocks = self.get_all_a_shares()
            
            if all_stocks.empty:
                logger.error("无法获取股票列表，更新终止")
                return False
            
            # 2. 选择要更新的股票（样本模式或全量）
            if sample_mode:
                symbols = all_stocks['symbol'].head(max_stocks).tolist()
                logger.info(f"样本模式: 更新前{max_stocks}只股票")
            else:
                symbols = all_stocks['symbol'].tolist()
                logger.info(f"全量模式: 更新{len(symbols)}只股票")
            
            # 3. 批量更新股票数据
            logger.info("步骤2: 批量更新股票数据")
            updated_data = self.update_stock_data_batch(symbols)
            
            if updated_data.empty:
                logger.error("股票数据更新失败，更新终止")
                return False
            
            # 4. 应用选股策略
            logger.info("步骤3: 应用选股策略筛选")
            filtered_stocks = self.apply_stock_selection_strategy(updated_data)
            
            # 5. 更新本地文件
            logger.info("步骤4: 更新本地数据文件")
            self.update_local_data_files(filtered_stocks)
            
            # 6. 生成报告
            if self.config["output"]["generate_report"]:
                logger.info("步骤5: 生成更新报告")
                report = self.generate_update_report(all_stocks, filtered_stocks)
                
                # 打印报告摘要
                print("\n" + "=" * 60)
                print("股票数据自动更新完成!")
                print("=" * 60)
                print(f"获取股票: {len(all_stocks)}只")
                print(f"筛选股票: {len(filtered_stocks)}只")
                
                if not filtered_stocks.empty:
                    print(f"最高评分: {filtered_stocks['composite_score'].max():.1f}")
                    print(f"平均评分: {filtered_stocks['composite_score'].mean():.1f}")
                    print("\n前5名股票:")
                    for i, (_, row) in enumerate(filtered_stocks.head(5).iterrows(), 1):
                        change_icon = "📈" if row['change'] > 0 else "📉" if row['change'] < 0 else "➖"
                        print(f"  {i}. {row['symbol']} {row['name']} - {row['price']:.2f}元 "
                              f"({change_icon}{row['change']:.2f}%) - 评分: {row['composite_score']:.1f}")
            
            # 计算耗时
            elapsed_time = time.time() - start_time
            logger.info(f"更新流程完成，总耗时: {elapsed_time:.1f}秒")
            
            return True
            
        except Exception as e:
            logger.error(f"更新流程失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False


def main():
    """主函数"""
    print("股票数据自动更新系统 v1.0")
    print("=" * 50)
    
    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description='股票数据自动更新系统')
    parser.add_argument('--sample', action='store_true', help='样本模式（只更新少量股票）')
    parser.add_argument('--max-stocks', type=int, default=50, help='样本模式下的最大股票数量')
    parser.add_argument('--config', type=str, default='config/stock_pool_config.json', help='配置文件路径')
    
    args = parser.parse_args()
    
    # 创建更新器
    updater = StockDataUpdater(config_path=args.config)
    
    # 运行更新
    success = updater.run_full_update(
        sample_mode=args.sample,
        max_stocks=args.max_stocks
    )
    
    if success:
        print("\n✅ 股票数据更新成功!")
        print(f"   报告文件: data/stock_pool/update_report_*.md")
        print(f"   数据文件: data/stock_list_latest.csv")
        print(f"   日志文件: data/stock_pool/update_log_*.log")
    else:
        print("\n❌ 股票数据更新失败!")
        print("   请检查日志文件查看详细错误信息")
    
    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()