# 弱弱投资日记 | Ruoruo Investment Diary

每日A股市场分析、投资策略与财经观察

🔗 **GitHub Pages**: https://vidbun-chu.github.io/ruoruo-blog/

## 📖 简介

「弱弱投资日记」是一个自动化投资分析博客，通过 Python 脚本每日抓取 A 股市场数据并生成结构化的分析文章。

### ✨ 特色功能

- 📊 **数据驱动** - 基于腾讯行情 API 的实时市场数据
- 🤖 **自动更新** - Python 脚本每日自动生成分析文章
- 🌙 **暗色主题** - 专业的金融终端风格设计
- 📱 **响应式设计** - 完美适配桌面端和移动端
- 🔍 **SEO 优化** - 支持 RSS 订阅，优化搜索引擎收录
- 💰 **赞赏支持** - 内置赞赏码展示功能

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/vidbun-chu/ruoruo-blog.git
cd ruoruo-blog
```

### 2. 生成今日文章

```bash
python3 generate_article.py
```

### 3. 本地预览

```bash
# 使用 Python 内置 HTTP 服务器
python3 -m http.server 8000

# 访问 http://localhost:8000
```

### 4. 部署到 GitHub Pages

```bash
git add .
git commit -m "Update daily article"
git push origin main
```

访问 https://vidbun-chu.github.io/ruoruo-blog/ 查看效果。

## 📁 项目结构

```
ruoruo-blog/
├── index.html          # 主页面
├── style.css           # 样式表
├── script.js           # JavaScript
├── generate_article.py # 文章生成脚本
├── feed.xml            # RSS 订阅源
├── .nojekyll           # 跳过 Jekyll 构建
├── README.md           # 项目说明
└── articles/           # 生成的文章目录
    ├── index.json      # 文章索引
    └── YYYY-MM-DD.html # 每日文章
```

## 🔧 自动化配置

### 使用 GitHub Actions 自动更新

创建 `.github/workflows/daily-article.yml`:

```yaml
name: Generate Daily Article

on:
  schedule:
    - cron: '0 16 * * 1-5'  # 工作日 UTC 16:00 (北京时间 00:00)
  workflow_dispatch:

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Generate article
        run: python3 generate_article.py
      
      - name: Commit and push
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add .
          git commit -m "Auto-generate daily article $(date +%Y-%m-%d)" || exit 0
          git push
```

## 📊 数据来源

- **行情数据**: 腾讯财经 API (qt.gtimg.cn)
- **主要指数**: 上证指数、深证成指、创业板指、沪深300、上证50
- **重点个股**: 贵州茅台、中国平安、五粮液、宁德时代、招商银行

## ⚠️ 免责声明

- 本站所有内容均由程序自动生成
- 内容仅供学习交流，不构成任何投资建议
- 投资有风险，入市需谨慎
- 历史数据不代表未来表现

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📮 联系方式

- GitHub: [@vidbun-chu](https://github.com/vidbun-chu)
- 博客: https://vidbun-chu.github.io/ruoruo-blog/

---

**弱弱投资日记** © 2024-2026
