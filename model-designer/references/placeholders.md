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
| `#LC.xxx#` | LINKCONST 全局常量（运行时查库，按 CUSCODE 过滤；`GlobalFormula.vb:1006-1022`）。样例未出现【已源码核对】 |
| `#LINKID_ACTION#` / `#LINKID_RESULT#` | 动作/结果 ID（`GlobalFormula.vb:1132/1136`）。LinkIdAction=每次动作执行前新生成 GUID（SysDataModel.vb:11263/11428/11933，附加模型可继承主模型）；LinkIdResult=模型每次加载数据时生成（SysDataModel.vb:2078）并传给附加模型。样例未出现【已源码核对 2026-11-05】 |
| `#SYSUSER.UDFxxx#` | 登录用户字段：先改写为 `#LINKUSER(当前用户).COL#` 再查 SYSUSER 表（KeyName1=LOGINUSER），**任意列**非仅 UDF；列不存在返回字面量 `ColNotExist`（`GlobalFormula.vb:1182-1201`、`MLTShared2.vb:2773-2797`）。样例未出现【已源码核对 2026-11-05】 |
| `#TAG#` | 标签打印场景（`LinkDefine.cs:365`） |
| `#LINKDOCNUM([已有单号,]规则码)#` | 单据自动编号（三种形态与取号规则见下节） |
| `#LINKUSER(#LOGIN_USER#).DEPTn#` | 登录用户的组织维度字段：DEPT1~DEPT3 是 SYSUSER 表列（**n 上限 3**），返回**部门代码**非名称（名称用 DeptName1~3 列）。TAMPER 语料 `X.AH#10`【已源码核对 2026-11-05：GlobalFormula.vb:1206-1221、SysUser.vb:44-46】 |
| `#LINKDATE(年偏移,月偏移,日偏移,格式)#` | 相对当前日期的偏移量（如 `#LINKDATE(0,0,-7,yyyy-MM-dd)#` = 7 天前）。TAMPER 语料 #110 H5Para 参数默认值 |
| `#LINK_TODAY#` | 今天（日期字面量）。TAMPER 语料 #110 H5Para |
| `#LINKJSONVALUE:$.路径#` | REST 响应 JSON 的 JSONPath 取值（配 `CALLFUNCTION~LINKRESTAPI~`，见 `callfunction-actions.md`）。TAMPER 语料 10X#501 |
| `#LINKCONN.<连接码>#` | 环境连接字符串（报表/接口用，如 `["#LINKCONN.LINK01#"]`）。TAMPER 语料 BH10X#503 |
| `#LINKREPORTPATH#` | 服务端报表目录（`ARSetting.reportFile` 前缀，rdlx 报表）。TAMPER 语料 BH10X#503 |
| `#MENUTITLE#` / `#PARENTNO#` / `#MENUICON#` / `#DMCODE##DMNUM#` | 菜单注册 JSON 专用（`ConnString=LINKMENUITEM` 的 500-List，见 `fb-page-families.md` §3） |
| `@列名@` | **新行占位**（SQLUpdateScript 行编辑/新增时的新值，配 `--LINKADDNEWROWS`/`--LINKEDITMODE`；MERGE INTO 场景实证 TAMPERFB BH#10/BL#10） |

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

## 2026-11-05 运行器会话补充（TotalLINKDEV.html 差异校验）

> 来源：`LINK/LINK/Note/TotalLINKDEV.html`（133 项）与 skill 已有知识、640 语料三方比对后，按组拍板校验/直收。除标注【未核对】外均经源码核实。HTML 手册勘误（详见 `link-flags.md` 勘误节）：`#LINKRSAENCRYPT` 实为**双参** `(明文,公钥)`、`--LINKSERVERTASK` 实为 `--LINKSERVERTASK.任务ID`、`--LINKIDACTION` 非控制标记。

### 会话/用户上下文（A 组）

**DM 依赖组**（ModelFieldProcessor，仅 DM 非空时替换，入口 `GlobalFormula.vb:157`；无空值回退，DM 为空时只有脚本带 `--LINKAUTOREPLACEEMPTYCOLUMNS` 才被清空，:708-711）：

| 占位符 | 取值 | 行号 |
|---|---|---|
| `#LOGIN_USER#` / `#LOGIN_NAME#` / `#LOGIN_LAN#` | LinkVar.UserCode / UserName / LangCode | 1102/1103/1104 |
| `#LOGIN_ROLE#` / `#LOGIN_COMPUTER#` / `#LOGIN_ID#` | LinkVar.Role / DevID / LoginID | 1107/1110/1113 |
| `#CURR_MODELCODE#` / `#CURR_MODELNUM#` | dm.ModelCode / ModelNumber | 1116/1119 |
| `#ATTACH_MODELCODE#` | dm.AttachModelCode（仅附加模型链路有值） | 1122 |
| `#LINKSERVER#` / `#LINKCUSCODE#` | LinkVar.Server / CusCode | 1125/1128 |
| `#LINKID_ACTION#` / `#LINKID_RESULT#` | 见上表（已核实赋值时机） | 1132/1136 |

**DM 无关组**（DM 为空也替换）：

| 占位符 | 取值 | 行号 |
|---|---|---|
| `#LINKDB#` | LINK 数据库名 | 853 |
| `#LINKTOKEN#` | DM 非空=DM.LinkToken；否则默认 `TotalLINKInternal`（`BASE_LinkToken` 非空则用它）——唯一有回退值的占位符 | 856、121、165-167 |
| `#TotalLINKMAXUSERS#` | 最大用户数（HTML 未收录的增量发现） | 859 |
| `#LINKURLPWD#` | 动态密码 `ddMMyyyy × 1949` 按日变化（MLTShared2.vb:2804-2808） | 881-882 |

### 日期时间（B 组）

`DatePlaceholderProcessor`（GlobalFormula.vb:750-829，入口条件 `result.Contains("#LINK_")`:763，基准 `DateTime.Now`）。函数体内 24 条 Replace 与下表一一对应，**无手册未收录项**：

| 占位符 | 输出 |
|---|---|
| `#LINK_TODAY#` / `#LINK_YESTERDAY#` / `#LINK_TOMORROW#` | 今天/昨天/明天 `yyyy-MM-dd`（:767-769） |
| `#LINK_THISYEAR#` / `#LINK_THISYEAR2#` | `yyyy` / `yy`（:771-772） |
| `#LINK_THISMONTH#` / `#LINK_THISMONTH4#` | `MM` / `yyMM`（:773-774） |
| `#LINK_THISYEARMONTH#` / `#LINK_THISYEARMONTH6#` | `yyyy-MM` / `yyyyMM`（:776-777） |
| `#LINK_FIRSTDAY_THISMONTH#` / `#LINK_LASTDAY_THISMONTH#` | 本月首日 `yyyy-MM-01` / 月末（次日 1 日减 1 天）（:779-781） |
| `#LINK_LASTYEAR#` / `#LINK_LASTMONTH#` | 去年 `yyyy` / 上月 `MM`（:783-784） |
| `#LINK_LASTYEARMONTH#` / `#LINK_LASTYEARMONTH6#` | 去年同月 `yyyy-MM` / `yyyyMM`（:786-787） |
| `#LINK_FIRSTDAY_LASTMONTH#` / `#LINK_LASTDAY_LASTMONTH#` | 上月首日/末日（:789-791） |
| `#LINK_TODAY8#` | `yyyyMMdd`（:796） |
| `#LINK_TIMETICKS#` / `#LINK_TIMESTAMPMS#` / `#LINK_TIMESTAMPS#` | .NET Ticks / Unix 毫秒 / Unix 秒（:793/797/798） |
| `#LINK_TIMEHMS#` / `#LINK_TIMEHM#` | `HH:mm:ss` / `HH:mm`（:800-801） |
| `#LINK_FULLTIME#` | `yyyy-MM-dd HH:mm:ss.fff`（:803） |
| `#LINKDATE(年偏移,月偏移,日偏移,.NET格式)#` | 前三段 AddYears/AddMonths/AddDays（:806-825） |

### 数据集/多层数据（C 组）

| 占位符 | 语义 | 行号 |
|---|---|---|
| `##LINKECHARTDATASET##` | 当前模型 GDs 网格数据转 ECharts dataset 二维 JSON（首行列名数组 + 数据行） | SysDataModel.vb:6845-6849（生成 ：6926-） |
| `##LINKLEVELDATA##` | 当前模型自身 GetLevelData 的 JArray JSON | SysDataModel.vb:6852-6856 |
| `#LINKLEVELDATA(模型,编号[,参数…])#` | 实例化指定模型取 GetLevelData JArray；模型返回 Nothing → `"[]"` 兜底 | GlobalFormula.vb:615-651 |
| `#LINKXMLDATA(模型,编号[,参数…])#` | 同上取 GetXMLData XML；**无 Nothing 兜底**（与 JSON 形态行为差异：模型空返回时替换为空串或异常） | GlobalFormula.vb:654-685 |
| `#LINKJSON{JSONPath[,分段长,拼接串]}#` | 从当前 moreData（JToken 提交数据）按 JSONPath 取值；3 参形态按分段长切片重连（Oracle CLOB 场景） | SysDataModel.vb:6041-6109 |
| `#LINKARRAYITEM((路径)(JArray原文))#` | 双括号：第 2 括号=JSON Array 原文（`"null"`→空），第 1 括号逐元素 JSONPath 取值后**逗号拼接**（供 SQL IN） | GlobalFormula.vb:286-329 |

共用 JSONPath 取数工具：`GetJTokenString`（MLTShared2.vb:4685）。

### 变量/脚本复用（D 组）

| 占位符 | 语义 | 行号 |
|---|---|---|
| `#LINKSETVAL(名,值)#` / `#LINKGETVAL(名)#` | **进程内存字典，不落库**；键=`变量名+LoginID`；Win 客户端=整个运行期，IIS=应用池生命周期**跨请求共享**（仅靠 LoginID 区分用户，无并发锁）；取不到返回 `""` | GF.vb:431-480 → MLTShared2.vb:2214/2228 → Globle.vb:685 |
| `#LINKFUNC.名称[(参数…)]#` | 查 LINKFUNC 表（FUNCODE），参数按 `{0}{1}` 位置填充 → 脚本递归过 GlobalFormulaReplace → 按 FUNTYPE 分派：LINKFORMULA=DataTable.Compute / LINKSCRIPTGET=ExecScalar / LINKSCRIPTRUN=Exec；FUNCONN 空=默认连 LINKBI；SETPROCESS/FILEDIALOG 等内置类型不走表；**参数含逗号会被切错** | GF.vb:416-429 → MLTShared2.vb:2058-2185 |
| `#TotalLINKScript.编号.脚本类型(名1,值1,名2,值2…)#` | 从固定模型 `TOTALLINKSCRIPT` 取脚本（脚本类型=枚举名 BaseScript/CreateScript/DeleteScript/TreateScript）；变量**成对**消费，替换带引号的 `'@xxx'`→`'值'`；在所有其他占位符**之前**处理 | GF.vb:82-109；字段映射 SysDataModel4.vb:120-157 |
| `#_LINKSYS_.序号.字段#` | 系统内置模型 `_LINKSYS_`：执行该编号查询并取**第 0 行**指定列（多行只看第一行） | GF.vb:209-233 |

### 加密与 Token（E 组）

| 占位符 | 语义 | 行号 |
|---|---|---|
| `#LINKENCRYPT(内容)#` | 3DES-CBC+PKCS → Base64，**密钥硬编码** `lINKbipLUS`（可逆混淆，非安全加密） | GF.vb:974-1000 → MLTSimple3Des.vb:85-88 |
| `#LINKRSAENCRYPT(明文,公钥)#` | **双参**（HTML 单参有误）：公钥由第二参直接携带，Java 公钥转 .NET 后 RSA 加密；两参都不能含逗号 | GF.vb:591-612 |
| `#LINKTOKEN(用户代码)#` | 目标用户=当前用户 → 直接返回 dm.LinkToken；否则为该用户现造 LinkSpecial Token（存 SYSCODE 表 CODETYPE='TotalLINKToken'，按天滚动、默认 7 天有效）；**不校验调用者权限**（安全注意：任何脚本能触发替换即可为任意用户造 Token） | GF.vb:1226-1256 → MLTSimple3Des.vb:100-137 |
| `#LINKWEIXINTOKEN#` `#LINKDINGTALKTOKEN#` `#LINKBAIDUAITOKEN#` `#LINKFEISHUTOKEN#` | 微信/钉钉/百度/飞书 AI Token【未核对，直收】 | — |

### 集成/设备/路径（F 组，用户拍板直接收编，【未核对】）

`#LINKIOT.设备.项#`（设备信息采集）、`#LINKINFLUX(查询)#`（InfluxDB 采集信息）、`#LINKACTIVITY(…)#`（LINKFUNC 权限模式判断）、`#LINKSIGNSTEPSETTING(…)#`（审批 SIGNLIST 条件控制，返回提示信息）、`#LINKLOCATION#`/`#LINKLOCATIONJSON#`（简洁/完整地理位置）、`#LINKLOCALPATH#`（本地工作路径）、`#LOCALREPORTPATH#` / `#LINKEXPORTPATH#`（本地报表/导出路径）。

## 使用原则

1. 三套体系替换时机不同：`{N}` 在脚本格式化时替换、`#列#` 在行级动作时替换、`#LC.` 等在全局公式替换时处理。混用没有问题，但不要用错层（比如想在 SQLScript 全局查询里用行级 `#COL#`——没有行，替换不出值）。
2. 只用样例实证过的写法；样例没有的占位符先用源码验证再用。
