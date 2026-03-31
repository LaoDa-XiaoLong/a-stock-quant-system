        report_content += f"""
## 三、操作建议

### 📊 已达到进场条件的股票 ({len(entered_stocks)}只)
"""
        
        if entered_stocks:
            for i, (stock, entry_type) in enumerate(entered_stocks, 1):
                report_content += f"""{i}. **{stock['code']} {stock['name']}** - {entry_type}
   - 当前价格: {stock['current_price']}元
   - 进场类型: {entry_type}
   - 建议仓位: {'60%' if entry_type == '激进进场' else '80%' if entry_type == '稳健进场' else '100%'}
   - 止损点位: {stock['stop_loss']}元
   - 安全边际: {(stock['current_price'] - stock['stop_loss'])/stock['current_price']*100:.1f}%
   - 操作建议: 可以考虑{entry_type}，使用相应仓位比例

"""
        else:
            report_content += "暂无股票达到进场条件\n"
        
        report_content += f"""
### 💡 策略刷新说明

**为什么需要刷新策略？**
1. **市场价格变化**: 股票价格实时变动，需要基于最新价格重新计算
2. **风险控制更新**: 止损止盈点位需要随价格变化调整
3. **进场机会识别**: 重新评估当前是否适合进场
4. **策略优化**: 基于最新数据优化投资决策

**新策略特点**:
1. **动态计算**: 基于最新真实价格计算进场点位
2. **风险适配**: 止损止盈点位与当前价格匹配
3. **实时评估**: 每3分钟自动刷新价格和策略
4. **科学决策**: 基于量化评分选择最佳进场时机

### ⏰ 后续监控计划

**自动监控系统**:
- **监控频率**: 每3分钟获取一次真实价格
- **交易时间**: 09:30-11:30, 13:00-15:00
- **自动启动**: 明天09:29和12:59自动开始监控
- **条件检查**: 实时检查进场、止损、止盈条件
- **自动执行**: 达到条件时自动模拟成交

**报告生成**:
- **实时报告**: 每次监控后更新状态
- **每日报告**: 收盘后16:00生成详细报告
- **交易记录**: 自动记录所有模拟交易

### 📈 刷新前后对比

| 项目 | 刷新前 | 刷新后 | 变化 |
|------|--------|--------|------|
| 数据源 | 模拟价格 | 新浪财经实时API | ✅ 更准确 |
| 进场点位 | 固定值 | 基于最新价格动态计算 | ✅ 更合理 |
| 风险控制 | 固定值 | 基于进场价动态计算 | ✅ 更科学 |
| 更新频率 | 一次性 | 每3分钟自动更新 | ✅ 更及时 |

## 四、系统状态

✅ 投资策略已刷新完成
✅ 真实价格数据已获取
✅ 新进场点位已计算
✅ 风险控制参数已更新
✅ 定时任务已配置
✅ 监控系统已就绪

---

*报告生成: 量化小助理投资策略刷新系统 v2.0*
*下次自动刷新: 明天交易时间每3分钟*
*建议操作: 根据新策略评估进场机会*
"""

        # 写入报告文件
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ 策略刷新报告已生成: {report_file}")
        
        # 生成简版摘要
        summary_file = f'{self.tracking_dir}/strategy_refresh_summary_{timestamp}.txt'
        
        summary_content = f"""🔄 投资策略刷新摘要 ({today} {datetime.now().strftime('%H:%M:%S')})

【刷新结果】
股票数量: {len(portfolio['stocks'])}只
数据源: 新浪财经实时API
策略版本: v2.0

【已达到进场条件】 ({len(entered_stocks)}只)
"""
        
        for stock, entry_type in entered_stocks:
            summary_content += f"{stock['code']} {stock['name']}: {stock['current_price']}元 ({entry_type})\n"
        
        if not entered_stocks:
            summary_content += "暂无\n"
        
        summary_content += f"""
【新策略特点】
1. 基于最新真实价格动态计算
2. 每3分钟自动刷新
3. 科学的风险控制
4. 实时进场机会识别

【明日自动执行】
- 09:29: 监控系统启动
- 每3分钟: 获取真实价格
- 自动检查: 进场/止损/止盈条件
- 16:00: 生成详细报告

【系统状态】 ✅ 准备就绪
"""
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        print(f"✅ 策略刷新摘要已生成: {summary_file}")
        
        return report_file
    
    def main(self):
        """主函数"""
        print("=" * 60)
        print("🔄 投资策略刷新 - 基于最新真实价格")
        print("=" * 60)
        
        # 刷新投资策略
        new_portfolio = self.refresh_from_existing_portfolio()
        
        if new_portfolio:
            # 生成报告
            report_file = self.generate_refresh_report(new_portfolio)
            
            print("=" * 60)
            print("🎉 投资策略刷新完成！")
            print()
            print("📁 生成的文件:")
            print(f"1. {report_file} - 详细刷新报告")
            print(f"2. data/investment_tracking/strategy_refresh_summary_*.txt - 摘要")
            print(f"3. data/investment_tracking/investment_portfolio_refreshed_*.json - 新投资组合")
            print()
            print("📊 刷新结果摘要:")
            
            # 统计达到进场条件的股票
            entered_stocks = []
            for stock in new_portfolio['stocks']:
                current_price = stock['current_price']
                entry_strategy = stock['entry_strategy']
                
                if current_price <= entry_strategy['激进进场']:
                    entered_stocks.append((stock, '激进进场'))
                elif current_price <= entry_strategy['稳健进场']:
                    entered_stocks.append((stock, '稳健进场'))
                elif current_price <= entry_strategy['保守进场']:
                    entered_stocks.append((stock, '保守进场'))
            
            print(f"   已达到进场条件的股票: {len(entered_stocks)}/{len(new_portfolio['stocks'])}只")
            
            if entered_stocks:
                print("   🎯 具体股票:")
                for stock, entry_type in entered_stocks:
                    print(f"      {stock['code']} {stock['name']}: {stock['current_price']}元 ({entry_type})")
            
            print()
            print("⏰ 系统将在明天交易时间自动启动:")
            print("   09:29 - 上午监控启动")
            print("   12:59 - 下午监控启动")
            print("   每3分钟获取一次真实价格")
            print("   自动检查进场条件并执行")
        else:
            print("❌ 策略刷新失败")

def main():
    """主函数"""
    refresher = InvestmentStrategyRefresher()
    refresher.main()

if __name__ == '__main__':
    main()