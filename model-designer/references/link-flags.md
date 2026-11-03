# 脚本注释标记（--LINKxxx）与结果标记

> 权威来源：`BaseLib/DataModel/SysDataModel.vb`（解析处）+ 21 个真实样例。样例证据 + 源码行号双重锚定。

## 样例实证的标记（优先使用）

写在脚本字段**首行注释**（`--` 开头），运行时按行解析：

| 标记 | 所在字段 | 参数格式 | 语义 | 样例证据 |
|------|---------|---------|------|---------|
| `--LINKSAVEONENTERKEY` | SQLUpdateScript | 无 | 回车即保存 | ERAQA1005#10:21 等 7 处 |
| `--LINKEDITMODE` | SQLUpdateScript | 无 | 启用行编辑 | ERAQA1005#10:22 等 6 处 |
| `--LINKREQUIRED:列1,列2` | SQLUpdateScript | **冒号 + 逗号分隔列名** | 必填校验 | ERAQA1005#10:23 |
| `--LINKADDNEWROWS` | SQLNew | 无 | 启用新增行 | ERAQA1005#10:73 等 5 处 |
| `--LINKNOGROUP` | SQLScript | 无 | 禁止分组 | ERAQA101010X#700:10 |
| `--LINKDATAMINELAYOUT:55,45` | SQLScript | **冒号 + 逗号数值** | 挖掘布局比例 | ERAQA1010#10:10 |
| `--LINKLOADDATAIMMEDIATE` | SQLScript | 无 | 立即加载数据（导出类大查询） | ERAQA1010#20:10 |
| `--LINKDATAMINEOVERVIEW,VERTICAL,60,AUTOREFRESH` | SQLScript | **逗号分隔多参数** | 挖掘总览（方向/比例/自动刷新） | ERAQA1020#10:10 |
| `--LINKREFRESH` | SQLClear | 无 | 动作执行后刷新 | ERAQA101010X#21:62 等 6 处 |
| `--LINKSCRIPTGET@连接代码:` | SQLScript/SQLRemove | **`@连接代码` + `:`**，脚本体到独立一行 `#` 结束 | 在指定连接的数据库上执行内嵌脚本并返回结果值（`MLTShared.vb:3164` `GetScriptValue`：`LINKSCRIPTRUN@连接代码:脚本` 执行不返回 / `LINKSCRIPTGET@连接代码:脚本` 返回单值）。**连接代码因环境而异（样例为 `TMESERAQA`），生成时必须问用户** | ERAQA101010X#1000:61-66 |

## 脚本返回值中的结果标记（非 `--` 注释）

写在 SQL 返回字符串（`N'...'`）开头，运行器据此拦截/确认：

| 标记 | 语义 | 样例证据 |
|------|------|---------|
| `LINKPREVENT:消息` | 阻止操作并提示 | ERAQA101010X#1000（删除检查）、501X#1000、502X#1000 |
| `LINKCONFIRM:消息` | 弹确认框，用户确认后继续 | ERAQA101010X501X#1000（Copy 数据检查） |

配套用法：主动作模型（如 #501 Copy）配一个「数据检查模型」（`主代码501X#1000`），SQLScript 用 `--LINKSCRIPTGET@源:` + CASE WHEN 返回 `LINKPREVENT`/`LINKCONFIRM`/空串。

## 脚本字段取值层指令

- `LINKDATAMINE~30`：整个 SQLScript 只写这一行——指定数据挖掘行号（数据挖掘导出入口模型，如 ERAQA101010X#0）。经 `FunctionSplit` 分割，**生成时用 `~<!>~`：`LINKDATAMINE~<!>~30`**。

## 完整词表（源码侧，样例未出现）

以下标记在 `SysDataModel.vb` 有解析逻辑但本批样例未用到，需要时先读对应行号源码再决定是否使用，不要臆造参数格式：
`--LINKAUTHORIZE`(L576)、`--LINKDATAAUTOSAVE`(L328)、`--LINKADDNEWROWTOP`(L1106-1111)、`--LINKGANTTVIEW`(L1197)、`--LINKCALENDARVIEW`(L1199)、`--LINKLOGICALDAY=`(L1201)、`--LINKPIVOTGRID`(L1210)、`--LINKNOEXPORT`(L1217)、`--LINKWAITTASKDONE`(L1458)、`--LINKCALLFUNCTION`(L1685)、`--LINKSHOWPROCESS`(L1686)、`--LINKSHOWEXCEPTION`(L1688)、`--LINKUPDATESCRIPT`(L1721)、`--LINKDATATRANSPOSITION`(L2095)、`--LINKDETAILLIST(...)`(L4642)、`--LINKBACKFUNC:`(L6431)、`--LINKWINDOWMODE`(L11401)、`--LINKMYROWDATA`(SysDataModel3.vb:34)、`--LINKDATAMINE~`(MLTGridEvent.vb:30)。

## 使用原则

1. 带参数标记的格式差异很大（`:` / `,` / `@...:`），**只用本表实证过的写法**。
2. 宁可少用标记；不确定就查源码行号或问用户。
