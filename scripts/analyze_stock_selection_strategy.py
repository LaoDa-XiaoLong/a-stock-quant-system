    value_stocks = sorted(value_stocks, key=lambda x: x['score'], reverse=True)[:5]

    for i, stock in enumerate(value_stocks, 1):
        report += f"{i}. **{stock['code']} {stock['name']}**: 评分{stock['score']}分，今日{stock['change_pct']:+.2f}%\n"

    report += f"""
### 4.2 成长投资策略 (高评分 + 高涨幅)
推荐关注基本面优秀且近期表现强势的股票：
"""

    growth_stocks = [s for s in all_stocks if s['score'] >= 85 and s['change_pct'] >= 2]
    growth_stocks = sorted(growth_stocks, key=lambda x: x['change_pct'], reverse=True)[:5]

    for i, stock in enumerate(growth_stocks, 1):
        report += f"{i}. **{stock['code']} {stock['name']}**: 评分{stock['score']}分，今日{stock['change_pct']:+.2f}%\n"

    report += f"""
### 4.3 反转投资策略 (今日下跌但基本面好)
推荐关注今日下跌但基本面优秀的股票，可能有反弹机会：
"""

    reversal_stocks = [s for s in all_stocks if s['change_pct'] < 0 and s['score'] >= 80]
    reversal_stocks = sorted(reversal_stocks, key=lambda x: x['score'], reverse=True)[:5]

    for i, stock in enumerate(reversal_stocks, 1):
        report += f"{i}. **{stock['code']} {stock['name']}**: 评分{stock['score']}分，今日{stock['change_pct']:+.2f}%\n"

    report += f"""
## 五、综合投资建议

### 5.1 当前选股策略评估
**优点**:
1. ✅ **质量优先**: 评分≥85分确保股票基本面优秀
2. ✅ **风险控制**: 涨跌幅控制避免追高和过度抄底
3. ✅ **集中投资**: 5只股票便于跟踪管理
4. ✅ **ST处理**: 合理控制ST股票风险

**可优化点**:
1. 🔄 **行业分散**: 可考虑增加行业分散度
2. 🔄 **市值分布**: 可考虑不同市值股票的配置
3. 🔄 **动态调整**: 可根据市场变化动态调整选股标准

### 5.2 建议操作方案

#### 方案A: 保持当前配置 (稳健型)
- 继续监控当前5只股票
- 严格执行风险控制纪律
- 等待价格达到进场条件

#### 方案B: 增加1-2只额外机会 (平衡型)
- 从高评分未选中股票中选择1-2只
- 建议关注: 000007 全新好 (评分90) 或 000028 国药一致 (评分90)
- 增加监控股票至6-7只

#### 方案C: 调整投资策略 (进取型)
- 根据个人风险偏好选择不同策略
- 价值投资: 关注低涨幅高评分股票
- 成长投资: 关注高涨幅高评分股票
- 反转投资: 关注下跌但基本面好的股票

### 5.3 风险提示
1. ⚠️ **市场风险**: 股市有风险，投资需谨慎
2. ⚠️ **ST风险**: *ST股票有退市风险
3. ⚠️ **流动性风险**: 确保所选股票流动性充足
4. ⚠️ **策略风险**: 不同策略适合不同市场环境

### 5.4 后续跟踪建议
1. 📊 **每日监控**: 系统已配置每3分钟自动监控
2. 📈 **定期复盘**: 每日收盘后生成详细报告
3. 🔄 **策略优化**: 根据市场变化优化选股标准
4. 📋 **记录学习**: 记录投资决策和结果，持续学习

## 六、技术实现说明

### 6.1 当前系统状态
- ✅ **实时监控**: 每3分钟获取真实价格
- ✅ **动态策略**: 基于最新价格计算进场点位
- ✅ **自动执行**: 达到条件时自动模拟成交
- ✅ **报告生成**: 每日自动生成详细报告
- ✅ **风险控制**: 自动执行止损止盈

### 6.2 明日自动执行计划
1. **09:29** - 交易监控系统自动启动
2. **每3分钟** - 获取真实价格并检查条件
3. **自动成交** - 达到条件时自动模拟成交
4. **16:00** - 自动生成当日详细报告

## 七、结论

基于详细分析，当前选股策略科学合理，5只选中股票质量优秀。同时发现了多个额外投资机会，可根据个人风险偏好和投资策略进行选择。

系统已准备就绪，从明天开始将自动执行监控和交易，为用户提供完整的投资决策支持。

---

*报告生成: 量化小助理选股策略分析系统*
*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*数据来源: 原始筛选结果 + 新浪财经实时API*
*建议: 根据个人风险偏好选择投资方案*"""

    return report

def main():
    """主函数"""
    analyze_selection_strategy()

if __name__ == '__main__':
    main()
