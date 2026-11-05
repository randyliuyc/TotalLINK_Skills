# CALLFUNCTION 动作脚本语法

> 权威来源：`BaseLib/Modules/CallFunction.vb`（switch 分发）、`BaseLib/Modules/MLTShared3.vb:94`（`FunctionSplit`）+ 样例实证。

## 语法与分隔符

```text
CALLFUNCTION~<!>~ACTION~<!>~参数1~<!>~参数2~<!>~...
```

- **产出必须用新分隔符 `~<!>~`**（`MLTShared3.vb:96-101`，兼容参数值中含 `~`）。
- 分割规则：含 `~<!>~` 则用它分割，否则回退单字符 `~`。**本批 21 个样例全部是旧 `~` 风格，0 处新分隔符**——读样例容错，产出必须用新。
- 特殊入口：`sWords[1]` 以 `LINKACTION.` 开头时为内部模型动作（`LINKACTION.模型代码.序号`，`sWords[2]` 为动作名）。

## 样例实证：LINKFILEUPLOAD

唯一样例（ERAQA102010X#501-文件上传.xml:72-85，原文）：

```text
CALLFUNCTION~LINKFILEUPLOAD~{
    "par": {
        "dm": {
            "dmCode": "LINKFLOW",
            "dmNum": 25,
            "Para": []
        },
        "scriptType": 1,
        "rowData": {
            "DOCNUM": "#OPESTD#",
            "DOCTYP": "OPESTD"
        }
    }
}
```

要点：第 3 段是 JSON（`par.dm` 指定目标模型代码/编号、`rowData` 带行级占位符）；执行前会先经 `ScriptFormatedWithRowData` 做行数据替换（`fDataAnalysis.vb:2913`）。生成时 JSON 内的花括号无需转义（此脚本不经过 `string.Format`，但含 `{N}` 参数时需注意——样例用行级 `#OPESTD#` 而非 `{N}`）。

## 样例实证：LINKRESTAPI（REST 接口调用，TAMPER 语料 2026-11-05）

`TAMPERFB/TMESEXC0510X#501-材料出库创建接口调用.xml:72`，CallFunction 字段承载：

```text
CALLFUNCTION~LINKRESTAPI~
{
    "ClientURL": "https://...",
    "AuthUser": null, "AuthPassword": null,
    "Timeout": 120,
    "Method": 1,
    "Header": { "Content-Type": "application/json", "appKey": "...", "openToken": "..." },
    "Parameter": null, "UrlSegment": null, "XmlBody": null, "files": null,
    "JsonBody": { ... 业务报文，可嵌 #列# 占位 ... },
    "chkToken": null, "chkValue": null, "chkMessage": "$.message",
    "resultFormula": "材料出库单创建结果:成功=HTTP200,错误信息 = #LINKJSONVALUE:$.message#",
    "resultList": { "success": "$.message", "message": "$.message" },
    "resultSetValue": { "errorMsg": "$.message" },
    "resultAutoHide": false
}
```

要点：响应 JSON 字段用 **`#LINKJSONVALUE:$.路径#`** 提取（`$.message` 等 JSONPath）；`resultFormula` 是给用户看的结果文案模板。**appKey/openToken 等密钥不得硬编码进模型**——向用户索取配置方式。

## 样例实证：FILEEXPORT（报表 PDF 导出/打印，TAMPER 语料）

`TAMPERFB/TMESEXC0510X.BH10X#503-单据打印.xml:72`（单号打印动作模型）：

```text
CALLFUNCTION~FILEEXPORT~
[
    {
        "fileType":"REPORT.PDF",
        "fileName":"领料申请#DOCNUM#",
        "fileDesc":"领料申请#DOCNUM#",
        "ARSetting":{
            "reportFile":"#LINKREPORTPATH#\\MFGPKH.rdlx",
            "connString":[ "#LINKCONN.LINK01#" ],
            "para":[ "#DOCNUM#" ]
        }
    }
]
```

要点：参数段是**数组**（可多文件）；报表路径用 `#LINKREPORTPATH#`、连接用 `#LINKCONN.<连接码>#`、报表参数走 `para` 数组（行级 `#列#`）。与 `X3WEB` 类似，分隔符在语料中为旧式单 `~`（`FunctionSplit` 回退兼容），产出仍推荐 `~<!>~`。

## 样例实证：数据检查模式（动作防呆的推荐结构）

主动作模型配一个检查模型，在动作执行前拦截：

```text
ERAQA101010X#501-Copy Grade          （主动作，SQLClear 承载 INSERT）
ERAQA101010X501X#1000-Copy数据检查    （检查模型，SQLScript 承载检查）
```

检查模型 SQLScript 的固定写法（ERAQA101010X501X#1000 原文）：

```sql
--LINKSCRIPTGET@TMESERAQA:
SELECT  
  CASE WHEN '{4}'=''  THEN   N'LINKPREVENT:Grade编码必填.
Grade Code is required' 
       WHEN COUNT(*)>0 THEN N'LINKPREVENT:Grade 已经存在.
Grade already exists'
       WHEN '{5}'='' THEN N'LINKCONFIRM:Grade名称为空，确认要复制吗？.
Grade name is empty, are you sure you want to copy it？'
	    ELSE N'' END
FROM QAGRADE WHERE GRDCOD='{4}'
#
```

- `LINKPREVENT:消息` → 阻止执行；`LINKCONFIRM:消息` → 确认后继续；空串 → 直接放行。
- 消息支持中英双语两行。

## 已知存在的 action（名称确认，参数段【待核对】）

来源：`LINK.Core/docs/agents/callfunction-followup-tickets.md`。使用前必须以 `CallFunction.vb` 对应 handler 或真实样例为准：

- 文件类：`FILEEXPORT`、`GETFILELIST`、`GETFILEINFO`
- Excel/CSV/文本：`GETEXCELDATA`、`GETEXCELCELLLIST`、`GETEXCELCELLDATA`、`GETEXCELSHEETLIST`、`SAVEEXCELDATA`、`GETCSVDATA`、`TEXTFIELDDATA`
- JSON/正则：`GETJSONDATA`、`REGULARMATCH`
- 工作流：`WFTASKCREATE` ~ `WFTASKRESTART`（16 个）
- Web 服务：`X3WEB`/`LINKSAGEX3WS`、`SOAPWEB`、`LINKRESTAPI`
- 其他：`REPORTPRINT`、`BULKCOPY`、`LINKREPORT`
- 内部动作：`LINKDMACTION`、`LINKDMACTIONLIST`、`LINKSETVALUE` 等（经 `LINKACTION.` 入口）

## 使用原则

1. 每个 action 的参数段数与格式必须以 `CallFunction.vb` handler 或真实样例为准，不确定就问用户。
2. 不要为不存在的按钮生成脚本——先想清楚该动作由运行器哪个入口消费（状态动作/行级动作/上传等）。
