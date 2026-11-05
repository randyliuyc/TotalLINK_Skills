# FB 页面族组织（.A/.B × .H/.L 多族结构）

> 依据：2026-11-05 用户提供的标杆语料 `samples-corpus/TAMPERFB/`（TMESEXC05 领料申请，22 模型，用户认定为典型 FormBuilder 表单设计模型组）。
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
- 菜单/列表行点击把行值传给详情族：列表行 → `#列名#` 映射 → 详情族 `#10` 的 SQLScript 直接用行级 `#DOCNUM#` 占位（FB 页面上下文有行数据，validate 对含 `.` 的族码会豁免 `ROW_TOKEN_IN_QUERY` 提示）。

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

- **formbuilder JSON 只出现在 Para / 表单设置两种 500 的 H5Para**，五件套与旧结论一致：`formtemplate`（MOD26xxxxxxx）、`formData:"#FORMDATA#"`、`selectData:{}`、`formbtns:[]`（恒空，按钮固化在 formtemplate 模板里按编号调 50x/70x 模型）
- `tableData` 的键即表格区数据源：`TABLE_1` → 列表/明细模型（带 `Para` 数组，元素是 `#列名#` 行级令牌）；保留名 `LINKDOCLIST` → `LINKFLOW#25`（工作流单据列表）；本组未出现 `LINKSIGNLIST`
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

## 4. 动作模型模式（#501/#502/#503）

- **确认/关闭/行关闭类动作**：`SQLScript`/`SQLUpdateScript` 全空，**UPDATE 写在 SQLClear**（如 `BH10X#501-确认`：更新 MFGPKL 行状态 + MFGPKH `DOCSTA=2`；`#502-关闭`：头行 `CLOSTA=1` + `CLOREA='#CLOREA#'`）。按钮 `script="4"` 消费 SQLClear，与 APP 侧契约一致
- **单据打印**：`CallFunction` 承载 `CALLFUNCTION~FILEEXPORT~` + JSON（`fileType:"REPORT.PDF"`、`reportFile:#LINKREPORTPATH#\表名.rdlx`、`connString:["#LINKCONN.连接码#"]`、`para:["#DOCNUM#"]`）
- **外部接口调用**：`CALLFUNCTION~LINKRESTAPI~` + REST JSON（`ClientURL/Method/Header/JsonBody/resultFormula/resultList`，取响应字段用 `#LINKJSONVALUE:$.path#`）——**密钥类字段不能硬编码进模型，向用户索取或走系统配置**
- **按钮防呆**：`#700` 按钮控制模型 SQLScript 用 `#LINKSCRIPTGET@连接:...#` 包标量 SELECT，返回 `'LINKPREVENT:原因'` 或空串（与 `app-buttons.md` §1② 同构）；**注意 #700 双语义**——`X.AH10X#700-单据状态` 是普通 SELECT 状态选项数据源，按内容区分，不按编号

## 5. SQL 风格（FB 族语料确立）

- SELECT 一律大写英文列名/表列名，无中文显示别名；日期统一 `CONVERT(VARCHAR(16),...,21)`；计算列英文别名
- 写脚本惯例：MERGE INTO + `N'#字段#'`（回写）、`N'@字段@'`（新行占位）、数值列 `0#字段#` 强转、`SQLUpdateScript` 头部 `--LINKADDNEWROWS` + `--LINKAUTOREPLACEEMPTYCOLUMNS`（源码允许，见 `link-flags.md`）
- **CubeSetting 在 FB 族不是结果集投影**：主模型 SQL 仅 1 列而 CubeSetting 枚举数十列（表结构派生元数据 + `LINKRESERVE_DMTITLE` 多语言标题）。`datasearch-windows.md` 的「COLNAME=结果集列名」契约**仅适用于开窗/列表数据源场景**，不适用于 FB 页面族的 formSetting 模型

## 6. 生成清单（搭 FB 页面组前自查）

- [ ] 按「页面×数据」拆族并命名 `.AH/.AL/.BH/.BL`，族伴生码 = 族码+`10X`
- [ ] 每族 #10 主模型 + #500 伴生模型（形态按 §2 对号入座）
- [ ] 菜单注册 500-List 指向 `.AH#10`；详情接参走 Document 映射
- [ ] 动作模型 UPDATE 写 SQLClear；防呆配 #700（LINKPREVENT 型）
- [ ] formbuilder JSON 只写进 Para/表单设置的 H5Para；formtemplate 问用户取号或克隆存量
