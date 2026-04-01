#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础功能测试
测试量化分析项目的基本功能
"""

import unittest
import os
import sys
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

class TestBasicFunctionality(unittest.TestCase):
    """基础功能测试类"""
    
    def test_project_structure(self):
        """测试项目结构"""
        # 检查必要的目录是否存在
        required_dirs = [
            'strategies',
            'config', 
            'data',
            'logs',
            'reports',
            'tests'
        ]
        
        for dir_name in required_dirs:
            dir_path = os.path.join(os.path.dirname(__file__), '..', dir_name)
            self.assertTrue(os.path.exists(dir_path), f"目录不存在: {dir_name}")
    
    def test_config_files(self):
        """测试配置文件"""
        config_files = [
            'config/financial_monitor_config.json',
            'config/stock_pool_config.json'
        ]
        
        for config_file in config_files:
            file_path = os.path.join(os.path.dirname(__file__), '..', config_file)
            if os.path.exists(file_path):
                # 验证JSON格式
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        config_data = json.load(f)
                        self.assertIsInstance(config_data, dict, f"配置文件不是有效的JSON字典: {config_file}")
                    except json.JSONDecodeError as e:
                        self.fail(f"配置文件JSON格式错误 {config_file}: {e}")
    
    def test_python_files(self):
        """测试Python文件语法"""
        import subprocess
        
        # 检查strategies目录下的Python文件
        strategies_dir = os.path.join(os.path.dirname(__file__), '..', 'strategies')
        if os.path.exists(strategies_dir):
            for root, dirs, files in os.walk(strategies_dir):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        # 使用python -m py_compile检查语法
                        result = subprocess.run(
                            [sys.executable, '-m', 'py_compile', file_path],
                            capture_output=True,
                            text=True
                        )
                        self.assertEqual(result.returncode, 0, 
                                       f"Python文件语法错误 {file_path}: {result.stderr}")
    
    def test_import_modules(self):
        """测试模块导入"""
        # 测试是否能导入一些关键模块
        try:
            # 这里可以添加项目特定的模块导入测试
            pass
        except ImportError as e:
            self.fail(f"模块导入失败: {e}")

class TestDataQuality(unittest.TestCase):
    """数据质量测试"""
    
    def test_data_directory(self):
        """测试数据目录"""
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        if os.path.exists(data_dir):
            # 检查数据目录是否可访问
            self.assertTrue(os.access(data_dir, os.R_OK), "数据目录不可读")
            self.assertTrue(os.access(data_dir, os.W_OK), "数据目录不可写")
    
    def test_logs_directory(self):
        """测试日志目录"""
        logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        if os.path.exists(logs_dir):
            self.assertTrue(os.access(logs_dir, os.R_OK), "日志目录不可读")
            self.assertTrue(os.access(logs_dir, os.W_OK), "日志目录不可写")

if __name__ == '__main__':
    unittest.main(verbosity=2)