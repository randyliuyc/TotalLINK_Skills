#!/usr/bin/env python3
"""TotalLINK CLI 核心：配置管理、Payload 构造、请求与错误处理。

职责边界：本模块只做「读配置 → 构造请求 → 发请求 → 归类错误」，不做命令行解析与输出格式。
命令行入口见同目录 tlk.py。

所有业务调用统一走 /api/DataModel/linkDMAIAction，服务端根据 scriptType 自动区分查询/提交。

配置：~/.totallink/config.json，形如
  {"active": "<项目名>", "projects": {"<项目名>": {"auth_token": "tlk_...", "base_url": "..."}}}
"""

import json
import os
import sys
import urllib.error
import urllib.request

CONFIG_PATH = os.path.expanduser("~/.totallink/config.json")

ENDPOINT = "/api/DataModel/linkDMAIAction"

DEFAULT_BASE_URL = "http://124.71.144.80:8088"

# 服务端警告机制：响应 action="warning" 时表示服务端主动发出警告
# （如配额预检查失败后降速、额度已用完等），警告后仍会返回正常结果。
# 这是设计行为，不是故障——调用方应识别并提示用户，避免误判为网络/服务器超时。
# 判定只看 action 字段，不解析 message 内容，兼容未来其他警告类型。
DEFAULT_TIMEOUT = 180  # 请求超时（秒），需大于服务端最大降速等待时间
WARNING_ACTION = "warning"  # action 取该值时视为服务端警告

# 环境自检：额度查询模型（配额豁免组，cost=0，不会被配额拦截）
QUOTA_DM_CODE = "SYSINFOMATION"
QUOTA_DM_NUM = 220
# 额度按环境统一管理（池账户），不按用户拆分；服务端 220 的 SQL 固定 WHERE USR='TotalLINK'
QUOTA_USR = "TotalLINK"

# 工具发现：SEARCHLIST 的关键字检索
TOOL_SEARCH_DM_CODE = "SEARCHLIST"
TOOL_SEARCH_DM_NUM = 100


# ---------------------------------------------------------------- 配置

def load_all_config():
    """从 ~/.totallink/config.json 读取全部配置。"""
    if not os.path.exists(CONFIG_PATH):
        return None
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_config(cfg):
    """保存配置到文件。"""
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def get_project_config(project_name=None):
    """
    获取指定项目的认证配置。

    优先级：project_name 参数 > active 字段 > 第一个项目
    返回: (project_key, project_cfg) 或 (None, None)
    """
    cfg = load_all_config()
    if not cfg:
        return None, None

    projects = cfg.get("projects", {})

    if not projects:
        return None, None

    if project_name and project_name in projects:
        return project_name, projects[project_name]

    active = cfg.get("active")
    if active and active in projects:
        return active, projects[active]

    # fallback: 第一个项目
    first_key = next(iter(projects))
    return first_key, projects[first_key]


def list_projects():
    """列出所有项目，标记活跃项目。"""
    cfg = load_all_config()
    if not cfg:
        return []
    projects = cfg.get("projects", {})
    active = cfg.get("active", "")
    result = []
    for name, proj in projects.items():
        result.append({
            "name": name,
            "base_url": proj.get("base_url", ""),
            "active": name == active,
        })
    return result


def set_active_project(project_name):
    """设置活跃项目（精确匹配项目名）。"""
    cfg = load_all_config()
    if not cfg:
        return {"error": "CONFIG", "message": "配置文件不存在，请先创建项目配置"}
    if project_name not in cfg.get("projects", {}):
        return {"error": "CONFIG", "message": f"项目 '{project_name}' 不存在"}
    cfg["active"] = project_name
    save_config(cfg)
    return {"status": "ok", "active": project_name}


def add_project(project_name, auth_token, base_url=DEFAULT_BASE_URL):
    """添加或更新项目配置。"""
    cfg = load_all_config()
    if not cfg:
        cfg = {"projects": {}, "active": project_name}
    cfg["projects"][project_name] = {
        "auth_token": auth_token,
        "base_url": base_url,
    }
    if cfg.get("active") is None:
        cfg["active"] = project_name
    save_config(cfg)
    return {"status": "ok", "project": project_name, "active": cfg["active"]}


# ---------------------------------------------------------------- 请求

def _resolve_project(project_name=None):
    """解析项目配置，返回 (project_key, project_cfg, error)。"""
    project_key, proj_cfg = get_project_config(project_name)
    if not proj_cfg:
        return project_key, None, {
            "error": "CONFIG",
            "message": f"配置文件不存在：{CONFIG_PATH}，请先运行首次认证配置",
        }
    return project_key, proj_cfg, None


def _post(url, payload, project_key, timeout=DEFAULT_TIMEOUT):
    """
    发送 POST 请求并解析 JSON。

    网络层失败统一转成 {"error": ...}，不抛异常；成功时原样返回响应 dict。
    错误码语义：
      AUTH    — HTTP 401/403（服务端一般不会返回，令牌问题走 BIZ 分支）
      HTTP    — 其余 HTTP 错误，带 code/reason
      NETWORK — 连不上（DNS/端口/超时等）
      UNKNOWN — 其他异常
    """
    req_body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=req_body,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            return {
                "error": "AUTH",
                "message": f"令牌无效或已过期，请检查项目 '{project_key}' 的 auth_token",
            }
        return {"error": "HTTP", "code": e.code, "reason": e.reason}
    except urllib.error.URLError as e:
        return {
            "error": "NETWORK",
            "message": f"无法连接 TotalLINK 服务，请检查项目 '{project_key}' 的 base_url：{str(e.reason)}",
        }
    except Exception as e:
        return {"error": "UNKNOWN", "message": str(e)}


def call(dm_code, dm_num, params=None,
         script_type=0, row_data=None, table_data=None, project=None,
         timeout=DEFAULT_TIMEOUT):
    """
    调用 TotalLINK API，统一走 /api/DataModel/linkDMAIAction。

    参数:
        dm_code:     工具代码，如 "LINKAI2010X"
        dm_num:      工具编号，如 10
        params:      Para 参数列表（字符串数组）
        script_type: 工具的 script_type 值（整数），服务端据此自动区分查询/提交
        row_data:    rowData 字典（按工具说明按需传入）
        table_data:  tableData 列表（按工具说明按需传入）
        project:     项目名，不传则使用活跃项目
        timeout:     请求超时秒数（默认 DEFAULT_TIMEOUT，须大于服务端降速等待时间）

    返回:
        dict: API 响应 JSON，出错时包含 "error" 字段
    """
    project_key, proj_cfg, error = _resolve_project(project)
    if error:
        return error

    base_url = proj_cfg["base_url"].rstrip("/")
    url = base_url + ENDPOINT

    dm_block = {"dmCode": dm_code, "dmNum": dm_num, "Para": params or []}
    par = {
        "dm": dm_block,
        "scriptType": script_type,
        "rowData": row_data or {},
        "tableData": table_data or [],
    }

    payload = {"loginID": proj_cfg["auth_token"], "par": par}

    resp = _post(url, payload, project_key, timeout)
    if "error" in resp:
        return resp

    resp["_project"] = project_key
    if resp.get("isSuccess") == "false":
        return {"error": "BIZ", "message": resp.get("message", "未知业务错误"), "_project": project_key}

    # 检测服务端警告：action == "warning" 时服务端主动警告后返回（设计行为，非故障）。
    # 判定只看 action 字段，不解析 message；message 原文随结果保留，供提示用户时使用。
    if resp.get("action") == WARNING_ACTION:
        resp["_warning"] = {
            "detected": True,
            "message": resp.get("message", ""),
        }
        print(
            f"[TotalLINK] 服务端警告: {resp.get('message', '')}",
            file=sys.stderr,
        )

    return resp


# ---------------------------------------------------------------- 环境自检

def _quota_months(data):
    """把 220 的 data.Table（列式）转成按月额度列表。"""
    table = (data or {}).get("Table") or {}
    schema = table.get("schema") or []
    rows = table.get("data") or []
    months = []
    for row in rows:
        item = dict(zip(schema, row))
        months.append({
            "month": item.get("MONTHKEY", ""),
            "quota": item.get("MONQUOTA", 0),
            "used": item.get("USEDQUOTA", 0),
            "avail": item.get("AVAILQUOTA", 0),
        })
    return months


def verify(project=None):
    """
    环境自检：打 SYSINFOMATION/220（余额查询），报 项目 / URL / 用户 / 额度。

    失败细分（服务端对无效令牌返回 isSuccess=false，而不是 HTTP 401/403）：
      AUTH    — 令牌无效/过期（message 含「令牌无效」或 data 为英文 token 提示）
      BIZ     — 其他业务错误（如模型不存在）
      NETWORK — 连不上 base_url
      CONFIG  — 没有可用项目配置
    """
    project_key, proj_cfg, error = _resolve_project(project)
    if error:
        return error

    base_url = proj_cfg["base_url"].rstrip("/")
    payload = {
        "loginID": proj_cfg["auth_token"],
        "par": {
            "dm": {"dmCode": QUOTA_DM_CODE, "dmNum": QUOTA_DM_NUM, "Para": []},
            "scriptType": 0,
            "rowData": {},
            "tableData": [],
        },
    }

    resp = _post(base_url + ENDPOINT, payload, project_key)

    if "error" in resp:
        resp.setdefault("_project", project_key)
        return resp

    if resp.get("isSuccess") == "false":
        detail = resp.get("data")
        detail = detail if isinstance(detail, str) else ""
        message = resp.get("message") or "未知业务错误"
        # 令牌无效：中文 message「TotalLINK AI 令牌无效」+ 英文 data「TotalLINK AI token is invalid.」
        if "令牌" in message or "token" in detail.lower():
            return {
                "error": "AUTH",
                "message": f"令牌无效或已过期，请检查项目 '{project_key}' 的 auth_token",
                "detail": detail or message,
                "_project": project_key,
            }
        return {
            "error": "BIZ",
            "message": message,
            "detail": detail,
            "_project": project_key,
        }

    return {
        "status": "ok",
        "project": project_key,
        "base_url": base_url,
        "user": QUOTA_USR,
        "quota": {"months": _quota_months(resp.get("data"))},
        "_project": project_key,
    }


# ---------------------------------------------------------------- 工具发现

def search_tools(keyword, project=None, timeout=DEFAULT_TIMEOUT):
    """
    按关键字搜索可用工具（SEARCHLIST/100），输出结构与 parse_tools.py 一致。

    返回 list（工具列表）或 {"error": ...}（出错时原样透出错误）。
    """
    from parse_tools import parse_response

    resp = call(
        TOOL_SEARCH_DM_CODE,
        TOOL_SEARCH_DM_NUM,
        params=[keyword],
        script_type=0,
        project=project,
        timeout=timeout,
    )
    if "error" in resp:
        return resp
    return parse_response(resp)
