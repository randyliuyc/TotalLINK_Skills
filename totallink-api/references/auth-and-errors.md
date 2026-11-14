# 认证、令牌与错误语义

> 权威基准：LINKIIS 项目（GitHub `randyliuyc/LINK`）。写对接代码前先读本文；具体接口入参见 `endpoints.md`。

## 1. token 是什么

- 登录接口返回的 `loginID` **就是 token 字符串**（LinkToken），服务端用 3DES 对称解密还原用户上下文（`LINKController.cs:276` 调 `MLTSimple3Des.GetTokenInf`）。
- 对接方只做一件事：**妥善保管并原样回传**。不要解析、缓存拆解或拼改它的内容；它过期/失效只能重新登录获取。
- token 即会话凭证——泄露等同账号泄露。服务端到服务器对接建议：配置而非硬编码凭证、HTTPS 传输（服务端 CORS 全开且无 IP 白名单，`Web.config:67-73`）、不落日志（服务端已对日志做 token/密码脱敏，`LINKController.cs:101-103`，但对接方自己也不该打印）。

## 2. 双轨下发与传递方式（最易踩坑处）

| 轨道 | 登录接口 | token 下发位置 | 后续调用如何带 |
|------|----------|----------------|----------------|
| APP/客户端/服务器 | `linkUserLogin` | 返回体 `data` | 每个请求 body 的 `loginID` 字段 |
| 浏览器集成 | `linkUserLoginAPI` | HttpOnly Cookie `TotalLINK_TOKEN`（24h，`LINKController.cs:186-195`） | 浏览器自动带 Cookie，body `loginID` 留空（服务端 Cookie 兜底，`LINKController.cs:1284-1300`） |

**决策规则**：
- 纯服务端/脚本对接（无浏览器）→ 只能走 `linkUserLogin` 轨道；`linkUserLoginAPI` 需要预签发的第三方 `linkToken` 且 token 在 HttpOnly Cookie 里，服务端代码拿不到也不该拿。
- 浏览器内嵌直连 → 用 `linkUserLoginAPI`，JS 无法读取 Cookie 是设计行为（防 XSS），不要想办法绕。
- 两种方式不要混用：混用会出现「同一个账号两个会话互相踢」或权限上下文不一致。

## 3. 会话生命周期与重登录

- 服务端未在 HTTP 层给 token 强过期时间（Cookie 轨道 24h 是浏览器侧约束）；token 失效由服务端解析失败判定。
- **对接方必须实现统一重登录逻辑**：任一调用返回 `InvalidLinkToken` → 重新 `linkUserLogin` 换新 token → 重放当前调用。不要在业务代码里散落处理。
- 密码即将过期（≤7 天）登录仍成功但 `action="warning"`（`LINKController.cs:90-98`）——记录并提醒维护密码，不要当作登录失败。

## 4. linkResult.action 三分支语义

`LinkFunction/LinkDefine.cs:48-53`；服务端脚本用 `LINKWARNING:` / `LINKCONFIRM:` / `LINKPREVENT:` 前缀生成（`MLTShared.vb:2663-2669`）。

| action | 含义 | 对接方行为 |
|--------|------|-----------|
| `""` / null | 正常 | 继续 |
| `warning` | 提示信息，服务端已继续 | 记录/透出 message，继续处理 data |
| `confirm` | 服务端要求人工确认才能继续 | **终止本次自动化流程**，把 message 呈现给人，等明确确认后重发请求（可带 skip 等参数时由模型定义决定） |
| `prevent` | 服务端拒绝执行 | 视为业务失败，不重试相同请求 |

⚠️ 防呆规则（模型脚本的数据检查）走的就是 confirm/prevent——**忽略 action = 绕过业务防呆**，例如重复审批、提交被拒单据。这是对接代码最常见的集成事故来源。

## 5. 错误对照表

判定方式：先看 `isSuccess`（字符串 `"true"/"false"`），再看 `data` 中的错误码、`action` 中的分支。

| 错误信号 | 来源端点 | 含义 | 处理 |
|----------|----------|------|------|
| `data="InvalidLinkToken"` | 全部 | token 无效/会话失效 | 重登录 → 重放（见 §3） |
| `data="AccessFail"` | GridRowSubmit/GridDataSubmit/ContextFunBack/DataSubmit | 无该模型对应功能权限 | 停止重试；找管理员开通 `EDIT/NEW/TREAT/REMOVE` 权限 |
| `data="ModelNotExist"` | DataModel 各端点 | dmCode/dmNum 不存在 | 核对模型编号（用 model-designer 的 tools search / 服务端确认），不要试探编号 |
| `data="NoConnection"` | DataModel 各端点 | 服务端连接串未初始化 | 服务端环境问题，重试无效，报告部署方 |
| `data="InvalidFileType"` | FileUpload | 扩展名不在白名单/命中黑名单 | 换允许的文件类型（白名单见 endpoints.md §9） |
| `data` 以 `err_` 开头 | 登录端点 | 登录失败错误码 | 按 message 提示；检查用户名/密码/设备标识 |
| `message` 含异常堆栈 | DatasetResult 等 | 服务端执行异常 | report-only；不要依赖 message 格式（含堆栈，未来版本可能变化） |

登录类失败（`isSuccess=false` 且 `action="warning"`）与业务失败区分：登录端点的失败也是 warning 形态（`LINKController.cs:80-82, 167-169`）。

## 6. 权限模型速记

- token 解析后服务端还原 `用户 + 角色 + 用户设置`（`LINKController.cs:1363-1375`）——权限跟人走，与对接系统无关。
- 每个写端点的功能权限映射（`FuncAccess`）见 `endpoints.md` 对应小节；查询端点（DatasetResult）无显式功能权限校验，但模型脚本内部可能有自己的数据权限逻辑。
- 第三方对接账号建议：专用账号 + 最小权限（只开需要的模型权限），并在服务端功能授权中配置。
