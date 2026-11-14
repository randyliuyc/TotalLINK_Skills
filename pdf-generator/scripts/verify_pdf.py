#!/usr/bin/env python3
"""verify_pdf.py — 校验 Chrome headless 生成的 PDF：页数、内容完整性。

为什么需要这个脚本：
Chrome 嵌入字体的 ToUnicode 表会把「一/风/车」等汉字映射到康熙部首码位
（U+2E80~U+2FDF），pdfplumber 提取文本时会得到「⼀/⻛」。直接比对关键词会把
正常文档误判为内容缺失。本脚本在比对前先做 NFKC 归一化。视觉渲染不受影响，
不要因此调整排版。

用法:
  python3 verify_pdf.py 报告.pdf
  python3 verify_pdf.py 报告.pdf --expect "执行摘要" "结论" --max-pages 20
"""

import argparse
import logging
import sys
import unicodedata
from pathlib import Path

# pdfminer 对部分嵌入字体会刷 "Could not get FontBBox from font descriptor" 警告，
# 属于解析库的已知噪音，与内容校验无关，抑制之。
logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("pdfplumber").setLevel(logging.ERROR)


def normalize(text: str) -> str:
    return unicodedata.normalize("NFKC", text)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pdf", type=Path, help="待校验的 PDF 文件")
    parser.add_argument("--expect", nargs="*", default=[],
                        help="期望出现的关键词（NFKC 归一化后比对）")
    parser.add_argument("--max-pages", type=int, default=None,
                        help="页数上限，超出视为异常")
    parser.add_argument("--min-chars", type=int, default=0,
                        help="提取字符数下限，低于视为渲染异常")
    args = parser.parse_args()

    try:
        import pdfplumber
    except ImportError:
        print("错误: 需要 pdfplumber。请在 $TOTALLINK_PYTHON 下运行本脚本。", file=sys.stderr)
        return 2

    if not args.pdf.is_file():
        print(f"错误: 文件不存在: {args.pdf}", file=sys.stderr)
        return 1

    with pdfplumber.open(args.pdf) as pdf:
        page_count = len(pdf.pages)
        raw_text = "\n".join((page.extract_text() or "") for page in pdf.pages)

    normalized = normalize(raw_text)
    print(f"文件: {args.pdf}")
    print(f"页数: {page_count}")
    print(f"提取字符数: {len(raw_text)}")

    problems = []

    if args.max_pages is not None and page_count > args.max_pages:
        problems.append(f"页数 {page_count} 超过上限 {args.max_pages}")

    if args.min_chars and len(raw_text) < args.min_chars:
        problems.append(f"提取字符数 {len(raw_text)} 低于下限 {args.min_chars}，可能渲染异常")

    if args.expect:
        missing = [word for word in args.expect if normalize(word) not in normalized]
        if missing:
            problems.append(f"缺失关键词: {missing}")
        else:
            print(f"关键词命中: {len(args.expect)}/{len(args.expect)}")

    if problems:
        for item in problems:
            print(f"需人工确认: {item}")
        return 1

    print("结果: 通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
