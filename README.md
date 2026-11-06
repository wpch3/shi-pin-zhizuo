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
