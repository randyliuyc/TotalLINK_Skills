# TotalLINK HTTP 接口契约（8 端点 + 文件上传）

> 权威基准：LINKIIS 项目（旧 C# ASP.NET Web API，GitHub `randyliuyc/LINK` 仓库）。所有结论附 `文件:行号`。
> 读者：开发第三方系统对接代码的开发者 / Agent。

## 0. 通用约定

### 0.1 路由与请求

- 路由模板 `api/{controller}/{action}/{id?}`（`LINKIIS/App_Start/WebApiConfig.cs:20-26`），完整 URL 形如 `http(s)://<server>/api/DataModel/linkDMDatasetResult`。**MVC 路由 `{controller}/{action}` 不承载这些接口**。
- 除文件上传外全部为 `POST`，`Content-Type: application/json`，JSON body。
- CORS 全局放开（`Access-Control-Allow-Origin: *`，允许 Headers `Content-Type,x-token`：`LINKIIS/Web.config:67-73`）；无 IP 白名单。
- 全局 Cookie 约束：`sameSite="Lax"`、`httpOnlyCookies="true"`（`LINKIIS/Web.config:50`）。

### 0.2 统一返回结构 linkResult

所有端点返回同一结构（`LinkFunction/LinkDefine.cs:41-54`）：

```json
{
  "isSuccess": "true",      // 字符串，不是布尔："true" / "false"
  "dataType":  "DataSet",   // data 的 .NET 类型名（DataSet / Int32 / String / LinkToken / parDataModelWithInfo ...）
  "data":      {},          // object，类型由 dataType 指示
  "message":   "Data Result from Data Model",
  "action":    ""           // "" | warning | confirm | prevent
}
```

- `dataType` 由 `data.GetType().Name` 生成（`BaseLib/Modules/MLTShared.vb:2601-2628`）。
- `action` 语义（`LinkDefine.cs:48-53`）：空=正常继续；`warning`=提示后继续；`confirm`=由用户选择；`prevent`=终止。服务端在 message 中用 `LINKWARNING:` / `LINKCONFIRM:` / `LINKPREVENT:` 前缀触发（`MLTShared.vb:2663-2669`），返回给客户端时已转成 action 值。
- **对接方必须识别 `action`**：防呆规则（模型脚本 `--LINKCONFIRM:` 等）通过它下发；直接忽略会造成"重复提交/绕过确认"类事故。语义详见 `auth-and-errors.md`。

### 0.3 鉴权链（每个 DataModel 端点共用）

1. body 里 `loginID` 字段装登录返回的 token 字符串（**字段名叫 loginID，值就是 LinkToken**）。
2. `loginID` 为空时服务端从 Cookie `TotalLINK_TOKEN` 兜底（`LINKController.cs:1284-1300` ResolveLinkToken）。
3. `ResetLinkConnStr(apiName, p, p.loginID)` 解析 token、还原用户上下文（`LINKController.cs:1307-1389`）；token 无效 → `isSuccess=false`，`data="InvalidLinkToken"`。
4. 各端点再按模型功能权限校验（`M.FuncAccess(...)`），失败 → `data="AccessFail"`。

服务端到服务器的对接（无浏览器 Cookie）**一律在 body 里带 `loginID`**，不要依赖 Cookie。

### 0.4 数据行词汇：RDs / GDs

- **GridRowData** = `{ "Key": "列名", "Type": ".NET类型名", "Value": "值" }`（结构定义在被引用的 BaseLib 程序集内，字段用法见 `BaseLib/Modules/Globle.vb:78-82` 注释与 `SysDataModel.vb` 各处 `rds.Key/.Value` 消费）。
- **RDs**：`GridRowData[]`，单据/单行数据（主表一行）。
- **GDs**：`GridData[]`，每个元素 `{ "RowData": GridRowData[] }`（一行一个元素），用于多行网格提交。
- **rowData**（object）：JSON 原始数据入口；**有值时忽略 RDs**，由服务端转换为 RDs（`LinkDefine.cs:859-863, 1333-1337`）。二选一即可，建议对接方直接用 RDs。
- **脚本类型枚举 eModelScriptType**（`LinkDefine.cs:427-436`，body 中传数字）：
  `0=Base, 1=新增, 2=编辑, 3=删除, 4=动作`（101+ 为 H5 族，第三方对接一般不用）。

### 0.5 模型参数

`dm.Para` / `par.Para` 是**字符串数组，位置对应模型定义的参数 01~10**（`{0}`~`{9}`），空位传 `""` 占位，不可跳过（与 totallink-base 的 `--params-json` 同一位置匹配语义）。所有提交端点的共同行为：**Para 为空时服务端取"最近参数"（`GetLastParamsValue`）**——第三方对接请始终显式传 Para，不要依赖服务端会话残留参数（`DataModelController.cs:3414-3418, 3729-3733, 3795-3799`）。

---

## 1. linkUserLogin —— 用户名密码登录（对接主路径）

`POST api/LINK/linkUserLogin`（`LINKIIS/Controllers/LINKController.cs:42-104`）

- 入参 `parUser`（`LinkDefine.cs:543-572`）：

| 字段 | 说明 |
|------|------|
| `loginUser` | 用户代码 |
| `loginPassword` | 密码 |
| `loginComputer` | 客户端标识（建议传对接系统名） |
| `getuiCID` | 推送 CID，第三方传 `""` |
| `langcode` | 语言代码（如 `zh`/`en`），可空 |
| `loginMode` | 登录方式枚举；`WinClientHttp` 归为 WinClient，其余归为 LinkAPP（`LINKController.cs:54-63`） |

- 成功：**token（loginID）在返回体 `data` 中**（`LINKController.cs:97`）；密码 7 天内过期时 `action="warning"`、message 为过期提示（:90-98）。
- 失败：`isSuccess=false`、`action="warning"`、`data` 为 `err_` 前缀错误码（:78-82）。
- 服务端会验证设备真实性（类注释 `LINKController.cs:36-39`）——同一 `loginComputer` 重复登录可能踢掉旧会话，对接方应固定一个稳定标识并处理登录失败重试。

```json
// 请求
{"loginUser":"APIUSER","loginPassword":"***","loginComputer":"ERP-INTEGRATION","getuiCID":"","langcode":"zh","loginMode":0}
// 成功响应
{"isSuccess":"true","dataType":"String","data":"<token 字符串>","message":"Login Success","action":""}
```

> 后续所有调用把这个 token 填进 body 的 `loginID` 字段。

## 2. linkUserLoginAPI —— 浏览器集成登录

`POST api/LINK/linkUserLoginAPI`（`LINKController.cs:129-206`）

- 入参 `parUserAPI`（`LinkDefine.cs:588-632`）：与 parUser 类似，另需 **`linkToken`**（平台预签发的第三方接入 Token，经 `SysLogin.TokenCheck3rdAccount` 校验，`LINKController.cs:140`）；`sourceCol3rd/sourceID3rd/sourceCode3rd` 用于企业微信等第三方 SSO 匹配；`loginComputer` 为空时自动生成 GUID（:146-150）。
- **token 不在返回体里**：成功后写 HttpOnly Cookie `TotalLINK_TOKEN`（HttpOnly、HTTPS 下 Secure、Path=/、24h 过期，:183-195），返回体 `data` 是字面量 `"TotalLINK_TOKEN"`（:197-198）。
- 适用于"第三方系统的网页用户直连 TotalLINK"的场景；纯服务端对接用 §1。

## 3. linkUserByToken —— token 解析

`GET api/LINK/linkUserByToken?sLinkToken=<token>`（`LINKController.cs:261-289`）

- `sLinkToken` 可空：空时从 Cookie 兜底（:267-269）。无 Cookie 的服务端对接必须带 query 参数。
- 成功：`data` = LinkToken 结构（用户信息键值对，已剔除 PWD/LINKDEVID 等敏感键，:280-284）。失效：`data="InvalidLinkToken"`。
- 用途：第三方网关校验/桥接会话。**不要**用它当"每次调用前验活"的心跳——直接调用业务端点、按 InvalidLinkToken 错误处理即可。

## 4. linkDMDatasetResult —— 模型查询

`POST api/DataModel/linkDMDatasetResult`（`DataModelController.cs:2938-3010`）

- 入参 `plkDataModelWithParams`（`LinkDefine.cs:850-886`）：

```json
{
  "loginID": "<token>",
  "par": { "dmCode": "ERAQA", "dmNum": 1010, "Para": ["", "2026-06-01", "2026-06-30"], "SimpleFlag": false },
  "RDs": [],
  "rowData": null
}
```

- 无显式功能权限校验（token 有效即可查询）；模型不存在时返回**包含错误信息的 DataSet**（`DataModelController.cs:2954-2957`）——注意此时 `isSuccess` 可能仍为 `true`，**要检查 DataSet 内容/rowCount 判断空错**。
- 连接代码为 `MULTILEVELDATA` 的多级模型走 `GetLevelData`，`data` 是嵌套 object（:2966-2970）。
- 普通模型：`data` = DataSet 的 JSON 序列化，形如 `{"Table1":[{...},{...}]}`，**表名取决于模型结果集的 TableName**（Json.NET 直接序列化 DataSet，`LINKIIS` 中无自定义 Formatter，:2983-2984）。

```json
// 成功响应
{"isSuccess":"true","dataType":"DataSet",
 "data":{"Table1":[{"DOCNUM":"QA26030001","STATUS":"10"},{"DOCNUM":"QA26030002","STATUS":"20"}]},
 "message":"Data Result from Data Model","action":""}
```

- 执行异常时 `message` 直接带服务端异常堆栈（:2997-3001），对接方报错时注意脱敏。

## 5. linkDMGridRowSubmit —— 单行提交

`POST api/DataModel/linkDMGridRowSubmit`（`DataModelController.cs:3384-3464`）

- 入参 `plkDataModelDef`（`LinkDefine.cs:1310-1345`）：

```json
{
  "loginID": "<token>",
  "par": {
    "dm": { "dmCode": "ERAQA", "dmNum": 1010, "Para": [] },
    "scriptType": 2,
    "RDs": [ {"Key":"DOCNUM","Type":"System.String","Value":"QA26030001"},
             {"Key":"STATUS","Type":"System.String","Value":"30"} ],
    "rowData": null,
    "skip": "", "skipMsg": ""
  }
}
```

- 权限映射（:3404-3407）：`scriptType 2→FuncAccess("EDIT")`、`1→NEW`、`4→TREAT`、`3→REMOVE`；无权限 → `data="AccessFail"`。
- 单行语义：一次提交一组 RDs（主表一行）；逐行处理请循环调用。
- `data` = 影响行数（Int32）。`skip="1"` 可跳过模型的 Action 联动（:1339-1344）。
- 成功判定看 `isSuccess` 与 `callsta`（脚本内防呆失败时 `action` 会带 confirm/prevent）。

## 6. linkDMGridDataSubmit —— 多行网格提交

`POST api/DataModel/linkDMGridDataSubmit`（`DataModelController.cs:3701-3767`）

- 入参 `plkDataModelWithScriptTypeGridData`（`LinkDefine.cs:1375-1409`）：`par` 在 §5 基础上以 `GDs`（`GridData[]`，每元素 `{ "RowData": [...] }`）承载多行，`RDs` 作单据头附加数据。

```json
{
  "loginID": "<token>",
  "par": {
    "dm": { "dmCode": "ERAMI", "dmNum": 1020, "Para": [] },
    "scriptType": 4,
    "GDs": [ {"RowData":[{"Key":"DOCNUM","Type":"System.String","Value":"QA26030001"}]},
             {"RowData":[{"Key":"DOCNUM","Type":"System.String","Value":"QA26030002"}]} ],
    "RDs": [],
    "rowData": null
  }
}
```

- 权限映射与 §5 相同（:3721-3724）。`data` = 影响行数。

## 7. linkDMContextFunBack —— 上下文动作（附加模型）

`POST api/DataModel/linkDMContextFunBack`（`DataModelController.cs:2061-2130`）

- 入参 `plkContextFunction`（`LinkDefine.cs:1450-1478`）：

```json
{
  "loginID": "<token>",
  "par": {
    "dm": { "dmCode": "ERAQA", "dmNum": 1010, "Para": [] },
    "contextMenuNo": 1000,
    "RDs": [ {"Key":"DOCNUM","Type":"System.String","Value":"QA26030001"} ],
    "rowData": null
  }
}
```

- `contextMenuNo` = 附加模型（上下文菜单）编号（模型族 `{代码}{编号}X` 段，常见 1000~）。需要 `FuncAccess("TREAT")`（:2080）。
- 成功 `data` = `parDataModelWithInfo`（模型执行信息 + 附加数据，如文件导出列表、脚本错误信息，类注释 :2055-2057）。
- `dm.Para` 为空时服务端取最近参数（:2105-2108）——同 0.5 节，显式传。

## 8. linkDMDataSubmit —— DataSubmit 过程提交

`POST api/DataModel/linkDMDataSubmit`（`DataModelController.cs:3773-3830`）

- 入参 `parDataSubmit`（`LinkDefine.cs:2081-2089`）：注意**此端点 par 直接就是 dm**（无 scriptType/GDs）：

```json
{
  "loginID": "<token>",
  "dm": { "dmCode": "ERAMI", "dmNum": 1020, "Para": [] },
  "data": { "DOCNUM": "QA26030001", "LINES": [ {"ITEM":"A001","QTY":10} ] }
}
```

- `data`（任意 JToken JSON）交由模型 CALLFUNCTION 定义的 **DataSubmit 过程**处理（`M.MoreDataSubmit`，:3807）。需要 `FuncAccess("TREAT")`（:3792）。
- 适用：模型侧设计了复杂数据提交过程（多表、自定义结构）的场景；结构必须与模型 DataSubmit 定义对齐，先向模型设计方索取结构说明。

## 9. linkDMFileUpload —— 文件上传

`POST api/DataModel/linkDMFileUpload`（`DataModelController.cs:3248-3370`）

- **multipart/form-data**，不是 JSON body：
  - 表单字段 `para`：**JSON 字符串**，结构同 §5 的 `plkDataModelDef`（loginID + par.dm/dmNum/RDs）（:3262-3268）；
  - 文件字段：`Request.Files` 集合（:3285），可多文件。
- 扩展名双名单（:3288-3303）：**白名单优先**——只允许 `.jpg/.jpeg/.png/.gif/.bmp/.webp/.pdf/.doc/.docx/.xls/.xlsx/.txt/.csv/.zip/.rar/.7z`；黑名单命中或不在白名单 → `data="InvalidFileType"`、`isSuccess=false`。
- 存储路径由**模型脚本决定**（占位符 `#LINKLOCALPATH#`/`#LINKREPORTPATH#`/`#LINKEXPORTPATH#`，见 `GlobalFormula.vb:902-911`），控制器不落盘；上传记录写入也走模型（`M.FileUpload`，:3359）。dmCode/dmNum 须指向对应的附件模型。
- 无显式 FuncAccess 校验（仅模型存在 + token 有效）。

```bash
curl -X POST "https://<server>/api/DataModel/linkDMFileUpload" \
  -F 'para={"loginID":"<token>","par":{"dm":{"dmCode":"ERAQA","dmNum":1020,"Para":[]},"scriptType":1,"RDs":[]}}' \
  -F "file1=@/path/report.pdf"
```

---

## 10. 部署注意项：LINK.Core 迁移项目（独立于主契约）

迁移项目（.NET 10）的上述接口行为对齐 LINKIIS，**但 `linkDMDatasetResult` 存在已拍板的格式改造**：服务端 DataSet 序列化从 JSON 改为「魔数 `LINKDS/2` + XML + GZip」二进制（客户端 `RetrieveDataSet` 检测魔数后按 XML 解析）。该格式**老 JSON 客户端无法解析**。此改造部署后，本文件 §4 的 JSON 返回描述对启用新格式的环境不再成立——对接前先与部署方确认服务端版本；本文档的其余契约（鉴权、权限映射、linkResult 结构、入参结构）不受影响。
