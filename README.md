# DeepPresenter PPT 工作流

> 基于 DeepPresenter 的本地 PPT 制作自动化工作流，支持知识库接入和分层可编辑输出

---

## 特性

- **DeepPresenter 驱动**：使用 DeepPresenter AI 完成设计 + 排版 + 图片生成
- **知识库接入**：支持 Markdown / TXT / PDF 文档作为输入源
- **分层可编辑**：最终 PPT 文字/图片/背景完全分离，可自由修改
- **完全本地运行**：敏感内容不外泄
- **Session 隔离**：子会话执行避免进程中断

---

## 快速开始

### 1. 安装依赖

```bash
# Python 依赖
pip install -r requirements.txt
playwright install chromium

# Node.js（用于 html2pptx）
npm install -g html2pptx

# DeepPresenter
pip install deeppresenter
```

### 2. 配置 API

复制配置文件并填入你的 API Key：

```bash
cp config.yaml.example config.yaml
```

编辑 `config.yaml`：
- `text_api.key` - 文本生成 API Key
- `image_api.key` - 图片生成 API Key

或设置环境变量：
```bash
export TEXT_API_KEY="your-key"
export IMAGE_API_KEY="your-key"
```

### 3. 准备知识库

将 Markdown / TXT 文件放入 `input/` 目录：

```
input/
├── 文档1.md
├── 文档2.md
└── 产品介绍.txt
```

### 4. 一键运行

```bash
chmod +x run_pipeline.sh
./run_pipeline.sh
```

---

## 系统架构

```
知识库文档 (Markdown/TXT/PDF)
         ↓
    ┌─────────────────────────┐
    │  analyze_content.py      │
    │  读取知识库 → AI 生成大纲  │
    └────────────┬────────────┘
         ↓       ↓
    ┌─────────────────────────┐
    │  generate_html.py       │
    │  大纲 → HTML 设计稿       │
    └────────────┬────────────┘
         ↓       ↓
    ┌─────────────────────────┐
    │  Playwright 截图         │
    │  分层截图（背景/文字）     │
    └────────────┬────────────┘
         ↓       ↓
    ┌─────────────────────────┐
    │  assemble_layered.py    │
    │  python-pptx 组装        │
    └────────────┬────────────┘
         ↓
    分层可编辑 PPTX
```

---

## 核心脚本

### analyze_content.py

读取知识库文档，调用 AI 生成 PPT 大纲

```bash
python3 scripts/analyze_content.py \
    --input input/ \
    --output output/outline.md \
    --api "https://api.openai.com/v1/chat/completions" \
    --key "your-api-key"
```

### generate_html.py

根据大纲生成带 CSS 样式的 HTML 文件

```bash
python3 scripts/generate_html.py \
    --outline output/outline.md \
    --output slides/
```

### screenshot_layers.py

使用 Playwright 对 HTML 页面进行分层截图

```bash
python3 scripts/screenshot_layers.py \
    --slides slides/ \
    --output screenshots/
```

### assemble_layered.py

将分层截图组装为可编辑的 PPTX

```bash
python3 scripts/assemble_layered.py \
    --screenshots screenshots/ \
    --slides slides/ \
    --output output/layered.pptx
```

---

## 目录结构

```
.
├── README.md
├── config.yaml.example     # 配置文件示例
├── requirements.txt         # Python 依赖
├── run_pipeline.sh          # 一键运行脚本
├── scripts/
│   ├── analyze_content.py   # 知识库 → 大纲
│   ├── generate_html.py     # 大纲 → HTML 设计稿
│   ├── screenshot_layers.py # Playwright 分层截图
│   └── assemble_layered.py  # 组装分层 PPTX
├── input/                   # 知识库文档（自备）
├── slides/                  # HTML 设计稿（自动生成）
├── screenshots/             # 分层截图（自动生成）
└── output/                  # 输出目录
    ├── outline.md          # 生成的大纲
    ├── final.pptx         # 标准 PPTX
    └── layered.pptx        # 分层可编辑 PPTX
```

---

## 分层 PPTX 说明

| 层级 | 内容 | 可编辑性 |
|------|------|----------|
| 背景层 | 背景图/渐变 | 需重新截图修改 |
| 图表层 | 产品图/数据图 | 需重新截图修改 |
| 文字层 | 标题/正文 | **可直接编辑** |

分层 PPTX 适合需要交付给客户并进行修改的场景。

---

## 图片生成配置

支持多种图片生成服务：

| 服务 | 模型 | 端点示例 |
|------|------|----------|
| OpenAI | DALL-E / GPT-Image | api.openai.com |
| 豆包 | doubao-seedream | ark.cn-beijing.volces.com |
| 通义万相 | wanx-v1 | dashscope.aliyuncs.com |
| DeepSeek | - | api.deepseek.com |

---

## FAQ

**Q: 必须用 DeepPresenter 吗？**
A: DeepPresenter 提供最佳 AI 设计质量，也可替换为其他设计工具。

**Q: 图片生成 API 必须配置吗？**
A: 不配置也可以运行，使用默认背景。

**Q: 分层 PPTX 和标准 PPTX 区别？**
A: 分层版 - 文字图片分离可编辑，适合客户交付；标准版 - 体积小生成快。

**Q: 如何自定义样式？**
A: 修改 `generate_html.py` 中的 `SLIDE_TEMPLATE` HTML 模板。

---

## License

MIT License
