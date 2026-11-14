# 错误与诊断对照表（errors）

> 本文件是 `model-designer` 的**排错索引**，从 SKILL.md 拆出以降低常驻上下文。
> 什么时候读：`validate` 报出看不懂的 code、`model dict` 报 `CONFIG`、`model run/import` 返回 `error` 时。
> 严重级别口径：`error` = 导入会被拒 / 反序列化必失败 / 必填项缺失；`warning` = 运行时大概率不对；`info` = 写法提示，不影响执行。

## 一、`validate` 的顶层 `error`

| 值 | 含义 | 处理 |
|---|---|---|
| `VALIDATE` | 有 error 级诊断（明细在 `diagnostics`） | 先修再导 |
| `IO` | 文件读不到或为空 | 检查路径 / 编码（支持 UTF-8 BOM） |

无 `error` 字段即通过；`summary.error == 0` 是交付门槛。

## 二、`validate` 的诊断 code

| code | 含义 | 处理 |
|------|------|------|
| `STRUCTURE` 类（`UNKNOWN_ELEMENT` / `DUPLICATE_ELEMENT` / `BAD_INT` / `BAD_BOOL` / `ROOT_TAG` / `MISSING_FIELD`） | XML 结构或字段名不对，导入会失败或字段被丢弃 | 对照 `fields.md` 改元素名/类型 |
| `SYSMODELFLAG` | 系统级标志为 true | 改 `false`（硬规则 3） |
| `PARATYPE_ILLEGAL`（info） | `ParaType` 不在 `EParamType` 词汇表（`DATEC8/DATEC10/DATEINT8/DATEVAL/DATETIME/DEC/STR/SPEECHSTR/PICKERSTR/DROPDOWN/DROPRELOAD/MOREFUNC`，见 `fields.md`）。语料另有 `TEXTAREA`/`字符型` 等写法，引擎不因此拒绝导入 | 词表可能不全，确认运行时是否生效 |
| `PARAM_INDEX_UNDEFINED` | 脚本引用了未定义的参数位（主模型会原样留在脚本里；附加模型可能由调用方传参）。`{10}` 不在此列——它是系统传入的文本框内容 | 主模型补 `ParaLabel` 或改占位符；附加模型确认调用链 |
| `PARAM_UNUSED` / `PARA_GAP` / `PARA_ORPHAN` | 参数定义了没引用 / 中间有空洞 / 只填了半个四件套 | 按提示补齐或删掉该参数位 |
| `ROW_TOKEN_IN_QUERY` | 主模型 `SQLScript` 里用了行级 `#列名#` | 挪到编辑/新增/删除/动作脚本 |
| `OLD_SEPARATOR` / `SEPARATOR_MIXED` | 旧 `~` 或混用分隔符 | 改用 `~<!>~`（硬规则 4） |
| `BRACE_UNESCAPED` | 经 `string.Format` 的脚本含未转义字面花括号 | 写 `{{ }}`；JSON 片段本身除外 |
| `FLAG_*`（`FLAG_UNKNOWN` / `FLAG_WRONG_FIELD` / `FLAG_FORMAT` / `FLAG_UNEVIDENCED`） | `--LINKxxx` 标记未知、写错字段或格式不对 | 对照 `link-flags.md` |
| `MODELSETTING_*`（`_JSON` / `_CASE` / `_UNKNOWN_KEY` / `_DEAD_KEY` / `_JSON_DYNAMIC`） | ModelSetting JSON 非法、键名大小写错、用了无读取方的键 | 对照 `modelsetting.md` |
| `CUBE_UNCOVERED` / `CUBE_STALE` | CubeSetting 与实际返回列不对应 | 补/删对应列的设置 |
| `CUBE_COLNAME` / `CUBE_COLTYPE` / `CUBE_LANG_GAP` / `CUBE_FORMULA` / `CUBE_DMKEY` | CubeSetting 列级设置问题；空 COLNAME 视为无效条目（模型标题行可忽略） | 对照本文末「CubeSetting」节 |
| `EXPECT_MISMATCH` | XML 内编号与给定期望值不一致 | 确认是否用错了模板 |
| `MODELCODE_NAMING` / `IMAGEFILE_*` / `CUSCODE_NONEMPTY` / `RET_NONZERO` / `MD5HASH_EMPTY` / `SQL_ALIAS_LEGACY` | 命名/恒填/风格类提示 | 按硬规则 2、6、7 与「速查」修正 |
| `INSERT_COLVAL_MISMATCH` | INSERT 的列数与 VALUES 值数不一致 | 实机报「列的数目大于…」即此类问题 |
| `FAMILY_*`（`--env` 时） | 模型族一致性问题（H5GRIDHDR/DTL 不成对、H5PARA 空、500 JSON 非法、`#FORMDATA#` 写法错等） | 对照 `endpoints.md` 修复 |

> `--columns` 未提供时只报 `CUBE_UNCHECKED`（info），跳过"覆盖实际返回列"检查；第 2 轮迭代起应带上 `model run` 返回的 `columns`。

## 三、`model dict` 的降级路径

缺配置时报 `CONFIG`（`missing` 列出缺哪几项）→ **问用户**要 ①字典模型 dmCode/dmNum ②连接代码 conn ③数据库名 db，拿到后 `--code/--num/--conn/--db --save` 落进项目配置，不自行试探（硬规则 10）。

列清单为空时按 `hint` 走：该表可能在另一个连接/库上，先确认连接归属，仍为空则改问用户列结构。

## 四、`model run` / `model import` 的 `error`

| error | 含义 | 处理 |
|-------|------|------|
| `BIZ`，`message` 为「功能模型不存在」 | 编号写错或未导入（`detail` 是英文 `Function model does not exist.`） | 核对编号；未导入先 `import` |
| `BIZ`，`message` 含「没有操作权限」 | 角色闸门或功能授权 | 告知用户找管理员，不换项目重试 |
| `BIZ`，其他（哈希不符、无结果集） | 脚本问题或 `MD5HASH` 不一致 | 按 `message` 修脚本；哈希问题重新 `import` 让服务端重算 |
| `AUTH` | 令牌无效 | 提示用户更新令牌 |
| `CONFIG` | 没有可用项目配置，或 `--project` 指定的项目不存在 | 回到 base 的 `env add` / `env use` / `env list` |
| `NETWORK` | 连不上 `base_url` | 检查地址，用 base 的 `auth verify` 定向排查 |
| `PARAM` | 命令行参数不合法（如 `--params-json` 不是数组、`--max-rows` 越界） | 按提示修正命令 |
| `HTTP` | `404` = 该环境未部署该端点；5xx = 后端异常 | 404 告知用户版本不支持；5xx 稍后重试 |
| `UNKNOWN` | 其他异常 | 把 `message` 原文报给用户 |
