# 开窗选择窗契约（linkdatasearch / 数据选择窗）

> 依据：语料 `KEEWAYZUPPDA/KEEWAYZUP.LOC#10-选择库位.xml`（正常工作的选择窗）+ TMESSTK2010X#710 实机 bug 修复（2026-11-04，空白行症状）。
> 属性级定义见 `../totallink-app-help/references/attributes.md`（text-value / target-id / not-para 等）。

## 1. 链路

H5Edit / H5NewRec 里的开窗按钮 → 打开目标模型的**数据选择窗** → 用户选行 → 按 `text-value` 指定的列回填到 `target-id` 输入框：

```html
<input type="text" required id="物料编码" paratype="STR" paradm="" value="">
<button class="mui-icon mui-icon-list linkdatasearch one"
  not-para target-id="物料编码" paratype="STR"
  code="TMESSTK2010X" num="710" text-value="产品编码-产品编码" para="">
</button>
```

## 2. 三处命名必须一致（核心契约）

> **适用范围（2026-11-05 TAMPER 语料细化）**：本契约适用于**开窗/列表数据源模型**（TMESSTK20 实测、KEEWAYZUP 语料）。
> 两类例外见 §2a/§2b：APP PDA 开窗走 `automatch` 不配业务列 CubeSetting；FB 页面族的 CubeSetting 是表结构元数据不是结果集投影。

| 位置 | 要求 | 不一致的实机症状 |
|---|---|---|
| 目标模型 SQLScript 结果集列名 | 别名（若写）或底层列名 | — |
| 目标模型 CubeSetting 的 `COLNAME` | **必须等于结果集列名** | **列表有行但数据空白**（客户端按 COLNAME 匹配结果集，对不上即渲染空行） |
| 调用方按钮 `text-value` | 引用**实际存在的结果集列名** | 选中后回填失败 |

TMESSTK2010X#710 修复记录：SQL 别名 `产品编码/产品名称`，CubeSetting 写了 `物料编码/物料名称` → APP 列表 100 行全空白；对齐后恢复。

## 2a. APP PDA 开窗：列匹配走 automatch（TAMPER 语料）

PDA 扫码类开窗（`TAMPERAPP/TMESPDA13010X#702/704/705/706`）的对接方式不同：

- **开窗数据源模型不配业务列 CubeSetting**——四个开窗模型的 CubeSetting 只有 `LINKRESERVE_DMTITLE`（多语言标题）两条，无任何业务列 COLNAME
- 列回填由**调用方按钮的 `automatch` JSON** 完成（结果列 → 表单字段 id 映射，属性族详见 `app-buttons.md` §1⑤）：

```html
<button class="mui-btn mui-btn-blue linkdatasearch one"
  code="TMESPDA13010X" num="704" text-value="ITM1-ITM1"
  para="{SITE,ITMNO,UOM,NEDQTY}"
  automatch='{"WH":"WH","LOC":"LOC","UOMCOE":"UOM","QTY":"QTY","PK":"PK"}'
  reload props>
```

- 数据源 SQL 直接输出表列名（`K.WH, K.LOC, K.UOMCOE, K.PK`）+ 一个拼接显示列（`text-value` 引用，如 `ITM1`）；「本次可领数量」等业务约束用 CASE 算进输出列
- 结论：**COLNAME 契约在 automatch 场景不适用**；`text-value` 仍必须引用实际结果集列名

## 2b. FB 页面族：CubeSetting 是元数据不是投影（TAMPER 语料）

FB 页面族（`fb-page-families.md`）的主模型 SQL 可能只有 1 列（如 `SELECT '领料申请'`），CubeSetting 却枚举数十个 COLNAME——这是**表结构派生的元数据 + `LINKRESERVE_DMTITLE` 多语言标题**，不参与结果集匹配。「COLNAME=结果集列名」对此类 formSetting 模型不适用，也不要求业务列 CAPTION 齐全。

> **SQL 列名风格（2026-11-04 定）**：新模型 SELECT 不为显示目的写中文别名（语料中的别名写法是早期风格，不作推荐），直接用表列名（可带表前缀）；显示标题由 CubeSetting `CAPTION`（运行器翻译）或 H5 模板内联 label（APP）承担。开窗窗体的列标题同样来自 CubeSetting。计算/聚合列无原始列名可用时才用别名，且建议英文标识符（如 `QTY_SUM`）。validate 对中文别名报 `SQL_ALIAS_LEGACY`（info 级，存量模型可保留）。
**例外（2026-11-05 TAMPER 语料）**：无界面服务型模型（扫码解析/校验/按钮控制）的消息与辅助列可用中文别名——它们不用于列表显示，直接作为前端提示文案（如 `TMESPDA13010X#1521` 的 `SELECT '领料单已关闭！' 提示`）。

新风格示例（与旧别名版等价）：

```sql
SELECT TOP 100 ITMNO              -- CubeSetting: COLNAME=ITMNO, CAPTION zh=产品编码 / en=Item Code
              ,MAX(ITMNAM) QTY_SUM_ITEMNAME_NA -- 聚合列必须有别名（英文标识符）
FROM   ITM
WHERE  ITMNO LIKE '%{0}%'
GROUP  BY ITMNO
```
聚合列示例中 CAPTION 承担中文标题。

## 3. 目标模型（选择窗数据源）的写法

```sql
SELECT TOP 100 ITMNO        产品编码
              ,MAX(ITMNAM)  产品名称
FROM   ITM
WHERE  ITMNO + ISNULL(ITMNAM, '') LIKE '%{0}%'
GROUP  BY ITMNO
ORDER  BY ITMNO
```

- 参数 `{0}` = 用户输入的过滤关键字（LIKE 双侧通配）
- CubeSetting：`LINKRESERVE_DMTITLE`（zh+en）必须写；列级 caption 的 COLNAME 按上表对齐
- `UseParameter=true`；H5Para/H5List 留空（LOC#10 范式）
- `ShowInMenu=false`
- 按钮上 `para` 传主键/过滤上下文（如按地点过滤库位：`para="#收货地点#"`），不需要则留空

## 4. text-value 格式【待源码核实】

两种记载并存：
- 语料按钮写法：`text-value="库位-库位"` / `text-value="产品编码-产品编码"`（**连字符分隔**，疑似 `显示列-回填列`）
- attributes.md：`text-value`（:3963）记为 `key:val` 选择列表字段名标识

稳妥写法：显示列与回填列写同一个列名（`X-X`）；要「显示名称、回填编码」效果时试 `产品编码-产品名称` 并实机验证。

## 5. 症状速查

| 症状 | 排查顺序 |
|---|---|
| 列表有行但数据空白 | ① CubeSetting COLNAME ≠ SQL 别名（最常见）② 列级 COLTYPE 不是 `LANGUAGE-*` |
| 选中后输入框没值 | `text-value` 引用了不存在的列名 |
| 开窗窗体打不开 | code/num 拼错；目标模型不在同环境（ConnString 注意跨库，见 environments.md） |
| 关键字过滤不生效 | 目标模型 SQL 没用 `{0}` 或没包 `%...%` |
