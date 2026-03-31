#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试获取真实股票价格
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import json
import os

print("🧪 测试获取真实股票价格")
print("=" * 50)

# 测试股票代码
test_codes = ['000020', '000010', '000004', '000027', '000009']

try:
    print("1. 测试akshare实时数据接口...")
    
    # 获取所有A股实时数据
    stock_zh_a_spot = ak.stock_zh_a_spot()
    print(f"✅ 获取到{len(stock_zh_a_spot)}只A股实时数据")
    
    # 查找我们的股票
    for code in test_codes:
        stock_data = stock_zh_a_spot[stock_zh_a_spot['代码'] == code]
        
        if not stock_data.empty:
            name = stock_data.iloc[0]['名称']
            price = stock_data.iloc[0]['最新价']
            change = stock_data.iloc[0]['涨跌幅']
            print(f"✅ {code} {name}: {price}元 ({change}%)")
        else:
            print(f"❌ {code}: 未在实时数据中找到")
            
            # 尝试获取历史数据
            try:
                stock_zh_a_daily = ak.stock_zh_a_daily(symbol=code, adjust="qfq")
                if not stock_zh_a_daily.empty:
                    latest_close = stock_zh_a_daily.iloc[-1]['close']
                    print(f"   📅 最新收盘价: {latest_close}元")
                else:
                    print(f"   ❌ 也无法获取历史数据")
            except Exception as e:
                print(f"   ❌ 获取历史数据失败: {e}")
    
except Exception as e:
    print(f"❌ akshare接口失败: {e}")
    
    # 尝试新浪财经接口
    print("\n2. 测试新浪财经接口...")
    import requests
    import re
    
    for code in test_codes:
        try:
            if code.startswith('6'):
                symbol = f'sh{code}'
            else:
                symbol = f'sz{code}'
            
            url = f'http://hq.sinajs.cn/list={symbol}'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'gbk'
            
            data_str = response.text
            match = re.search(r'="(.*?)"', data_str)
            
            if match:
                data = match.group(1).split(',')
                if len(data) > 3:
                    name = data[0]
                    price = float(data[3])
                    yesterday_close = float(data[2])
                    
                    if yesterday_close > 0:
                        change = (price - yesterday_close) / yesterday_close * 100
                    else:
                        change = 0.0
                    
                    print(f"✅ {code} {name}: {price}元 ({change:.2f}%)")
                else:
                    print(f"❌ {code}: 数据格式错误")
            else:
                print(f"❌ {code}: 未获取到数据")
                
        except Exception as e2:
            print(f"❌ {code}: 新浪接口失败 - {e2}")

print("\n" + "=" * 50)
print("💡 建议: 使用新浪财经接口作为主要数据源，akshare作为备用")