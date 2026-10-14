#!/usr/bin/env bash
#
# 双击这个文件即可卸载（macOS 会用「终端」打开并运行）。
# 会先问你一次，确认后才动手。
#
# 也可以手动运行：  bash 一键卸载.command
#
set -u

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" || {
  echo "无法进入脚本所在目录。"
  read -n 1 -s -r -p "按任意键关闭…" || true
  exit 1
}

export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

CODEX_DIR="${CODEX_HOME:-$HOME/.codex}"

clear 2>/dev/null || true
cat <<'BANNER'
  ══════════════════════════════════════════════════════
    Codex 改用 DeepSeek · 一键卸载（还原到安装前）
  ══════════════════════════════════════════════════════

  会做三件事：
    1. 停掉并移除后台适配器服务
    2. 用安装时的备份还原 config.toml
    3. 删除适配器目录（含里面的请求日志）
BANNER
echo "    Codex 目录：$CODEX_DIR"
echo

if [ ! -f ./uninstall.sh ]; then
  echo "  ✗ 这个文件夹里没有 uninstall.sh，无法卸载。"
  echo
  read -n 1 -s -r -p "  按任意键关闭…" || true
  exit 1
fi

printf '  确定要卸载吗？输入 y 再回车确认（直接回车 = 取消）：'
read -r _ANS || true
case "${_ANS:-}" in
  [Yy]*) ;;
  *) echo; echo "  已取消，什么都没改。"
     echo; read -n 1 -s -r -p "  按任意键关闭…" || true
     exit 0 ;;
esac

echo
bash ./uninstall.sh
CODE=$?

echo
if [ "$CODE" -eq 0 ]; then
  cat <<'EOF'
  ══════════════════════════════════════════════════════
    ✓ 已卸载，Codex 回到安装前的配置
  ══════════════════════════════════════════════════════

  如果 Codex / ChatGPT 桌面端正开着，请【完全退出再打开】。

  （可选）还想删掉模型目录的话，手动跑一次：
    ./uninstall.sh --purge
EOF
else
  echo "  ✗ 卸载过程中出错了（退出码 $CODE），请把上面的内容截图发出来。"
fi

echo
read -n 1 -s -r -p "  按任意键关闭…" || true
exit "$CODE"
