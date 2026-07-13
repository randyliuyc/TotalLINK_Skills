#!/usr/bin/env python3
"""
TotalLINK API 调用封装：认证、Payload 构造、请求与错误处理。

支持三种调用类型：
  AIResult     — 数据查询 → /api/DataModel/linkDMAIResult
  AIRowSubmit  — 行数据提交 → /api/DataModel/linkDMAIRowSubmit
  AIDataSubmit — 批量数据提交 → /api/DataModel/linkDMAIDataSubmit

用法：
  python3 scripts/totallink_api.py --type AIResult --dm-code LINKEXP01 --dm-num 9 \\
    --params "" "2026-06-01" "2026-07-11" ""

  python3 scripts/totallink_api.py --type AIRowSubmit --dm-code LINKEXP01 --dm-num 10 \\
    --params "param1" --script-type 1 --row-data '{"field": "value"}'

  python3 scripts/totallink_api.py --type AIDataSubmit --dm-code LINKEXP01 --dm-num 10 \\
    --params "param1" --script-type 1 --row-data '{"f1":"v1"}' --table-data '[{"f1":"v1"}]'
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

CONFIG_PATH = os.path.expanduser("~/.totallink/config.json")

ENDPOINTS = {
    "AIResult": "/api/DataModel/linkDMAIResult",
    "AIRowSubmit": "/api/DataModel/linkDMAIRowSubmit",
    "AIDataSubmit": "/api/DataModel/linkDMAIDataSubmit",
}


def load_config():
    """从 ~/.totallink/config.json 读取认证信息。"""
    if not os.path.exists(CONFIG_PATH):
        print(
            json.dumps(
                {
                    "error": "CONFIG",
                    "message": f"配置文件不存在：{CONFIG_PATH}，请先运行首次认证配置",
                },
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        sys.exit(1)
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def call(call_type, dm_code, dm_num, params=None,
         script_type=None, row_data=None, table_data=None):
    """
    调用 TotalLINK API。

    参数:
        call_type:  "AIResult" | "AIRowSubmit" | "AIDataSubmit"
        dm_code:    工具代码，如 "LINKEXP01"
        dm_num:     工具编号，如 9
        params:     Para 参数列表（字符串数组），如 ["", "2026-06-01", "", ""]
        script_type: 操作类型（仅 AIRowSubmit / AIDataSubmit）
        row_data:   rowData 字典（仅 AIRowSubmit / AIDataSubmit）
        table_data: tableData 列表（仅 AIDataSubmit）

    返回:
        dict: API 响应 JSON，出错时包含 "error" 字段
    """
    cfg = load_config()
    base_url = cfg["base_url"].rstrip("/")
    endpoint = ENDPOINTS.get(call_type)
    if not endpoint:
        return {"error": "PARAM", "message": f"未知调用类型：{call_type}"}

    url = base_url + endpoint
    dm_block = {"dmCode": dm_code, "dmNum": dm_num, "Para": params or []}

    if call_type == "AIResult":
        par = dm_block
    else:
        par = {
            "dm": dm_block,
            "scriptType": script_type,
            "rowData": row_data or {},
        }
        if call_type == "AIDataSubmit":
            par["tableData"] = table_data or []

    payload = {"loginID": cfg["auth_token"], "par": par}

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
                "message": "令牌无效或已过期，请检查 ~/.totallink/config.json 中的 auth_token",
            }
        return {"error": "HTTP", "code": e.code, "reason": e.reason}
    except urllib.error.URLError as e:
        return {
            "error": "NETWORK",
            "message": f"无法连接 TotalLINK 服务，请检查 base_url：{str(e.reason)}",
        }
    except Exception as e:
        return {"error": "UNKNOWN", "message": str(e)}

    if resp.get("isSuccess") == "false":
        return {"error": "BIZ", "message": resp.get("message", "未知业务错误")}

    return resp


def main():
    parser = argparse.ArgumentParser(
        description="TotalLINK API 通用调用工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --type AIResult --dm-code LINKEXP01 --dm-num 9 --params "" "2026-06-01" ""
  %(prog)s --type AIRowSubmit --dm-code LINKEXP01 --dm-num 10 \\
      --params "EXP001" --script-type 1 --row-data '{"amount":"100"}'
        """,
    )
    parser.add_argument(
        "--type", dest="call_type", required=True,
        choices=list(ENDPOINTS.keys()),
        help="调用类型",
    )
    parser.add_argument("--dm-code", required=True, help="工具代码")
    parser.add_argument("--dm-num", type=int, required=True, help="工具编号")
    parser.add_argument(
        "--params", nargs="*", default=[],
        help="Para 参数列表，空位传 ''",
    )
    parser.add_argument(
        "--script-type", type=int,
        help="操作类型（AIRowSubmit / AIDataSubmit 必传）",
    )
    parser.add_argument(
        "--row-data", type=json.loads, default={},
        help="rowData JSON 字典（AIRowSubmit / AIDataSubmit）",
    )
    parser.add_argument(
        "--table-data", type=json.loads, default=[],
        help="tableData JSON 数组（仅 AIDataSubmit）",
    )

    args = parser.parse_args()

    result = call(
        call_type=args.call_type,
        dm_code=args.dm_code,
        dm_num=args.dm_num,
        params=args.params,
        script_type=args.script_type,
        row_data=args.row_data,
        table_data=args.table_data,
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))

    if "error" in result:
        sys.exit(1)


if __name__ == "__main__":
    main()
