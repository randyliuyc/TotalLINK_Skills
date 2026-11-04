# 模型内容 × 服务端端点契约（endpoints）

> 事实来源：旧版服务端（`LINK/BaseLib/DataModel/SysDataModel*.vb`、`LINKIIS/Controllers/DataModelController.cs`、`LINKIIS/Controllers/LINKController.cs`），已与迁移项目 LINK.Core 交叉核对（11/12 条一致，差异见文末「与迁移实现的已知差异」）。
> 行号均指旧库文件。本文回答一个问题：**模型里的每个属性是如何被执行的、如何影响消费方返回的数据**。

## 总原则

- 模型 = 主模型 + 一组附加模型（`{主模型代码}{主模型编号}X` 代码下的 `SEARCHNUM` 分段记录，编号段语义见 `samples/README.md`）。
- 脚本"非空"本身就是开关：查询/新增/编辑/删除/动作脚本写了，按钮和功能就出现；不写就没有。没有单独的"按钮配置"。
- FB 与 APP 消费**同一批端点、同一份模型定义**；差异只在内容模板的形态（HTML 片段 vs JSON 表单）。
- `linkDMAIAction`（AI 调用）`scriptType=0` 时只执行 `SEARCHSELECT`，不读任何 `H5*` 字段；非 0 转发提交链路（`DataModelController.cs:151,157`）。所以模型的查询脚本必须独立自洽，才能同时被 AI 调用。

## APP 框架调用链（linkDMH5Data → H5Data）

APP 是壳，页面内容全部来自服务端返回的 HTML 片段与原始数据。

```
linkDMH5Data(dmCode, dmNum, Para, scriptType)          DataModelController.cs:951
 └─ H5Data(scriptType, idTag)                           SysDataModel.vb:4496-4560
     ├─ H5BatchDataListWithGDs(1, scriptType)           SysDataModel.vb:4621-4698   ← 列表正文
     │   ├─ DatasetResult → 执行 SEARCHSELECT            // 数据
     │   ├─ H5GRIDHDR 非空 → H5GridContent（表格模式：H5GRIDHDR 表头 + H5GRIDDTL 行模板×每行）
     │   │            否则 → H5List 模板 × 每行数据       // 模板填数
     │   ├─ H5MaxLines × batches 截断，尾接 #moredata N / endofdata 分页标记
     │   └─ --LINKDETAILLIST(code,num,para...) → 拉子模型数据 + 子模型 H5List，嵌入每行   :4644-4660
     ├─ DataStru = {列名: 类型}（来自查询结果列）          // APP 据此生成编辑控件     :4520
     ├─ FunList = 功能按钮 <li> 串（派生规则见下表）       SysDataModel.vb:4763-4843
     ├─ ContextMenuList = 501~520 附加模型 → <li id="501" linkrefresh linkparafill linklocation linkimage>   :12224-12280
     ├─ URLList = 601~650 → <li linktype=...>（ConnString=LINKMAP 特判成 id=linkmap）  :12287-12303
     ├─ DataMineList = SYSDM 行 → <li echartflag=0|1 class=linkdatalist|linkchart>     :4850-4881
     ├─ NewRecList = H5NewRec 模板（仅 AllowAddnew 时）
     ├─ ParaList = H5PARA 模板填上次参数/公式值            :4903-4923
     └─ js = JAVASCRIPT（占位符已展开）                    :4554
```

**FunList 派生规则**（按钮 ⇔ 脚本非空 + 权限，`SysDataModel.vb:4763-4843`、`SysDataModel3.vb:442-629`）：

| APP 按钮 | 出现条件 |
|---|---|
| 添加 | `SQLNew` 非空（含 `--LINKADDNEWROWS` 时反而不显示，改为编辑态加行）+ `FuncAvaiable("NEW")` |
| 编辑 | `SEARCHWHERE`（XML 元素 `SQLUpdateScript`）非空 + `FuncAvaiable("EDIT")` |
| 删除 | `SQLRemove` 非空 + `FuncAvaiable("REMOVE")` |
| 预处理 / 后处理 | 存在 21~30 / 41~50 附加模型（标题取其描述） |
| 打印 | `H5DETAIL` 或 `ListPrint` 非空（H5DETAIL 双用途：TAGPrint=102 的映射列，`SysDataModel.vb:3578`） |

定位占位符同理：`#LINKLOCATION#`/`#LINKLOCATIONJSON#` 出现在新增/编辑脚本里 ⇔ APP 传回定位信息（`SysDataModel3.vb:486-494,601-610`）。

**语料证据（2026-11-04，KEEWAYZUPPDA 139 个模型）**：
- 界面形态由模板字段组合决定，与 `ChartType`/SEARCHORDER 无关（该列恒空）：`H5LIST` 非空 = 卡片列表；`H5GRIDHDR`+`H5GRIDDTL` 成对 = 表格模式（仅 2/139，少数派；HDR 是组头模板、末尾放 `#LINKTABLEROWS#`，DTL 是行模板）。
- 按钮 除了 FunList 派生，卡片/表格模板内还能放内嵌按钮（`linkquick="8" btnid="501" linkparafill="0" linkrefresh="1"`）直接触发附加动作。
- `js`（JAVASCRIPT）承载前端钩子（`scan_para`/`beforeFunction`/`afterFunction` 等），钩子清单见 `js-hooks.md`。

特殊 `ConnString`：`LINKURL`/`LINKURLINTERNAL` → `Data` 返回 SEARCHSELECT 脚本文本本身当 URL、`URLList`=ConnCode（`SysDataModel.vb:4504-4511`）。

## FB 表单框架调用链（linkDMFormData → FormData）

一个 FB 表单页 = 页面骨架 + 表单定义 + 单行数据 + 子模型（明细/下拉），四层拼装：

```
linkDMFormData(dmCode, dmNum, Para)                     DataModelController.cs:3093
 └─ FormData()                                          SysDataModel2.vb:39-208
     ├─ ① 主模型 SEARCHSELECT → 取 1 行数据（RDs）        // 数据源：按单号/主键过滤的单行查询
     ├─ ② 500 附加模型（FormSetting）
     │   ├─ H5PARA       = 表单设置 JSON（formSetting）   // 表单的"定义"
     │   └─ SEARCHSELECT = formData 定义，替换字面量 "#FORMDATA#"（带双引号！）  :57-58
     ├─ ③ ReplaceRowDataJson + GlobalFormulaReplace      // #列名# 与公式填进 formSetting  :78-79
     ├─ ④ tableData：formSetting 里每个子表 {dmCode,dmNum,Para}
     │        → DetailFormDataByDM 拉子模型数据填充（oriTableData=true 时直用数组）      :97-127
     ├─ ⑤ $.formtemplate → SELECT MODJSON FROM LINKFORMMOD（页面骨架）
     │        → 骨架的 formData/tableData 换成真实数据                                    :129-155
     ├─ ⑥ selectList：{node, dataValue, dataText, data:{dmCode,dmNum,Para}}
     │        → GetSelectData 替换为实际下拉数据                                          :216-249
     └─ ⑦ formbtns 合并进骨架 btns → 返回 {formData, tableData, btns, ...}              :189-200
```

两个易错点：
1. `"#FORMDATA#"` 替换是**带双引号的字面量**——500 模型的 SEARCHSELECT 里 formData 必须以 JSON 字符串值形式嵌在 formSetting 中，写法错则替换不上，返回 `{}` 且 Status 仍为 true（静默失败）。
2. 主模型 SEARCHSELECT 返回多行时**只取第 1 行**（`GetGridDataFromDS(ds, 1)`）——FB 表单模型的查询脚本必须按业务键过滤到单行。

**语料证据（2026-11-04，TMESPUR 259 个模型，其中 21 个 #500）**：
- formSetting 写法 21 处高度一致：`formtemplate` 形如 `MOD220500008`（指向 LINKFORMMOD 骨架）；`formData` 全部是 `"#FORMDATA#"` 字面量（无直接 JSON 变体）；**`formbtns` 与 `selectData` 全部为空**——生成时默认空数组/空对象，按钮逻辑由 #501+ 动作模型与骨架 btns 承担。
- `tableData` 键名：业务表用 `TABLE_1`/`TABLE_2`，保留名 `LINKDOCLIST`（附件，`LINKFLOW#25`）与 `LINKSIGNLIST`（签核，`LINKFLOW#21`）。
- **菜单/列表注册是独立链路**：`XXX9X#500`（描述「菜单设置/List」）`ConnString=LINKMENUITEM`，SQLScript 直接是列表页配置 JSON（title/path/column/paraData/paraCustom）——FB 查询参数区的控件 UI 由这里的 `paraCustom` 定义，不在 H5PARA。
- **FB 按钮 action ↔ 端点对照**（与 `formbuilder-json-generator` 的按钮配置互证）：按钮 `action.api` 0=取模型数据、1=提交单行、2=附加功能、3=提交多行、4=取公式、5=载入模板/跳转刷新、6=提交全部数据（→ `linkDMDataSubmit` 走主模型 `SQLClear`，语料 `#700-API=6` 附加模型即此机制的模型侧落点）、7=取级联、8=取图表。`formbtns` 恒空时这套机制不启用，按钮逻辑回落到 #501+ 模型。

**保存回写**：`linkDMDataSubmit` 无 scriptType，固定执行主模型 `TreateScript`（`SQLClear`），`data.formData` 整包作 moreData 传入（`SysDataModel.cs`(Core) :6762-6796；旧库同构）。FB 表单的保存 SQL 写在主模型 `SQLClear`，防呆配 1000 号检查模型。

## APP vs FB 对照

| | APP（linkDMH5Data） | FB（linkDMFormData） |
|---|---|---|
| 内容模板 | `H5List`/`H5GRIDHDR/DTL`（HTML 片段） | 500 的 `H5PARA`(JSON) + `LINKFORMMOD` 骨架 |
| 数据 | 多行列表，`H5MaxLines` 分页 | 单行表单 + 子模型明细表/下拉 |
| 按钮 | 派生（脚本非空即出现）+ 模板内嵌按钮（linkquick/btnid） | formSetting 的 `formbtns`（语料恒空）+ 骨架 `btns`；实际按钮逻辑由 #501+ 动作模型承担 |
| 保存 | `linkDMGridDataSubmit` 等按 scriptType 选脚本 | `linkDMDataSubmit` 固定走主模型 `SQLClear` |
| 联动 | `--LINKDETAILLIST`、501~520、SYSDM | `tableData`、`selectList` 引用子模型 |

## 能力组 × 端点 × 模型内容（总表）

| 能力组 | 端点 | 依赖的模型内容 | 决定返回结果的什么 |
|---|---|---|---|
| ① 列表/网格取数 | `linkDMData`、`linkDMDataWithLastParams`、`linkDMH5BatchDataListWithGDs`、`linkDMDatasetResult` | `SEARCHSELECT`、参数、`H5LIST`、`H5GRIDHDR`、`H5GRIDDTL`、`H5MAXLINES`、`--LINKDETAILLIST`、ModelSetting(`dataReplace/dataFill/filterRows`)、`LINKCUBESETTING` | `Data`/`DataList`（HTML 串）、分页标记、列标题 |
| ② 表单（FB） | `linkDMFormData`、`linkFormMenuSetting` | 500 附加记录的 `SEARCHSELECT`(JSON) + `H5PARA`、`LINKFORMMOD.MODJSON` | 表单 JSON（formData/tableData/btns/selectList） |
| ③ 编辑视图 | `linkDMEditList` | `H5EDIT`、ModelSetting `EditCols`/`EditValueList`、`SEARCHSELECT` 列结构 | 编辑表单 HTML；`RDs` 为空返回 `"No data found."` |
| ④ 提交 | `linkDMGridDataSubmit`、`linkDMGridRowSubmit`、`linkDMDataSubmit`、`linkDMFileUpload` | `SQLNew`/`SEARCHWHERE`/`SQLRemove`/`SQLClear`/`CallFunction` + 附加 1~10 同步 + 11~20/31~40 前后置 + `--LINKCALLFUNCTION`/`--LINKUPDATESCRIPT`/`--LINKMULTIROWS` | 逐行/单行、执行哪个脚本、`data=int` 与 `message` |
| ⑤ 动作/防呆 | `linkDMContextFunBack`、`linkDMContextActionInfo`、`linkDMConditionAction`、`linkDMPre/PostProcessByGridDataBack`、`linkDMAttachURLFunction` | 501~520（动作脚本用 `SQLCLEAR` 承载）、1000（`LINKPREVENT/LINKCONFIRM/LINKWARNING` → type=3/2/1）、21~30/41~50、提示模型 `+2000`、`--LINKREFRESH` | `type/condition/message`、`funType`、跳转目标 |
| ⑥ 参数区 | `linkDMH5ParaListJS`、`linkDMH5AttachParaListJS` | `H5PARA`、`JAVASCRIPT`、`ParaDefVal` 公式、`SYSSEARCHVAL` 上次参数 | 参数表单 HTML + `js`；`Para` 为空先回填上次参数 |
| ⑦ 图表/挖掘/多层级 | `linkDMEChartScript`、`linkDMDataMine`、`linkDMLevelData` | `H5CHART`、`SYSDM`(DMLINE/PARA01-10)、ModelSetting `leveldatasetting` | 图表脚本串、下钻目标模型、树形 `children` |
| ⑧ 登录/公式 | `linkUserLogin(API)`、`linkUserByToken`、`linkPwdChange`、`linkDeviceReg`、`linkFormula` | 与模型无关（`SYSUSER/SYSCODE/SYSLOGIN/SYSCONN`） | `linkFormula` 决定脚本里能用哪些 `#...#` 公式（`#SYSUSER.列#`、`#LINKCONN.code#`；无模型列占位符） |

### 关键映射（排查时按列名找）

- 脚本类型枚举（`LinkDefine.cs:427-459`）：`0=SEARCHSELECT, 1=SQLNEW, 2=SEARCHWHERE(XML 的 SQLUpdateScript), 3=SQLREMOVE, 4=SQLCLEAR, 101=H5LIST, 102=H5DETAIL, 103=H5EDIT, 104=H5CHART, 105=H5NEWREC, 106=H5PARA, 107=H5ATTPARA, 108=H5GRIDHDR, 109=H5GRIDDTL, 111=CALLFUNCTION, 112=JAVASCRIPT, 113=MODELSETTING, 121=LISTPRINT`。
- `Script(type)`→SYSSEARCH 列映射：`SysDataModel.vb:543-547, 3548-3572`。**没有 SQLUPDATE 列，编辑脚本落库在 SEARCHWHERE**。
- 参数四件套（`ParaLabel/ParaType/ParaSearchCode/ParaDefVal` 01~10）在 `SYSSEARCH` 表（`PARAMLABEL01~10` 等，`SysDataModel.vb:7169-7259`）。`LINKCONTENTLIST` 参数模板生成逻辑**不采用**（见排除项）。

### XML 元素 ↔ SYSSEARCH 列名对照（库级诊断用）

> 历史原因，部分列名与模型含义不对应（权威依据：SYSSEARCH 列语义对照表）。**生成 XML 按左列元素名写不变；库级排查（`model dict` 查 SYSSEARCH、手工 SQL）按右列找。**

| XML 元素 | SYSSEARCH 列 | 含义 | 备注 |
|---|---|---|---|
| `ModelCode` / `ModelNum` / `ModelDesc` | `SEARCHCODE` / `SEARCHNUM` / `SEARCHDESC` | 模型代码 / 顺序号 / 描述 | |
| `SQLScript` | `SEARCHSELECT` | 基本模型脚本 | |
| `SQLUpdateScript` | `SEARCHWHERE` | **更新记录** | 无 SQLUPDATE 列 |
| `SQLNew` / `SQLRemove` | `SQLNEW` / `SQLREMOVE` | 添加 / 删除记录 | |
| `SQLClear` | `SQLCLEAR` | **多行数据处理** | AllDataTreat 与动作脚本承载 |
| `UseParameter` | `USEADDICOND` | 使用参数（参数区开关） | ⚠️ 列名错位 |
| `ChartType` | `SEARCHORDER` | 图表类型 | ⚠️ 列名错位 |
| `FunctionCode` | `SEARCHGROUP` | 访问代码（权限组） | ⚠️ 列名错位 |
| `ConnString` | `CONNSTRING` | 数据连接 | |
| `ParaLabel/Type/SearchCode/DefVal 01~10` | `PARAMLABEL/PARAMTYPE/PARAMSEARCH/PARAMDEFVAL 01~10` | 参数名/类型/搜索/值 | |
| `SysModelFlag` | `SYSMODELFLAG` | 系统模型 | 必须 false |
| `H5List` / `H5GridHeader` / `H5GridDetail` | `H5LIST` / `H5GRIDHDR` / `H5GRIDDTL` | 数据列表 / 表格头 / 表格明细 | |
| `ListPrint` + `H5Detail` | `LISTPRINT` + `H5DETAIL` | **标签头 + 标签明细** | 标签打印成对模板，H5DETAIL 兼 TAGPrint=102 |
| `H5Edit` / `H5Chart` / `H5MaxLines` | `H5EDIT` / `H5CHART` / `H5MAXLINES` | 编辑脚本 / 图表脚本 / 最大行数 | |
| `AllDataTreatTitle` | `ALLDTTITLE` | 数据处理标题 | |
| `H5NewRec` / `H5Para` / `H5AttPara` | `H5NEWREC` / `H5PARA` / `H5ATTPARA` | 添加记录脚本 / 参数脚本 / 附加参数脚本 | |
| `CallFunction` / `JavaScript` / `ModelSetting` / `MD5HASH` | 同名 | | |
| — | `ID` | 行主键 | 脚本里 `#LINKROWID#` 指查询结果行的 ID 列 |
- `ParaDefVal` 首字符 `?` = 必填，同时决定附加模型是否需要人工补参（`ParamsFillManully`，`SysDataModel.vb:12311-12337`）。

## 排除项（不在 model design 范围，防止误查）

- **FB 菜单可见性链**：`SHOWINMENU`、`SYSMENU.APIFLG`、`SYSROLEMENU.ACCESSFLAG`、`LINK_FN_FUN_ACTIVE`——属部署配置，不是模型内容。
- **LINKCONTENTLIST 参数模板生成**：参数区以模型自身 `H5PARA` 内容为准。
- `linkDeviceID`：纯桩成功，与任何表无关。
- `linkDMAttachURLFunction`：不做 LinkToken 校验（`DataModelController.cs:2010-2014`）。

## 与迁移实现（LINK.Core）的已知差异

仅记录，不影响本 Skill 的模型设计规则：

1. `#LC.xxx#`：旧库走 `CusSetting("LINKCONST")`，与 dm 是否为 null 无关；LINK.Core 的 `GetLinkConstValue` 带 CUSCODE 过滤、`GlobalFormula` 里 dm=null 时替换为空。
2. `#SYSUSER.列#`：旧库按 DataRow 列名取值（未知列返回 `ColNotExist`）；LINK.Core 有显式白名单。
3. H5 空模板兜底（`H5ParaListTemplate`/`GetDefH5ModelScript` 等）：旧库存在；LINK.Core 已按决策删除，模板为空返回空。本 Skill 由此规定：**H5 模板必须显式设计，不依赖兜底**。
