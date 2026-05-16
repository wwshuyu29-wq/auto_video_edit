# Worker

This directory will contain the cloud worker for video-processing jobs.

## Planned Responsibilities

- Pull pending jobs from the database or queue.
- Download only the required footage and reference assets from object storage.
- Call `packages/skill-core` to run the existing TK video workflow modules.
- Run FFmpeg and PNG caption rendering.
- Upload final videos, covers, and render reports back to object storage.
- Update job status and error messages.

The worker should be deployed separately from the web app because render jobs are CPU-heavy and can run longer than normal web requests.

## Current Local CLI

The first worker step is a local command-line interface. Think of it as a
temporary control panel before the web buttons exist.

Inspect a project:

```bash
python3 apps/worker/worker_cli.py inspect \
  --project-dir projects/citely/research-connect-google-scholar-template
```

Run one stage without changing project files:

```bash
python3 apps/worker/worker_cli.py run-stage \
  --project-dir projects/citely/research-connect-google-scholar-template \
  --stage asset_matching \
  --dry-run
```

Supported stages:

- `viral_deconstruction`
- `product_script_rewrite`
- `asset_matching`

Rendering is intentionally not wired into this first CLI because video export is
heavier and needs stricter storage cleanup rules.
