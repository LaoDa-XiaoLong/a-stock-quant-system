"""
测试配置和fixture
"""
import pytest
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def sample_stock_data():
    """示例股票数据"""
    return {
        'stock_code': '000001',
        'stock_name': '平安银行',
        'revenue_actual': 1000000000.0,
        'revenue_expected': 900000000.0,
        'revenue_exceed': 0.1111,
        'profit_actual': 200000000.0,
        'profit_expected': 180000000.0,
        'profit_exceed': 0.1111,
        'revenue_yoy': 0.15,
        'profit_yoy': 0.20,
        'report_type': '年报',
        'report_date': '2026-03-28'
    }

@pytest.fixture
def sample_stock_list():
    """示例股票列表"""
    return [
        ('000001', '平安银行'),
        ('000002', '万科A'),
        ('002352', '顺丰控股'),
        ('600519', '贵州茅台'),
        ('000858', '五粮液'),
        ('002594', '比亚迪'),
        ('603259', '药明康德')
    ]

@pytest.fixture
def temp_db_path(tmp_path):
    """临时数据库路径"""
    db_dir = tmp_path / "test_data"
    db_dir.mkdir()
    return str(db_dir / "test.db")

@pytest.fixture
def mock_config():
    """模拟配置"""
    return {
        'monitor_config': {
            'check_interval_seconds': 3600,
            'max_workers': 10,
            'batch_size': 100,
            'alert_threshold': 0.2,
            'high_alert_threshold': 0.5
        },
        'data_sources': {
            'eastmoney': 'http://data.eastmoney.com/',
            'sina_finance': 'http://vip.stock.finance.sina.com.cn/',
            'akshare': 'https://www.akshare.xyz/'
        }
    }