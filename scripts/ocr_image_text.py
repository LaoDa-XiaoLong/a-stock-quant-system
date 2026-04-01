#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR识别图片文字
识别用户提供的尾盘选股方法图片
"""

import os
import sys
import json
from datetime import datetime

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

def check_ocr_dependencies():
    """检查OCR依赖"""
    print("检查OCR依赖...")
    
    missing_deps = []
    
    try:
        import pytesseract
        print("✅ pytesseract 已安装")
    except ImportError:
        missing_deps.append("pytesseract")
        print("❌ pytesseract 未安装")
    
    try:
        from PIL import Image
        print("✅ PIL/Pillow 已安装")
    except ImportError:
        missing_deps.append("Pillow")
        print("❌ PIL/Pillow 未安装")
    
    # 检查tesseract命令
    try:
        import subprocess
        result = subprocess.run(['which', 'tesseract'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ tesseract 已安装: {result.stdout.strip()}")
        else:
            missing_deps.append("tesseract")
            print("❌ tesseract 未安装")
    except:
        missing_deps.append("tesseract")
        print("❌ 无法检查tesseract")
    
    return missing_deps

def extract_text_from_image(image_path):
    """从图片中提取文字"""
    if not OCR_AVAILABLE:
        print("❌ OCR库未安装，无法提取文字")
        return None
    
    if not os.path.exists(image_path):
        print(f"❌ 图片文件不存在: {image_path}")
        return None
    
    try:
        print(f"正在识别图片文字: {image_path}")
        
        # 打开图片
        image = Image.open(image_path)
        
        # 获取图片信息
        width, height = image.size
        print(f"图片尺寸: {width}x{height}")
        print(f"图片格式: {image.format}")
        print(f"图片模式: {image.mode}")
        
        # 使用OCR提取文字
        print("正在使用OCR提取文字...")
        text = pytesseract.image_to_string(image, lang='chi_sim+eng')
        
        # 清理文字
        text = text.strip()
        
        if text:
            print(f"✅ 成功提取 {len(text)} 个字符")
            return text
        else:
            print("❌ 未识别到文字")
            return None
            
    except Exception as e:
        print(f"❌ OCR识别失败: {e}")
        return None

def analyze_tail_end_methods_from_text(text):
    """从文字中分析尾盘选股方法"""
    print("\n分析尾盘选股方法...")
    
    # 常见尾盘选股关键词
    keywords = {
        "尾盘": ["尾盘", "收盘前", "收盘", "下午", "14:", "15:", "最后"],
        "拉升": ["拉升", "上涨", "涨", "突破", "冲高", "放量"],
        "资金": ["资金", "流入", "流出", "主力", "大单", "机构"],
        "技术": ["MACD", "KDJ", "RSI", "均线", "金叉", "死叉", "指标"],
        "形态": ["形态", "W底", "头肩", "突破", "平台", "整理"],
        "成交量": ["成交量", "放量", "缩量", "量比", "换手"],
        "价格": ["价格", "价位", "点位", "支撑", "压力", "突破"]
    }
    
    # 分析文本
    analysis = {
        "extracted_text": text[:500] + "..." if len(text) > 500 else text,
        "text_length": len(text),
        "keywords_found": {},
        "methods_detected": [],
        "confidence": "medium"
    }
    
    # 查找关键词
    for category, words in keywords.items():
        found_words = []
        for word in words:
            if word.lower() in text.lower():
                found_words.append(word)
        
        if found_words:
            analysis["keywords_found"][category] = found_words
    
    # 根据关键词推断方法
    methods = []
    
    # 方法1: 尾盘拉升识别法
    if ("尾盘" in analysis["keywords_found"]) and ("拉升" in analysis["keywords_found"] or "放量" in analysis["keywords_found"]):
        methods.append({
            "name": "尾盘拉升识别法",
            "description": "识别收盘前30分钟开始放量拉升的股票",
            "confidence": "high" if "放量" in analysis["keywords_found"] else "medium"
        })
    
    # 方法2: 尾盘突破法
    if ("突破" in analysis["keywords_found"]) and ("价格" in analysis["keywords_found"] or "压力" in analysis["keywords_found"]):
        methods.append({
            "name": "尾盘突破法",
            "description": "识别尾盘突破重要技术位的股票",
            "confidence": "high" if "压力" in analysis["keywords_found"] else "medium"
        })
    
    # 方法3: 尾盘资金流入法
    if ("资金" in analysis["keywords_found"]) and ("流入" in analysis["keywords_found"] or "主力" in analysis["keywords_found"]):
        methods.append({
            "name": "尾盘资金流入法",
            "description": "识别尾盘有大单资金持续流入的股票",
            "confidence": "high" if "大单" in analysis["keywords_found"] else "medium"
        })
    
    # 方法4: 技术指标共振法
    if ("技术" in analysis["keywords_found"]) and ("MACD" in analysis["keywords_found"] or "KDJ" in analysis["keywords_found"]):
        methods.append({
            "name": "技术指标共振法",
            "description": "多个技术指标同时发出买入信号",
            "confidence": "high" if "金叉" in analysis["keywords_found"] else "medium"
        })
    
    # 方法5: 形态选股法
    if ("形态" in analysis["keywords_found"]) and ("W底" in analysis["keywords_found"] or "头肩" in analysis["keywords_found"]):
        methods.append({
            "name": "形态选股法",
            "description": "基于K线形态和分时图形态选股",
            "confidence": "high" if "W底" in analysis["keywords_found"] else "medium"
        })
    
    # 如果没有检测到特定方法，使用通用方法
    if not methods and analysis["keywords_found"]:
        methods.append({
            "name": "综合尾盘选股法",
            "description": "基于多种因素综合判断的尾盘选股方法",
            "confidence": "low",
            "notes": "未检测到具体方法，使用综合方法"
        })
    
    analysis["methods_detected"] = methods
    
    return analysis

def save_analysis_results(analysis, image_path):
    """保存分析结果"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 创建输出目录
    output_dir = "data/ocr_analysis"
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存JSON结果
    json_path = os.path.join(output_dir, f"ocr_analysis_{timestamp}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    # 保存文本结果
    text_path = os.path.join(output_dir, f"extracted_text_{timestamp}.txt")
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(analysis.get("extracted_text", "无文字内容"))
    
    print(f"\n✅ 分析结果已保存:")
    print(f"  - JSON文件: {json_path}")
    print(f"  - 文本文件: {text_path}")
    
    return json_path, text_path

def generate_report(analysis):
    """生成分析报告"""
    report = []
    
    report.append("# OCR图片文字识别分析报告")
    report.append(f"## 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"## 分析图片: 用户提供的尾盘选股方法图片")
    report.append("")
    
    report.append("## 1. 文字提取结果")
    report.append(f"- **提取字符数**: {analysis['text_length']}")
    report.append(f"- **置信度**: {analysis['confidence']}")
    report.append("")
    
    report.append("### 提取的文字内容:")
    report.append("```")
    report.append(analysis.get("extracted_text", "无文字内容"))
    report.append("```")
    report.append("")
    
    report.append("## 2. 关键词分析")
    if analysis["keywords_found"]:
        for category, words in analysis["keywords_found"].items():
            report.append(f"- **{category}**: {', '.join(words)}")
    else:
        report.append("- 未识别到关键词")
    report.append("")
    
    report.append("## 3. 尾盘选股方法识别")
    if analysis["methods_detected"]:
        for i, method in enumerate(analysis["methods_detected"], 1):
            report.append(f"### {i}. {method['name']}")
            report.append(f"- **描述**: {method['description']}")
            report.append(f"- **置信度**: {method['confidence']}")
            if method.get('notes'):
                report.append(f"- **备注**: {method['notes']}")
            report.append("")
    else:
        report.append("未识别到具体的尾盘选股方法")
        report.append("")
    
    report.append("## 4. 建议")
    report.append("基于分析结果，建议:")
    
    if analysis["methods_detected"]:
        report.append("1. **使用识别到的方法**构建尾盘选股策略")
        report.append("2. **结合多种方法**提高选股准确性")
        report.append("3. **根据置信度**调整策略权重")
    else:
        report.append("1. **使用通用尾盘选股方法**")
        report.append("2. **等待用户确认具体方法**")
        report.append("3. **基于常见方法建立策略**")
    
    report.append("")
    report.append("## 5. 下一步操作")
    report.append("1. 根据识别的方法优化尾盘选股策略")
    report.append("2. 等待用户确认方法准确性")
    report.append("3. 实施优化后的策略")
    
    return "\n".join(report)

def main():
    """主函数"""
    print("OCR图片文字识别系统")
    print("=" * 60)
    
    # 检查依赖
    missing_deps = check_ocr_dependencies()
    if missing_deps:
        print(f"\n❌ 缺少依赖: {', '.join(missing_deps)}")
        print("请安装依赖:")
        print("  pip3 install pytesseract pillow")
        print("  brew install tesseract")
        return False
    
    # 图片路径
    image_path = "/Users/ago/.openclaw/media/inbound/69744a2e-6758-4de2-87ef-b39b8911c75f.jpg"
    
    if not os.path.exists(image_path):
        print(f"❌ 图片文件不存在: {image_path}")
        print("请确保图片已正确上传")
        return False
    
    print(f"\n📷 处理图片: {image_path}")
    
    # 提取文字
    text = extract_text_from_image(image_path)
    
    if not text:
        print("\n❌ 无法从图片中提取文字")
        print("可能原因:")
        print("  1. 图片质量不佳")
        print("  2. 文字太小或模糊")
        print("  3. 语言不支持")
        print("\n建议:")
        print("  1. 提供更清晰的图片")
        print("  2. 手动描述图片内容")
        print("  3. 使用其他OCR工具")
        return False
    
    print("\n" + "=" * 60)
    print("📊 文字提取成功!")
    print("=" * 60)
    
    # 分析尾盘选股方法
    analysis = analyze_tail_end_methods_from_text(text)
    
    # 保存结果
    json_path, text_path = save_analysis_results(analysis, image_path)
    
    # 生成报告
    report = generate_report(analysis)
    
    # 保存报告
    report_path = os.path.join("data/ocr_analysis", f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📋 分析报告: {report_path}")
    
    # 显示报告摘要
    print("\n" + "=" * 60)
    print("📄 报告摘要:")
    print("=" * 60)
    
    lines = report.split('\n')[:30]
    for line in lines:
        print(line)
    
    if len(report.split('\n')) > 30:
        print("...")
    
    print("\n" + "=" * 60)
    print("✅ OCR分析完成!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)