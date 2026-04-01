                reasons.append(f"中盘股({market_cap:.1f}亿)，略大")
            else:
                step5_score = 2
                reasons.append(f"大盘股({market_cap:.1f}亿)，不符合要求")
            
            score += step5_score
            step_results.append({
                "step": 5,
                "name": "市值筛选",
                "score": step5_score,
                "passed": step5_score >= 8,
                "reason": reasons[-1]
            })
            
            # 步骤6: 技术空间筛选 (5%~10%)
            tech_space = data.get("technical_space", 0)  # 技术上涨空间
            if 8 <= tech_space <= 12:
                step6_score = 10
                reasons.append(f"技术上涨空间优秀({tech_space:.1f}%)")
            elif 5 <= tech_space <= 15:
                step6_score = 8
                reasons.append(f"技术上涨空间良好({tech_space:.1f}%)")
            else:
                step6_score = 3
                reasons.append(f"技术空间一般({tech_space:.1f}%)")
            
            score += step6_score
            step_results.append({
                "step": 6,
                "name": "技术形态筛选",
                "score": step6_score,
                "passed": step6_score >= 8,
                "reason": reasons[-1]
            })
            
            # 最终评分（0-100）
            final_score = min(int(score), 100)
            
            # 杨永兴战法要求：至少通过4个步骤，且总分≥70
            passed_steps = sum(1 for step in step_results if step["passed"])
            
            if passed_steps >= 4 and final_score >= 70:
                stock_info = {
                    "code": code,
                    "name": data.get("name", f"股票{code}"),
                    "score": final_score,
                    "passed_steps": passed_steps,
                    "current_price": data.get("current_price", 0),
                    "change_percent": data.get("change_percent", 0),
                    "selection_reasons": reasons,
                    "step_results": step_results,
                    "strategy_name": self.strategy_name,
                    "strategy_version": self.strategy_version,
                    "selection_time": self.get_current_time().strftime("%Y-%m-%d %H:%M:%S"),
                    "overnight_strategy": True
                }
                selected_stocks.append(stock_info)
        
        # 按评分排序
        selected_stocks.sort(key=lambda x: x["score"], reverse=True)
        
        return selected_stocks
    
    def calculate_overnight_entry_points(self, stock: Dict) -> Dict:
        """
        计算隔夜套利进场点位
        杨永兴战法：尾盘进场，次日冲高卖出
        """
        current_price = stock["current_price"]
        
        # 基于评分的进场策略
        score = stock["score"]
        
        if score >= 90:
            # 优质股票：激进进场
            entry_price = round(current_price * 1.005, 2)  # 上涨0.5%追入
            target_price = round(current_price * 1.08, 2)   # 目标涨幅8%
            stop_loss = round(current_price * 0.97, 2)      # 止损3%
            position = "重仓（不超过30%）"
        elif score >= 80:
            # 良好股票：稳健进场
            entry_price = round(current_price * 1.00, 2)    # 现价或略低
            target_price = round(current_price * 1.06, 2)   # 目标涨幅6%
            stop_loss = round(current_price * 0.96, 2)      # 止损4%
            position = "中等仓位（不超过20%）"
        else:  # 70-79分
            # 一般股票：保守进场
            entry_price = round(current_price * 0.995, 2)   # 下跌0.5%买入
            target_price = round(current_price * 1.05, 2)   # 目标涨幅5%
            stop_loss = round(current_price * 0.95, 2)      # 止损5%
            position = "轻仓（不超过10%）"
        
        return {
            "entry_strategy": "尾盘隔夜套利",
            "entry_price": entry_price,
            "entry_condition": f"达到{entry_price:.2f}元时进场",
            "target_price": target_price,
            "target_gain": round((target_price - current_price) / current_price * 100, 2),
            "stop_loss": stop_loss,
            "max_loss": round((current_price - stop_loss) / current_price * 100, 2),
            "risk_reward_ratio": round((target_price - entry_price) / (entry_price - stop_loss), 2),
            "position_suggestion": position,
            "holding_period": "隔夜（今日尾盘进场，明日冲高卖出）",
            "exit_strategy": "次日冲高时卖出，不贪不恋"
        }
    
    def generate_yang_yongxing_report(self, selected_stocks: List[Dict]) -> str:
        """生成杨永兴战法报告"""
        report_lines = []
        
        report_lines.append("# 杨永兴隔夜套利战法 - 尾盘选股报告")
        report_lines.append(f"## 生成时间: {self.get_current_time().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"## 策略作者: {self.strategy_author}")
        report_lines.append(f"## 历史业绩: {self.strategy_performance}")
        report_lines.append(f"## 策略版本: {self.strategy_name} {self.strategy_version}")
        report_lines.append(f"## 选股时间: {self.selection_time}")
        report_lines.append("")
        
        report_lines.append("## 一、核心理念")
        for key, value in self.core_principles.items():
            report_lines.append(f"- **{key}**: {value}")
        report_lines.append("")
        
        report_lines.append("## 二、六大选股步骤")
        for step in self.six_selection_steps:
            report_lines.append(f"{step['step']}. **{step['name']}**: {step['description']} - {step['criteria']}")
        report_lines.append("")
        
        if not selected_stocks:
            report_lines.append("## 三、选股结果: 无符合条件的股票")
            return "\n".join(report_lines)
        
        report_lines.append(f"## 三、选股结果: 共筛选出 {len(selected_stocks)} 只股票")
        report_lines.append("")
        
        for i, stock in enumerate(selected_stocks[:5], 1):  # 只显示前5只
            entry_data = self.calculate_overnight_entry_points(stock)
            
            report_lines.append(f"### {i}. {stock['name']} ({stock['code']})")
            report_lines.append(f"- **综合评分**: {stock['score']}/100")
            report_lines.append(f"- **通过步骤**: {stock['passed_steps']}/6")
            report_lines.append(f"- **当前价格**: {stock['current_price']:.2f}元")
            report_lines.append(f"- **今日涨跌**: {stock['change_percent']:.2f}%")
            report_lines.append("")
            
            report_lines.append("#### 进场策略:")
            report_lines.append(f"- **策略**: {entry_data['entry_strategy']}")
            report_lines.append(f"- **进场价**: {entry_data['entry_price']:.2f}元 ({entry_data['entry_condition']})")
            report_lines.append(f"- **目标价**: {entry_data['target_price']:.2f}元 (涨幅{entry_data['target_gain']:.1f}%)")
            report_lines.append(f"- **止损价**: {entry_data['stop_loss']:.2f}元 (最大亏损{entry_data['max_loss']:.1f}%)")
            report_lines.append(f"- **风险收益比**: {entry_data['risk_reward_ratio']:.2f}")
            report_lines.append(f"- **仓位建议**: {entry_data['position_suggestion']}")
            report_lines.append(f"- **持有周期**: {entry_data['holding_period']}")
            report_lines.append(f"- **出场策略**: {entry_data['exit_strategy']}")
            report_lines.append("")
            
            report_lines.append("#### 选股步骤详情:")
            for step_result in stock["step_results"]:
                status = "✅" if step_result["passed"] else "❌"
                report_lines.append(f"{status} **步骤{step_result['step']} {step_result['name']}**: {step_result['reason']} ({step_result['score']}分)")
            report_lines.append("")
            
            report_lines.append("#### 主要选股理由:")
            for reason in stock['selection_reasons'][:6]:  # 显示前6个理由
                report_lines.append(f"- {reason}")
            
            report_lines.append("")
            report_lines.append("---")
            report_lines.append("")
        
        report_lines.append("## 四、风险提示")
        report_lines.append("1. **隔夜风险**: 持有过夜存在不确定性")
        report_lines.append("2. **次日开盘**: 可能低开或不及预期")
        report_lines.append("3. **严格执行**: 必须严格执行止损止盈")
        report_lines.append("4. **仓位控制**: 单只股票不超过总资金的30%")
        report_lines.append("5. **分散投资**: 建议分散到2-3只股票")
        report_lines.append("")
        
        report_lines.append("## 五、操作建议")
        report_lines.append("1. **尾盘执行**: 严格在14:30之后进场")
        report_lines.append("2. **分批进场**: 可分批买入，降低风险")
        report_lines.append("3. **次日冲高卖出**: 不贪不恋，有利润就出")
        report_lines.append("4. **严格止损**: 达到止损位立即卖出")
        report_lines.append("5. **持续学习**: 总结经验，优化策略")
        
        return "\n".join(report_lines)
    
    def get_sample_stock_data(self):
        """获取示例股票数据（模拟）"""
        sample_stocks = {}
        
        # 模拟10只股票数据
        for i in range(1, 11):
            code = f"600{i:03d}"
            
            # 随机生成符合杨永兴战法的数据
            current_price = np.random.uniform(10, 50)
            change_percent = np.random.uniform(2, 6)  # 2-6%涨幅
            
            sample_stocks[code] = {
                "code": code,
                "name": f"杨永兴示例股{i}",
                "current_price": current_price,
                "change_percent": change_percent,
                "capital_flow_ratio": np.random.uniform(0.05, 0.25),  # 资金流入5-25%
                "volume_ratio": np.random.uniform(1.5, 2.5),         # 量比1.5-2.5
                "market_cap": np.random.uniform(50, 300),           # 市值50-300亿
                "technical_space": np.random.uniform(5, 12)         # 技术空间5-12%
            }
        
        return sample_stocks
    
    def run_selection(self):
        """运行杨永兴战法选股"""
        print(f"开始执行杨永兴隔夜套利战法")
        print(f"策略作者: {self.strategy_author}")
        print(f"历史业绩: {self.strategy_performance}")
        print(f"选股时间: {self.selection_time}")
        print("=" * 60)
        
        # 检查时间窗口
        if not self.is_yang_yongxing_time():
            current_time = self.get_current_time().strftime("%H:%M:%S")
            print(f"当前时间 {current_time} 不在杨永兴战法时间窗口内")
            print(f"杨永兴战法时间窗口: {self.selection_time}")
            return None
        
        # 获取股票数据
        stock_data = self.get_sample_stock_data()
        print(f"分析 {len(stock_data)} 只股票数据...")
        
        # 应用选股标准
        selected_stocks = self.apply_yang_yongxing_criteria(stock_data)
        
        print(f"筛选完成，共选出 {len(selected_stocks)} 只符合条件的股票")
        
        if selected_stocks:
            print("\n前3只推荐股票:")
            for i, stock in enumerate(selected_stocks[:3], 1):
                entry_data = self.calculate_overnight_entry_points(stock)
                print(f"{i}. {stock['name']} ({stock['code']})")
                print(f"   评分: {stock['score']}分 | 通过步骤: {stock['passed_steps']}/6")
                print(f"   进场价: {entry_data['entry_price']:.2f}元 | 目标价: {entry_data['target_price']:.2f}元")
                print(f"   仓位: {entry_data['position_suggestion']}")
        
        # 保存结果
        timestamp = self.get_current_time().strftime("%Y%m%d_%H%M%S")
        
        # 保存JSON
        json_path = os.path.join(self.output_dir, f"yang_yongxing_selection_{timestamp}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                "selection_time": timestamp,
                "strategy_name": self.strategy_name,
                "strategy_version": self.strategy_version,
                "strategy_author": self.strategy_author,
                "total_selected": len(selected_stocks),
                "stocks": selected_stocks
            }, f, ensure_ascii=False, indent=2)
        
        # 生成报告
        report_content = self.generate_yang_yongxing_report(selected_stocks)
        report_path = os.path.join(self.output_dir, f"yang_yongxing_report_{timestamp}.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"\n✅ 选股结果已保存:")
        print(f"  - JSON文件: {json_path}")
        print(f"  - 报告文件: {report_path}")
        
        return {
            "selected_stocks": selected_stocks,
            "json_path": json_path,
            "report_path": report_path
        }


def main():
    """主函数"""
    strategy = YangYongxingOvernightStrategy()
    
    # 运行选股
    result = strategy.run_selection()
    
    if result:
        print("\n杨永兴隔夜套利战法执行完成！")
        print(f"详细报告请查看: {result['report_path']}")
    else:
        print("杨永兴战法未执行（不在尾盘时间窗口）")


if __name__ == "__main__":
    main()