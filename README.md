# 《星辰落进灯火里》V3手绘完整重制

> **制作前必读：`PROJECT_MEMORY.md`。**其中记录长期记忆、禁止偷懒红线和真实完成标准。现有第一话因直接复用人设立绘及“原图加对话框”已退回，不再视为合格定稿；必须按剧情独立创作并逐页精细化审查。

当前唯一视觉基准为用户新确认的 `art/reference/family-character-design-v3.jpg`。正式风格统一为暖纸底、低饱和灰蓝与米棕、细腻手绘线、自然五官及轻薄柔和的填色。旧V2高饱和粗描边人物不再混入正式成品。

## 正式交付

- `deliverables/第一话_V3_手绘完整重制.pdf`：姐姐封面＋7页正片，共8页。
- `deliverables/第一话_竖屏全页漫画.pdf`：同一正式第一话的通用路径。
- `deliverables/full-v3/chapter-01/`：8张独立成品PNG，供直接合成视频。
- `deliverables/完整人设与合照_V3.pdf`：7张完整人设卡＋七人合照，共8页。
- `deliverables/完整人设与合照.pdf`：同一正式人设与合照的通用路径。
- `deliverables/full-v3/characters/`：7张人设卡及1张合照PNG；每张人设卡均已合并该角色的单独立绘、姓名身份、人物简介与完整设定。
- `data/characters.json`：七人正式姓名与补全人设的排版来源。
- `docs/V3角色与画风锁定.md`：唯一参考、造型和统一画风规范。
- `docs/V3逐页视觉与剧情审查.md`：每页交付前必须执行的视觉、画风及剧情审查铁律。
- `docs/V2扩展角色预案.md`：后续备选角色，未进入第一话。
- `scripts/build_full_v3.py`：V3全量排版与PDF构建脚本。

全部页面为 **3:4、1440×1920**。标题、对白、日程表和结尾文字均已排入PNG/PDF，无口播、旁白或音乐。第一话7张正片均使用新基准重新制作的独立场景，不使用V2立绘拼贴。

## 大哥独立故事线

- `docs/大哥独立故事线/原始设定.md`：逐字保存用户提出的完整原始故事及讨论结论。
- `docs/大哥独立故事线/七话章节规划.md`：暂定7话、每话8—10页的章节规划，约56—70页。
- 暂定系列名：《大哥以前，也只是个孩子》；核心为“曾经被家人接住的人，如今也成为能够接住家人的人”。

## 原始素材

- `art/reference/family-character-design-v3.jpg`：用户指定的五人角色及画风基准。
- `art/character-v3/`：依据确认基准逐张重新生成的七人单独立绘，不再使用从旧参考图直接裁切的人设图。
- `art/family-v3/group.png`：七人合照。
- `art/vertical-v3/`：7张无字正片场景。

## 重新构建

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt pymupdf
.venv/bin/python scripts/build_full_v3.py
```

字体使用Noto Sans CJK SC，授权文件见 `assets/fonts/OFL.txt`。

## 历史文件

V2漫画样张仅作制作过程记录，不再作为正式风格。旧版单独人设卡、旧人设合集PDF及V2角色标准卡已经舍弃并移出交付目录；正式人设只以 `deliverables/full-v3/characters/` 和 `deliverables/完整人设与合照_V3.pdf` 为准。

旧版 `art/characters/`、`art/vertical-chapter-01/`、早期四格漫画和 `stories/` 同样属于历史草案。被否决的 `niece-refined.png` 不得恢复使用。
