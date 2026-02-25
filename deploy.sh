#!/bin/bash

# GEO AI 搜索引擎监测工具 - 快速部署脚本

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║     GEO AI 搜索引擎监测工具 - 快速部署                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 检查 Git
if ! command -v git &> /dev/null; then
    echo "❌ 错误：未检测到 Git"
    echo "请先安装 Git："
    echo "  Mac: brew install git"
    echo "  Linux: sudo apt-get install git"
    exit 1
fi

echo "✅ Git 已安装"

# 检查文件
if [ ! -f "index.html" ]; then
    echo "❌ 错误：未找到 index.html"
    echo "请确保在 geo-monitor 文件夹内运行此脚本"
    exit 1
fi

echo "✅ 文件检查通过"

show_menu() {
    echo ""
    echo "请选择部署方式："
    echo ""
    echo "  [1] Vercel 部署（推荐，自动更新）"
    echo "  [2] GitHub Pages 部署（最简单）"
    echo "  [3] 仅创建 GitHub 仓库（不上传）"
    echo "  [0] 退出"
    echo ""
    read -p "请输入选项: " choice
    
    case $choice in
        1) deploy_vercel ;;
        2) deploy_github_pages ;;
        3) create_repo ;;
        0) exit 0 ;;
        *) show_menu ;;
    esac
}

create_repo() {
    echo ""
    echo "📦 创建 GitHub 仓库..."
    echo ""
    read -p "请输入你的 GitHub 用户名: " username
    
    echo ""
    echo "正在初始化 Git 仓库..."
    git init
    git add .
    git commit -m "Initial commit"
    
    echo ""
    echo "请在浏览器中创建 GitHub 仓库："
    echo "https://github.com/new"
    echo ""
    echo "仓库名称建议：geo-monitor"
    echo "选择 Public（公开）"
    echo ""
    read -p "创建完成后按回车键继续..."
    
    echo ""
    read -p "请输入仓库地址（例如：https://github.com/$username/geo-monitor.git）: " repo_url
    
    git remote add origin $repo_url
    git branch -M main
    git push -u origin main
    
    echo ""
    echo "✅ GitHub 仓库创建完成！"
    echo "仓库地址：https://github.com/$username/geo-monitor"
    echo ""
    read -p "按回车键继续..."
    show_menu
}

deploy_vercel() {
    echo ""
    echo "🚀 Vercel 部署..."
    echo ""
    echo "请确保已经："
    echo "1. 在 https://github.com 注册账号"
    echo "2. 在 https://vercel.com 用 GitHub 登录"
    echo "3. 创建了 GitHub 仓库并上传了代码"
    echo ""
    read -p "按回车键继续..."
    
    echo ""
    echo "请访问 Vercel 并导入项目："
    echo "https://vercel.com/new"
    echo ""
    echo "步骤："
    echo "1. 点击 \"Import Git Repository\""
    echo "2. 选择你的 geo-monitor 仓库"
    echo "3. Framework Preset 选择 \"Other\""
    echo "4. 点击 \"Deploy\""
    echo ""
    echo "部署完成后，你将得到一个网址，如："
    echo "https://geo-monitor-xxx.vercel.app"
    echo ""
    read -p "按回车键继续..."
    show_menu
}

deploy_github_pages() {
    echo ""
    echo "📄 GitHub Pages 部署..."
    echo ""
    echo "步骤："
    echo "1. 访问 https://github.com/new 创建仓库"
    echo "2. Repository name: geo-monitor"
    echo "3. 选择 Public（公开）"
    echo "4. 勾选 \"Add a README file\""
    echo "5. 点击 \"Create repository\""
    echo ""
    echo "然后："
    echo "1. 点击 \"Add file\" → \"Upload files\""
    echo "2. 拖拽上传 index.html 文件"
    echo "3. 点击 \"Commit changes\""
    echo "4. 进入 Settings → Pages"
    echo "5. Source 选择 \"Deploy from a branch\""
    echo "6. Branch 选择 \"main\"，文件夹选择 \"/ (root)\""
    echo "7. 点击 \"Save\""
    echo ""
    echo "等待 2-5 分钟后访问："
    echo "https://你的用户名.github.io/geo-monitor"
    echo ""
    read -p "按回车键继续..."
    show_menu
}

# 启动菜单
show_menu
