# 模型要素 → 桌面运行器行为映射

> 回答「这样设计模型，用户在运行器里会看到什么」。按标记查语法用 `link-flags.md`，按占位符查用 `placeholders.md`；本文按**设计意图**查行为。
> 权威来源：`LINK/` 仓库源码（2026-11-05 核实，file:line 锚定）。环境标签：`[运行器]` = WinForms 客户端行为；`[跨环境]` = 引擎级、IIS 链路同样生效。

## 0. 先记住：一套引擎，多种前端

BaseLib 引擎（SysDataModel*/GlobalFormula）同时运行于运行器客户端与 LINKIIS 服务端（LINKIIS.csproj 直接引用 BaseLib.vbproj）。标记解析在引擎，**UI 行为实现在各前端**：

- `--LINK*` 标记 → 引擎解析进 FlagsInfo/ModelSetting JSON 下发 → WinForms 控件消费（`MLTUGridDetail`/`fDataAnalysis`）；
- 两个例外是**纯客户端字面量直读**（引擎不认识、不进 modelFlags）：`--LINKROWDOUBLECLICK`、`--LINKROWENTERACTION`（MLTUGridDetail.vb:4358/7135）。LINK.Core 移植时也未收录这两个——新前端要复刻需自行补。

## 1. 打开模型：加载与表格初始形态 [运行器]

数据加载后 `InitGridStyle()`（MLTUGridDetail.vb:1661-1686）按脚本标记决定表格初始形态：

| 用户看到 | 由什么决定 |
|---|---|
| 打开即出数据，还是先点查询 | `--LINKLOADDATAIMMEDIATE`（立即加载） |
| 有没有过滤行 | 默认有；`--LINKNOFILTER` 整表隐藏（:1669） |
| 多层数据：子层有没有过滤行/列标题 | `--LINKNOSUBFILTER`（:1676）、`--LINKTOPBANDHEADERONLY`（:1681） |
| 能不能导出 | 默认能；`--LINKNOEXPORT` 禁用导出按钮（fDataAnalysis.vb:2405；仅 UI，数据照发） |
| 列宽 | ModelSetting `ColumnWidth`（用户未保存布局时） |

## 2. 编辑链路：三种形态 [运行器]

| 形态 | 触发 | 标记组合 |
|---|---|---|
| **弹窗编辑**（默认） | 双击行弹编辑窗 | 无标记；`--LINKAUTOCLOSE` 保存后自动关窗（fDataAnalysis.vb:4068） |
| **行内编辑** | 查询后网格直接进编辑态并保持 | `--LINKEDITMODE` |
| **直接加行** | 表格里常驻添加行 | `--LINKADDNEWROWS`；`--LINKCOPYLINE` 加行时复制上一行 |

编辑态的行为开关：

- **必填**：`--LINKREQUIRED:列1,列2`（冒号+逗号分隔列名）。
- **校验门槛**：`--LINKCELLVALID` 单元格级（编辑时校验）、`--LINKROWVALID` 行级（不通过不许离开当前行）。
- **下拉/联动**：列别名前缀 `LINKDROPVALID/LINKDROPDOWN/LINKLIST/LOAD*` + ModelSetting `EditValueList`（加载时机由前缀决定，见 modelsetting.md）。
- **批量填写**：`--LINKBATCHEDIT` 头部模板行填一次批量应用多行（MLTUGridDetail.vb:4412/6604）。
- **回车语义**：编辑态 `--LINKSAVEONENTERKEY` 回车即保存；非编辑态 `--LINKROWENTERACTION` 回车触发当前行编辑（两者互斥判断，:7135）。
- **离开网格时的保存策略**（MLTUGridDetail.vb:7244-7250，优先级从高到低）：`--LINKDATAAUTOSAVE` 直接自动保存 → `--DISABLEAUTOSAVE` 既不保存也不弹确认 → 默认弹 `Question(msg.QSave)` 确认框。
- **扫码入口**：`--LINKINPUTBOX` 显示多行输入框（扫码枪连续输入）；`--DISABLEINPUTIMEMODE` 只对该输入框禁输入法。

## 3. 数据处理链路 [跨环境]

| 设计意图 | 机制 |
|---|---|
| 整批提交变更行（JSON 一次处理） | `--LINKJSONDATASUBMIT` + 脚本 `#LINKJSON{$}#` + `OPENJSON/MERGE`；跳过逐行 TreatEachRow（SysDataModel2.vb:2327 → SysDataModel.vb:6041）。设计器菜单可生成骨架（fDataModel.vb:1657-1689） |
| 附加模型逐行处理 | `--LINKMULTIROWS`：默认只处理选中/活动行（GetRowDataWSummary），有标记则 RDs 全部行逐行/逐组执行（SysDataModel.vb:1616）；**与 condition 不能共用** |
| 存储过程回传结果 | `--LINKEXECOUTPUT`：EXEC OUTPUT 后 `SELECT @RPTSTA,@RPTMSG` 回传 |
| 换连接/控超时 | `--LINKCONN@连接代码`（连接代码本身可含占位符）、`--LINKTIMEOUT:秒数` |

## 4. 动作/防呆链路

- 防呆三件套（脚本返回字符串开头）：`LINKPREVENT:` 阻止、`LINKCONFIRM:` 确认后继续、`LINKWARNING:` 提示——模型侧配 `主代码501X#1000` 检查模型。
- **两种服务端任务机制，别混用**：
  - `--LINKSERVERTASK.任务ID`：运行器 HTTP POST 到 IIS `linkDMScriptExec` **即时执行**，不等待、KeyVal 记状态防重入，**不落任务表**（SysDataModel.vb:1478-1516）；
  - `--LINKACTIONPUSH(优先级~JobKey~操作用户~模型,编号~参数)`：CALLFUNCTION 命令，INSERT LINKACTIONPOOL **持久化队列**，LinkTasks Quartz 消费（MLTShared2.vb:4410-4441）。
- 进度反馈 [仅运行器]：`--LINKSHOWPROCESS` 弹仪表窗（需 `BASE_PROGRESSGAUGE_ENABLE` 开关，默认 False）；`--LINKSHOWACTION` 用于 302 附加模型。
- 完成后：`--LINKREFRESH` 刷新原模型（附加模型脚本）。
- `--LINKAUTHORIZE`：免登录执行，IIS 所有 SysDataModel 端点尊重；合成身份 TotalLINK + 跳过权限（SysDataModel.vb:569-592）。

## 5. 上传链路 [跨环境]

`--LINKUPLOAD_FILETYPE:类型`（无扩展名兜底，默认 jpg）、`--LINKUPLOAD_PATHASSIGN:路径`（空则自动 `yyyy\MMdd\HHmmssfff`）、`--LINKUPLOAD_KEEPFILENAME:1`（**必须带参**，非空=保留原名；空=`用户_Ticks_原名` 防覆盖）。解析在 SysDataModel2.FileUpload（:1793 起），IIS `linkDMFileUpload` 同样生效，但端点自身有硬编码扩展名白/黑名单先拦截。

## 6. 脚本执行引擎行为 [跨环境]

| 设计意图 | 机制 |
|---|---|
| 脚本里的公式/占位符不被替换（原样交给下游） | `--LINKKEEPORIGINAL`（GlobalFormula.vb:112） |
| 未替换的 `#列#`/`@列@` 清空成空白 | `--LINKAUTOREPLACEEMPTYCOLUMNS`（GlobalFormula.vb:708-713） |
| 免登录模型（扫码回传/IoT 回调等） | `--LINKAUTHORIZE` |
| 无界面取数 | `#TotalLINKScript.#`（TOTALLINKSCRIPT 固定模型）、`#LINKLEVELDATA(...)#`/`#LINKXMLDATA(...)#`（实例化其他模型取多层 JSON/XML） |

## 7. 运行器专属能力（设计 APP/FB 模型时不要用）

以下标记/能力**只在 WinForms 运行器生效**，APP/FB 链路无消费代码（部分会随 modelFlags 下发但被忽略）：过滤行/列标题控制（NOFILTER/NOSUBFILTER/TOPBANDHEADERONLY）、导出开关（NOEXPORT）、进度窗（SHOWPROCESS/SHOWACTION）、行双击/回车编辑（ROWDOUBLECLICK/ROWENTERACTION，纯客户端直读）、批量编辑（BATCHEDIT）、甘特/日历/透视（GANTTVIEW/CALENDARVIEW/PIVOTGRID，未逐项核实但同为 Infragistics 网格属性）。给 APP 的模型里写这些是**无效载荷**——不报错，但也不起作用。

## 设计规律（能力组轴 × 四元组）

> 每条规律 = 设计意图 / 推荐形态 / 运行器依据（file:line）/ 反模式。与 `discovery.md` 问卷能力组同构。

### ① 列表/查询

- **设计意图**：用户要看什么、筛什么、能不能带走数据。
- **推荐形态**：查询展示型按需关掉交互负担——过滤行用 `--LINKNOFILTER`、导出用 `--LINKNOEXPORT`；打开即出数用 `--LINKLOADDATAIMMEDIATE`（大结果集导出类）。多层数据默认给子层留过滤行，纯展示用 `--LINKNOSUBFILTER`/`--LINKTOPBANDHEADERONLY`。
- **运行器依据**：`InitGridStyle` MLTUGridDetail.vb:1661-1686；AllowExport fDataAnalysis.vb:2405。
- **反模式**：给 APP/FB 模型写这些标记（无效载荷，§7）；查询列写中文别名（validate 报 `SQL_ALIAS_LEGACY`）。

### ③ 编辑

- **设计意图**：改动频率 × 单次改动范围，决定编辑形态。
- **推荐形态**：高频小改（状态、数量）→ `--LINKEDITMODE` 行内常驻编辑；低频整单维护 → 默认弹窗 + `--LINKAUTOCLOSE` 保存后关窗；流水录入 → `--LINKADDNEWROWS`（+`--LINKCOPYLINE` 复制上一行）；一次填头行刷多行 → `--LINKBATCHEDIT`。
- **运行器依据**：弹窗关窗 fDataAnalysis.vb:4068；模板行批量 MLTUGridDetail.vb:4412/6604；离开保存策略三档 MLTUGridDetail.vb:7244-7250。
- **反模式**：编辑列没进 `EditCols`（回退解析 SET 子句，SysDataModel.vb:5909——列名对不上**静默不可编辑**）；`--LINKREQUIRED` 写成空格分隔或漏冒号（参数格式是 `:列1,列2`）；离开保存策略三档标记叠加时忘了优先级是 DATAAUTOSAVE > DISABLEAUTOSAVE > 默认弹确认。

### ④ 新增

- **设计意图**：新行默认值从哪来。
- **推荐形态**：默认值用参数占位 `{N}`、`#LOGIN_USER#`、`GETDATE()`；逐列新值用 `@列名@` 新行占位（配 ADDNEWROWS/LINKEDITMODE）。
- **运行器依据**：CopyLine MLTUGridDetail.vb:6880。
- **反模式**：新行默认值用行级 `#列名#`（新行没有行上下文，替换不出值）。

### ⑤ 动作/防呆

- **设计意图**：动作要不要拦、要不要异步、完成后去哪。
- **推荐形态**：同步防呆 → `501X#1000` 检查模型返回 `LINKPREVENT:/LINKCONFIRM:`；异步 → 按语义二选一：**即时触发不等待**用 `--LINKSERVERTASK.任务ID`（HTTP 发出即返回，KeyVal 防重入，不落任务表），**持久队列**用 `--LINKACTIONPUSH(...)`（LINKACTIONPOOL → LinkTasks 消费）；完成后回原界面用 `--LINKREFRESH`。
- **运行器依据**：SysDataModel.vb:1478-1516；MLTShared2.vb:4410-4441。
- **反模式**：把 `--LINKIDACTION` 当标记写（无解析点，无效果；动作号是 `#LINKID_ACTION#`）；期望 SERVERTASK 留下可查的任务记录（它不落任务表）；`--LINKMULTIROWS` 与 condition 共用（Globle.vb:420-425 明确禁止）。

### ⑦ 图表/挖掘/多层级

- **设计意图**：图表/树的数据从哪取。
- **推荐形态**：图表 dataset 直接 `##LINKECHARTDATASET##`（当前模型网格数据）；任意脚本取其他模型的层级数据用 `#LINKLEVELDATA(模型,编号)#`（空返回有 `"[]"` 兜底）——**优先于 XML 形态**。
- **运行器依据**：SysDataModel.vb:6845-6849、6852-6856；GlobalFormula.vb:615-651 vs 654-685。
- **反模式**：`#LINKXMLDATA(...)#` 用于可能空返回的模型（**无 Nothing 兜底**，替换为空串或异常）；`--LINKSHOWPROCESS` 以为加了就有进度窗（还需服务端 `BASE_PROGRESSGAUGE_ENABLE=True`，默认 False）。

### 通用

- **跨脚本复用**：一段逻辑多处用 → `#LINKFUNC.名称#`（LINKFUNC 表，FUNTYPE 三类）；跨脚本传值 → `#LINKSETVAL/GETVAL#`（进程内存字典）。
- **反模式**：IIS 链路把 SETVAL/GETVAL 当「会话变量」存敏感状态（应用池级跨请求共享，仅靠 LoginID 区分、无锁）；`#LINKFUNC.` 参数里带逗号（会被 `Split(",")` 切错）；`#LINKTOKEN(用户)#` 用于常规业务（不校验调用者权限，且为他人造的 Token 按天滚动，隔天失效）。
