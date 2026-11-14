# 打印 CSS 参考

自包含打印样式表。屏幕预览与打印预览保持一致。

## 基础模板

```css
:root {
  --page-margin-top: 18mm;
  --page-margin-right: 17mm;
  --page-margin-bottom: 20mm;
  --page-margin-left: 20mm;
  --body-font: -apple-system, BlinkMacSystemFont, "PingFang SC",
               "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  --mono-font: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
}

@page {
  size: A4;
  margin: var(--page-margin-top) var(--page-margin-right)
          var(--page-margin-bottom) var(--page-margin-left);
}

body {
  font-family: var(--body-font);
  font-size: 11pt;
  line-height: 1.75;
  color: #222;
  /* 中文长文两端对齐；标题与短标签保持左对齐 */
  text-align: justify;
  text-justify: inter-ideograph;
}

h1, h2, h3, h4, th, .label, .metric-value { text-align: left; }

@media print {
  .screen-only { display: none !important; }
  .print-break-before { break-before: page; page-break-before: always; }
  h1, h2, h3, h4 { break-after: avoid; page-break-after: avoid; }
  table, figure, .callout, .summary-card {
    break-inside: avoid; page-break-inside: avoid;
  }
  thead { display: table-header-group; }   /* 长表跨页重复表头 */
  tr { break-inside: avoid; }
  a { color: inherit; text-decoration: none; }
}
```

## 实施要点

- 自定义属性按文档所选视觉方向替换数值，不要保留占位值。
- 页面尺寸与边距用 `@page`；仅打印生效的行为放 `@media print`。
- **避免** CSS Grid、脆弱的绝对定位、依赖 hover 或 JavaScript 的布局 —— 这些在 headless 打印中不可靠。
- 长表格、宽代码块、SVG、图片、跨页标题都必须实机验证，不能凭经验假定。

## Chrome headless 渲染约束（实测）

本项目 PDF 渲染走 Chrome headless，以下限制是实测结论，不要试图绕过：

| 约束 | 说明 | 处理方式 |
|------|------|----------|
| **`@page` 页码计数器不支持** | Chrome 不实现 `counter(page)` / `content: counter(page)`，headless 输出的 PDF **没有页码** | 接受该限制并在交付说明中标注；确需页码时由用户在 Chrome 打印对话框勾选「页眉和页脚」 |
| **默认页眉页脚** | 不加 `--no-pdf-header-footer` 时，Chrome 会自行加上含标题、`file://` URL、日期的页眉页脚 | 默认加该参数，保持版面干净 |
| **本地字体依赖** | 只使用系统已安装字体，禁止远程字体 / CDN | 使用上面的本地字体回退链 |
| **`file://` 加载** | headless 直接读本地 HTML，相对路径资源可正常加载；绝对本机路径不可移植 | 图片优先相对路径或 data URL |

> 嵌入字体的 ToUnicode 会把「一/风/车」等汉字映射到康熙部首码位（U+2E80~U+2FDF），
> 用 pdfplumber 提取文本校验时会得到「⼀/⻛」。校验前需先做 **NFKC 归一化**，
> 否则会误判为内容缺失。**视觉渲染不受影响**，不必因此调整排版。
