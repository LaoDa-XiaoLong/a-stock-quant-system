            # 按超预期率排序
            industry_rates.sort(key=lambda x: x[1], reverse=True)
            
            for i, (industry, rate, data) in enumerate(industry_rates[:5], 1):  # 显示前5个
                if rate >= 50:
                    lines.append(f"{i}. **<font color='green'>{industry}</font>**: {data['surprises']}/{data['total']}只超预期({rate:.1f}%)")
                elif rate >= 30:
                    lines.append(f"{i}. **{industry}**: {data['surprises']}/{data['total']}只超预期({rate:.1f}%)")
                else:
                    lines.append(f"{i}. <font color='orange'>{industry}</font>: {data['surprises']}/{data['total']}只超预期({rate:.1f}%)")
        
        # 极端值提醒
        if stats['extreme_values']:
            lines.append("")
            lines.append("### ⚠️ 极端值提醒")
            lines.append(f"发现{len(stats['extreme_values'])}个极端值(>500%):")
            for extreme in stats['extreme_values'][:3]:  # 只显示前3个
                lines.append(f"- {extreme['name']}: {extreme['ratio']:.1f}%")
            if len(stats['extreme_values']) > 3:
                lines.append(f"- ...等{len(stats['extreme_values'])}个极端值")
        
        # 综合交易建议
        lines.append("")
        lines.append("## 💡 综合交易建议")
        
        # 根据持仓数据生成建议
        if holdings:
            # 分类建议
            strong_buy = [s for s in holdings if s.get('surprise_ratio', 0) >= 0.30]
            consider_buy = [s for s in holdings if 0.20 <= s.get('surprise_ratio', 0) < 0.30]
            hold = [s for s in holdings if 0 <= s.get('surprise_ratio', 0) < 0.20]
            consider_sell = [s for s in holdings if s.get('surprise_ratio', 0) < 0]
            
            if strong_buy:
                lines.append("### 🚀 强烈推荐加仓")
                for stock in strong_buy[:3]:
                    lines.append(f"- **{stock['stock_name']}**: {stock.get('metric', '')}+{stock.get('surprise_ratio', 0)*100:.1f}%")
            
            if consider_buy:
                lines.append("### ✅ 考虑加仓")
                for stock in consider_buy[:3]:
                    lines.append(f"- {stock['stock_name']}: {stock.get('metric', '')}+{stock.get('surprise_ratio', 0)*100:.1f}%")
            
            if hold:
                lines.append("### 🔍 持有观察")
                for stock in hold[:3]:
                    lines.append(f"- {stock['stock_name']}: {stock.get('metric', '')}{stock.get('surprise_ratio', 0)*100:+.1f}%")
            
            if consider_sell:
                lines.append("### ⚠️ 关注风险")
                for stock in consider_sell[:3]:
                    lines.append(f"- {stock['stock_name']}: {stock.get('metric', '')}{stock.get('surprise_ratio', 0)*100:+.1f}%")
        
        # 数据质量说明
        lines.append("")
        lines.append("## 🔍 数据质量说明")
        lines.append(f"**质量阈值**: 75分")
        lines.append(f"**平均分数**: {report.get('data_quality_score', 0):.1f}分")
        lines.append("**验证项目**: 完整性、合理性、一致性、极端值")
        
        # 改进建议
        lines.append("")
        lines.append("## 🛠️ 系统改进建议")
        lines.append("1. **调整预期数据生成逻辑**，避免过于保守")
        lines.append("2. **提高超预期阈值至30%**，提高筛选标准")
        lines.append("3. **添加同比数据分析**，更好评估成长性")
        lines.append("4. **优化数据质量检查**，识别并过滤异常值")
        
        # 生成时间
        lines.append("")
        lines.append(f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        lines.append("*V3深度优化版 - 解决综合性、重点突出、数据合理性三大问题*")
        
        return "\n".join(lines)
    
    def send_v3_report(self):
        """发送V3版报告（分层发送）"""
        print("🚀 开始发送V3深度优化版财报监控报告...")
        
        # 1. 获取报告数据
        report = self.get_today_report_data()
        if not report:
            print("❌ 无法获取报告数据，停止发送")
            return False
        
        print(f"✅ 获取到 {report.get('date', '今日')} 的报告数据")
        
        # 2. 生成并发送核心摘要
        print("📤 发送核心摘要（第一层）...")
        core_summary = self.generate_core_summary(report)
        
        # 发送核心摘要到飞书
        success1 = self.sender.send_text(core_summary)
        if not success1:
            print("❌ 核心摘要发送失败")
            return False
        
        print("✅ 核心摘要发送成功")
        
        # 3. 等待3秒，然后发送详细分析
        import time
        time.sleep(3)
        
        print("📤 发送详细综合分析（第二层）...")
        detailed_analysis = self.generate_detailed_analysis(report)
        
        # 发送详细分析
        success2 = self.sender.send_text(detailed_analysis)
        if not success2:
            print("❌ 详细分析发送失败")
            return False
        
        print("✅ 详细分析发送成功")
        
        # 4. 保存完整报告到文件
        self._save_v3_report(report)
        
        print("🎉 V3深度优化版财报监控报告发送完成！")
        return True
    
    def _save_v3_report(self, report: Dict):
        """保存V3版完整报告到文件"""
        try:
            report_dir = "reports/financial_daily_v3"
            os.makedirs(report_dir, exist_ok=True)
            
            date_str = report.get('date', datetime.now().strftime('%Y-%m-%d'))
            filename = f"{report_dir}/daily_report_{date_str}_v3.md"
            
            with open(filename, 'w', encoding='utf-8') as f:
                # 写入核心摘要
                f.write(self.generate_core_summary(report))
                f.write("\n\n")
                
                # 写入详细分析
                f.write(self.generate_detailed_analysis(report))
            
            print(f"💾 V3版完整报告已保存: {filename}")
            
            # 同时保存JSON格式数据
            json_file = f"{report_dir}/daily_report_{date_str}_v3.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            print(f"💾 原始数据已保存: {json_file}")
            
        except Exception as e:
            print(f"❌ 保存报告失败: {e}")
    
    def run(self):
        """运行V3版发送任务"""
        print("=" * 60)
        print("📈 A股财报监控日报发送任务 - V3深度优化版")
        print("=" * 60)
        print("🎯 解决三大问题:")
        print("1. 综合性不足 → 每只股票一个综合段落")
        print("2. 重点不突出 → 颜色/图标/加粗系统")
        print("3. 数据合理性 → 识别并标注可疑数据")
        print("=" * 60)
        
        try:
            # 使用V3版分层发送方案
            success = self.send_v3_report()
            
            if success:
                print("✅ V3版任务执行成功！")
                return True
            else:
                print("❌ V3版任务执行失败")
                return False
                
        except Exception as e:
            print(f"❌ 任务执行异常: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    # 创建V3版发送器实例
    sender = FinancialReportSenderV3()
    
    # 运行发送任务
    success = sender.run()
    
    # 退出码
    sys.exit(0 if success else 1)