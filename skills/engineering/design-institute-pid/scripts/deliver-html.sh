#!/bin/bash
# v3.4 P&ID 交付脚本
# 用途：写完 HTML 后，一键验证 + 启 HTTP server + 输出可发送的链接
# 女王 2026-06-06 硬性要求：交付必须用 HTTP 链接，不发附件
# 用法：bash deliver-html.sh <filepath> [port]

set -e

FILEPATH="${1:-}"
PORT="${2:-28082}"

if [ -z "$FILEPATH" ]; then
  echo "用法: bash deliver-html.sh <filepath> [port]"
  echo "示例: bash deliver-html.sh /path/to/pid.html 28082"
  exit 1
fi

if [ ! -f "$FILEPATH" ]; then
  echo "❌ 文件不存在: $FILEPATH"
  exit 1
fi

FILENAME=$(basename "$FILEPATH")
DIRNAME=$(dirname "$FILEPATH")
EXTERNAL_IP="69.12.72.246"

echo "================================================"
echo "v3.4 P&ID 交付脚本"
echo "================================================"
echo "文件: $FILENAME"
echo "路径: $DIRNAME"
echo "端口: $PORT"
echo ""

# Step 1: 检查 UTF-8 BOM
echo "[1/4] 检查 UTF-8 BOM..."
BOM=$(head -c 3 "$FILEPATH" | xxd -p)
if [ "$BOM" = "efbbbf" ]; then
  echo "✓ UTF-8 BOM 存在"
else
  echo "⚠ UTF-8 BOM 缺失，自动添加..."
  echo -ne '\xef\xbb\xbf' > /tmp/bom.tmp
  cat "$FILEPATH" >> /tmp/bom.tmp
  mv /tmp/bom.tmp "$FILEPATH"
  echo "✓ UTF-8 BOM 已添加"
fi

# Step 2: 检查 HTTP server 是否已运行
echo ""
echo "[2/4] 检查 HTTP server 状态..."
if lsof -i :$PORT > /dev/null 2>&1; then
  echo "✓ HTTP server 已在端口 $PORT 运行"
else
  echo "启动 HTTP server（端口 $PORT）..."
  cd "$DIRNAME"
  nohup python3 -m http.server $PORT --bind 0.0.0.0 > /tmp/http-server-$PORT.log 2>&1 &
  sleep 2
  echo "✓ HTTP server 已启动 (PID: $!)"
fi

# Step 3: 本机 + 外网验证
echo ""
echo "[3/4] HTTP 验证..."
LOCAL=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:$PORT/$FILENAME 2>&1 || echo "FAIL")
echo "  本机: HTTP $LOCAL"

EXTERNAL=$(curl -s -o /dev/null -w '%{http_code} | size %{size_download} bytes | time %{time_total}s' http://$EXTERNAL_IP:$PORT/$FILENAME 2>&1 || echo "FAIL")
echo "  外网: HTTP $EXTERNAL"

if [[ "$EXTERNAL" == *"200"* ]]; then
  echo ""
  echo "✓✓✓ 验证通过 ✓✓✓"
else
  echo ""
  echo "❌ 外网验证失败，请检查防火墙/端口转发"
  exit 1
fi

# Step 4: 输出可发送的链接
echo ""
echo "[4/4] 准备交付..."
echo "================================================"
echo "📋 可发送的链接（复制到微信/邮件）："
echo ""
echo "  http://$EXTERNAL_IP:$PORT/$FILENAME"
echo ""
echo "📋 文件信息："
echo "  路径: $FILEPATH"
echo "  大小: $(du -h $FILEPATH | cut -f1)"
echo "  BOM:  $([ "$BOM" = "efbbbf" ] && echo "✓ UTF-8" || echo "✗ 缺失")"
echo "================================================"
echo ""
echo "⚠️  女王要求：必须发送 HTTP 链接，不要直接发附件！"
echo "   理由：Windows 11 微信传 HTML 附件经常被安全策略拦截"
echo "   HTTP 链接可点击直接在 Edge/Chrome 中渲染 SVG"
