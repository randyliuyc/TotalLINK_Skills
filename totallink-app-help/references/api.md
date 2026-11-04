# 服务端接口约定

## 1. 请求基础

- **服务地址**：全局 `globleServer`（memGet，index.js 登录时 memSet）；**登录令牌**：`LinkID`（=loginID）
- 请求体统一 `{loginID, par:{...}}`，响应 `{message, dataType, data:{...}}`
- 封装：`linkAjax(parajson, url, ajaxSetting(id))`，catch 时 alert + closeWaiting + rethrow

## 2. 接口清单（均为 `globleServer + '/api/DataModel/...'`，除非注明）

| 接口 | 用途 | 证据（linkshared.js 快照行号） |
|---|---|---|
| linkDMContextActionInfo | 附加模型动作信息校验（DMContextAction type=0） | :5308, :5325 |
| linkDMConditionAction | 条件动作校验（type=1，action=id） | :5322 |
| linkDMContextFunBack | 附加模型执行后回跳/单行处理（contextCall1） | :1242, :3468, :4799 |
| linkDMAttachURLFunction | URL 型附加功能 | :826 |
| linkDMPreProcessByGridDataBack / linkDMPostProcessByGridDataBack | 预处理/后处理（ProcessCall） | :898/:904 |
| linkDMGridRowSubmit | 单行提交（linkQuickAjax2） | :1740 等 |
| linkDMGridDataSubmit | 多行记录提交（linkQuickAjax4） | :5037 等 |
| linkDMDatasetResult | 模型数据查询（linkQuickAjax1） | :144 等 |
| linkDMFormData | 载入模板/跳转刷新（linkQuickAjax6） | :4822 |
| linkDMDataSubmit | 全量数据提交（linkQuickAjax7） | :4836 |
| linkDMDataMine | 数据挖掘（linkQuickAjax10） | :5231 |
| linkDMEditList / linkDMPickList | 编辑列表 / 下拉选项 | :6365 / :4025 |
| linkDMData | 模型数据 | :7733 |
| linkDMFileUpload | 文件上传 | :7739/:7793 |
| linkDMH5ParaListJS | H5 参数列表（modelpara.js） | :74 |
| linkDMEChartScript / linkDMChartScript / linkDMEChartScriptLastPara | 图表脚本（三种方式） | linkchart.js:114/:136/:153 |
| /api/LINK/linkFormula | 公式计算（GET） | :4807 |
| /api/LINK/linkUserByToken | Token 取用户/服务端版本（setting.js） | :20 |

> 行号是编写时快照；调用处请以 search_content 实际核实为准。

## 3. parajson 参数结构

- type=0（功能信息）：`{loginID, par:{dm:{dmCode, dmNum}, contextMenuNo: id, RDs}}`
- type=1（条件动作）：`{loginID, par:{dm:{dmCode, dmNum}, action: id, RDs}}`
- 预/后处理：`{loginID, par:{dm:{dmCode, dmNum, Para:reParaList()}, GDs: [{RowData:[RDs...]}]}}`
- 附加模型校验的 dm 标识：`dmCode = 主dmCode + 主dmNum + 'X'`，`dmNum = contextid（附加模型编号）`

## 4. 返回值处理（DMContextAction 内）

返回 `dataType=="modelActionInfo"` 时按 `a.type` 分支：
- 1：执行 func() + 长 toast
- 2：mui.confirm 后 func()
- 3：a.condition 为 True/1 才 func()，否则 alert
- 其它/空白内容：直接 func()

## 5. 离线模式

- `ifOffline()` = memGet("offline")=="1"
- 离线数据走 SQLite（manifest 权限含 SQLite）；menugroup.js/collection.js 等直接 openDB → selectData → closeDB
- 每个 linkquickActionN 均有 `_offline` 版本（如 linkquickAction8_offline 直接 closeWaiting）

## 6. 方法/扩展点速查

原外部文档（formbuilder/api/methods.html）不可作为依据（地址可能失效）。其中列出的方法/属性已**逐条与本项目源码核实**并归档到 `references/methods.md`（含行号、真实签名、未找到条目更正清单）。回答"某方法怎么用/是否存在"类问题时，读 methods.md，并以 search_content/read_file 复核当前源码为准。
