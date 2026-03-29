# 美股免费数据源调研报告

## 📋 调研目标
寻找适合A股交易系统的美股免费数据源，用于：
1. 美股-A股联动分析
2. 科技股全球影响分析
3. 第六维度（科技地缘政治）数据支持

## 🔍 调研方法
1. 测试各免费API的可用性和稳定性
2. 评估数据完整性和实时性
3. 分析调用限制和扩展性
4. 考虑长期可持续性

## 📊 候选数据源评估

### 1. Alpha Vantage ⭐⭐⭐⭐⭐
**网址**: https://www.alphavantage.co/

**免费层限制**:
- 500次API调用/天
- 5次API调用/分钟
- 支持实时和历史数据

**支持的数据**:
- ✅ 实时股价（有15分钟延迟）
- ✅ 历史日线/周线/月线
- ✅ 技术指标（SMA, EMA, RSI, MACD等）
- ✅ 基本面数据（部分）
- ✅ 外汇、加密货币

**API示例**:
```python
import requests

# 获取苹果公司实时股价
url = "https://www.alphavantage.co/query"
params = {
    "function": "TIME_SERIES_INTRADAY",
    "symbol": "AAPL",
    "interval": "5min",
    "apikey": "YOUR_API_KEY"
}
response = requests.get(url, params=params)
```

**优点**:
- 数据全面，覆盖全球市场
- 文档完善，社区活跃
- 免费层足够个人使用

**缺点**:
- 实时数据有15分钟延迟
- 调用频率限制较严格

### 2. Yahoo Finance (yfinance库) ⭐⭐⭐⭐
**Python库**: `yfinance`

**安装**: `pip install yfinance`

**免费限制**:
- 完全免费
- 无官方API限制（但可能被限流）
- 数据来自Yahoo Finance

**支持的数据**:
- ✅ 实时股价（有延迟）
- ✅ 历史数据（日线、周线、月线）
- ✅ 基本面数据（财报、股息等）
- ✅ 期权数据
- ✅ 市场指数

**使用示例**:
```python
import yfinance as yf

# 获取苹果公司数据
aapl = yf.Ticker("AAPL")
hist = aapl.history(period="1mo")  # 过去一个月数据
info = aapl.info  # 公司信息
```

**优点**:
- 完全免费，无调用限制
- 数据质量较好
- Python接口简单易用

**缺点**:
- 非官方API，稳定性依赖Yahoo
- 可能被限流或封禁
- 数据更新有延迟

### 3. IEX Cloud ⭐⭐⭐
**网址**: https://iexcloud.io/

**免费层限制**:
- 50万消息/月
- 支持实时和历史数据
- 需要注册获取token

**支持的数据**:
- ✅ 实时股价（IEX交易所）
- ✅ 历史数据
- ✅ 基本面数据
- ✅ 新闻数据
- ✅ 期权数据

**优点**:
- 数据质量高
- 实时数据来自IEX交易所
- 文档完善

**缺点**:
- 免费层消息数有限
- 主要覆盖美股

### 4. Twelve Data ⭐⭐⭐
**网址**: https://twelvedata.com/

**免费层限制**:
- 800次API调用/天
- 2次API调用/秒
- 需要注册获取API key

**支持的数据**:
- ✅ 实时股价
- ✅ 历史数据
- ✅ 技术指标
- ✅ 外汇、加密货币

**优点**:
- 支持全球市场
- 技术指标丰富
- 响应速度快

**缺点**:
- 免费层调用限制较严格
- 数据源稳定性一般

### 5. Financial Modeling Prep ⭐⭐⭐⭐
**网址**: https://financialmodelingprep.com/

**免费层限制**:
- 250次API调用/天
- 需要注册获取API key

**支持的数据**:
- ✅ 实时股价
- ✅ 历史数据
- ✅ 财务报表
- ✅ 估值指标
- ✅ 市场情绪

**优点**:
- 基本面数据丰富
- 财务报表完整
- 适合价值投资分析

**缺点**:
- 调用次数有限
- 实时数据有延迟

## 🎯 推荐方案

### 短期方案（立即使用）
**主数据源**: Alpha Vantage + yfinance
**备用数据源**: IEX Cloud

**理由**:
1. **Alpha Vantage**: 稳定可靠，500次/天足够初期使用
2. **yfinance**: 完全免费，作为补充和备份
3. **IEX Cloud**: 高质量实时数据，用于关键股票

### 中期方案（1-3个月）
**考虑付费升级**:
- Alpha Vantage Premium: $49/月，无限制调用
- IEX Cloud Growth: $9/月，增加消息数

### 长期方案（3-6个月）
**自建数据管道**:
1. 多数据源聚合
2. 本地数据缓存
3. 数据质量监控
4. 故障自动切换

## 🔧 技术实现建议

### 数据获取层设计
```python
class USStockDataFetcher:
    def __init__(self):
        self.sources = {
            'alpha_vantage': AlphaVantageSource(),
            'yfinance': YahooFinanceSource(),
            'iex': IEXCloudSource()
        }
        self.cache = DataCache()
    
    def get_price(self, symbol, source='auto'):
        """获取股价，自动选择最优数据源"""
        # 1. 检查缓存
        cached = self.cache.get(symbol)
        if cached and not self.cache.is_expired(cached):
            return cached
        
        # 2. 按优先级获取
        for source_name in self.get_source_priority():
            try:
                data = self.sources[source_name].get_price(symbol)
                if data:
                    self.cache.set(symbol, data)
                    return data
            except Exception as e:
                logger.warning(f"数据源{source_name}失败: {e}")
                continue
        
        return None
```

### 数据缓存策略
1. **实时数据**: 缓存5-15分钟
2. **历史数据**: 缓存24小时
3. **基本面数据**: 缓存7天
4. **财报数据**: 缓存30天

### 错误处理和重试
1. **指数退避重试**: 失败后等待时间指数增加
2. **故障转移**: 主数据源失败时自动切换到备用
3. **降级策略**: 实时数据失败时返回最近缓存

## 📈 数据需求分析

### 核心数据需求
| 数据类型 | 更新频率 | 精度要求 | 数据源优先级 |
|----------|----------|----------|--------------|
| 实时股价 | 5分钟 | 高 | Alpha Vantage → yfinance → IEX |
| 历史日线 | 每日 | 高 | yfinance → Alpha Vantage |
| 技术指标 | 每日 | 中 | Alpha Vantage → 本地计算 |
| 基本面 | 季度 | 中 | Financial Modeling Prep → yfinance |
| 新闻情绪 | 实时 | 低 | 免费新闻API |

### 重点监控股票
1. **科技龙头**: AAPL, MSFT, NVDA, AMD, GOOGL
2. **半导体**: TSM, AVGO, QCOM, INTC
3. **中概股**: BABA, PDD, BIDU, JD
4. **指数**: ^GSPC (标普500), ^IXIC (纳斯达克), ^SOX (费城半导体)

## 🚀 实施计划

### 第1周：基础接入
- [ ] 注册Alpha Vantage获取API key
- [ ] 测试yfinance基础功能
- [ ] 开发基础数据获取模块
- [ ] 实现简单缓存机制

### 第2周：完善功能
- [ ] 实现多数据源故障转移
- [ ] 开发数据质量监控
- [ ] 建立历史数据存储
- [ ] 测试美股-A股相关性分析

### 第3周：系统集成
- [ ] 集成到第六维度分析
- [ ] 开发实时监控报警
- [ ] 优化性能和数据更新
- [ ] 进行压力测试

### 第4周：生产部署
- [ ] 部署到生产环境
- [ ] 建立数据备份机制
- [ ] 监控系统运行状态
- [ ] 编写使用文档

## 💰 成本估算

### 免费方案
- **Alpha Vantage**: $0 (500次/天)
- **yfinance**: $0
- **IEX Cloud**: $0 (50万消息/月)
- **总成本**: $0

### 基础付费方案
- **Alpha Vantage Premium**: $49/月
- **IEX Cloud Growth**: $9/月
- **总成本**: $58/月

### 高级方案
- **多个数据源订阅**: $100-200/月
- **数据存储**: $20-50/月
- **总成本**: $120-250/月

## ⚠️ 风险与对策

### 技术风险
1. **API限制**: 设计合理的调用频率和缓存
2. **数据延迟**: 明确标注数据时效性
3. **服务中断**: 多数据源备份

### 业务风险
1. **免费服务变更**: 监控服务条款变化
2. **数据质量波动**: 建立数据验证机制
3. **合规风险**: 确保数据使用符合条款

### 应对策略
1. **冗余设计**: 至少2个数据源互为备份
2. **降级方案**: 关键功能降级使用缓存数据
3. **监控报警**: 实时监控数据获取状态

## 📝 结论与建议

### 立即行动
1. **注册Alpha Vantage**，获取免费API key
2. **安装yfinance**，测试基础功能
3. **开发基础数据模块**，实现美股数据获取

### 短期重点
1. 建立稳定的美股数据获取管道
2. 实现美股-A股联动分析基础功能
3. 集成到第六维度分析框架

### 长期规划
1. 考虑付费升级提高数据质量
2. 建立自建数据管道减少外部依赖
3. 扩展其他国际市场数据

---

**调研时间**: 2026-03-28  
**调研人**: 量化小助理  
**下次评估**: 2026-04-04