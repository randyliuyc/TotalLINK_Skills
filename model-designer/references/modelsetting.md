# ModelSetting JSON 键词汇表

> 权威来源：运行时真实读取代码（行号锚定）+ 21 个样例。**设计器没有 UI 开关生成这个 JSON——全部手写**（`fDataModel.vb` 的 `medModelSetting` 编辑框直存 `MODELSETTING` 列）。

## 解析机制（生成前必知）

- 存储于 `SYSSEARCH.MODELSETTING` 列，即「113 号脚本」（`eModelScriptType.ModelSetting`）；**读取时先做占位符替换再解析**（`SysDataModel3.vb:22` `ScriptFormatedWithRowData`）——JSON 里可嵌 `{N}` 参数与 `#列名#` 行级占位符。
- Newtonsoft.Json 解析（`MLTShared2.vb:4295` `JobjectFromStr`）；**解析失败静默返回空**（只记日志），所有键视为缺失。
- 取键用 JSONPath `SelectToken`（`SysDataModel3.vb:165-171`），`$.` 前缀可省略。
- **键名大小写敏感，写错 = 静默失效**。官方拼写：`paraDisabled`（小写 p）、`leveldatasetting`（全小写）、`dataClear`（小写 d）、其余 PascalCase。
- 键缺失的默认行为：EditCols 回退解析 UpdateScript 的 SET 子句（`SysDataModel.vb:5909-5912`）；Timeout=0；LinkConn=模型自身连接；WindowSize=0.6/0.6；paraDisabled=全部参数可编辑。

## 运行时真实读取的键（可安全生成）

### 网格行为

| 键路径 | 语义 | 值格式 | 证据 |
|--------|------|--------|------|
| `$.DataScript.UpdateScript.EditValueList` | 可编辑列的下拉/开窗来源。键=列名，值=`"模型代码#序号"`（`#序号` 可省，省略取该代码第一个模型）。加载方式由列别名前缀决定：`LINKDROPDOWN/LINKDROPVALID/LINKLIST`=预载，`LOAD*`=单元格动态加载，其他=开窗搜索 | `{"列名":"模型代码#序号"}` | `MLTUGridDetail.vb:1805-1849` |
| `$.DataScript.{BaseScript\|CreateScript\|UpdateScript\|DeleteScript\|TreateScript}.EditCols` | 各脚本的可编辑列白名单 | `["COL1","COL2"]` | `SysDataModel3.vb:173-179`、`SysDataModel.vb:5909` |
| `$.ColumnWidth` | 默认列宽（用户未保存布局时） | `[{"列名": 像素}]` | `MLTUGridDetail.vb:1974-1997` |
| `$.DoubleClickDataMine` | 双击单元格触发数据挖掘（值=挖掘附加序号；命中则不触发行编辑） | `[{"列名": 序号}]` | `MLTUGridDetail.vb:4326-4352` |
| `$.GridDataSave` | 右键动作执行前先保存指定网格的未保存编辑 | `["模型代码", ...]` | `fDataAnalysis.vb:2974-2990` |
| `$.leveldatasetting.hidecols` | 树状层级数据各层隐藏列（**全小写键**） | `["COL", ...]` | `SysDataModel2.vb:2631-2636` |

### 参数区

| 键 | 语义 | 值格式 | 证据 |
|----|------|--------|------|
| `$.paraDisabled` | 参数只读控制：按参数序号，`"1"`=只读、`"0"`/缺省=可编辑 | `["0","1","0",...]` | `fDataAnalysis.vb:3201-3217` |

### 保存联动 / 脚本执行

| 键 | 语义 | 值格式 | 证据 |
|----|------|--------|------|
| `$.DataScript.BeforeSaveAction` | 网格保存**前**先执行另一模型的 TreateScript（如先存子表） | `{"dmCode":"代码","dmNum":序号}` | `MLTShared2.vb:3486-3505` |
| `$.DataScript.AfterSaveAction` | 网格保存**后**自动触发另一模型 | 同上 | 同上 |
| `$.DataScript.{ScriptType}.Timeout` | 脚本执行超时秒数（缺省 0=不限） | 整数 | `SysDataModel3.vb:191-198` |
| `$.DataScript.{ScriptType}.LinkConn` | 该脚本使用的连接代码（缺省=模型 ConnString） | `"连接代码"` | `SysDataModel3.vb:200-207` |

### 数据挖掘 / 弹窗

| 键 | 语义 | 值格式 | 证据 |
|----|------|--------|------|
| `$.DataMineCondition` | 挖掘动作执行前防呆：支持 `"LINKWARNING:/LINKCONFIRM:/LINKPREVENT:..."` 或对象（condition 支持 LINKSCRIPT/LINKFORMULA） | 字符串或 JObject | `SysDataModel.vb:8984-8993, 9194-9218` |
| `$.WindowSize` | 弹窗占屏幕比例 `[宽,高]`（1=全屏；数据选择窗默认 0.6/0.6，挖掘窗 0.9/0.8） | `[0.9,0.8]` | `fDataModelSearch.vb:438-453`、`SysDataModel.vb:11429-11444` |

### 结果集清理（服务端消费）

| 键 | 语义 | 值格式 | 证据 |
|----|------|--------|------|
| `dataClear`（顶层小写） | 结果集清理：`dataReplace:[{columns,find,replace}]` 内容替换、`dataFill:[{columns,fill}]` 空值填充、`filterRows:"DataTable.Select 表达式"` 行过滤 | JObject | `LinkFunction/LinkHelper.cs:860-967` |

## 不要生成的键【不建议】

`SysDataModel3.vb:261` 的 `ModelSettingReset_XXXX`（脚本标记→JSON 转换器）是**从未被调用的死代码**，它列出的键（`BatchEdit`、`SaveOnEnterKey`、`LinkEditMode`、`AutoClose`、`CopyPreviousLine`、`LoadDataImmediate`、`InputBox`、`DataMineOverview.*`、`DeepAnalysisType`、`LocationType` 等）**没有运行时读取方**——这些行为实际全部由脚本标记 `--LINKxxx` 控制（见 `link-flags.md`）。生成时用脚本标记，不要写这些 JSON 键。

`$.DataScript.UpdateScript.RequiredCols` 读取端存疑（`SysDataModel3.vb:182-189` 定义了 `ModelRequiredCols` 但未发现调用方）——必填校验实际走 `--LINKREQUIRED:` 脚本标记，不要用这个键。

## 样例参照

- EditCols + EditValueList：`samples/ERAQA1020#10`、`ERAQA102010X#700`
- 仅 EditCols：`ERAQA1005#10`、`ERAQA1010#10`、`ERAQA101010X#700/#701`、`ERAQA102010X#710`
