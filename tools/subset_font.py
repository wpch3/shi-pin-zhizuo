# -*- coding: utf-8 -*-
"""把完整霞鹜文楷子集化到「本项目实际用到的字」，让仓库只带 ~200KB 字体。

完整字体请先运行 tools/get_fonts.sh 下载到 /home/user/fonts。
改完文案后重跑本脚本即可（缺字会以方框显示，跑完记得看一眼出图）。
"""
import glob
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = "/home/user/fonts"
DST = os.path.join(ROOT, "assets/fonts")

EXTRA = ("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz "
         ".,:;!?()[]{}<>/\\|-—…·「」『』【】“”‘’％%℃▷+")


def collect():
    chars = set(EXTRA)
    for f in glob.glob(os.path.join(ROOT, "tools/*.py")):
        src = open(f, encoding="utf-8").read()
        for s in re.findall(r'"([^"\n]*)"', src):
            chars.update(ch for ch in s if ord(ch) > 0x2000)
    return chars


def main():
    chars = collect()
    cps = ",".join(f"U+{ord(c):04X}" for c in sorted(chars))
    os.makedirs(DST, exist_ok=True)
    for w in ("Regular", "Medium"):
        src = os.path.join(RAW, f"LXGWWenKai-{w}.ttf")
        if not os.path.exists(src):
            raise SystemExit(f"缺少完整字体 {src}，先运行 tools/get_fonts.sh")
        out = os.path.join(DST, f"LXGWWenKai-{w}.subset.ttf")
        subprocess.run(["pyftsubset", src, f"--unicodes={cps}", "--layout-features=*",
                        "--no-hinting", f"--output-file={out}"], check=True)
        print(f"{out}  {os.path.getsize(out)//1024} KB  ({len(chars)} 字形)")


if __name__ == "__main__":
    main()
