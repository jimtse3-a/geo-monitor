# GEO AI 搜索引擎监测工具 - 快速启动

## 🚀 一键部署脚本

### Windows 用户

双击运行：`deploy.bat`

或在命令行执行：
```cmd
deploy.bat
```

### Mac/Linux 用户

在终端执行：
```bash
chmod +x deploy.sh
./deploy.sh
```

---

## 📖 详细部署步骤

### 方案一：Vercel 部署（最简单，推荐）

**优点**：
- ✅ 完全免费
- ✅ 自动部署（代码推送到 GitHub 后自动更新）
- ✅ 自带 CDN，国内访问速度快
- ✅ 支持自定义域名
- ✅ HTTPS 自动配置

**步骤**：

1. **准备工作**
   - 注册 GitHub 账号：https://github.com
   - 注册 Vercel 账号：https://vercel.com（使用 GitHub 登录）

2. **创建 GitHub 仓库**
   ```bash
   # 在 geo-monitor 文件夹内执行
   git init
   git add .
   git commit -m "Initial commit"
   
   # 访问 https://github.com/new 创建仓库
   # 然后执行：
   git remote add origin https://github.com/你的用户名/geo-monitor.git
   git branch -M main
   git push -u origin main
   ```

3. **部署到 Vercel**
   - 登录 https://vercel.com
   - 点击 "Add New..." → "Project"
   - 选择你的 `geo-monitor` 仓库
   - Framework Preset 选择 "Other"
   - 点击 "Deploy"

4. **获取网址**
   - 等待 1-2 分钟
   - 你会得到类似 `https://geo-monitor-xxx.vercel.app` 的网址
   - 点击即可访问！

---

### 方案二：GitHub Pages 部署

**优点**：
- ✅ 完全免费
- ✅ 无需额外账号
- ✅ 与 GitHub 集成好

**步骤**：

1. **创建 GitHub 仓库**
   - 访问 https://github.com/new
   - Repository name: `geo-monitor`
   - 选择 "Public"
   - 勾选 "Add a README file"
   - 点击 "Create repository"

2. **上传文件**
   - 点击 "Add file" → "Upload files"
   - 拖拽上传 `index.html` 文件
   - 点击 "Commit changes"

3. **启用 GitHub Pages**
   - 进入仓库的 "Settings"
   - 左侧找到 "Pages"
   - Source 选择 "Deploy from a branch"
   - Branch 选择 "main"，文件夹选择 "/ (root)"
   - 点击 "Save"

4. **等待部署**
   - 等待 2-5 分钟
   - 访问：`https://你的用户名.github.io/geo-monitor`

---

## 📱 分享给他人使用

部署完成后，你可以：

### 1. 直接分享链接
```
https://你的网址.com
```

### 2. 生成二维码
访问 https://cli.im 输入网址生成二维码

### 3. 嵌入到其他网站
```html
<iframe src="https://你的网址.com" width="100%" height="800px"></iframe>
```

---

## 🔧 常见问题

**Q: 部署后打开是空白页？**
A: 确保 `index.html` 在仓库根目录，文件名正确。

**Q: 如何更新网站内容？**
A: 
- Vercel: 修改代码后推送到 GitHub，自动更新
- GitHub Pages: 在网页上修改文件，自动重新部署

**Q: 可以绑定自己的域名吗？**
A: 可以！
- Vercel: 项目设置 → Domains → 添加域名
- GitHub Pages: Settings → Pages → Custom domain

**Q: 免费版有什么限制？**
A: 
- Vercel: 每月 100GB 流量（完全够用）
- GitHub Pages: 每月 100GB 流量，1GB 存储

---

## 🎯 使用演示

部署完成后，你可以：

1. **输入任意品牌名称**
   - 例如：特斯拉、Apple、星巴克、小米

2. **选择监测平台**
   - 勾选 DeepSeek、Kimi、豆包等 AI 平台

3. **自定义关键词**
   - 输入与品牌相关的关键词
   - 例如：电动汽车、手机、咖啡

4. **开始监测**
   - 点击"开始监测"按钮
   - 查看 AI Brand Score 和各项指标

5. **分享结果**
   - 截图分享给朋友
   - 或让对方直接访问你的网址

---

## 💡 提示

- 当前是**演示版本**，数据为模拟生成
- 如需真实监测，需要接入真实 AI API（DeepSeek、Kimi 等）
- 所有代码都是开源的，可以自由修改

祝部署顺利！🎉
