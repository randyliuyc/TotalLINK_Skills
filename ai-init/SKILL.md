---
name: ai-init
description: TotalLINK AI 环境初始化——用户新配置一个环境（env add 之后），或要求对 AI 环境/额度/积分进行初始化时，导入本目录 models/ 的 LINKAIINIT 模型组，并执行 SYSINFOMATION230X/501「LINKAI 环境初始化」动作脚本（新建 LINKAIAVT/LINKAIBAL 表并固化汇总行基线）。
---

# TotalLINK AI 环境初始化（ai-init）

新环境首次使用 AI 能力前，服务端数据库还没有 `LINKAIAVT`（激活记录）/`LINKAIBAL`（额度余额）两张表及防篡改汇总行基线，`SYSINFOMATION/210~230` 等额度模型会查不到数据或报错。本 Skill 负责把这组模型导入目标环境并执行初始化脚本。

## 触发条件

- 用户刚通过 `tlk env add` 配置了一个**新环境**（首次使用该环境）
- 用户要求「初始化 AI 环境」「初始化额度/积分」「环境初始化」

## 模型组（models/，共 6 个）

| 文件 | 代码#编号 | 作用 |
|------|-----------|------|
| `SEARCHLIST#100-AI Tool List.xml` | SEARCHLIST#100 | AI 工具发现（`tools search` 数据源） |
| `SYSINFOMATION#210-我的积分消耗记录.xml` | SYSINFOMATION#210 | 调用记录查询（0） |
| `SYSINFOMATION#220-我的积分使用情况.xml` | SYSINFOMATION#220 | 额度查询（0，`auth verify` 依赖） |
| `SYSINFOMATION#230-My AI Quota Activation.xml` | SYSINFOMATION#230 | 额度激活（0） |
| `SYSINFOMATION#300-Formbuilder单据模板管理.xml` | SYSINFOMATION#300 | FB 单据模板查询/落库（0） |
| `SYSINFOMATION230X#501-LINKAI 环境初始化.xml` | SYSINFOMATION230X#501 | **初始化动作（4）**：建表 + 固化汇总行基线 |

## 执行流程

1. **确认环境可用**：`python3 scripts/tlk.py auth verify` 通过（AUTH/NETWORK 失败先修令牌/地址，不导入）。
2. **逐个导入**（路径含 `#` 和空格，必须加引号）：

   ```bash
   python3 scripts/tlk.py model import "ai-init/models/SEARCHLIST#100-AI Tool List.xml"
   python3 scripts/tlk.py model import "ai-init/models/SYSINFOMATION#210-我的积分消耗记录.xml"
   python3 scripts/tlk.py model import "ai-init/models/SYSINFOMATION#220-我的积分使用情况.xml"
   python3 scripts/tlk.py model import "ai-init/models/SYSINFOMATION#230-My AI Quota Activation.xml"
   python3 scripts/tlk.py model import "ai-init/models/SYSINFOMATION#300-Formbuilder单据模板管理.xml"
   python3 scripts/tlk.py model import "ai-init/models/SYSINFOMATION230X#501-LINKAI 环境初始化.xml"
   ```

   - 返回 `action: created` 为正常；报「已存在」说明该模型导入过，**跳过**；确需覆盖先征得用户同意再加 `--force`。
   - 全部 404（环境未部署 `linkDMImport`）→ 告知用户该环境版本不支持写入，改为交付 XML 让管理员手工导入，流程终止。

3. **执行初始化动作**（第 501 个模型，全部导入完成后执行）：

   ```bash
   python3 scripts/tlk.py call SYSINFOMATION230X 501 --script-type 4 --params-json '[]'
   ```

   ⚠️ **必须用 `call`，不能用 `model run`**——`model run` 的 script-type ≠ 0 只返回 `formattedScript`，不执行数据库。

4. **验证**：重跑 `python3 scripts/tlk.py auth verify`；`SYSINFOMATION/220` 能返回 `quota.months` 即初始化成功。

## 幂等与注意

- 501 脚本自身幂等（`IF OBJECT_ID ... IS NULL` / `IF NOT EXISTS` 基线行），重跑安全，不会重复建表或重复插基线。
- XML 里的 `MD5HASH` 是导出快照，导入时服务端重算，无须关心。
- `CUSCODE` 留空（客户归属由服务端按登录环境决定）。
- 导入是写入操作：**执行前向用户报一句将导入哪些模型、是否覆盖已存在模型**，确认后再动手。
