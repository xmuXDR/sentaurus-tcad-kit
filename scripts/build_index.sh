#!/bin/bash
# build_index.sh — 把服务器上的官方 PDF 手册转成可检索的纯文本
# 在装有 Sentaurus 的服务器上运行。只需跑一次；以后新增/更新手册时可重跑（已转换的会跳过）。
set -u
PDFDIR=/home/synopsys/sentaurus/X-2025.06/tcad/X-2025.06/manuals/olh_sentaurus/pdf
OUT=~/manual_index/text
mkdir -p "$OUT"
for pdf in "$PDFDIR"/*.pdf; do
  base=$(basename "$pdf" .pdf)
  if [ -f "$OUT/$base.txt" ]; then
    echo "skip $base (already converted)"
    continue
  fi
  nice -n 10 pdftotext -layout "$pdf" "$OUT/$base.txt"
  echo "converted $base"
done
echo "BUILD_DONE total=$(ls "$OUT" | wc -l) files, $(du -sh "$OUT" | cut -f1)"
