# 《星辰落进灯火里》V2完整重制

当前正式风格为 **3:4、1440×1920、高对比黑线、近景大人物、黄色粗标题与粗台词**。标题、对白、日程表和结尾文字均已排入PNG/PDF，不含口播、旁白或音乐。

## 正式交付

- `deliverables/第一话_V2_完整重制.pdf`：姐姐封面＋7页正片，共8页。
- `deliverables/第一话_竖屏全页漫画.pdf`：同一正式第一话文件的兼容路径。
- `deliverables/full-v2/chapter-01/`：8张独立成品PNG，供直接合成视频。
- `deliverables/完整人设与合照_V2.pdf`：7张完整人设卡＋七人合照，共8页。
- `deliverables/完整人设与合照.pdf`：同一人设与合照文件的兼容路径。
- `deliverables/full-v2/characters/`：7张人设卡及1张合照PNG。
- `data/characters.json`：七人正式姓名与补全人设的唯一排版来源。
- `docs/V2角色与画幅规范.md`：V2统一绘制及排版规则。
- `docs/V2扩展角色预案.md`：妹妹同学、小姨的后续备选；均未进入正文。
- `scripts/build_full_v2.py`：V2全量排版与PDF构建脚本。

第1、4、5镜为V2独立场景；第2、3镜采用已确认V2样张；第6、7镜使用同一套V2标准立绘合成，并非独立生成场景。所有页面均经过排版与渲染检查。

## 风格样张

- `deliverables/三页风格样张_V2.pdf`：用户确认风格方向的3页样张。
- `deliverables/核心角色标准图_V2.pdf`：江望舒、江辰希、江星野核心角色标准图。
- `art/character-v2/`：七人V2标准原图。
- `art/family-v2/group.png`：七人全员合照原图。
- `art/vertical-v2/`：V2无字场景原图。
- `deliverables/style-v2/`：已确认的3页样张与3张核心角色卡。

## 重新构建

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt pymupdf
.venv/bin/python scripts/build_full_v2.py
```

脚本重建第一话8页、人设及合照8页和两份正式PDF。字体使用Noto Sans CJK SC，授权文件见 `assets/fonts/OFL.txt`。

## 历史文件

旧版 `art/characters/`、`art/vertical-chapter-01/`、`deliverables/vertical-chapter-01/`、`deliverables/complete-character-sheets/`、`deliverables/chapter-01/` 与早期四格漫画只作历史参考。`stories/` 为停止制作的历史草案，均不再作为正式画风或剧情依据。被否决的 `niece-refined.png` 不得恢复使用。
