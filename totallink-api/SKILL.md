---
name: totallink-api
description: TotalLINK 服务端 HTTP 接口契约权威文档——第三方系统对接 TotalLINK 时使用的 8 个端点（用户登录、数据查询、行提交、网格提交、上下文动作、数据提交、文件上传）。当用户要求开发「第三方系统对接 TotalLINK」「调用 TotalLINK API」「集成 TotalLINK 服务端」的代码时使用。定位是接口契约参照（开发参考资料），不是 Agent 运行时直调通道（那是 totallink-base 的 tlk.py / linkDMAIAction）。
---

# TotalLINK HTTP 对接契约（totallink-api）

帮用户开发**第三方系统对接 TotalLINK 服务端**的代码时，本文档是接口契约的权威参照。

## 权威基准

- 基准源码：**LINKIIS 项目**（旧 C# ASP.NET Web API，本机路径 `GitHub/LINK/LINKIIS`，GitHub 仓库 `randyliuyc/LINK`）。所有契约结论附 `文件:行号` 证据。
- 迁移项目（LINK.Core，.NET 10）的这些接口行为对齐 LINKIIS；唯一已知差异（linkDMDatasetResult 的 XML+GZip 二进制 DataSet 格式改造）作为**部署注意项**标注，不混入主契约——见 `references/endpoints.md` 末节。
- 服务端实际 URL 带 `api/` 前缀：`http(s)://<server>/api/{Controller}/{Action}`（不要写成 `/{Controller}/{Action}`）。

## 接口清单

| # | 端点 | 用途 | 详情 |
|---|------|------|------|
| 1 | `POST api/LINK/linkUserLogin` | 用户名/密码登录（**服务端对接主路径**，token 在返回体中） | endpoints.md §1 |
| 2 | `POST api/LINK/linkUserLoginAPI` | 浏览器集成登录（需预签发 linkToken，token 走 HttpOnly Cookie） | endpoints.md §2 |
| 3 | `GET api/LINK/linkUserByToken` | 解析 token 得到用户信息（会话桥接用） | endpoints.md §3 |
| 4 | `POST api/DataModel/linkDMDatasetResult` | 执行模型查询脚本，返回 DataSet JSON | endpoints.md §4 |
| 5 | `POST api/DataModel/linkDMGridRowSubmit` | 单行提交（新增/编辑/删除/动作） | endpoints.md §5 |
| 6 | `POST api/DataModel/linkDMGridDataSubmit` | 多行网格提交 | endpoints.md §6 |
| 7 | `POST api/DataModel/linkDMContextFunBack` | 触发附加模型（上下文动作） | endpoints.md §7 |
| 8 | `POST api/DataModel/linkDMDataSubmit` | 提交任意 JSON 到模型 CALLFUNCTION DataSubmit 过程 | endpoints.md §8 |
| — | `POST api/DataModel/linkDMFileUpload` | 文件上传（multipart，路径由模型脚本决定） | endpoints.md §9 |

## 调用链总览

```text
第三方系统                      TotalLINK 服务端
    │  ① linkUserLogin(用户/密码)      │
    │◄─────── data = loginID(token) ───┤
    │                                  │
    │  ② 后续每个调用：body 里带        │
    │     "loginID": "<token>"         │
    │  ──► linkDMDatasetResult /       │
    │      linkDMGridRowSubmit / ... ──► 服务端 3DES 解析 token
    │◄─────── linkResult JSON ─────────┤ 还原用户上下文 + 按模型校验权限
```

- 令牌机制、双轨下发（body vs Cookie）、token 传递陷阱：读 `references/auth-and-errors.md`。
- 每个接口的入参 JSON 结构、权限校验映射、最小请求/响应示例：读 `references/endpoints.md`。

## 必读文档

| 任务 | 必读 |
|------|------|
| 开始任何对接开发（第一入口） | `references/auth-and-errors.md`（token 生命周期 + linkResult 语义 + 错误对照） |
| 写具体接口的调用代码 | `references/endpoints.md` 对应小节 |
| 拿不准某个响应字段/错误怎么处理 | `references/endpoints.md` 通用约定节 + `references/auth-and-errors.md` 错误表 |

## 与其他 Skill 的分工

- **model-designer**：建模侧——把业务需求设计成数据模型（SYSSEARCH）并落库。本 skill：对接侧——外部系统用 HTTP 消费**已建好**的模型能力。两者不重叠：接口调用的 dmCode/dmNum 是模型编号，建模本身去 model-designer。
- **totallink-base（仓库根 SKILL.md）**：AI 通道——`tlk_` 令牌 + `linkDMAIAction` 端点 + `tlk.py`。与本 skill 是**两套独立通道**（不同端点、不同凭证体系）；本 skill 文档不适用 tlk.py 调用。
- **totallink-app-help / formbuilder-json-generator**：FB/APP 壳前端如何消费端点（按钮 action.api 0~8 / 1~7 与本 skill 的 HTTP 端点不是一回事，编号错位，勿混用）。

## 明确不在本文档范围

服务端内部机制，第三方对接方不应依赖：TotaLINKForward 转发、`X-Internal-Call` 内部互调、3DES token 内部结构与豁免值。遇到相关需求时提示用户走官方支持渠道，不要在对接代码里模拟这些行为。
