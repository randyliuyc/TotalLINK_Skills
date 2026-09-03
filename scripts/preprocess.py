#!/usr/bin/env python3
"""TotalLINK 通用数据预处理 — 业务无关的大数据量自动摘要工具。

用法:
  totallink_api.py ... | preprocess.py --smart      # 自动检测大小
  preprocess.py data.json --describe               # 列描述
  preprocess.py data.json --group <列名>            # 按列分组计数
  preprocess.py data.json --filter <列名>=<值>      # 过滤
  preprocess.py data.json --stats                  # 数值列统计
  preprocess.py data.json --head 5                 # 前N行预览
"""

import json
import sys
import os
from collections import Counter

SMALL_THRESHOLD = 50 * 1024      # 50KB: 透传
MEDIUM_THRESHOLD = 500 * 1024    # 500KB: 自动摘要
MAX_PREVIEW = 5


def load_data(source):
    """加载 JSON：支持文件路径或 stdin。"""
    if isinstance(source, str) and os.path.isfile(source):
        with open(source) as f:
            return json.load(f)
    return json.loads(source)


def extract_rows(data):
    """从 TotalLINK 响应中提取 rows + schema + captions。"""
    table = data.get("data", {}).get("Table", {})
    return table.get("data", []), table.get("schema", []), table.get("captions", {})


def describe(rows, schema, captions):
    """列描述：非空率、去重数、样例值。"""
    n = len(rows)
    if n == 0:
        print("数据为空")
        return

    cols = [captions.get(c, c) for c in schema]
    print(f"总行数: {n} | 列数: {len(schema)}")
    print(f"{'列名':<20} {'非空率':>6} {'去重值':>6}  示例")
    print("-" * 60)

    for i, col in enumerate(cols):
        vals = [r[i] for r in rows if i < len(r) and r[i] is not None]
        fill = len(vals) / n
        uniq = len(set(str(v) for v in vals))
        sample = ", ".join(str(v) for v in vals[:3])
        print(f"{col:<20} {fill:>5.1%} {uniq:>6d}  {sample}")


def group_by(rows, schema, captions, column):
    """按指定列分组计数。"""
    idx = _resolve_index(schema, captions, column)
    if idx is None:
        return

    counter = Counter()
    for r in rows:
        key = str(r[idx]) if idx < len(r) and r[idx] is not None else "(空)"
        counter[key] += 1

    name = captions.get(column, column)
    print(f"按 [{name}] 分组:")
    for k, v in counter.most_common():
        print(f"  {k}: {v}")


def _to_number(v):
    """把 API 返回的金额字符串（如 '300.00'、'1,250.5'）转成 float；不可转换返回 None。"""
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if not isinstance(v, str):
        return None
    s = v.strip().replace(",", "")
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def filter_rows(rows, schema, captions, expr):
    """过滤: 列名=值。始终返回 list（列不存在时返回原 rows，绝不返回 None）。"""
    if "=" not in expr:
        print(f"过滤表达式格式错误，应为 列名=值，实际: {expr}")
        return rows

    col, val = expr.split("=", 1)
    idx = _resolve_index(schema, captions, col)
    if idx is None:
        return rows

    return [r for r in rows if idx < len(r) and str(r[idx]) == val]


def stats(rows, schema, captions):
    """数值列 min/avg/max/sum。兼容 API 返回的字符串金额（如 '300.00'）。"""
    numeric_cols = []
    for i, c in enumerate(schema):
        vals = [n for r in rows if i < len(r) for n in [_to_number(r[i])] if n is not None]
        if vals:
            numeric_cols.append((captions.get(c, c), i, vals))

    if not numeric_cols:
        print("无数值列")
        return

    for name, i, vals in numeric_cols:
        print(
            f"{name}: min={min(vals):.2f}, avg={sum(vals)/len(vals):.2f}, "
            f"max={max(vals):.2f}, sum={sum(vals):.2f}, count={len(vals)}"
        )


def head(rows, schema, captions, n=5):
    """前 N 行预览。"""
    cols = [captions.get(c, c) for c in schema]
    print("\t".join(cols))
    for r in rows[:n]:
        print("\t".join(str(v) for v in r))


def _find_col(captions, name):
    """通过 captions 名称找 schema 列名。"""
    for k, v in captions.items():
        if v == name or k == name:
            return k
    raise KeyError(name)


def _resolve_index(schema, captions, column):
    """解析列名为 schema 索引。支持 schema 名或 captions 名。"""
    if column in schema:
        return schema.index(column)
    for i, c in enumerate(schema):
        if captions.get(c) == column:
            return i
    print(f"列 '{column}' 不存在，可用列: {[captions.get(c, c) for c in schema]}")
    return None


def smart_entry(raw, source_file=None):
    """自动检测大小，决定透传或摘要。"""
    data = load_data(raw)
    rows, schema, captions = extract_rows(data)

    # 无表格数据 → 透传
    if not schema:
        print(raw if isinstance(raw, str) else json.dumps(data, ensure_ascii=False, indent=2))
        return

    size = len(raw) if isinstance(raw, str) else 0

    if size < SMALL_THRESHOLD:
        # 透传原始 JSON
        print(raw if isinstance(raw, str) else json.dumps(data, ensure_ascii=False, indent=2))
    elif size < MEDIUM_THRESHOLD:
        describe(rows, schema, captions)
    else:
        describe(rows, schema, captions)
        print(f"\n💡 数据量 {size/1024:.0f}KB，可使用:")
        print("    preprocess.py data.json --group <列名>  # 分组统计")
        print("    preprocess.py data.json --filter <列名>=<值> # 过滤")
        print("    preprocess.py data.json --stats  # 数值统计")


def main():
    import argparse
    p = argparse.ArgumentParser(description="TotalLINK 通用数据预处理")
    p.add_argument("input", nargs="?", help="JSON 文件路径（默认 stdin）")
    p.add_argument("--smart", action="store_true", help="自动检测大小，小数据透传、大数据摘要")
    p.add_argument("--describe", action="store_true", help="列描述")
    p.add_argument("--group", help="按指定列分组计数")
    p.add_argument("--filter", dest="filter_expr", help="过滤: 列名=值")
    p.add_argument("--stats", action="store_true", help="数值列统计")
    p.add_argument("--head", type=int, nargs="?", const=5, help="预览前N行")
    args = p.parse_args()

    # 读取输入
    if args.input:
        with open(args.input) as f:
            raw = f.read()
    else:
        raw = sys.stdin.read()

    data = load_data(raw)
    rows, schema, captions = extract_rows(data)

    if args.smart:
        smart_entry(raw)
        return

    if args.describe:
        describe(rows, schema, captions)
    if args.group:
        group_by(rows, schema, captions, args.group)
    if args.filter_expr:
        rows = filter_rows(rows, schema, captions, args.filter_expr)
        print(f"过滤后 {len(rows)} 行")
        head(rows, schema, captions, 10)
    if args.stats:
        stats(rows, schema, captions)
    if args.head is not None:
        head(rows, schema, captions, args.head)

    if not any([args.describe, args.group, args.filter_expr, args.stats, args.head is not None]):
        print(raw)


if __name__ == "__main__":
    main()
