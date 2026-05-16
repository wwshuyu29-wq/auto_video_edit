# Cloud Architecture

## Current Principle

The local Codex skill remains the working production line. Cloud migration should wrap it first, then gradually extract stable package APIs.

Do not break:

```text
skills/tk-video-editor/
```

## Target Layout

```text
apps/
  web/                 # project UI, upload flow, status pages
  worker/              # async render and analysis jobs
packages/
  skill-core/          # cloud wrapper around tk-video-editor
  schemas/             # project/job/storage schemas
skills/
  tk-video-editor/     # current Codex skill implementation
docs/                  # architecture and deployment notes
product-library/       # approved product facts
projects/              # local project examples and structured artifacts
```

## Runtime Split

### Web App

The web app handles user interaction only:

- project creation
- product selection
- reference URL/video upload
- raw footage upload
- artifact review
- final delivery display

It should not render videos or run long FFmpeg jobs.

### Worker

The worker handles long-running work:

- reference analysis
- product script rewrite
- asset matching
- cover generation
- PNG subtitle rendering
- FFmpeg video export
- upload final assets

The worker can call the current skill modules through `packages/skill-core`.

### Skill Core

`packages/skill-core` is a thin wrapper. It exists so web/worker code can call the current skill implementation without hard-coding paths everywhere.

Later, stable logic can move from `skills/tk-video-editor` into `packages/skill-core`, but only after the local workflow remains reproducible.

## Storage Rules

Git stores:

- source code
- skill instructions
- JSON schemas
- product facts
- reusable JSON/MD examples
- architecture docs

Object storage stores:

- raw `.mov` uploads
- downloaded reference videos
- extracted frames/contact sheets
- generated cover images
- final `.mp4` videos
- temporary render segments and overlay PNGs

Database stores:

- project metadata
- job status
- object storage keys
- references to JSON artifacts
- error messages

## Object Storage Key Pattern

Use predictable storage keys:

```text
projects/{project_id}/raw/{asset_id}.mov
projects/{project_id}/reference/{asset_id}.mp4
projects/{project_id}/artifacts/{artifact_id}.json
projects/{project_id}/covers/{variant_id}.jpg
projects/{project_id}/videos/{variant_id}.mp4
projects/{project_id}/tmp/{job_id}/...
```

Temporary keys should have a cleanup TTL.

## First Cloud MVP

1. Web form creates a `CloudProject`.
2. Uploads go to object storage.
3. A `full_workflow` job is queued.
4. Worker downloads assets and runs `skill-core`.
5. Worker uploads final videos and covers.
6. Web page displays the delivery manifest.

Keep one worker instance first. Add queues and scaling only after the manual workflow is stable.
