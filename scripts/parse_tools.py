#!/usr/bin/env python3
"""
解析 TotalLINK SEARCHLIST 返回的 Table 数据，转换为结构化工具列表。

输入（stdin）：linkDMAIAction 的 JSON 响应
输出（stdout）：[{ code, num, name, desc, script_type }, ...]
script_type 字段为工具的 script_type 值，直接作为 --script-type 参数传入。

parse_response() 供 scripts/tlk.py 的 `tools search` 复用（不经过 stdin 管道）。

用法：
  python3 scripts/tlk.py tools search "报销"
"""

import sys
import json


def parse_response(raw):
    """把 linkDMAIAction 的响应 dict 解析为工具列表（无结果时返回空列表）。"""
    table = raw.get("data", {}).get("Table")
    if not table:
        return []

    schema = table.get("schema", [])
    rows = table.get("data", [])

    items = []
    for row in rows:
        item = dict(zip(schema, row))
        items.append({
            "code": item.get("TOOL_CODE", ""),
            "num": item.get("TOOL_NUM", ""),
            "name": item.get("TOOL_NAME", ""),
            "desc": item.get("TOOL_DESC", ""),
            "script_type": item.get("TOOL_TYPE", "0"),
        })

    return items


def main():
    raw = json.load(sys.stdin)

    if "error" in raw:
        print(json.dumps(raw, ensure_ascii=False, indent=2))
        sys.exit(1)

    print(json.dumps(parse_response(raw), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
