
class FixedDataQualityValidator(DataQualityValidator):
    """修复版数据质量验证器"""

    def _check_consistency(self, data: Dict) -> float:
        """加强版数据一致性检查"""
        score = 100

        # 检查营收和利润的一致性
        if 'revenue_yoy' in data and 'profit_yoy' in data:
            revenue_growth = data['revenue_yoy']
            profit_growth = data['profit_yoy']

            # 1. 营收增长但利润大幅下降（增收不增利）
            if revenue_growth > 0.1 and profit_growth < -0.1:
                score -= 25

            # 2. 营收下降但利润大幅增长（可能有问题）
            elif revenue_growth < -0.1 and profit_growth > 0.2:
                score -= 20

            # 3. 营收和利润增长方向相反
            elif revenue_growth * profit_growth < 0:
                score -= 15

            # 4. 利润为0或接近0（特殊情况）
            if abs(profit_growth) < 0.01:  # 增长小于1%
                score -= 10

        # 检查毛利率和净利率的一致性
        if 'gross_margin' in data and 'net_margin' in data:
            gross_margin = data['gross_margin']
            net_margin = data['net_margin']

            # 净利率不应超过毛利率
            if net_margin > gross_margin:
                score -= 30

            # 净利率通常远低于毛利率
            elif net_margin > gross_margin * 0.7:  # 降低阈值
                score -= 15

            # 净利率为负但毛利率为正（可能有问题）
            elif net_margin < 0 and gross_margin > 0.1:
                score -= 20

        return max(0, score)

    def _check_extreme_values(self, data: Dict) -> Dict:
        """加强版极端值检查"""
        results = {
            'penalty': 0,
            'extreme_values': [],
            'warnings': [],
            'errors': []
        }

        # 降低阈值
        extreme_thresholds = {
            'revenue_yoy': 2.0,      # 降低到200%增长
            'profit_yoy': 3.0,       # 降低到300%增长
            'revenue_amount': 5000,  # 降低到5000亿元
            'profit_amount': 500,    # 降低到500亿元
        }

        for field, threshold in extreme_thresholds.items():
            if field in data and data[field] is not None:
                value = data[field]

                if abs(value) > threshold:
                    results['penalty'] += 25  # 增加惩罚
                    results['extreme_values'].append({
                        'field': field,
                        'value': value,
                        'threshold': threshold
                    })

                    if field.endswith('_yoy'):
                        results['errors'].append(  # 改为错误
                            f"{field}增长异常: {value:.1%} (阈值: {threshold:.1%})"
                        )
                    else:
                        results['errors'].append(
                            f"{field}数值异常: {value:,.0f} (阈值: {threshold:,.0f})"
                        )

        return results

    def validate_financial_data(self, stock_code: str, stock_name: str,
                               financial_data: Dict) -> Dict:
        """修复版验证方法"""
        result = super().validate_financial_data(stock_code, stock_name, financial_data)

        # 添加专项检查
        special_checks = self._perform_special_checks(financial_data)

        # 更新分数
        result['overall_score'] = max(0, result['overall_score'] - special_checks['penalty'])

        # 更新警告和错误
        result['warnings'].extend(special_checks['warnings'])
        result['errors'].extend(special_checks['errors'])

        # 更新合理性判断
        if result['overall_score'] < 75:
            result['is_reasonable'] = False

        return result

    def _perform_special_checks(self, data: Dict) -> Dict:
        """专项检查"""
        results = {
            'penalty': 0,
            'warnings': [],
            'errors': []
        }

        # 检查利润质量
        if 'profit_yoy' in data:
            profit_growth = data['profit_yoy']

            # 利润为0或接近0
            if abs(profit_growth) < 0.01:
                results['penalty'] += 15
                results['errors'].append("利润增长接近0%，需要特别关注")

            # 利润为负但营收大幅增长
            if profit_growth < 0 and data.get('revenue_yoy', 0) > 0.5:
                results['penalty'] += 20
                results['errors'].append("营收大幅增长但利润为负，可能存在成本问题")

        return results
