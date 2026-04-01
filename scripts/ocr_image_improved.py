#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进的OCR图片文字识别
专门针对中文尾盘选股方法图片
"""

import os
import sys
import json
from datetime import datetime

try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

def preprocess_image(image_path):
    """预处理图片以提高OCR识别率"""
    try:
        # 打开图片
        image = Image.open(image_path)
        
        # 转换为灰度图
        if image.mode != 'L':
            image = image.convert('L')
        
        # 增强对比度
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)  # 提高对比度
        
        # 增强锐度
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)
        
        # 二值化处理
        threshold = 150
        image = image.point(lambda p: p > threshold and 255)
        
        # 去除噪声
        image = image.filter(ImageFilter.MedianFilter(size=3))
        
        return image
        
    except Exception as e:
        print(f"❌ 图片预处理失败: {e}")
        return None

def extract_text_with_multiple_methods(image_path):
    """使用多种方法提取文字"""
    results = {}
    
    # 方法1: 直接OCR
    try:
        image = Image.open(image_path)
        text_direct = pytesseract.image_to_string(image, lang='chi_sim+eng')
        results['direct'] = text_direct.strip()
    except Exception as e:
        results['direct'] = f"直接OCR失败: {e}"
    
    # 方法2: 预处理后OCR
    try:
        processed_image = preprocess_image(image_path)
        if processed_image:
            text_processed = pytesseract.image_to_string(processed_image, lang='chi_sim+eng')
            results['processed'] = text_processed.strip()
        else:
            results['processed'] = "图片预处理失败"
    except Exception as e:
        results['processed'] = f"预处理OCR失败: {e}"
    
    # 方法3: 只使用中文
    try:
        image = Image.open(image_path)
        text_chinese = pytesseract.image_to_string(image, lang='chi_sim')
        results['chinese_only'] = text_chinese.strip()
    except Exception as e:
        results['chinese_only'] = f"中文OCR失败: {e}"
    
    # 方法4: 只使用英文
    try:
        image = Image.open(image_path)
        text_english = pytesseract.image_to_string(image, lang='eng')
        results['english_only'] = text_english.strip()
    except Exception as e:
        results['english_only'] = f"英文OCR失败: {e}"
    
    return results

def analyze_tail_end_methods_advanced(text_results):
    """高级分析尾盘选股方法"""
    print("\n高级分析尾盘选股方法...")
    
    # 合并所有文本
    all_text = " ".join([v for v in text_results.values() if isinstance(v, str)])
    
    # 尾盘选股方法关键词
    method_patterns = {
        "尾盘拉升": ["尾盘拉升", "收盘前拉升", "尾盘上涨", "尾盘放量"],
        "尾盘突破": ["尾盘突破", "突破压力", "突破阻力", "突破高点"],
        "资金流入": ["资金流入", "大单流入", "主力流入", "资金净流入"],
        "技术指标": ["MACD", "KDJ", "RSI", "金叉", "死叉", "技术指标"],
        "形态选股": ["W底", "头肩底", "突破形态", "整理形态", "K线形态"],
        "成交量": ["放量", "缩量", "成交量", "量比", "换手率"],
        "时间窗口": ["14:30", "15:00", "收盘前", "尾盘时段", "最后30分钟"],
        "进场条件": ["进场", "买入", "建仓", "入场", "进场条件"],
        "止损止盈": ["止损", "止盈", "风险控制", "仓位管理"]
    }
    
    # 分析文本
    analysis = {
        "all_text": all_text[:1000] + "..." if len(all_text) > 1000 else all_text,
        "text_length": len(all_text),
        "method_matches": {},
        "detected_methods": [],
        "confidence_scores": {}
    }
    
    # 查找方法匹配
    for method_name, keywords in method_patterns.items():
        matches = []
        for keyword in keywords:
            if keyword in all_text:
                matches.append(keyword)
        
        if matches:
            analysis["method_matches"][method_name] = matches
            confidence = min(len(matches) * 20, 100)  # 每个匹配词增加20%置信度
            analysis["confidence_scores"][method_name] = confidence
    
    # 推断具体方法
    # 方法1: 尾盘拉升识别法
    if "尾盘拉升" in analysis["method_matches"] and "时间窗口" in analysis["method_matches"]:
        analysis["detected_methods"].append({
            "name": "尾盘拉升识别法",
            "description": "在收盘前30分钟识别放量拉升的股票",
            "confidence": analysis["confidence_scores"].get("尾盘拉升", 50),
            "key_conditions": ["尾盘时间窗口", "放量拉升", "价格突破"]
        })
    
    # 方法2: 尾盘突破法
    if "尾盘突破" in analysis["method_matches"] and "进场条件" in analysis["method_matches"]:
        analysis["detected_methods"].append({
            "name": "尾盘突破法",
            "description": "识别尾盘突破重要技术位的股票",
            "confidence": analysis["confidence_scores"].get("尾盘突破", 50),
            "key_conditions": ["突破压力位", "成交量配合", "技术确认"]
        })
    
    # 方法3: 资金流入法
    if "资金流入" in analysis["method_matches"]:
        analysis["detected_methods"].append({
            "name": "尾盘资金流入法",
            "description": "识别尾盘有大单资金持续流入的股票",
            "confidence": analysis["confidence_scores"].get("资金流入", 50),
            "key_conditions": ["大单净流入", "资金持续流入", "股价同步上涨"]
        })
    
    # 方法4: 技术指标法
    if "技术指标" in analysis["method_matches"]:
        analysis["detected_methods"].append({
            "name": "技术指标共振法",
            "description": "多个技术指标同时发出买入信号",
            "confidence": analysis["confidence_scores"].get("技术指标", 50),
            "key_conditions": ["MACD金叉", "KDJ低位金叉", "RSI超卖回升"]
        })
    
    # 如果没有检测到具体方法，使用通用方法
    if not analysis["detected_methods"] and analysis["method_matches"]:
        analysis["detected_methods"].append({
            "name": "综合尾盘选股法",
            "description": "基于多种因素综合判断的尾盘选股方法",
            "confidence": 30,
            "notes": "基于检测到的关键词推断",
            "detected_keywords": list(analysis["method_matches"].keys())
        })
    
    # 按置信度排序
    analysis["detected_methods"].sort(key=lambda x: x["confidence"], reverse=True)
    
    return analysis

def create_tail_end_strategy_from_analysis(analysis):
    """根据分析结果创建尾盘选股策略"""
    print("\n创建尾盘选股策略...")
    
    strategy = {
        "strategy_name": "基于OCR分析的尾盘选股策略",
        "strategy_version": "v3.0",
        "creation_date": datetime.now().strftime("%Y-%m-%d"),
        "analysis_source": "OCR图片识别",
        "detected_methods": analysis["detected_methods"],
        "strategy_config": {}
    }
    
    # 根据检测到的方法创建策略配置
    if analysis["detected_methods"]:
        # 提取所有方法的关键条件
        all_conditions = []
        for method in analysis["detected_methods"]:
            if "key_conditions" in method:
                all_conditions.extend(method["key_conditions"])
        
        # 去重
        all_conditions = list(set(all_conditions))
        
        # 创建策略规则
        strategy["strategy_config"] = {
            "selection_time": "14:30-15:00",
            "selection_criteria": all_conditions[:10],  # 取前10个条件
            "scoring_system": {
                "base_score": 50,
                "condition_bonus": 10,  # 每个符合条件加10分
                "minimum_score": 70
            },
            "entry_strategy": {
                "aggressive": "当前价格下跌1-2%",
                "steady": "当前价格下跌3-5%",
                "conservative": "当前价格下跌5-8%"
            },
            "risk_management": {
                "stop_loss": "下跌8-10%",
                "take_profit": "上涨8-15%",
                "position_size": "单只股票不超过总资金的20%"
            }
        }
    
    return strategy

def save_strategy_config(strategy):
    """保存策略配置"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 创建目录
    output_dir = "data/tail_end_strategy_v3"
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存策略配置
    config_path = os.path.join(output_dir, f"tail_end_strategy_v3_{timestamp}.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(strategy, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 策略配置已保存: {config_path}")
    return config_path

def generate_strategy_report(strategy, analysis):
    """生成策略报告"""
    report = []
    
    report.append("# 基于OCR分析的尾盘选股策略报告")
    report.append(f"## 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"## 策略名称: {strategy['strategy_name']}")
    report.append(f"## 策略版本: {strategy['strategy_version']}")
    report.append("")
    
    report.append("## 1. OCR分析结果")
    report.append(f"- **分析源**: {strategy['analysis_source']}")
    report.append(f"- **文本长度**: {analysis['text_length']} 字符")
    report.append(f"- **检测到的方法数**: {len(analysis['detected_methods'])}")
    report.append("")
    
    report.append("## 2. 检测到的尾盘选股方法")
    if analysis["detected_methods"]:
        for i, method in enumerate(analysis["detected_methods"], 1):
            report.append(f"### {i}. {method['name']}")
            report.append(f"- **描述**: {method['description']}")
            report.append(f"- **置信度**: {method['confidence']}%")
            if "key_conditions" in method:
                report.append(f"- **关键条件**: {', '.join(method['key_conditions'])}")
            if "notes" in method:
                report.append(f"- **备注**: {method['notes']}")
            report.append("")
    else:
        report.append("未检测到具体的尾盘选股方法")
        report.append("")
    
    report.append("## 3. 策略配置")
    if strategy["strategy_config"]:
        config = strategy["strategy_config"]
        report.append("### 3.1 选股时间")
        report.append(f"- **时间窗口**: {config['selection_time']}")
        report.append("")
        
        report.append("### 3.2 选股条件")
        for condition in config.get('selection_criteria', []):
            report.append(f"- {condition}")
        report.append("")
        
        report.append("### 3.3 评分系统")
        scoring = config.get('scoring_system', {})
        report.append(f"- **基础分**: {scoring.get('base_score', 0)}")
        report.append(f"- **条件加分**: {scoring.get('condition_bonus', 0)}")
        report.append(f"- **最低合格分**: {scoring.get('minimum_score', 0)}")
        report.append("")
        
        report.append("### 3.4 进场策略")
        entry = config.get('entry_strategy', {})
        for entry_type, desc in entry.items():
            report.append(f"- **{entry_type}**: {desc}")
        report.append("")
        
        report.append("### 3.5 风险管理")
        risk = config.get('risk_management', {})
        for control, value in risk.items():
            report.append(f"- **{control}**: {value}")
    else:
        report.append("策略配置为空")
    report.append("")
    
    report.append("## 4. 执行计划")
    report.append("### 4.1 今日执行")
    report.append("- **14:30**: 第一次尾盘选股")
    report.append("- **14:45**: 第二次尾盘选股")
    report.append("- **15:00**: 最终尾盘选股")
    report.append("- **16:00**: 生成当日报告")
    report.append("")
    
    report.append("### 4.2 输出文件")
    report.append("- 选股报告: `data/tail_end_selection_v3/`")
    report.append("- 投资组合: `data/investment_tracking/tail_end_portfolio_v3.json`")
    report.append("- 运行日志: `logs/tail_end_v3.log`")
    report.append("")
    
    report.append("## 5. 下一步操作")
    report.append("1. 验证OCR识别准确性")
    report.append("2. 根据用户反馈调整策略")
    report.append("3. 今天14:30开始自动执行")
    report.append("4. 监控策略执行效果")
    
    return "\n".join(report)

def main():
    """主函数"""
    print("改进的OCR图片文字识别系统")
    print("专门针对中文尾盘选股方法图片")
    print("=" * 60)
    
    if not OCR_AVAILABLE:
        print("❌ OCR库未安装")
        return False
    
    # 图片路径
    image_path = "/Users/ago/.openclaw/media/inbound/69744a2e-6758-4de2-87ef-b39b8911c75f.jpg"
    
    if not os.path.exists(image_path):
        print(f"❌ 图片文件不存在: {image_path}")
        return False
    
    print(f"📷 处理图片: {image_path}")
    
    # 使用多种方法提取文字
    print("\n使用多种OCR方法提取文字...")
    text_results = extract_text_with_multiple_methods(image_path)
    
    # 显示提取结果
    print("\nOCR提取结果:")
    for method, text in text_results.items():
        print(f"\n{method}:")
        if len(text) > 200:
            print(f"  {text[:200]}...")
        else:
            print(f"  {text}")
    
    # 高级分析
    analysis = analyze_tail_end_methods_advanced(text_results)
    
    # 创建策略
    strategy = create_tail_end_strategy_from_analysis(analysis)
    
    # 保存策略配置
    config_path = save_strategy_config(strategy)
    
    # 生成报告
    report = generate_strategy_report(strategy, analysis)
    
    # 保存报告
    report_dir = "data/tail_end_strategy_v3"
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f"strategy_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📋 策略报告: {report_path}")
    
    # 显示报告摘要
    print("\n" + "=" * 60)
    print("📄 策略报告摘要:")
    print("=" * 60)
    
    lines = report.split('\n')[:40]
    for line in lines:
        print(line)
    
    if len(report.split('\n')) > 40:
        print("...")
    
    print("\n" + "=" * 60)
    print("✅ OCR分析与策略创建完成!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)