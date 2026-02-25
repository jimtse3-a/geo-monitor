#!/bin/bash

# GEO AI 搜索引擎监测工具启动脚本

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║         GEO AI 搜索引擎监测工具 - 演示版                    ║"
echo "║         监测品牌在 AI 平台的可见率与关键词录用情况          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

show_menu() {
    echo "请选择操作："
    echo ""
    echo "  [1] 启动交互式 WEB 仪表盘（推荐）"
    echo "  [2] 生成演示数据（7天）"
    echo "  [3] 生成演示数据（30天）"
    echo "  [4] 运行完整监测"
    echo "  [5] 生成 HTML 报告"
    echo "  [6] 查看帮助"
    echo "  [0] 退出"
    echo ""
    read -p "请输入选项 (0-6): " choice
    
    case $choice in
        1) start_dashboard ;;
        2) generate_demo 7 ;;
        3) generate_demo 30 ;;
        4) run_monitor ;;
        5) generate_report ;;
        6) show_help ;;
        0) exit 0 ;;
        *) 
            echo "无效选项，请重新选择。"
            show_menu
            ;;
    esac
}

start_dashboard() {
    echo ""
    echo "正在启动交互式仪表盘..."
    
    # 根据操作系统打开浏览器
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open index.html
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open index.html
    else
        echo "请手动打开 index.html 文件"
    fi
    
    echo "✅ 已打开 index.html"
    echo ""
    read -p "按回车键继续..."
    show_menu
}

generate_demo() {
    echo ""
    echo "正在生成 $1 天演示数据..."
    python3 monitor.py --demo --days $1
    echo ""
    read -p "按回车键继续..."
    show_menu
}

run_monitor() {
    echo ""
    echo "正在运行完整监测..."
    python3 monitor.py
    echo ""
    read -p "按回车键继续..."
    show_menu
}

generate_report() {
    echo ""
    echo "正在生成报告..."
    python3 monitor.py --report
    echo ""
    read -p "按回车键继续..."
    show_menu
}

show_help() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                         使用帮助                            ║"
    echo "╠════════════════════════════════════════════════════════════╣"
    echo "║  1. WEB 仪表盘 - 可视化界面，支持多品牌/多平台监测          ║"
    echo "║  2. 命令行模式 - 适合自动化和批处理                          ║"
    echo "║                                                            ║"
    echo "║  命令行参数：                                              ║"
    echo "║    python3 monitor.py --platforms kimi doubao              ║"
    echo "║    python3 monitor.py --brands 印暨咖啡 星巴克              ║"
    echo "║    python3 monitor.py --demo --days 30                     ║"
    echo "║                                                            ║"
    echo "║  支持的平台：                                              ║"
    echo "║    kimi, doubao, qianwen, deepseek, wenxin, hunyuan, zhipu ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    read -p "按回车键继续..."
    show_menu
}

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误：未找到 Python3，请先安装 Python3"
    exit 1
fi

# 启动菜单
show_menu
