                    df = pd.read_csv(latest_file, encoding='utf-8')
                    latest_data = {
                        "update_time": latest_time,
                        "total_stocks": len(df),
                        "sample_stocks": df.head(5).to_dict(orient='records')
                    }
                except Exception as e:
                    self.logger.warning(f"读取最新文件失败: {e}")

        return {
            "date": date,
            "has_data": True,
            "time_points": len(time_points),
            "latest_data": latest_data,
            "data_directory": date_dir
        }

    def cleanup_old_data(self, days_to_keep: int = 30):
        """清理旧数据"""
        try:
            current_date = datetime.now()
            cutoff_date = current_date - timedelta(days=days_to_keep)

            deleted_count = 0
            for item in os.listdir(self.data_dir):
                item_path = os.path.join(self.data_dir, item)

                # 检查是否为日期目录
                if os.path.isdir(item_path):
                    try:
                        item_date = datetime.strptime(item, "%Y-%m-%d")
                        if item_date < cutoff_date:
                            import shutil
                            shutil.rmtree(item_path)
                            deleted_count += 1
                            self.logger.info(f"删除旧数据目录: {item}")
                    except ValueError:
                        # 不是日期格式，跳过
                        continue

            self.logger.info(f"清理完成，删除了 {deleted_count} 个旧数据目录")
            return deleted_count

        except Exception as e:
            self.logger.error(f"清理旧数据失败: {e}")
            return 0


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='A股实时价格API')
    parser.add_argument('--start-monitoring', action='store_true', help='启动实时监控')
    parser.add_argument('--get-prices', action='store_true', help='获取一次实时价格')
    parser.add_argument('--get-latest', action='store_true', help='获取最新价格')
    parser.add_argument('--daily-summary', action='store_true', help='获取当日摘要')
    parser.add_argument('--cleanup', action='store_true', help='清理旧数据')
    parser.add_argument('--interval', type=int, default=3, help='监控间隔（分钟）')

    args = parser.parse_args()

    api = AStockRealtimeAPI()

    if args.start_monitoring:
        print(f"启动A股实时价格监控，间隔 {args.interval} 分钟")
        print("按 Ctrl+C 停止")
        api.start_realtime_monitoring(args.interval)

    elif args.get_prices:
        print("获取实时价格数据...")
        prices = api.get_realtime_prices()
        if prices is not None:
            print(f"获取到 {len(prices)} 条数据")
            file_path = api.save_prices(prices)
            print(f"数据已保存: {file_path}")
        else:
            print("获取价格数据失败")

    elif args.get_latest:
        print("获取最新价格数据...")
        prices = api.get_latest_prices()
        if prices is not None:
            print(f"最新数据: {len(prices)} 条")
            print(prices.head())
        else:
            print("无最新数据")

    elif args.daily_summary:
        print("获取当日数据摘要...")
        summary = api.get_daily_summary()
        print(json.dumps(summary, ensure_ascii=False, indent=2))

    elif args.cleanup:
        print("清理旧数据...")
        deleted = api.cleanup_old_data()
        print(f"删除了 {deleted} 个旧数据目录")

    else:
        print("A股实时价格API Skill")
        print(f"版本: {api.version}")
        print(f"作者: {api.author}")
        print(f"数据目录: {api.data_dir}")
        print("")
        print("可用命令:")
        print("  --start-monitoring  启动实时监控")
        print("  --get-prices        获取一次实时价格")
        print("  --get-latest        获取最新价格")
        print("  --daily-summary     获取当日摘要")
        print("  --cleanup           清理旧数据")


if __name__ == "__main__":
    main()
