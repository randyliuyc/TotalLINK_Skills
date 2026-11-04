# 高级配置规则补充

本文档补充表格、权限、数据源、校验、序号、按钮执行等场景的进阶配置规则。字段归属：`col.xxx`（组件自身）、`row.xxx`（表格行/表头列）、`jsonData.xxx`（全局数据对象）。

---

## 一、表格（table 类型）进阶

### 1.1 表格默认值 `col.defaultValue`

- **结构**：数组，每项 `{ text: 字段名, value: 默认值 }`。
- `value` 支持 6 种写法：
  1. 静态数据：直接写值
  2. `{XXX}`：取主表 `jsonData.formData.XXX` 的值
  3. `{XX+XXX}`：拼接多个主表字段值（找不到字段返回原表达式；`{X}` 特殊标记转为空字符 `""`）
  4. `[XXXXXX]`：自定义表达式，需**自行写 return**，可用参数 `jsonData`（模板数据）、`table`（对应表格数据）
  5. 表达式示例：`[return jsonData.formData.XXX]`、`[if(jsonData.formData.XXX)return '1';return '']`
  6. 内置消息函数：`$message`、`$alert`、`$confirm`、`$prompt`、`$msgbox`、`$notify`

### 1.2 多层级（树形）表格主键 `col.rowKey`

- 多层级表格数据的主键/唯一标识字段名，默认 `id`。
- 多个主键用逗号隔开，如 `"id,pid"` 表示 `id` 和 `pid` 联合主键。
- 关联字段：
  - `col.children`：子集字段名，默认 `children`
  - `col.leaf`：叶子节点字段名，默认 `leaf`
  - `col.showAll`：默认展开所有节点

### 1.3 表格排序 `col.sortable` / `col.sortName`

- `sortable`（布尔）开启列排序；`sortName` 指定排序字段，多个逗号隔开（按顺序依次比较）。

### 1.4 搜索相关

| 字段 | 归属 | 说明 |
|------|------|------|
| `openSearch` | `row` | 搜索总开关（勾选才触发筛选） |
| `search` | `col` | 单列搜索开关（列表头显示搜索框） |
| `searchValue` | `col` | 列搜索默认筛选值 |
| `codeSearch` / `numSearch` / `paraSearch` | `col` | 列搜索的模型代码/编号/参数 |
| `reloadSearch` | `col` | 实时刷新 |
| `dataKeySearch` | `col` | 搜索数据统一 |

### 1.5 筛选相关

| 字段 | 归属 | 说明 |
|------|------|------|
| `filterEnabled` | `row` | 开启筛选结果 |
| `openFilter` | `col` | 开启列条件筛选（显示搜索图标） |
| `filter` | `col` | 筛选控件配置对象，默认 `{ type: 'input', hidden: false, role: true }` |
| `filterIcon` | `col` | 筛选图标，默认 `el-icon-search` |
| `filterValue` | `col` | 筛选值，默认 `null` |
| `autoOptions` | `col` | 自定义数据（勾选后获取模型下拉列表） |
| `tagType` | `col` | 标签颜色（primary/success/warning/danger/info） |

### 1.6 表格分页 `col.pagination` 系列

| 字段 | 说明 |
|------|------|
| `pagination` | 布尔，启用分页器 |
| `pageSize` | 每页条目数，默认 10 |
| `pageCount` | 总页数（与 total 二选一） |
| `total` | 总条数 |
| `pagerCount` | 页码按钮数量（>=5 且 <=21 的奇数） |
| `pageSizes` | 每页条数选项，默认 `10, 20, 30, 40, 50, 100` |
| `layout` | 分页布局，默认 `prev, pager, next, jumper, ->, total` |
| `small` | 小型分页样式 |
| `pageColor` | 添加背景色 |
| `reloadAllCheck` | 刷新全选状态 |

---

## 二、权限相关

### 2.1 行权限 `row.roleCustom`（整个表格判断）

1. 直接配置字段名（主表或子表当前行字段）：有值允许编辑，无值不允许。
2. `{XXX}` 表达式（自带 return）：返回 true/有值 = 允许编辑，false/空 = 不允许。
3. 用 `?:` 代替 if-else。示例：`{jsonData.formData.XX==='1'?true:false}`

### 2.2 字段编辑权限 `col.role` / `col.roleCustom`

- `role`（布尔）可编辑开关。
- `roleCustom`：规则同行权限。

### 2.3 隐藏 `col.hiddenCol`

1. 直接填字段名：有值隐藏，无值显示。
2. `{XXX}` 表达式：**与直接字段名方式相反**——返回 true/有值 = 不隐藏，false/空 = 隐藏。

### 2.4 删除相关

- `col.delete`（可删除，末尾加删除列）、`col.confirm`（删除确认框）、`col.key`（删除主键字段，默认 ID）、`col.code`/`num`/`para`/`script`（删除模型）。

---

## 三、数据源进阶

### 3.1 临时数据源 `col.tempData` / `col.tempDataKey`

- `tempData`（布尔）绑定临时数据源 `jsonData.tempData`。
- `tempDataKey`：临时字段名，默认 `tempData`，即绑定 `jsonData.tempData[临时字段]`。
- 若 `jsonData.tempData` 不存在会自动创建 `{}`。

### 3.2 数据统一 `col.dataKey` 与原始数据 `col.oriData`

- `dataKey`（数据统一）：引用外层 `jsonData.selectData` 或 `jsonData.tableData` 里的数组数据，减少渲染压力。直接填 `selectData`/`tableData` 内部的字段名。
- `oriData`（原始数据）：勾选后使用自身绑定字段（`col.value`）对应的值作为数据源，值可为逗号分隔字符串（自动转数组）或数组。

### 3.3 自动带出 `col.automatch`

- 单选可用。规则：
  - 字段相同/不同带出：`A1-A2`（把选中项的 A1 字段值赋给 A2）
  - 带出子表：`[模型代码-模型编号-模型参数-数据源-子数据源-公式赋值]`（需 5 个 `-` 横杠）

### 3.4 去重 `col.unique`

- 去重主键，逗号隔开。

---

## 四、校验进阶

| 字段 | 说明 |
|------|------|
| `required` | 必填 |
| `error` | 必填提示（组件下方红色） |
| `notZero` | 勾选后输入 0 也触发必填，需配合 required |
| `inputVerify` | 输入定义/自定义校验（无需 `{}`，无 return，用 `set()` 赋值） |
| `errorLang` | 校验翻译 `{zh:中文,en:...}` |
| `inputFormat` / `textFormat` | 输入格式自动转换 |
| `dataType` | 数字类型（勾选后传值转数字） |
| `quickCalc` + `fixed` | 快速计算表达式 + 保留小数 |

快速计算示例：`A+B-C*D/E` 或 `(A+B-E)*C/D`（A~E 为字段名），结果作为 `result` 参数。

---

## 五、序号与特殊格式

### 5.1 自增序号 `col.indexFormat`（type='lineid'）

1. `$index`：从 1 自增，`"NO$index"` → `NO1,NO2...`
2. 逗号隔开多个表达式：`"NO,$index"` → `NO1,NO2...`
3. `{XXX}`：主表字段值，如 `"{DOC},$index"` → `NO1...`
4. `[XXX]`：子表当前行字段值，如 `"[DOC],$index"`

### 5.2 ToF 布尔格式 `col.ToF`

- 默认 `"是,否"`，格式 `"YES,NO"`。true/1 → YES（"是"），false/0 → NO（"否"）。

---

## 六、按钮执行前（before）补充字段

| 字段 | 说明 |
|------|------|
| `closeMessage` | 调用成功后不显示提示 |
| `closeLoading` | 调用前不显示等待提示 |
| `status` / `statusList` | 状态字段 + 可见列表（逗号分隔转数组），状态值在列表中才显示按钮 |
| `before.form` | 表单/表格必填校验开关 |
| `before.message` | 必填默认提示（默认 `*号标识为必填项`） |
| `before.messageTypeBefore` | 消息类型（alert/message/notify） |
| `before.table` | 表格行必填 `[{text:表格名, value:字段逗号隔开}]` |
| `before.confirm` / `confirmTip` | 确认框 + 消息 |
| `before.prompt` / `promptTip` / `promptValue` | 提交框 + 提示 + 字段（默认存 `jsonData.formData.prompt`） |
| `before.hidden` | 执行前隐藏字段，格式 `0-0,1-1`（行-列，序号从 0） |
| `before.and` | 逻辑模式（false=或，true=与） |
| `before.custom` | 自定义校验数组（见下） |

### before.custom 每项字段

| 字段 | 说明 |
|------|------|
| `data1` | 表单数据（`.` 链式，如 `formData.A`） |
| `condition` | not/null/>/</==/!=/>=/<=/express/some/every/length |
| `data2` | 目标数据 |
| `filterField` | 筛选字段 |
| `zeroLen` | 数组长度 |
| `express` | 条件定义 |
| `tip` | 提示 |

---

## 七、按钮执行逻辑（action）补充字段

### 逻辑项通用字段

| 字段 | 说明 |
|------|------|
| `actionBefore` | 执行校验（表达式） |
| `beforeMessage` | 提示消息（默认"取消"） |
| `api` | 接口类型（0-8、Function、sleep） |
| `submitTempData` / `submitTempDataKey` | 提交临时数据 + 临时字段 |
| `allTable` | 提交子表所有数据 |
| `noDirty` | 禁止过滤未修改行 |
| `filterTable` | 提交搜索后数据 |
| `complex` | 多级数组转一级数组 |
| `checkedKey` / `checkedValue` | 过滤字段 + 过滤值（逗号隔开一一对应） |
| `recordRows` | 记录行数保存到主表字段 |
| `children` | 数组节点（默认 children） |
| `_blank` / `_return` | 新窗口打开 + 返回刷新 |
| `attach` | 附加参数（api=3，默认 DOCNUM） |
| `value` / `value2` / `modelKey` / `tempDataKey` | 数据源 / 子数据源 / 模型字段 / 临时字段 |
| `formula` | 公式赋值（`.` 多层级 + `=` 必填） |
| `after` | open/message/alert/refresh/notify/express/formula/modelInfo/messageCustom/closeMessage/closeForm |
| `afterFormula` / `afterExpress` | 执行后数据配置/后表达式 |
| `openKey` | 打开字段（默认 url） |
| `closeMID` | 指定关闭消息 ID |
| `newCode` / `newNum` / `newPara` | 改变当前模型信息 |
| `id` | 图表 ID（api=8） |

### 表格添加行（type='add'）关键字段

| 字段 | 说明 |
|------|------|
| `defaultValue` | 默认值字符串 `"字段名1:默认值1,字段名2:默认值2"`，支持 `{XXX}`、`{XX+XXX}`、`[表达式]` |
| `addType` | start（首行）/push（追加默认）/end（尾行）/nullArray（空数组添加） |
| `tableName` | 表格名称 |
| `tempData` / `tempDataKey` | 临时数据赋值 |

---

## 八、字段归属速查表

| 配置项 | 归属 | 说明 |
|---|---|---|
| 表格默认值 | `col.defaultValue` | `{text,value}` 数组 |
| 多层级主键 | `col.rowKey` | 默认 id，联合主键逗号隔开 |
| 排序 | `col.sortName` / `col.sortable` | |
| 搜索总开关 | `row.openSearch` | 表格行配置 |
| 筛选 | `row.filterEnabled`、`col.openFilter`、`col.filter` | |
| 分页 | `col.pagination` 系列 | |
| 行权限 | `row.roleCustom` | 整个表格 |
| 字段权限 | `col.role` / `col.roleCustom` | |
| 隐藏 | `col.hiddenCol` | |
| 临时数据 | `col.tempData` / `col.tempDataKey` | 存 `jsonData.tempData` |
| 数据统一 | `col.dataKey` | 引用 `selectData`/`tableData` |
| 原始数据 | `col.oriData` | |
| 必填 | `col.required` / `col.error` | |
| 禁输0 | `col.notZero` | 配合 required |
| 序号格式 | `col.indexFormat` | `$index`/`{XXX}`/`[XXX]` |
