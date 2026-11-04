---
name: formbuilder-json-generator
description: 根据用户的自然语言描述，生成符合 formbuilder 表单引擎规则的表单 JSON。当用户描述"做一个表单""生成表单配置""XX录入/审批/查询表单""含哪些字段的表单"等需求时使用。该技能理解 formbuilder 引擎的布局规则（row/col/totalColspan）、全部控件类型（input、select、radio、checkbox、date、table、cascader、tabs 等）、以及按钮配置（btns），并输出可直接被引擎解析的 JSON。
---

# Formbuilder 表单 JSON 生成器

## 概述

根据用户对表单的自然语言描述，生成 formbuilder 引擎可直接解析的表单 JSON。输出的是引擎的 `json` 对象本身（不含 `id`、`text` 等最外层包裹字段），包含 `formData`（表单数据）、`tableData`（表格数据）、`row`（布局行数组）、`btns`（按钮）等字段。

## 工作流程

1. **解析需求**：从用户描述中提取字段（字段名、类型、是否必填、默认值、选项、布局列数等）。
2. **确定布局**：根据字段数量和用户意图，确定 `totalColspan`（总列数）和每行的 `colspan` 分配。
3. **生成 row 数组**：按布局规则组装 `line`（普通行）或 `table`（表格行）。
4. **组装顶层 JSON**：填充 `formData`、`tableData`、`btns`、`item`、`init` 等字段。
5. **自检**：按"校验清单"核对字段完整性。

## 输出格式

**直接输出 `json` 对象本身，不要外层包裹。** 即不要 `id`、`text` 等最外层字段，也不要用 `{ "json": {...} }` 包裹，输出内容就是表单引擎要解析的 `json` 对象：

```json
{
  "formData": {},        // 表单字段值（key 为字段 value，value 为初始值）
  "tableData": {},       // 表格数据（key 为表格标识，value 为行对象数组）
  "row": [],             // 布局行数组（核心）
  "btns": [],            // 顶部/底部操作按钮
  "status": {},          // 流程状态配置
  "navMenu": [],         // 顶部导航条（锚点导航，每项含 id/text，关联 row 的 id）
  "init": [],            // 初始化脚本
  "selectData": {},      // 下拉数据源（key 为标识，value 为选项数组）
  "totalColspan": "4",   // 总列数（字符串，决定一行放几个控件）
  "loyout": "collapse",  // 布局模式（默认折叠表单布局）
  "tops": true           // 按钮布局（默认顶部布局）
}
```

> 注意：
> - `totalColspan` 是**字符串**，例如 `"4"` 表示 4 列布局。
> - **输出只含上述 `json` 对象本身，不包含 `id`、`text` 等最外层字段。**
> - **顶层字段必须完整**：`formData`、`tableData`、`row`、`btns`、`status`、`navMenu`、`init`、`selectData`、`totalColspan`、`loyout`、`tops` 都要输出，不能遗漏。**尤其 `status` 字段（`{}`）绝不能缺失**，否则引擎渲染时访问 `jsonData.status.open` 会报 `Cannot read properties of undefined (reading 'open')` 错误。

## 布局模式（loyout / collapse）

`json.loyout` 字段控制整体布局模式，取值：

| loyout 值 | 布局模式 | 说明 |
|-----------|---------|------|
| `"collapse"` | **折叠表单布局（默认）** | 以折叠面板（el-collapse）形式展示，每行一个可折叠面板 |
| `"tabs"` | 标签页布局 | 以标签页形式分组展示 |
| `"drag"` | 拖拽布局 | 可拖拽排序的卡片布局 |
| `""`（空/不设置） | 普通表格布局 | 非折叠的平铺表格布局 |

`json.collapse` 是布尔字段，为 `true` 时同样触发折叠布局（引擎判断条件 `jsonData.collapse || jsonData.loyout=='collapse'`）。

> **默认规则（重要）**：当用户**没有明确说明布局模式**时，默认采用**折叠表单布局**，即设置 `"loyout": "collapse"`。仅当用户明确要求"标签页布局"、"拖拽布局"或"普通表格布局（不折叠）"时，才相应调整 `loyout` 值。

> **折叠布局的 row 标题**：折叠布局下，每个 `row` 元素必须带 `title`（作为折叠面板的标题栏显示），除非用户明确说明不需要标题。

## 顶部导航条（navMenu）

顶部导航条用 `json.navMenu` 数组（**不是 `item`**），每项含 `id` 和 `text`，通过 `id` 关联对应 `row` 元素的 `id`（滚动锚点）：

```json
{
  "navMenu": [
    { "id": 1, "text": "表头信息" },
    { "id": 2, "text": "订单明细" },
    { "id": 3, "text": "附件列表" }
  ]
}
```

被导航的 `row` 元素需要有对应的 `id` 字段（与 `navMenu` 项的 `id` 一致）：

```json
{ "id": 1, "type": "line", "title": "表头信息", "col": [...] }
```

> 相关可选配置：`navMenuBg`（导航背景色）、`navMenuColor`（文字颜色）、`navMenuActColor`（激活色）、`navMenuTop`（固定偏移）。

## 布局规则（row 数组）

`row` 数组的每个元素是一个布局行，有两种 `type`：

### 1. `line` 类型（普通行）

一行内通过 `col` 数组放置多个控件，每个控件用 `colspan` 占列。`colspan` 之和应等于 `totalColspan`。

```json
{
  "hidden": false,
  "upload": false,
  "type": "line",
  "title": "基本信息",
  "col": [
    { "type": "input", "colspan": 1, "title": "姓名", "role": true, "value": "name" },
    { "type": "date", "colspan": 1, "title": "入职日期", "role": true, "value": "joinDate", "dateType": "date" }
  ]
}
```

**字段写法（重要）**：每个字段**只需一个 `col`**，通过 `col.title` 显示标题（引擎用 `el-form-item` 的 `label` 渲染 `col.title`），`col.type` 是控件类型，`col.value` 是字段名。**不要**再额外生成一个 `type: "text"` + `style: "th"` 的标签列，否则标题会重复。

> `style: "th"` 仅用于「整格作为纯标题格」的场景（如分组标题行、纯展示的栏目头），不是字段标签的写法。字段标签用 `col.title` 即可。

### 2. `table` 类型（表格行）

用于多行数据录入，用 `column` 定义表格列，`data` 指向 `tableData` 的 key。

```json
{
  "hidden": false,
  "upload": false,
  "type": "table",
  "column": [
    { "text": "姓名", "value": "name", "role": true, "type": "input" },
    { "text": "性别", "value": "sex", "role": true, "type": "select", "data": [{ "text": "男", "value": "man", "role": true }] }
  ],
  "data": "TABLE_1",
  "oldData": "TABLE_1"
}
```

**表格列宽度规则**：不要给每一列都设置 `width`。应该**留一列不设 `width`**（通常是内容较长、可伸缩的列，如"产品名称"），让它自适应铺满屏幕；其余列可设 `width`。仅当用户明确指定了列宽时才逐列设置。

```json
"column": [
  { "text": "产品编码", "value": "productCode", "role": true, "type": "input", "width": "120" },
  { "text": "产品名称", "value": "productName", "role": true, "type": "input" },   // 不设 width，自适应铺满
  { "text": "销售数量", "value": "saleQty", "role": true, "type": "number", "width": "100" }
]
```

## 控件类型速查

所有控件的 `type` 值与对应组件：

| type | 说明 | 关键字段 |
|------|------|---------|
| `text` | 纯文本展示 | `value`、`text`（显示内容）；`style:"th"` 时作为整格标题格 |
| `input` | 文本输入框 | `value`、`placeholder` |
| `number` | 数字计数器 | `min`、`max`、`step`、`stepStrictly`、`dataType` |
| `numberKey` | 数字键盘 | `value` |
| `select` | 下拉选择 | `data`（选项数组）、`dataText`、`dataValue`、`multiple` |
| `select-search` | 可搜索下拉 | `data`、`dataText`、`dataValue` |
| `autoinput` | 带输入建议 | `data`、`oriData`、`dataKey` |
| `radio` | 单选 | `data`（选项数组） |
| `checkbox` | 多选 | `data`（选项数组）、`border` |
| `date` | 日期 | `value`、`format` |
| `time` | 时间 | `value` |
| `timeSelect` | 时间段选择 | `value` |
| `cascader` | 级联选择 | `data`（树形）、`multiple`、`checkStrictly`、`lazy` |
| `switch` | 开关 | `value` |
| `slider` | 滑块 | `value` |
| `rate` | 评分 | `value` |
| `colorPicker` | 颜色选择 | `value` |
| `image` | 图片 | `value`、`btns` |
| `tag` | 标签 | `color`、`bg`、`size`、`theme` |
| `href` | 超链接 | `data`、`url` |
| `h1` | 标题 | `value`、`text` |
| `dropdown` | 下拉菜单 | `btns` |
| `carousel` | 走马灯 | `data` |
| `progress` | 进度条 | `value` |
| `card` | 自定义卡片 | `value` |
| `lineid` | 自增序号 | `value`、`indexFormat` |
| `button` / `btn` | 自定义按钮 | `btns`（按钮配置数组） |
| `iframe` | 网页嵌套 | `url`、`height`、`query` |
| `bgImage` | 背景图 | `value` |
| `treeData` | 树形数据 | `data`、`value` |
| `tinymce` | 富文本 | `value` |
| `selection` | 选择框（表格勾选） | `colType:"selection"` |
| `expand` | 折叠行 | `colType:"expand"`、`templateType`、`rowTemplate` |

> 详细字段说明见 `references/control-types.md`。

## 通用字段（col 对象）

每个 `col` 控件对象常见的通用字段：

- `type`：控件类型（必填）
- `value`：字段名/绑定值（必填，作为 formData 的 key）
- `title`：字段标题（`line` 行内显示在控件左侧/上方）；`text`：纯文本控件的显示内容或表格列名
- `colspan`：占列数（`line` 行内使用）
- `role`：是否可编辑（`true`）
- `style`：`"th"` 表示整格作为纯标题格（仅用于分组标题/纯展示栏，不是字段标签写法）
- `labelHidden`：是否隐藏字段标题
- `required`：是否必填
- `placeholder`：输入提示
- `hidden`：是否隐藏
- `data`：静态选项数组（格式 `[{ text, value, role: true }]`）
- `dataText` / `dataValue`：选项的显示字段/值字段（默认 `text`/`value`）
- `multiple`：是否多选
- `width` / `minWidth`：列宽（表格列**不要每列都设 width**，留一列自适应铺满屏幕，除非用户指定宽度）
- `align`：对齐（`left`/`center`/`right`）
- `fix`：列固定

## 选项数据格式

`select`、`radio`、`checkbox` 等控件的 `data` 是选项数组：

```json
"data": [
  { "text": "男", "value": "man", "role": true },
  { "text": "女", "value": "woman", "role": true }
]
```

选项来源优先级（引擎 `returnListData` 逻辑）：
1. `filterOptions`（筛选场景）
2. `oriData` + 源数据（`formData[value]` 或 `selectData[key]`/`tableData[key]`）
3. `col.data` 静态数组

## 按钮配置（btns）

### 按钮组的三种分布位置

按钮可以放在三个层级，作用域不同：

| 分布位置 | 字段 | 说明 |
|---------|------|------|
| **最外层（全局按钮）** | `jsonData.btns` 数组 | 默认分布，作用于整个表单 |
| **行内按钮** | `row.btns` 数组 | 在某个布局行（`row` 元素）内，作用于该行 |
| **列内按钮** | `col.btns` 数组 | 在某个列控件（`col.type=='button'`）内，作用于该控件 |

#### 1. 最外层按钮（`jsonData.btns`）的两种布局

最外层按钮通过 `jsonData.tops` 字段控制布局位置：

| `tops` 值 | 布局 | 说明 |
|-----------|------|------|
| `true` | **顶部布局（默认）** | 按钮组固定在表单顶部 |
| 不设置 / `false` | 右侧布局 | 按钮组固定在表单右侧 |

> **默认规则**：按钮**默认顶部布局**，即 `"tops": true`。仅当用户明确要求"右侧按钮"时，才不设置 `tops` 或设 `tops: false`。

```json
{
  "btns": [
    { "id": 1788406468977, "type": "btn", "text": "保存", "color": "primary", "action": [], "before": { "form": false, "table": [] }, "after": { "mode": false, "btnHide": [], "btnNotEdit": [] } },
    { "id": 1788406468978, "type": "btn", "text": "关闭", "color": "default", "action": [], "before": { "form": false, "table": [] }, "after": { "mode": false, "btnHide": [], "btnNotEdit": [] } }
  ],
  "tops": true
}
```

> 按钮对象的完整字段见下方「单个按钮的完整结构」，每个按钮必须有唯一的 `id`、`action`、`before`、`after` 等完整字段。

#### 2. 行内按钮（`row.btns`）

在某个 `row` 元素内，`btns` 数组与该行的 `col` 并列：

```json
{
  "type": "line",
  "title": "操作行",
  "btns": [
    { "id": 1788406468979, "type": "btn", "text": "添加", "color": "primary", "action": [], "before": { "form": false, "table": [] }, "after": { "mode": false, "btnHide": [], "btnNotEdit": [] } }
  ],
  "col": [ ... ]
}
```

#### 3. 列内按钮（`col.btns`）

在 `col` 元素内，`col.type` 为 `button`/`btn`，通过 `btns` 数组配置多个按钮：

```json
{
  "type": "button",
  "colspan": 2,
  "btns": [
    { "id": 1788406468980, "type": "btn", "text": "保存", "color": "primary", "action": [], "before": { "form": false, "table": [] }, "after": { "mode": false, "btnHide": [], "btnNotEdit": [] } },
    { "id": 1788406468981, "type": "btn", "text": "重置", "color": "default", "action": [], "before": { "form": false, "table": [] }, "after": { "mode": false, "btnHide": [], "btnNotEdit": [] } }
  ]
}
```

### 单个按钮的完整结构（重要）

每个按钮对象（无论在哪个层级）必须是**完整的按钮结构**，包含以下字段：

```json
{
  "id": 1788406468977,        // 唯一随机数（时间戳 new Date().getTime()），每个按钮必填且唯一
  "text": "保存",             // 按钮显示名
  "type": "btn",              // 按钮类型
  "icon": "",                 // 图标（el-icon-*）
  "color": "primary",         // 颜色（primary/default/success/info/warning/danger/text）
  "action": [],               // 执行逻辑数组（模型调用等，见下方）
  "size": false,              // 尺寸
  "select": false,            // 是否选择
  "multiple": false,          // 是否多选
  "column": [],               // 关联列
  "fileList": [],             // 文件列表
  "disabled": false,          // 是否禁用
  "hidden": false,            // 是否隐藏
  "before": {                 // 执行前配置
    "form": false,            // 表单必填校验
    "table": []               // 表格行必填校验
  },
  "after": {                  // 执行后配置
    "mode": false,            // 模式
    "btnHide": [],            // 执行后隐藏的按钮（按钮 id 数组）
    "btnNotEdit": []          // 执行后禁用的按钮（按钮 id 数组）
  }
}
```

**关键规则**：

1. **`id` 必填且唯一**：每个按钮都要有 `id`，用时间戳（`new Date().getTime()`，如 `1788406468977`）生成，同一表单内不重复。
2. **`before` 固定结构**：`{ "form": false, "table": [] }`。需要表单必填校验时 `form: true`；表格行必填时 `table` 填 `[{ "text": "表格名", "value": "字段1,字段2" }]`。
3. **`after` 固定结构**：`{ "mode": false, "btnHide": [], "btnNotEdit": [] }`。执行后隐藏/禁用其他按钮时，在 `btnHide`/`btnNotEdit` 数组里填对应按钮的 `id`。
4. **`action` 是数组**：按钮的执行逻辑（模型调用、自定义函数等）放在 `action` 数组里，每项是一个 action 对象。
5. **上传按钮（`type: "upload"`）默认 `tip: " "`（空格）**：`tip` 为空格时不显示上传提示文字（引擎判断 `i.tip != ' '` 才显示提示）。仅当用户要求显示上传提示时才设置具体文案。

**带完整结构的按钮示例**（保存按钮 + 提交数据 + 刷新）：

```json
{
  "id": 1788406468977,
  "text": "保存",
  "type": "btn",
  "icon": "",
  "color": "primary",
  "action": [
    { "api": "6", "code": "DM_SAVE", "num": "1", "para": "formData", "script": 3, "after": "refresh" }
  ],
  "size": false,
  "select": false,
  "multiple": false,
  "column": [],
  "fileList": [],
  "disabled": false,
  "hidden": false,
  "before": { "form": true, "table": [] },
  "after": { "mode": false, "btnHide": [], "btnNotEdit": [] }
}
```

详细字段定义（按钮类型枚举、before 校验、action 的 api 类型/自定义函数等）见 `references/button-and-common-config.md`。

## 校验清单

生成后自检：

- [ ] 顶层字段**完整**，必须包含：`formData`、`tableData`、`row`、`btns`、`status`、`navMenu`、`init`、`selectData`、`totalColspan`、`loyout`、`tops`
- [ ] **`status` 字段不能缺失**（至少 `"status": {}`，否则渲染报 `undefined.open` 错误）
- [ ] 未明确指定布局模式时，设置 `"loyout": "collapse"`（默认折叠表单布局）
- [ ] 每个 `row` 元素带 `title`（折叠面板标题），除非用户明确说不需要
- [ ] 按钮默认顶部布局，设置 `"tops": true`
- [ ] 顶部导航条用 `navMenu`（每项含 `id`/`text`），且对应 `row` 元素带相同 `id`
- [ ] `totalColspan` 是字符串
- [ ] 每个 `line` 行的 `col` 数组 `colspan` 之和等于 `totalColspan`
- [ ] 每个 `col` 有 `type` 和 `value`
- [ ] 字段标题用 `col.title` 表达，**不要**额外生成 `type:"text"`+`style:"th"` 的标签列（避免标题重复）
- [ ] 选项类控件的 `data` 数组每项含 `text` 和 `value`
- [ ] `table` 行的 `data` 指向的 key 在 `tableData` 中已初始化

## 参考资源

- `references/control-types.md`：所有控件类型的详细 JSON 字段定义和示例
- `references/layout-and-buttons.md`：布局规则详解 + 按钮（btns）基础配置
- `references/button-and-common-config.md`：组件通用配置（zujian）+ 按钮执行前配置（before）+ 按钮执行逻辑（action）详解
- `references/expression-rules.md`：自定义表达式规则详解（括号标记、内置参数、三元表达式、各场景差异）
- `references/advanced-config.md`：高级配置补充（表格默认值/主键/排序/搜索/筛选/分页、权限、临时数据源、校验、序号格式、按钮执行进阶字段）

## 与 model-designer 的分工

> 本 skill 负责 formbuilder 表单骨架（LINKFORMMOD.MODJSON 内容）的设计与生成。模型侧（SYSSEARCH 模型族 XML：主模型 + 500 伴生模型的 formSetting/formData、导入与验证）由 `model-designer` skill 负责——其 FB 契约见 `model-designer/references/endpoints.md`，骨架设计知识来源即本 skill。
