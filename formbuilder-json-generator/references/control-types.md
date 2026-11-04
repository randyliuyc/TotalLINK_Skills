# 控件类型详细字段定义

本文档列出 formbuilder 引擎所有控件的 `type` 值、关键字段和 JSON 示例。字段来源为各控件组件的 props 和模板绑定。

> **重要约定**：下方各控件示例为了聚焦"该控件的特有字段"，省略了通用字段 `title`（字段标题）、`colspan`（占列）、`role`（可编辑）。**实际生成 JSON 时必须带上 `title`**（字段标题，通过 `el-form-item` 的 label 渲染），否则字段会没有标题。例如 `input` 控件完整写法应为 `{ "type": "input", "title": "姓名", "value": "name", "role": true }`，而不是只有 `{ "type": "input", "value": "name" }`。

## 基础输入类

### text（纯文本/标签）

用于静态文本/纯展示内容（非输入）。显示内容用 `text` 或 `value` 绑定值。作为"整格纯标题格"（分组标题行、纯展示栏头）时配合 `style: "th"`。

```json
{ "type": "text", "colspan": 1, "title": "分组标题", "role": true, "style": "th", "value": "groupTitle" }
```

字段：`value`（绑定字段/显示内容）、`text`（显示内容）、`style`（`"th"` 表示整格纯标题格）、`align`、`fontColor`、`bgColor`。

> 注意：字段的标题不要用 `text`+`style:"th"` 表达，而应直接用各控件的 `title` 字段（如 `input` 的 `title`）。

### input（文本输入框）

```json
{ "type": "input", "colspan": 1, "title": "姓名", "role": true, "value": "name", "placeholder": "请输入姓名" }
```

字段：`value`、`placeholder`、`disabled`、`maxlength`、`showWordLimit`。

### number（数字计数器，el-input-number）

```json
{ "type": "number", "colspan": 1, "value": "age", "min": 0, "max": 100, "step": 1, "stepStrictly": true, "precision": 0 }
```

字段：`min`、`max`、`step`、`stepStrictly`、`precision`、`size`、`disabled`、`controls`、`position`。

### numberKey（数字键盘）

```json
{ "type": "numberKey", "colspan": 1, "value": "code" }
```

## 选择类

### select（下拉选择）

```json
{
  "type": "select", "colspan": 1, "value": "work",
  "data": [
    { "text": "教师", "value": "teacher", "role": true },
    { "text": "学生", "value": "student", "role": true }
  ],
  "dataText": "text", "dataValue": "value", "multiple": false
}
```

字段：`data`（选项数组）、`dataText`（显示字段，默认 `text`）、`dataValue`（值字段，默认 `value`）、`multiple`（多选）、`disabled`。

### select-search（可搜索下拉）

与 `select` 结构相同，额外支持搜索过滤。字段：`data`、`dataText`、`dataValue`、`multiple`。

### autoinput（带输入建议）

支持 `oriData`（源数据）、`dataKey`（统一数据标识）。字段：`data`、`oriData`、`dataKey`、`dataText`、`dataValue`。

### radio（单选）

```json
{
  "type": "radio", "colspan": 1, "value": "sex",
  "data": [
    { "text": "男", "value": "man", "role": true },
    { "text": "女", "value": "woman", "role": true }
  ],
  "justifyContent": "flex-start", "rowGap": "", "columnGap": ""
}
```

字段：`data`、`justifyContent`、`rowGap`、`columnGap`。无 `data` 时默认显示"是/否"（1/0）。

### checkbox（多选）

```json
{
  "type": "checkbox", "colspan": 1, "value": "hobby",
  "data": [
    { "text": "篮球", "value": "basketball", "role": true },
    { "text": "足球", "value": "football", "role": true }
  ],
  "border": false, "size": "small", "min": 0, "max": 99,
  "single": false, "trueLabel": "1", "falseLabel": "0", "checkboxText": ""
}
```

字段：`data`、`border`、`size`、`min`、`max`、`single`（单选模式）、`trueLabel`、`falseLabel`、`checkboxText`、`fontSize`。

### cascader（级联选择器）

```json
{
  "type": "cascader", "colspan": 1, "value": "region",
  "data": [
    { "text": "广东", "value": "gd", "children": [ { "text": "广州", "value": "gz" } ] }
  ],
  "multiple": false, "checkStrictly": false, "cascaderList": false,
  "cascaderMode": "click", "children": "children", "lazy": false, "leaf": "leaf"
}
```

字段：`data`（树形，`children` 嵌套）、`dataValue`、`dataText`、`multiple`、`checkStrictly`、`cascaderList`（`show-all-levels`）、`cascaderMode`（`click`/`hover`）、`children`、`lazy`、`leaf`、`lazySetting`。

### dropdown（下拉菜单）

下拉触发多个动作按钮。字段：`btns`（按钮数组）、`value`。

## 日期时间类

### date（日期选择器）

```json
{ "type": "date", "colspan": 1, "value": "birthday", "dateType": "date", "dateFormat": "yyyy-MM-dd" }
```

字段：`dateType`（`date`/`datetime`/`datetimerange`/`year`/`month`/`week`/`daterange`）、`dateFormat`、`options`（快捷选项/禁用日期）、`disabledDate`、`disabledDateExpress`、`placeholder`。

### time（时间选择器）

```json
{ "type": "time", "colspan": 1, "value": "workTime" }
```

### timeSelect（时间段选择器）

```json
{ "type": "timeSelect", "colspan": 1, "value": "timeRange" }
```

## 数值/状态类

### switch（开关）

```json
{ "type": "switch", "colspan": 1, "value": "enable" }
```

### slider（滑块）

```json
{ "type": "slider", "colspan": 1, "value": "score" }
```

### rate（评分）

```json
{ "type": "rate", "colspan": 1, "value": "rating" }
```

### progress（进度条）

```json
{ "type": "progress", "colspan": 1, "value": "progress" }
```

### colorPicker（颜色选择器）

```json
{ "type": "colorPicker", "colspan": 1, "value": "themeColor" }
```

## 展示/媒体类

### image（图片）

```json
{ "type": "image", "colspan": 1, "value": "avatar", "btns": [] }
```

字段：`value`、`btns`（图片操作按钮）。

### tag（标签）

```json
{ "type": "tag", "colspan": 1, "value": "status", "color": "success", "bg": "", "size": "small", "theme": "light", "border": false }
```

字段：`color`（`success`/`warning`/`info`/`danger`/空）、`bg`、`size`、`theme`（`light`/`dark`/`plain`）、`border`。

### href（超链接）

```json
{ "type": "href", "colspan": 1, "value": "url", "data": [] }
```

### h1（标题）

```json
{ "type": "h1", "colspan": 1, "value": "title" }
```

### carousel（走马灯）

```json
{ "type": "carousel", "colspan": 1, "value": "banner", "data": [] }
```

### card（自定义卡片）

```json
{ "type": "card", "colspan": 1, "value": "cardData" }
```

### lineid（自增序号）

```json
{ "type": "lineid", "colspan": 1, "value": "index", "indexFormat": "NO-$index" }
```

字段：`value`、`indexFormat`（序号格式，`$index` 占位符）。

### iframe（网页嵌套）

```json
{ "type": "iframe", "colspan": 1, "url": "https://example.com", "height": "600px", "query": [] }
```

字段：`url`（支持 `{field}` 占位符）、`height`、`query`（url 参数数组）。

### bgImage（背景图）

```json
{ "type": "bgImage", "colspan": 1, "value": "bgUrl" }
```

### treeData（树形数据）

```json
{ "type": "treeData", "colspan": 1, "value": "tree", "data": [] }
```

### tinymce（富文本）

```json
{ "type": "tinymce", "colspan": 1, "value": "content" }
```

## 表格/特殊类型

### button / btn（自定义按钮）

```json
{
  "type": "button", "colspan": 1,
  "btns": [
    { "value": "save", "text": "保存", "type": "primary" }
  ]
}
```

字段：`btns`（按钮配置数组，详见 layout-and-buttons.md）。

### selection（选择框，表格列）

表格列勾选，用 `colType` 而非 `type`：

```json
{ "colType": "selection", "text": "选择", "value": "checked", "trueLabel": "1", "falseLabel": "0" }
```

### expand（折叠行，表格列）

```json
{ "colType": "expand", "text": "展开", "value": "detail", "templateType": "fileList", "templateSetting": {}, "rowTemplate": "姓名-name,年龄-age" }
```

字段：`templateType`（`fileList`/`fileTable`/自定义）、`templateSetting`、`rowTemplate`（自定义模板，格式 `标签-字段` 逗号分隔）、`noHeader`。
