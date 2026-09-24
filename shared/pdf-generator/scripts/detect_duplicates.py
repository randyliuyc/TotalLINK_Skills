#!/usr/bin/env python3
"""Detect exact and lexical-near duplicate Markdown paragraphs.

This script is read-only. It never edits the input file. It emits JSON so the
calling workflow can preserve all content while presenting review candidates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Iterable

HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*$")
FENCE_RE = re.compile(r"^\s*(```+|~~~+)\s*")
TOKEN_RE = re.compile(r"[\u4e00-\u9fff]|[A-Za-z0-9_]+")
SPACE_RE = re.compile(r"\s+")


def normalize(text: str) -> str:
    text = re.sub(r"[`*_~]", "", text)
    text = SPACE_RE.sub(" ", text.strip())
    return text.casefold()


def tokens(text: str) -> set[str]:
    return set(TOKEN_RE.findall(normalize(text)))


def jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def paragraphs(lines: Iterable[str]) -> list[dict]:
    result: list[dict] = []
    buffer: list[str] = []
    start_line = 1
    heading_context = ""
    in_fence = False

    def flush(end_line: int) -> None:
        nonlocal buffer, start_line
        text = " ".join(part.strip() for part in buffer).strip()
        if text and len(normalize(text)) >= 20:
            result.append({
                "index": len(result) + 1,
                "start_line": start_line,
                "end_line": end_line,
                "heading_context": heading_context,
                "text": text,
                "normalized": normalize(text),
                "tokens": tokens(text),
            })
        buffer = []

    for line_no, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")
        if FENCE_RE.match(line):
            if buffer:
                flush(line_no - 1)
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        heading = HEADING_RE.match(line)
        if heading:
            if buffer:
                flush(line_no - 1)
            heading_context = heading.group(1).strip()
            continue
        if not line.strip():
            if buffer:
                flush(line_no - 1)
            continue
        if re.match(r"^\s*(?:[-*+] |\d+[.)] |>|\|)", line):
            if buffer:
                flush(line_no - 1)
            text = line.strip()
            if len(normalize(text)) >= 20:
                result.append({
                    "index": len(result) + 1,
                    "start_line": line_no,
                    "end_line": line_no,
                    "heading_context": heading_context,
                    "text": text,
                    "normalized": normalize(text),
                    "tokens": tokens(text),
                })
            continue
        if not buffer:
            start_line = line_no
        buffer.append(line)
    if buffer:
        flush(start_line + len(buffer) - 1)
    return result


def compact(item: dict) -> dict:
    return {key: item[key] for key in ("index", "start_line", "end_line", "heading_context", "text")}


def detect(items: list[dict], near_threshold: float) -> dict:
    exact_groups: dict[str, list[dict]] = {}
    for item in items:
        digest = hashlib.sha256(item["normalized"].encode("utf-8")).hexdigest()
        exact_groups.setdefault(digest, []).append(item)

    exact = [
        {"normalized_hash": digest, "occurrences": [compact(item) for item in group]}
        for digest, group in exact_groups.items()
        if len(group) > 1
    ]

    near: list[dict] = []
    for offset, left in enumerate(items):
        for right in items[offset + 1 :]:
            if left["normalized"] == right["normalized"]:
                continue
            if min(len(left["normalized"]), len(right["normalized"])) < 40:
                continue
            similarity = jaccard(left["tokens"], right["tokens"])
            length_ratio = min(len(left["normalized"]), len(right["normalized"])) / max(
                len(left["normalized"]), len(right["normalized"])
            )
            if similarity >= near_threshold and length_ratio >= 0.65:
                near.append({
                    "similarity": round(similarity, 3),
                    "occurrences": [compact(left), compact(right)],
                })

    return {
        "algorithm": "normalized-paragraph-exact-and-token-jaccard",
        "near_duplicate_threshold": near_threshold,
        "paragraph_count": len(items),
        "exact_duplicates": exact,
        "near_duplicates": near,
        "disclaimer": "近似重复为词汇相似度启发式结果，必须人工确认，不等同于语义判定。",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("markdown", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--near-threshold", type=float, default=0.72)
    args = parser.parse_args()

    source = args.markdown.read_text(encoding="utf-8")
    report = detect(paragraphs(source.splitlines()), args.near_threshold)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
