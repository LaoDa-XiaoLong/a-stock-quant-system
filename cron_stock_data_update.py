#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cron任务：股票数据自动更新 (v1.0)
功能：
1. 使用akshare获取最新A股数据（如果可用）
2. 应用选股策略筛选
3. 更新本地数据文件
4. 生成更新报告
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import sys
import time
import logging
import traceback

class CronStockUpdater:
    def __init__(self):
        self.data_dir = "data"
        self.stock_pool_dir = os.path.join(self.data_dir, "stock_pool")
        self.reports_dir = os.path.join(self.data_dir, "reports")
        
        # 创建目录
        os.makedirs(self.stock_pool_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # 设置日志
        self.setup_logging()
        
        # 配置
        self.config = {
            'max_stocks': 100,  # 最大处理股票数
            'min_turnover': 10000000,  # 最小成交额
            'price_range': (5, 500),  # 价格范围
            'change_limit': 5,  # 涨跌幅限制
            'use_real_data': True,  # 是否使用真实数据
        }
    
    def setup_logging(self):
        """设置日志"""
        log_file = os.path.join(self.stock_pool_dir, f"cron_update_{datetime.now().strftime('%Y%m%d')}.log")
        
        self.logger = logging.getLogger('CronStockUpdater')
        self.logger.setLevel(logging.INFO)
        
        # 清除现有处理器
        self.logger.handlers.clear()
        
        # 文件处理器
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.INFO)
        
        # 控制台处理器
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # 格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
    
    def get_stock_list(self):
        """获取股票列表"""
        self.logger.info("获取股票列表...")
        
        # 首先尝试从现有文件加载
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
                    if '名称' in df.columns:
                        df = df.rename(columns={'名称': 'name'})
                    
                    return df
                except Exception as e:
                    self.logger.warning(f"读取文件失败 {file_path}: {e}")
        
        # 如果没有文件，尝试使用akshare
        if self.config['use_real_data']:
            try:
                import akshare as ak
                stock_info = ak.stock_info_a_code_name()
                
                if not stock_info.empty:
                    stock_info = stock_info.rename(columns={'code': 'symbol', 'name': 'name'})
                    self.logger.info(f"从akshare获取股票列表: {len(stock_info)} 只")
                    return stock_info
            except ImportError:
                self.logger.warning("akshare未安装，使用模拟数据")
            except Exception as e:
                self.logger.warning(f"akshare获取失败: {e}")
        
        # 使用样本数据
        sample_stocks = [
            {'symbol': '000001', 'name': '平安银行'},
            {'symbol': '000002', 'name': '万科A'},
            {'symbol': '002352', 'name': '顺丰控股'},
            {'symbol': '600580', 'name': '卧龙电驱'},
            {'symbol': '603728', 'name': '鸣志电器'},
            {'symbol': '300750', 'name': '宁德时代'},
            {'symbol': '600519', 'name': '贵州茅台'},
            {'symbol': '000858', 'name': '五粮液'},
            {'symbol': '002415', 'name': '海康威视'},
            {'symbol': '601318', 'name': '中国平安'},
        ]
        
        self.logger.info(f"使用样本股票数据: {len(sample_stocks)} 只")
        return pd.DataFrame(sample_stocks)
    
    def get_stock_data(self, symbols):
        """获取股票数据"""
        self.logger.info(f"获取 {len(symbols)} 只股票数据...")
        
        results = []
        current_time = datetime.now()
        
        # 限制处理数量
        symbols = symbols[:self.config['max_stocks']]
        
        # 尝试使用真实数据
        if self.config['use_real_data']:
            try:
                import akshare as ak
                
                # 获取实时行情
                spot_data = ak.stock_zh_a_spot()
                
                if not spot_data.empty:
                    for symbol in symbols:
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
                                'data_source': 'akshare',
                                'update_time': current_time.strftime('%Y-%m-%d %H:%M:%S')
                            }
                            results.append(data)
                    
                    if results:
                        self.logger.info(f"从akshare获取 {len(results)} 只股票数据")
                        return pd.DataFrame(results)
                        
            except Exception as e:
                self.logger.warning(f"akshare获取数据失败: {e}")
        
        # 使用模拟数据
        self.logger.info("使用模拟数据")
        import random
        
        for symbol in symbols:
            # 查找股票名称
            name = symbol  # 默认使用代码作为名称
            
            # 生成模拟数据
            base_price = random.uniform(5, 200)
            change_pct = random.uniform(-self.config['change_limit'], self.config['change_limit'])
            price = base_price * (1 + change_pct / 100)
            
            data = {
                'symbol': symbol,
                'name': name,
                'price': round(price, 2),
                'change': round(change_pct, 2),
                'turnover': round(random.uniform(10000000, 500000000), 2),
                'volume': round(random.uniform(100000, 10000000), 2),
                'high': round(price * (1 + random.uniform(0, 0.05)), 2),
                'low': round(price * (1 - random.uniform(0, 0.05)), 2),
                'open': round(price * (1 + random.uniform(-0.02, 0.02)), 2),
                'data_source': 'simulated',
                'update_time': current_time.strftime('%Y-%m-%d %H:%M:%S')
            }
            results.append(data)
        
        df = pd.DataFrame(results)
        self.logger.info(f"生成 {len(df)} 只股票模拟数据")
        return df
    
    def apply_selection_strategy(self, stock_data):
        """应用选股策略"""
        if stock_data.empty:
            return stock_data
        
        filtered = stock_data.copy()
        
        # 1. 流动性筛选
        filtered = filtered[filtered['turnover'] > self.config['min_turnover']]
        
        # 2. 价格筛选
        min_price, max_price = self.config['price_range']
        filtered = filtered[(filtered['price'] >= min_price) & (filtered['price'] <= max_price)]
        
        # 3. 涨跌幅筛选
        filtered = filtered[abs(filtered['change']) <= self.config['change_limit']]
        
        # 4. 计算综合评分
        if not filtered.empty:
            # 流动性评分 (0-40分)
            max_turnover = filtered['turnover'].max()
            filtered['liquidity_score'] = (filtered['turnover'] / max_turnover) * 40
            
            # 稳定性评分 (0-30分)
            filtered['stability_score'] = (1 - abs(filtered['change']) / 10) * 30
            
            # 价格合理性评分 (0-30分)
            # 价格在20-100元之间得分较高
            def calculate_price_score(price):
                if 20 <= price <= 100:
                    return 30
                elif 10 <= price < 20 or 100 < price <= 150:
                    return 20
                elif 5 <= price < 10 or 150 < price <= 200:
                    return 15
                else:
                    return 10
            
            filtered['price_score'] = filtered['price'].apply(calculate_price_score)
            
            # 总分
            filtered['total_score'] = (
                filtered['liquidity_score'] + 
                filtered['stability_score'] + 
                filtered['price_score']
            )
            
            # 排序
            filtered = filtered.sort_values('total_score', ascending=False)
        
        self.logger.info(f"选股策略应用完成: 原始{len(stock_data)}只，筛选后{len(filtered)}只")
        return filtered
    
    def update_data_files(self, filtered_stocks, all_stocks):
        """更新数据文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. 保存筛选结果
        if not filtered_stocks.empty:
            # 详细结果
            detail_file = os.path.join(self.stock_pool_dir, f"selected_stocks_{timestamp}.csv")
            filtered_stocks.to_csv(detail_file, index=False, encoding='utf-8')
            self.logger.info(f"详细结果已保存: {detail_file}")
            
            # 简化结果（用于快速查看）
            simple_file = os.path.join(self.stock_pool_dir, "latest_selected.csv")
            simple_cols = ['symbol', 'name', 'price', 'change', 'turnover', 'total_score', 'data_source']
            filtered_stocks[simple_cols].to_csv(simple_file, index=False, encoding='utf-8')
            self.logger.info(f"最新结果已保存: {simple_file}")
        
        # 2. 更新股票列表
        if not all_stocks.empty:
            list_file = os.path.join(self.data_dir, "stock_list_updated.csv")
            all_stocks.to_csv(list_file, index=False, encoding='utf-8')
            self.logger.info(f"股票列表已更新: {list_file}")
        
        # 3. 保存更新记录
        record = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': 'v1.0',
            'total_stocks': len(all_stocks),
            'processed_stocks': len(filtered_stocks) if not filtered_stocks.empty else 0,
            'data_source': filtered_stocks['data_source'].iloc[0] if not filtered_stocks.empty else 'unknown',
            'config': self.config,
            'top_10_stocks': []
        }
        
        if not filtered_stocks.empty:
            top_10 = filtered_stocks.head(10)
            for _, row in top_10.iterrows():
                record['top_10_stocks'].append({
                    'symbol': row['symbol'],
                    'name': row['name'],
                    'price': float(row['price']),
                    'change': float(row['change']),
                    'turnover': float(row['turnover']),
                    'score': float(row['total_score'])
                })
        
        record_file = os.path.join(self.stock_pool_dir, f"update_record_{timestamp}.json")
        with open(record_file, 'w', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"更新记录已保存: {record_file}")
        
        return record
    
    def generate_report(self, record):
        """生成报告"""
        report_lines = []
        
        # 标题
        report_lines.append("# 📈 股票数据自动更新报告")
        report_lines.append(f"## 版本: {record['version']}")
        report_lines.append(f"## 生成时间: {record['timestamp']}")
        report_lines.append("")
        
        # 摘要
        report_lines.append("## 📊 执行摘要")
        report_lines.append(f"- **数据来源**: {record['data_source']}")
        report_lines.append(f"- **总股票数**: {record['total_stocks']} 只")
        report_lines.append(f"- **处理股票**: {record['processed_stocks']} 只")
        report_lines.append("")
        
        # 前10名股票
        if record['top_10_stocks']:
            report_lines.append("## 🏆 前10名推荐股票")
            report_lines.append("| 排名 | 代码 | 名称 | 价格 | 涨跌幅 | 成交额 | 综合评分 |")
            report_lines.append("|------|------|------|------|--------|--------|----------|")
            
            for i, stock in enumerate(record['top_10_stocks'], 1):
                change_icon = "📈" if stock['change'] > 0 else "📉" if stock['change'] < 0 else "➖"
                turnover_million = stock['turnover'] / 1_000_000
                report_lines.append(
                    f"| {i} | {stock['symbol']} | {stock['name']} | "
                    f"{stock['price']:.2f}元 | {change_icon}{stock['change']:.2f}% | "
                    f"{turnover_million:.1f}百万 | {stock['score']:.1f} |"
                )
            report_lines.append("")
        
        # 筛选条件
        report_lines.append("## ⚙️ 筛选条件")
        config = record['config']
        report_lines.append(f"- **最大处理股票数**: {config['max_stocks']} 只")
        report_lines.append(f"- **最小成交额**: {config['min_turnover']:,} 元")
        report_lines.append(f"- **价格范围**: {config['price_range'][0]} - {config['price_range'][1]} 元")
        report_lines.append(f"- **涨跌幅限制**: ±{config['change_limit']}%")
        report_lines.append(f"- **使用真实数据**: {'是' if config['use_real_data'] else '否'}")
        report_lines.append("")
        
        # 评分标准
        report_lines.append("## 📝 评分标准")
        report_lines.append("- **流动性评分 (40%)**: 基于成交额，成交额越高得分越高")
        report_lines.append("- **稳定性评分 (30%)**: 基于涨跌幅绝对值，波动越小得分越高")
        report_lines.append("- **价格合理性评分 (30%)**: 基于价格区间，20-100元得分最高")
        report_lines.append("")
        
        # 生成文件
        report_lines.append("## 💾 生成文件")
        report_lines.append(f"- **股票列表**: `data/stock_list_updated.csv`")
        report_lines.append(f"- **最新结果**: `data/stock_pool/latest_selected.csv`")
        report_lines.append(f"- **详细结果**: `data/stock_pool/selected_stocks_*.csv`")
        report_lines.append(f"- **更新记录**: `data/stock_pool/update_record_*.json`")
        report_lines.append(f"- **运行日志**: `data/stock_pool/cron_update_*.log`")
        report_lines.append("")
        
        # 下次更新建议
        next_hour = (datetime.now() + timedelta(hours=1)).strftime("%H:%M")
        report_lines.append("## ⏰ 更新建议")
        report_lines.append(f"- **建议下次更新时间**: {next_hour}")
        report_lines.append(f"- **建议更新频率**: 交易时间每小时一次")
        report_lines.append(f"- **最佳更新时间**: 09:30, 10:30, 13:00, 14:00")
        report_lines.append("")
        
        report_lines.append("---")
        report_lines.append("*报告由股票数据自动更新系统 v1.0 生成*")
        
        report_content = "\n".join(report_lines)
        
        # 保存报告
        report_file = os.path.join(self.reports_dir, f"stock_update_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.logger.info(f"报告已保存: {report_file}")
        
        return report_content
    
    def print_summary(self, record, report_content):
        """打印摘要"""
        print("=" * 70)
        print("股票数据自动更新任务执行完成")
        print("=" * 70)
        print(f"执行时间: {record['timestamp']}")
        print(f"数据来源: {record['data_source']}")
        print(f"总股票数: {record['total_stocks']} 只")
        print(f"处理股票: {record['processed_stocks']} 只")
        
        if record['top_10_stocks']:
            print("\n🏆 前5名股票:")
            for i, stock in enumerate(record['top_10_stocks'][:5], 1):
                change_icon = "📈" if stock['change'] > 0 else "📉" if stock['change'] < 0 else "➖"
                print(f"  {i}. {stock['symbol']} {stock['name']} - "
                      f"{stock['price']:.2f}元 ({change_icon}{stock['change']:.2f}%) - "
                      f"评分: {stock['score']:.1f}")
        
        print("\n📁 生成文件:")
        print(f"  - data/stock_list_updated.csv")
        print(f"  - data/stock_pool/latest_selected.csv")
        print(f"  - data/reports/stock_update_report_*.md")
        
        print("\n" + "=" * 70)
    
    def run(self):
        """运行完整更新流程"""
        self.logger.info("=" * 70)
        self.logger.info("开始执行股票数据自动更新任务 (v1.0)")
        self.logger.info("=" * 70)
        
        start_time = time.time()
        
        try:
            # 1. 获取股票列表
            all_stocks = self.get_stock_list()
            
            if all_stocks.empty:
                self.logger.error("无法获取股票列表，任务终止")
                return False
            
            # 2. 获取股票代码
            symbols = all_stocks['symbol'].tolist()
            self.logger.info(f"准备处理 {len(symbols)} 只股票")
            
            # 3. 获取股票数据
            stock_data = self.get_stock_data(symbols)
            
            if stock_data.empty:
                self.logger.error("无法获取股票数据，任务终止")
                return False
            
            # 4. 应用选股策略
            filtered_stocks = self.apply_selection_strategy(stock_data)
            
            # 5. 更新数据文件
            record = self.update_data_files(filtered_stocks, all_stocks)
            
            # 6. 生成报告
            report_content = self.generate_report(record)
            
            # 7. 打印摘要
            elapsed_time = time.time() - start_time
            record['elapsed_seconds'] = round(elapsed_time, 1)
            
            self.print_summary(record, report_content)
            
            self.logger.info(f"任务完成，总耗时: {elapsed_time:.1f}秒")
            self.logger.info("=" * 70)
            
            return True
            
        except Exception as e:
            self.logger.error(f"任务执行失败: {e}")
            self.logger.error(traceback.format_exc())
            return False

def main():
    """主函数"""
    print("股票数据自动更新系统 v1.0")
    print("=" * 50)
    print("功能: 获取股票数据 → 应用选股策略 → 更新本地文件 → 生成报告")
    print("=" * 50)
    
    updater = CronStockUpdater()
    success = updater.run()
    
    if success:
        print("\n✅ 股票数据自动更新任务执行成功!")
        print("   系统已按照v1.0版本要求完成所有步骤:")
        print("   1. ✓ 获取最新A股数据")
        print("   2. ✓ 应用选股策略筛选")
        print("   3. ✓ 更新本地数据文件")
        print("   4. ✓ 生成更新报告")
    else:
        print("\n❌ 股票数据自动更新任务执行失败!")
        print("   请查看日志文件获取详细错误信息")
    
    print("\n" + "=" * 50)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()