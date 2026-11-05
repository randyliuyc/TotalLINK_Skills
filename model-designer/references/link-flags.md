# 脚本注释标记（--LINKxxx）与结果标记

> 权威来源：`BaseLib/DataModel/SysDataModel.vb`（解析处）+ 21 个真实样例。样例证据 + 源码行号双重锚定。

## 样例实证的标记（优先使用）

写在脚本字段**首行注释**（`--` 开头），运行时按行解析：

| 标记 | 所在字段 | 参数格式 | 语义 | 样例证据 |
|------|---------|---------|------|---------|
| `--LINKSAVEONENTERKEY` | SQLUpdateScript | 无 | 回车即保存 | ERAQA1005#10:21 等 7 处 |
| `--LINKEDITMODE` | SQLUpdateScript | 无 | 启用行编辑 | ERAQA1005#10:22 等 6 处 |
| `--LINKREQUIRED:列1,列2` | SQLUpdateScript | **冒号 + 逗号分隔列名** | 必填校验 | ERAQA1005#10:23 |
| `--LINKADDNEWROWS` | SQLNew **或 SQLUpdateScript** | 无 | 启用新增行/编辑态直接添加记录行（2023-12-14 起 `SysDataModel.vb:1106-1108` 允许写在 UPDATESCRIPT） | ERAQA1005#10:73；TAMPERFB BH#10/BL#10 SQLUpdateScript 首部 |
| `--LINKNOGROUP` | SQLScript | 无 | 禁止分组 | ERAQA101010X#700:10 |
| `--LINKDATAMINELAYOUT:55,45` | SQLScript | **冒号 + 逗号数值** | 挖掘布局比例 | ERAQA1010#10:10 |
| `--LINKLOADDATAIMMEDIATE` | SQLScript | 无 | 立即加载数据（导出类大查询） | ERAQA1010#20:10 |
| `--LINKDATAMINEOVERVIEW,VERTICAL,60,AUTOREFRESH` | SQLScript | **逗号分隔多参数** | 挖掘总览（方向/比例/自动刷新） | ERAQA1020#10:10 |
| `--LINKREFRESH` | SQLClear | 无 | 动作执行后刷新 | ERAQA101010X#21:62 等 6 处 |
| `--LINKMYROWDATA` | SQLScript | 无 | 标记主列表行数据脚本（MyRowData 链路） | TAMPERAPP TMESPDA130#10:10 |
| `--LINKEXECOUTPUT` | SQLClear | 无 | 声明脚本带 OUTPUT 参数并返回结果集（EXEC 存储过程 OUTPUT 后 `SELECT @RPTSTA,@RPTMSG` 回传） | TAMPERAPP TMESPDA13010X#21:87 |
| `--LINKAUTOREPLACEEMPTYCOLUMNS` | 任意经公式替换的脚本（SQLScript/SQLUpdateScript 实证） | 无 | 未被替换的 `#xxx#`/`@xxx@` 一律替换为空白（`GlobalFormula.vb:708-713`） | TAMPERFB BH#10/BL#10 SQLUpdateScript 首部 |
| `--LINKSCRIPTGET@连接代码:` | SQLScript/SQLRemove | **`@连接代码` + `:`**，脚本体到独立一行 `#` 结束 | 在指定连接的数据库上执行内嵌脚本并返回结果值（`MLTShared.vb:3164` `GetScriptValue`：`LINKSCRIPTRUN@连接代码:脚本` 执行不返回 / `LINKSCRIPTGET@连接代码:脚本` 返回单值）。**连接代码因环境而异（样例为 `TMESERAQA`），生成时必须问用户** | ERAQA101010X#1000:61-66 |

## 脚本返回值中的结果标记（非 `--` 注释）

写在 SQL 返回字符串（`N'...'`）开头，运行器据此拦截/确认：

| 标记 | 语义 | 样例证据 |
|------|------|---------|
| `LINKPREVENT:消息` | 阻止操作并提示 | ERAQA101010X#1000（删除检查）、501X#1000、502X#1000 |
| `LINKCONFIRM:消息` | 弹确认框，用户确认后继续 | ERAQA101010X501X#1000（Copy 数据检查） |
| 输出列 `LINKFUNCTIONLIST` | APP 动作可用性控制：值为 `.` 分隔动作令牌（如 `.PREPROCESS.501` 允许预处理触发 50x 模型）；#301（MyRowData 段）整脚本一句 `SELECT '.PREPROCESS.501' AS LINKFUNCTIONLIST` | TAMPERAPP TMESPDA13010X#301:10 |

配套用法：主动作模型（如 #501 Copy）配一个「数据检查模型」（`主代码501X#1000`），SQLScript 用 `--LINKSCRIPTGET@源:` + CASE WHEN 返回 `LINKPREVENT`/`LINKCONFIRM`/空串。

## 脚本字段取值层指令

- `LINKDATAMINE~30`：整个 SQLScript 只写这一行——指定数据挖掘行号（数据挖掘导出入口模型，如 ERAQA101010X#0）。经 `FunctionSplit` 分割，**生成时用 `~<!>~`：`LINKDATAMINE~<!>~30`**。

## 完整词表（源码侧，样例未出现）

以下标记在 `SysDataModel.vb` 有解析逻辑但本批样例未用到，需要时先读对应行号源码再决定是否使用，不要臆造参数格式（2026-11-05 已移入下节详表的：AUTHORIZE、DATAAUTOSAVE、NOEXPORT、SHOWPROCESS）：
`--LINKADDNEWROWTOP`(L1106-1111)、`--LINKGANTTVIEW`(L1197)、`--LINKCALENDARVIEW`(L1199)、`--LINKLOGICALDAY=`(L1201)、`--LINKPIVOTGRID`(L1210)、`--LINKWAITTASKDONE`(L1458)、`--LINKCALLFUNCTION`(L1685)、`--LINKSHOWEXCEPTION`(L1688)、`--LINKUPDATESCRIPT`(L1721)、`--LINKDATATRANSPOSITION`(L2095)、`--LINKDETAILLIST(...)`(L4642)、`--LINKBACKFUNC:`(L6431)、`--LINKWINDOWMODE`(L11401)、`--LINKDATAMINE~`(MLTGridEvent.vb:30)。

## 2026-11-05 运行器会话补充（TotalLINKDEV.html 差异校验，25 项源码核实）

> 环境标签：LINKIIS 工程直接引用 BaseLib（LINKIIS.csproj:1237），引擎解析的标记随模型响应（modelFlags/ModelSetting JSON）下发，但 UI 行为是否实现取决于前端。[仅运行器] = WinForms 客户端直读脚本文本/网格属性，H5 无对应消费；[跨环境] = 引擎级，IIS 链路同样生效。常量统一定义于 `Globle.vb:392-432`。

### 编辑 / 保存

| 标记 | 语义（源码核实） | 解析/消费 | 环境 |
|---|---|---|---|
| `--LINKCELLVALID` | 编辑时单元格合法性校验 | SysDataModel.vb:1066（BaseScript）→ MLTUGridDetail.vb:6878 `.CellValidate` | 跨环境 |
| `--LINKROWVALID` | 行保存/离开行时校验，不通过不许离开当前行 | SysDataModel.vb:1069 → MLTUGridDetail.vb:6879 `.RowValidate` | 跨环境 |
| `--LINKKEEPORIGINAL` | 脚本中的公式不被替换（纯引擎行为，无 UI） | GlobalFormula.vb:112、116-119 | 服务端引擎 |
| `--LINKBATCHEDIT` | 批量编辑：AddNew 模板行头部填写后批量应用到多行 | SysDataModel.vb:1078 → fDataAnalysis.vb:2383、MLTUGridDetail.vb:4412/6604 | 跨环境 |
| `--LINKDATAAUTOSAVE` | 离开时自动保存（不弹确认） | SysDataModel.vb:1075（字段 ：334） | 跨环境 |
| `--DISABLEAUTOSAVE` | 既不自动保存**也不弹确认**（2026-07-21 新增；三者优先级：DATAAUTOSAVE > DISABLEAUTOSAVE > 默认弹确认） | Globle.vb:406、SysDataModel.vb:1075 → MLTUGridDetail.vb:7244-7250 | 跨环境 |
| `--LINKROWDOUBLECLICK` | 行双击触发当前行编辑 | 客户端字面量直读：MLTUGridDetail.vb:4358/7327（**无引擎解析点**） | 仅运行器 |
| `--LINKROWENTERACTION` | 非编辑态回车触发当前行编辑（与 LINKSAVEONENTERKEY 互斥判断） | 客户端字面量直读：MLTUGridDetail.vb:7135（**无引擎解析点**） | 仅运行器 |
| `--LINKAUTOCLOSE` | 弹窗保存成功后自动关窗 | fDataAnalysis.vb:4068；ModelSetting 名 `AutoClose`（SysDataModel3.vb:545） | 服务端+客户端 |
| `--LINKCOPYLINE` | 添加记录时复制上一行内容 | SysDataModel.vb:1060（CreateScript）→ MLTUGridDetail.vb:6880 | 跨环境 |
| `--LINKINPUTBOX` | 显示多行输入框（扫码枪连续输入） | SysDataModel.vb:1057 → fDataAnalysis.vb:2451-2454 `txtInputBox.Visible` | 跨环境 |
| `--DISABLEINPUTIMEMODE` | 仅作用于 InputBox 禁用输入法 | SysDataModel.vb:1084 → fDataAnalysis.vb:2388-2392 | 跨环境 |

### 显示

| 标记 | 语义 | 解析/消费 | 环境 |
|---|---|---|---|
| `--LINKNOFILTER` | 整表禁用数据过滤行 | MLTUGridDetail.vb:1669 `InitGridStyle` `AllowFiltering=False`；ModelSetting 名 `LinkNoFilter` | 仅运行器 |
| `--LINKNOSUBFILTER` | 多层 band 非首层禁用过滤 | MLTUGridDetail.vb:1676-1680 | 仅运行器 |
| `--LINKTOPBANDHEADERONLY` | 多层 band 非首层隐藏列标题 | MLTUGridDetail.vb:1681-1685 | 仅运行器 |
| `--LINKNOEXPORT` | 禁用网格导出（仅 UI 单点，数据照发，服务端无防护） | SysDataModel.vb:1217 → fDataAnalysis.vb:2405 | 仅运行器 |
| `--LINKSHOWPROCESS` | 弹进度仪表窗（需 `BASE_PROGRESSGAUGE_ENABLE`，默认 False，否则标记无效） | Globle.vb:223 + SysDataModel.vb:1686 等 → MLTShared2.vb:3283（fLinkProcess 窗体） | 仅运行器 |
| `--LINKSHOWACTION` | 302 附加模型执行后显示进度 | SysDataModel3.vb:700 + fDataAnalysis.vb:3719/3954 | 仅运行器 |

### 数据处理 / 上传

| 标记 | 语义 | 解析/消费 | 环境 |
|---|---|---|---|
| `--LINKJSONDATASUBMIT` | 变更行（或过滤内行）打包 JToken 整体提交，跳过逐行 TreatEachRow；脚本用 `#LINKJSON{$}#` 注入 + `OPENJSON/MERGE`；设计器菜单可生成脚本骨架 | fDataAnalysis.vb:4106/4306 → SysDataModel2.vb:2327 `MoreDataSubmit` → SysDataModel.vb:6041；骨架生成 fDataModel.vb:1657-1689 | 跨环境（IIS linkDMDataSubmit 同走 MoreDataSubmit） |
| `--LINKMULTIROWS` | 附加模型逐行处理：默认只处理选中/活动行（GetRowDataWSummary），有标记时 RDs 全部行逐行/逐组执行；**与 condition 不能共用**（Globle.vb:420-425 注释） | SysDataModel.vb:1087、1616 `ScriptExecWithRows` | 跨环境 |
| `--LINKUPLOAD_FILETYPE:类型` | 上传文件无扩展名时指定后缀（默认 jpg）；可被行列 `UploadFileType` 覆盖；IIS 端点另有硬编码白/黑名单先拦截 | SysDataModel2.vb:1798-1805、1876-1881 | 跨环境 |
| `--LINKUPLOAD_PATHASSIGN:路径` | 指定保存路径；空则自动 `yyyy\MMdd\HHmmssfff` 相对路径；**路径未做规范化校验**（目录遍历风险） | SysDataModel2.vb:1807-1813、1919-1961 | 跨环境 |
| `--LINKUPLOAD_KEEPFILENAME:1` | **要求带参数**（非空=保持原文件名；HTML 无参写法有误）；空=`用户_Ticks_原名` 防覆盖 | SysDataModel2.vb:1815-1822、1897-1908 | 跨环境 |
| `--LINKAUTHORIZE` | 无需登录：Token 校验失败时兜底放行 + 合成身份 TotalLINK + 清空 AccessList 跳过权限（不绕过 MD5 模型校验）；IIS 所有基于 SysDataModel 的端点都尊重 | SysDataModel.vb:569-592 | 跨环境/服务端 |

### 任务 / 基础设施

| 标记 | 语义 | 解析/消费 | 环境 |
|---|---|---|---|
| `--LINKSERVERTASK.任务ID` | **必须带 `.任务ID`**（HTML 漏写）：运行器 HTTP POST 到 LINKIIS `linkDMScriptExec` 即时执行同一脚本（5 秒超时不等待），KeyVal 表记状态防重入；**不落 LinkTasks 任务表** | SysDataModel2.vb:2192-2210 → SysDataModel.vb:1478-1516 → MLTServerTask.vb:18-58 → DataModelController.cs:3019 | 跨环境（运行器→IIS） |
| `--LINKACTIONPUSH(优先级~JobKey~操作用户~模型代码,编号~参数…)` | CALLFUNCTION 命令（带括号参数）：INSERT LINKACTIONPOOL 持久化任务队列，LinkTasks Quartz 消费执行后转 His | CallFunction.vb:194、549-552 → MLTShared2.vb:4410-4441 → LinkTasks.cs:805-808 | 服务端 |
| `--LINKTIMEOUT:秒数` | DbCommand.CommandTimeout（0=默认 10 秒）；ModelSetting 名 `Timeout` | MLTShared2.vb:3515-3525 → MLTData.vb:130-138 | 跨环境 |
| `--LINKCONN@连接代码` | 该脚本改用指定连接执行（连接代码本身可含占位符；EXCEL 等特殊连接分派专用通道）；ModelSetting 名 `LinkConn` | MLTShared2.vb:3534-3546 → SysDataModel.vb:1704/1913/2103 | 跨环境 |

### 勘误（HTML 手册 vs 源码）

1. **`--LINKIDACTION` 不是控制标记**：全仓库无解析点（唯一出现是 MLTShared2.vb:4344 的 SQL 注释）。动作序列号的真实载体是运行时 GUID `DM.LinkIdAction` + 占位符 `#LINKID_ACTION#` + LINKACTIONINFO 表（MLTShared2.vb:4328-4344）。往脚本里写 `--LINKIDACTION` 无任何效果。
2. `--LINKSERVERTASK` 必须带 `.任务ID` 后缀。
3. `--LINKUPLOAD_KEEPFILENAME` 必须带 `:1` 类参数。
4. `--LINKACTIONPUSH` 是 CALLFUNCTION 命令，带括号参数，非无参标记。
5. `#LINKRSAENCRYPT(明文,公钥)#` 为双参（HTML 单参写法有误），见 `placeholders.md` 2026-11-05 节。

## 使用原则

1. 带参数标记的格式差异很大（`:` / `,` / `@...:`），**只用本表实证过的写法**。
2. 宁可少用标记；不确定就查源码行号或问用户。
