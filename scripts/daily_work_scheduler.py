        report_lines.append("- `data/realtime_prices/` - 实时价格数据")
        report_lines.append("- `data/tail_end_selection/` - 尾盘选股数据")
        report_lines.append("- `data/daily_scheduler/` - 调度系统配置")
        report_lines.append("")
        
        report_lines.append("### Skill文件")
        report_lines.append("- `skills/a_stock_realtime_api/` - A股实时价格API")
        report_lines.append("- `skills/tail_end_selection/` - 尾盘选股法")
        report_lines.append("")
        
        report_lines.append("### 脚本文件")
        report_lines.append("- `scripts/daily_work_scheduler.py` - 调度系统主程序")
        report_lines.append("")
        
        report_lines.append("## 五、使用说明")
        report_lines.append("")
        report_lines.append("### 手动执行")
        report_lines.append("```bash")
        report_lines.append("# 启动实时价格监控")
        report_lines.append("cd /Users/ago/.openclaw/workspace")
        report_lines.append("python3 -m skills.a_stock_realtime_api --start-monitoring --interval 3")
        report_lines.append("")
        report_lines.append("# 执行尾盘选股")
        report_lines.append("python3 -m skills.tail_end_selection --execute-selection")
        report_lines.append("")
        report_lines.append("# 生成每日报告")
        report_lines.append("python3 -m skills.tail_end_selection --daily-report")
        report_lines.append("")
        report_lines.append("# 发送报告到群")
        report_lines.append("python3 -m skills.tail_end_selection --send-report \"A股数据分析群\"")
        report_lines.append("```")
        report_lines.append("")
        
        report_lines.append("### 自动执行")
        report_lines.append("使用生成的Cron任务配置文件，系统将自动执行所有任务。")
        report_lines.append("")
        
        report_lines.append("## 六、重要提醒")
        report_lines.append("1. **数据真实性**: 系统基于真实价格数据执行")
        report_lines.append("2. **自动执行**: 所有任务将每日自动执行，无需询问")
        report_lines.append("3. **报告发送**: 每日报告将自动发送到A股数据分析群")
        report_lines.append("4. **长期记忆**: 所有交易记录本地保存，便于复盘")
        report_lines.append("5. **风险控制**: 系统包含完整的风险控制机制")
        
        report_content = "\n".join(report_lines)
        
        # 保存报告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(self.data_dir, f"setup_report_{timestamp}.md")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.logger.info(f"设置报告已生成: {report_file}")
        
        return report_file


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='每日工作调度系统')
    parser.add_argument('--run-scheduler', action='store_true', help='运行调度器')
    parser.add_argument('--setup-cron', action='store_true', help='设置Cron任务')
    parser.add_argument('--generate-report', action='store_true', help='生成设置报告')
    parser.add_argument('--full-setup', action='store_true', help='完整设置')
    
    args = parser.parse_args()
    
    scheduler = DailyWorkScheduler()
    
    if args.run_scheduler:
        print("运行调度器...")
        print("按 Ctrl+C 停止")
        scheduler.run_scheduler()
    
    elif args.setup_cron:
        print("设置Cron任务...")
        cron_file = scheduler.setup_cron_jobs()
        print(f"✅ Cron任务配置已生成: {cron_file}")
    
    elif args.generate_report:
        print("生成设置报告...")
        report_file = scheduler.generate_setup_report()
        print(f"✅ 设置报告已生成: {report_file}")
    
    elif args.full_setup:
        print("执行完整设置...")
        print("=" * 60)
        
        print("1. 生成设置报告...")
        report_file = scheduler.generate_setup_report()
        print(f"   ✅ 报告: {report_file}")
        
        print("2. 设置Cron任务...")
        cron_file = scheduler.setup_cron_jobs()
        print(f"   ✅ Cron配置: {cron_file}")
        
        print("3. 显示执行计划...")
        print("\n📅 每日执行计划:")
        print("- 09:30-15:00: 每3分钟获取实时价格")
        print("- 14:30: 执行尾盘选股")
        print("- 18:00: 生成每日报告")
        print("- 18:05: 发送报告到A股数据分析群")
        
        print("\n" + "=" * 60)
        print("✅ 完整设置完成!")
        print("系统已准备就绪，将自动执行所有任务。")
        print("=" * 60)
    
    else:
        print("每日工作调度系统")
        print(f"版本: {scheduler.version}")
        print(f"作者: {scheduler.author}")
        print("")
        print("可用命令:")
        print("  --run-scheduler    运行调度器")
        print("  --setup-cron       设置Cron任务")
        print("  --generate-report  生成设置报告")
        print("  --full-setup       完整设置")


if __name__ == "__main__":
    main()