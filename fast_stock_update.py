#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速股票数据更新脚本
专注于核心功能，使用缓存提高效率
"""

import pandas as pd
import akshare as ak
from datetime import datetime, timedelta
import json
import os
import sys
import time

class FastStockUpdater:
    def __init__(self):
        self.data_dir = "data"
        self.stock_pool_dir = os.path.join(self.data_dir, "stock_pool")
        os.makedirs(self.stock_pool_dir, exist_ok=True)
        
        # 设置日志
        self.setup_logging()
        
    def setup_logging(self):
        """设置日志"""
        import logging
        log_file = os.path.join(self.stock_pool_dir, f"fast_update_{datetime.now().strftime('%Y%m%d')}.log")
        
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # 文件处理器
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.INFO)
        
        # 控制台处理器
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # 格式
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
    
    def get_cached_stock_list(self):
        """获取缓存的股票列表"""
        cache_file = os.path.join(self.stock_pool_dir, "cached_stock_list.json")
        
        # 检查缓存是否有效（1小时内）
        if os.path.exists(cache_file):
            cache_time = os.path.getmtime(cache_file)
            if time.time() - cache_time < 3600:  # 1小时
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    self.logger.info(f"从缓存加载股票列表: {len(data)} 只")
                    return pd.DataFrame(data)
                except:
                    pass
        
        # 获取新的股票列表
        self.logger.info("获取最新股票列表...")
        try:
            stock_info = ak.stock_info_a_code_name()
            
            if stock_info.empty:
                self.logger.error("获取的股票列表为空")
                return pd.DataFrame()
            
            # 简化数据
            stock_info = stock_info.rename(columns={'code': 'symbol', 'name': 'name'})
            stock_info['market'] = stock_info['symbol'].apply(
                lambda x: 'SH' if x.startswith('6') else 'SZ'
            )
            
            # 保存到缓存
            stock_info.to_json(cache_file, orient='records', force_ascii=False)
            self.logger.info(f"股票列表已缓存: {cache_file}")
            
            return stock_info
            
        except Exception as e:
            self.logger.error(f"获取股票列表失败: {e}")
            return pd.DataFrame()
    
    def get_top_stocks_data(self, count=20):
        """获取头部股票数据"""
        self.logger.info(f"获取前{count}只股票数据...")
        
        try:
            # 获取实时行情（所有股票）
            spot_data = ak.stock_zh_a_spot()
            
            if spot_data.empty:
                self.logger.error("实时行情数据为空")
                return pd.DataFrame()
            
            # 选择前count只股票（按成交额排序）
            spot_data = spot_data.sort_values('成交额', ascending=False)
            top_stocks = spot_data.head(count).copy()
            
            # 整理数据
            results = []
            for _, row in top_stocks.iterrows():
                data = {
                    'symbol': row['代码'],
                    'name': row['名称'],
                    'price': float(row['最新价']),
                    'change': float(row['涨跌幅']),
                    'turnover': float(row['成交额']),
                    'volume': float(row['成交量']),
                    'high': float(row['最高']),
                    'low': float(row['最低']),
                    'open': float(row['今开']),
                    'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                results.append(data)
            
            df = pd.DataFrame(results)
            self.logger.info(f"成功获取 {len(df)} 只头部股票数据")
            return df
            
        except Exception as e:
            self.logger.error(f"获取股票数据失败: {e}")
            return pd.DataFrame()
    
    def apply_quick_filter(self, stock_data):
        """应用快速筛选"""
        if stock_data.empty:
            return stock_data
        
        filtered = stock_data.copy()
        
        # 基本筛选条件
        filtered = filtered[filtered['turnover'] > 5000000]  # 成交额大于500万
        filtered = filtered[(filtered['price'] >= 2) & (filtered['price'] <= 300)]  # 价格范围
        filtered = filtered[abs(filtered['change']) <= 7]  # 涨跌幅不超过7%
        
        # 计算简单评分
        if not filtered.empty:
            # 流动性评分
            max_turnover = filtered['turnover'].max()
            filtered['liquidity_score'] = (filtered['turnover'] / max_turnover) * 40
            
            # 稳定性评分
            filtered['stability_score'] = (1 - abs(filtered['change']) / 10) * 30
            
            # 活跃度评分（基于成交量）
            max_volume = filtered['volume'].max()
            if max_volume > 0:
                filtered['activity_score'] = (filtered['volume'] / max_volume) * 30
            else:
                filtered['activity_score'] = 0
            
            # 总分
            filtered['total_score'] = filtered['liquidity_score'] + filtered['stability_score'] + filtered['activity_score']
            
            # 排序
            filtered = filtered.sort_values('total_score', ascending=False)
        
        self.logger.info(f"快速筛选完成: 原始{len(stock_data)}只，筛选后{len(filtered)}只")
        return filtered
    
    def save_results(self, filtered_stocks, all_stocks):
        """保存结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. 保存筛选结果
        if not filtered_stocks.empty:
            result_file = os.path.join(self.stock_pool_dir, f"fast_selected_{timestamp}.csv")
            # 只保存关键列
            cols_to_save = ['symbol', 'name', 'price', 'change', 'turnover', 'total_score']
            filtered_stocks[cols_to_save].to_csv(result_file, index=False, encoding='utf-8')
            self.logger.info(f"筛选结果已保存: {result_file}")
        
        # 2. 更新股票列表
        if not all_stocks.empty:
            list_file = os.path.join(self.data_dir, "stock_list_fast.csv")
            all_stocks[['symbol', 'name', 'market']].to_csv(list_file, index=False, encoding='utf-8')
            self.logger.info(f"股票列表已更新: {list_file}")
        
        # 3. 保存更新记录
        record = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_stocks': len(all_stocks),
            'filtered_stocks': len(filtered_stocks),
            'top_5_stocks': []
        }
        
        if not filtered_stocks.empty:
            top_5 = filtered_stocks.head(5)
            for _, row in top_5.iterrows():
                record['top_5_stocks'].append({
                    'symbol': row['symbol'],
                    'name': row['name'],
                    'price': float(row['price']),
                    'change': float(row['change']),
                    'score': float(row['total_score'])
                })
        
        record_file = os.path.join(self.stock_pool_dir, f"fast_record_{timestamp}.json")
        with open(record_file, 'w', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"更新记录已保存: {record_file}")
        
        return record
    
    def generate_summary(self, record):
        """生成摘要"""
        summary = []
        summary.append("=" * 60)
        summary.append("快速股票数据更新摘要")
        summary.append("=" * 60)
        summary.append(f"更新时间: {record['timestamp']}")
        summary.append(f"总股票数: {record['total_stocks']}")
        summary.append(f"筛选股票: {record['filtered_stocks']}")
        
        if record['top_5_stocks']:
            summary.append("\n🏆 前5名股票:")
            for i, stock in enumerate(record['top_5_stocks'], 1):
                change_icon = "📈" if stock['change'] > 0 else "📉" if stock['change'] < 0 else "➖"
                summary.append(f"  {i}. {stock['symbol']} {stock['name']} - "
                              f"{stock['price']:.2f}元 ({change_icon}{stock['change']:.2f}%) - "
                              f"评分: {stock['score']:.1f}")
        
        summary.append("\n📁 生成文件:")
        summary.append(f"  - data/stock_list_fast.csv")
        summary.append(f"  - data/stock_pool/fast_selected_*.csv")
        summary.append(f"  - data/stock_pool/fast_record_*.json")
        summary.append(f"  - data/stock_pool/fast_update_*.log")
        
        summary.append("\n" + "=" * 60)
        
        return "\n".join(summary)
    
    def run(self):
        """运行更新流程"""
        self.logger.info("=" * 60)
        self.logger.info("开始快速股票数据更新")
        self.logger.info("=" * 60)
        
        start_time = time.time()
        
        try:
            # 1. 获取股票列表（使用缓存）
            all_stocks = self.get_cached_stock_list()
            
            if all_stocks.empty:
                self.logger.error("无法获取股票列表")
                return False
            
            # 2. 获取头部股票数据
            stock_data = self.get_top_stocks_data(count=30)
            
            if stock_data.empty:
                self.logger.error("无法获取股票数据")
                return False
            
            # 3. 应用快速筛选
            filtered_stocks = self.apply_quick_filter(stock_data)
            
            # 4. 保存结果
            record = self.save_results(filtered_stocks, all_stocks)
            
            # 5. 生成摘要
            elapsed_time = time.time() - start_time
            record['elapsed_seconds'] = round(elapsed_time, 1)
            
            summary = self.generate_summary(record)
            print(summary)
            
            # 保存摘要
            summary_file = os.path.join(self.stock_pool_dir, f"fast_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            self.logger.info(f"更新完成，耗时: {elapsed_time:.1f}秒")
            self.logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            self.logger.error(f"更新失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False

def main():
    """主函数"""
    print("快速股票数据更新系统")
    print("=" * 50)
    
    updater = FastStockUpdater()
    success = updater.run()
    
    if success:
        print("\n✅ 快速更新成功!")
        print("   专注于头部股票，适合高频更新")
    else:
        print("\n❌ 快速更新失败!")
    
    print("\n" + "=" * 50)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()