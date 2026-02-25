# GEO AI 搜索引擎监测工具

🔍 **监测品牌在 AI 平台的可见率与关键词录用情况**

这是一个用于监测品牌在 AI 搜索引擎（如 Kimi、豆包、DeepSeek 等）中可见性的工具。支持多平台、多品牌、多关键词监测。

## ✨ 功能特点

- **多平台支持**：支持 7 大 AI 平台（Kimi、豆包、千问、DeepSeek、文心一言、腾讯混元、智谱）
- **多品牌监测**：同时监测多个品牌的 AI 可见率
- **关键词录用率**：分析不同关键词在 AI 平台中的表现
- **可视化报告**：生成 HTML 格式的可视化监测报告
- **演示模式**：无需 API 密钥，使用模拟数据进行演示

## 🚀 快速开始

### 1. 启动交互式仪表盘

直接在浏览器中打开 `index.html` 文件：

```bash
# Windows
start index.html

# Mac
open index.html

# Linux
xdg-open index.html
```

这将打开一个交互式的 WEB 界面，你可以：
- 选择要监测的企业/品牌
- 选择 AI 平台
- 输入关键词
- 查看实时图表和数据
- 导出监测报告

### 2. 命令行使用

#### 运行完整监测

```bash
python monitor.py
```

#### 生成演示数据

```bash
# 生成过去 7 天的演示数据
python monitor.py --demo

# 生成指定天数的演示数据
python monitor.py --demo --days 30
```

#### 指定平台和品牌

```bash
# 只监测 Kimi 和豆包平台
python monitor.py --platforms kimi doubao

# 只监测星巴克品牌
python monitor.py --brands 星巴克

# 组合使用
python monitor.py --platforms kimi doubao deepseek --brands 印暨咖啡 瑞幸咖啡
```

#### 自定义关键词

```bash
python monitor.py --keywords "精品咖啡" "办公室咖啡" "咖啡外卖"
```

#### 生成报告

```bash
# 根据已有数据生成报告
python monitor.py --report
```

## 📊 监测指标

### 1. 可见率（Visibility Rate）
品牌被 AI 平台提及的次数占总查询次数的百分比

### 2. 排名（Rank）
品牌在 AI 回复中的推荐位置（第 1/2/3 名）

### 3. 置信度（Confidence）
AI 对品牌信息的确定程度（0-100%）

### 4. 关键词录用率
特定关键词在 AI 平台中被成功提及的比例

## 🏢 预设品牌

- **印暨咖啡** - 精品咖啡品牌
- **瑞幸咖啡** - 连锁平价咖啡
- **星巴克** - 国际连锁咖啡
- **喜茶** - 新式茶饮
- **奈雪的茶** - 烘焙茶饮

## 🔧 支持的 AI 平台

| 平台 | ID | 特点 |
|------|-----|------|
| DeepSeek | deepseek | 深度思考型 |
| Kimi | kimi | 理性分析型 |
| 豆包 | doubao | 亲和推荐型 |
| 千问 | qianwen | 专业详细型 |
| 文心一言 | wenxin | 传统稳重型 |
| 腾讯混元 | hunyuan | 社交导向型 |
| 智谱 | zhipu | 技术驱动型 |

## 📁 文件说明

```
geo-monitor/
├── index.html          # 交互式 WEB 仪表盘
├── monitor.py          # 核心监测脚本
├── monitor.db          # SQLite 数据库
├── report_*.html       # 生成的监测报告
├── .env                # 环境变量配置（API 密钥）
└── README.md           # 本文件
```

## 🎮 演示模式

默认情况下，工具使用**模拟数据**进行演示。每个平台对不同品牌有不同的"偏好度"：

- **DeepSeek** 更倾向于提及：印暨咖啡、星巴克
- **Kimi** 更倾向于提及：星巴克、瑞幸咖啡
- **豆包** 更倾向于提及：喜茶、奈雪的茶
- **腾讯混元** 更倾向于提及：喜茶、奈雪的茶

这模拟了真实世界中不同 AI 平台的推荐倾向差异。

## 🔌 接入真实 API

要接入真实的 AI 平台 API，需要：

1. 在 `.env` 文件中添加 API 密钥：

```env
DEEPSEEK_API_KEY=your_deepseek_key
KIMI_API_KEY=your_kimi_key
DOUBAO_API_KEY=your_doubao_key
# ... 其他平台
```

2. 修改 `monitor.py` 中的 `MockAIClient` 类，替换为真实 API 调用

3. 示例代码：

```python
import openai

class RealAIClient:
    @classmethod
    def query(cls, platform, keyword, brand):
        client = openai.OpenAI(
            api_key=os.getenv(f"{platform.upper()}_API_KEY"),
            base_url=f"https://api.{platform}.com"
        )
        
        response = client.chat.completions.create(
            model="default",
            messages=[{
                "role": "user",
                "content": f"{keyword}，推荐几家并给出理由"
            }]
        )
        
        # 解析响应，判断是否提及品牌
        content = response.choices[0].message.content
        is_mentioned = brand in content
        
        return {
            "platform": platform,
            "keyword": keyword,
            "brand": brand,
            "is_mentioned": is_mentioned,
            # ... 其他字段
        }
```

## 📈 查看报告

监测完成后，会生成 HTML 格式的报告文件：`report_YYYYMMDD_HHMMSS.html`

用浏览器打开即可查看：
- 总体可见率统计
- 各平台表现对比
- 详细监测记录
- 品牌竞争力分析

## 💡 使用建议

1. **定期监测**：建议每周运行一次，追踪可见率变化趋势
2. **关键词优化**：根据录用率调整监测关键词
3. **平台差异化**：不同平台的用户群体不同，针对性优化
4. **竞品对比**：同时监测竞品品牌，了解竞争格局

## 🛠️ 技术栈

- **Python 3.7+**
- **SQLite** - 数据存储
- **Chart.js** - 可视化图表
- **HTML/CSS/JavaScript** - 交互界面

## 📝 License

MIT License - 自由使用和修改

## 🤝 贡献

欢迎提交 Issue 和 PR！

---

**提示**：这是一个演示版本，使用模拟数据。接入真实 API 后即可用于生产环境。
