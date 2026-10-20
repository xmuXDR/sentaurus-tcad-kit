#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""plt_parse.py — 解析 Sentaurus .plt（DF-ISE xyplot 文本格式）

比 pytaurus 更稳的写法：
- 列名优先取 Info 块 datasets 列表（不靠 "Data {"+固定空格的脆弱切分）
- 支持一个文件里多个 Data { } 块（NewCurrentFile/CurrentPlot 分段）
- 纯标准库，服务器 python3 直接跑，无需 pandas

用法：
  plt_parse.py file.plt --keys            # 列出列名
  plt_parse.py file.plt --csv out.csv     # 导出（多块时写 out_b0.csv, out_b1.csv ...）
  plt_parse.py file.plt --head 5          # 打印前 5 行预览
  plt_parse.py file.plt --dataset 1       # 只处理第 2 个 Data 块
作为库：
  from plt_parse import load_plt
  datasets = load_plt("n63_des.plt")      # [{names, rows, ncols, nrows}, ...]
"""

import argparse
import csv
import re
import sys

QUOTE_RE = re.compile(r'"([^"]+)"')
FLOAT_RE = re.compile(r"^[+-]?(?:\d+\.?\d*|\.\d+)(?:[Ee][+-]?\d+)?$|^[+-]?(?:NaN|Inf(?:inity)?)$")
DATA_BLOCK_RE = re.compile(r"Data\s*\{(.*?)\}", re.DOTALL)


def _parse_names(text):
    """取 Info 块 datasets 列表里的列名；找不到就取全文前若干个引号名。"""
    m = re.search(r"datasets\s*=\s*\[(.*?)\]", text, re.DOTALL)
    if m:
        return QUOTE_RE.findall(m.group(1))
    return QUOTE_RE.findall(text)


TOKEN_RE = re.compile(
    r'"[^"]+"|[+-]?(?:\d+\.?\d*|\.\d+)(?:[Ee][+-]?\d+)?|[+-]?(?:NaN|Inf(?:inity)?)')


def _parse_block(body):
    """解析一个 Data 块：数字之前出现的引号名是该块的列名（可选），其后全是数值。

    用 finditer 按"引号串或数字"扫描，避免带空格的列名被 split 拆碎。
    """
    names, values, seen_number = [], [], False
    for m in TOKEN_RE.finditer(body):
        tok = m.group(0)
        if tok.startswith('"'):
            if not seen_number:
                names.append(tok[1:-1])
        else:
            seen_number = True
            values.append(float(tok))
    return names, values


def load_plt(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()
    default_names = _parse_names(text)
    datasets = []
    for idx, block in enumerate(DATA_BLOCK_RE.findall(text)):
        names, values = _parse_block(block)
        if not names:
            names = default_names
        n = len(names)
        if n == 0 or len(values) % n != 0:
            raise ValueError(
                f"Data block {idx}: {len(values)} values cannot fill {n} columns"
                f"（块内有自带列名 {len(names)} 个，Info 列名 {len(default_names)} 个，"
                f"可能该块只含部分函数，请用 --dataset 单独看或检查文件）")
        rows = len(values) // n
        columns = {name: values[i * rows:(i + 1) * rows] for i, name in enumerate(names)}
        datasets.append({"names": names, "columns": columns, "ncols": n, "nrows": rows})
    if not datasets:
        raise ValueError("no 'Data { ... }' block found; not an xyplot PLT?")
    return datasets


def main():
    ap = argparse.ArgumentParser(description="Parse Sentaurus PLT (DF-ISE xyplot)")
    ap.add_argument("plt")
    ap.add_argument("--keys", action="store_true", help="list column names")
    ap.add_argument("--csv", metavar="OUT", help="export to CSV (multi-block: _b0, _b1 ...)")
    ap.add_argument("--head", type=int, metavar="N", help="print first N rows")
    ap.add_argument("--dataset", type=int, metavar="I", help="only process Data block I")
    args = ap.parse_args()

    try:
        datasets = load_plt(args.plt)
    except (OSError, ValueError) as exc:
        sys.exit(f"error: {exc}")

    if args.dataset is not None:
        if not 0 <= args.dataset < len(datasets):
            sys.exit(f"error: dataset index out of range (0..{len(datasets) - 1})")
        datasets = [datasets[args.dataset]]

    for i, ds in enumerate(datasets):
        tag = "" if len(datasets) == 1 else f"[block {i}] "
        print(f"{tag}{ds['nrows']} rows x {ds['ncols']} cols")
        if args.keys:
            for name in ds["names"]:
                print(f"  {name}")
        if args.head:
            names = ds["names"]
            print("\t".join(names))
            for r in range(min(args.head, ds["nrows"])):
                print("\t".join(f"{ds['columns'][n][r]:.6e}" for n in names))
        if args.csv:
            out = args.csv
            if len(datasets) > 1 or args.dataset is None and len(datasets) > 1:
                stem, dot, ext = out.rpartition(".")
                out = f"{stem}_b{i}.{ext}" if dot else f"{out}_b{i}"
            names = ds["names"]
            with open(out, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f, delimiter="\t")
                w.writerow(names)
                for r in range(ds["nrows"]):
                    w.writerow([ds["columns"][n][r] for n in names])
            print(f"  -> {out}")


if __name__ == "__main__":
    main()
