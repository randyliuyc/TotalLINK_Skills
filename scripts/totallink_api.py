#!/usr/bin/env python3
"""
TotalLINK API 调用封装：认证、Payload 构造、请求与错误处理。

所有调用统一走 /api/DataModel/linkDMAIAction，服务端根据 scriptType 自动区分查询/提交。
--row-data / --table-data 根据工具说明按需传入。

支持多项目环境，每个项目独立配置 auth_token 和 base_url。

用法：
  # 列出所有项目
  python3 scripts/totallink_api.py --list-projects

  # 切换活跃项目
  python3 scripts/totallink_api.py --set-active my-project

  # 指定项目调用（查询，script-type=0）
  python3 scripts/totallink_api.py --project my-project \\
    --dm-code LINKEXP01 --dm-num 9 --params "" "2026-06-01" "" --script-type 0

  # 使用活跃项目调用（提交，含 row_data）
  python3 scripts/totallink_api.py --dm-code LINKEXP01 --dm-num 10 \\
    --params "param1" --script-type 1 --row-data '{"field": "value"}'
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

CONFIG_PATH = os.path.expanduser("~/.totallink/config.json")

ENDPOINT = "/api/DataModel/linkDMAIAction"


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
    """设置活跃项目。"""
    cfg = load_all_config()
    if not cfg:
        print(json.dumps({"error": "CONFIG", "message": "配置文件不存在，请先创建项目配置"}, ensure_ascii=False))
        sys.exit(1)
    if project_name not in cfg.get("projects", {}):
        print(json.dumps({"error": "CONFIG", "message": f"项目 '{project_name}' 不存在"}, ensure_ascii=False))
        sys.exit(1)
    cfg["active"] = project_name
    save_config(cfg)
    return {"status": "ok", "active": project_name}


def add_project(project_name, auth_token, base_url="http://124.71.144.80:8088"):
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


def call(dm_code, dm_num, params=None,
         script_type=0, row_data=None, table_data=None, project=None):
    """
    调用 TotalLINK API，统一走 /api/DataModel/linkDMAIAction。

    参数:
        dm_code:     工具代码，如 "LINKEXP01"
        dm_num:      工具编号，如 9
        params:      Para 参数列表（字符串数组）
        script_type: 工具的 call_type 值（整数），服务端据此自动区分查询/提交
        row_data:    rowData 字典（按工具说明按需传入）
        table_data:  tableData 列表（按工具说明按需传入）
        project:     项目名，不传则使用活跃项目

    返回:
        dict: API 响应 JSON，出错时包含 "error" 字段
    """
    project_key, proj_cfg = get_project_config(project)
    if not proj_cfg:
        return {"error": "CONFIG", "message": f"配置文件不存在：{CONFIG_PATH}，请先运行首次认证配置"}

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

    req_body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=req_body,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            resp = json.loads(r.read().decode("utf-8"))
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

    resp["_project"] = project_key
    if resp.get("isSuccess") == "false":
        return {"error": "BIZ", "message": resp.get("message", "未知业务错误"), "_project": project_key}

    return resp


def main():
    parser = argparse.ArgumentParser(
        description="TotalLINK API 通用调用工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 列出项目
  %(prog)s --list-projects

  # 切换活跃项目
  %(prog)s --set-active my-project

  # 添加项目
  %(prog)s --add-project my-project --token "tlk_xxx" --url "http://host:8088"

  # 查询（script-type=0，无需 row-data / table-data）
  %(prog)s --dm-code LINKEXP01 --dm-num 9 --params "" "2026-06-01" "" --script-type 0

  # 行提交
  %(prog)s --project my-project --dm-code LINKEXP01 --dm-num 10 \\
      --params "EXP001" --script-type 1 --row-data '{"amount":"100"}'

  # 批量提交
  %(prog)s --dm-code LINKEXP02 --dm-num 15 \\
      --params "" --script-type 2 --row-data '{"key":"val"}' \\
      --table-data '[{"col1":"val1"}]'
        """,
    )

    # 项目管理
    parser.add_argument("--list-projects", action="store_true", help="列出所有项目")
    parser.add_argument("--set-active", metavar="PROJECT", help="设置活跃项目")
    parser.add_argument("--add-project", metavar="PROJECT", help="添加或更新项目配置（配合 --token 和 --url）")
    parser.add_argument("--token", metavar="TOKEN", help="auth_token（配合 --add-project）")
    parser.add_argument("--url", metavar="URL", help="base_url（配合 --add-project，默认 http://124.71.144.80:8088）")

    # API 调用参数
    parser.add_argument("--project", help="指定项目名（不传则使用活跃项目）")
    parser.add_argument("--dm-code", help="工具代码")
    parser.add_argument("--dm-num", type=int, help="工具编号")
    parser.add_argument(
        "--params", nargs="*", default=[],
        help="Para 参数列表，空位传 ''",
    )
    parser.add_argument(
        "--script-type", type=int,
        help="操作类型，取工具的 call_type 值，服务端自动区分查询/提交（整数 0-4）",
    )
    parser.add_argument(
        "--row-data", type=json.loads, default={},
        help="rowData JSON 字典（按工具说明按需传入）",
    )
    parser.add_argument(
        "--table-data", type=json.loads, default=[],
        help="tableData JSON 数组（按工具说明按需传入）",
    )

    args = parser.parse_args()

    # --- 管理命令 ---
    if args.list_projects:
        projects = list_projects()
        print(json.dumps(projects, ensure_ascii=False, indent=2))
        return

    if args.set_active:
        result = set_active_project(args.set_active)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.add_project:
        if args.token is None:
            print(json.dumps({"error": "PARAM", "message": "--add-project 需要配合 --token"}, ensure_ascii=False))
            sys.exit(1)
        result = add_project(
            project_name=args.add_project,
            auth_token=args.token,
            base_url=args.url or "http://124.71.144.80:8088",
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # --- API 调用 ---
    if args.script_type is None:
        print(json.dumps({"error": "PARAM", "message": "API 调用必须提供 --script-type"}, ensure_ascii=False))
        sys.exit(1)

    result = call(
        dm_code=args.dm_code,
        dm_num=args.dm_num,
        params=args.params,
        script_type=args.script_type,
        row_data=args.row_data,
        table_data=args.table_data,
        project=args.project,
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))

    if "error" in result:
        sys.exit(1)


if __name__ == "__main__":
    main()
