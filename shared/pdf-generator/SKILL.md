---
name: totallink-pdf-generator
slug: totallink-pdf
description:
  TotalLINK 文档输出公共 Skill：将 Markdown 排版为自包含 HTML，并用 Chrome headless
  自动渲染为 A4 PDF。支持项目方案 / 技术教程 / 商务报告三类版式自动判定、打印安全中文
  排版、重复内容检测（只报告不删除）。全流程自动执行，无需人工确认。被报销审核等场景
  化 Skill 引用。
metadata:
  workbuddy:
    note: "渲染依赖 Chrome/Chromium/Edge（自动探测）；PDF 校验可选依赖 pdfplumber（$TOTALLINK_PYTHON）"
---

# 文档输出 Skill（Markdown → HTML → PDF）

## 概述

两步自动流程：

```
报告.md ──[排版]──→ 自包含 HTML ──[Chrome headless]──→ 报告.pdf
```

与旧版（Pandoc + WeasyPrint）的区别：

- **排版层**由模型依据 `references/` 规范生成 HTML，排版质量远高于 Pandoc 机械转换；
- **渲染层**改用 Chrome headless —— WeasyPrint 依赖系统 glib/pango，本机不可用；
- **全流程自动**：不等待文档类型确认，不等待重复内容确认，直接产出 PDF。

## 前置条件

| 依赖 | 必需性 | 说明 |
|------|--------|------|
| Chrome / Chromium / Edge | **必需** | 脚本自动探测；可用 `CHROME_BIN` 指定路径 |
| 中文字体 | **必需** | PingFang SC / STHeiti / Microsoft YaHei（macOS/Windows 自带） |
| pdfplumber | 可选 | 在 `$TOTALLINK_PYTHON` 下，用于 PDF 生成后校验 |
| pandoc | 可选 | 仅「快速路径」使用，不在 PATH 时用绝对路径 |

> ⚠️ **不要走 WeasyPrint 路径。** 本机 default venv 缺 `libgobject-2.0-0`，
> `import weasyprint` 直接抛 `OSError`。渲染统一走 Chrome headless。

## 工作流

### 1. 读取原文（只读）

- 读取 Markdown 文件或文本；**源文件视为只读**，不得覆盖、移动、重命名、删除。
- 保留正文措辞、段落顺序、标题层级、列表顺序、代码、图片引用、公式、表格、引用、脚注、任务清单。
- 允许新增排版层元素：封面、目录、章节编号、页眉页脚、信息卡片、提示框、摘要区、文档元信息。
  新增元素不得冒充原文。

### 2. 自动判定文档类型（不询问）

按 `references/visual-design.md` 的线索自动判定，**不向用户询问、不阻塞流程**；
判定结果与依据写入交付说明。用户显式指定类型时以用户指定为准。

| 类型 | 版式方向 |
|------|----------|
| `project-proposal` | 稳重清晰、适合评审，标题页安静留白 |
| `technical-tutorial` | 层级强、代码友好、命令与输出可区分 |
| `business-report` | 正式克制、指标入表、结论突出无营销装饰 |

判定存疑时按 `business-report` 处理并标注。

### 3. 检测重复内容（只报告，不删除）

对 Markdown 文件运行重复检测：

```bash
python3 scripts/detect_duplicates.py 报告.md -o duplicate-report.json
```

- 检测归一化后完全相同的段落，以及较长段落的词汇近似重复；
- 记录段落序号、标题上下文、原文摘录、相似度；
- **生成 HTML 时保留全部内容**，不因重复而删减、合并、改写；
- 语义近似属启发式提示，不得当作确定重复；
- 模板化表格行（如「报销人 / 部门」）会报 exact 重复，属结构性重复，**正常，不要删**。

### 4. 生成自包含 HTML

输出单个 `.html` 文件，必须包含：

- UTF-8 `meta`；明确标题与元信息；语义化标题层级；
- 自动目录，目录项链接到正文锚点；
- `@page` 与 `@media print` 规则；A4 尺寸与页边距；
- 中文正文两端对齐、合适行距段距、中英混排；
- 表格 / 卡片 / 标题的 `break-inside: avoid` 分页保护，长表 `thead` 跨页重复；
- 代码、表格、图片、SVG、公式、引用的溢出保护；
- 无 JavaScript 也能阅读核心内容。

排版细则见 `references/print-css.md` 与 `references/visual-design.md`。
适度智能识别「项目目标」「实施步骤」「风险与对策」「关键结论」等结构并呈现为卡片或提示框；
识别不确定时用普通排版。**绝不改变原文措辞或顺序。**

### 5. 渲染 PDF（自动）

```bash
./scripts/render_pdf.sh 报告.html 报告.pdf
```

- 默认加 `--no-pdf-header-footer`，输出干净版面；
- 需要页码时加 `--with-header-footer`（页眉会含 `file://` URL 与日期）；
- 与运行中的 Chrome 冲突时，用 `CHROME_USER_DATA_DIR` 指定独立用户数据目录。

### 6. 校验

```bash
"$TOTALLINK_PYTHON" scripts/verify_pdf.py 报告.pdf \
  --expect "执行摘要" "结论" --max-pages 30
```

再按 `references/review-checklist.md` 自检。发现问题时**保留原文并在交付说明中列出**，
不要静默修改内容。

### 7. 交付

输出目录由调用方指定；未指定时使用 `outputs/<document-slug>/`：

```text
outputs/<document-slug>/
├── <document-slug>.html
├── <document-slug>.pdf
├── duplicate-report.json
└── render-notes.html      # 可选：渲染说明与待人工确认事项
```

交付说明中必须写明：判定的文档类型及依据、HTML 与 PDF 路径、重复检测结论、
Mermaid/SVG 处理状态、**页码缺失情况**、仍需人工检查的事项。

## 特殊元素处理

| 元素 | 处理方式 |
|------|----------|
| Mermaid | 优先转内嵌 SVG；无可用转换器时保留源码并标记待转换，**不得伪造图形** |
| Graphviz | 同上 |
| 图片 | 优先相对路径或 data URL；检查存在性与打印溢出；不硬编码本机绝对路径为唯一地址 |
| 代码块 | 保留语言标识，本地 CSS 高亮；不依赖远程高亮脚本 |
| 数学公式 | 优先已有 SVG/图片或可打印文本回退；不依赖在线 MathJax |
| 复杂表格 | 真实 `<table>`/`<thead>`/`<tbody>`，重复表头，避免横向溢出 |
| 引用 / 脚注 / 任务清单 | 保留来源关系、编号与完成状态 |

## 可选：Pandoc 快速路径

仅用于结构简单、无需精排的文档。**精排场景一律走第 4 步的模型排版路径。**

```bash
pandoc 报告.md -o 报告.html --embed-resources --standalone
./scripts/render_pdf.sh 报告.html 报告.pdf
```

**Pandoc 安全规则（防止解析异常）：**

| 规则 | 禁止 | 使用 |
|------|------|------|
| 任务列表 | `[X]` `[!]` `[OK]` | `X` `!` `OK`（不加方括号） |
| 星号转义 | `\*文本\*` | `*文本*`（表格内不要转义星号） |
| 表格前空行 | 表格紧接上文 | 表格前后必须有空行 |

## 已知限制

- **Chrome headless 不支持 `@page` 页码计数器**，输出的 PDF **无页码**。这是固有限制，
  不是缺陷；确需页码时由用户在 Chrome 打印对话框勾选「页眉和页脚」。
- Chrome 嵌入字体的 ToUnicode 会把「一/风/车」等映射为康熙部首码位（U+2E80~U+2FDF），
  pdfplumber 提取文本会得到「⼀/⻛」，校验前需 NFKC 归一化（`verify_pdf.py` 已内置）。
  **视觉渲染不受影响。**

## 默认禁止事项

- 不覆盖源 Markdown；不修改正文措辞；不改变原文顺序
- **不自动删除重复内容**（重复只报告）
- 不伪造 Mermaid / Graphviz 转换结果
- 不依赖远程字体、远程脚本或在线 CDN
- 不以装饰牺牲分页、表格、中文长文阅读与 PDF 可靠性
- 不把疑似语义重复当作确定重复

## 资源

- 重复检测：`scripts/detect_duplicates.py`
- HTML → PDF 渲染：`scripts/render_pdf.sh`
- PDF 内容校验：`scripts/verify_pdf.py`
- 打印 CSS：`references/print-css.md`
- 视觉方向：`references/visual-design.md`
- 交付前检查：`references/review-checklist.md`
