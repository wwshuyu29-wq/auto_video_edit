# Auto Video Workspace

This folder contains the first TK automated video workflow package.

## Cloud-Ready Layout

This repository is now being prepared for cloud migration.

```text
apps/web                 Local Next.js control console
apps/worker              Local worker CLI and background runner
packages/skill-core      Thin Python wrapper around the current skill
packages/schemas         Cloud project/job/storage schemas
skills/tk-video-editor   Current local Codex skill implementation
docs                     Architecture and migration notes
```

The local skill remains the source of truth for now. The web app, worker, and cloud packages wrap it first so the current working video pipeline is not broken during migration.

## Current Local App

`apps/web` is a local control console, not a production cloud app yet. It can:

- create local project folders and `project_job.json` files
- upload or index local footage
- show viral/script/shot-plan artifacts
- run the local worker after preflight checks
- display preview renders, covers, publishing copy, and delivery manifests

Run it with:

```bash
cd apps/web
npm install
npm run dev
```

Open `http://localhost:3000`.

For preview rendering, install the Python image dependency:

```bash
python3 -m pip install -r skills/tk-video-editor/requirements.txt
```

## Main Skill

`skills/tk-video-editor/`

This is the Codex skill being customized for the workflow:

1. Analyze TikTok competitor accounts or viral videos.
2. Extract repeatable content logic.
3. Rewrite scripts around product features.
4. Index handheld footage.
5. Match footage to script beats.
6. Render 9:16 videos and subtitles.

Installed copy:

`/Users/kk/.codex/skills/tk-video-editor/`

Restart Codex after edits if you want it to appear as an available skill in future sessions.

## Source Skills

`source-skills/`

Reference projects pulled for adaptation:

- `video-use`: editing workflow, EDL rendering, transcript packing, timeline view.
- `youtube-clipper-skill`: clipping, subtitle burning, FFmpeg handling.
- `remotion-skills`: Remotion video-generation and subtitle-animation rules.
- `claude-code-video-toolkit`: map of Claude video-production tools.

Treat source skills as references, not trusted production code. Review scripts and dependencies before running anything new.

## Cloud Migration Docs

- `cloud-migration-plan.md`
- `docs/cloud-architecture.md`
- `docs/development-roadmap.md`
- `docs/plain-language-glossary.md`
- `docs/repo-policy.md`
