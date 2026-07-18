---
name: totallink-base
slug: totallink
description:
  TotalLINK 数据分析平台基础 Skill，提供多项目认证管理、动态工具发现和通用 API 调用能力。
  所有 TotalLINK 场景化 Skill（报销审核、库存管理、客户分析等）均依赖本基础 Skill。
metadata:
  workbuddy:
    env:
      TOTALLINK_AUTH_TOKEN: ""
      TOTALLINK_BASE_URL: "http://124.71.144.80:8088"
    note: "支持多项目环境，每个项目独立配置 auth_token 和 base_url，持久化到 ~/.totallink/config.json"
---

# TotalLINK 基础 Skill

## 认证管理

TotalLINK 支持**多项目环境**，每个项目独立配置认证令牌和服务地址，统一持久化到 `~/.totallink/config.json`。

### 首次使用：选择或创建项目

**第一步：检查已配置的项目**

```bash
python3 scripts/totallink_api.py --list-projects
```

**第二步：根据结果处理**

- **有项目**：列出项目列表，提示用户选择（如 `["default", "uat", "prod"]`）。用户选择后，设置活跃项目：
  ```bash
  python3 scripts/totallink_api.py --set-active <项目名>
  ```

- **无项目**：提示用户提供项目信息，创建第一个项目：
  ```bash
  python3 scripts/totallink_api.py --add-project <项目名> \
    --token "tlk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
    --url "http://124.71.144.80:8088"
  ```
  若用户未提供 `--url`，默认使用 `http://124.71.144.80:8088`。
  若用户未提供项目名，默认使用 `default`。

### 配置文件格式

```json
{
  "projects": {
    "default": {
      "auth_token": "tlk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "base_url": "http://124.71.144.80:8088"
    },
    "uat": {
      "auth_token": "tlk_yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy",
      "base_url": "http://uat-server:8088"
    }
  },
  "active": "default"
}
```

### 项目选择流程（每次会话）

AI Agent 在每次会话开始时应遵循以下流程：

1. 执行 `python3 scripts/totallink_api.py --list-projects` 获取项目列表
2. **只有一个项目**：直接使用，无需询问用户
3. **有多个项目**：使用 `AskUserQuestion` 弹出交互式选择菜单，而非让用户手动输入项目名：

   ```
   AskUserQuestion:
     question: "当前有 N 个 TotalLINK 项目，请选择要使用的环境："
     header: "项目选择"
     options:
       - label: "default (活跃)"    description: "http://124.71.144.80:8088"
       - label: "Tamper"            description: "http://124.71.144.80:8081"
   ```

   每个选项的 `label` 格式为 `"<项目名> [(活跃)]"`，`description` 为 `base_url`。用户点击后，如果所选项目不是当前活跃项目则执行 `--set-active <项目名>` 切换；如果已是活跃项目则直接确认。
4. 后续所有 API 调用可通过 `--project <项目名>` 显式指定，或省略以使用活跃项目。

### 添加新项目

当用户需要在现有配置中增加新项目时：

```bash
python3 scripts/totallink_api.py --add-project <项目名> \
  --token "<auth_token>" --url "<base_url>"
```

### 配置变更

- 检测到认证失败（`HTTP 401/403` 或 `error: "AUTH"`）→ 提示当前项目令牌失效，引导用户更新令牌
- 检测到连接失败（`error: "NETWORK"`）→ 检查当前项目的 `base_url` 是否正确可达
- 更新令牌：重新执行 `--add-project <项目名> --token <新令牌>` 即可覆盖

---

## 工具发现（可选）

仅在需要探索未知工具时使用。已知工具应直接硬编码 `dmCode`/`dmNum`，跳过此步。

### 搜索工具

```bash
# 按关键字搜索（服务端过滤）
python3 scripts/totallink_api.py --type AIResult --dm-code SEARCHLIST --dm-num 100 \
  --params "报销" | python3 scripts/parse_tools.py

# 列出所有工具（空关键字）
python3 scripts/totallink_api.py --type AIResult --dm-code SEARCHLIST --dm-num 100 \
  --params "" | python3 scripts/parse_tools.py
```

`--params` 传入搜索关键字时，服务端 `SEARCHLIST` 工具自动按 `TOOL_NAME`/`TOOL_DESC` 过滤；传空字符串时返回全部工具。管道接入 `scripts/parse_tools.py` 将原始 `Table` 转为结构化 JSON 列表。

### 解析结果

输出格式：
```json
[
  {
    "code": "LINKEXP01",
    "num": "9",
    "name": "报销单列表",
    "desc": "按日期范围查询报销单，参数：开始日期、结束日期",
    "type": "AIResult"
  }
]
```

字段说明：
- `code` → dmCode
- `num` → dmNum
- `name` → 工具名称
- `desc` → 描述（含参数说明）
- `type` → AIResult / AIRowSubmit / AIDataSubmit / AIAction（除前三种外统一调用 AIAction）

---

## API 调用

所有 API 调用统一通过 `scripts/totallink_api.py` 脚本执行，脚本自动处理项目管理、认证、Payload 构造和错误解析。

### 四种调用模式

```bash
# AIResult — 数据查询
python3 scripts/totallink_api.py --type AIResult --dm-code <dmCode> --dm-num <dmNum> \
  --params "参数1" "参数2" "..."

# AIRowSubmit — 行数据提交
python3 scripts/totallink_api.py --type AIRowSubmit --dm-code <dmCode> --dm-num <dmNum> \
  --params "参数1" --script-type <操作类型> --row-data '{"字段":"值"}'

# AIDataSubmit — 批量数据提交
python3 scripts/totallink_api.py --type AIDataSubmit --dm-code <dmCode> --dm-num <dmNum> \
  --params "参数1" --script-type <操作类型> --row-data '{"字段":"值"}' \
  --table-data '[{"字段1":"值1"},{"字段1":"值2"}]'

# AIAction — 功能操作
python3 scripts/totallink_api.py --type AIAction --dm-code <dmCode> --dm-num <dmNum> \
  --params "参数1" --script-type <操作类型> --row-data '{"字段":"值"}' \
  --table-data '[{"字段1":"值1"}]'
```

- 省略 `--project` 时自动使用活跃项目（`active` 字段指定的项目）
- 显式 `--project <项目名>` 可临时切换到其他项目

### 响应处理

- 成功：输出 JSON 含 `data` 字段和 `_project` 字段（标识当前使用的项目）
- 出错：输出 JSON 含 `error` 字段 + 非零退出码，常见类型：
  - `CONFIG` — 配置文件缺失或项目不存在
  - `AUTH` — 令牌无效（提示用户更新对应项目的令牌）
  - `NETWORK` — 无法连接（检查对应项目的 base_url）
  - `HTTP` — HTTP 错误
  - `BIZ` — 业务错误（`isSuccess: "false"`）

### 手动 JSON 参考

如需了解完整 Payload 结构，参见 [references/api-templates.md](references/api-templates.md)。

---

## 场景化 Skill 引用方式

场景化 Skill 在文档开头声明依赖，通过脚本调用 API：

```markdown
## 前置条件

- **TotalLINK 项目选择**：参照基础 Skill 完成项目选择和 `${TOTALLINK_AUTH_TOKEN}` 配置
- **API 调用**：通过 `scripts/totallink_api.py` 调用，详见基础 Skill
```

调用时脚本路径相对于 `totallink-base/` 目录，场景 Skill 中使用 `../totallink-base/scripts/totallink_api.py`。

---

## 错误处理

脚本自动解析错误并以 JSON + 非零退出码返回，场景 Skill 根据 `error` 字段处理：
- `CONFIG` → 配置文件缺失，引导用户创建项目
- `AUTH` → 令牌无效，提示用户更新对应项目的令牌
- `NETWORK` → 后端不可达，提示检查对应项目的 base_url
- `BIZ` → 检查 `message` 字段了解业务错误详情
- `HTTP 5xx` → 后端异常，稍后重试
