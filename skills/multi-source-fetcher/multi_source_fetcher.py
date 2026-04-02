#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多源数据获取器
支持从多个数据源获取股票数据，提供故障转移和缓存功能
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import json
import os
import time
import hashlib
from typing import Dict, List, Optional, Tuple, Any
import requests
from abc import ABC, abstractmethod

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataSource(ABC):
    """数据源抽象基类"""

    def __init__(self, name: str, priority: int = 5):
        self.name = name
        self.priority = priority
        self.last_success_time = None
        self.error_count = 0
        self.success_count = 0
        self.is_healthy = True

    @abstractmethod
    def get_stock_data(self, symbol: str, name: str = "") -> Optional[Dict]:
        """获取股票数据"""
        pass

    def record_success(self):
        """记录成功"""
        self.last_success_time = datetime.now()
        self.success_count += 1
        self.error_count = 0
        self.is_healthy = True

    def record_error(self, error: str):
        """记录错误"""
        self.error_count += 1
        if self.error_count > 3:
            self.is_healthy = False
        logger.warning(f"数据源 {self.name} 错误: {error}")

    def get_health_score(self) -> float:
        """计算健康分数"""
        if self.success_count + self.error_count == 0:
            return 0.5

        success_rate = self.success_count / (self.success_count + self.error_count)

        # 考虑最近成功时间
        recency_score = 1.0
        if self.last_success_time:
            hours_since_last = (datetime.now() - self.last_success_time).total_seconds() / 3600
            if hours_since_last > 24:
                recency_score = 0.3
            elif hours_since_last > 6:
                recency_score = 0.7

        return success_rate * recency_score


class AkshareSource(DataSource):
    """akshare数据源（A股）"""

    def __init__(self):
        super().__init__('akshare', priority=1)

    def get_stock_data(self, symbol: str, name: str = "") -> Optional[Dict]:
        """获取A股股票数据"""
        try:
            import akshare as ak

            # 获取实时行情
            stock_zh_a_spot = ak.stock_zh_a_spot()
            if stock_zh_a_spot.empty:
                return None

            stock_data = stock_zh_a_spot[stock_zh_a_spot['代码'] == symbol]
            if stock_data.empty:
                return None

            data = {
                'symbol': symbol,
                'name': stock_data.iloc[0]['名称'],
                'price': float(stock_data.iloc[0]['最新价']),
                'change': float(stock_data.iloc[0]['涨跌额']),
                'change_percent': float(stock_data.iloc[0]['涨跌幅']),
                'volume': float(stock_data.iloc[0]['成交量']),
                'amount': float(stock_data.iloc[0]['成交额']),
                'high': float(stock_data.iloc[0]['最高']),
                'low': float(stock_data.iloc[0]['最低']),
                'open': float(stock_data.iloc[0]['今开']),
                'prev_close': float(stock_data.iloc[0]['昨收']),
                'source': self.name,
                'timestamp': datetime.now().isoformat()
            }

            self.record_success()
            return data

        except Exception as e:
            self.record_error(str(e))
            return None


class SinaFinanceSource(DataSource):
    """新浪财经数据源（A股实时）"""

    def __init__(self):
        super().__init__('sina_finance', priority=2)

    def get_stock_data(self, symbol: str, name: str = "") -> Optional[Dict]:
        """获取新浪财经实时数据"""
        try:
            if symbol.startswith('6'):
                market_symbol = f"sh{symbol}"
            else:
                market_symbol = f"sz{symbol}"

            url = f"http://hq.sinajs.cn/list={market_symbol}"
            headers = {
                'Referer': 'http://finance.sina.com.cn',
                'User-Agent': 'Mozilla/5.0'
            }

            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code != 200:
                return None

            content = response.text
            if '=' not in content:
                return None

            data_str = content.split('=')[1].strip('";')
            data_parts = data_str.split(',')

            if len(data_parts) < 30:
                return None

            data = {
                'symbol': symbol,
                'name': data_parts[0],
                'open': float(data_parts[1]),
                'prev_close': float(data_parts[2]),
                'price': float(data_parts[3]),
                'high': float(data_parts[4]),
                'low': float(data_parts[5]),
                'volume': float(data_parts[8]),
                'amount': float(data_parts[9]),
                'bid_price': float(data_parts[11]),
                'ask_price': float(data_parts[21]),
                'timestamp': f"{data_parts[30]} {data_parts[31]}",
                'source': self.name
            }

            self.record_success()
            return data

        except Exception as e:
            self.record_error(str(e))
            return None


class YahooFinanceSource(DataSource):
    """Yahoo Finance数据源（美股）"""

    def __init__(self):
        super().__init__('yfinance', priority=3)

    def get_stock_data(self, symbol: str, name: str = "") -> Optional[Dict]:
        """获取Yahoo Finance数据"""
        try:
            import yfinance as yf

            ticker = yf.Ticker(symbol)
            info = ticker.info

            # 获取最新价格
            hist = ticker.history(period="1d")
            if hist.empty:
                return None

            data = {
                'symbol': symbol,
                'name': info.get('longName', name),
                'price': float(hist['Close'].iloc[-1]),
                'open': float(hist['Open'].iloc[-1]),
                'high': float(hist['High'].iloc[-1]),
                'low': float(hist['Low'].iloc[-1]),
                'volume': float(hist['Volume'].iloc[-1]),
                'prev_close': float(hist['Close'].iloc[-2]) if len(hist) > 1 else float(hist['Close'].iloc[-1]),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'source': self.name,
                'timestamp': datetime.now().isoformat()
            }

            self.record_success()
            return data

        except Exception as e:
            self.record_error(str(e))
            return None


class MockSource(DataSource):
    """模拟数据源（用于测试）"""

    def __init__(self, market_type='A'):
        name = f'mock_{market_type}'
        super().__init__(name, priority=99)
        self.market_type = market_type

    def get_stock_data(self, symbol: str, name: str = "") -> Optional[Dict]:
        """生成模拟数据"""
        try:
            # 基础价格（根据股票不同）
            base_prices = {
                '000001': 15.0, '000002': 8.0, '002352': 40.0,
                '600519': 1800.0, 'AAPL': 180.0, 'MSFT': 420.0
            }

            base_price = base_prices.get(symbol, 100.0)

            # 生成随机波动
            np.random.seed(hash(symbol) % 10000)
            change_percent = np.random.normal(0, 0.02)
            price = base_price * (1 + change_percent)

            data = {
                'symbol': symbol,
                'name': name or f"股票{symbol}",
                'price': round(price, 2),
                'change': round(price * change_percent, 2),
                'change_percent': round(change_percent * 100, 2),
                'volume': np.random.randint(1000000, 10000000),
                'amount': np.random.randint(50000000, 500000000),
                'high': round(price * (1 + abs(np.random.normal(0, 0.01))), 2),
                'low': round(price * (1 - abs(np.random.normal(0, 0.01))), 2),
                'open': round(price * (1 + np.random.normal(0, 0.005)), 2),
                'prev_close': round(base_price, 2),
                'source': self.name,
                'timestamp': datetime.now().isoformat(),
                'is_mock': True
            }

            self.record_success()
            return data

        except Exception as e:
            self.record_error(str(e))
            return None


class CacheManager:
    """缓存管理器"""

    def __init__(self, cache_dir: str = "./data/cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

        # 缓存配置
        self.ttl_config = {
            'realtime': 300,      # 5分钟
            'daily': 3600,        # 1小时
            'historical': 86400   # 24小时
        }

    def get_cache_key(self, symbol: str, data_type: str = 'realtime') -> str:
        """生成缓存键"""
        key_str = f"{symbol}_{data_type}_{datetime.now().strftime('%Y%m%d')}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def get_cache_path(self, cache_key: str) -> str:
        """获取缓存文件路径"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")

    def get(self, symbol: str, data_type: str = 'realtime') -> Optional[Dict]:
        """从缓存获取数据"""
        cache_key = self.get_cache_key(symbol, data_type)
        cache_path = self.get_cache_path(cache_key)

        if not os.path.exists(cache_path):
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # 检查是否过期
            cache_time = datetime.fromisoformat(cache_data['cache_time'])
            ttl_seconds = self.ttl_config.get(data_type, 300)

            if (datetime.now() - cache_time).total_seconds() > ttl_seconds:
                os.remove(cache_path)  # 删除过期缓存
                return None

            return cache_data['data']

        except Exception as e:
            logger.warning(f"读取缓存失败: {e}")
            return None

    def set(self, symbol: str, data: Dict, data_type: str = 'realtime'):
        """设置缓存"""
        cache_key = self.get_cache_key(symbol, data_type)
        cache_path = self.get_cache_path(cache_key)

        try:
            cache_data = {
                'symbol': symbol,
                'data_type': data_type,
                'data': data,
                'cache_time': datetime.now().isoformat(),
                'ttl_seconds': self.ttl_config.get(data_type, 300)
            }

            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.warning(f"写入缓存失败: {e}")

    def clean_expired(self):
        """清理过期缓存"""
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.cache_dir, filename)

                    with open(filepath, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)

                    cache_time = datetime.fromisoformat(cache_data['cache_time'])
                    ttl_seconds = cache_data.get('ttl_seconds', 300)

                    if (datetime.now() - cache_time).total_seconds() > ttl_seconds:
                        os.remove(filepath)
                        logger.debug(f"清理过期缓存: {filename}")

        except Exception as e:
            logger.warning(f"清理缓存失败: {e}")

    def get_stats(self) -> Dict:
        """获取缓存统计"""
        try:
            files = [f for f in os.listdir(self.cache_dir) if f.endswith('.json')]

            total_size = 0
            for filename in files:
                filepath = os.path.join(self.cache_dir, filename)
                total_size += os.path.getsize(filepath)

            return {
                'file_count': len(files),
                'total_size_mb': total_size / (1024 * 1024),
                'cache_dir': self.cache_dir
            }

        except Exception as e:
            logger.warning(f"获取缓存统计失败: {e}")
            return {'file_count': 0, 'total_size_mb': 0, 'cache_dir': self.cache_dir}


class MultiSourceFetcher:
    """多源数据获取器"""

    def __init__(self, cache_enabled: bool = True):
        self.sources: Dict[str, DataSource] = {}
        self.cache_enabled = cache_enabled
        self.cache_manager = CacheManager()

        # 初始化内置数据源
        self._init_builtin_sources()

        # 配置
        self.max_retries = 3
        self.retry_delay = 1.0  # 秒
        self.enable_quality_check = True
        self.min_quality_score = 75

        logger.info("多源数据获取器初始化完成")

    def _init_builtin_sources(self):
        """初始化内置数据源"""
        # A股数据源
        try:
            self.add_source('akshare', AkshareSource())
        except ImportError:
            logger.warning("akshare未安装，跳过akshare数据源")

        try:
            self.add_source('sina_finance', SinaFinanceSource())
        except Exception:
            logger.warning("新浪财经数据源初始化失败")

        # 美股数据源
        try:
            self.add_source('yfinance', YahooFinanceSource())
        except ImportError:
            logger.warning("yfinance未安装，跳过Yahoo Finance数据源")

        # 模拟数据源（备用）
        self.add_source('mock_a', MockSource('A'))
        self.add_source('mock_us', MockSource('US'))

    def add_source(self, name: str, source: DataSource, priority: int = None):
        """添加数据源"""
        if priority is not None:
            source.priority = priority

        self.sources[name] = source
        logger.info(f"添加数据源: {name} (优先级: {source.priority})")

    def remove_source(self, name: str):
        """移除数据源"""
        if name in self.sources:
            del self.sources[name]
            logger.info(f"移除数据源: {name}")

    def get_stock_data(self, symbol: str, name: str = "",
                      use_cache: bool = True) -> Optional[Dict]:
        """获取股票数据（带故障转移）"""
        # 检查缓存
        if use_cache and self.cache_enabled:
            cached_data = self.cache_manager.get(symbol, 'realtime')
            if cached_data:
                logger.debug(f"从缓存获取数据: {symbol}")
                return cached_data

        # 按优先级尝试数据源
        sorted_sources = sorted(
            self.sources.items(),
            key=lambda x: (x[1].priority, -x[1].get_health_score())
        )

        last_error = None
        for source_name, source in sorted_sources:
            try:
                logger.debug(f"尝试数据源: {source_name} 获取 {symbol}")

                data = source.get_stock_data(symbol, name)
                if data:
                    # 数据质量检查
                    if self.enable_quality_check:
                        if not self._check_data_quality(data):
                            logger.warning(f"数据源 {source_name} 数据质量检查失败: {symbol}")
                            continue

                    # 保存到缓存
                    if self.cache_enabled:
                        self.cache_manager.set(symbol, data, 'realtime')

                    logger.info(f"从数据源 {source_name} 成功获取数据: {symbol}")
                    return data

            except Exception as e:
                last_error = str(e)
                logger.warning(f"数据源 {source_name} 获取失败: {e}")
                time.sleep(self.retry_delay)

        # 所有数据源都失败
        logger.error(f"所有数据源都失败: {symbol}, 最后错误: {last_error}")

        # 尝试返回缓存数据（即使过期）
        if self.cache_enabled:
            cached_data = self.cache_manager.get(symbol, 'realtime')
            if cached_data:
                logger.warning(f"返回过期缓存数据: {symbol}")
                cached_data['source'] = 'expired_cache'
                return cached_data

        return None

