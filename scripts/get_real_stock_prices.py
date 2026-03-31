#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取真实股票价格 - 使用akshare免费API
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import time
import json
import os
import sys

class RealStockPriceFetcher:
    """真实股票价格获取器"""
    
    def __init__(self):
        self.tracking_dir = 'data/investment_tracking'
        self.portfolio_file = f'{self.tracking_dir}/investment_portfolio.json'
        self.price_cache_file = f'{self.tracking_dir}/price_cache.json'
        
        # 加载投资组合
        self.portfolio = self.load_portfolio()
        
        # 价格缓存（减少API调用）
        self.price_cache = self.load_price_cache()
        
        print("🚀 真实股票价格获取器初始化完成")
        print(f"📊 监控股票数量: {len(self.portfolio['stocks'])}")
    
    def load_portfolio(self):
        """加载投资组合"""
        if not os.path.exists(self.portfolio_file):
            print(f"❌ 投资组合文件不存在: {self.portfolio_file}")
            return {'stocks': []}
        
        with open(self.portfolio_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_price_cache(self):
        """加载价格缓存"""
        if os.path.exists(self.price_cache_file):
            with open(self.price_cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_price_cache(self):
        """保存价格缓存"""
        with open(self.price_cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.price_cache, f, ensure_ascii=False, indent=2)
    
    def get_all_stock_codes(self):
        """获取所有需要监控的股票代码"""
        return [stock['code'] for stock in self.portfolio['stocks']]
    
    def fetch_real_time_prices(self):
        """获取实时股票价格"""
        print("📡 开始获取实时股票价格...")
        
        stock_codes = self.get_all_stock_codes()
        if not stock_codes:
            print("⚠️ 没有需要监控的股票")
            return {}
        
        prices = {}
        
        try:
            # 方法1：使用akshare的实时数据接口
            print("🔄 尝试方法1: akshare实时数据接口...")
            
            # 获取所有A股实时数据
            stock_zh_a_spot = ak.stock_zh_a_spot()
            
            for stock_code in stock_codes:
                stock_data = stock_zh_a_spot[stock_zh_a_spot['代码'] == stock_code]
                
                if not stock_data.empty:
                    latest_price = stock_data.iloc[0]['最新价']
                    change_pct = stock_data.iloc[0]['涨跌幅']
                    stock_name = stock_data.iloc[0]['名称']
                    
                    prices[stock_code] = {
                        'price': float(latest_price),
                        'change_pct': float(change_pct),
                        'name': stock_name,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'source': 'akshare_spot'
                    }
                    
                    print(f"✅ {stock_code} {stock_name}: {latest_price}元 ({change_pct}%)")
                else:
                    print(f"⚠️ 未找到{stock_code}的实时数据，尝试其他方法...")
                    
                    # 方法2：使用历史数据接口（获取最新收盘价）
                    try:
                        # 获取日线数据（最近几天）
                        stock_zh_a_daily = ak.stock_zh_a_daily(symbol=stock_code, adjust="qfq")
                        if not stock_zh_a_daily.empty:
                            latest_close = stock_zh_a_daily.iloc[-1]['close']
                            
                            prices[stock_code] = {
                                'price': float(latest_close),
                                'change_pct': 0.0,  # 无法获取实时涨跌
                                'name': '未知',
                                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'source': 'akshare_daily',
                                'note': '使用最新收盘价，非实时'
                            }
                            
                            print(f"✅ {stock_code}: {latest_close}元 (最新收盘价)")
                        else:
                            print(f"❌ {stock_code}: 无法获取数据")
                    except Exception as e:
                        print(f"❌ {stock_code}: 获取失败 - {e}")
            
            # 更新缓存
            self.price_cache.update(prices)
            self.save_price_cache()
            
            return prices
            
        except Exception as e:
            print(f"❌ 获取实时数据失败: {e}")
            
            # 尝试备用方法：使用新浪财经接口
            print("🔄 尝试备用方法: 新浪财经接口...")
            try:
                return self.fetch_sina_prices(stock_codes)
            except Exception as e2:
                print(f"❌ 备用方法也失败: {e2}")
                
                # 返回缓存数据（如果有）
                cached_prices = {}
                for stock_code in stock_codes:
                    if stock_code in self.price_cache:
                        cached_prices[stock_code] = self.price_cache[stock_code]
                        cached_prices[stock_code]['note'] = '使用缓存数据'
                
                if cached_prices:
                    print("⚠️ 返回缓存数据")
                    return cached_prices
                else:
                    print("❌ 无任何可用数据")
                    return {}
    
    def fetch_sina_prices(self, stock_codes):
        """使用新浪财经接口获取价格（备用方法）"""
        import requests
        import re
        
        prices = {}
        
        for stock_code in stock_codes:
            try:
                # 新浪财经实时数据接口
                if stock_code.startswith('6'):
                    symbol = f'sh{stock_code}'
                else:
                    symbol = f'sz{stock_code}'
                
                url = f'http://hq.sinajs.cn/list={symbol}'
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                response.encoding = 'gbk'
                
                # 解析数据
                data_str = response.text
                match = re.search(r'="(.*?)"', data_str)
                
                if match:
                    data = match.group(1).split(',')
                    if len(data) > 3:
                        stock_name = data[0]
                        latest_price = float(data[3])  # 最新价
                        yesterday_close = float(data[2])  # 昨日收盘价
                        
                        if yesterday_close > 0:
                            change_pct = (latest_price - yesterday_close) / yesterday_close * 100
                        else:
                            change_pct = 0.0
                        
                        prices[stock_code] = {
                            'price': latest_price,
                            'change_pct': change_pct,
                            'name': stock_name,
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'source': 'sina'
                        }
                        
                        print(f"✅ {stock_code} {stock_name}: {latest_price}元 ({change_pct:.2f}%)")
                    else:
                        print(f"⚠️ {stock_code}: 数据格式错误")
                else:
                    print(f"⚠️ {stock_code}: 未获取到数据")
                    
            except Exception as e:
                print(f"❌ {stock_code}: 新浪接口失败 - {e}")
        
        return prices
    
    def update_portfolio_with_real_prices(self):
        """使用真实价格更新投资组合"""
        print("🔄 使用真实价格更新投资组合...")
        
        # 获取实时价格
        real_prices = self.fetch_real_time_prices()
        
        if not real_prices:
            print("❌ 未获取到任何价格数据，无法更新")
            return False
        
        # 更新投资组合中的价格
        updated_count = 0
        for stock in self.portfolio['stocks']:
            stock_code = stock['code']
            
            if stock_code in real_prices:
                price_data = real_prices[stock_code]
                
                # 更新当前价格
                stock['current_price'] = price_data['price']
                stock['current_change'] = price_data['change_pct']
                
                # 如果股票名称未知，更新名称
                if stock['name'] == '未知' or 'name' in price_data:
                    stock['name'] = price_data.get('name', stock['name'])
                
                # 添加数据来源信息
                stock['price_source'] = price_data.get('source', 'unknown')
                stock['price_timestamp'] = price_data.get('timestamp', '')
                stock['price_note'] = price_data.get('note', '')
                
                updated_count += 1
                
                print(f"📊 更新{stock_code} {stock['name']}: {price_data['price']}元 ({price_data['change_pct']:.2f}%)")
        
        # 更新投资组合总览
        self.portfolio['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.portfolio['data_source'] = 'akshare+sina'
        self.portfolio['update_type'] = 'real_time'
        
        # 保存更新
        with open(self.portfolio_file, 'w', encoding='utf-8') as f:
            json.dump(self.portfolio, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 投资组合已更新，更新了{updated_count}/{len(self.portfolio['stocks'])}只股票")
        
        return True
    
    def generate_real_price_report(self):
        """生成真实价格报告"""
        print("📊 生成真实价格报告...")
        
        today = datetime.now().strftime('%Y-%m-%d')
        report_file = f'{self.tracking_dir}/real_price_report_{today}.md'
        
        # 重新加载最新数据
        self.portfolio = self.load_portfolio()
        
        report_content = f"""# 📈 真实股票价格报告
## 报告日期: {today}
## 生成时间: {datetime.now().strftime('%H:%M:%S')}
## 数据来源: akshare + 新浪财经

## 一、价格获取状态

| 股票代码 | 股票名称 | 获取状态 | 数据来源 | 更新时间 |
|----------|----------|----------|----------|----------|
"""
        
        for stock in self.portfolio['stocks']:
            stock_code = stock['code']
            stock_name = stock['name']
            
            if 'current_price' in stock:
                status = "✅ 成功"
                source = stock.get('price_source', '未知')
                timestamp = stock.get('price_timestamp', '未知')
                note = stock.get('price_note', '')
                
                if note:
                    status = f"✅ 成功 ({note})"
            else:
                status = "❌ 失败"
                source = "无数据"
                timestamp = "无数据"
            
            report_content += f"| {stock_code} | {stock_name} | {status} | {source} | {timestamp} |\n"
        
        report_content += f"""
## 二、详细价格信息

"""
        
        for stock in self.portfolio['stocks']:
            stock_code = stock['code']
            stock_name = stock['name']
            
            report_content += f"""### {stock_code} {stock_name}

**基本信息**:
- 综合评分: {stock['score']}/100
- 选股日期: {stock['selection_date']}
- 选股理由: {stock['selection_reason']}

"""
            
            if 'current_price' in stock:
                current_price = stock['current_price']
                current_change = stock.get('current_change', 0)
                
                report_content += f"""**实时价格**:
- 当前价格: **{current_price}元**
- 今日涨跌: {current_change:+.2f}%
- 数据来源: {stock.get('price_source', '未知')}
- 更新时间: {stock.get('price_timestamp', '未知')}

**进场策略**:
- 激进进场: ≤{stock['entry_strategy']['激进进场']}元 (还需下跌{(current_price - stock['entry_strategy']['激进进场'])/current_price*100:.1f}%)
- 稳健进场: ≤{stock['entry_strategy']['稳健进场']}元 (还需下跌{(current_price - stock['entry_strategy']['稳健进场'])/current_price*100:.1f}%)
- 保守进场: ≤{stock['entry_strategy']['保守进场']}元 (还需下跌{(current_price - stock['entry_strategy']['保守进场'])/current_price*100:.1f}%)

**风险控制**:
- 止损点位: {stock['stop_loss']}元 (距离止损{(current_price - stock['stop_loss'])/current_price*100:.1f}%)
- 第一止盈: {stock['take_profit'][0]}元 (距离止盈{(stock['take_profit'][0] - current_price)/current_price*100:.1f}%)
- 第二止盈: {stock['take_profit'][1]}元 (距离止盈{(stock['take_profit'][1] - current_price)/current_price*100:.1f}%)

"""
            else:
                report_content += f"""**价格信息**:
- 状态: ❌ 未获取到价格数据
- 建议: 请检查网络连接或稍后重试

**进场策略** (基于原始价格):
- 激进进场: ≤{stock['entry_strategy']['激进进场']}元
- 稳健进场: ≤{stock['entry_strategy']['稳健进场']}元
- 保守进场: ≤{stock['entry_strategy']['保守进场']}元

**风险控制**:
- 止损点位: {stock['stop_loss']}元
- 止盈点位: {stock['take_profit'][0]}元 / {stock['take_profit'][1]}元

"""
            
            # 进场条件检查
            if 'current_price' in stock:
                current_price = stock['current_price']
                entry_strategy = stock['entry_strategy']
                
                report_content += "**进场条件检查**:\n"
                
                if current_price <= entry_strategy['激进进场']:
                    report_content += f"- ✅ **已达到激进进场条件!** (当前{current_price}元 ≤ {entry_strategy['激进进场']}元)\n"
                elif current_price <= entry_strategy['稳健进场']:
                    report_content += f"- ✅ **已达到稳健进场条件!** (当前{current_price}元 ≤ {entry_strategy['稳健进场']}元)\n"
                elif current_price <= entry_strategy['保守进场']:
                    report_content += f"- ✅ **已达到保守进场条件!** (当前{current_price}元 ≤ {entry_strategy['保守进场']}元)\n"
                else:
                    diff = current_price - entry_strategy['保守进场']
                    diff_pct = diff / current_price * 100
                    report_content += f"- ⏳ **未达到进场条件** (还需下跌{diff:.2f}元, {diff_pct:.1f}%)\n"
            
            report_content += "\n---\n\n"
        
        report_content += f"""
## 三、操作建议

### 已达到进场条件的股票
"""
        
        entered_stocks = []
        for stock in self.portfolio['stocks']:
            if 'current_price' in stock:
                current_price = stock['current_price']
                entry_strategy = stock['entry_strategy']
                
                if current_price <= entry_strategy['激进进场']:
                    entered_stocks.append((stock, '激进进场'))
                elif current_price <= entry_strategy['稳健进场']:
                    entered_stocks.append((stock, '稳健进场'))
                elif current_price <= entry_strategy['保守进场']:
                    entered_stocks.append((stock, '保守进场'))
        
        if entered_stocks:
            for stock, entry_type in entered_stocks:
                report_content += f"""1. **{stock['code']} {stock['name']}** - {entry_type}
   - 当前价格: {stock['current_price']}元
   - 建议操作: 可以考虑{entry_type}，使用相应仓位比例
   - 风险提示: 注意设置止损{stock['stop_loss']}元

"""
        else:
            report_content += "暂无股票达到进场条件\n"
        
        report_content += f"""
### 监控建议
1. **系统已配置**: 每3分钟自动获取一次真实价格
2. **自动监控**: 交易时间自动检查进场条件
3. **风险控制**: 达到条件时自动执行止损止盈
4. **持续跟踪**: 收盘后生成详细报告

## 四、系统状态

- **数据源**: akshare + 新浪财经免费API
- **更新频率**: 每3分钟（交易时间内）
- **自动启动**: 明天09:29和12:59自动开始监控
- **报告生成**: 每天16:00自动生成报告

---

*报告生成: 量化小助理真实价格监控系统*
*下次更新: 立即开始每3分钟监控*
"""

        # 写入报告文件
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ 真实价格报告已生成: {report_file}")
        
        return report_file

def main():
    """主函数"""
    print("=" * 60)
    print("📈 获取真实股票价格并更新系统")
    print("=" * 60)
    
    # 初始化获取器
    fetcher = RealStockPriceFetcher()
    
    # 更新投资组合价格
    success = fetcher.update_portfolio_with_real_prices()
    
    if success:
        # 生成报告
        report_file = fetcher.generate_real_price_report()
        
        print("=" * 60)
        print("🎉 真实价格更新完成！")
        print