#!/usr/bin/env bash
#
# 双击这个文件即可安装（macOS 会用「终端」打开并运行）。
# 它会问你要网关 key，其余全部用推荐默认值。
#
# 也可以手动运行：  bash 一键安装.command
# Linux 上同样可用： bash 一键安装.command
#
set -u

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" || {
  echo "无法进入脚本所在目录。"
  read -n 1 -s -r -p "按任意键关闭…" || true
  exit 1
}

# 从 Finder 启动时的 PATH 可能不含 Homebrew / 本地 bin，补齐常见位置（codex、python3 靠它找）
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

clear 2>/dev/null || true
cat <<'BANNER'
  ══════════════════════════════════════════════════════
    Codex 改用 DeepSeek · 一键安装
  ══════════════════════════════════════════════════════

  这个窗口会问你 1~2 个问题，然后自动装好。
  什么都不用填，直接回车就是推荐设置。
BANNER

if [ ! -f ./install.sh ]; then
  echo
  echo "  ✗ 这个文件夹里没有 install.sh。"
  echo "    请确认「一键安装.command」和 install.sh 在同一个文件夹里。"
  echo
  read -n 1 -s -r -p "  按任意键关闭…" || true
  exit 1
fi

bash ./install.sh
CODE=$?

echo
if [ "$CODE" -eq 0 ]; then
  # 端口可能不是默认的 8899，从 config.toml 里读回来
  URL="$(sed -n 's/.*base_url *= *"\(http:\/\/127\.0\.0\.1:[0-9]\{1,\}\).*/\1/p' \
          "${CODEX_HOME:-$HOME/.codex}/config.toml" 2>/dev/null | head -1)"
  [ -n "$URL" ] || URL="http://127.0.0.1:8899"

  cat <<EOF

  ══════════════════════════════════════════════════════
    ✓ 安装完成
  ══════════════════════════════════════════════════════

  接下来请做一件事：
  如果 Codex / ChatGPT 桌面端正开着，请【完全退出再打开】，
  否则它会继续用旧配置。（终端里跑 codex 的话不用管）

  看请求和回复的网页：
    $URL/__ui

EOF
  printf '  按回车打开这个网页（不想打开就直接关窗口）：'
  read -r _ || true
  command -v open >/dev/null 2>&1 && open "$URL/__ui"
elif [ "$CODE" -eq 3 ]; then
  # 3 = 用户在问答里选择了取消（install.sh 专门用这个码区分于失败）
  echo "  没有做任何改动。要安装就再双击一次这个文件。"
  echo
  read -n 1 -s -r -p "  按任意键关闭…" || true
else
  echo "  ✗ 安装没有成功（退出码 $CODE）。"
  echo "    把上面的报错内容截图发出来即可，机器本身没有被改坏："
  echo "    想回到安装前，双击「一键卸载.command」。"
  echo
  read -n 1 -s -r -p "  按任意键关闭…" || true
fi

exit "$CODE"
