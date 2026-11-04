# 模型的三个消费环境

同一份模型定义（SYSSEARCH / 模型 XML）被三个环境消费。三环境的字段契约与执行机制见 `endpoints.md`（权威）；本文件只讲差异与生成约束。

| 环境 | 入口 | 消费的字段 | 本版状态 |
|------|------|-----------|---------|
| **模型运行器（fDataAnalysis）** | WinForms：`fDataModelList` → 双击/btnTest → `fDataAnalysis` | SQLScript 四件套、参数四件套、CallFunction、JavaScript、ModelSetting、ChartType、CubeSetting、全部 `--LINKxxx` 标记 | ✅ 首版覆盖，持续基准 |
| **TotalLINK APP（H5 界面）** | 移动端壳渲染服务端返回的 HTML 片段（`linkDMH5Data` 链） | `H5List`/`H5GridHeader`+`H5GridDetail`、`H5Edit`、`H5NewRec`、`H5Para`、`H5AttPara`、`H5Chart`、`H5MaxLines`、按钮由脚本非空派生 | ✅ 问卷覆盖（discovery.md L2）；模板从样例索引克隆 |
| **FB 网页表单（formbuilder）** | 浏览器端，`linkDMFormData` 链 | **500 伴生模型**的 `H5PARA`(formSetting JSON) + `SEARCHSELECT`(formData)、主模型单行查询、`tableData`/`selectList` 引用子模型、`LINKFORMMOD` 骨架 | ✅ 问卷覆盖（discovery.md L2-2）；模板从样例索引克隆 |

## 给生成阶段的约束

1. 按任务书的目标环境决定 H5 族字段：只做运行器/AI → 留空；含 APP/FB → 必须显式设计（服务端兜底已删除）。
2. FB 表单是**模型族**：主模型（单行查询 + `SQLClear` 承载保存）+ 500 伴生模型，一次生成两份 XML。
3. 模板型内容（H5LIST/H5PARA/500 表单 JSON）不从零手写：从 `samples-index.md` 或任务书 §6 指定的存量模型克隆，只替换 `#列名#` 与列名。
4. 用户需求如果明确说「APP 上用」「FB 网页上用」，问卷按对应能力组走，交付时人工断言清单交用户实机确认（`model run` 验不了模板渲染）。
5. 未来扩展：在此文档补环境差异，在 `endpoints.md` 补契约，不重构语法参考（fields/link-flags/callfunction-actions/placeholders 是环境无关的）。

## 连接（ConnString）路由与多库事实

`ConnString` 决定脚本在哪个数据库执行，**同一环境往往并存多个连接**，表必须挂对连接：

- 各连接的表域不同：如 TotalLINK 开发环境中，`LINKDB` = MES 业务表（STKAPLH/STKAPL/ITM 等），
  `LINKX3DEMO` = X3 ERP 表（DEMO.ITMMASTER 等）。哪个连接有哪些表**查不到静态清单**，
  以 `model dict` 能否返回列 + 存量模型引用为证据，拿不准就问用户。
- **跨连接不能 JOIN**：一条脚本只在一个连接上执行，SQL 里只能引用该连接库内的表。
  需要跨库信息时拆成两个模型（各自挂自己的连接），或由业务侧冗余字段承担。
- `dict` 对「不在当前字典模型覆盖内的表」会返回 `status ok` + 空列清单——**这不是表不存在**，
  可能只是表在另一个连接的库上。空列时先怀疑连接归属，再问用户（CLI 侧已有对应提示）。
- 问卷 L1-1（涉及哪些表）必须连带确认**每张表所在的连接**，并写进任务书 §1 的 ConnString 栏。

### APP 与 Client 的传参模式差异

同一段 SQLRemove/行定位脚本在两端行为不同：APP 按钮删除走模型参数 `{0}`，
Client/运行器走行级令牌 `#LINKROWID#`。权威说明见 `app-buttons.md` §0。
