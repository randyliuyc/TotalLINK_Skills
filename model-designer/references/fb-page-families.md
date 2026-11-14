# FB 页面族组织（.A/.B × .H/.L 多族结构）

> 依据：2026-11-05 用户提供的标杆语料 `samples-corpus/TAMPERFB/`（TMESEXC05 领料申请，22 模型，用户认定为典型 FormBuilder 表单设计模型组）。
> 2026-11-12 增补：Formbuilder 混淆前前端源码（`TotalLINKFB/src`）核实，见 §7——族命名是**建模/菜单注册侧约定**，前端不做任何族派生。
> 本文件**修正并细化**旧结论「FB 表单必须有 500 伴生模型」——单一 500 形态的认知不成立。

## 1. 双层族命名约定（ModelCode 含 `.` 的页面族）

一个 FB 页面组按「页面 × 数据」两个维度拆成多个族：

| 后缀 | 维度 | 含义 |
|------|------|------|
| `.A*` | 页面 | **列表页**（A=list 页） |
| `.B*` | 页面 | **详情页**（B=detail 页） |
| `.xH` | 数据 | 表头（header） |
| `.xL` | 数据 | 明细/列表行（line） |

组合出的四个族（以 TMESEXC05 为例）：

| 族 | 角色 | #10 主模型内容 | 伴生码 |
|----|------|---------------|--------|
| `TMESEXC0510X.AH` | 列表页-查询参数 | 8 个查询参数模型（返回 `P*` 列，`UseParameter=true`） | `TMESEXC0510X.AH10X` |
| `TMESEXC0510X.AL` | 列表页-数据 | 表头+明细 JOIN 的列表 SELECT | `TMESEXC0510X.AL10X` |
| `TMESEXC0510X.BH` | 详情页-表头 | SELECT MFGPKH + **SQLUpdateScript=MERGE INTO**（表单保存）+ SQLRemove 删头 | `TMESEXC0510X.BH10X` |
| `TMESEXC0510X.BL` | 详情页-明细行 | SELECT MFGPKL + MERGE INTO（行保存），`LINKROWID` 用 `DOCNUM+DOCLIN` 拼接 | `TMESEXC0510X.BL10X` |

- **族伴生模型码 = 族码 + `10X`**（如 `TMESEXC0510X.AH10X`）——与「主模型代码+主模型编号+X」的通用规则一致，只是这里族码本身已含 `.`。
- 根模型 `TMESEXC05#10`（无 `.`）是旧式工作流审批卡片（mui-card + 审批按钮 JS 指向 `LINKWFTASKPR`），SQLScript 允许 `SELECT '标题'` 纯占位——与页面族同码体系共存。区分「根模型 #10」与「族 #10」两种形态。
- 菜单/列表行点击把行值传给详情族：**前端机制**（2026-11-12 源码核实，§7）——详情模型取菜单 `code2/num2`（行字段 `LINKDMCODE/LINKDMNUM` 可覆盖），行值经 `RDs=cObj(row)` 伴随查询、菜单/按钮参数用 `{字段}`（主表 formData）与 `[字段]`（当前行）占位；脚本侧的 `#列名#` 行级令牌由引擎在服务端替换，**不进前端**——两层语法分层，勿混写。

## 2. 五种 #500 形态（FormSetting 编号段的实际用法）

一个页面组的 500 不止一个：每个族的伴生码下各挂自己的 500，形态由内容决定：

| 形态 | 实例 | SQLScript 内容 | H5Para |
|------|------|---------------|--------|
| **List（菜单注册）** | `TMESEXC0510X#500-List` | 菜单 JSON（见 §3），`ConnString=LINKMENUITEM` | 空 |
| **Para（查询区 formSetting）** | `X.AH10X#500` | 参数回填映射 JSON：`"PCONTEXT":"#PCONTEXT#"` … | **formbuilder JSON**（formtemplate `MOD260300003`） |
| **Document（行传参映射）** | `X.AL10X#500` | 列表全部输出列 → `#列名#` 的映射 JSON，供详情页接参 | 空 |
| **表单设置（表头 formSetting）** | `X.BH10X#500` | 表头字段映射 JSON | **formbuilder JSON**（formtemplate `MOD260300002`） |
| **表格设置（明细 formSetting）** | `X.BL10X#500` | 明细行字段映射 JSON | 空 |

要点：

- **formbuilder JSON 只出现在 Para / 表单设置两种 500 的 H5Para**。H5Para 键表按后端 `FormData()` 实读修正（`LINK.Core SysDataModel.cs:5338-5500`，2026-11-12 源码核实）：`formtemplate`（MOD26xxxxxxx，服务端 `SELECT MODJSON FROM LINKFORMMOD` 取骨架 :5429-5431）、`formData:"#FORMDATA#"`（**必须带双引号的字面量**，服务端用 500 模型 BaseScript 产物整体替换 :5357-5358）、`tableData`（子表定义 dmCode/dmNum/Para/oriTableData :5395-5422）、`selectList`（动态下拉 {node,dataValue,dataText,data}，:5515）、`formbtns`。**「formbtns 恒空」是语料观察不是代码约束**：后端会把 `formbtns` 合并进骨架 `btns`（仅当 MODJSON 已含 btns 数组，:5492-5500），FB 设计器共享按钮功能也读它（`TotalLINKFB/src/components/plusin/example/btns.vue:3042-3056`，经 LINKFORM/40）。语料里出现的 `selectData:{}` 键**后端不读**——那是 FB 设计器 jsonData 的「数据统一」下拉缓存键（懒加载写入），与后端键 `selectList` 是两个东西
- `tableData` 的键即表格区数据源：`TABLE_1` → 列表/明细模型（带 `Para` 数组，元素是 `#列名#` 行级令牌）。`LINKDOCLIST`/`LINKSIGNLIST` 是**键名约定（语料观察），源码无任何特殊分支**（FB 前端、LINK.Core、LINK(VB) 三处 0 命中）——`LINKDOCLIST → LINKFLOW#25` 这类映射照常写进 tableData 的 dmCode/dmNum 即可，引擎不看键名。签核有专门的独立键：`signFormSetting`（签核子表单分支，:5379-5390）与 `signbtns`（签核按钮合并，:5470-5488），不在 tableData 里
- 字段映射 JSON（SQLScript）不经 string.Format 执行，花括号是结构本身（validate 已豁免）

## 3. 菜单注册 JSON 契约（500-List，ConnString=LINKMENUITEM）

```json
{
    "title":"#MENUTITLE#",
    "path":"/#PARENTNO#/#DMCODE##DMNUM#",
    "code":"TMESEXC0510X.AH",      ← 入口指向列表页参数族 #10
    "num":"10",
    "para":"{X}",
    "icon":"#MENUICON#",
    "paraData":{ "showType":"detail" }
}
```

- 可用占位符：`#MENUTITLE#` / `#PARENTNO#` / `#DMCODE##DMNUM#` / `#MENUICON#`
- `code`/`num` 指向**列表页参数族**（`.AH#10`），不是数据族；`showType:"detail"` 声明详情页跳转模式
- **前端只消费一个菜单接口**：`linkFormItems`（`TotalLINKFB/src/api/api.js:199-204` → 动态路由 `store/modules/user.js:166-183` + `router/index.js:247-318`）。`linkFormMenu`/`linkFormMenuSetting` 在 FB 前端**定义后未接线**（`getFormMenuSet` 还有 `&dmnum` 缺 `=` 的 bug）——菜单 JSON 消费字段以 `router/index.js` 的 meta 键为准：`code/code2/num/num2/para/paraData/paraCustom/attach/column/href/type` 等

## 4. 动作模型模式（#501/#502/#503）

- **确认/关闭/行关闭类动作**：`SQLScript`/`SQLUpdateScript` 全空，**UPDATE 写在 SQLClear**（如 `BH10X#501-确认`：更新 MFGPKL 行状态 + MFGPKH `DOCSTA=2`；`#502-关闭`：头行 `CLOSTA=1` + `CLOREA='#CLOREA#'`）。按钮 `script="4"` 消费 SQLClear，与 APP 侧契约一致
- **单据打印**：`CallFunction` 承载 `CALLFUNCTION~FILEEXPORT~` + JSON（`fileType:"REPORT.PDF"`、`reportFile:#LINKREPORTPATH#\表名.rdlx`、`connString:["#LINKCONN.连接码#"]`、`para:["#DOCNUM#"]`）
- **外部接口调用**：`CALLFUNCTION~LINKRESTAPI~` + REST JSON（`ClientURL/Method/Header/JsonBody/resultFormula/resultList`，取响应字段用 `#LINKJSONVALUE:$.path#`）——**密钥类字段不能硬编码进模型，向用户索取或走系统配置**
- **按钮防呆**：`#700` 按钮控制模型 SQLScript 用 `#LINKSCRIPTGET@连接:...#` 包标量 SELECT，返回 `'LINKPREVENT:原因'` 或空串（与 `app-buttons.md` §1② 同构）；**注意 #700 双语义**——`X.AH10X#700-单据状态` 是普通 SELECT 状态选项数据源，按内容区分，不按编号

## 5. SQL 风格（FB 族语料确立）

- SELECT 一律大写英文列名/表列名，无中文显示别名；日期统一 `CONVERT(VARCHAR(16),...,21)`；计算列英文别名
- 写脚本惯例：MERGE INTO + `N'#字段#'`（回写）、`N'@字段@'`（新行占位）、数值列 `0#字段#` 强转、`SQLUpdateScript` 头部 `--LINKADDNEWROWS` + `--LINKAUTOREPLACEEMPTYCOLUMNS`（源码允许，见 `link-flags.md`）
- **CubeSetting 在 FB 族不是结果集投影**：主模型 SQL 仅 1 列而 CubeSetting 枚举数十列（表结构派生元数据 + `LINKRESERVE_DMTITLE` 多语言标题）。`datasearch-windows.md` 的「COLNAME=结果集列名」契约**仅适用于开窗/列表数据源场景**，不适用于 FB 页面族的 formSetting 模型
- **CubeSetting 是引擎/服务端内部数据，FB 前端零消费**（2026-11-12 源码核实：`TotalLINKFB/src` 全库 `CubeSetting/CAPTION/COLNAME` 0 命中）。FB 的列标题/格式实际来自三处：菜单 JSON 的 `column` 配置、**`LINKFORM#10` 模型返回的 `FATJSON`**（列格式，用户可在列表页改列格式后回写：`getUserItemBack("LINKFORM",10,2,...)`，`views/lists/index.vue:967-968`）、表单模板内嵌 label。CubeSetting 只影响引擎侧（如 AI 调用、`model run` 的 `captions`）

## 6. 生成清单（搭 FB 页面组前自查）

- [ ] 按「页面×数据」拆族并命名 `.AH/.AL/.BH/.BL`，族伴生码 = 族码+`10X`
- [ ] 每族 #10 主模型 + #500 伴生模型（形态按 §2 对号入座）
- [ ] 菜单注册 500-List 指向 `.AH#10`；详情接参走 Document 映射
- [ ] 动作模型 UPDATE 写 SQLClear；防呆配 #700（LINKPREVENT 型）
- [ ] formbuilder JSON 只写进 Para/表单设置的 H5Para；formtemplate 问用户取号或克隆存量

## 7. FB 前端机制（2026-11-12 混淆前源码核实）

> 来源：`TotalLINKFB/src`（Vue2；设计器 = `views/table/index.vue`，运行时 = `views/forms/index.vue` + `views/lists/index.vue`）。待验项 D7（formtemplate 生成/解析链路）由此关闭。

**路由与页面族**：前端**没有任何 `.A/.B/.H/.L/10X` 族派生逻辑**（全库 0 命中族运算）。页面分发依据全部是菜单 JSON 显式字段 + 行数据字段：

| 场景 | 取值 | 源码 |
|---|---|---|
| 列表页 | 菜单 meta `code`/`num`（缺省 `num=9`） | `TotalLINKFB/src/router/index.js:230,269` |
| 详情页 | 菜单 meta `code2`/`num2`（缺省 `num2=10`），行字段 `LINKDMCODE`/`LINKDMNUM`/`LINKDMPARA` 可覆盖 | `router/index.js:269` + `views/lists/index.vue:1466-1479` |
| 菜单 type=="custom" | 进 formbuilder 设计器（`views/table/index.vue`） | `router/index.js:191-197` |
| 有 children | 进 `views/common/index` | `router/index.js:296` |

族命名（`.AH/.AL/.BH/.BL`、伴生 `10X`）因此是**建模与菜单注册侧的数据约定**（服务端菜单生成按它产出 meta），前端只是被动接收 `num` 值——生成模型族时仍按 §1 命名，但排查页面跳转问题查菜单 JSON 与行字段，不是前端代码。

**表头/明细**：前端不按 `.H/.L` 分页面——FB 内是同一模板的主表（`formData`）+ 子表（`tableData`）结构。主子表提交三通道：

| 通道 | action.api | 数据组装 | 源码 |
|---|---|---|---|
| 一次全部提交 | 6 → `linkDMDataSubmit` | `linkConcat`：`{…tableData(各子表), formData(主表∪当前操作)}`，`e.allTable` 提交子表全部行不过滤 | `views/forms/index.vue:9405-9423` + `api.js:266-283` |
| 分明细提交 | 3 → `linkDMGridDataSubmit` | **GDs=单张子表行集**（`e.para`=子表键），每行回填主表外键 `e.attach\|\|'DOCNUM'`；RDs=主表 formData。注意实参顺序与函数签名直觉相反 | `views/forms/index.vue:8974-8995、8007` |
| 单行提交 | 1 → `linkDMGridRowSubmit` | RDs=formData∪当前行对象 | `api.js:245-264` |

**行传参语法（前端）**：按钮/菜单参数占位是 `{字段}`（取主表 formData）与 `[字段]`（取当前行，无值回退 formData），见 `TotalLINKFB/src/utils/mybase.js:696-717`。`#列名#` 是引擎侧脚本令牌（服务端 GlobalFormula 替换），前端不做 `#…#` 替换（`api.js:220` 把 `#公式#` 原样上送 `linkFormula` 可证）——两层语法分层，别在按钮参数里写 `#列名#`。
