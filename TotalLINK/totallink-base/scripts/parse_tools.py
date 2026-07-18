#!/usr/bin/env python3
"""
解析 TotalLINK SEARCHLIST 返回的 Table 数据，转换为结构化工具列表。

输入（stdin）：totallink_api.py 的 JSON 输出
输出（stdout）：[{ code, num, name, desc, script_type }, ...]
script_type 字段为工具的 call_type 值，直接作为 --script-type 参数传入。

用法：
  python3 scripts/totallink_api.py --dm-code SEARCHLIST --dm-num 100 --params "报销" --script-type 0 \\
    | python3 scripts/parse_tools.py
"""

import sys
import json


def main():
    raw = json.load(sys.stdin)

    if "error" in raw:
        print(json.dumps(raw, ensure_ascii=False, indent=2))
        sys.exit(1)

    table = raw.get("data", {}).get("Table")
    if not table:
        print(json.dumps([], ensure_ascii=False, indent=2))
        return

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

    print(json.dumps(items, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
