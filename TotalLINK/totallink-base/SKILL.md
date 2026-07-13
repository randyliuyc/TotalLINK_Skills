---
name: totallink-base
slug: totallink
description:
  TotalLINK 数据分析平台基础 Skill，提供认证管理、动态工具发现和通用 API 调用能力。
  所有 TotalLINK 场景化 Skill（报销审核、库存管理、客户分析等）均依赖本基础 Skill。
metadata:
  workbuddy:
    env:
      TOTALLINK_AUTH_TOKEN: ""
      TOTALLINK_BASE_URL: "http://124.71.144.80:8088"
    note: "Token 和 Base URL 首次使用时由用户提供，持久化到 ~/.totallink/config.json，后续自动读取"
---

# TotalLINK 基础 Skill

## 认证管理

### 首次使用

用户提供 TotalLINK 授权令牌和服务地址，持久化到 `~/.totallink/config.json`：

```json
{
  "auth_token": "tlk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "base_url": "http://124.71.144.80:8088"
}
```

若用户未指定 `base_url`，默认使用 `http://124.71.144.80:8088`。

### 后续使用

每次调用时从配置文件读取令牌和服务地址，注入为环境变量：

```bash
export TOTALLINK_AUTH_TOKEN=$(cat ~/.totallink/config.json | python3 -c "import sys,json; print(json.load(sys.stdin)['auth_token'])")
export TOTALLINK_BASE_URL=$(cat ~/.totallink/config.json | python3 -c "import sys,json; print(json.load(sys.stdin)['base_url'])")
```

### 配置变更

- 检测到认证失败（`HTTP 401/403` 或 `isSuccess: "false"`）时，提示用户检查令牌并重新提供
- 若连接超时或 `HTTP 5xx`，提示用户检查 `base_url` 是否正确可达
- 更新 `~/.totallink/config.json` 对应字段即可，无需重新配置全部

---

## 工具发现（可选）

仅在需要探索未知工具时使用。已知工具应直接硬编码 `dmCode`/`dmNum`，跳过此步。

```
POST ${TOTALLINK_BASE_URL}/api/DataModel/linkDMAIResult

{
  "loginID": "${TOTALLINK_AUTH_TOKEN}",
  "par": {
    "dmCode": "SEARCHLIST",
    "dmNum": 100,
    "Para": []
  }
}
```

返回的 `data.Table` 包含工具列表，关键字段：
- `TOOL_CODE` → dmCode
- `TOOL_NUM` → dmNum
- `TOOL_NAME` → 工具名称
- `TOOL_DESC` → 描述（含参数说明）
- `TOOL_TYPE` → AIResult / AIRowSubmit / AIDataSubmit

---

## API 调用

所有 API 调用统一通过 `scripts/totallink_api.py` 脚本执行，脚本自动处理认证、Payload 构造和错误解析。

### 三种调用模式

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
```

### 响应处理

- 成功：输出 JSON 含 `data` 字段，可通过 `python3 -c "import sys,json; d=json.load(sys.stdin); ..."` 提取
- 出错：输出 JSON 含 `error` 字段 + 非零退出码，常见类型：
  - `CONFIG` — 配置文件缺失
  - `AUTH` — 令牌无效（提示用户更新）
  - `NETWORK` — 无法连接（检查 base_url）
  - `HTTP` — HTTP 错误
  - `BIZ` — 业务错误（`isSuccess: "false"`）

### 手动 JSON 参考

如需了解完整 Payload 结构，参见 [references/api-templates.md](references/api-templates.md)。

---

## 场景化 Skill 引用方式

场景化 Skill 在文档开头声明依赖，通过脚本调用 API：

```markdown
## 前置条件

- **TotalLINK 认证**：参照基础 Skill 完成 `${TOTALLINK_AUTH_TOKEN}` 配置
- **API 调用**：通过 `scripts/totallink_api.py` 调用，详见基础 Skill
```

调用时脚本路径相对于 `totallink-base/` 目录，场景 Skill 中使用 `../totallink-base/scripts/totallink_api.py`。

---

## 错误处理

脚本自动解析错误并以 JSON + 非零退出码返回，场景 Skill 根据 `error` 字段处理：
- `AUTH` → 令牌无效，提示用户重新提供
- `NETWORK` → 后端不可达，提示检查 base_url
- `BIZ` → 检查 `message` 字段了解业务错误详情
- `HTTP 5xx` → 后端异常，稍后重试
