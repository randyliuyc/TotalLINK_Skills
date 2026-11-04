# 样例结构特征索引（samples-index）

> 用途：问卷命中「界面形态」后，从这里找模板克隆来源（只替换 `#列名#` 与列名，不从零手写 HTML/JSON）。
> 状态：**已填（2026-11-04）**——基于 `samples/` 43 个精选样例 + `samples-corpus/` 640 个全量语料（四个项目）盘点。
> 分隔符注意：全部语料 0 处 `~<!>~`（旧 `~` 只出现在 CallFunction/SQLClear 动作语法里）；读样例容忍旧写法，**产出必须 `~<!>~`**。

## 归类维度

每个条目按这些特征打标签，问卷答案按标签匹配：

| 维度 | 取值 |
|------|------|
| 环境 | APP / FB / 运行器 |
| 界面形态 | 卡片列表 / 表格模式 / 单行表单 / 主从（列表嵌明细）/ 编辑表单 / 新增表单 / 参数区 / 图表 / 多级树 / 标签打印 / 文件上传 |
| 模型族角色 | 主模型 #10 / 500 表单定义 / 501~520 动作 / 1000 防呆 / 21~50 前后置 / 其他附加 |
| 模板承载字段 | H5List / H5GRIDHDR+H5GRIDDTL / H5EDIT / H5NEWREC / H5PARA / 500 的 SEARCHSELECT(formData) |

## 索引（精选样例，samples/ 目录）

### APP（KEEWAYZUPPDA，凯途仓库管理）

| 环境 | 形态 | 模型族角色 | 模板字段 | 样例文件 | 备注 |
|------|------|-----------|---------|----------|------|
| APP | 卡片列表+编辑+参数区 | 主模型 #10 | H5List/H5Edit/H5Para/JavaScript | `KEEWAYZUP10#10-订单收货.xml` | 卡片标杆：四 JS 钩子齐全（见 `js-hooks.md`）；参数四件套含 DROPDOWN+SearchCode；`#LINK_TODAY#`；`.LOC` 参数选择按钮 |
| APP | 表格模式+行内编辑 | 主模型 #5 | H5GRIDHDR+H5GRIDDTL/SQLUpdateScript | `KEEWAYZUP10#5-整单收货.xml` | 同 ModelCode 不同入口（#5/#7/#10）；行内编辑注释三件套（--LINKEDITMODE/--LINKSAVEONENTERKEY/--LINKDATAAUTOSAVE）+ `ModelSetting.EditCols`；表头放动作按钮 linkquick+btnid |
| APP | 表格模式（第二证） | 主模型 #10 | H5GRIDHDR+H5GRIDDTL | `KEEWAYZUP20#10-存货变动.xml` | 与 #5 交叉验证 GRIDHDR 写法（语料中仅 2/139 用表格，**卡片是主流**） |
| APP | 扫码解析 | 附加 #1522 | SQLScript | `KEEWAYZUP107X#1522-扫描解析.xml` | 托/箱分支、`|`/`/` 定界解析；报错范式 `SELECT N'lang:{…}' 数据检查 RETURN` |
| APP | 参数区满配 | 附加 #501 | 参数四件套 01~10 | `KEEWAYZUP5010X#501-扫码检验.xml` | 10 槽全用 + 必填默认值（该文件用全角 `？`，生成仍按半角 `?`）+ SQLClear INSERT 提交 |
| APP | 提交/动作双承载 | 附加 #21 | SQLClear+CallFunction | `KEEWAYZUP1010X#21-提交.xml` | `--LINKREFRESH:目标模型(参数)` 声明刷新 + `#LINKID_ACTION#` 批次 + `CALLFUNCTION~X3WEB~RUN`（旧分隔符→产出用 `~<!>~`） |
| APP | 主从子表 | 附加 #700 | H5List | `KEEWAYZUP1010X#700-APP收货明细.xml` | 主模型 SQL 头 `--LINKDETAILLIST(code,num,para...)` 挂载；子 SQL 输出 `pid` 匹配父卡片 `id`；行级删除按钮；`AllDataTreatTitle`=批量操作标题；SQLRemove |
| APP | 图片展示 | 附加 #703 | H5List/JavaScript | `KEEWAYZUP2010X#703-图片展示.xml` | BLOB→base64 + `linkMediaImages` + 双指缩放 JS |

### FB（TMESPUR，百隆越南采购）

| 环境 | 形态 | 模型族角色 | 模板字段 | 样例文件 | 备注 |
|------|------|-----------|---------|----------|------|
| FB | 列表数据源 | 主模型 #9 | SQLScript/参数四件套 | `TMESPUR01#9-采购申请.xml` | 纯数据源样板：UseParameter + `{0}~{3}` 占位 + 权限过滤；H5 全空 |
| FB | 详情卡片页 | 主模型 #10 | H5List/JavaScript | `TMESPUR01#10-采购申请详情.xml` | 按钮标志位列（SABFLG/DEBFLG…）+ `btnid` 按钮 + `--LINKDETAILLIST` 注释 + `contextTap` 钩子 |
| FB | 明细（tableData 数据源） | 主模型 #20 | SQLUpdateScript | `TMESPUR01#20-采购申请明细.xml` | `pid` 关联 + MERGE INTO upsert（行编辑回写标准写法） |
| FB | 参数投影最小模型 | 附加 #110 | SQLScript | `TMESPUR01#110-…查询参数.xml` | `SELECT '{0}' AS …` 纯参数投影 + UseParameter，3KB 极简形态 |
| FB | 复杂查询/报表 | 附加 #120 | SQLScript/SQLUpdateScript/ParaDefVal | `TMESPUR01#120-申请明细查询.xml` | CTE 多源 JOIN + 可回写 MERGE + `#LINKDATE(0,-1,0,yyyy-MM-dd)#` 默认值 |
| FB | 表单定义 | 附加 #500 | H5PARA(formSetting)+SQLScript | `TMESPUR0110X#500-表单设置.xml` | formSetting 标准：`formtemplate`（MOD220500008 形态）+ `"#FORMDATA#"` 字面量 + tableData（保留名 LINKDOCLIST/LINKSIGNLIST）；SQLScript=字段映照 JSON。**formtemplate 指向的骨架需新建时用 `formbuilder-json-generator` skill** |
| FB | 菜单/列表注册 | 附加 #500 | SQLScript | `TMESPUR029X#500-List.xml` | **独立链路 ConnString=LINKMENUITEM**：列表页配置 JSON（title/path/column/paraData/paraCustom 全控件类型）；FB 查询区 UI 由这里的 paraCustom 定义，不在 H5PARA |

### 运行器增量（ERAQA 埃赫曼 / KEEWAYZUPSCH 凯途计划）

| 环境 | 形态 | 模型族角色 | 模板字段 | 样例文件 | 备注 |
|------|------|-----------|---------|----------|------|
| 运行器 | 卡片视图数据契约 | 附加 #700 | SQLScript | `ERAQATSK10X#700-检验任务信息-卡片.xml` | 运行器卡片靠 **SQL 契约列**：TITLE/INFO/REMARK/CHECKED/CARDSIZE/状态色（#e57373 等）/SORT_ORDER |
| 运行器 | 动态列表头 | 附加 #721 | SQLScript | `ERAQATSK10X#721-数字控制列标题.xml` | SQL 返回 COLNAME+CAPTION 两列，运行器动态生成表头 |
| 运行器 | 查询行为控制 | 附加 #713 | SQLScript | `ERAQATSK10X#713-检测结果汇总-数字控制.xml` | `--LINKNOGROUP`/`--LINKNOFILTER` 指令注释 |
| 运行器 | .A 子家族+文件超链 | 主模型 #10 | SQLRemove | `ERAQA205010X.A#10-Tracking Information.xml` | `.A` 子家族命名；LINKROWID 隐藏列；SQL 拼 `#LINKSERVER#` 文件超链接列（LINKDOCFIL） |
| 运行器 | 打印/导出 | 附加 #501 | SQLClear+CallFunction | `ERAQA401010X#501-客户报告-英文.xml` | `#LINKSCRIPTGET` 前置校验 + SQLClear EXEC 存储过程出报表数据 + `CALLFUNCTION~FILEEXPORT` 出 PDF（fileType 换 EXCEL 即信封导出变体） |
| 运行器 | ERP 回写 | 附加 #501 | CallFunction | `KEEWAYZUPSCH2010X#501-转采购订单.xml` | `CALLFUNCTION~X3WEB~RUN` 调 X3 Web 服务 + 三语 LINKPREVENT/LINKCONFIRM 三分支 |
| 运行器 | 自动单号动作 | 附加 #21 | SQLClear | `KEEWAYZUPSCH1010X#21-新计划单.xml` | `#LINKDOCNUM(,{0})#` 自动单号 + 三语 LINKPREVENT |

### 运行器基础形态（存量 21 个）

基础教学点（最小维护模型、参数化查询、导出报表、#21/#41 前后置、#501 行级动作、#1000 防呆、子表维护、列级下拉、文件上传）见 `samples/README.md` 的教学点表——不在此重复展开。

## 全量语料（samples-corpus/，只读参照，不直接克隆）

| 子目录 | 项目 | 环境 | 文件数 | 语料价值 |
|---|---|---|---|---|
| `ERAQA/` | 埃赫曼质量管理 | 运行器 | 187 | 现有 21 样例的超集；UI 模板字段全空，价值在 SQL 驱动的运行器契约（卡片列、动态表头） |
| `KEEWAYZUPSCH/` | 凯途计划管理 | 运行器 | 55 | 与 ERAQA 同构；增量仅 X3WEB 调用与三语提示 |
| `KEEWAYZUPPDA/` | 凯途仓库管理 | **APP** | 139 | H5 模板富矿（卡片/表格/扫码/参数/图片/JS 钩子） |
| `TMESPUR/` | 百隆越南采购 | **FB** | 259 | #500 formSetting 21 处一致写法；LINKMENUITEM 菜单注册；#110/#120 形态 |

精选样例之外的形态按图索骥：先在 `samples-corpus/<对应环境>/` 里按文件名（编号段+描述）定位，再抽读。

## 语料盘点统计结论（2026-11-04）

- 500 表单 JSON：formSetting 的 `formbtns` 与 `selectData` **259 个 FB 文件恒空**——生成时默认空数组/空对象，按钮逻辑由 #501+ 动作模型与骨架 btns 承担。
- 界面形态由**模板字段组合**决定，与 `ChartType`（SEARCHORDER）无关（APP 语料该列恒空）：H5List=卡片、H5GRIDHDR+H5GRIDDTL 成对=表格（少数派）。
- `H5GridHeader/H5GridDetail`、`ListPrint`+`H5Detail` 成对标签模板在四个项目语料中均未见使用——仍标【无样例证据】。
- JS 脚本：APP 约 19% 模型非空，钩子见 `js-hooks.md`。
