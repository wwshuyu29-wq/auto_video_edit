# Auto Video Workspace

这是一个本地短视频自动化工作台。第一次接触这个项目时，可以把它理解成：

```text
用户给参考 TikTok 视频 + 产品信息 + 自己拍的素材
项目拆解参考视频套路
项目把套路改写成产品脚本
项目把脚本每一句匹配到素材
项目生成带字幕的 9:16 预览视频和发布文案
```

当前重点不是做一个公开上线的 SaaS，而是先把本地工作流跑通，并且让每一步产物都能被检查、修改和复用。

## 这个项目解决什么问题

做 TikTok / TK 产品短视频时，通常有几个重复但很耗时的步骤：

1. 看对标账号或爆款视频，拆出它为什么有效。
2. 把对标视频的结构改写成自己产品能说、且不夸大的脚本。
3. 在自己的素材库里找每句脚本对应的画面。
4. 剪成竖屏视频，加字幕、封面和发布文案。

这个仓库就是把上面流程变成一套可重复执行的本地系统。

## 当前能做什么

- 创建 Literfy、Citely、FigPad 等产品视频项目。
- 保存 TikTok reference URL、产品信息、视频长度、语气和备注。
- 上传或索引本地 `.mov` / `.mp4` 素材。
- 生成并查看 5 类核心产物：
  - `human_hook_observation.json` / `hook_frame_index.json`：参考视频前几秒抽帧和视觉观察。
  - `viral_pattern_card.json`：参考视频拆解。
  - `human_hook_card.json`：真人出镜 hook 的识别、画面理解和文生视频提示词。
  - `product_script_card.json`：产品脚本。
  - `shot_matching_plan.json`：脚本和素材的匹配表。
  - `worker_preview.mp4` / `worker_render_report.json`：预览视频和渲染报告。
  - `publishing_copy_card.json`：标题、caption、hashtags 等发布文案。
- 通过网页按钮启动本地 worker，也可以用命令行单独跑某个阶段。

## 项目目录怎么读

```text
apps/web                 本地网页控制台，用来创建项目、上传素材、查看产物、启动 worker
apps/worker              本地 worker，负责真正跑脚本拆解、素材匹配和视频渲染
packages/skill-core      Python 包装层，让 worker 能调用 tk-video-editor skill
packages/schemas         项目、任务、素材、渲染产物的 JSON schema
skills/tk-video-editor   当前最核心的视频生产逻辑
product-library          产品事实库，规定每个产品能说什么、不能说什么
projects                 本地项目数据和输出产物
docs                     云迁移、对象存储、开发路线等文档
```

简单理解：

- `apps/web` 是前台页面。
- `apps/worker` 是后台生产线。
- `skills/tk-video-editor` 是真正的短视频工作流大脑。
- `projects` 是每个视频项目的输入和输出文件夹。

## 本地启动前准备

需要本机有：

- Node.js 和 npm：运行网页控制台。
- Python 3.11+：运行 worker 和视频工作流。
- FFmpeg / ffprobe：读取视频信息、生成缩略图、渲染预览视频。
- yt-dlp：正式跑 reference 阶段时，尝试从 TikTok 视频 URL 下载参考视频。

如果还没有 FFmpeg，可以先安装：

```bash
brew install ffmpeg
brew install yt-dlp
```

建议在仓库根目录创建 Python 虚拟环境：

```bash
python3 -m venv .venv
.venv/bin/python3 -m pip install -r skills/tk-video-editor/requirements.txt
```

`requirements.txt` 里主要包含预览渲染需要的图片处理依赖。

## 启动网页控制台

在仓库根目录下运行：

```bash
cd apps/web
npm install
npm run dev
```

然后打开：

```text
http://localhost:3000
```

网页控制台现在是本地工具，不是生产环境网站。它会直接读写仓库里的 `projects/` 文件夹。

## 第一次怎么用

### 1. 创建项目

打开：

```text
http://localhost:3000/projects/new
```

填写：

- 项目名。
- 产品名，例如 `Literfy`、`Citely`、`FigPad`。
- TikTok 参考账号 URL 或视频 URL。
- 目标视频长度、语气、模板名和备注。

创建后，系统会生成一个项目目录，例如：

```text
projects/literfy/research-connect-7633832153922489621/
```

里面最重要的两个文件是：

```text
full_workflow_input.json   整个项目的输入
project_job.json           worker 要执行的工作单
```

### 2. 上传或索引素材

进入项目详情页后，去素材页面上传 `.mov` 或 `.mp4`。

系统会把素材放到类似这样的目录：

```text
projects/<product>/<project-id>/materials/raw/
```

然后生成或更新：

```text
output/asset_library.json
output/material_index.json
```

这里记录每个素材的时长、方向、缩略图、镜头标签、适合用在哪些脚本 beat 上。

### 3. 跑 worker

在网页里点击运行按钮时，系统会先做 preflight 检查。

preflight 的意思是“开工前检查”，主要确认：

- `project_job.json` 是否存在。
- `full_workflow_input.json` 是否存在。
- 素材库是否存在。
- FFmpeg 是否能运行。
- Python 依赖是否可用。

检查通过后，网页会启动本地 worker。worker 会按顺序执行：

```text
reference_hook_analysis
viral_deconstruction
human_hook_generation
product_script_rewrite
asset_matching
video_rendering
```

### 4. 检查 5 步输出

项目详情页会把结果拆成 5 步：

1. `Reference`：参考视频拆解和字幕节奏。
2. `Script`：产品脚本、hook、分镜文案。
3. `Assets`：素材库和脚本 beat 的匹配结果。
4. `Video & Cover`：预览视频、字幕、封面、渲染报告。
5. `Publish Copy`：标题、caption、hashtags 和发布注意事项。

这个项目的原则是：每一步都留下 JSON 或 Markdown 产物，方便人工检查和重新跑。

## 不走网页，直接用命令行

命令行适合调试 worker 或只跑某一个阶段。

先回到仓库根目录：

```bash
cd /Users/kk/Desktop/auto\ video
```

检查一个项目：

```bash
.venv/bin/python3 apps/worker/worker_cli.py inspect \
  --project-dir projects/literfy/research-connect-7633832153922489621
```

只试跑一个阶段，不覆盖项目文件：

```bash
.venv/bin/python3 apps/worker/worker_cli.py run-stage \
  --project-dir projects/literfy/research-connect-7633832153922489621 \
  --stage asset_matching \
  --dry-run
```

跑完整项目，但不覆盖正式输出：

```bash
.venv/bin/python3 apps/worker/worker_cli.py run-project \
  --job-file projects/literfy/research-connect-7633832153922489621/project_job.json \
  --dry-run
```

去掉 `--dry-run` 才会写入正式输出文件。

## 核心工作流是什么

核心逻辑在：

```text
skills/tk-video-editor/
```

它的模块边界如下：

```text
reference_hook_analysis   抽取 reference 前几秒帧，生成视觉观察 JSON
viral_deconstruction      只拆参考视频结构，不写产品脚本
human_hook_generation     识别真人出镜开头，写文生视频 prompt，可调用 API 生成 AI 真人 hook
product_script_rewrite    用产品事实改写脚本，不选素材
asset_matching            把脚本 beat 匹配到素材，不重写脚本
video_rendering           按 shot plan 渲染预览视频
publishing_copy_rewrite   写标题、caption、hashtags，不改视频
```

如果后面的模块发现前面有问题，应该返回 revision flag 或风险说明，而不是偷偷改掉前面模块的产物。

## 重要输入和输出文件

一个项目通常长这样：

```text
projects/<product>/<project-id>/
├── full_workflow_input.json
├── project_job.json
├── materials/
│   ├── raw/
│   └── contact_sheets/
└── output/
    ├── viral_pattern_card.json
    ├── human_hook_observation.json
    ├── hook_frame_index.json
    ├── human_hook_card.json
    ├── product_script_card.json
    ├── asset_library.json
    ├── material_index.json
    ├── shot_matching_plan.json
    ├── render_report.json
    └── final_delivery/
        ├── worker_preview.mp4
        └── worker_render_report.json
```

常见含义：

- `full_workflow_input.json`：项目总输入。包含 reference、产品、语气、视频长度、素材库。
- `project_job.json`：worker 的工作单。决定哪些阶段要跑，哪些阶段复用旧文件。
- `human_hook_observation.json`：从参考视频前几秒抽帧后得到的动作、神态、环境、镜头风格观察。
- `hook_frame_index.json`：抽出来的帧、contact sheet、视频 metadata。
- `human_hook_card.json`：如果参考视频前几秒是真人 hook，这里记录人物动作、神态、环境、镜头风格、文生视频 prompt 和生成任务状态。
- `asset_library.json`：素材库索引。告诉系统有哪些视频素材、适合怎么用。
- `shot_matching_plan.json`：剪辑计划。告诉渲染模块每个 beat 用哪个 clip。
- `worker_preview.mp4`：当前 worker 生成的预览视频。

## 产品事实库

产品信息不要随便写死在脚本里，应该放在：

```text
product-library/products.json
```

这里记录：

- 产品一句话介绍。
- 目标用户。
- 核心功能。
- 用户痛点。
- TikTok 角度。
- 禁止使用的夸大说法。

脚本生成时应该以这里为准，避免说出产品没有证明的功能或风险很高的 claim。

## TikTok 输入的现实边界

不要把当前系统理解成“输入任意 TikTok 账号，自动抓取所有公开视频”。

TikTok 页面动态加载、经常需要登录、也有地区和反爬限制。当前更可靠的方式是：

- 粘贴 TikTok URL 作为上下文。
- 上传参考视频或录屏；如果本机有 `yt-dlp`，正式运行时也会先尝试从单条视频 URL 下载。
- 上传截图、字幕、transcript 或人工整理的 frame summary。

也就是说，MVP 更像是：

```text
上传对标素材 + 产品事实 + 自己素材
得到脚本、镜头表和预览视频
```

而不是承诺稳定抓取所有 TikTok 数据。

## 环境变量和安全

本地可能会用到 `.env.local`，例如真人 AI 视频 API、对象存储 token 等。

注意：

- 不要把 `.env.local` 提交到 Git。
- 不要把 API key 写进 README、日志、产物 JSON 或最终回复。
- 如果 key 曾经被公开复制过，应该轮换。

对象存储相关变量可以参考：

```text
apps/web/.env.example
docs/cloudflare-r2-storage.md
```

真人 hook 视频生成会读取：

```text
EVOLINK_API_KEY
AI_REAL_PERSON_VIDEO_API_KEY
```

两个变量有任意一个即可。`--dry-run` 只会生成 prompt，不会调用 API，也不会消耗额度。

参考视频视觉识别会读取：

```text
OPENAI_API_KEY
OPENAI_VISION_MODEL
```

如果你用的是 Evolink 的 OpenAI 兼容网关，不要把 Evolink key 直接打到 OpenAI 官方地址。需要额外配置网关 endpoint，例如：

```text
EVOLINK_OPENAI_RESPONSES_ENDPOINT
EVOLINK_RESPONSES_ENDPOINT
EVOLINK_OPENAI_CHAT_COMPLETIONS_ENDPOINT
EVOLINK_CHAT_COMPLETIONS_ENDPOINT
EVOLINK_OPENAI_BASE_URL
EVOLINK_OPENAI_MODEL
```

系统会用 `EVOLINK_API_KEY` 或 `AI_REAL_PERSON_VIDEO_API_KEY` 调这个 Evolink endpoint。没有 `OPENAI_API_KEY` 且没有 Evolink 兼容 endpoint 时，系统仍会抽帧并生成可人工补充的 observation JSON；不会阻塞后续流程。

如果视频服务的接口地址和默认值不同，可以额外配置：

```text
EVOLINK_BASE_URL
EVOLINK_API_BASE_URL
EVOLINK_VIDEO_GENERATE_ENDPOINT
EVOLINK_TASK_STATUS_ENDPOINT
EVOLINK_VIDEO_MODEL
```

## 云迁移方向

当前本地工作流仍然是主线。云迁移的目标是先包住现有流程，而不是重写它。

目标拆分：

```text
Web App   负责项目创建、上传、状态展示、产物 review
Worker    负责长时间运行的视频分析、匹配、渲染
Storage   存 raw 视频、参考视频、封面、最终 mp4
Database  存项目元数据、任务状态、文件引用和错误信息
```

相关文档：

- `cloud-migration-plan.md`
- `docs/cloud-architecture.md`
- `docs/development-roadmap.md`
- `docs/cloudflare-r2-storage.md`
- `docs/repo-policy.md`

## 常见问题

### 网页能打开，但跑不出视频

先确认：

```bash
ffmpeg -version
ffprobe -version
.venv/bin/python3 -m pip install -r skills/tk-video-editor/requirements.txt
```

再看项目里的：

```text
output/worker_run_status.json
output/worker_run.log
```

### 素材匹配很差

通常是 `asset_library.json` 里的素材标签太少。需要补充：

- `shot_type`
- `scene`
- `visible_objects`
- `best_use`
- `usable_segments`
- `notes`

### 脚本看起来像广告

优先检查：

```text
product-library/products.json
output/viral_pattern_card.json
output/product_script_card.json
```

脚本应该像 creator 分享 workflow，不应该像产品官网文案。

### 想改 workflow 规则

优先改：

```text
skills/tk-video-editor/SKILL.md
skills/tk-video-editor/references/
skills/tk-video-editor/modules/
```

如果是产品事实，改 `product-library/products.json`。

如果是云部署、存储、队列这些工程问题，改 `docs/` 下的对应文档。
