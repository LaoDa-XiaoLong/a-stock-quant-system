#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票池筛选系统 - 修复完整版
"""

import pandas as pd
import numpy as np
import akshare as ak
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Tuple
import json
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StockPoolFilter:
    """股票池筛选器"""

    def __init__(self, config_path: str = "config/stock_pool_config.json"):
        """初始化筛选器"""
        self.config = self._load_config(config_path)
        self.cache_dir = "data/stock_pool"
        os.makedirs(self.cache_dir, exist_ok=True)

        # 初始化筛选规则
        self.rules = self._init_rules()

        logger.info("股票池筛选系统初始化完成")

    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        default_config = {
            "liquidity": {
                "min_daily_turnover": 10000000,
                "min_daily_volume": 1000000,
                "min_market_cap": 5000000000,
                "max_market_cap": 1000000000000,
            },
            "fundamental": {
                "min_pe": 0,
                "max_pe": 100,
                "min_pb": 0.5,
                "max_pb": 10,
                "min_roe": 0,
                "max_debt_ratio": 70,
            },
            "compliance": {
                "exclude_st": True,
                "exclude_suspended": True,
                "exclude_delisting": True,
            },
            "technical": {
                "price_stability_days": 20,
                "max_price_volatility": 0.5,
                "min_trading_days": 60,
            },
            "industry": {
                "excluded_industries": [],
                "preferred_industries": [],
                "max_industry_concentration": 0.3,
            }
        }

        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
                logger.info(f"已加载用户配置: {config_path}")
            except Exception as e:
                logger.warning(f"加载配置文件失败: {e}, 使用默认配置")

        return default_config

    def _init_rules(self) -> List[Dict]:
        """初始化筛选规则"""
        rules = [
            {
                "name": "流动性规则",
                "function": self._check_liquidity,
                "weight": 1.0,
                "required": True,
            },
            {
                "name": "基本面规则",
                "function": self._check_fundamental,
                "weight": 0.8,
                "required": True,
            },
            {
                "name": "合规性规则",
                "function": self._check_compliance,
                "weight": 1.0,
                "required": True,
            },
            {
                "name": "技术面规则",
                "function": self._check_technical,
                "weight": 0.6,
                "required": False,
            },
            {
                "name": "行业规则",
                "function": self._check_industry,
                "weight": 0.4,
                "required": False,
            },
        ]
        return rules

    def get_all_a_shares(self) -> pd.DataFrame:
        """获取所有A股股票列表"""
        cache_file = os.path.join(self.cache_dir, "all_a_shares.csv")

        if os.path.exists(cache_file):
            cache_time = os.path.getmtime(cache_file)
            if datetime.now().timestamp() - cache_time < 86400:
                logger.info("从缓存加载A股列表")
                return pd.read_csv(cache_file)

        logger.info("从akshare获取A股列表")
        try:
            stock_info = ak.stock_info_a_code_name()

            if stock_info.empty:
                logger.error("获取A股列表失败")
                return pd.DataFrame()

            stock_info = stock_info.rename(columns={
                'code': 'symbol',
                'name': 'name'
            })

            stock_info['market'] = stock_info['symbol'].apply(
                lambda x: 'SH' if x.startswith('6') else 'SZ'
            )

            stock_info.to_csv(cache_file, index=False, encoding='utf-8')
            logger.info(f"A股列表已保存到缓存: {cache_file}")

            return stock_info

        except Exception as e:
            logger.error(f"获取A股列表失败: {e}")
            return pd.DataFrame({
                'symbol': ['000001', '000002', '002352', '600580', '603728'],
                'name': ['平安银行', '万科A', '顺丰控股', '卧龙电驱', '鸣志电器'],
                'market': ['SZ', 'SZ', 'SZ', 'SH', 'SH']
            })

    def get_stock_details(self, symbol: str) -> Dict:
        """获取股票详细信息"""
        cache_file = os.path.join(self.cache_dir, f"{symbol}_details.json")

        if os.path.exists(cache_file):
            cache_time = os.path.getmtime(cache_file)
            if datetime.now().timestamp() - cache_time < 3600:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)

        details = {
            'symbol': symbol,
            'name': '',
            'industry': '',
            'market_cap': 0,
            'pe_ratio': 0,
            'pb_ratio': 0,
            'roe': 0,
            'debt_ratio': 0,
            'daily_turnover': 0,
            'daily_volume': 0,
            'price': 0,
            'is_st': False,
            'is_suspended': False,
            'update_time': datetime.now().isoformat()
        }

        try:
            stock_zh_a_spot = ak.stock_zh_a_spot()
            if not stock_zh_a_spot.empty:
                stock_data = stock_zh_a_spot[stock_zh_a_spot['代码'] == symbol]
                if not stock_data.empty:
                    details['price'] = float(stock_data.iloc[0]['最新价'])
                    details['daily_turnover'] = float(stock_data.iloc[0]['成交额'])
                    details['daily_volume'] = float(stock_data.iloc[0]['成交量'])
                    details['name'] = stock_data.iloc[0]['名称']

        except Exception as e:
            logger.warning(f"获取股票{symbol}详情失败: {e}")

        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(details, f, ensure_ascii=False, indent=2)

        return details

    def _check_liquidity(self, stock_details: Dict) -> Tuple[bool, str, float]:
        """检查流动性规则"""
        config = self.config['liquidity']

        issues = []
        score = 100

        if stock_details['daily_turnover'] < config['min_daily_turnover']:
            issues.append(f"成交额不足: {stock_details['daily_turnover']:,.0f}")
            score -= 30

        if stock_details['daily_volume'] < config['min_daily_volume']:
            issues.append(f"成交量不足: {stock_details['daily_volume']:,.0f}")
            score -= 20

        if stock_details['market_cap'] > 0:
            if stock_details['market_cap'] < config['min_market_cap']:
                issues.append(f"市值过小: {stock_details['market_cap']:,.0f}")
                score -= 25
            if stock_details['market_cap'] > config['max_market_cap']:
                issues.append(f"市值过大: {stock_details['market_cap']:,.0f}")
                score -= 15

        passed = len(issues) == 0
        message = "通过" if passed else "; ".join(issues)

        return passed, message, max(0, score)

    def _check_fundamental(self, stock_details: Dict) -> Tuple[bool, str, float]:
        """检查基本面规则"""
        config = self.config['fundamental']

        issues = []
        score = 100

        if stock_details['pe_ratio'] > 0:
            if stock_details['pe_ratio'] < config['min_pe']:
                issues.append(f"PE过低: {stock_details['pe_ratio']:.1f}")
                score -= 20
            if stock_details['pe_ratio'] > config['max_pe']:
                issues.append(f"PE过高: {stock_details['pe_ratio']:.1f}")
                score -= 30

        if stock_details['pb_ratio'] > 0:
            if stock_details['pb_ratio'] < config['min_pb']:
                issues.append(f"PB过低: {stock_details['pb_ratio']:.2f}")
                score -= 15
            if stock_details['pb_ratio'] > config['max_pb']:
                issues.append(f"PB过高: {stock_details['pb_ratio']:.2f}")
                score -= 25

        if stock_details['roe'] < config['min_roe']:
            issues.append(f"ROE过低: {stock_details['roe']:.1f}%")
            score -= 20

        if stock_details['debt_ratio'] > config['max_debt_ratio']:
            issues.append(f"负债率过高: {stock_details['debt_ratio']:.1f}%")
            score -= 25

        passed = len(issues) == 0
        message = "通过" if passed else "; ".join(issues)

        return passed, message, max(0, score)

    def _check_compliance(self, stock_details: Dict) -> Tuple[bool, str, float]:
        """检查合规性规则"""
        config = self.config['compliance']

        issues = []
        score = 100

        if config['exclude_st'] and stock_details['is_st']:
            issues.append("ST股票")
            score = 0

        if config['exclude_suspended'] and stock_details['is_suspended']:
            issues.append("停牌股票")
            score = 0

        passed = len(issues) == 0
        message = "通过" if passed else "; ".join(issues)

        return passed, message, score

    def _check_technical(self, stock_details: Dict) -> Tuple[bool, str, float]:
        """检查技术面规则"""
        score = 80
        message = "技术面检查（简化版）"

        return True, message, score

    def _check_industry(self, stock_details: Dict) -> Tuple[bool, str, float]:
        """检查行业规则"""
        config = self.config['industry']

        issues = []
        score = 100

        if stock_details['industry'] in config['excluded_industries']:
            issues.append(f"行业被排除: {stock_details['industry']}")
            score -= 50

        if stock_details['industry'] in config['preferred_industries']:
            score += 20

        passed = True
        message = f"行业: {stock_details['industry']}" if stock_details['industry'] else "行业信息缺失"

        return passed, message, max(0, score)

    def filter_stock(self, symbol: str) -> Dict:
        """筛选单个股票"""
        logger.info(f"开始筛选股票: {symbol}")

        details = self.get_stock_details(symbol)

        results = {
            'symbol': symbol,
            'name': details['name'],
            'industry': details['industry'],
            'total_score': 0,
            'weighted_score': 0,
            'passed': True,
            'rule_results': [],
            'details': details
        }

        total_weight = 0
        weighted_score = 0

        for rule in self.rules:
            passed, message, score = rule['function'](details)

            rule_result = {
                'name': rule['name'],
                'passed': passed,
                'message': message,
                'raw_score': score,
                'weighted_score': score * rule['weight'],
                'weight': rule['weight'],
                'required': rule['required']
            }

            results['rule_results'].append(rule_result)
            results['total_score'] += score

            if passed or not rule['required']:
                weighted_score += score * rule['weight']
                total_weight += rule['weight']
            else:
                results['passed'] = False

            if rule['required'] and not passed:
                logger.info(f"股票{symbol}未通过必须规则: {rule['name']}")
                break

        if total_weight > 0:
            results['weighted_score'] = weighted_score / total_weight
        else:
            results['weighted_score'] = 0

        min_score = 60
        results['passed'] = results['passed'] and results['weighted_score'] >= min_score

        logger.info(f"股票{symbol}筛选完成: 加权分={results['weighted_score']:.1f}, 通过={results['passed']}")

        return results

    def filter_stock_pool(self, symbols: List[str] = None, max_stocks: int = 100) -> pd.DataFrame:
        """筛选股票池"""
        if symbols is None:
            all_stocks = self.get_all_a_shares()
            symbols = all_stocks['symbol'].tolist()

        logger.info(f"开始筛选股票池，共{len(symbols)}只股票")

        results = []
        passed_stocks = []

        for i, symbol in enumerate(symbols, 1):
            if i % 10 == 0:
                logger.info(f"筛选进度: {i}/{len(symbols)}")

            try:
                result = self.filter_stock(symbol)
                results.append(result)

                if result['passed']:
                    passed_stocks.append({
                        'symbol': symbol,
                        'name': result['name'],
                        'industry': result['industry'],
                        'weighted_score': result['weighted_score'],
                        'total_score': result['total_score'],
                        'details': result['details']
                    })

                if len(passed_stocks) >= max_stocks:
                    logger.info(f"已达到最大股票数量限制: {max_stocks}")
                    break

            except Exception as e:
                logger.error(f"筛选股票{symbol}时出错: {e}")
                continue

        passed_stocks.sort(key=lambda x: x['weighted_score'], reverse=True)

        df_data = []
        for stock in passed_stocks:
            df_data.append({
                'symbol': stock['symbol'],
                'name': stock['name'],
                'industry': stock['industry'],
                'weighted_score': stock['weighted_score'],
                'total_score': stock['total_score'],
                'price': stock['details']['price'],
                'daily_turnover': stock['details']['daily_turnover'],
                'daily_volume': stock['details']['daily_volume'],
                'market_cap': stock['details']['market_cap'],
                'pe_ratio': stock['details']['pe_ratio'],
                'pb_ratio': stock['details']['pb_ratio'],
                'roe': stock['details']['roe'],
                'debt_ratio': stock['details']['debt_ratio'],
            })

        result_df = pd.DataFrame(df_data)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = os.path.join(self.cache_dir, f"filtered_stock_pool_{timestamp}.csv")
        result_df.to_csv(result_file, index=False, encoding='utf-8')

        detail_file = os.path.join(self.cache_dir, f"filtered_stock_details_{timestamp}.json")
        with open(detail_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        logger.info(f"股票池筛选完成: 总共{len(symbols)}只，通过{len(passed_stocks)}只")
        logger.info(f"结果已保存: {result_file}")

        return result_df

    def generate_report(self, filtered_stocks: pd.DataFrame) -> str:
        """生成筛选报告"""
        if filtered_stocks.empty:
            return "筛选结果为空"

        report_lines = []

        report_lines.append("# 股票池筛选报告")
        report_lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"筛选股票数量: {len(filtered_stocks)}")
        report_lines.append("")

        score_stats = filtered_stocks['weighted_score'].describe()
        report_lines.append("## 分数分布")
        report_lines.append(f"- 平均分: {score_stats['mean']:.1f}")
        report_lines.append(f"- 最高分: {score_stats['max']:.1f}")
        report_lines.append(f"- 最低分: {score_stats['min']:.1f}")
        report_lines.append(f"- 中位数: {score_stats['50%']:.1f}")
        report_lines.append("")

        if 'industry' in filtered_stocks.columns and not filtered_stocks['industry'].isna().all():
            industry_counts = filtered_stocks['industry'].value_counts().head(10)
            report_lines.append("## 行业分布（前10）")
            for industry, count in industry_counts.items():
                report_lines.append(f"- {industry}: {count}只")
            report_lines.append("")

        if 'market_cap' in filtered_stocks.columns and filtered_stocks['market_cap'].sum() > 0:
            filtered_stocks['market_cap_group'] = pd.cut(
                filtered_stocks['market_cap'],
                bins=[0, 100e8, 500e8, 1000e8, 5000e8, float('inf')],
                labels=['<100亿', '100-500亿', '500-1000亿', '1000-5000亿', '>5000亿']
            )
            cap_counts = filtered_stocks['market_cap_group'].value_counts()
            report_lines.append("## 市值分布")
            for group, count in cap_counts.items():
                report_lines.append(f"- {group}: {count}只")
            report_lines.append("")

        report_lines.append("## 前20名股票")
        report_lines.append("| 排名 | 代码 | 名称 | 行业 | 加权分数 | 价格 | 成交额 |")
        report_lines.append("|------|------|------|------|----------|------|--------|")

        top_20 = filtered_stocks.head(20)
        for i, (_, row) in enumerate(top_20.iterrows(), 1):
            report_lines.append(
                f"| {i} | {row['symbol']} | {row['name']} | "
                f"{row.get('industry', '')} | {row['weighted_score']:.1f} | "
                f"{row.get('price', 0):.2f} | {row.get('daily_turnover', 0)/1e8:.2f}亿 |"
            )

        report_lines.append("")
        report_lines.append("## 筛选配置")
        report_lines.append("```json")
        report_lines.append(json.dumps(self.config, ensure_ascii=False, indent=2))
        report_lines.append("```")

        return "\n".join(report_lines)


def test_filter():
    """测试函数"""
    print("股票池筛选系统测试")
    print("=" * 50)

    filter = StockPoolFilter()

    print("1. 获取A股列表...")
    all_stocks = filter.get_all_a_shares()
    print(f"   获取到 {len(all_stocks)} 只A股股票")

    print("\n2. 测试筛选股票...")
    test_symbols = ['000001', '000002', '002352', '600580', '603728']

    for symbol in test_symbols:
        result = filter.filter_stock(symbol)
        status = "✅ 通过" if result['passed'] else "❌ 未通过"
        print(f"   {symbol}: {status} (分数: {result['weighted_score']:.1f})")

    print("\n3. 生成股票池...")
    filtered_pool = filter.filter_stock_pool(symbols=test_symbols, max_stocks=10)

    if not filtered_pool.empty:
        print(f"   生成股票池: {len(filtered_pool)} 只股票")
        print("\n   前5名股票:")
        for i, (_, row) in enumerate(filtered_pool.head(5).iterrows(), 1):
            print(f"   {i}. {row['symbol']} {row['name']} - 分数: {row['weighted_score']:.1f}")

        report = filter.generate_report(filtered_pool)
        report_file = "data/stock_pool/filter_report_fixed.md"
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n   报告已保存: {report_file}")
    else:
        print("   未筛选出任何股票")

    print("\n" + "=" * 50)
    print("股票池筛选系统测试完成")


if __name__ == "__main__":
    test_filter()
