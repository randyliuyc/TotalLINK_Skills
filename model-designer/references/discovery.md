# 需求问卷与模型任务书（discovery）

> 问卷的作用是**澄清需求**，不是收集配置。环境值（编号/连接/语言）沿用 SKILL.md 硬规则 1、2，不在问卷里重复问。
> 访谈纪律与门禁见文末。事实优先：能查到的（表字典、存量模型、`tools search`）不问用户。

## 门禁（硬规则）

1. **生成 XML 之前必须先落盘任务书**（`<ModelCode>#<ModelNum>-brief.md`），并得到用户确认。
2. 任务书未确认前，只允许做事实调查（字典查询、样例检索），不允许生成任何 XML。
3. 任务书即验收清单：交付时逐条核对（可执行断言 agent 跑，人工断言列给用户）。

## 访谈纪律（grilling 原则）

> 本节是 `model-interview` Skill（grilling 纪律）在模型设计场景的落地；完整纪律见该 Skill。

- **一次只问一个问题**，等回答再继续；每个问题附上你的推荐答案。
- 能通过环境查到的**事实**（列结构、已有模型、工具能力）直接查，不问；**决策**（要不要这个功能、叫什么、给谁用）逐个交给用户。
- 沿能力组逐个过，上一组的答案决定下一组问不问（能力组没命中就整组跳过）。
- 用户回答含糊时追问，直到该题的"完成判据"满足才进入下一题。

## 阶段 0：能力组判定（第一轮访谈）

先问目标，从答案圈定能力组（能力组定义见 `endpoints.md` 总表），后续只问命中组的问题：

| 问 | 命中能力组 | 产出的模型族构成 |
|---|---|---|
| 这个模型给谁用？（模型运行器 / APP / FB 网页 / AI 调用） | — | 决定 H5 族字段是否必做 |
| 用户在界面上要做什么？（查列表 / 看单据表单 / 编辑 / 新增 / 删除 / 行动作 / 前后置处理 / 打印 / 图表 / 挖掘 / 多级展开） | ①~⑦ | 主模型 + 附加模型编号段清单 |
| 数据是一个列表还是一张单据？ | ① vs ② | 列表模型 or FB 表单模型族 |

完成判据：能写出任务书的「能力清单」和「模型族构成」两节。

## 问题库（按层，命中才问）

每题格式：**问题 →（推荐）→ 答案映射的 XML 元素 → 消费端点 → 完成判据**。

### L1 数据面

| # | 问题 | 推荐 | 映射 | 消费端点 |
|---|---|---|---|---|
| L1-1 | 涉及哪些表？**各表在哪个连接（ConnString）上？** | — | — | **先跑 `tlk model dict` 把列清单拉进任务书，后续选列只准从清单选**；连接归属写进任务书 §1（环境常多库并存，跨连接不可 JOIN，见 `environments.md`） |
| L1-2 | 列表/表单展示哪些列？标题怎么来？ | 只展示业务需要的列；SQL 用表列名不写中文别名（早期样例风格，validate 报 `SQL_ALIAS_LEGACY` info），标题走 `CubeSetting` 多语言 CAPTION（运行器）/ H5 模板内联 label（APP） | `SEARCHSELECT` 输出列 + `CubeSetting`（COLNAME=结果集列名，列标题×语言） | ①② |
| L1-3 | 有哪些查询参数？各是什么类型、必填吗？ | 常用筛选 1~4 个；必填 `ParaDefVal` 写 `?` | `ParaLabel/ParaType/ParaSearchCode/ParaDefVal 01~10`、`UseParameter` | ①⑥ |
| L1-4 | 参数区在 APP/FB 上长什么样？（对照样例索引选形态） | 克隆最接近样例的 `H5PARA` 骨架 | `H5PARA` | ⑥ |
| L1-5 | 连接代码？（默认 LINKDB，按环境确认） | 问用户确认 | `ConnString` | 全部 |

完成判据：任务书的「列清单」（来自字典，含 name/type/desc/pk）与「参数表」两节填毕。

### 业务列默认语义（问卷时先按此理解，用户可覆盖）

单据状态类列（`DOCSTA` 等，X3 风格 `OPTID/OPTDES` 码表）默认语义：

| 取值 | 语义 |
|---|---|
| 1 | 计划的（草稿/初始） |
| 2 | 确认的（已提交/已确认） |
| 3 | 挂起的 |
| 4 | 完成的 |

用法：状态显示文案、防呆判据（如「仅 1 可改/可删」「提交后置 2」）默认按上表写；
用户环境码表不同时以用户给的 `OPTID/OPTDES` 为准，并写进任务书 §4。

另有并列的提交进度列（X3 风格）：`SUBSTA`（<3 = 未完成，提交时由动作脚本打批次号，见下）。

### 编号段语义补充（TAMPER 语料 2026-11-05，接 samples/README 编号表）

- **#110 查询入口形态**：同 ModelCode 下的纯只读查询模型（H5Para+H5List、`DATEVAL` 参数、`LIKE N'%{n}%'` 模糊、自造关键字列）——APP 端「查询列表页」的实际载体，编号表未收录，属语料确立的惯例（TMESPUR01#110 同型）
- **#301 按钮控制**：MyRowData 段的 APP 用法——`SELECT '.PREPROCESS.501' AS LINKFUNCTIONLIST` 控制前端动作可用性（`link-flags.md` 结果标记表）
- **15xx 扫码解析服务段**：无界面模型（H5/JS 全空，仅 SQLScript）。惯例：1521 校验单据（返回 `提示`=OK/错误文案）、1522 拆二维码内容；跨模型传参靠 `#列#` 注入（`js-hooks.md` 扫码解析链）
- **#700 双语义**：按钮防呆（`#LINKSCRIPTGET@连接:...#` 返回 `LINKPREVENT:...`）或数据源下拉/开窗（普通 SELECT）——按脚本内容区分，不按编号

### 单据编号的两种模式（按业务选型，任务书 §1 写明）

| 模式 | 写法 | 适用 |
|------|------|------|
| 即时取号 | `#LINKDOCNUM([已有单号,]规则码)#`（`placeholders.md`） | 单号在 INSERT 时即确定 |
| 延迟生成 | INSERT `'' AS DOCNUM` 占位 → 提交动作 UPDATE `BATCHID=#LINKID_ACTION#` → 存储过程赋号（TAMPERAPP #10+#21 标杆） | 单号在提交时才由后端生成 |

### L2 交互面（按命中能力组）

**① 列表/网格**

| # | 问题 | 推荐 | 映射 | 消费端点 |
|---|---|---|---|---|
| L2-1a | 列表形态：卡片列表还是表格？ | **默认卡片**（语料中表格是少数派：APP 139 个模型仅 2 个）；卡片用 `H5LIST`；表格模式用 `H5GRIDHDR`+`H5GRIDDTL`（两者必须成对） | `H5LIST` / `H5GRIDHDR`+`H5GRIDDTL` | ① |
| L2-1b | 每行要嵌明细吗？ | 有主从关系才用 | `--LINKDETAILLIST(code,num,para...)` + 子模型 `H5LIST` | ① |
| L2-1c | 每批多少行？ | 默认 100，不问 | `H5MAXLINES` | ① |

**② FB 表单**（模型族 = 主模型 + 500 附加模型）

| # | 问题 | 推荐 | 映射 | 消费端点 |
|---|---|---|---|---|
| L2-2a | 表单按什么键取单行？（必须过滤到单行） | 业务单号 | 主模型 `SEARCHSELECT`（WHERE 到单行） | ② |
| L2-2b | 表单里有哪些字段控件、哪些按钮？ | 从样例索引克隆 500 模板骨架 | 500 的 `H5PARA`(formSetting JSON) + `SEARCHSELECT`(formData，注意 `"#FORMDATA#"` 带引号字面量) | ② |
| L2-2c | 有子表/下拉吗？来源模型是？ | 复用已有明细/下拉模型 | formSetting `tableData` / `selectList`（引用 dmCode/dmNum） | ② |

**③ 编辑 / ④ 提交**

| # | 问题 | 推荐 | 映射 | 消费端点 |
|---|---|---|---|---|
| L2-3 | 能编辑哪些列？怎么定位行？ | `WHERE 主键=0#LINKROWID#` | `SQLUpdateScript`（落库列 SEARCHWHERE）+ `--LINKEDITMODE` | ③④ |
| L2-4 | 能新增吗？默认值？ | `#LOGIN_USER#`、`GETDATE()` | `SQLNew` + `--LINKADDNEWROWS`（编辑态加行）或留空（按钮式新增） | ④ |
| L2-5 | 能删除吗？ | 软删/防呆时改走 1000 检查模型 | `SQLRemove` | ④ |
| L2-6 | 编辑列的下拉/联动？ | — | ModelSetting `EditValueList`（模型代码#序号）、`EditCols` | ③ |

**⑤ 动作/防呆**

| # | 问题 | 推荐 | 映射 | 消费端点 |
|---|---|---|---|---|
| L2-7 | 有哪些行级动作（右键菜单/按钮）？各做什么？ | 动作 SQL 写在附加模型的 `SQLCLEAR` | 附加 501~520 + `--LINKREFRESH` | ⑤ |
| L2-8 | 动作前要检查/确认什么？ | 防呆文案写脚本注释标记 | 附加 1000 + `LINKPREVENT`(阻止)/`LINKCONFIRM`(确认)/`LINKWARNING`(提示) | ⑤ |
| L2-9 | 有自动前/后置处理吗？ | — | 附加 11~20 / 31~40；手动版 21~30 / 41~50 | ④⑤ |
| L2-10 | 动作完成后跳哪 / 提示什么？ | — | `--LINKREFRESH`；提示模型 编号+2000 | ⑤ |

**⑦ 图表/挖掘/多层级**

| # | 问题 | 推荐 | 映射 | 消费端点 |
|---|---|---|---|---|
| L2-11 | 要图表吗？数据从哪来？ | — | `H5CHART`（ECharts 脚本） | ⑦ |
| L2-12 | 要数据挖掘入口/下钻吗？ | — | `SYSDM` 行（DMLINE、PARA01~10） | ⑦ |
| L2-13 | 要多级/树形展开吗？ | — | ModelSetting `leveldatasetting` + `ConnString=MULTILEVELDATA` | ⑦ |

**JavaScript 钩子（跨能力组，APP 为主；钩子清单与签名见 `js-hooks.md`）**

| # | 问题 | 推荐 | 映射 | 消费端点 |
|---|---|---|---|---|
| L2-J1 | 有扫码输入吗？扫码后要自动查询/校验/跳焦点吗？ | 有扫码才写 `scan_para`（可选 `scanAfterAction`） | `JavaScript` | APP 链路 js |
| L2-J2 | 提交/更新/删除前有跨字段业务校验吗？ | 有才写 `beforeFunction`（返回 true 即中断） | `JavaScript` | APP 链路 js |
| L2-J3 | 动作完成后要自动刷新/通知列表页吗？ | SQL 脚本 `--LINKREFRESH` 不够时才写 `afterFunction`/`Save_Data` | `JavaScript` | APP 链路 js |

约 81% 的 APP 模型不需要 JS——三问都不命中就不写。FB 侧只有详情页行点击 `contextTap` 一种。

**文件上传**（若有）：附加模型承载上传记录脚本，脚本标记 `--LINKUPLOAD_FILETYPE/PATHASSIGN/KEEPFILENAME`，端点 `linkDMFileUpload`。

### L3 验收面

| # | 问题 | 产出 |
|---|---|---|
| L3-1 | 「做对了」长什么样？逐条说出可观察的结果 | 任务书「验收断言」：可执行断言（agent 跑）+ 人工断言（用户在 APP/FB 实机确认） |
| L3-2 | 模型是否也要能被 AI 调用？ | 是 → `SEARCHSELECT` 必须参数自洽（`tools search` 描述可读） |

## 任务书模板（`<ModelCode>#<ModelNum>-brief.md`）

```markdown
# 模型任务书：<ModelCode>#<ModelNum> <ModelDesc>

## 1. 目标与环境
- 用途（一句话）：          目标环境：运行器 / APP / FB / AI
- ModelCode / ModelNum（编号段语义）：      ConnString：      语言集合：

## 2. 能力清单（命中的能力组）
- [ ] ① 列表/网格   [ ] ② FB 表单   [ ] ③ 编辑   [ ] ④ 新增/删除
- [ ] ⑤ 动作/防呆   [ ] ⑥ 参数区    [ ] ⑦ 图表/挖掘/多层级   [ ] 文件上传

## 3. 模型族构成
| 模型代码 | 编号 | 编号段职责 | 被哪个端点消费 |
|---|---|---|---|
| <主模型> | 10 | 主查询/列表 | linkDMH5Data / linkDMData |
| <主模型>10X | 500 | FB 表单定义（formSetting + formData） | linkDMFormData |
| <主模型>10X | 1000 | 删除防呆 | linkDMConditionAction |
| ... | | | |

## 4. 列清单（来自 tlk model dict，选列只准从这里选）
| 列名 | 类型 | 含义 | 用途（输出列/参数/编辑列/仅引用） |
|---|---|---|---|

## 5. 参数表
| 位 | ParaLabel | ParaType | ParaSearchCode | ParaDefVal | 必填 |
|---|---|---|---|---|---|

## 6. 界面形态与模板来源
- 列表形态 / 模板克隆自（样例文件或存量模型编号）：
- H5PARA / H5EDIT / H5NEWREC / 500 表单：各自克隆来源：
  - 500 的 `formtemplate` 指向的 FB 表单骨架若需**新建**，用 `formbuilder-json-generator` skill 生成（formbtns 默认空数组，按钮逻辑走模型 #501+）
  - APP H5 模板内的控件 class / link- 属性 / 取值提交约定，以 `totallink-app-help` 的 h5-guide / classes-ids / attributes 为准
- JS 钩子（L2-J 命中项）：scan_para / beforeFunction / afterFunction / contextTap / 无

## 7. 动作清单
| 动作 | 承载位置（哪个模型的哪个脚本） | 防呆 | 完成后行为 |
|---|---|---|---|

## 8. 验收断言
### 可执行（agent 跑，全过才交付）
- [ ] validate 无 error（含族内一致性）
- [ ] model run scriptType=0 返回预期列 + 非空 rows（列与本表 §4 一致）
- [ ] 模板脚本 scriptType=101/103/106/108 formattedScript 无残留占位符
- [ ] 提交脚本 scriptType=1/2/3/4 formattedScript 格式正确
### 人工（用户实机确认）
- [ ] APP 列表/按钮/表单渲染        - [ ] FB 表单渲染与保存回写
- [ ] 动作与防呆提示                - [ ] 扫码/JS 钩子行为（若 L2-J 命中）
- [ ] 其他：＿＿＿
```

## 流程位置（接 SKILL.md 工作流）

```
需求澄清（阶段 0 能力组判定 + 问题库 L1→L2→L3）
  → 落盘任务书 → 用户确认（门禁）
  → 生成 XML（按任务书 §6 克隆模板、§4 选列）
  → validate / import / run（两层验收，任务书 §8 逐条核对）
```
