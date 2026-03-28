#!/bin/bash
# A股量化交易系统 - 项目设置脚本

set -e  # 遇到错误立即退出

echo "========================================="
echo "A股量化交易系统 - 项目设置"
echo "========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 函数：打印带颜色的消息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Python版本
check_python_version() {
    print_info "检查Python版本..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_info "找到Python $PYTHON_VERSION"
        
        # 检查版本是否 >= 3.8
        MAJOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f1)
        MINOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ $MAJOR_VERSION -lt 3 ] || ([ $MAJOR_VERSION -eq 3 ] && [ $MINOR_VERSION -lt 8 ]); then
            print_error "需要Python 3.8或更高版本，当前版本: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "未找到Python3，请先安装Python 3.8+"
        exit 1
    fi
}

# 检查Git
check_git() {
    print_info "检查Git..."
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version | cut -d' ' -f3)
        print_info "找到Git $GIT_VERSION"
    else
        print_error "未找到Git，请先安装Git"
        exit 1
    fi
}

# 创建虚拟环境
create_venv() {
    print_info "创建Python虚拟环境..."
    
    if [ -d "venv" ]; then
        print_warning "虚拟环境已存在，跳过创建"
    else
        python3 -m venv venv
        print_info "虚拟环境创建成功"
    fi
    
    # 激活虚拟环境
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        print_info "虚拟环境已激活"
    else
        print_error "无法激活虚拟环境"
        exit 1
    fi
}

# 安装依赖
install_dependencies() {
    print_info "安装项目依赖..."
    
    # 升级pip
    pip install --upgrade pip
    
    # 安装基础依赖
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_info "基础依赖安装完成"
    else
        print_error "未找到requirements.txt文件"
        exit 1
    fi
    
    # 安装开发依赖
    print_info "安装开发依赖..."
    pip install pylint black mypy pytest pytest-cov pre-commit
    
    # 安装可选依赖
    print_info "安装可选依赖..."
    pip install loguru tqdm python-dotenv
    
    print_info "所有依赖安装完成"
}

# 配置Git
setup_git() {
    print_info "配置Git..."
    
    # 检查是否在Git仓库中
    if [ ! -d ".git" ]; then
        print_warning "当前目录不是Git仓库，跳过Git配置"
        return
    fi
    
    # 设置Git用户信息（如果未设置）
    if [ -z "$(git config user.name)" ]; then
        read -p "请输入Git用户名: " git_username
        git config --global user.name "$git_username"
    fi
    
    if [ -z "$(git config user.email)" ]; then
        read -p "请输入Git邮箱: " git_email
        git config --global user.email "$git_email"
    fi
    
    # 设置Git编辑器
    git config --global core.editor "code --wait"
    
    # 设置行尾处理
    git config --global core.autocrlf input
    
    print_info "Git配置完成"
}

# 设置pre-commit钩子
setup_pre_commit() {
    print_info "设置pre-commit钩子..."
    
    if command -v pre-commit &> /dev/null; then
        pre-commit install
        print_info "pre-commit钩子安装完成"
    else
        print_warning "pre-commit未安装，跳过钩子设置"
    fi
}

# 运行测试
run_tests() {
    print_info "运行测试..."
    
    if [ -d "tests" ]; then
        python -m pytest tests/ -v
        if [ $? -eq 0 ]; then
            print_info "测试通过"
        else
            print_warning "测试失败，但继续设置"
        fi
    else
        print_warning "未找到测试目录，跳过测试"
    fi
}

# 代码质量检查
run_code_quality() {
    print_info "运行代码质量检查..."
    
    # 运行pylint
    if command -v pylint &> /dev/null; then
        python -m pylint scripts/ --fail-under=8.0 || print_warning "代码质量检查未通过，但继续设置"
    fi
    
    # 运行black检查
    if command -v black &> /dev/null; then
        python -m black --check scripts/ || print_warning "代码格式需要调整"
    fi
}

# 创建配置文件
create_config_files() {
    print_info "创建配置文件..."
    
    # 创建示例配置文件
    if [ ! -f "config/financial_monitor_config.json" ]; then
        mkdir -p config
        cat > config/financial_monitor_config.json << 'EOF'
{
  "monitor_config": {
    "check_interval_seconds": 3600,
    "max_workers": 10,
    "batch_size": 100,
    "alert_threshold": 0.2,
    "high_alert_threshold": 0.5
  },
  
  "data_sources": {
    "eastmoney": "http://data.eastmoney.com/",
    "sina_finance": "http://vip.stock.finance.sina.com.cn/",
    "tushare": "https://tushare.pro/",
    "akshare": "https://www.akshare.xyz/",
    "szse": "http://www.szse.cn/",
    "sse": "http://www.sse.com.cn/",
    "cninfo": "http://www.cninfo.com.cn/"
  },
  
  "focus_industries": [
    "新能源汽车",
    "锂电池",
    "光伏",
    "半导体",
    "医药",
    "白酒",
    "银行",
    "保险",
    "证券"
  ],
  
  "holding_stocks": [
    {"code": "000001", "name": "平安银行"},
    {"code": "000002", "name": "万科A"},
    {"code": "002352", "name": "顺丰控股"},
    {"code": "600519", "name": "贵州茅台"},
    {"code": "000858", "name": "五粮液"},
    {"code": "002594", "name": "比亚迪"},
    {"code": "603259", "name": "药明康德"}
  ],
  
  "feishu_webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_TOKEN",
  
  "database": {
    "path": "data/final_financial/final_reports.db",
    "backup_dir": "data/backups/"
  },
  
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "logs/quant_system.log"
  }
}
EOF
        print_info "配置文件创建完成: config/financial_monitor_config.json"
        print_warning "请编辑配置文件，特别是飞书Webhook和API密钥"
    fi
}

# 创建数据目录
create_data_directories() {
    print_info "创建数据目录..."
    
    mkdir -p data/final_financial
    mkdir -p data/quality_validation
    mkdir -p data/stock_pool
    mkdir -p data/backups
    mkdir -p logs
    mkdir -p reports
    
    print_info "数据目录创建完成"
}

# 显示完成信息
show_completion() {
    echo ""
    echo "========================================="
    echo "🎉 项目设置完成！"
    echo "========================================="
    echo ""
    echo "下一步操作："
    echo ""
    echo "1. 编辑配置文件："
    echo "   📝 config/financial_monitor_config.json"
    echo "   特别是飞书Webhook和API密钥"
    echo ""
    echo "2. 激活虚拟环境："
    echo "   source venv/bin/activate"
    echo ""
    echo "3. 运行财报监控："
    echo "   python scripts/final_financial_monitor_fixed.py"
    echo ""
    echo "4. 运行股票池筛选："
    echo "   python strategies/stock_pool_filter_fixed.py"
    echo ""
    echo "5. 查看文档："
    echo "   📚 docs/ 目录包含完整文档"
    echo ""
    echo "6. GitHub仓库设置："
    echo "   按照 docs/github_setup_guide.md 配置远程仓库"
    echo ""
    echo "========================================="
    echo "📊 项目信息："
    echo "========================================="
    echo "• Python版本: $PYTHON_VERSION"
    echo "• Git版本: $GIT_VERSION"
    echo "• 虚拟环境: venv/"
    echo "• 依赖安装: 完成"
    echo "• 配置文件: 已创建"
    echo "• 数据目录: 已创建"
    echo ""
    echo "💡 提示：每次开发前记得激活虚拟环境"
    echo "========================================="
}

# 主函数
main() {
    echo ""
    print_info "开始设置A股量化交易系统..."
    echo ""
    
    # 执行设置步骤
    check_python_version
    check_git
    create_venv
    install_dependencies
    setup_git
    setup_pre_commit
    create_config_files
    create_data_directories
    run_tests
    run_code_quality
    
    # 显示完成信息
    show_completion
}

# 运行主函数
main "$@"