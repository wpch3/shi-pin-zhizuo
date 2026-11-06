# V2角色与画幅样张

- `deliverables/三页风格样张_V2.pdf`：3:4高对比角色漫画，共3页，台词已排入。
- `deliverables/核心角色标准图_V2.pdf`：江望舒、江辰希、江星野的新角色标准图。
- `art/character-v2/`：三张核心角色原图。
- `art/vertical-v2/`：三页无字场景原图。
- `deliverables/style-v2/`：全部1440×1920成品PNG。
- `docs/V2角色与画幅规范.md`：后续统一制作规则。

# 当前正式交付

- `deliverables/第一话_竖屏全页漫画.pdf`：封面1页＋正片7页，1440×2560，9:16，每镜一张完整画面。
- `deliverables/vertical-chapter-01/`：封面及上述7页的独立PNG，供用户直接制作视频。
- `deliverables/完整人设与合照.pdf`：7张完整人设卡及1张全员合照。
- `deliverables/complete-character-sheets/`：上述8页的独立PNG。
- `data/characters.json`：用户最新补全人设及已经确认的正式姓名。
- `docs/第一话_竖屏全页分镜.md`：最新制作规格与七页正文。
- `scripts/build_vertical_comic.py`：竖屏漫画、人设卡和PDF构建脚本。

早期四格漫画与 `stories/` 中故事均为历史草案，不再作为正式制作依据。

# 《回家以后》短篇漫画

基于仓库内用户 PDF 制作的纯漫画项目。保留 PDF 中七位家庭成员的人设原文与视觉锚点，不制作语音，不依赖视频。

## 已完成

- **第一话《外人眼里的他们》：5 页 × 4 格，共 20 格。**
- **七张独立人设卡：**父亲、母亲、大哥、姐姐、二哥、妹妹、小侄女。
- 上个 AI 方案审阅、光影调整与故事优化说明。
- 可重复构建的 Python 排版脚本，中文文字不依赖图像生成模型。

## 直接查看成品

- `deliverables/回家以后_第一话.pdf` — 完整五页漫画
- `deliverables/chapter-01/page-01.png` 至 `page-05.png` — 单页图片
- `deliverables/全员人设图.pdf` — 七页人设合集
- `deliverables/character-sheets/` — 七张独立人设卡 PNG
- `docs/项目审阅与制作规范.md` — 对上个方案、光影和故事的完整评估
- `docs/第一话分镜与对白.md` — 逐格文字稿

## 人设锁定

`data/characters.json` 是人设排版的唯一文字来源。不得在续作中擅自添加官方姓名、年龄、亲属关系或改写已确定的学历、工作与性格。视觉锚点只用于延续 PDF 中的立绘识别。

## 重新构建

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/build_comic.py
```

脚本会重建七张人设卡、五张漫画页、两份 PDF 和逐格文字稿。原始立绘位于 `art/characters/`，`art/chapter-01/` 现有十三张独立场景原图；其余分镜使用同一套锁定立绘合成。

字体使用 Noto Sans CJK SC，授权文件见 `assets/fonts/OFL.txt`。

## 短篇故事集

- `stories/README.md`：三篇独立单元剧与一部三话连续短篇的索引。
- `stories/单元剧_只耽误一分钟.md`：4页16格。
- `stories/单元剧_姐姐今天不撒娇.md`：4页16格。
- `stories/单元剧_装进行李箱的二哥.md`：4页16格。
- `stories/连续短篇_三天以后二哥归我们.md`：3话，共12页48格。

这些故事仅使用已经确认的人设，不启用尚未确认的新名字。

## 视觉与命名提案

- `deliverables/视觉与命名提案.pdf`：已选小侄女正比/Q版、撒娇反差样张、命名与降低AI画风规则。
- `docs/命名与视觉优化提案.md`：命名及视觉执行边界。
- `scripts/build_style_review.py`：视觉提案构建脚本。
