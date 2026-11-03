# 样例模型清单与编号约定

> 样例来源：用户从生产环境导出（fDataModel 导出按钮，格式与 `tlk model export` 一致），QA（质量管理）模块。
> **样例盘点发现（2026-10-29）：全部使用旧 `~` 分隔符，0 处 `~<!>~`；产出时必须用新分隔符。**

## 文件清单与覆盖的教学点

| 教学点 | 样例文件 |
|--------|---------|
| 最小维护模型（查询+编辑+新增+删除+Cube+DMUsage） | `ERAQA1005#10-Element.xml` |
| 参数化模糊查询 + 数据挖掘布局 + 完整增删改 | `ERAQA1010#10-Grade.xml` |
| 导出报表（大 SQL + PIVOT + 临时表 + `--LINKLOADDATAIMMEDIATE`） | `ERAQA1010#20`、`ERAQA1020#20` |
| 数据挖掘导出入口（单行 `LINKDATAMINE~30`） | `ERAQA101010X#0`、`ERAQA102010X#0` |
| 手动前置动作（SQLClear + `--LINKREFRESH` 改状态） | `ERAQA101010X#21-Release` |
| 手动后置动作 | `ERAQA101010X#41-Frozen` |
| 行级右键菜单动作（SQLClear 承载 INSERT，`{N}` 引用模型参数） | `#501-Copy Grade`、`#502-Allocate Customer Spec` |
| 数据处理条件/防呆（LINKPREVENT/LINKCONFIRM + `--LINKSCRIPTGET@源:`） | `ERAQA101010X#1000`、`ERAQA101010X501X#1000`、`ERAQA101010X502X#1000` |
| 用户自定义子表维护（按主键过滤的明细编辑） | `#700-Grade Element`、`#701-Grade Version`、`ERAQA102010X#700`、`#710` |
| 列级下拉模型（裸代码 ParaSearchCode + 跨库 ConnString） | `ERAQA101010X.SUPCOD#10-选择供应商` |
| 列别名下拉回写（LINKDROPVALID + EditValueList） | `ERAQA1020#10`、`ERAQA102010X#700` |
| 文件上传（CALLFUNCTION~LINKFILEUPLOAD~JSON） | `ERAQA102010X#501` |

## ModelNum = 附加模型编号（全平台约定，权威定义）

**权威来源：`LinkEnum.eModelAttachNum`（`LinkFunction/LinkDefine.cs:190-292`）**。主模型（#10）之外，每个 ModelNum 是主模型的一个「附加模型」，编号段有严格语义：

| 编号段 | 枚举名 | 语义 |
|--------|--------|------|
| `0` | `CallProcess` | 可调用的外部应用程序（样例中承载 LINKDATAMINE 挖掘入口） |
| `1~10` | `Sync*` | 同步处理程序（执行 New/Edit/Remove/All 脚本） |
| `11~20` | `AutoPre*` | 自动前置程序（All 脚本，当前单行数据作参数） |
| `21~30` | `ManuPre*` | 手动前置程序（如 #21 Release） |
| `31~40` | `AutoPost*` | 自动后置程序 |
| `41~50` | `ManuPost*` | 手动后置程序（如 #41 Frozen） |
| `61~70` | `ManuPreCall*` | 手动前置调用功能 |
| `81~90` | `ManuPostCall*` | 手动后置调用功能 |
| `121~130` / `141~150` | `Manu*ProcessAll` | 手动前/后置（以过滤后的所有行作参数） |
| `161~170` / `181~190` | `Manu*CallAll` | 手动前/后置调用（所有行） |
| `201~220` / `221` | `Schedule*` | 甘特/日历视图数据处理、Owner List |
| `301` | `MyRowData` | 执行前预置数据（可改写行/隐藏敏感列/改造动作脚本；全局版为 `_LINKSYS_#301`） |
| `302` | `TaskProcess` | 数据执行进度显示 |
| `404` | `Exception` | 错误处理 |
| `500` | `FormSetting` | Web Form 页面模板定义 |
| `501~520` | `contextMenuStrip*` | **数据行右键菜单**（执行 All 脚本，传回当前模型参数；样例 #501 Copy、#502 Allocate、#501 文件上传） |
| `601~650` | `Function*` | 附加功能（按 CONNCODE 区分 LINKURL/LINKREPORT） |
| `700~999` | `UserDefine*` | 用户自定义（样例 #700/#701/#710 子表维护） |
| `1000` | `SQLScriptCondition` | **数据处理条件/防呆检查**（样例删除检查、Copy/Allocate 数据检查） |
| `1001~1020` / `1021` | `MultiLevel*` | 多层级数据（`--MULTILEVELDATA`）及关系定义 |
| `1501~1520` / `1521` / `1522` | `tag*` | 标签扫描解析相关附加模型 |
| `2000` / `2021` / `2041` | `*Msg` | 加载后提示、前/后处理动作提示 |

**AI 可据此为新模型建议 ModelNum（选择正确编号段），最终由用户确认。**

## ModelCode 命名规范（全平台约定）

**前缀 = 系统缩写 + 模块缩写**：样例 `ERAQA` = `ERA`（系统/公司缩写）+ `QA`（模块缩写）。这是良好的开发规范；**新模型的系统/模块缩写必须问用户**。

**附属模型后缀也是全平台约定**，权威证据：模型移植工具 `fDMTransfer.vb:24-34` 的官方 SQL：

```sql
SET @ATTDMCODE = CONCAT(@DMCODE, @DMNUM, 'X');   -- 附加模型代码 = 主模型代码+主模型编号+X
```

移植时用 `LIKE @ATTDMCODE + '%'` 级联匹配全部附属模型（`fDMTransfer.vb:273`）——因此附属模型代码**必须**以「主模型代码+主模型编号+X」开头：

- `主模型X`（`ERAQA1010` + `10` + `X` = `ERAQA101010X`）= 主模型 #10 的附属模型族；
- `主模型X + 动作号 + X`（如 `ERAQA101010X501X`）= 「501 号动作的检查模型族」（参数公式同族匹配规则见 `fDMTransfer.vb:337` `LIKE ... + '%X'`）；
- `主模型X.列名`（如 `ERAQA101010X.SUPCOD`）= 列级下拉模型。

顺带两个相关平台约定（来自同一移植工具，生成模型 XML 时不涉及但需知道）：
- 模型参数公式（ParaDefVal 的高级公式）存 `SYSCODE` 表（`CODETYPE='DMPARAFORMULA'`，`CODE`=模型代码）；
- 模型挂菜单走 `SysMenu` 表（`MenuNo`=ModelCode），不在模型 XML 范围内——新模型如需进菜单，提醒用户另行配置。

## DMUsage 书写约定（样例确立）

见 `fields.md` DMUsage 小节。样例中 `SCRIPT`：0=查询、3=删除、4=动作/更新；文本含 `params: [...]` 与 `rowData: {...}` 两种说明段。
