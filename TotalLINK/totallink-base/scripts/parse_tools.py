#!/usr/bin/env python3
"""
解析 TotalLINK SEARCHLIST 返回的 Table 数据，转换为结构化工具列表。

输入（stdin）：totallink_api.py 的 JSON 输出
输出（stdout）：[{ code, num, name, desc, type }, ...]
type 字段包含四种：AIResult / AIRowSubmit / AIDataSubmit / AIAction

用法：
  python3 scripts/totallink_api.py --type AIResult --dm-code SEARCHLIST --dm-num 100 --params "报销" \\
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
            "type": item.get("TOOL_TYPE", ""),
        })

    print(json.dumps(items, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
