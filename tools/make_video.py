# -*- coding: utf-8 -*-
"""把 comic/ep01/p01..p06.png 合成 1080x1920 竖屏漫剪（静音，可自行配 BGM）。

每页 6s：3% 缓推 + 前后 0.5s 淡入淡出。需要 ffmpeg —— 用 imageio-ffmpeg 提供。
"""
import os
import subprocess
import tempfile

try:
    import imageio_ffmpeg
    FF = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:  # 允许系统自带 ffmpeg
    FF = "ffmpeg"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "comic/ep01")
OUT = os.path.join(ROOT, "out")
os.makedirs(OUT, exist_ok=True)

DUR = 6.0
FPS = 25


def main():
    tmp = tempfile.mkdtemp()
    segs = []
    for i in range(1, 7):
        img = os.path.join(SRC, f"p{i:02d}.png")
        seg = os.path.join(tmp, f"s{i}.mp4")
        vf = (
            "scale=1620:2880,"
            "zoompan=z='min(1+0.00012*on,1.04)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d=1:s=1080x1920:fps={FPS},"
            f"fade=t=in:st=0:d=0.45,fade=t=out:st={DUR-0.55}:d=0.55,format=yuv420p"
        )
        subprocess.run([FF, "-y", "-loglevel", "error", "-loop", "1", "-framerate", str(FPS),
                        "-t", str(DUR), "-i", img, "-vf", vf, "-c:v", "libx264",
                        "-preset", "medium", "-crf", "20", "-movflags", "+faststart", seg], check=True)
        segs.append(seg)
        print("segment", i, "ok")

    lst = os.path.join(tmp, "list.txt")
    with open(lst, "w") as f:
        for s in segs:
            f.write(f"file '{s}'\n")
    out = os.path.join(OUT, "第一话_竖屏漫剪.mp4")
    subprocess.run([FF, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", lst, "-c", "copy", out], check=True)
    print("saved", out, round(os.path.getsize(out) / 1e6, 2), "MB")


if __name__ == "__main__":
    main()
