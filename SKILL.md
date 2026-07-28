---
name: totallink-base
slug: totallink
description:
  TotalLINK 平台基础 Skill，提供多项目认证、工具发现和统一 API 调用能力。
  所有场景化 Skill 均依赖本 Skill。
setup:
  required:
    - Python 3.9+
---

# TotalLINK 基础 Skill

> 支持 WorkBuddy 及任何能执行 shell 的 AI Agent。脚本位于相对于本文件的 `scripts/` 目录。

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
| error | 含义 | 处理 |
|-------|------|------|
| `CONFIG` | 配置文件缺失 | 引导创建项目 |
| `BIZ: 没有操作权限` | 令牌过期/无效或项目配置信息错误 | 提示用户检查令牌并执行更新命令。**禁止尝试切换项目**——令牌有效时不会出现此错误，切换项目只会浪费时间 |
| `BIZ` | 其他业务错误 | 告知用户 `message` 内容 |
| `HTTP 5xx` | 后端异常 | 提示稍后重试 |

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
