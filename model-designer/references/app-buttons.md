# APP 按钮调用契约（H5 模板里的按钮怎么触发模型脚本）

> 依据：`../totallink-app-help/references/linkquick.md`（linkquick 1~16 分发，源码行号锚定）、
> `attributes.md`（属性全集）、语料实证（KEEWAYZUP 系 APP 语料 139 个模型）。
> 属性级权威定义在 app-help 侧，本文件只讲**模型设计者**怎么用：哪种按钮配哪个脚本字段、参数怎么传。

## 0. 环境区分：传参模式不同（先读这个）

同一份 XML 的脚本字段，**两种消费端定位行的方式不同**：

| 消费端 | 行上下文 | SQLRemove / 定位行的写法 | 语料实证 |
|---|---|---|---|
| **APP（H5）按钮删除** | 无行上下文：按钮 `para` 把行 ID 作为**模型参数**传入 | `WHERE ID = '{0}'`（**用 `{0}`**） | KEEWAYZUP1010X#700：`WHERE PK_0='{0}'`；KEEWAYZUP2010X#700 同 |
| **Client/运行器（网格）** | 有行上下文：行级令牌可替换 | `WHERE ID = 0#LINKROWID#`（**用行级令牌**） | KEEWAYZUP5010X#710、ERAQA205010X.A#10 |

写错的症状：APP 上点删除报 `SQL 语法错误："#LINKROWID#" 附近`（令牌没被替换、原样进 SQL）。
SQLUpdateScript（`--LINKEDITMODE` 行编辑上下文）在两端都可以用行级令牌 `0#LINKROWID#`。

## 1. 四种按钮范式（语料实证）

### ① 新建（打开附加模型参数表单）
```html
<button type="button" linkquick="8" btnid="501" id="linknewrecord"
  linkparafill="1" linkrefresh="1" linktitle="...">
```
- `linkquick="8"`：附加功能入口；`btnid="501"` = 同族附加模型编号（框架自动拼 `主code+主num+'X'`）
- `id="linknewrecord"`：特化委托（contentlist.js 928-991）识别的新建入口
- `linkparafill="1"`：打开**附加模型参数补充页**（attachmodelpara.html；源码语义见 linkquick.md §4）
  - ⚠️ 参数预填是否按位置对齐主模型参数：语料强烈支持（KZ3010X#700 参数前两位与主模型同名对齐；TMESSTK2010X#501 实测带入成功），**但源码未核实**——设计时让附加模型参数 01、02 与主模型参数 01、02 同名同义，不依赖巧合
- 配套：附加模型 `UseParameter=true` + 参数四件套（`ParaDefVal='?'` 必填）。APP 框架可按 ParaLabel 自动渲染参数表单（KZ5010X#501 的 H5Para 为空也能用），但**校验器要求显式 H5Para**（服务端兜底已删除），生成时仍写 H5Para 模板

### ② 卡片级动作（提交/删除整单等，显式指明目标模型）
```html
<button type="button" linkquick="12" linklocation="0" api="3"
  code="TMESSTK2010X" num="502" para="#出库单号#" script="4"
  confirm="lang:{zh:确认提交?,en:Submit?,de:Einreichen?}">
```
- `script="4"`：执行目标模型 SQLClear（脚本类型 4=动作）；`"3"`=SQLRemove、`"2"`=SQLUpdateScript、`"1"`=SQLNew
- `api="3"`：走 linkDMContextFunBack 链（linkQuickAjax1~7 选接口，见 linkquick.md §6）
- `para="#出库单号#"`：把当前行该列的值作为目标模型参数 `{0}` 传入；多参数用逗号拼接 `para="#列A#,#列B#"`
- `confirm`：执行前确认框（支持 `lang:{}` 三语）
- 动作模型配套：`SQLScript` 写前置防呆（`#LINKSCRIPTGET@连接:SELECT CASE WHEN ... THEN N'LINKPREVENT:lang:{...}' ELSE '' END#`），`SQLClear` 首行 `--LINKREFRESH`

### ③ 行级删除（明细子表内）
```html
<button type="button" linkquick="12" linklocation="0" api="2"
  code="TMESSTK2010X" num="700" para="#LINKROWID#" script="3"
  confirm="lang:{...}?" class="... #LINKROWIDBTNFLG#">
```
- `para="#LINKROWID#"`：行 ID 列的值作为目标模型参数 `{0}` 传入（见 §0，SQLRemove 写 `{0}` 不写 `#LINKROWID#`）
- `api="2"`：linkDMGridRowSubmit 单行提交
- `#LINKROWIDBTNFLG#`：SQL 输出的显隐控制列（`mui-hidden` 时按钮隐藏），用于「已提交行禁删」
- 主模型 SQL 需输出 `LINKROWID` 列（如 `SELECT S.ID LINKROWID`）

### ④ 行内编辑（明细子表，卡片 collapse 内）
- 子模型 SQLUpdateScript 首行 `--LINKEDITMODE`，值用 `@列名@`，定位 `WHERE ID = 0#LINKROWID#`（行编辑上下文，两端通用）
- 可编辑性控制：输出 `LINKAPPR列名` 控制列（历史写法配 CubeSetting COLFORMAT；**当前校验器视为遗留**，推荐改由 SQL WHERE 守卫 + 按钮显隐列实现）
- 语料：KEEWAYZUP1010X#701（`--LINKEDITMODE` + `@列名@` 全套）

## 2. linkquick 分发速查（完整表见 app-help/linkquick.md）

| linkquick | 用途 | 模型设计相关 |
|---|---|---|
| 1 / 2 | 前置/后置处理 | 固定调附加 21~30 / 41~50 |
| 3 | 添加记录 | SQLNew（`--LINKADDNEWROWS`）|
| 5 | 编辑 | SQLUpdateScript 校验+编辑页 |
| 6 | 删除 | SQLRemove |
| 8 | 附加功能 | `btnid`→contextid；拍照 linkimage=1/2 |
| 10 | 数据挖掘 | btnid + paraconfirm |
| 12 | 提交所有数据 | api 1~7 + script 脚本号，模型自定义动作主力 |

## 3. 生成清单（写按钮前自查）

- [ ] `code`/`num` 指向的目标模型编号写对（附加族 = 主code+主num+X）
- [ ] `para` 引用的列在 SQL 输出里存在（含 `LINKROWID`）
- [ ] `script` 与目标脚本字段匹配（1/2/3/4）
- [ ] SQLRemove 用 `{0}`（APP）；SQLUpdateScript 用 `0#LINKROWID#`（行编辑）
- [ ] 防呆：动作模型 SQLScript 前置 LINKPREVENT 三语；显隐用 `#列#` 输出 `mui-hidden`
- [ ] 确认框 `confirm`、刷新 `--LINKREFRESH`（或 `linkrefresh="1"`）
