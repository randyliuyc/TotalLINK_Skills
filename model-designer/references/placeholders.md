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
| `#LINKDOCNUM([已有单号,]规则码)#` | 单据自动编号（三种形态与取号规则见下节） |

### 单据编号占位符：`#LINKDOCNUM` 三形态

权威来源：`BaseLib/Modules/GlobalFormula.vb:337-410`（替换层）、`BaseLib/Models/LinkDocNum.vb`（取号），2026-11-04 源码核实。

| 形态 | 语义 |
|------|------|
| `#LINKDOCNUM(已有单号,规则码)#` | **第一参非空 → 原样回填该值，不产生新号**（幂等）；第一参为空（写作 `(,规则码)`）→ 按规则取新号 |
| `#LINKDOCNUM(规则码)#` | 单参 = 规则码，直接取新号 |
| `#LINKDOCNUM.规则码#` / `#LINKDOCNUMBY(规则码)#` | 无条件取新号（`GlobalFormula.vb:337-352` / `:389-410`） |

取号规则（`LinkDocNum.NewDocNum`）：

- 规则码 = **LINKDOCNUM 表的 `NUMCODE`**（键 CUSCODE+NUMCODE），存 `NUMFORMULA`（公式）/`NUMLEN`（流水位数）/`RESETFMT`（重置周期）/`NUMLAST`（当前流水）；**不是前缀字面量**——前缀写在公式里。
- 规则不存在时**自动创建默认规则**：公式 `{规则码}#LINK_THISMONTH4##LINKNUM#`、NUMLEN=5 → 生成 `规则码+yyMM+5位流水`，如 SAR261100001（TMESSTK2010X#501 实测吻合）。
- 公式可嵌日期占位符（`#LINK_THISMONTH4#`=yyMM、`#LINK_THISYEAR#`=yyyy 等，`GlobalFormula.vb:771-777`）+ `#LINKNUM#`（NUMLEN 位左补零）。
- 重置周期 `RESETFMT`：`Y`=按年 / `M`=按月 / `D`=按日，空缺省按月；周期切换后流水归 1。
- 取号即 UPDATE 回写 `NUMLAST/DOCNUMLAST`：后续 INSERT 失败回滚**不回收**（会断号）；先读后写无锁，**并发可能重号**（内部系统可接受，高频写入口慎用）。
- 替换时机：`{N}` 参数替换先于此处理（`GlobalFormula.vb:136` vs `:354`），所以参数槽里传的单号/规则码此时已是实际值。平台在跳转检查等场景置 `NoDOCNew` 跳过取号防重复消耗号段（`SysDataModel2.vb:1563`）。

常见用法：

```sql
-- 按维度分段：把分组维度（如地点）的参数值直接当规则码传第二参
'#LINKDOCNUM(,{0})#' --XMHNUM_0（KEEWAYZUPSCH1010X#21，{0}=STOFCY 地点）

-- 固定规则码取新号
#LINKDOCNUM(,SAR)#

-- 幂等模式：FB 明细加行 UNION 空行场景，真实行 {0}=已取单号原样回填，空行才取新号
N'#LINKDOCNUM({0},PRQ)#' AS [DOCNUM]（TMESPUR01#10）
```

## 使用原则

1. 三套体系替换时机不同：`{N}` 在脚本格式化时替换、`#列#` 在行级动作时替换、`#LC.` 等在全局公式替换时处理。混用没有问题，但不要用错层（比如想在 SQLScript 全局查询里用行级 `#COL#`——没有行，替换不出值）。
2. 只用样例实证过的写法；样例没有的占位符先用源码验证再用。
