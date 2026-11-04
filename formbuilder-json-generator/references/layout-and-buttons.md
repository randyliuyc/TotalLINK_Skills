# 布局规则与按钮配置详解

## 一、布局规则

### totalColspan（总列数）

顶层 `json.totalColspan` 是字符串，决定一行最多放几个"列单元"。常见值：`"1"`、`"2"`、`"3"`、`"4"`、`"6"`、`"8"`。

### row 行类型

`row` 是布局行数组，每行元素有两种 `type`：

#### 1. `line`（普通行）

`col` 数组内每个控件通过 `colspan` 声明占几列，所有 `colspan` 之和 ≤ `totalColspan`。

```json
{
  "hidden": false,
  "upload": false,
  "type": "line",
  "title": "基本信息",
  "col": [
    { "type": "input", "colspan": 1, "title": "姓名", "role": true, "value": "name" },
    { "type": "radio", "colspan": 1, "title": "性别", "role": true, "value": "sex",
      "data": [{ "text": "男", "value": "man", "role": true }, { "text": "女", "value": "woman", "role": true }] }
  ]
}
```

**关键约定**：每个字段**只需一个 `col`**，用 `col.title` 显示标题（引擎通过 `el-form-item` 的 `label` 渲染），`col.type` 是控件类型。**不要**额外生成 `type:"text"` + `style:"th"` 的标签列，否则标题会重复。`totalColspan: "4"` 时，上面示例一行放 2 个字段（每个字段占 1 列，共 2 列）。

#### 2. `table`（表格行）

多行数据录入，`column` 定义表格列，`data` 指向 `tableData` 的 key。

```json
{
  "hidden": false,
  "upload": false,
  "type": "table",
  "column": [
    { "text": "姓名", "value": "name", "role": true, "type": "input" },
    { "text": "性别", "value": "sex", "role": true, "type": "select",
      "data": [{ "text": "男", "value": "man", "role": true }] }
  ],
  "data": "TABLE_1",
  "oldData": "TABLE_1"
}
```

`tableData` 中需初始化对应的空数组：

```json
"tableData": { "TABLE_1": [{}, {}] }
```

### 布局常见模式

| totalColspan | 典型用法 |
|--------------|---------|
| `"1"` | 单列纵向表单 |
| `"2"` | 每行 1~2 个字段 |
| `"4"` | 每行 2 个字段（标签+控件各占1列 × 2 组） |
| `"6"` | 每行 3 个字段 |
| `"8"` | 每行 4 个字段 |

## 二、按钮配置（btns）

### 按钮类型（buttonType 枚举）

| value | 说明 |
|-------|------|
| `btn` | 普通按钮 |
| `button` | 按钮（兼容 button） |
| `input` | 文本输入框 |
| `upload` | 上传控件 |
| `href` | 超链接 |
| `import` | 导入 excel/csv |
| `text` | 文本框 |
| `dropdown` | 下拉菜单 |

### 按钮通用字段

```json
{
  "value": "save",           // 绑定字段/动作标识
  "type": "btn",             // 按钮类型
  "text": "保存",            // 按钮内容
  "color": "primary",        // 按钮颜色
  "background": "#409EFF",   // 自定背景色
  "fontColor": "#fff",       // 字体颜色
  "icon": "el-icon-check",   // 按钮图标（el-icon-*）
  "fontStyle": "Microsoft YaHei",
  "fontSize": "14px",
  "circle": false,           // 圆形
  "round": false,            // 圆角
  "plain": false,            // 简洁
  "btnSize": "medium",       // 尺寸
  "width": "", "minWidth": "", "height": "",
  "hiddenCol": "",           // 隐藏配置
  "disabled": false,         // 禁用配置
  "url": "",                 // href 类型链接地址（支持 {表达式}）
  "target": "_blank"         // href 打开模式
}
```

按钮颜色枚举（colors）：`primary`（蓝）、`default`（白）、`success`（绿）、`info`（灰）、`warning`（橙）、`danger`（红）、`text`（透明/文字按钮）。

### 按钮动作配置（调用后端模型）

按钮的核心是触发后端模型调用，关键字段：

```json
{
  "code": "模型代码",
  "num": "模型编号",
  "para": "模型参数",
  "script": 3,              // 脚本类型，默认 3
  "deleteCode": "",          // 删除功能模型代码
  "deleteNum": "",
  "deletePara": "",
  "deleteScript": ""
}
```

- `para`（模型参数）可选值：`formData`（主表）、或 `tableData` 中的表格名（子表）。
- 按钮支持多个 `action` 动作串行/并行执行，每个 action 含 `code`/`num`/`para`/`script`。

### 上传按钮（type:"upload"）专用字段

```json
{
  "type": "upload",
  "drag": false,             // 拖拽上传
  "limit": 0,                // 文件数量限制，0 不限
  "accept": "*",             // 文件类型
  "code": "", "num": "", "script": 3, "para": "formData",
  "compress": 0,             // 图片压缩（MB）
  "orderPara": ""            // 排序参数
}
```

### 按钮配置示例

```json
{
  "type": "button",
  "colspan": 2,
  "btns": [
    { "type": "btn", "value": "save", "text": "保存", "color": "primary",
      "code": "DM_SAVE", "num": "1", "para": "formData", "script": 3 },
    { "type": "btn", "value": "back", "text": "返回", "color": "default" }
  ]
}
```

## 三、完整表单示例

4 列布局的员工信息表单（对应 `src/views/json/4X4.json` 结构）：

```json
{
  "formData": {},
  "tableData": { "TABLE_1": [{}] },
  "row": [
    {
      "hidden": false, "upload": false, "type": "line", "title": "基本信息",
      "col": [
        { "type": "input", "colspan": 1, "title": "姓名", "role": true, "value": "name" },
        { "type": "radio", "colspan": 1, "title": "性别", "role": true, "value": "sex",
          "data": [{ "text": "男", "value": "man", "role": true }, { "text": "女", "value": "woman", "role": true }] }
      ]
    },
    {
      "hidden": false, "upload": false, "type": "line", "title": "工作信息",
      "col": [
        { "type": "select-search", "colspan": 1, "title": "部门", "role": true, "value": "dept",
          "data": [
            { "text": "研发", "value": "dev", "role": true },
            { "text": "市场", "value": "market", "role": true }
          ] },
        { "type": "date", "colspan": 1, "title": "入职日期", "role": true, "value": "date", "dateType": "date" }
      ]
    },
    {
      "hidden": false, "upload": false, "type": "table",
      "column": [
        { "text": "姓名", "value": "name", "role": true, "type": "input" },
        { "text": "年龄", "value": "age", "role": true, "type": "number" }
      ],
      "data": "TABLE_1", "oldData": "TABLE_1"
    }
  ],
  "btns": [],
  "status": {},
  "navMenu": [],
  "init": [],
  "selectData": {},
  "totalColspan": "4",
  "loyout": "collapse",
  "tops": true
}
```
