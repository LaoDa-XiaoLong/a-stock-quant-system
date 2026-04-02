"""
财报监控系统单元测试
"""
import pytest
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.final_financial_monitor_fixed import FinancialMonitorFixed


class TestFinancialMonitorFixed:
    """财报监控系统测试"""

    def test_init(self, mock_config, tmp_path):
        """测试初始化"""
        # 创建临时配置文件
        config_path = tmp_path / "test_config.json"
        import json
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(mock_config, f)

        monitor = FinancialMonitorFixed(str(config_path))
        assert monitor is not None
        assert monitor.alert_threshold == 0.2
        assert monitor.quality_threshold == 75

    def test_get_financial_data(self):
        """测试获取财务数据"""
        monitor = FinancialMonitorFixed()
        data = monitor.get_financial_data('000001', '平安银行')

        assert data is not None
        assert data['stock_code'] == '000001'
        assert data['stock_name'] == '平安银行'
        assert 'revenue_actual' in data
        assert 'profit_actual' in data
        assert 'revenue_exceed' in data
        assert 'profit_exceed' in data
        assert 'report_type' in data
        assert 'report_date' in data

    def test_validate_data_quality(self, sample_stock_data):
        """测试数据质量验证"""
        monitor = FinancialMonitorFixed()

        # 测试正常数据
        result = monitor.validate_data_quality(sample_stock_data)
        assert result['overall_score'] >= 75
        assert result['is_reasonable'] is True
        assert len(result['errors']) == 0

        # 测试异常数据（营收为负）
        bad_data = sample_stock_data.copy()
        bad_data['revenue_actual'] = -1000000
        result = monitor.validate_data_quality(bad_data)
        assert result['overall_score'] < 75
        assert '营收实际值必须大于0' in result['errors']

    def test_analyze_stock(self, sample_stock_data, tmp_path):
        """测试股票分析"""
        monitor = FinancialMonitorFixed()

        # 模拟数据获取
        import types
        monitor.get_financial_data = lambda code, name: sample_stock_data

        result = monitor.analyze_stock('000001', '平安银行')

        assert result is not None
        assert result['stock_code'] == '000001'
        assert result['stock_name'] == '平安银行'
        assert 'alert_level' in result
        assert 'data_quality_score' in result
        assert 'is_reasonable' in result

    def test_alert_level_calculation(self):
        """测试警报级别计算"""
        monitor = FinancialMonitorFixed()

        # 测试超预期
        data = {
            'revenue_exceed': 0.25,  # 25% > 20%阈值
            'profit_exceed': 0.15,
            'data_quality_score': 95.0,
            'is_reasonable': True
        }
        # 这里需要调用内部方法或重构代码以便测试

        # 测试不及预期
        data = {
            'revenue_exceed': -0.25,  # -25% < -20%阈值
            'profit_exceed': -0.15,
            'data_quality_score': 95.0,
            'is_reasonable': True
        }

        # 测试正常
        data = {
            'revenue_exceed': 0.15,  # 15%在阈值内
            'profit_exceed': 0.10,
            'data_quality_score': 95.0,
            'is_reasonable': True
        }

    def test_generate_daily_report(self, sample_stock_list):
        """测试日报生成"""
        monitor = FinancialMonitorFixed()

        # 模拟分析结果
        results = []
        for code, name in sample_stock_list[:3]:
            data = monitor.get_financial_data(code, name)
            if data:
                results.append(data)

        # 生成报告
        report = monitor._generate_daily_report(
            results,
            exceeded_stocks=results[:1],
            warning_stocks=results[1:2],
            quality_warnings=[]
        )

        assert report is not None
        assert 'date' in report
        assert 'total_stocks' in report
        assert 'exceeded_count' in report
        assert 'warning_count' in report
        assert 'avg_quality_score' in report

    def test_system_status(self):
        """测试系统状态获取"""
        monitor = FinancialMonitorFixed()
        status = monitor.get_system_status()

        assert status is not None
        assert 'system' in status
        assert 'version' in status
        assert 'status' in status
        assert 'config' in status
        assert 'database' in status


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
