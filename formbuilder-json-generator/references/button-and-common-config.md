# 组件通用配置 + 按钮执行配置详解

本文档整合三个配置面板的字段定义，用于生成正确的表单 JSON。字段来源：`setting/zujian.vue`（组件通用配置）、`setting/before.vue`（按钮执行前配置）、`setting/action.vue`（按钮执行逻辑配置）。

---

## 一、组件通用配置（zujian.vue 提炼）

所有控件（col）的通用字段，按用途分类。字段名前缀 `col.xxx`。

### 1. 基础样式

| 字段 | 含义 | 类型/可选值 |
|------|------|-----------|
| `size` | 表单尺寸 | `""`/`medium`/`small`/`mini` |
| `labelWidth` | 标题宽度 | 如 `90px` |
| `labelHidden` | 隐藏列标题 | boolean |
| `minWidth` | 最小宽度 | 如 `100px` |
| `width` / `height` | 宽度/高度 | 如 `100px` / `30px` |
| `align` | 对齐方式 | `left`/`center`/`right` |
| `fontStyle` | 字体样式 | `SimHei`/`SimSun`/`Microsoft YaHei` 等 |
| `fontSize` | 字体大小 | 如 `14px` |
| `fontColor` | 字体颜色 | 色值 |
| `bgColor` | 背景颜色 | 色值 |
| `titleColor` | 标题颜色 | 色值 |
| `lineHeight` | 行高 | 如 `30px` |
| `padding` | 内边距 | 如 `5px` |
| `justifyContent` | 布局方式 | `flex-start`/`center`/`flex-end`/`space-between`/`space-around`/`space-evenly` |
| `rowGap` / `columnGap` | 行内/列间距 | 如 `5px` |

### 2. 布局

| 字段 | 含义 | 类型/可选值 |
|------|------|-----------|
| `colspan` | 列占位（占几列） | number，`line` 行内使用 |
| `rowspan` | 行占位（行高） | number |
| `rowMerge` | 合并行数 | number |
| `style` | 格子类型 | `td`（标准）/`th`（表头标签） |
| `colType` | 列类型（表格） | `""`/`selection`/`expand` |

### 3. 校验 / 权限 / 隐藏

| 字段 | 含义 | 类型 |
|------|------|------|
| `required` | 必填 | boolean |
| `error` | 必填提示文案 | string |
| `notZero` | 禁输入 0 | boolean |
| `role` | 可编辑权限 | boolean |
| `roleCustom` | 自定义权限规则 | 表达式 |
| `hiddenCol` | 隐藏配置 | 表达式 |
| `disabled` | 禁用字段 | 字段名或 boolean |
| `inputVerify` | 输入校验规则 | 自定义函数 |
| `express` | 绑定值变化触发的自定义函数 | 函数体 |

### 4. 数据源 / 绑定

| 字段 | 含义 | 说明 |
|------|------|------|
| `value` | 绑定字段名 | formData 的 key |
| `dataText` | 选项显示字段 | 默认 `text` |
| `dataValue` | 选项值字段 | 默认 `value` |
| `dataKey` | 统一数据源标识 | 指向 `selectData`/`tableData` 的 key |
| `oriData` | 使用原始数据源 | boolean |
| `automatch` | 自动带出 | 带出字段配置 |
| `automatchArray` | 自动带出数组 | 数组格式 |
| `tempData` | 临时数据源 | boolean |
| `tempDataKey` | 临时字段名 | string |
| `defaultValue` | 默认值 | 各控件不同 |
| `multiple` | 单选/多选 | boolean（select/checkbox/cascader） |

### 5. 事件 / 模型调用

| 字段 | 含义 | 可选值 |
|------|------|--------|
| `clickEvent` | 操作事件 | `click`/`dbClick` |
| `code` | 模型代码 | string |
| `num` | 模型编号 | string |
| `para` | 模型参数 | string |
| `script` | 脚本类型 | 默认 `3` |

---

## 二、按钮执行前配置（before.vue 提炼）

按钮字段前缀 `col.before.xxx`（执行前）、`col.after.xxx`（执行后）。

### 1. 必填校验（`before.form`）

```json
"before": {
  "form": true,              // 启用表单必填校验
  "message": "*号标识为必填项",  // 必填提示
  "messageTypeBefore": "message" // alert/message/notify
}
```

### 2. 表格行必填（`before.table` 数组）

```json
"before": {
  "table": [
    { "text": "TABLE_1", "value": "name,age" }  // 表格名 + 必填字段（逗号分隔）
  ]
}
```

### 3. 确认框 / 提交框

| 字段 | 含义 |
|------|------|
| `before.confirm` | 确认框内容（支持 `{表达式}`） |
| `before.confirmTip` | 确认提示 |
| `before.prompt` | 提交框内容 |
| `before.promptTip` | 提交提示 |
| `before.promptValue` | 提交内容绑定字段，默认 `prompt` |

### 4. 执行前模型校验

```json
"before": {
  "code": "模型代码",
  "num": "模型编号",
  "para": "模型参数",
  "script": 3,
  "beforeJs": "自定义校验函数"
}
```

### 5. 自定义条件校验（`before.custom` 数组）

```json
"before": {
  "and": false,              // false=逻辑或，true=逻辑与
  "express": "",             // 自定义表达式（优先级最高）
  "tip": "整体提示",
  "custom": [
    {
      "data1": "formData.A",     // 表单数据（.链式）
      "condition": "==",         // 条件运算符
      "data2": "formData.B",     // 目标数据
      "tip": "提示信息"
    }
  ]
}
```

**条件运算符可选值**：

| value | 含义 |
|-------|------|
| `not` | 不等于空 |
| `null` | 等于空 |
| `>` / `<` / `>=` / `<=` | 比较 |
| `==` / `!=` | 等于/不等于 |
| `express` | 自定义表达式 |
| `some` / `every` | 数组满足条件 |
| `length` | 判断数组长度是否为空 |

### 6. 执行后处理（`after`）

| 字段 | 含义 |
|------|------|
| `after.close` | 关闭表单 |
| `after.status` | 执行后修改状态字段值 |
| `after.notEidt` | 执行后表单不可编辑 |
| `after.btnNotEdit` | 禁用按钮（按钮 ID，逗号分隔） |
| `after.btnHide` | 隐藏按钮（按钮 ID，逗号分隔） |
| `after.colNotEdit` | 禁用字段（`0-0,1-1` 行-列格式） |
| `after.colHide` | 隐藏字段（`0-0,1-1` 格式） |
| `after.show` | 显示字段（`0-0,1-1` 格式） |

---

## 三、按钮执行逻辑配置（action.vue 提炼）

按钮的核心逻辑存在 `action` 数组（普通逻辑）或 `ifAction` 数组（条件逻辑）中，每项是一个 action 对象。

### 1. api 类型（最核心字段）

`api` 决定动作类型：

| api 值 | 含义 |
|--------|------|
| `0` | 获取模型数据 |
| `1` | 提交单行记录数据 |
| `2` | 附加功能处理 |
| `3` | 提交多行记录数据 |
| `4` | 获取公式结果 |
| `5` | 载入模板/跳转刷新 |
| `6` | 提交全部数据 |
| `7` | 获取级联数据 |
| `8` | 获取图表 |
| `Function` | 自定义函数 |
| `sleep` | 延时执行 |

### 2. 模型调用参数

```json
{
  "api": "0",
  "code": "模型代码",
  "num": "模型编号",
  "para": "模型参数",
  "orderPara": "有序参数",   // api=3/6
  "script": 3,
  "attach": "DOCNUM",        // api=3，附加参数
  "formula": "公式赋值"       // api=0/4/5/6/7
}
```

### 3. 数据来源（api=0/4）

| 字段 | 含义 | 可选值 |
|------|------|--------|
| `value` | 数据源 | `formData`/`selectData`/`tempData`/各 tableData 名 |
| `value2` | 子数据源 | string |
| `modelKey` | 模型字段 | 如 `DOCNUM` |
| `tempDataKey` | 临时字段 | string |

### 4. 执行后行为（`after` 字段）

| after 值 | 含义 |
|----------|------|
| `open` | 打开文件 |
| `message` | 自动消失提示 |
| `alert` | 弹窗消息 |
| `refresh` | 刷新表单 |
| `notify` | 右上角通知 |
| `express` | 自定义表达式 |
| `formula` | 公式赋值 |
| `modelInfo` | 改变当前模型信息 |
| `messageCustom` | 自定义消息 |
| `closeMessage` | 关闭所有自定义消息 |
| `closeForm` | 关闭表单 |

### 5. 自定义函数类型（`type` 字段，api=Function 时）

`type` 决定快捷函数行为：

| type 值 | 含义 |
|---------|------|
| `add` | 表格添加行 |
| `delete` | 根据序号删除 |
| `deepDelete` | 根据主键删除 |
| `download` | 下载文件 |
| `refreshTable` | 重新渲染表格 |
| `refreshAll` | 重新渲染界面 |
| `matchData` | 带出上级数据 |
| `mergeObjects` | 主表合并数据 |
| `changeData` | 改变主表/子表数据 |
| `openDetail` | 打开详情 |
| `scan` | 扫码 |
| `ai` | 打开 AI 助手 |
| `waterMarker` | 水印功能 |
| `changeColor` | 改变行颜色 |
| `tempData` | 临时数据赋值 |
| `logout` | 退出登录 |
| `tableScroll` | 表格自动滚动 |
| `tableFill` | 表格批量填充 |
| `uniqueTable` | 表格去重 |
| `array2string` | 数组转字符 |

### 6. 延时执行（api=sleep）

```json
{ "api": "sleep", "time": 1000 }   // 暂停时间（毫秒）
```

---

## 四、完整按钮配置示例

一个带"执行前校验 + 提交数据 + 刷新"的保存按钮（注意：按钮对象必须包含完整的字段结构，尤其 `id` 唯一、`action`/`before`/`after` 等）：

```json
{
  "type": "button",
  "colspan": 4,
  "btns": [
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
  ]
}
```

## 五、按钮对象的标准字段结构

每个按钮对象（无论在 `jsonData.btns`、`row.btns` 还是 `col.btns` 中）都应包含以下完整字段：

```json
{
  "id": 1788406468977,       // 唯一随机数（时间戳），必填且唯一
  "text": "保存",            // 显示名
  "type": "btn",             // 按钮类型（btn/upload/href/import/input 等）
  "icon": "",                // 图标 el-icon-*
  "color": "primary",        // 颜色
  "action": [],              // 执行逻辑数组
  "size": false,
  "select": false,
  "multiple": false,
  "column": [],
  "fileList": [],
  "disabled": false,
  "hidden": false,
  "before": { "form": false, "table": [] },
  "after": { "mode": false, "btnHide": [], "btnNotEdit": [] }
}
```

**上传按钮（`type: "upload"`）的 `tip` 字段**：

- `tip` 为上传控件下方的提示文字，引擎判断 `i.tip != ' '` 时才显示。
- **默认 `tip: " "`（空格）**，表示不显示任何提示文字。
- 仅当用户明确要求显示提示（如"只能上传 PDF 文件"）时，才设置具体文案。

```json
{
  "id": 1788406468980,
  "text": "上传文件",
  "type": "upload",
  "icon": "",
  "color": "default",
  "tip": " ",
  "action": [],
  "size": false,
  "select": false,
  "multiple": false,
  "column": [],
  "fileList": [],
  "disabled": false,
  "hidden": false,
  "before": { "form": false, "table": [] },
  "after": { "mode": false, "btnHide": [], "btnNotEdit": [] }
}
```

> 字段完整定义见 `references/button-and-common-config.md`，控件类型定义见 `references/control-types.md`。
