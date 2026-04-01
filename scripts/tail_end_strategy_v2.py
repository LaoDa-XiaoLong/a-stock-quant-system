            for category, result in details.items():
                weight = self.weights.get(category, 0)
                actual_score = result["score"] * weight / 100
                report_lines.append(f"  - {category}: {result['score']}分 × {weight}% = {actual_score:.1f}分")
            
            report_lines.append("")
            report_lines.append("#### 进场点位建议:")
            for entry_type, price in risk_data["entry_points"].items():
                diff_percent = (price - stock['current_price']) / stock['current_price'] * 100
                direction = "上涨" if diff_percent > 0 else "下跌"
                report_lines.append(f"  - **{entry_type}**: {price:.2f}元 ({direction}{abs(diff_percent):.1f}%)")
            
            report_lines.append("")
            report_lines.append("#### 风险控制:")
            report_lines.append(f"  - **止损位**: {risk_data['stop_loss']:.2f}元 (下跌{((stock['current_price'] - risk_data['stop_loss']) / stock['current_price'] * 100):.1f}%)")
            report_lines.append(f"  - **第一止盈**: {risk_data['take_profit'][0]:.2f}元 (上涨{((risk_data['take_profit'][0] - stock['current_price']) / stock['current_price'] * 100):.1f}%)")
            report_lines.append(f"  - **第二止盈**: {risk_data['take_profit'][1]:.2f}元 (上涨{((risk_data['take_profit'][1] - stock['current_price']) / stock['current_price'] * 100):.1f}%)")
            report_lines.append(f"  - **风险收益比**: {risk_data['risk_reward_ratio']:.2f}")
            report_lines.append("")
            
            report_lines.append("#### 主要选股理由:")
            for reason in stock['selection_reasons'][:8]:  # 显示前8个理由
                report_lines.append(f"  - {reason}")
            
            report_lines.append("")
            report_lines.append("---")
            report_lines.append("")
        
        # 添加策略说明
        report_lines.append("## 策略说明")
        report_lines.append("### 核心选股标准:")
        report_lines.append("1. **价格走势（25%）**: 关注当日涨跌幅、日内振幅、尾盘走势")
        report_lines.append("2. **成交量分析（20%）**: 尾盘量比、换手率、成交量趋势")
        report_lines.append("3. **资金流向（25%）**: 大单资金流、主力资金占比")
        report_lines.append("4. **技术指标（20%）**: MACD、KDJ、RSI等技术指标")
        report_lines.append("5. **形态分析（10%）**: 分时图形态、K线形态")
        report_lines.append("")
        report_lines.append("### 进场策略:")
        report_lines.append("- **优质股票（≥90分）**: 保守进场，止损6%")
        report_lines.append("- **良好股票（80-89分）**: 稳健进场，止损8%")
        report_lines.append("- **一般股票（70-79分）**: 谨慎进场，止损10%")
        report_lines.append("")
        report_lines.append("### 风险提示:")
        report_lines.append("1. 尾盘交易时间有限，需快速决策")
        report_lines.append("2. 注意大盘环境和板块轮动")
        report_lines.append("3. 严格控制仓位，单只股票不超过总资金的30%")
        report_lines.append("4. 设置止损止盈，严格执行纪律")
        
        return "\n".join(report_lines)
    
    def save_selection_results(self, selected_stocks: List[Dict]):
        """保存选股结果"""
        timestamp = self.get_current_time().strftime("%Y%m%d_%H%M%S")
        
        # 保存JSON格式
        json_path = os.path.join(self.output_dir, f"tail_end_selection_v2_{timestamp}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                "selection_time": timestamp,
                "strategy_name": self.strategy_name,
                "strategy_version": self.strategy_version,
                "weights": self.weights,
                "total_selected": len(selected_stocks),
                "stocks": selected_stocks
            }, f, ensure_ascii=False, indent=2)
        
        # 保存报告
        report_path = os.path.join(self.output_dir, f"tail_end_selection_report_v2_{timestamp}.md")
        report_content = self.generate_detailed_report(selected_stocks)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"选股结果已保存:")
        print(f"  - JSON文件: {json_path}")
        print(f"  - 报告文件: {report_path}")
        
        return json_path, report_path
    
    def get_sample_stock_data(self):
        """获取示例股票数据（模拟）"""
        sample_stocks = {}
        
        # 模拟10只股票数据
        for i in range(1, 11):
            code = f"0000{i:02d}"
            
            # 随机生成股票数据
            current_price = np.random.uniform(5, 50)
            change_percent = np.random.uniform(-5, 5)
            
            sample_stocks[code] = {
                "code": code,
                "name": f"示例股票{i}",
                "current_price": current_price,
                "change_percent": change_percent,
                "amplitude": np.random.uniform(2, 10),
                "turnover_rate": np.random.uniform(1, 20),
                "tail_volume_ratio": np.random.uniform(0.8, 2.5),
                "volume_trend": np.random.choice(["递增", "平稳", "递减"]),
                "large_order_flow": np.random.uniform(-20000000, 20000000),
                "main_capital_ratio": np.random.uniform(0, 0.3),
                "tail_trend": np.random.choice(["拉升", "平稳", "下跌"]),
                "intraday_pattern": np.random.choice(["V型反转", "U型反转", "尾盘拉升", "突破平台", "横盘震荡"]),
                "kline_pattern": np.random.choice(["W底", "头肩底", "突破整理", "均线多头", "无特殊形态"]),
                "technical_indicators": {
                    "macd": {
                        "dif": np.random.uniform(-1, 1),
                        "dea": np.random.uniform(-1, 1),
                        "macd": np.random.uniform(-0.5, 0.5),
                        "signal": np.random.choice(["金叉", "死叉", "即将金叉"])
                    },
                    "kdj": {
                        "k": np.random.uniform(0, 100),
                        "d": np.random.uniform(0, 100),
                        "j": np.random.uniform(0, 100)
                    },
                    "rsi": {
                        "rsi6": np.random.uniform(20, 80),
                        "rsi12": np.random.uniform(20, 80),
                        "rsi24": np.random.uniform(20, 80)
                    }
                }
            }
        
        return sample_stocks
    
    def run_selection(self, stock_data: Dict[str, Dict] = None):
        """运行尾盘选股"""
        print(f"开始执行尾盘选股策略 v2.0: {self.strategy_name}")
        print(f"选股时间窗口: {self.selection_time}")
        print(f"策略权重: {json.dumps(self.weights, ensure_ascii=False)}")
        print("=" * 60)
        
        # 检查是否是尾盘时间
        if not self.is_tail_end_time():
            current_time = self.get_current_time().strftime("%H:%M:%S")
            print(f"当前时间 {current_time} 不在尾盘选股时间窗口内")
            print(f"尾盘选股时间窗口: {self.selection_time}")
            return None
        
        # 如果没有提供股票数据，使用示例数据
        if stock_data is None:
            print("使用示例股票数据进行测试...")
            stock_data = self.get_sample_stock_data()
        
        print(f"分析 {len(stock_data)} 只股票数据...")
        selected_stocks = self.apply_selection_criteria(stock_data)
        
        print(f"筛选完成，共选出 {len(selected_stocks)} 只符合条件的股票")
        
        if selected_stocks:
            print("\n前5只推荐股票:")
            for i, stock in enumerate(selected_stocks[:5], 1):
                risk_data = self.calculate_tail_end_entry_points(stock)
                print(f"{i}. {stock['name']} ({stock['code']})")
                print(f"   评分: {stock['score']}分 | 价格: {stock['current_price']:.2f}元")
                print(f"   仓位: {risk_data['position_suggestion']}")
                print(f"   风险收益比: {risk_data['risk_reward_ratio']:.2f}")
        
        # 保存结果
        json_path, report_path = self.save_selection_results(selected_stocks)
        
        return {
            "selected_stocks": selected_stocks,
            "json_path": json_path,
            "report_path": report_path
        }


def main():
    """主函数"""
    selector = TailEndStrategyV2()
    
    # 运行选股
    result = selector.run_selection()
    
    if result:
        print("\n尾盘选股策略 v2.0 执行完成！")
        print(f"详细报告请查看: {result['report_path']}")
    else:
        print("尾盘选股策略未执行（不在尾盘时间窗口）")


if __name__ == "__main__":
    main()