# 占位符体系

> 权威来源：21 个真实样例（首要）+ `BaseLib/Modules/GlobalFormula.vb`。样例证据优先于代码推断。

## 三套替换体系（必须分清）

### 1. 模型参数 `{N}`（0 基，N = 参数序号 - 1）

| 写法 | 语义 | 样例证据 |
|------|------|---------|
| `'{0}'` / `{0}` | 第 1 个模型参数（参数 01） | ERAQA101010X#700:11 `DECLARE @GRDCOD VARCHAR(30)='{0}';` |
| `'%{0}%'` | 参数包上 LIKE 通配（模糊查询） | ERAQA1010#10:11 |

样例头部习惯：SQLScript 开头把所有参数 `DECLARE` 成局部变量再引用：

```sql
DECLARE @GRDCOD VARCHAR(30)='{0}';
DECLARE @CUSCOD VARCHAR(30)='{1}';
```

注意：`{N}` 也是 `string.Format` 槽位——脚本含字面花括号（JSON 片段）时写 `{{ }}` 转义（`GlobalFormula.vb:168`，失败回退逐个替换为异常驱动兜底，与原 VB 一致）。

### 2. 行级占位符 `#列名#`（行数据替换）

| 写法 | 语义 | 样例证据 |
|------|------|---------|
| `#COLNAME#` | 当前行该列的值 | `'#ELECOD#'`（ERAQA1005#10 SQLNew） |
| `0#COLNAME#` | **数字列防呆**：前缀 `0` 防 NULL/空串造成 SQL 语法错误 | `ELESEQ=0#ELESEQ#`（ERAQA1005#10:24） |
| `#LINKROWID#` | 行标识列（查询时 `SELECT S.ID LINKROWID` 带出） | `WHERE ID=0#LINKROWID#` |
| `#LOGIN_USER#` | 当前登录用户 | `,'#LOGIN_USER#'--<CREUSR...` |

**SQL 注入注意**：字符串列值直接拼入 SQL（`'#COL#'`），这是平台既有风格；生成时不要发明新的参数化方式，但新脚本应尽量走 `DECLARE @x = '{N}'` 头部声明模式减少拼接点。

### 3. 列别名回写模式（下拉列）

可编辑下拉列的固定套路（`LINKDROPVALID` 前缀 + EditValueList 配对）：

```sql
-- SQLScript：原值列起别名带出
S.CTLTYP LINKDROPVALIDCTLTYP

-- SQLUpdateScript：写回时用别名占位
, CTLTYP = N'#LINKDROPVALIDCTLTYP#'
```

```json
-- ModelSetting.EditValueList：声明该列的下拉来源模型
{"DataScript":{"UpdateScript":{"EditCols":["LINKDROPVALIDCTLTYP"],
  "EditValueList":{"LINKDROPVALIDCTLTYP":"ERAQACTLTYP#10"}}}}
```

同理 `VERDESC LINKTEXTVERDESC`（纯文本编辑别名，无下拉）。列别名以 `LINKTEXT`/`LINKDROPVALID` 开头触发对应编辑控件（推断【待核对】，样例强烈支持）。

## 资源与其他

| 写法 | 语义 |
|------|------|
| `#LINKRES#数字` | 客户端图标资源引用（ImageFile 字段专用，数字 0~99 随机即可） |
| `#LINKSCRIPTGET@连接代码:SQL#` / `#LINKSCRIPTRUN@连接代码:SQL#` | 公式占位符形式的内嵌脚本：GET 返回单值、RUN 执行返回空（`GlobalFormula.vb:541`、`MLTShared.vb:3164`）。连接代码因环境而异，问用户 |
| `#LC.xxx#` | LINKCONST 全局常量（运行时查库，按 CUSCODE 过滤；`GlobalFormula.vb:1006-1022`）。样例未出现【待核对】 |
| `#LINKID_ACTION#` / `#LINKID_RESULT#` | 动作/结果 ID（`SysDataModel.vb:3723/3727`）。样例未出现【待核对】 |
| `#SYSUSER.UDFxxx#` | 登录用户自定义字段。样例未出现【待核对】 |
| `#TAG#` | 标签打印场景（`LinkDefine.cs:365`） |

## 使用原则

1. 三套体系替换时机不同：`{N}` 在脚本格式化时替换、`#列#` 在行级动作时替换、`#LC.` 等在全局公式替换时处理。混用没有问题，但不要用错层（比如想在 SQLScript 全局查询里用行级 `#COL#`——没有行，替换不出值）。
2. 只用样例实证过的写法；样例没有的占位符先用源码验证再用。
