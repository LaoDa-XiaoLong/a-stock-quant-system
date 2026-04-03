#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单股票数据更新脚本
使用现有数据文件，避免API调用问题
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import sys
import time
import random

class SimpleStockUpdater:
    def __init__(self):
        self.data_dir = "data"
        self.stock_pool_dir = os.path.join(self.data_dir, "stock_pool")
        os.makedirs(self.stock_pool_dir, exist_ok=True)
        
        # 设置日志
        self.setup_logging()
        
        # 模拟数据
        self.sample_stocks = [
            {'symbol': '000001', 'name': '平安银行', 'market': 'SZ', 'base_price': 10.5},
            {'symbol': '000002', 'name': '万科A', 'market': 'SZ', 'base_price': 8.2},
            {'symbol': '002352', 'name': '顺丰控股', 'market': 'SZ', 'base_price': 35.6},
            {'symbol': '600580', 'name': '卧龙电驱', 'market': 'SH', 'base_price': 15.8},
            {'symbol': '603728', 'name': '鸣志电器', 'market': 'SH', 'base_price': 22.3},
            {'symbol': '300750', 'name': '宁德时代', 'market': 'SZ', 'base_price': 180.5},
            {'symbol': '600519', 'name': '贵州茅台', 'market': 'SH', 'base_price': 1650.0},
            {'symbol': '000858', 'name': '五粮液', 'market': 'SZ', 'base_price': 135.2},
            {'symbol': '002415', 'name': '海康威视', 'market': 'SZ', 'base_price': 28.7},
            {'symbol': '601318', 'name': '中国平安', 'market': 'SH', 'base_price': 42.3},
        ]
    
    def setup_logging(self):
        """设置日志"""
        import logging
        log_file = os.path.join(self.stock_pool_dir, f"simple_update_{datetime.now().strftime('%Y%m%d')}.log")
        
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
    
    def load_existing_stock_list(self):
        """加载现有股票列表"""
        stock_files = [
            os.path.join(self.data_dir, "stock_list_latest.csv"),
            os.path.join(self.data_dir, "stock_list_all.csv"),
            os.path.join(self.data_dir, "stock_list.csv")
        ]
        
        for file_path in stock_files:
            if os.path.exists(file_path):
                try:
                    df = pd.read_csv(file_path)
                    self.logger.info(f"从文件加载股票列表: {file_path} ({len(df)} 只)")
                    
                    # 标准化列名
                    if 'code' in df.columns:
                        df = df.rename(columns={'code': 'symbol'})
                    elif '股票代码' in df.columns:
                        df = df.rename(columns={'股票代码': 'symbol'})
                    
                    if '名称' in df.columns:
                        df = df.rename(columns={'名称': 'name'})
                    
                    return df
                except Exception as e:
                    self.logger.warning(f"读取文件失败 {file_path}: {e}")
        
        # 如果没有找到文件，使用样本数据
        self.logger.info("使用样本股票数据")
        return pd.DataFrame(self.sample_stocks)
    
    def generate_simulated_data(self, stock_list):
        """生成模拟股票数据"""
        self.logger.info("生成模拟股票数据...")
        
        results = []
        current_time = datetime.now()
        
        for _, stock in stock_list.iterrows():
            # 获取基本信息
            symbol = stock.get('symbol', '')
            name = stock.get('name', '')
            
            if not symbol:
                continue
            
            # 生成模拟价格（基于基础价格或随机）
            if 'base_price' in stock:
                base_price = stock['base_price']
            else:
                base_price = random.uniform(5, 200)
            
            # 生成随机涨跌幅 (-5% 到 +5%)
            change_pct = random.uniform(-5, 5)
            price = base_price * (1 + change_pct / 100)
            
            # 生成其他数据
            turnover = random.uniform(1000000, 500000000)  # 成交额
            volume = random.uniform(10000, 10000000)  # 成交量
            high = price * (1 + random.uniform(0, 0.05))  # 最高价
            low = price * (1 - random.uniform(0, 0.05))  # 最低价
            open_price = price * (1 + random.uniform(-0.02, 0.02))  # 开盘价
            
            data = {
                'symbol': symbol,
                'name': name,
                'price': round(price, 2),
                'change': round(change_pct, 2),
                'turnover': round(turnover, 2),
                'volume': round(volume, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'open': round(open_price, 2),
                'update_time': current_time.strftime('%Y-%m-%d %H:%M:%S')
            }
            results.append(data)
        
        df = pd.DataFrame(results)
        self.logger.info(f"生成 {len(df)} 只股票模拟数据")
        return df
    
    def apply_simple_filter(self, stock_data):
        """应用简单筛选"""
        if stock_data.empty:
            return stock_data
        
        filtered = stock_data.copy()
        
        # 基本筛选条件
        filtered = filtered[filtered['turnover'] > 10000000]  # 成交额大于1000万
        filtered = filtered[(filtered['price'] >= 5) & (filtered['price'] <= 500)]  # 价格范围
        filtered = filtered[abs(filtered['change']) <= 5]  # 涨跌幅不超过5%
        
        # 计算评分
        if not filtered.empty:
            # 流动性评分 (0-40分)
            max_turnover = filtered['turnover'].max()
            filtered['liquidity_score'] = (filtered['turnover'] / max_turnover) * 40
            
            # 稳定性评分 (0-30分)
            filtered['stability_score'] = (1 - abs(filtered['change']) / 10) * 30
            
            # 价格合理性评分 (0-30分)
            # 价格在10-100元之间得分较高
            price_scores = []
            for price in filtered['price']:
                if 10 <= price <= 100:
                    score = 30
                elif 5 <= price < 10 or 100 < price <= 200:
                    score = 20
                else:
                    score = 10
                price_scores.append(score)
            filtered['price_score'] = price_scores
            
            # 总分
            filtered['total_score'] = (
                filtered['liquidity_score'] + 
                filtered['stability_score'] + 
                filtered['price_score']
            )
            
            # 排序
            filtered = filtered.sort_values('total_score', ascending=False)
        
        self.logger.info(f"筛选完成: 原始{len(stock_data)}只，筛选后{len(filtered)}只")
        return filtered
    
    def save_results(self, filtered_stocks, all_stocks):
        """保存结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. 保存筛选结果
        if not filtered_stocks.empty:
            result_file = os.path.join(self.stock_pool_dir, f"simple_selected_{timestamp}.csv")
            # 只保存关键列
            cols_to_save = ['symbol', 'name', 'price', 'change', 'turnover', 'total_score']
            filtered_stocks[cols_to_save].to_csv(result_file, index=False, encoding='utf-8')
            self.logger.info(f"筛选结果已保存: {result_file}")
        
        # 2. 更新股票列表
        if not all_stocks.empty:
            list_file = os.path.join(self.data_dir, "stock_list_simple_latest.csv")
            all_stocks.to_csv(list_file, index=False, encoding='utf-8')
            self.logger.info(f"股票列表已更新: {list_file}")
        
        # 3. 保存更新记录
        record = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_stocks': len(all_stocks),
            'filtered_stocks': len(filtered_stocks),
            'data_source': 'simulated',
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
        
        record_file = os.path.join(self.stock_pool_dir, f"simple_record_{timestamp}.json")
        with open(record_file, 'w', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"更新记录已保存: {record_file}")
        
        return record
    
    def generate_summary(self, record):
        """生成摘要"""
        summary = []
        summary.append("=" * 60)
        summary.append("简单股票数据更新摘要")
        summary.append("=" * 60)
        summary.append(f"更新时间: {record['timestamp']}")
        summary.append(f"数据来源: {record['data_source']}")
        summary.append(f"总股票数: {record['total_stocks']}")
        summary.append(f"筛选股票: {record['filtered_stocks']}")
        
        if record['top_5_stocks']:
            summary.append("\n🏆 前5名推荐股票:")
            for i, stock in enumerate(record['top_5_stocks'], 1):
                change_icon = "📈" if stock['change'] > 0 else "📉" if stock['change'] < 0 else "➖"
                summary.append(f"  {i}. {stock['symbol']} {stock['name']} - "
                              f"{stock['price']:.2f}元 ({change_icon}{stock['change']:.2f}%) - "
                              f"综合评分: {stock['score']:.1f}")
        
        summary.append("\n📊 筛选条件:")
        summary.append("  - 成交额 > 1000万元")
        summary.append("  - 价格范围: 5-500元")
        summary.append("  - 涨跌幅: ±5%以内")
        summary.append("  - 评分: 流动性(40%) + 稳定性(30%) + 价格合理性(30%)")
        
        summary.append("\n📁 生成文件:")
        summary.append(f"  - data/stock_list_simple_latest.csv")
        summary.append(f"  - data/stock_pool/simple_selected_*.csv")
        summary.append(f"  - data/stock_pool/simple_record_*.json")
        summary.append(f"  - data/stock_pool/simple_update_*.log")
        
        summary.append("\n" + "=" * 60)
        
        return "\n".join(summary)
    
    def run(self):
        """运行更新流程"""
        self.logger.info("=" * 60)
        self.logger.info("开始简单股票数据更新")
        self.logger.info("=" * 60)
        
        start_time = time.time()
        
        try:
            # 1. 加载现有股票列表
            all_stocks = self.load_existing_stock_list()
            
            if all_stocks.empty:
                self.logger.error("无法加载股票列表")
                return False
            
            # 2. 生成模拟数据
            stock_data = self.generate_simulated_data(all_stocks)
            
            if stock_data.empty:
                self.logger.error("无法生成股票数据")
                return False
            
            # 3. 应用筛选
            filtered_stocks = self.apply_simple_filter(stock_data)
            
            # 4. 保存结果
            record = self.save_results(filtered_stocks, all_stocks)
            
            # 5. 生成摘要
            elapsed_time = time.time() - start_time
            record['elapsed_seconds'] = round(elapsed_time, 1)
            
            summary = self.generate_summary(record)
            print(summary)
            
            # 保存摘要
            summary_file = os.path.join(self.stock_pool_dir, f"simple_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
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
    print("简单股票数据更新系统")
    print("=" * 50)
    print("说明: 使用模拟数据演示更新流程")
    print("=" * 50)
    
    updater = SimpleStockUpdater()
    success = updater.run()
    
    if success:
        print("\n✅ 简单更新成功!")
        print("   使用模拟数据演示了完整的更新流程")
        print("   实际使用时可以替换为真实数据源")
    else:
        print("\n❌ 简单更新失败!")
    
    print("\n" + "=" * 50)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()