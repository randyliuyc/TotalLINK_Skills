# 模型 XML 字段全集（SysDataModelXML）

> 权威来源：`BaseLib/DataModel/SysDataModelXML.vb`（XmlSerializer 序列化）+ 精选样例（`samples/` 43 个，盘点 2026-10-29 / 2026-11-04）+ 全量语料（`samples-corpus/` 640 个）。
> 标注【无样例证据】的条目：样例中恒空，语义按代码线索推断——保持留空，不要臆造。

## 序列化习惯（生成 XML 必须遵守）

- 根元素 `<SysDataModelXML xmlns:xsd="..." xmlns:xsi="...">`，首行 `<?xml version="1.0"?>`（无 encoding 声明）。
- **所有元素一律输出**（含空值，写成自闭合 `<Tag />`），顺序固定（按 DTO 属性顺序）：`ModelCode, ModelNum, ModelDesc, KeyWords, DataMineCode, FunctionCode, ChartType, SQLScript, SQLUpdateScript, Ret1..Ret5, UseParameter, ConnString, ModuleCode, ParaLabel01..10, ParaType01..10, ParaSearchCode01..10, ParaDefVal01..10, SQLNew, SQLRemove, SQLClear, H5 系列, AllDataTreatTitle, CallFunction, JavaScript, ImageFile, ListPrint, MD5HASH, ModelSetting, ShowInMenu, SysModelFlag, CubeSetting?, DMUsage?`。
- bool 序列化为小写 `true`/`false`；数值为十进制文本（`0`）。
- 脚本中 `<` `>` 转义为 `&lt;` `&gt;`（XML 标准转义，工具会自动处理）。
- 缩进 2 空格/层。

## 标识与基础

| 元素 | 类型 | 说明 |
|------|------|------|
| `ModelCode` | string | 模型代码，与 `ModelNum` 组成落库双键。**必须由用户指定**。命名习惯见 `samples/README.md` |
| `ModelNum` | int | = `eModelAttachNum` 附加模型编号，编号段语义是**全平台约定**（权威定义 `LinkFunction/LinkDefine.cs:190-292`，全表见 `samples/README.md`）。AI 可按约定建议，用户确认后使用 |
| `ModelDesc` | string | 模型描述（样例为英文短语） |
| `KeyWords` | string | 【无样例证据】留空 |
| `DataMineCode` | string | **已废弃**，留空 |
| `FunctionCode` | string | 访问代码/权限组（落库列 `SEARCHGROUP`）。样例恒空（权限另行配置），保持留空 |
| `ChartType` | string | 图表类型（落库列 `SEARCHORDER`，列名错位见 `endpoints.md` 对照表）。样例恒空，语义已确认；保持留空 |
| `ShowInMenu` | bool | 样例恒 `false` |
| `SysModelFlag` | bool | **硬规则：必须 false**（样例全部为 false） |
| `MD5HASH` | string | 服务端重算。**警告：它不是整个文档的哈希**——盘点时发现内容不同的两个样例共享同一 MD5。生成时留空，比对时排除，绝不用于唯一性判断 |

## 脚本字段

| 元素 | 说明 |
|------|------|
| `SQLScript` | 基础查询脚本。首行放 `--LINKxxx` 标记；参数用 `{N}` 声明（见 `placeholders.md`） |
| `SQLUpdateScript` | 行编辑脚本。首行常见 `--LINKEDITMODE` / `--LINKSAVEONENTERKEY`；`WHERE ID=0#LINKROWID#` 定位行 |
| `SQLNew` | 新增记录脚本。首行 `--LINKADDNEWROWS`；常含 `#LOGIN_USER#`、`GETDATE()` |
| `SQLRemove` | 删除脚本。`DELETE ... WHERE ID=0#LINKROWID#` 或按业务键；需要防呆时改用「数据检查模型」（见 `callfunction-actions.md` 的 LINKPREVENT） |
| `SQLClear` | 界面「关闭/动作」脚本（落库语义：**多行数据处理**）。状态动作模型（Release/Frozen）、行级动作模型（Copy/Allocate）与 FB 表单保存都用它承载 UPDATE/INSERT，常配 `--LINKREFRESH` |
| `CallFunction` | CALLFUNCTION 动作脚本，见 `callfunction-actions.md`。样例中仅 1 处非空 |
| `JavaScript` | 前端脚本（APP 为主）。**非必填**：APP 语料 139 个模型中 26 个非空（约 19%）；钩子按名约定（`scan_para`/`beforeFunction`/`afterFunction` 等），清单与签名见 `js-hooks.md`。FB 侧仅 `contextTap`。顶层语句即页面初始化脚本。运行器/AI 模型留空 |
| `ModelSetting` | JSON 开关集合，完整键词汇表见 `modelsetting.md`（EditCols / EditValueList / paraDisabled / Before·AfterSaveAction / DataMineCondition 等） |
| `ListPrint` | 标签打印**表头**模板（LISTPrint=121，通过 `#TAG#` 嵌入 `H5Detail` 明细内容）。样例恒空；做标签打印时与 `H5Detail` 成对设计 |
| `AllDataTreatTitle` | 数据处理标题（落库列 `ALLDTTITLE`）。样例证据：`KEEWAYZUP1010X#700` 填 `批量删除`——多行批量操作时显示的操作标题 |
| `ImageFile` | **恒非空**：`#LINKRES#数字`（图标资源引用）。数字取 0~99 内随机即可（系统保留了一组图标，随机选用只为界面不单调），不必问用户 |

## 参数定义（01~10）

| 字段 | 说明 |
|------|------|
| `ParaLabel01~10` | 参数标签（英文/中文均见） |
| `ParaType01~10` | 权威词汇表 = `EParamType`（旧库 `GlobeEnum.vb:61-81`）：`DATEC8/DATEC10/DATEINT8/DATEVAL/DATETIME/DEC/STR/SPEECHSTR/PICKERSTR/DROPDOWN/DROPRELOAD/MOREFUNC`。语料实证：`STR`（多数）、`DATEVAL`（`KEEWAYZUP10#10`、`TMESPUR01#9`）、`DROPDOWN`（配 `ParaSearchCode` 指定下拉模型）。没把握的用法先查 `GlobeEnum.vb` 注释，再问用户 |
| `ParaSearchCode01~10` | 下拉来源。**样例证据：裸模型代码**（如 `ERAQACUS`，客户主数据下拉模型）——用于**查询参数区**的下拉 |
| `ParaDefVal01~10` | 默认值。样例用 `?` 表示「必填，需用户输入」。APP 语料有个别文件写全角 `？`（`KEEWAYZUP5010X#501`）——生成时统一写半角 `?` |
| `UseParameter` | 是否启用参数区。注意样例存在 `UseParameter=false` 但仍填 ParaLabel 的情况——不严格联动，以实际需求为准 |

**两套下拉体系**（易混）：查询参数区下拉 = `ParaSearchCode`（裸模型代码）；可编辑单元格下拉 = `ModelSetting.EditValueList`（「模型代码#序号」）。

## 其他

| 元素 | 说明 |
|------|------|
| `ConnString` | **连接代码**：模型脚本执行的目标数据库连接。空 = 默认连接（`BASE_DefaultConnString`，`SysDataModel.vb:510-512`）；样例值 `DATAQA`（多数）、`ERASTEEL`（跨库查供应商主数据）；`#link#` 前缀 = 强制从服务器端执行（L11003-11008）。**连接代码因环境而异，生成时问用户，默认提供 `LINK01`** |
| `ModuleCode` | DBNAME。【无样例证据】留空 |
| `Ret1` ~ `Ret5` | 样例恒 `0`，语义无证据。**保持 0，不要臆造** |

## H5 系列（APP / FB 消费的脚本族）

存量运行器样例全空；APP/FB 形态样例见 `samples-index.md`（克隆来源）。按 SKILL.md 硬规则 5：目标环境只做运行器/AI → 留空；含 APP/FB → 必须显式设计（从样例索引或存量模型克隆，服务端兜底已删除）。字段语义见 `endpoints.md` 的对照表与链路图；`H5Detail` 兼任标签打印明细（与 `ListPrint` 成对）。

语料盘点结论（2026-11-04，指导形态选型）：
- **界面形态由模板字段组合决定**，与 `ChartType`（SEARCHORDER）无关（APP 语料该列恒空）：`H5List` 非空 = 卡片列表；`H5GRIDHDR`+`H5GRIDDTL` 成对非空 = 表格模式（**少数派**：APP 语料 139 个模型仅 2 个）。
- APP 卡片模板 = mui HTML 片段（`<li id='#' class='mui-card'>` + `#列名#` 占位 + `linkquick`/`btnid` 内嵌按钮）；编辑模板 `H5EDIT` = `mui-input-row` 表单；参数区 `H5PARA` 控件 `value="{N}"` 直接绑定模型参数。
- FB 500 的 `H5PARA` 是 formSetting JSON（formtemplate/formData/tableData，`formbtns`/`selectData` 语料恒空，默认留空）；查询区 UI 不在 H5PARA，在 LINKMENUITEM 菜单注册模型的 `paraCustom`（见 `samples-index.md` TMESPUR029X#500 条目）。

## 子列表

### `CubeSetting`（List\<DMCubeSetting\>，对应 LINKCUBESETTING）

列级显示配置。样例规律：
- **每列 × 每语言一条**（`COLTYPE` = `LANGUAGE-<语言代码>` 成对），`CAPTION` 为对应语言标题。**语言集合询问用户：默认 `zh` + `en`；需要更多语言时由用户提供语言代码（如 `vi`），写作 `LANGUAGE-vi`**；
- 保留列也要配置：`LINKRESERVE_DMTITLE`、`LINKRESERVE_DMPARA01~06`（参数标题）、`LINKROWID`；
- `FORMULA` 样例中个别列填 `X`——为历史遗留（字段曾配翻译对照后删除），**生成时一律留空，不要模仿**；
- 无成员时输出 `<CubeSetting />`，少数文件整个省略该元素。

### `DMUsage`（List\<DMUsage\>，模型使用说明，AI 双语料）

`DMCODE`/`DMNUM`/`SCRIPT`/`DMUSAGE`。样例 `SCRIPT` 取值：**0=查询、3=删除、4=动作/更新**。`DMUSAGE` 文本约定（对 AI 与人都可读）：

```text
功能一句话说明
- 注意事项/前置条件

params: ["参数1说明", "参数2说明"]      # 有模型参数时
rowData: {"列名": "说明"}               # 行级动作时
```

**新模型默认留空**（输出 `<DMUsage />` 或不带该元素）；仅当用户明确要求补充使用说明时才按上述格式填写。

## 导入落库行为（须知）

`SetXMLData`（`SysDataModel.vb`）：目标编号不存在则 `INSERT INTO SYSSEARCH`，否则 `UPDATE`；且**无条件 DELETE 并重写** `LINKCUBESETTING`、`SYSDMUSAGE`。落库定位用实例的 `ModelCode/ModelNumber`，XML 内嵌编号不参与定位（`model import --code/--num` 传入的编号优先，见 SKILL.md）。
