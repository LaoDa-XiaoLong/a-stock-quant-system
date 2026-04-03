#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cron任务专用股票数据更新脚本
简化版本，专注于核心功能
"""

import pandas as pd
import akshare as ak
from datetime import datetime
import json
import os
import sys
import time

def setup_logging():
    """设置日志"""
    import logging
    log_dir = "data/stock_pool"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"cron_update_{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def get_stock_list():
    """获取股票列表"""
    logger.info("获取A股股票列表...")
    try:
        stock_info = ak.stock_info_a_code_name()
        logger.info(f"获取到 {len(stock_info)} 只A股股票")
        return stock_info
    except Exception as e:
        logger.error(f"获取股票列表失败: {e}")
        return pd.DataFrame()

def get_sample_stocks(stock_info, count=50):
    """获取样本股票"""
    if stock_info.empty:
        return []
    
    # 选择前count只股票作为样本
    symbols = stock_info['code'].head(count).tolist()
    logger.info(f"选择 {len(symbols)} 只样本股票")
    return symbols

def update_stock_data(symbols):
    """更新股票数据"""
    logger.info(f"开始更新 {len(symbols)} 只股票数据...")
    
    results = []
    
    for i, symbol in enumerate(symbols, 1):
        try:
            # 获取实时数据
            spot_data = ak.stock_zh_a_spot()
            stock_data = spot_data[spot_data['代码'] == symbol]
            
            if not stock_data.empty:
                data = {
                    'symbol': symbol,
                    'name': stock_data.iloc[0]['名称'],
                    'price': float(stock_data.iloc[0]['最新价']),
                    'change': float(stock_data.iloc[0]['涨跌幅']),
                    'turnover': float(stock_data.iloc[0]['成交额']),
                    'volume': float(stock_data.iloc[0]['成交量']),
                    'high': float(stock_data.iloc[0]['最高']),
                    'low': float(stock_data.iloc[0]['最低']),
                    'open': float(stock_data.iloc[0]['今开']),
                    'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                results.append(data)
            
            if i % 10 == 0:
                logger.info(f"更新进度: {i}/{len(symbols)}")
                
        except Exception as e:
            logger.warning(f"更新股票{symbol}失败: {e}")
            continue
    
    logger.info(f"股票数据更新完成: 成功{len(results)}只，失败{len(symbols)-len(results)}只")
    return pd.DataFrame(results)

def apply_simple_filter(stock_data):
    """应用简单筛选"""
    if stock_data.empty:
        return stock_data
    
    filtered = stock_data.copy()
    
    # 1. 流动性筛选（成交额大于1000万）
    filtered = filtered[filtered['turnover'] > 10000000]
    
    # 2. 价格筛选（5-500元）
    filtered = filtered[(filtered['price'] >= 5) & (filtered['price'] <= 500)]
    
    # 3. 涨跌幅筛选（-5%到5%）
    filtered = filtered[(filtered['change'] >= -5) & (filtered['change'] <= 5)]
    
    # 4. 计算简单评分
    filtered['score'] = 50  # 基础分
    
    # 流动性评分
    if filtered['turnover'].max() > 0:
        filtered['score'] += (filtered['turnover'] / filtered['turnover'].max()) * 30
    
    # 稳定性评分（涨跌幅绝对值越小越好）
    filtered['score'] += (1 - abs(filtered['change']) / 10) * 20
    
    # 排序
    filtered = filtered.sort_values('score', ascending=False)
    
    logger.info(f"筛选完成: 原始{len(stock_data)}只，筛选后{len(filtered)}只")
    return filtered

def save_results(filtered_stocks, all_stocks):
    """保存结果"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. 保存筛选结果
    if not filtered_stocks.empty:
        result_file = f"data/stock_pool/cron_selected_{timestamp}.csv"
        filtered_stocks.to_csv(result_file, index=False, encoding='utf-8')
        logger.info(f"筛选结果已保存: {result_file}")
    
    # 2. 更新最新股票列表
    if not all_stocks.empty:
        list_file = "data/stock_list_latest.csv"
        all_stocks.to_csv(list_file, index=False, encoding='utf-8')
        logger.info(f"股票列表已更新: {list_file}")
    
    # 3. 保存更新记录
    record = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_stocks': len(all_stocks),
        'filtered_stocks': len(filtered_stocks),
        'top_stocks': []
    }
    
    if not filtered_stocks.empty:
        top_5 = filtered_stocks.head(5)
        for _, row in top_5.iterrows():
            record['top_stocks'].append({
                'symbol': row['symbol'],
                'name': row['name'],
                'price': float(row['price']),
                'score': float(row['score'])
            })
    
    record_file = f"data/stock_pool/cron_record_{timestamp}.json"
    with open(record_file, 'w', encoding='utf-8') as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    
    logger.info(f"更新记录已保存: {record_file}")
    
    return record

def generate_summary(record):
    """生成摘要"""
    summary = []
    summary.append("=" * 60)
    summary.append("股票数据自动更新摘要")
    summary.append("=" * 60)
    summary.append(f"更新时间: {record['timestamp']}")
    summary.append(f"总股票数: {record['total_stocks']}")
    summary.append(f"筛选股票: {record['filtered_stocks']}")
    
    if record['top_stocks']:
        summary.append("\n🏆 前5名股票:")
        for i, stock in enumerate(record['top_stocks'], 1):
            summary.append(f"  {i}. {stock['symbol']} {stock['name']} - "
                          f"{stock['price']:.2f}元 (评分: {stock['score']:.1f})")
    
    summary.append("\n📁 生成文件:")
    summary.append(f"  - data/stock_list_latest.csv")
    summary.append(f"  - data/stock_pool/cron_selected_*.csv")
    summary.append(f"  - data/stock_pool/cron_record_*.json")
    summary.append(f"  - data/stock_pool/cron_update_*.log")
    
    summary.append("\n" + "=" * 60)
    
    return "\n".join(summary)

def main():
    """主函数"""
    global logger
    logger = setup_logging()
    
    start_time = time.time()
    
    logger.info("=" * 60)
    logger.info("开始执行Cron股票数据更新任务")
    logger.info("=" * 60)
    
    try:
        # 1. 获取股票列表
        all_stocks = get_stock_list()
        
        if all_stocks.empty:
            logger.error("无法获取股票列表，任务终止")
            return False
        
        # 2. 选择样本股票（为了速度，只更新前50只）
        sample_symbols = get_sample_stocks(all_stocks, count=50)
        
        if not sample_symbols:
            logger.error("没有可更新的股票")
            return False
        
        # 3. 更新股票数据
        stock_data = update_stock_data(sample_symbols)
        
        if stock_data.empty:
            logger.error("股票数据更新失败")
            return False
        
        # 4. 应用筛选策略
        filtered_stocks = apply_simple_filter(stock_data)
        
        # 5. 保存结果
        record = save_results(filtered_stocks, all_stocks)
        
        # 6. 生成摘要
        elapsed_time = time.time() - start_time
        record['elapsed_seconds'] = round(elapsed_time, 1)
        
        summary = generate_summary(record)
        print(summary)
        
        # 保存摘要文件
        summary_file = f"data/stock_pool/cron_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        logger.info(f"任务完成，耗时: {elapsed_time:.1f}秒")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"任务执行失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)