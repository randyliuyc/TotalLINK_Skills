---
name: totallink-base
slug: totallink
description:
  TotalLINK 平台基础 Skill，提供多项目认证、工具发现和统一 API 调用能力。
  所有场景化 Skill 均依赖本 Skill。
metadata:
  workbuddy:
    note: "每个项目独立配置 auth_token 和 base_url，持久化到 ~/.totallink/config.json"
---

# TotalLINK 基础 Skill

## 认证管理

支持**多项目环境**，每个项目独立配置令牌和服务地址，持久化到 `~/.totallink/config.json`。

### 首次使用

```bash
python3 scripts/totallink_api.py --list-projects
```

- **有项目**：列出列表，提示用户选择，然后 `--set-active <项目名>` 切换
- **无项目**：提示用户提供信息，创建项目：
  ```bash
  python3 scripts/totallink_api.py --add-project <项目名> \
    --token "tlk_..." --url "http://124.71.144.80:8088"
  ```
  未提供 `--url` 默认 `http://124.71.144.80:8088`，未提供项目名默认 `default`。

### 配置文件格式

```json
{
  "projects": {
    "default": { "auth_token": "tlk_...", "base_url": "http://124.71.144.80:8088" },
    "uat":     { "auth_token": "tlk_...", "base_url": "http://uat-server:8088" }
  },
  "active": "default"
}
```

### 每次会话的项目选择

1. 执行 `--list-projects` 获取项目列表
2. **单项目**：直接使用
3. **多项目**：使用 `AskUserQuestion` 弹出交互式选择：

   ```
   AskUserQuestion:
     question: "当前有 N 个 TotalLINK 项目，请选择要使用的环境："
     header: "项目选择"
     options:
       - label: "TotalLINK Development (活跃)"   description: "http://124.71.144.80:8088"
       - label: "Tamper"                         description: "http://124.71.144.80:8081"
   ```

   `label` 格式 `"<项目名> [(活跃)]"`，`description` 为 `base_url`。如所选项目不是当前活跃项目则 `--set-active` 切换。

### 输入识别

收到以下格式的字符串时自动处理：

| 前缀 | 含义 | 处理 |
|------|------|------|
| `tlk_` | Auth Token | 执行令牌更新命令 |
| `TotalLINK.AI.QUOTA.` | 额度激活码 | 调用 SYSINFOMATION/230 激活，需选择起始月份 |

### 命令参考

```bash
# 创建/更新项目令牌（<URL> 为当前项目配置的 base_url，可从 --list-projects 查看）
python3 scripts/totallink_api.py --add-project <项目名> --token "<auth_token>" --url "<base_url>"
```

> ⚠️ 更新令牌时 `--url` 必传，不带则覆盖为默认值导致连接错误。

---

## 工具发现

已知工具应直接硬编码 `dmCode`/`dmNum`，仅在探索未知工具时才调用 SEARCHLIST。

```bash
# 搜索工具（空关键字返回全部，传关键字自动过滤）
python3 scripts/totallink_api.py --dm-code SEARCHLIST --dm-num 100 \
  --params "<搜索关键字>" --script-type 0 | python3 scripts/parse_tools.py
```

管道接入 `scripts/parse_tools.py`，将 `Table` 转为结构化 JSON：

```json
[
  {
    "code": "LINKEXP01",
    "num": 9,
    "name": "驳回报销单",
    "desc": "驳回报销单。params: [\"单据号\"] rowdata: {\"DOCNUM\": \"单据号\", \"REMARK\": \"驳回原因\"}",
    "script_type": 0
  }
]
```

- `code` → dmCode，`num` → dmNum
- `name` / `desc` → 工具语义描述（含参数列表）
- `script_type` → 直接作为 `--script-type` 参数传入

---

## 通用系统工具（所有项目可用）

以下工具硬编码使用，无需通过 SEARCHLIST 发现：

| dmCode | dmNum | 功能 | script_type | 参数 |
|--------|-------|------|-------------|------|
| SYSINFOMATION | 210 | 调用记录查询 | 0 | `["起始日期","结束日期"]` |
| SYSINFOMATION | 220 | 积分额度���询 | 0 | 无 |
| SYSINFOMATION | 230 | 额度激活 | 0 | `["激活码","激活月份(yyyyMM)"]` |

---

## API 调用

所有调用通过 `scripts/totallink_api.py` 执行，统一 POST `/api/DataModel/linkDMAIAction`，服务端根据 `--script-type` 自动区分查询/提交。

### 参数传递规则（重要）

`--params` 后的参数按**严格位置匹配**，顺序和数量必须与工具 `params: [...]` 列表一致。**不可跳过位置**，空位用 `""` 占位。

```bash
# ✅ 正确：4 个参数全部传入
--params "" "2026-06-18" "2026-07-18" ""

# ❌ 错误：只传 2 个，后端参数错位
--params "2026-06-18" "2026-07-18"
```

### 统一调用模板

```bash
python3 scripts/totallink_api.py --dm-code <dmCode> --dm-num <dmNum> \
  --params "<参数1>" "<参数2>" "..." \
  --script-type <script_type> \
  [--project <项目名>] \
  [--row-data '{"字段":"值"}'] [--table-data '[...]']
```

- `--script-type`：必传，取工具声明中的 `script_type` 值（来自工具发现结果或场景 Skill 硬编码的工具表）
- `--row-data` / `--table-data`：按工具说明按需传入
- `--project`：省略时使用活跃项目，显式指定可临时切换

### 大数据预处理

当数据量较大（>50KB）或用户提到「分析/汇总/统计」时，管道接入 `scripts/preprocess.py --smart`：

```bash
python3 scripts/totallink_api.py ... --script-type 0 \
  | python3 scripts/preprocess.py --smart
```

**行为**：
- < 50KB → 透传原始 JSON，零干扰
- 50KB~500KB → 自动输出列描述（非空率、去重值）
- > 500KB → 列描述 + 提示可用分析命令

**手动分析**：
```bash
preprocess.py data.json --group <列名>     # 按列分组计数
preprocess.py data.json --filter <列名>=<值> # 过滤
preprocess.py data.json --stats             # 数值列 min/avg/max
preprocess.py data.json --head 10           # 前 N 行预览
```

### 响应与错误处理

成功时 JSON 含 `data` 和 `_project`；失败时含 `error` + 非零退出码：

| error | 含义 | 处理 |
|-------|------|------|
| `CONFIG` | 配置文件缺失或项目不存在 | 引导创建项目 |
| `BIZ: 没有操作权限` | 令牌过期或无效 | 提示用户检查令牌，执行令牌更新命令 |
| `BIZ` | 业务错误（`isSuccess: "false"`） | 查看 `message` |
| `HTTP 5xx` | 后端异常 | 稍后重试 |

### 数据字段（captions）

`data.Table` 可能包含 `captions` 对象，提供 schema 字段的本地化标签（随用户语言变化）：

```json
{
  "schema": ["ELECOD", "ELENAM", "ELEUNT"],
  "captions": { "ELECOD": "元素编码", "ELENAM": "元素名称", "ELEUNT": "单位" },
  "data": [["C", "Carbon", "%"]]
}
```

- `schema` — 程序字段名（不变）
- `captions` — 人/Agent 可读标签，**以 captions 为准理解含义**
- 输出给用户时用 captions 标签，不直接暴露 schema 字段名

### 手动 JSON 参考

完整 Payload 结构参见 [references/api-templates.md](references/api-templates.md)。

---

## 场景化 Skill 引用方式

场景 Skill 开头声明依赖：

```markdown
## 前置条件
- **TotalLINK 项目选择**：参照基础 Skill 完成项目配置
- **API 调用**：通过 `../totallink-base/scripts/totallink_api.py` 调用
```
