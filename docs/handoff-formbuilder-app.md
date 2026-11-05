# 交接文档：Formbuilder / APP 源码分析会话

> 交接自 2026-11-05 桌面运行器会话。目标读者：接手 Formbuilder 平台源码分析、TotalLINK APP 源码分析的两个后续会话（用户将提供**混淆前源码**）。

## 1. 本会话（运行器）已完成什么

按「源码 ↔ skill 对应」方法论完成了桌面运行器的全量核对，改动清单：

| 文件 | 改动 |
|---|---|
| `model-designer/references/placeholders.md` | +「2026-11-05 运行器会话补充」：A~F 组占位符（上下文/日期/数据集/变量/加密/集成）带行号收编；关闭 4 个存量【待核对】 |
| `model-designer/references/link-flags.md` | +G 组 25 项控制脚本四栏表（语义/解析消费/环境标签）+ HTML 勘误节 |
| `model-designer/references/runner-behavior.md` | **新建**：模型要素 → 运行器行为映射（7 节）+ 设计规律（能力组四元组） |
| `model-designer/references/discovery.md` | L2-3/4/9 补行为维度；新增 L2-R1~R4 运行器专属题；阶段 0 目标环境改多选；任务书 §6 加「关键交互行为开关」行 |
| `model-designer/SKILL.md` | 必读文档表接入 runner-behavior.md |
| `LINK 仓库 LINK/LINK/Note/TotalLINKDEV.html` | 勘误：`--LINKSERVERTASK.任务ID`、`--LINKUPLOAD_KEEPFILENAME:1`、RSA 双参、删除 `--LINKIDACTION` 行、计数 48→47 |

## 2. 后续会话的既定决策（不要重新讨论）

1. **范围切分**：运行器（已完成）→ Formbuilder → APP，三个会话各自收口；FB 与 APP 共用 linkDM* 端点，问卷按「能力组」组织（已有共识，见 model-designer SKILL.md）。
2. **环境作第二过滤维度**：行为条目带 `[运行器]/[APP]/[FB]/[通用]` 标签，问卷 L2 题按阶段 0 目标环境过滤（discovery.md 已接线）。后续会话的职责是把 `runner-behavior.md` §7 列的「运行器专属」清单反向补全——即确认 APP/FB 端**各自**消费哪些标记/字段。
3. **FB 模板设计规律本次只记待验项**（D7 拍板）：混淆前源码到位后才验证 formtemplate（MODJSON）生成/解析链路，不要把推断写成结论。

## 3. 可复用的方法论（运行器会话验证有效）

1. **三方比对**：官方文档（TotalLINKDEV.html）↔ skill 已有知识 ↔ 语料实际用法（grep samples-corpus 统计频率），分出「已覆盖/增量/冲突」三档。
2. **分组拍板**：把待校验项按主题分组交给用户逐组决策（低频/弃用的项用户会直接指出，避免白查）。
3. **并行子代理源码校验**：每个子代理负责一组，产出带 file:line 的校验笔记；主会话**复核行号**后写入（尤其反直觉结论必须亲自验证——本会话子代理曾全对，但主会话自己出过一次误报，见 §5）。
4. **写入格式**：每条带 file:line；词表条目带「环境标签」；对官方文档的出入单独开「勘误」节而不是默默改。
5. **问卷融合滞后于校验**：先把词表/行为文档写完给用户过目（检查点），再动问卷——避免凭未校验的原文写进问卷。

## 4. 待验项清单（新会话的第一批任务素材）

### 4a. Formbuilder 会话

- `formtemplate`（MODJSON）的生成与解析链路：设计器如何产出、运行时如何渲染、按钮 `action.api 0~8` 与端点的真实对应（现有知识在 `formbuilder-json-generator/`，多为语料反推）。
- formSetting JSON 的完整键表：现有 `fb-page-families.md` 记录了 formbtns 恒空、formData `#FORMDATA#` 字面量等规律，需从前端源码确认为什么/是否强制。
- FB 端对 `--LINK*` 标记的消费：`runner-behavior.md` §7 清单里哪些在 FB 有对应行为（引擎 modelFlags 随响应下发，但前端读不读未知）。
- 500 模型的 `CubeSetting`（表结构派生元数据）在前端的实际用途。

### 4b. APP 会话

- APP 壳对 modelFlags/H5 族字段的消费矩阵：现有 `totallink-app-help/`（h5-guide/classes-ids/attributes）来自运行观察，需源码确认。
- JS 钩子签名与中断语义：`references/js-hooks.md` 列了 8 个钩子（scan_para/beforeFunction 返回 true 中断/afterFunction 等），源码核实签名与执行时机。
- `--LINKROWDOUBLECLICK`/`--LINKROWENTERACTION` 是**纯客户端字面量直读**（不进 modelFlags、不在 LINK.Core 移植清单）——APP 端如有对应交互，机制完全不同，别按运行器语义迁移。
- 编号段语义（#110/#301/15xx/#700 双语义）在 APP 壳里的路由依据（现有结论来自 TAMPERAPP 语料，见 `discovery.md`「编号段语义补充」）。

### 4c. 两会话共通

- F 组直收未核对占位符：`#LINKIOT.#`、`#LINKINFLUX()#`、`#LINKACTIVITY()#`、`#LINKSIGNSTEPSETTING()#`、`#LINKLOCATION*#`、`#LINKLOCALPATH#`、`#LOCALREPORTPATH#`、`#LINKEXPORTPATH#`（placeholders.md 标注【未核对】）。
- E 组未核对：4 个第三方 AI Token 占位符（`#LINKWEIXINTOKEN#` 等）。
- `--LINKGANTTVIEW/CALENDARVIEW/PIVOTGRID/DETAILLIST/BACKFUNC/WAITTASKDONE/CALLFUNCTION/SHOWEXCEPTION/UPDATESCRIPT/DATATRANSPOSITION/ADDNEWROWTOP/WINDOWMODE` 仍在 link-flags.md 词表（只有行号，未核实消费端）。

## 5. 源码获取清单（向用户索取）

- **Formbuilder 混淆前源码**（前端工程 + 设计器）。
- **TotalLINK APP 混淆前源码**（APP 壳/h5 容器）。
- 已在仓库的参照：`/Users/liuyongchao/Documents/GitHub/LINK`（BaseLib 引擎 + LINKIIS 服务端 + LINK/Note/TotalLINKDEV.html 官方手册，注意 LINKIIS.csproj 直接引用 BaseLib.vbproj——引擎解析是共享的，前端消费才是各会话重点）。

## 6. 本会话的教训（少走弯路）

- 官方手册也可能错，但**先怀疑自己的阅读**：本会话曾误报手册把 `#LINKDB#` 写成双井号（原文即单井号），复核原文后才修正——所有「勘误」结论必须贴原文行号。
- 反直觉结论必须主会话亲自 grep 复核（如 `--LINKIDACTION` 无解析点这类「删文档条目」级结论）。
- 语料零命中 ≠ 弃用：是否弃用只有用户能拍板，直收项明确标【未核对】保留追溯线。
