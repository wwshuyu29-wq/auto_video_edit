# TK Video Editor Skill README

这个 skill 用来把 TikTok 对标视频变成可批量复用的产品短视频流程。它不是单纯写脚本，也不是单纯剪视频，而是把“对标拆解、产品改写、素材匹配、AI 真人开头、字幕渲染、发布文案、打包交付”串成一个可复用工作流。

适合团队成员在做海外 TikTok、StudyTok、AI 工具推广、SaaS 工具演示、学术工具演示、生产力工具演示时使用。

## 一句话说明

输入一个对标 TikTok 视频、产品信息和产品素材库，这个 skill 会先拆解对标视频为什么有效，再把它改写成产品自己的脚本，匹配手持产品素材，必要时调用 API 生成 AI 真人 hook，最后输出带字幕的竖屏视频和发布文案。

## 什么时候使用

适合这些需求：

- 根据一个 TikTok 对标视频，给多个产品批量生成短视频。
- 根据对标视频前几秒真人 hook，改写成自己的 AI 真人开头。
- 把 AI 真人开头接到后面的手持产品功能素材。
- 给视频自动烧录 TikTok 风格字幕。
- 给每条视频生成海外 TikTok caption、hashtags、pinned comment。
- 整理视频产物、QA 截图、分镜文件和发布文案，方便交付。

不适合这些需求：

- 只想写一句普通营销文案。
- 没有产品信息，也没有参考视频或参考截图。
- 想完全复刻对标视频的人脸、身份、房间、动作或字幕。
- 想生成带口播、唇形同步、可读文字的 AI 真人开头。

## 核心原则

这个 skill 的核心原则是：

1. 先拆对标，再写产品。
2. 先看产品事实，再做爆款改写。
3. AI 真人 hook 只模仿情绪和节奏，不复刻原视频。
4. 视频发布文案不能和视频字幕完全一样。
5. 字幕必须留安全边距，不能贴左右边，也不能被 TikTok 右侧按钮挡住。
6. 发布文案要像海外真实创作者发的，不要像品牌广告。

## 输入材料

一次完整任务通常需要这些材料。

### 1. 对标视频

可以提供：

- TikTok 链接
- 本地视频文件
- 截图
- 视频字幕
- 视频标题和发布文案
- 用户说明：为什么喜欢这个模板

如果 TikTok 链接打不开，不能编造内容。需要让用户补充视频截图、字幕或本地视频。

### 2. 产品信息

每个产品至少需要：

- 产品名
- 一句话说明
- 目标用户
- 主要痛点
- 核心功能
- 视频里能看到的结果
- 不能说的内容

例如学术工具不能说：

- 保证引用 100% 正确
- 保证绕过检测
- 替用户写论文
- 鼓励学术不诚信

### 3. 产品素材

可以是：

- 手持拍摄的视频
- 屏幕录制
- 已整理好的 `asset_library.json`
- 素材库文件夹

每段素材最好标清：

- 展示什么功能
- 适合哪个脚本 beat
- 可用时间段
- 不适合展示什么

## Skill 流程

完整流程如下：

```text
reference video
  -> reference_hook_analysis
  -> viral_deconstruction
  -> human_hook_generation
  -> product_script_rewrite
  -> asset_matching
  -> video_rendering
  -> publishing_copy_rewrite
  -> QA and delivery
```

## Step 1: Reference Hook Analysis

模块：

```text
modules/reference_hook_analysis
```

作用：

- 下载或读取对标视频。
- 截取开头几秒。
- 抽帧，生成 contact sheet。
- 识别人脸、表情、动作、场景、镜头、氛围。
- 输出结构化观察结果。

常见输出：

```text
output/human_hook_observation.json
output/hook_frame_index.json
```

这一阶段只做观察，不写产品脚本，也不生成视频。

需要拆出来的信息：

- 人物类型：学生、创作者、研究者、上班族等。
- 表情：焦虑、震惊、无语、心虚、疲惫、松一口气等。
- 动作：扶额、捂嘴、看电脑、指屏幕、递纸、看向镜头等。
- 场景：宿舍、书桌、图书馆、办公室、实验室等。
- 景别：自拍近景、中近景、桌面视角、手持镜头。
- 镜头运动：轻微手持、静止自拍、推近、快速切换。
- 灯光氛围：暖光、冷屏幕光、夜间学习感、自然光。
- 字幕安全区：后期字幕适合放在哪里，不挡脸和产品。

## Step 2: Viral Deconstruction

模块：

```text
modules/viral_deconstruction
```

作用：

- 拆解对标视频为什么能吸引停留。
- 提取爆款结构，不复制原话。
- 记录字幕节奏、CTA 位置、痛点触发方式。

常见输出：

```text
output/viral_pattern_card.json
```

要拆的不是“这个视频讲了什么”，而是：

- 开头为什么让人停下。
- 中间怎么证明产品有用。
- 结尾怎么引导点击、评论、保存。
- 哪些结构可以复用。
- 哪些内容不能复制。

常见模板结构：

```text
[痛点/八卦/翻车现场] + [坏结果] + [慌张情绪] + [切到工具流程] + [结果证明]
```

## Step 3: Human Hook Generation

模块：

```text
modules/human_hook_generation
```

作用：

- 把参考视频的真人开头拆成 AI 视频提示词。
- 调用文字转视频 API 生成新的 AI 真人开头。
- 把生成的视频作为 `ai_human_hook` 写入素材库。

常见输出：

```text
output/human_hook_card.json
output/generated_hooks/ai_human_hook.mp4
```

### AI 真人 hook 规则

AI 真人 hook 只做“表情和动作反应”，不要开口说话。

必须满足：

- 不说话。
- 不做唇形同步。
- 不内嵌字幕。
- 不出现可读文字。
- 不出现产品 UI。
- 不复刻对标视频人物长相。
- 不复刻对标视频房间、衣服、动作顺序。

可以保留：

- 情绪功能。
- 镜头节奏。
- 学生/创作者的真实感。
- “先慌一下，再切产品”的叙事功能。

提示词结构：

```text
[原创人物] + [新场景] + [表情] + [小动作] + [镜头/景别] + [氛围] + [无口播/无字幕/无文字约束]
```

示例：

```text
Realistic vertical 9:16 smartphone selfie video, 4 seconds.
An original young adult student sits at a messy library desk with laptop,
highlighted papers, and sticky notes. The student looks tired and quietly
panicked, presses one hand to their forehead, glances down at the laptop,
then slides a paper slightly into view. Subtle handheld phone motion,
authentic StudyTok style. Silent reaction only. No speaking, no lip-sync,
no subtitles, no readable text, no logos.
```

## Step 4: Product Script Rewrite

模块：

```text
modules/product_script_rewrite
```

作用：

- 把对标模板改写成产品自己的视频脚本。
- 每个产品按照自己的痛点和功能生成不同版本。
- 保留参考视频的爆款结构，但不照抄文案。

常见输出：

```text
output/product_script_card.json
```

脚本需要做到：

- 第一行短，能停留。
- 产品功能转成用户痛点。
- 每个字幕 beat 都能用素材证明。
- 不夸大、不承诺保证结果。
- 不像广告口播。

错误示例：

```text
This AI citation tool improves your academic workflow.
```

更好的写法：

```text
AI gave me citations...
the confidence was high
the sources were not
```

## Step 5: Asset Matching

模块：

```text
modules/asset_matching
```

作用：

- 把脚本每个 beat 匹配到素材库里的视频片段。
- 决定每段素材的开始时间、结束时间、速度。
- 标注为什么这段素材能证明这句字幕。
- 找出缺失素材。

常见输出：

```text
output/shot_matching_plan.json
```

`shot_matching_plan.json` 是渲染的核心文件。里面通常包含：

```json
{
  "time": "0-4s",
  "beat": "hook",
  "on_screen_text": "ran the detector first 😭\n97% AI...\npanic mode",
  "clip_id": "ai_human_hook",
  "clip_start": 0,
  "clip_end": 4,
  "caption_style": {
    "max_width": 640,
    "y_ratio": 0.56
  }
}
```

如果某个 `clip_id` 不存在，不能硬渲染，需要换素材或补素材。

## Step 6: Video Rendering

模块：

```text
modules/video_rendering
scripts/render_tiktok_preview.py
```

作用：

- 按 `shot_matching_plan.json` 剪辑素材。
- 把字幕烧录进视频。
- 输出竖屏 TikTok 视频。
- 生成 QA contact sheet 和字幕文件。

常见输出：

```text
output/final_video.mp4
output/render_report.json
output/captions.json
output/master.srt
output/*_sheet.jpg
output/*_midpoint_sheet.jpg
```

推荐先用 PNG 字幕预览路径，因为它不依赖 FFmpeg 的字幕字体扩展：

```bash
python3 modules/video_rendering/run.py \
  --input output/shot_matching_plan.json \
  --asset-library output/asset_library.json \
  --preview-render \
  --preview-out output/preview.mp4
```

## 字幕安全区规则

这是强制规则。

字幕不能贴近屏幕左右边缘，也不能被 TikTok 右侧按钮挡住。

建议：

- 1080x1920 视频中，字幕最大宽度优先用 `680-740px`。
- 真人自拍开头可以更窄，例如 `620-700px`。
- 长句强制拆成 2-3 行。
- 不要让字幕横跨整屏。
- 不要把字幕放到人脸正中间挡表情。
- 不要放到右侧点赞、评论、收藏、分享按钮区域。

推荐 caption style：

```json
{
  "font_size": 52,
  "min_font_size": 38,
  "max_width": 640,
  "y_ratio": 0.56,
  "line_gap": 8,
  "lines": ["ran the detector first 😭", "97% AI...", "panic mode"]
}
```

## Step 7: Publishing Copy Rewrite

模块：

```text
modules/publishing_copy_rewrite
```

同时配合：

```text
overseas-tiktok-publish-copywriting
```

作用：

- 生成 TikTok 发布 caption。
- 生成 3-6 个相关 hashtags。
- 生成 pinned comment。
- 分析参考视频的发布文案结构。

注意：发布文案不是视频字幕的复制版。

视频字幕是画面内节奏，用来让用户看懂视频。

发布文案是平台上的 caption，用来让用户停留、评论、保存、点击。

发布文案要做到：

- 像海外真实创作者。
- 不像品牌广告。
- 不中文直译。
- 不堆无关热门标签。
- pinned comment 可以有趣一点、吐槽一点，但不能攻击用户。

示例：

```text
Caption:
AI citations have the wildest confidence for something that may not exist.
I check the trail before trusting the bibliography.

Hashtags:
#studytok #citationcheck #researchtips #academictok #aitools

Pinned comment:
citation said “trust me bro” and that was the first red flag
```

## Step 8: QA

交付前必须检查：

- 视频是否为 `1080x1920`。
- 时长是否正常。
- 前 2 秒 hook 是否清楚。
- 字幕是否贴边。
- 字幕是否挡住脸或产品关键区域。
- 右侧 TikTok UI 区域是否安全。
- 产品素材是否和字幕对应。
- 是否有黑屏、跳帧、奇怪裁切。
- 是否有夸大或违规学术承诺。
- 发布文案是否和字幕完全一样，如果一样需要重写。

常见 QA 方式：

```bash
ffprobe -v error -show_entries format=duration:stream=width,height -of json output/final_video.mp4
```

也可以查看：

```text
output/*_sheet.jpg
output/*_midpoint_sheet.jpg
```

## 交付结构

推荐每个产品一个文件夹：

```text
delivery/
├── Literfy/
│   ├── Literfy_video.mp4
│   ├── Literfy_raw_ai_human_hook.mp4
│   ├── publishing_copy.md
│   ├── shot_matching_plan.json
│   ├── human_hook_card.json
│   └── midpoint_QA_sheet.jpg
├── Citely/
├── FigPad/
├── Clearfy/
├── publishing_copy_all.md
└── manifest.json
```

如果是补交第二批，可以放到：

```text
main/
```

避免覆盖上一批视频。

## 常见问题

### 1. TikTok 链接打不开怎么办？

不要编造视频内容。让用户提供本地视频、截图、字幕或可见描述。

### 2. API 返回 403 或超时怎么办？

先区分是“创建任务失败”还是“查询状态超时”。

- 创建任务失败：检查 key、base url、模型名、权限。
- 查询状态超时：保留 task id，之后继续轮询状态。
- 任务完成但下载失败：用状态文件里的 video url 重新下载。

### 3. AI 真人 hook 可以开口说话吗？

默认不可以。这个流程里的 AI 真人开头只做表情、动作和氛围，字幕后期烧录进去。

### 4. 可以复刻参考视频人物吗？

不可以。只能复用情绪功能和镜头节奏，必须改变人物、衣服、房间、道具、角度或动作时机。

### 5. 为什么发布文案不能和字幕一样？

因为它们的任务不同。字幕服务于画面节奏，发布文案服务于平台互动和点击。发布文案要根据产品痛点、功能、参考发布模板和 TikTok 语感重新写。

## 推荐工作方式

每次任务建议按这个顺序交付：

1. 确认参考视频和目标产品。
2. 拆前几秒 hook。
3. 写产品安全版脚本。
4. 生成 AI 真人 hook。
5. 接产品手持素材。
6. 渲染视频。
7. QA 字幕安全区。
8. 生成发布文案和 tags。
9. 分类打包。

## 最重要的检查清单

交付前最后看这 8 项：

- 对标视频结构已拆解。
- AI 真人 hook 没有一比一复刻。
- 真人 hook 不说话、不内嵌字幕。
- 每个产品脚本角度不同。
- 每句字幕都有对应画面证明。
- 字幕留出左右安全距离。
- 发布文案不是字幕复制版。
- 文件已按产品分类打包。
