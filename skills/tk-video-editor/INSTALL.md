# TK Video Editor Skill 安装与共享说明

这个文件给拿到 skill 的团队成员使用。

## 方式一：放到某个项目里使用

把整个文件夹复制到目标项目：

```text
<project-root>/skills/tk-video-editor
```

然后在 Codex 里打开这个项目，直接说：

```text
使用 tk-video-editor skill，帮我根据这个 TikTok 对标视频给四个产品生成视频。
```

适合只在某一个视频项目里使用。

## 方式二：作为全局 skill 使用

把整个文件夹复制到本机 Codex skills 目录：

```text
~/.codex/skills/tk-video-editor
```

之后在任何项目里都可以调用：

```text
使用 tk-video-editor skill
```

适合团队成员经常做 TikTok 视频任务。

## 必要依赖

本 skill 会用到本地脚本和视频处理工具。建议确认这些工具可用：

```bash
python3 --version
ffmpeg -version
ffprobe -version
```

如果要从 TikTok 链接下载参考视频，还需要：

```bash
yt-dlp --version
```

如果只提供本地参考视频或截图，可以不依赖 TikTok 下载。

## API 配置

如果要生成 AI 真人开头，需要在项目根目录配置 `.env.local`。

示例：

```env
EVOLINK_API_KEY=你的_key
EVOLINK_API_BASE_URL=https://api.evolink.ai/v1
EVOLINK_VIDEO_MODEL=seedance-2.0-text-to-video
EVOLINK_VIDEO_QUALITY=720p
EVOLINK_VIDEO_GENERATE_AUDIO=false
EVOLINK_VIDEO_WEB_SEARCH=false
```

注意：

- 不要把 `.env.local` 发给别人。
- 不要把 API key 写进 README、脚本、分镜文件或交付文档。
- 如果 API 超时，先检查任务是否已经创建；很多时候只是状态查询超时，可以用 task id 继续查。

## 推荐使用请求

可以这样对 Codex 说：

```text
请使用 tk-video-editor skill。
我给你一个 TikTok 对标视频链接，请拆解前 4 秒 hook，
改写成四个产品的 AI 真人开头，
然后接到后面的手持产品素材，
每个产品生成 2 条视频，
最后附上 TikTok 发布 caption、hashtags、pinned comment。
字幕要留左右安全区，不能贴边。
```

## 输入材料清单

使用前最好准备：

- TikTok 对标视频链接或本地视频。
- 产品信息：产品名、目标用户、痛点、核心功能、不能说的内容。
- 产品素材库：手持视频、屏幕录制或 `asset_library.json`。
- 输出数量：每个产品几条。
- 特殊要求：字幕风格、是否要 emoji、高亮词、打包位置。

## 交付检查

交付前请确认：

- 视频是 9:16 竖屏，建议 `1080x1920`。
- AI 真人 hook 没有复刻对标人物。
- AI 真人 hook 没有开口、唇形、内嵌字幕或可读文字。
- 字幕有左右安全边距。
- 每条视频都有发布 caption、hashtags、pinned comment。
- 发布 caption 不是视频字幕的简单复制。
