#!/usr/bin/env python3
"""TotalLINK 报销单审计 — 跨单发票查重

用法:
    python3 dedup_check.py invoices_index.json [more_index.json ...]

输入: 一个或多个 invoices_index.json（格式见 reimbursement-audit SKILL.md Step 4.5）。
      传入多个月份的索引即可实现跨月查重。
输出: stdout 打印重复发票分组（JSON），供写入审计报告「重复发票专项」小节。
退出码: 0=无重复, 2=发现重复, 1=参数/格式错误。
"""
import json
import sys
from collections import defaultdict


def load(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    period = data.get("period", "?")
    invoices = data.get("invoices")
    if not isinstance(invoices, list):
        raise ValueError(f"{path}: 缺少 invoices 数组")
    return period, invoices


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    records = []
    for path in sys.argv[1:]:
        try:
            period, invoices = load(path)
        except FileNotFoundError:
            print(f"错误: 文件不存在: {path}", file=sys.stderr)
            return 1
        except json.JSONDecodeError as e:
            print(f"错误: {path} 不是有效 JSON: {e}", file=sys.stderr)
            return 1
        except AttributeError:
            print(
                f"错误: {path} 顶层应为 {{\"period\": …, \"invoices\": […]}} 对象，读到的是数组或其他类型",
                file=sys.stderr,
            )
            return 1
        except ValueError as e:
            print(f"错误: {e}", file=sys.stderr)
            return 1
        for inv in invoices:
            no = str(inv.get("invoice_no", "")).strip()
            if not no or no == "非发票":
                continue  # 非发票附件不参与查重
            records.append({
                "period": period,
                "doc": inv.get("doc", "?"),
                "invoice_no": no,
                "issue_date": inv.get("issue_date", ""),
                "total": inv.get("total"),
                "source": inv.get("source", ""),
            })

    groups = defaultdict(list)
    for r in records:
        groups[r["invoice_no"]].append(r)

    duplicates = []
    for no, items in sorted(groups.items()):
        docs = {i["doc"] for i in items}
        # 同一发票号出现在不同单据 → 跨单重复；同单内重复也一并报告
        if len(items) > 1:
            amounts = {i["total"] for i in items if i["total"] is not None}
            duplicates.append({
                "invoice_no": no,
                "occurrences": items,
                "docs": sorted(docs),
                "count": len(items),
                "amounts": sorted(amounts),
                "amount_conflict": len(amounts) > 1,
                "cross_period": len({i["period"] for i in items}) > 1,
            })

    result = {
        "scanned_invoices": len(records),
        "duplicate_groups": len(duplicates),
        "duplicates": duplicates,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if duplicates else 0


if __name__ == "__main__":
    sys.exit(main())
