---
name: model-designer
description: 设计 TotalLINK 数据模型（SYSSEARCH）并落库验证——需求问卷澄清 → 模型任务书 → 生成模型 XML → tlk model validate 静态诊断 → tlk model import 导入 → tlk model run 设计态运行 → 两层验收迭代。覆盖三类消费环境：模型运行器（fDataAnalysis）、TotalLINK APP（H5）、FB 网页表单（formbuilder）。当用户要求创建/修改数据模型、设计查询模型、生成模型 XML、把业务需求落成 TotalLINK 模型时使用。
---

# TotalLINK 模型设计器（model-designer）

把业务需求设计成 TotalLINK 数据模型（模型族 = 主模型 + 附加模型），产出模型 XML（`SysDataModelXML` 格式），导入并完成两层验收后交付。

本目录的 `tlk_group.py` 把 `model` 命令组注册进 base 入口，所以命令统一是 `tlk model ...`——入口、环境与令牌都由 totallink-base 提供。

## 前提

- **已完成 totallink-base 环境配置**：`env list` 能列出项目、`auth verify` 通过。
- 令牌所属角色的 `RoleType` 须为 `SystemAdmin` 或 `SystemExpert`。模型三端点有角色闸门，普通用户自助签发的 `tlk_` 调不通——遇到「没有操作权限」直接告知用户找管理员，不要换项目重试。

## 命令

| 命令 | 作用 |
|------|------|
| `model dict <表名> [--code --num --conn --db] [--save]` | 查表字典（配置驱动，缺省 SYSTEMCODE/30；`--save` 写入项目配置） |
| `model export <dmCode> <dmNum> -o <file.xml>` | 导出现有模型为 XML（当模板或回归基线） |
| `model validate <file.xml> [dmCode dmNum] [--columns COL1,COL2] [--env fb\|app]` | 纯 XML 静态诊断，不走网络；`--env` 加模型族一致性检查 |
| `model import <file.xml> [--force] [--code X --num Y]` | 导入落库（服务端重算 `MD5HASH`） |
| `model run <dmCode> <dmNum> --params-json '[...]' [--script-type N] [--max-rows 20]` | 设计态运行：不计配额、不校验 `AccessFlag` |

下文一律写完整入口：`python3 scripts/tlk.py model ...`。

- **`dict`**：配置驱动的薄封装（编号/连接/参数模板都在 `~/.totallink/config.json` 项目节 `dict` 键下，CLI 可临时覆盖）。三级降级：①缺省 SYSTEMCODE/30 调通 → 正常返回归一化列清单；②模型不存在/404 → 输出可操作错误，转去问用户（用 `tools search` 搜「表结构」，或请用户提供 dmCode/dmNum 后 `--save` 配置）；③返回列与已知词汇表对不上 → 原样输出 schema+样例行并标注「列映射未知」，**不猜**，问用户各列含义。
- **`validate` 的输出去看 `summary` 与 `diagnostics`**（`error` / `warning` / `info`）；顶层出现 `error` 字段表示有 error 级诊断（`VALIDATE`）或文件读不到（`IO`）。诊断项自带 `code` 与 `path`，按 `path` 定位到字段/列。
- `validate [dmCode dmNum]` 校验 XML 内嵌编号是否等于给定期望值——以样例为模板改名时用它防混淆。`--env fb` 检查 500 伴生模型、`#FORMDATA#` 写法；`--env app` 检查 H5 族字段成对性与 `H5PARA` 非空。
- `--columns` 取 `model run` 返回的 `columns`（逗号分隔），用于检查 CubeSetting 是否覆盖实际返回列。
- `import` 不带 `--force` 时目标编号已存在会被拒绝；覆盖前必须向用户确认。
- `run --script-type 0` 真执行查询；其他值不执行数据库，只回 `formattedScript`。脚本类型编号（验证模板用）：`101=H5List, 103=H5Edit, 106=H5Para, 108=H5GRIDHDR, 1/2/3/4=新增/编辑/删除/动作`。
- 该环境服务端未部署 `linkDMImport` 时返回 `HTTP 404`，此时告知用户该环境版本不支持写入，改为交付 XML。

## 硬规则（任何步骤不得违反）

0. **任务书门禁**：生成任何 XML 之前，必须先按 `references/discovery.md` 完成问卷并落盘任务书（`<CODE>#<NUM>-brief.md`），经用户确认。任务书未确认前只允许事实调查（字典查询、样例检索），不允许产出 XML。
1. **编号直接询问用户**：`ModelCode` / `ModelNum` 向用户索取。询问时附上 `eModelAttachNum` 编号段语义（`references/samples/README.md`）供参考。
2. **环境相关值必须问用户，但提供默认值**：
   - 连接代码（`ConnString`，与 `--LINKSCRIPTGET@连接代码:` 同域）：默认 `LINKDB`，用户确认或改写；
   - 模块前缀（系统缩写+模块缩写）：问用户，不沿用样例值；
   - CubeSetting 语言集合：默认 `zh` + `en`（每列×每语言一条），需要更多语言由用户给代码（如 `vi` → `LANGUAGE-vi`）；
   - `ImageFile` 的 `#LINKRES#` 数字取 0~99 随机即可，不必问。
3. **`SysModelFlag` 必须 `false`**：系统级模型既过不了 `validate`，服务端也拒绝导入。
4. **新分隔符**：经 `FunctionSplit` 解析的脚本（`CALLFUNCTION`、`LINKDATAMINE` 等）一律用 `~<!>~`，不用旧的单字符 `~`。读参考样例时容忍旧写法（`validate` 会把旧写法报成 `OLD_SEPARATOR`），自己产出必须用新写法。
5. **H5 族字段按目标环境处理**：
   - 只做运行器/AI 的模型：`H5*` 留空；
   - 目标环境含 APP/FB：`H5PARA`、`H5LIST`（或 `H5GRIDHDR`+`H5GRIDDTL`）、`H5EDIT`、`H5NEWREC` 等**必须显式设计，从样例/存量模型克隆**——不依赖服务端兜底（新服务端兜底已删除，模板为空就是空）；
   - 以存量模型为模板时保持原值。
6. **`MD5HASH` 留空**：导入时由服务端重算。它不是文档哈希，不能用它判断两个 XML 是否同源。
7. **`CUSCODE` 统一留空**（2026-11-05 定）：客户归属由服务端按登录环境决定；`model export` 导出的参考模型可能带 CUSCODE 值，生成/克隆时一律清空（validate 报 `CUSCODE_NONEMPTY`）。
8. **不臆造**：列名只准从 `model dict` 的列清单选；不认识的字段、标记、action，先查 `references/`；文档没有的问用户。
9. **模型是模型族**：动主模型时检查附加模型族（`{代码}{编号}X`）是否需要同步调整；FB 表单按页面族组织（`.AH/.AL/.BH/.BL` 四族 + 各族 500 伴生模型，见 `references/fb-page-families.md`）。

## 工作流

1. **需求澄清 = 问卷（阶段 0 + 问题库）**：严格按 `references/discovery.md` 执行——先判定能力组（①~⑦），再按层问 L1 数据面 → L2 交互面 → L3 验收面；一次一题、附推荐、能查的事实不问。数据面第一件事：`model dict` 拉列清单。
   *完成判据：能力清单、模型族构成、列清单、参数表全部齐备。*
2. **落盘任务书**：按 `discovery.md` 模板写 `<CODE>#<NUM>-brief.md`，交用户确认。**未确认不得生成 XML**（硬规则 0）。
3. **找模板与能力发现**：
   - 已存在同类模型 → `python3 scripts/tlk.py model export <代码> <编号> -o tmpl.xml`，以它为模板；
   - 不确定该编号/该业务是否已有模型 → `python3 scripts/tlk.py tools search <关键字>`；
   - 模板型内容（H5LIST/H5PARA/500 表单 JSON）从样例索引（`references/samples-index.md`）或任务书 §6 指定的来源克隆，只替换 `#列名#` 与列名。
   *完成判据：手上有 1 个可参照的模型 XML 或样例。*
4. **生成 XML**：按 `references/fields.md` 的元素顺序与取值规范产出，文件名 `CODE#NUM-描述.xml`；FB 模型族一次生成主模型 + 500 伴生模型。
5. **静态诊断**：`python3 scripts/tlk.py model validate <file.xml> [代码 编号] [--env fb|app]`，把 `error` 全部修掉；`warning` 逐条判定「是不是我这次的写法问题」。
   模型已经能在设计态跑通之后（第 2 轮迭代起），先跑第 7 步拿到 `columns`，再 `validate <file> <代码> <编号> --columns <逗号分隔列名>` 把 CubeSetting 覆盖检查接上——首次生成时列名还是纸面设计，跳过这条即可。
   *完成判据：`summary.error == 0`。*
6. **导入**：`python3 scripts/tlk.py model import <file.xml>`，成功返回 `action`（`created` / `updated`）与服务端重算的 `md5`、`cubeSettings` 条数。
   *完成判据：返回 `status: ok` 且 `action` 符合预期（新建应为 `created`）。*
7. **设计态运行**：`python3 scripts/tlk.py model run <代码> <编号> --params-json '[...]'`。
   - `columns` 与任务书 §4 的输出列对齐，`captions` 反映 CubeSetting 是否生效；
   - 写脚本/模板用 `--script-type <非 0>` 只看 `formattedScript`，不碰数据库。
   *完成判据：`scriptType=0` 时返回预期列与非空 `rows`（确实无数据的模型则 `rowCount` 可解释）。*
8. **两层验收（对照任务书 §8）**：
   - 可执行断言（agent 跑）：validate 无 error、run 列对齐、模板 scriptType 的 `formattedScript` 无残留占位符（`{N}`/`#列名#`）；
   - 人工断言（列给用户实机确认）：APP 列表/按钮/表单渲染、FB 表单渲染与保存回写、动作与防呆提示——agent 不声称这些已验证。
9. **迭代**：`validate` 报 error → 改 XML 回第 5 步；`run` 报错或列不符 → 改脚本/字段回第 4 步；`import` 被拒（覆盖保护、系统级、反序列化失败）→ 按 `message` 处理后再导。

**交付判据**：任务书 §8 可执行断言全过 + `import` 返回 ok + 人工断言清单已交用户。三者缺一不算完成。

## 错误怎么读

`validate` 的顶层 `error`：`VALIDATE` = 有 error 级诊断（先修再导）；`IO` = 文件读不到或为空。

`validate` 的诊断 `code`：

| code | 含义 | 处理 |
|------|------|------|
| `STRUCTURE` 类（`UNKNOWN_ELEMENT` / `DUPLICATE_ELEMENT` / `BAD_INT` / `BAD_BOOL` / `ROOT_TAG` / `MISSING_FIELD`） | XML 结构或字段名不对，导入会失败或字段被丢弃 | 对照 `fields.md` 改元素名/类型 |
| `SYSMODELFLAG` | 系统级标志为 true | 改 `false` |
| `PARATYPE_ILLEGAL` | `ParaType` 不在 `EParamType` 词汇表（`DATEC8/DATEC10/DATEINT8/DATEVAL/DATETIME/DEC/STR/SPEECHSTR/PICKERSTR/DROPDOWN/DROPRELOAD/MOREFUNC`，见 `fields.md`） | 改类型 |
| `PARAM_INDEX_UNDEFINED` | 脚本引用了未定义的参数位（主模型会原样留在脚本里；附加模型可能由调用方传参） | 主模型补 `ParaLabel` 或改占位符；附加模型确认调用链 |
| `ROW_TOKEN_IN_QUERY` | 主模型 `SQLScript` 里用了行级 `#列名#` | 挪到编辑/新增/删除/动作脚本 |
| `OLD_SEPARATOR` / `SEPARATOR_MIXED` | 旧 `~` 或混用分隔符 | 改用 `~<!>~` |
| `FLAG_*` | `--LINKxxx` 标记未知、写错字段或格式不对 | 对照 `link-flags.md` |
| `MODELSETTING_*` | ModelSetting JSON 非法、键名大小写错、用了无读取方的键 | 对照 `modelsetting.md` |
| `CUBE_UNCOVERED` / `CUBE_STALE` | CubeSetting 与实际返回列不对应 | 补/删对应列的设置 |
| `EXPECT_MISMATCH` | XML 内编号与给定期望值不一致 | 确认是否用错了模板 |
| `FAMILY_*`（`--env` 时） | 模型族一致性问题（H5GRIDHDR/DTL 不成对、H5PARA 空、500 JSON 非法、`#FORMDATA#` 写法错等） | 对照 `endpoints.md` 修复 |

`dict` 的降级提示：见上文命令表 `dict` 条目——按提示转 `tools search` 或问用户。

`run` 的 `error`：

| error | 含义 | 处理 |
|-------|------|------|
| `BIZ`，`message` 为「功能模型不存在」 | 编号写错或未导入（`detail` 是英文 `Function model does not exist.`） | 核对编号；未导入先 `import` |
| `BIZ`，`message` 含「没有操作权限」 | 角色闸门或功能授权 | 告知用户找管理员，不换项目重试 |
| `BIZ`，其他（哈希不符、无结果集） | 脚本问题或 `MD5HASH` 不一致 | 按 `message` 修脚本；哈希问题重新 `import` 让服务端重算 |
| `AUTH` | 令牌无效 | 提示用户更新令牌 |
| `CONFIG` | 没有可用项目配置 | 回到 base 的 `env add` / `env use` |
| `NETWORK` | 连不上 `base_url` | 检查地址，用 base 的 `auth verify` 定向排查 |
| `HTTP` | `404` = 该环境未部署该端点；5xx = 后端异常 | 404 告知用户版本不支持；5xx 稍后重试 |
| `UNKNOWN` | 其他异常 | 把 `message` 原文报给用户 |

## 任务 → 必读文档

| 任务 | 必读 |
|------|------|
| 任何模型需求（第一入口） | `references/discovery.md`（问卷 + 任务书模板） |
| 弄不清某字段/脚本如何被执行、影响哪个返回 | `references/endpoints.md`（链路图 + 能力组契约表） |
| 纯查询/报表模型 | `references/fields.md`、`references/placeholders.md` |
| 带增删改的模型 | `references/fields.md`、`references/link-flags.md` |
| 预判某个标记/配置在运行器里长什么样（界面行为） | `references/runner-behavior.md`（模型要素 → 运行器行为映射 + 设计规律） |
| 带动作按钮/外部调用 | `references/fields.md`、`references/callfunction-actions.md` |
| 带下拉参数（DROPDOWN/DROPRELOAD） | `references/fields.md`、`references/samples/ERAQA101010X.SUPCOD#10-选择供应商.xml` |
| 可编辑网格/列编辑/保存联动 | `references/fields.md`、`references/modelsetting.md` |
| 数据检查/防呆（LINKPREVENT/LINKCONFIRM） | `references/link-flags.md`、`references/samples/ERAQA101010X#1000-删除检查.xml` |
| 附加模型/数据挖掘联动 | `references/samples/README.md`、`references/samples/ERAQA101010X#21-Release.xml` |
| APP/FB 模板克隆来源 | `references/samples-index.md` |
| APP 按钮怎么写（新建/动作/删除，`linkquick`/`btnid`/`para`/`script`、APP 与 Client 传参模式区别） | `references/app-buttons.md`（属性级细节见 `../totallink-app-help/references/linkquick.md`、`attributes.md`） |
| 开窗选择窗（linkdatasearch 数据源模型，列表空白的排查） | `references/datasearch-windows.md` |
| FB 页面组怎么组织（.A/.B×.H/.L 族、五种 500 形态、菜单 JSON、动作模型） | `references/fb-page-families.md` |
| FB 需**新建/修改** formbuilder 表单骨架（formtemplate 指向的 MODJSON） | `../formbuilder-json-generator/`（布局/控件/按钮/表达式规则；模板查询/落库走 AI 工具 `SYSINFOMATION/300`，契约见其「模板落库」节，按环境开放、缺工具时提示用户在服务端开放） |
| APP 模型要写前端脚本（扫码/校验/刷新钩子） | `references/js-hooks.md` |
| APP H5 模板的控件 class、link- 属性、取值/提交链路等客户端约定 | `../totallink-app-help/references/`（h5-guide / classes-ids / attributes / methods） |
| 拿不准某字段影响哪个环境 | `references/environments.md`、`references/endpoints.md`、`references/runner-behavior.md`（环境标签） |
| 任何生成之前 | 对应类型的最接近样例 + 已确认的任务书 |

## 速查

- 根元素 `<SysDataModelXML>`，字段全集与取值规范见 `references/fields.md`。
- 两套参数占位符（勿混）：模型参数 `{N}`（0 基，`{0}` = 参数 01）；网格行级值 `#列名#`（数字列写 `0#列名#` 防 NULL/空串）。详见 `references/placeholders.md`。
- **APP 按钮删除传参走 `{0}`**（`para="#LINKROWID#" script="3"` 把行 ID 当模型参数传入）；`#LINKROWID#` 行级令牌只在 Client/运行器行编辑上下文生效——见 `references/app-buttons.md` §0。
- **SQL 列名风格（2026-11-04 定）**：新模型 SELECT 不为显示目的写中文别名（早期样例风格），直接用表列名；标题走 CubeSetting CAPTION（运行器）/ H5 模板内联 label（APP）；聚合列才用英文别名。validate 对中文别名报 `SQL_ALIAS_LEGACY`（info）。**例外**：无界面服务型模型的消息列可用中文别名（TAMPERAPP#1521 `提示`）。
- 开窗选择窗契约：列表/开窗数据源模型 CubeSetting `COLNAME` 必须等于结果集列名，`text-value` 引用实际列名，对不上即 APP 列表「有行但空白」；**APP PDA 开窗走按钮 `automatch` 不配业务列 CubeSetting**——适用范围与排查见 `references/datasearch-windows.md` §2/2a/2b。
- 参数四件套：`ParaLabel01~10` / `ParaType01~10` / `ParaSearchCode01~10` / `ParaDefVal01~10`，最多 10 个，存在 SYSSEARCH 表；`ParaDefVal` 写 `?` 表示必填（同时决定附加模型是否需人工补参）。
- 恒填字段：`ImageFile = #LINKRES#数字`（数字取 0~99）；`MD5HASH` 留空。
- 脚本注释标记（`--LINKEDITMODE`、`--LINKREQUIRED:` 等）见 `references/link-flags.md`。
- `ModelNum` 编号段语义与 `ModelCode` 命名规范见 `references/samples/README.md`。
- 脚本类型编号：`0=查询, 1/2/3/4=新/编/删/动作, 101~109/121=H5 族, 111~113=CALLFUNCTION/JAVASCRIPT/MODELSETTING`。编辑脚本 XML 元素叫 `SQLUpdateScript`，落库列叫 `SEARCHWHERE`。
