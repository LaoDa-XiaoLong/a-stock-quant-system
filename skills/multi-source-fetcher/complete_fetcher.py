#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多源数据获取器 - 完整版
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

        # 配置
        self.max_retries = 3
        self.retry_delay = 1.0  # 秒
        self.enable_quality_check = True
        self.min_quality_score = 75

        logger.info("多源数据获取器初始化完成")

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

    def _check_data_quality(self, data: Dict) -> bool:
        """检查数据质量"""
        try:
            # 检查必要字段
            required_fields = ['symbol', 'price', 'timestamp']
            for field in required_fields:
                if field not in data or data[field] is None:
                    logger.warning(f"数据缺少必要字段: {field}")
                    return False

            # 检查价格合理性
            price = data.get('price', 0)
            if price <= 0:
                logger.warning(f"价格不合理: {price}")
                return False

            # 检查时间戳
            timestamp = data.get('timestamp', '')
            if not timestamp:
                logger.warning("时间戳为空")
                return False

            return True

        except Exception as e:
            logger.warning(f"数据质量检查失败: {e}")
            return False

    def compare_sources(self, symbol: str, name: str = "") -> Dict:
        """比较多个数据源的数据"""
        results = {
            'symbol': symbol,
            'name': name,
            'comparison_time': datetime.now().isoformat(),
            'sources': {},
            'consensus': {},
            'discrepancies': [],
            'recommended_source': None
        }

        # 从所有数据源获取数据
        for source_name, source in self.sources.items():
            try:
                data = source.get_stock_data(symbol, name)
                if data and self._check_data_quality(data):
                    results['sources'][source_name] = {
                        'price': data.get('price', 0),
                        'volume': data.get('volume', 0),
                        'timestamp': data.get('timestamp', ''),
                        'health_score': source.get_health_score()
                    }
            except Exception as e:
                logger.warning(f"数据源 {source_name} 比较失败: {e}")

        if not results['sources']:
            return results

        # 计算共识值（加权平均）
        prices = []
        weights = []

        for source_name, source_data in results['sources'].items():
            price = source_data['price']
            weight = source_data['health_score']

            if price > 0:
                prices.append(price)
                weights.append(weight)

        if prices:
            # 加权平均
            weighted_sum = sum(p * w for p, w in zip(prices, weights))
            total_weight = sum(weights)

            if total_weight > 0:
                results['consensus']['price'] = weighted_sum / total_weight
            else:
                results['consensus']['price'] = np.mean(prices)

        # 查找差异
        if len(results['sources']) >= 2:
            price_values = [d['price'] for d in results['sources'].values()]
            mean_price = np.mean(price_values)
            std_price = np.std(price_values)

            if mean_price > 0:
                cv = std_price / mean_price
                if cv > 0.1:  # 变异系数超过10%
                    results['discrepancies'].append({
                        'field': 'price',
                        'cv': cv,
                        'sources': {s: d['price'] for s, d in results['sources'].items()}
                    })

        # 推荐最佳数据源
        if results['sources']:
            best_source = None
            best_score = -1

            for source_name, source_data in results['sources'].items():
                score = source_data['health_score']
                if score > best_score:
                    best_score = score
                    best_source = source_name

            results['recommended_source'] = best_source

        return results

    def batch_get_stock_data(self, symbols: List[str], names: List[str] = None) -> Dict[str, Dict]:
        """批量获取股票数据"""
        results = {}

        if names is None:
            names = [""] * len(symbols)

        for symbol, name in zip(symbols, names):
            try:
                data = self.get_stock_data(symbol, name)
                if data:
                    results[symbol] = data
                else:
                    results[symbol] = {'error': '获取失败'}
            except Exception as e:
                results[symbol] = {'error': str(e)}

            # 避免请求过快
            time.sleep(0.1)

        return results

    def get_source_status(self) -> Dict:
        """获取数据源状态"""
        status = {}

        for source_name, source in self.sources.items():
            status[source_name] = {
                'healthy': source.is_healthy,
                'health_score': source.get_health_score(),
                'priority': source.priority,
                'success_count': source.success_count,
                'error_count': source.error_count,
                'last_success': source.last_success_time.isoformat() if source.last_success_time else None
            }

        return status

    def configure_cache(self, enabled: bool = True, cache_dir: str = None,
                       ttl_config: Dict = None):
        """配置缓存"""
        self.cache_enabled = enabled

        if cache_dir:
            self.cache_manager.cache_dir = cache_dir
            os.makedirs(cache_dir, exist_ok=True)

        if ttl_config:
            self.cache_manager.ttl_config.update(ttl_config)

        logger.info(f"缓存配置更新: enabled={enabled}, dir={cache_dir or 'default'}")

    def configure_failover(self, max_retries: int = 3, retry_delay: float = 1.0):
        """配置故障转移"""
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        logger.info(f"故障转移配置: max_retries={max_retries}, retry_delay={retry_delay}")

    def clean_cache(self):
        """清理缓存"""
        self.cache_manager.clean_expired()
        logger.info("缓存清理完成")

    def get_cache_stats(self) -> Dict:
        """获取缓存统计"""
        return self.cache_manager.get_stats()


# 示例数据源实现
class MockDataSource(DataSource):
    """模拟数据源"""

    def get_stock_data(self, symbol: str, name: str = "") -> Optional[Dict]:
        """获取模拟数据"""
        try:
            # 基础价格
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


# 使用示例
def example_usage():
    """使用示例"""
    print("多源数据获取器示例")
    print("=" * 60)

    # 创建获取器
    fetcher = MultiSourceFetcher()

    # 添加模拟数据源
    fetcher.add_source('mock_a', MockDataSource('mock_a'), priority=1)
    fetcher.add_source('
