---
name: model-designer
description: 设计 TotalLINK 数据模型（SYSSEARCH）并落库验证——生成模型 XML → tlk model validate 静态诊断 → tlk model import 导入 → tlk model run 设计态运行 → 迭代。当用户要求创建/修改数据模型、设计查询模型、生成模型 XML、把业务需求落成 TotalLINK 模型时使用。
---

# TotalLINK 模型设计器（model-designer）

把业务需求设计成 TotalLINK 数据模型，产出模型 XML（`SysDataModelXML` 格式），导入并在设计态跑通后交付。

本目录的 `tlk_group.py` 把 `model` 命令组注册进 base 入口，所以命令统一是 `tlk model ...`——入口、环境与令牌都由 totallink-base 提供。

## 前提

- **已完成 totallink-base 环境配置**：`env list` 能列出项目、`auth verify` 通过。
- 令牌所属角色的 `RoleType` 须为 `SystemAdmin` 或 `SystemExpert`。模型三端点有角色闸门，普通用户自助签发的 `tlk_` 调不通——遇到「没有操作权限」直接告知用户找管理员，不要换项目重试。
- 本 Skill 覆盖「模型运行器（fDataAnalysis）」场景；H5 / BS 设计器见 `references/environments.md`。

## 命令

| 命令 | 作用 |
|------|------|
| `model export <dmCode> <dmNum> -o <file.xml>` | 导出现有模型为 XML（当模板或回归基线） |
| `model validate <file.xml> [dmCode dmNum] [--columns COL1,COL2]` | 纯 XML 静态诊断，不走网络 |
| `model import <file.xml> [--force] [--code X --num Y]` | 导入落库（服务端重算 `MD5HASH`） |
| `model run <dmCode> <dmNum> --params-json '[...]' [--max-rows 20] [--script-type N]` | 设计态运行：不计配额、不校验 `AccessFlag` |

下文一律写完整入口：`python3 scripts/tlk.py model ...`。

- **`validate` 的输出去看 `summary` 与 `diagnostics`**（`error` / `warning` / `info`）；顶层出现 `error` 字段表示有 error 级诊断（`VALIDATE`）或文件读不到（`IO`）。诊断项自带 `code` 与 `path`，按 `path` 定位到字段/列。
- `validate [dmCode dmNum]` 校验 XML 内嵌编号是否等于给定期望值——以样例为模板改名时用它防混淆。
- `--columns` 取 `model run` 返回的 `columns`（逗号分隔），用于检查 CubeSetting 是否覆盖实际返回列。
- `import` 不带 `--force` 时目标编号已存在会被拒绝；覆盖前必须向用户确认。
- `run --script-type 0` 真执行查询；其他值不执行数据库，只回 `formattedScript`，用来验证写脚本的格式。
- 该环境服务端未部署 `linkDMImport` 时返回 `HTTP 404`，此时告知用户该环境版本不支持写入，改为交付 XML。

## 硬规则（任何步骤不得违反）

1. **编号直接询问用户**：`ModelCode` / `ModelNum` 向用户索取。询问时附上 `eModelAttachNum` 编号段语义（`references/samples/README.md`）供参考。
2. **环境相关值必须问用户，但提供默认值**：
   - 连接代码（`ConnString`，与 `--LINKSCRIPTGET@连接代码:` 同域）：默认 `LINK01`，用户确认或改写；
   - 模块前缀（系统缩写+模块缩写）：问用户，不沿用样例值；
   - CubeSetting 语言集合：默认 `zh` + `en`（每列×每语言一条），需要更多语言由用户给代码（如 `vi` → `LANGUAGE-vi`）；
   - `ImageFile` 的 `#LINKRES#` 数字取 0~99 随机即可，不必问。
3. **`SysModelFlag` 必须 `false`**：系统级模型既过不了 `validate`，服务端也拒绝导入。
4. **新分隔符**：经 `FunctionSplit` 解析的脚本（`CALLFUNCTION`、`LINKDATAMINE` 等）一律用 `~<!>~`，不用旧的单字符 `~`。读参考样例时容忍旧写法（`validate` 会把旧写法报成 `OLD_SEPARATOR`），自己产出必须用新写法。
5. **H5 字段留空**：`H5*` 系列属 TotalLINK APP 场景；以存量模型为模板时保持原值。
6. **`MD5HASH` 留空**：导入时由服务端重算。它不是文档哈希，不能用它判断两个 XML 是否同源。
7. **不臆造**：遇到不认识的字段、标记、action，先查 `references/`；文档没有的问用户。

## 工作流

1. **需求澄清**：明确模型要查询/维护什么数据、参数有哪些、需要哪些动作（新增/编辑/删除/调用外部功能）。需求模糊时先追问。
   *完成判据：能说出「查询哪些列、参数几个、有哪几个动作」。*
2. **编号与环境值**：按硬规则 1、2 拿到 `ModelCode` / `ModelNum` / `ConnString` / 语言集合。
3. **找模板与能力发现**：
   - 已存在同类模型 → `python3 scripts/tlk.py model export <代码> <编号> -o tmpl.xml`，以它为模板；
   - 不确定该编号/该业务是否已有模型 → `python3 scripts/tlk.py tools search <关键字>`；
   - 从 `references/samples/` 挑最接近的样例（映射表见文末）。
   *完成判据：手上有 1 个可参照的模型 XML 或样例。*
4. **生成 XML**：按 `references/fields.md` 的元素顺序与取值规范产出，文件名 `CODE#NUM-描述.xml`。
5. **静态诊断**：`python3 scripts/tlk.py model validate <file.xml> [代码 编号]`，把 `error` 全部修掉；`warning` 逐条判定「是不是我这次的写法问题」。
   *完成判据：`summary.error == 0`。*
6. **导入**：`python3 scripts/tlk.py model import <file.xml>`，成功返回 `action`（`created` / `updated`）与服务端重算的 `md5`、`cubeSettings` 条数。
   *完成判据：返回 `status: ok` 且 `action` 符合预期（新建应为 `created`）。*
7. **设计态运行**：`python3 scripts/tlk.py model run <代码> <编号> --params-json '[...]'`。
   - `columns` 与第 4 步设计的输出列对齐，`captions` 反映 CubeSetting 是否生效；
   - 写脚本用 `--script-type <非 0>` 只看 `formattedScript`，不碰数据库。
   *完成判据：`scriptType=0` 时返回预期列与非空 `rows`（确实无数据的模型则 `rowCount` 可解释）。*
8. **迭代**：`validate` 报 error → 改 XML 回第 5 步；`run` 报错或列不符 → 改脚本/字段回第 4 步；`import` 被拒（覆盖保护、系统级、反序列化失败）→ 按 `message` 处理后再导。

**交付判据**：`validate` 无 error、`import` 返回 ok、`run` 返回预期列。三者缺一不算完成。

## 错误怎么读

`validate` 的诊断 `code`：

| code | 含义 | 处理 |
|------|------|------|
| `STRUCTURE` 类（`UNKNOWN_ELEMENT` / `DUPLICATE_ELEMENT` / `BAD_INT` / `BAD_BOOL` / `ROOT_TAG` / `MISSING_FIELD`） | XML 结构或字段名不对，导入会失败或字段被丢弃 | 对照 `fields.md` 改元素名/类型 |
| `SYSMODELFLAG` | 系统级标志为 true | 改 `false` |
| `PARATYPE_ILLEGAL` | `ParaType` 不在 `STR/DROPDOWN/DROPRELOAD/MOREFUNC` | 改类型 |
| `PARAM_INDEX_UNDEFINED` | 主模型脚本引用了不存在的参数位 | 补 `ParaLabel` 或改占位符 |
| `PARAM_INDEX_EXTERNAL` | 附加模型引用了未定义参数（可能由调用方传入） | 确认调用链，必要时补参数 |
| `ROW_TOKEN_IN_QUERY` | 主模型 `SQLScript` 里用了行级 `#列名#` | 挪到编辑/新增/删除/动作脚本 |
| `OLD_SEPARATOR` / `SEPARATOR_MIXED` | 旧 `~` 或混用分隔符 | 改用 `~<!>~` |
| `FLAG_*` | `--LINKxxx` 标记未知、写错字段或格式不对 | 对照 `link-flags.md` |
| `MODELSETTING_*` | ModelSetting JSON 非法、键名大小写错、用了无读取方的键 | 对照 `modelsetting.md` |
| `CUBE_UNCOVERED` / `CUBE_STALE` | CubeSetting 与实际返回列不对应 | 补/删对应列的设置 |
| `EXPECT_MISMATCH` | XML 内编号与给定期望值不一致 | 确认是否用错了模板 |

`run` 的 `error`：

| error | 含义 | 处理 |
|-------|------|------|
| `BIZ: 功能模型不存在` | 编号写错或未导入 | 核对编号；未导入先 `import` |
| `BIZ: 没有操作权限` | 角色闸门或功能授权 | 告知用户找管理员，不换项目重试 |
| `BIZ`（含哈希不符、无结果集） | 脚本问题或 `MD5HASH` 不一致 | 按 `message` 修脚本；哈希问题重新 `import` 让服务端重算 |
| `AUTH` | 令牌无效 | 提示用户更新令牌 |
| `NETWORK` | 连不上 `base_url` | 检查地址，用 base 的 `auth verify` 定向排查 |
| `HTTP` | `404` = 该环境未部署该端点；5xx = 后端异常 | 404 告知用户版本不支持；5xx 稍后重试 |

## 任务 → 必读文档

| 任务 | 必读 |
|------|------|
| 纯查询/报表模型 | `references/fields.md`、`references/placeholders.md` |
| 带增删改的模型 | `references/fields.md`、`references/link-flags.md` |
| 带动作按钮/外部调用 | `references/fields.md`、`references/callfunction-actions.md` |
| 带下拉参数（DROPDOWN/DROPRELOAD） | `references/fields.md`、`references/samples/ERAQA101010X.SUPCOD#10-选择供应商.xml` |
| 可编辑网格/列编辑/保存联动 | `references/fields.md`、`references/modelsetting.md` |
| 数据检查/防呆（LINKPREVENT/LINKCONFIRM） | `references/link-flags.md`、`references/samples/ERAQA101010X#1000-删除检查.xml` |
| 附加模型/数据挖掘联动 | `references/samples/README.md`、`references/samples/ERAQA101010X#21-Release.xml` |
| 拿不准某字段影响哪个环境 | `references/environments.md` |
| 任何生成之前 | 对应类型的最接近样例 |

## 速查

- 根元素 `<SysDataModelXML>`，字段全集与取值规范见 `references/fields.md`。
- 两套参数占位符（勿混）：模型参数 `{N}`（0 基，`{0}` = 参数 01）；网格行级值 `#列名#`（数字列写 `0#列名#` 防 NULL/空串）。详见 `references/placeholders.md`。
- 参数四件套：`ParaLabel01~10` / `ParaType01~10` / `ParaSearchCode01~10` / `ParaDefVal01~10`，最多 10 个；`ParaDefVal` 写 `?` 表示必填。
- 恒填字段：`ImageFile = #LINKRES#数字`（数字取 0~99）；`MD5HASH` 留空。
- 脚本注释标记（`--LINKEDITMODE`、`--LINKREQUIRED:` 等）见 `references/link-flags.md`。
- `ModelNum` 编号段语义与 `ModelCode` 命名规范见 `references/samples/README.md`。
