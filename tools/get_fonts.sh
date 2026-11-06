#!/usr/bin/env bash
# 下载霞鹜文楷（LXGW WenKai）完整字重到 /home/user/fonts，供子集化使用。
# 仅首次构建或 need 重新子集化时需要联网。
set -euo pipefail
DEST="${1:-/home/user/fonts}"
mkdir -p "$DEST"
cd "$DEST"
curl -sL -o lxgw.tar.gz "https://codeload.github.com/lxgw/LxgwWenKai/tar.gz/refs/heads/main"
tar xzf lxgw.tar.gz LxgwWenKai-main/fonts/TTF/LXGWWenKai-Regular.ttf \
                   LxgwWenKai-main/fonts/TTF/LXGWWenKai-Medium.ttf
cp LxgwWenKai-main/fonts/TTF/*.ttf .
rm -rf LxgwWenKai-main lxgw.tar.gz
echo "字体已就绪：$DEST"
