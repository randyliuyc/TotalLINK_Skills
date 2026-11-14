#!/usr/bin/env bash
#
# render_pdf.sh — 将自包含 HTML 渲染为 A4 PDF（Chrome headless）
#
# 用法:
#   ./render_pdf.sh <input.html> <output.pdf> [--with-header-footer]
#
# 说明:
#   - 默认加 --no-pdf-header-footer，输出干净版面（无 Chrome 自带页眉页脚）
#   - 加 --with-header-footer 可获得页码，但页眉会包含 file:// URL 与日期
#   - Chrome 不支持 @page 页码计数器，这是固有限制
#
# 环境变量:
#   CHROME_BIN            指定 Chrome/Chromium 可执行文件路径
#   CHROME_USER_DATA_DIR  指定用户数据目录（与运行中的 Chrome 冲突时使用）
#
set -euo pipefail

if [ $# -lt 2 ]; then
  echo "用法: $0 <input.html> <output.pdf> [--with-header-footer]" >&2
  exit 2
fi

HTML="$1"
PDF="$2"
shift 2

HEADER_FOOTER=0
for arg in "$@"; do
  case "$arg" in
    --with-header-footer) HEADER_FOOTER=1 ;;
    *) echo "错误: 未知参数 '$arg'" >&2; exit 2 ;;
  esac
done

if [ ! -f "$HTML" ]; then
  echo "错误: 输入 HTML 不存在: $HTML" >&2
  exit 1
fi

# Chrome 要求绝对路径
HTML_DIR="$(cd "$(dirname "$HTML")" && pwd)"
HTML_ABS="$HTML_DIR/$(basename "$HTML")"
PDF_DIR="$(cd "$(dirname "$PDF")" 2>/dev/null && pwd || { mkdir -p "$(dirname "$PDF")"; cd "$(dirname "$PDF")" && pwd; })"
PDF_ABS="$PDF_DIR/$(basename "$PDF")"

find_chrome() {
  if [ -n "${CHROME_BIN:-}" ]; then
    if [ -x "$CHROME_BIN" ]; then echo "$CHROME_BIN"; return 0; fi
    echo "错误: CHROME_BIN 指向的文件不可执行: $CHROME_BIN" >&2
    return 1
  fi

  local candidates=(
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    "/Applications/Chromium.app/Contents/MacOS/Chromium"
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
  )
  local c
  for c in "${candidates[@]}"; do
    [ -x "$c" ] && { echo "$c"; return 0; }
  done

  local names=(google-chrome google-chrome-stable chromium chromium-browser microsoft-edge)
  for c in "${names[@]}"; do
    if command -v "$c" >/dev/null 2>&1; then command -v "$c"; return 0; fi
  done

  return 1
}

CHROME="$(find_chrome)" || {
  echo "错误: 未找到 Chrome / Chromium / Edge。" >&2
  echo "      请安装其中之一，或用 CHROME_BIN 指定可执行文件绝对路径。" >&2
  exit 1
}

ARGS=(--headless --disable-gpu)
[ "$HEADER_FOOTER" -eq 0 ] && ARGS+=(--no-pdf-header-footer)
[ -n "${CHROME_USER_DATA_DIR:-}" ] && ARGS+=("--user-data-dir=$CHROME_USER_DATA_DIR")

if ! LOG="$("$CHROME" "${ARGS[@]}" --print-to-pdf="$PDF_ABS" "file://$HTML_ABS" 2>&1)"; then
  echo "错误: Chrome 渲染失败。" >&2
  echo "$LOG" | tail -5 >&2
  exit 1
fi

if [ ! -s "$PDF_ABS" ]; then
  echo "错误: PDF 未生成或为空: $PDF_ABS" >&2
  [ -n "$LOG" ] && echo "$LOG" | tail -5 >&2
  exit 1
fi

SIZE_KB=$(( $(wc -c < "$PDF_ABS") / 1024 ))
echo "PDF 已生成: $PDF_ABS (${SIZE_KB} KB)"
