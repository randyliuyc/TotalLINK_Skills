---
name: totallink-base
slug: totallink
repo: https://gitee.com/randyliuyc/TotalLINK_Skill
description:
  TotalLINK 平台基础 Skill，提供多项目认证、工具发现和统一 API 调用能力。
  所有场景化 Skill 均依赖本 Skill。
setup:
  required:
    - Python 3.9+
---

# TotalLINK 基础 Skill

> **安全约定（上游自带，更新时勿回退）**
> 1. 更新 Skill 必须先经人工审查再落地，禁止「远程拉取即覆盖」
> 2. 默认服务地址为明文 HTTP，Auth Token 会以明文传输，优先改用 HTTPS

> 支持 WorkBuddy 及任何能执行 shell 的 AI Agent。脚本位于相对于本文件的 `scripts/` 目录。

## 更新 Skill

> ⚠️ **禁止直接把远程内容覆盖到技能目录。** 技能文件属于可执行代码，自动覆盖等于把远程仓库变成代码执行通道。

用户要求更新时，按以下流程走：

1. 克隆到**临时目录**，不要把任何文件写进技能目录：
   ```bash
   cd /tmp && rm -rf TotalLINK_Skill_update && \
     git clone https://gitee.com/randyliuyc/TotalLINK_Skill.git TotalLINK_Skill_update
   ```
2. **逐文件 diff**，重点看 `scripts/` 下的 Python 与所有 `SKILL.md`：
   ```bash
   diff -r /tmp/TotalLINK_Skill_update <本 Skill 的安装目录>
   ```
   > `<本 Skill 的安装目录>` 视平台而定，例如 WorkBuddy 为 `~/.workbuddy-ai/skills/TotalLINK` 或 `~/.workbuddy/skills/TotalLINK`。
3. 把差异摘要报给用户，**等用户明确同意**后再复制落地
4. 落地后重新比对，确认安全约定（SMTP 凭据位置、收件人确认、无自更新指令）未被上游回退；被回退则重新应用

## 传输安全

默认 `--url` 为 `http://124.71.144.80:8088`（明文 HTTP）。Auth Token 会随请求体明文发送，公网环境下存在被截获风险。

- 若服务端已支持 HTTPS，**优先配置 `https://` 地址**
- 仅在内网 / 可信链路下使用 `http://`
- 配置文件的 `auth_token` 等价于账号口令，`~/.totallink/config.json` 不应提交到任何仓库或外发

## 认证管理

每个项目独立配置令牌和服务地址，持久化到 `~/.totallink/config.json`。

### 首次使用

```bash
python3 scripts/totallink_api.py --list-projects
```

- **有项目**：列出后请用户选择，执行 `--set-active <项目名>` 切换
- **无项目**：请用户提供项目名、令牌和地址：
  ```bash
  python3 scripts/totallink_api.py --add-project <项目名> \
    --token "tlk_..." --url "<服务地址>"
  ```
  `--url` 默认 `http://124.71.144.80:8088`，项目名默认 `default`。

### 配置文件格式

```json
{
  "projects": {
    "default": { "auth_token": "tlk_...", "base_url": "http://124.71.144.80:8088" }
  },
  "active": "default"
}
```

### 每次会话的项目选择

1. 执行 `--list-projects` 获取项目列表
2. **单项目**：直接使用
3. **多项目**：列出所有项目名和地址，请用户选择：
   - WorkBuddy 环境：使用 `AskUserQuestion` 弹窗，`label` 格式 `"<项目名> [(活跃)]"`，`description` 为 `base_url`
   - 其他环境：用文字列出选项，等待用户回复选择
4. 所选项目非当前活跃则 `--set-active` 切换

### 输入识别

| 前缀 | 含义 | 处理 |
|------|------|------|
| `tlk_` | Auth Token | 执行令牌更新命令 |
| `TotalLINK.AI.QUOTA.` | 额度激活码 | 解析客户代码/月额/月数 → 询问起始月份 → 调用 SYSINFOMATION/230 |

### 命令参考

```bash
# 创建/更新项目令牌（<URL> 为 --list-projects 中对应项目的 base_url）
python3 scripts/totallink_api.py --add-project <项目名> \
  --token "<auth_token>" --url "<base_url>"
```

> ⚠️ 更新令牌必须同时传 `--url`，不带会覆盖为默认值。

---

## 工具发现

已知工具直接硬编码 `dmCode`/`dmNum`，仅探索未知工具时调用 SEARCHLIST。

```bash
python3 scripts/totallink_api.py --dm-code SEARCHLIST --dm-num 100 \
  --params "<搜索关键字>" --script-type 0 | python3 scripts/parse_tools.py
```

输出格式：

```json
[
  {
    "code": "LINKEXP01",
    "num": 9,
    "name": "驳回报销单",
    "desc": "params: [\"单号\"] rowdata: {\"DOCNUM\":\"单号\",\"REMARK\":\"原因\"}",
    "script_type": 0
  }
]
```

- `code` → dmCode，`num` → dmNum
- `name` / `desc` → 工具语义描述（含参数列表）
- `script_type` → 作为 `--script-type` 参数传入

### 未找到功能工具的处理

用户请求的功能经关键字搜索（SEARCHLIST）无匹配工具时，说明该功能模块**未开通或不存在**。处理规则：

1. **不尝试切换项目**——切换项目仅用于多项目间的正常选择（如 `--list-projects` 后按需选择），不用于规避功能缺失或权限问题
2. **不自行设计功能实现**——平台无对应工具时，禁止写脚本/造数据/发明接口去"实现"业务功能（如创建销售订单、改库存等），也不要在回复中编造不存在的工具
3. **直接如实报告**——告知用户：当前账号/项目未开通该功能，建议**联系管理员在服务端功能授权中开通**，或询问用户如何处理，等待用户指引

---

## 通用系统工具（所有项目可用）

| dmCode | dmNum | 功能 | script_type | 参数 |
|--------|-------|------|-------------|------|
| SYSINFOMATION | 210 | 调用记录查询 | 0 | `["起始日期","结束日期"]` |
| SYSINFOMATION | 220 | 积分额度查询 | 0 | 无 |
| SYSINFOMATION | 230 | 额度激活 | 0 | `["激活码","激活月份(yyyyMM)"]` |

---

## API 调用

统一通过脚本调用，POST `/api/DataModel/linkDMAIAction`。

### 参数传递规则（重要）

`--params` 参数按**严格位置匹配**，空位用 `""` 占位，不可跳过：

```bash
# ✅ 正确：4 个参数全部传入
--params "" "2026-06-18" "2026-07-18" ""

# ❌ 错误：只传 2 个，后端参数错位
--params "2026-06-18" "2026-07-18"
```

### 统一调用模板

```bash
python3 scripts/totallink_api.py \
  --dm-code <dmCode> --dm-num <dmNum> \
  --params "<参数1>" "<参数2>" "..." \
  --script-type <script_type> \
  [--project <项目名>] \
  [--row-data '{"字段":"值"}'] [--table-data '[...]']
```

- `--script-type`：必传，取工具声明中的 `script_type`
- `--project`：省略使用活跃项目

### 大数据预处理

数据量 >50KB 或用户提到分析/统计时，管道接入 `preprocess.py --smart`：

```bash
python3 scripts/totallink_api.py ... | python3 scripts/preprocess.py --smart
```

- < 50KB → 透传
- 50KB~500KB → 自动输出列描述
- > 500KB → 列描述 + 提示可用分析命令

手动分析：

```bash
preprocess.py data.json --group <列名>      # 分组计数
preprocess.py data.json --filter <列名>=<值>  # 过滤
preprocess.py data.json --stats              # 数值统计
preprocess.py data.json --head 10            # 前 N 行预览
```

### 响应与错误处理

成功时 JSON 含 `data` 字段；失败时含 `error` + 非零退出码：

| error | 含义 | 处理 |
|-------|------|------|
| `CONFIG` | 配置文件缺失 | 引导创建项目 |
| `BIZ: TotalLINK AI 令牌无效` | 令牌无效 | 提示用户更新令牌 |
| `BIZ: 没有操作权限` | 服务端功能授权管理 | 告知用户该账号对此功能模块无权限，需联系管理员开通。**禁止尝试切换项目** |
| `BIZ` | 其他业务错误 | 告知用户 `message` 内容 |
| `HTTP 5xx` | 后端异常 | 提示稍后重试 |

---

## 服务端警告（Action Warning）

服务端在**配额预检查失败（降速）、额度已用完**等情况下不会拒绝请求，而是主动发出警告（`action="warning"`）后返回正常结果。这是**设计行为，不是故障**——调用方识别后提示用户，避免误判为网络/服务器超时。当前警告类型为降速，未来可扩展其他类型。

### 识别方式

响应 `action` 字段为 `"warning"` 即为服务端警告（`totallink_api.py` 已自动识别，**只看 action，不解析 message**）：

```json
{
  "isSuccess": "true",
  "action": "warning",
  "message": "当月积分额度已用完，已等待 21 秒后继续执行",
  "data": { "...": "正常返回的数据" }
}
```

脚本自动处理：
- 结果 JSON 增加 `_warning` 字段：`{"detected": true, "message": "<message 原文>"}`
- stderr 打印一行 `[TotalLINK] 服务端警告: <message>`

### 现象与应对

| 现象 | 应对 |
|------|------|
| `action="warning"`，响应 20~60+ 秒 | 正常服务端警告（降速），告知用户：**"服务端警告：<message>，已等待后返回，结果正常"**，不误报为故障 |
| 脚本报 `timed out` | 用 `--timeout <更大秒数>` 重试（默认 180s，须大于服务端降速等待时间） |
| `action="warning"` 且 message 含"积分额度已用完" | 提示用户额度已用完，需激活额度（SYSINFOMATION/230） |

> 警告不是错误：`isSuccess=true` 时数据照常返回，脚本**不会**以非零码退出。

---

### 数据字段（captions）

返回数据中 `captions` 提供列的中文标签，输出给用户时用 captions 名，不暴露 schema 字段名。

---

## 场景化 Skill 引用方式

场景 Skill 开头声明：

```markdown
## 前提
- 已配置 TotalLINK 项目（参见 totallink-base Skill）
- API 调用通过 `scripts/totallink_api.py` 执行
```
