#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""search.py — 在官方手册纯文本里做全文检索（服务器上运行）

用法：
  python3 search.py "eAvalanche"                 # 在所有手册里搜
  python3 search.py "Quasistationary" -t sdevice # 只搜 SDevice 手册
  python3 search.py "AddParam" -t swb -n 10      # 最多 10 条
  python3 search.py -r "HeavyIon.*Time" -c 2     # 正则 + 前后 2 行上下文
  python3 search.py "MGOALS" --training          # 同时搜 Sentaurus_Training HTML

说明：
- 结果带 PDF 页码（pdftotext 用换页符分页，页码=换页符计数+1）。
- 手册文本目录默认 ~/manual_index/text，可用 MANUAL_TEXT_DIR 覆盖。
"""

import argparse
import os
import re
import sys

TEXT_DIR = os.environ.get("MANUAL_TEXT_DIR", os.path.expanduser("~/manual_index/text"))
TRAINING_DIR = "/home/synopsys/sentaurus/X-2025.06/tcad/X-2025.06/Sentaurus_Training"
MAX_LINE = 300


def iter_matches(path, pattern):
    """yield (page, lineno, line) for lines matching pattern."""
    page = 1
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for lineno, line in enumerate(f, 1):
                page += line.count("\f")
                if pattern.search(line):
                    yield page, lineno, line.strip()
    except OSError as exc:
        print(f"!! cannot read {path}: {exc}", file=sys.stderr)


def search_texts(args, pattern):
    hits = 0
    for name in sorted(os.listdir(TEXT_DIR)):
        if not name.endswith(".txt"):
            continue
        if args.tool and args.tool.lower() not in name.lower():
            continue
        shown_file = False
        for page, lineno, line in iter_matches(os.path.join(TEXT_DIR, name), pattern):
            if not shown_file:
                print(f"\n== {name} ==")
                shown_file = True
            print(f"  p.{page} L{lineno}: {line[:MAX_LINE]}")
            hits += 1
            if hits >= args.max_total:
                print("\n...(达到 --max-total 上限，请加限定词或 -t 缩小范围)")
                return hits
    return hits


TAG_RE = re.compile(r"<[^>]+>")


def search_training(args, pattern):
    hits = 0
    for dirpath, _dirs, files in os.walk(TRAINING_DIR):
        for fn in sorted(files):
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    text = TAG_RE.sub(" ", f.read())
            except OSError:
                continue
            for lineno, line in enumerate(text.splitlines(), 1):
                if pattern.search(line):
                    rel = os.path.relpath(path, TRAINING_DIR)
                    print(f"  [training] {rel} L{lineno}: {line.strip()[:MAX_LINE]}")
                    hits += 1
                    if hits >= args.max_total:
                        return hits
    return hits


def main():
    ap = argparse.ArgumentParser(description="Search Sentaurus official manuals (local text index)")
    ap.add_argument("query", help="search text (case-insensitive) or regex with -r")
    ap.add_argument("-t", "--tool", help="only files containing this in name, e.g. sdevice, swb")
    ap.add_argument("-n", "--max-total", type=int, default=30, help="max hits total (default 30)")
    ap.add_argument("-r", "--regex", action="store_true", help="treat query as regex")
    ap.add_argument("--training", action="store_true", help="also search Sentaurus_Training HTML")
    ap.add_argument("-c", "--context", type=int, default=0, help="unused, reserved")
    args = ap.parse_args()

    flags = 0 if args.regex else re.IGNORECASE
    pattern = re.compile(args.query, flags)

    if not os.path.isdir(TEXT_DIR):
        sys.exit(f"text index not found: {TEXT_DIR}\n先在服务器上运行 build_index.sh")
    hits = search_texts(args, pattern)
    if args.training:
        hits += search_training(args, pattern)
    print(f"\n共 {hits} 条命中。文本库: {TEXT_DIR}")
    if hits == 0:
        print("建议: 换关键词、拆词、或用 -t 指定手册后再试。")


if __name__ == "__main__":
    main()
