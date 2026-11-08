# 《二弟的休息日被全家预约了》漫画制作

> **每次制作、修改、检查与交付前必读：`AGENTS.md`、`PROJECT_MEMORY.md`、`docs/错误复盘与优化方案长期记录.md`。必须逐页用眼睛观察实际成图并结合剧情与构图思考；脚本、尺寸、页数和几何检查通过不等于完成。**V4封面与7页正片均已重新独立绘制，不调用旧正片、不把人设立绘当剧情图，也不以“原图加方框”冒充优化。V3第一话保留作退回版本记录。

当前唯一视觉基准为用户新确认的 `art/reference/family-character-design-v3.jpg`。正式风格统一为暖纸底、低饱和灰蓝与米棕、细腻手绘线、自然五官及轻薄柔和的填色。旧V2高饱和粗描边人物不再混入正式成品。

## 正式交付

- `deliverables/第一话_V4_精细化重制.pdf`：独立剧情封面＋7页独立正片，共8页。
- `deliverables/第一话_竖屏全页漫画.pdf`：按用户参考原图比例制作的竖屏视频版，共8页。
- `deliverables/full-v4/chapter-01/`：V4的8张定版阅读PNG，3:4、1440×1920。
- `deliverables/full-v4-vertical/chapter-01/`：8张竖屏视频PNG，1440×2146；定版原画逐像素保留，只在上下补暖纸色。
- `art/chapter-01-v4/`：本次重新绘制的封面与7张剧情原图，未复用V3场景或人设立绘；其中第5、6页旧原画已被用户最终定稿取代，不再进入正式构建。
- `art/user-final/chapter-01/`：用户上传的第一话第5、6页最终原图、来源与哈希清单。构建脚本只读保护，不得重画、改字或重新排版；第6页第四项为“4. 睡觉休息”。
- `deliverables/第三话_妹妹的休息日.pdf`：第三话封面＋11页正片，**共12页**（2026-11-08第二次返修版）。
- `deliverables/第三话_竖屏全页漫画.pdf`：第三话1440×2146竖屏视频版，共12页。
- `deliverables/full-v4/chapter-03/`、`deliverables/full-v4-vertical/chapter-03/`：第三话阅读版与竖屏版独立PNG。
- `docs/第三话_用户确认剧情与制作边界.md`：第三话已确认的8个事件、现行12页映射、历次开工补充决定与禁止扩写边界。
- `docs/第三话_正式分镜与台词.md`：第三话封面+11页正片正式分镜与台词、家居/外出服；现行道具为一份巨型巴菲＋两把长勺（旧的Y形双头吸管设定已作废，仅作历史记录）。
- `docs/第三话_台词话本_待审.md`：12页版逐页台词话本与可选优化建议。
- `docs/第三话_台词自然度与场景前置复查.md`：按"谁说／为什么／接住上一句了吗／缺什么前提／是否重复"四问对本话及前两话逐句复查的完整结论。
- `art/chapter-03-v6/`：第三话**当前构建唯一来源**（12页版，四边铺满、无画框无空白带）；含新生成的第4／7／8页、局部修手的第6／10页，以及沿用已验收原画；目录内 `canvas-review.json` 记录人眼复核过的预筛误报。
- `art/chapter-03-v5/`：10页版原画，保留作历史对照，不再进构建。
- `art/chapter-03-v4/`：返修前原画，保留作缺陷证据，**不再进构建**；`outfits/` 为家居服/外出服设定，不得直接冒充封面或正片。
- `scripts/build_chapter_v4.py`：按每页原生构图和留白定制排版的构建脚本；第一话PDF已改用无损PNG/Flate导出。
- `scripts/build_chapter03_v4.py`：第三话构建入口（读 `art/chapter-03-v6/`，12页，页码 `NN / 11`）；`scene()` 用 `ImageOps.fit` 保证四边铺满不贴纸底，页码按背景亮度自动反色描边；缺少已审查原画时明确失败，禁止占位图冒充正片。
- `scripts/audit_page_canvas.py`：画面级预筛（黑边、画内框线、纯纸空白带、纸色外边距、画风与线宽漂移），支持 `--anchor` 画风锚点与 `canvas-review.json` 人眼复核台账；只做预筛，不拥有验收权。
- `deliverables/第二话_二姐的独占时间.pdf`：第二话独立封面＋7页正片，共8页。
- `deliverables/第二话_竖屏全页漫画.pdf`：第二话1440×2146竖屏视频版。
- `deliverables/full-v4/chapter-02/`、`deliverables/full-v4-vertical/chapter-02/`：第二话阅读版与竖屏版独立PNG。
- `docs/第二话_二姐的独占时间.md`、`docs/V4第二话精细化制作记录.md`：第二话定稿剧本、逐页制作与审查记录。
- `deliverables/完整人设与合照_V3.pdf`：7张完整人设卡＋七人合照，共8页。
- `deliverables/完整人设与合照.pdf`：同一正式人设与合照的通用路径。
- `deliverables/full-v3/characters/`：7张人设卡及1张合照PNG；每张人设卡均已合并该角色的单独立绘、姓名身份、人物简介与完整设定。
- `data/characters.json`：七人正式姓名与补全人设的排版来源。
- `docs/V3角色与画风锁定.md`：唯一参考、造型和统一画风规范。
- `docs/V3逐页视觉与剧情审查.md`：每页交付前必须执行的视觉、画风及剧情审查铁律。
- `docs/V2扩展角色预案.md`：后续备选角色，未进入第一话。
- `scripts/build_full_v3.py`：V3全量排版与PDF构建脚本。

阅读版页面为 **3:4、1440×1920**。竖屏视频版按参考原图 **1696×2528** 的原始比例等比制作，输出 **1440×2146**；原画不缩放、不裁切、不重绘，中央原画区域与定版PNG逐像素一致。合成视频时项目画布也必须使用该竖屏比例，不得再套入16:9横屏画布。标题、对白、日程表和结尾文字均已排入PNG/PDF，无口播、旁白或音乐。V4每页均有独立剧情动作、表情、视线和场景构图；文字按原生留白及气泡逐页排入，不使用统一方框模板遮盖画面。

## 大哥独立故事线

- `docs/大哥独立故事线/原始设定.md`：逐字保存用户提出的完整原始故事及讨论结论。
- `docs/大哥独立故事线/七话章节规划.md`：暂定7话、每话8—10页的章节规划，约56—70页。
- 暂定系列名：《大哥以前，也只是个孩子》；核心为“曾经被家人接住的人，如今也成为能够接住家人的人”。

## 原始素材

- `art/reference/family-character-design-v3.jpg`：用户指定的五人角色及画风基准。
- `art/character-v3/`：依据确认基准逐张重新生成的七人单独立绘，不再使用从旧参考图直接裁切的人设图。
- `art/family-v3/group.png`：七人合照。
- `art/vertical-v3/`：已退回的V3旧场景，仅作历史对照，不得用于V4。

## 重新构建

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/build_chapter_v4.py
.venv/bin/python scripts/build_chapter02_v4.py
.venv/bin/python scripts/build_chapter03_v4.py
# 如需重建七人正式人设卡，再运行：
.venv/bin/python scripts/build_full_v3.py
```

字体使用Noto Sans CJK SC，授权文件见 `assets/fonts/OFL.txt`。

## 历史文件

V2漫画样张仅作制作过程记录，不再作为正式风格。旧版单独人设卡、旧人设合集PDF及V2角色标准卡已经舍弃并移出交付目录；正式人设只以 `deliverables/full-v3/characters/` 和 `deliverables/完整人设与合照_V3.pdf` 为准。

旧版 `art/characters/`、`art/vertical-chapter-01/`、早期四格漫画和 `stories/` 同样属于历史草案。被否决的 `niece-refined.png` 不得恢复使用。
