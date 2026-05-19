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

Create a project-local Python environment and install the rendering dependency before running preview renders:

```bash
python3 -m venv .venv
.venv/bin/python3 -m pip install -r skills/tk-video-editor/requirements.txt
```

Inspect a project:

```bash
.venv/bin/python3 apps/worker/worker_cli.py inspect \
  --project-dir projects/citely/research-connect-google-scholar-template
```

Run one stage without changing project files:

```bash
.venv/bin/python3 apps/worker/worker_cli.py run-stage \
  --project-dir projects/citely/research-connect-google-scholar-template \
  --stage asset_matching \
  --dry-run
```

Create a standard project job file:

```bash
.venv/bin/python3 apps/worker/worker_cli.py init-job \
  --project-dir projects/literfy/research-connect-7633832153922489621
```

Run a whole project from the job file:

```bash
.venv/bin/python3 apps/worker/worker_cli.py run-project \
  --job-file projects/literfy/research-connect-7633832153922489621/project_job.json \
  --dry-run
```

Supported stages:

- `viral_deconstruction`
- `product_script_rewrite`
- `asset_matching`
- `video_rendering`

The render step currently uses the existing preview-render path. Plain meaning:
it can automatically produce a captioned preview video from the approved shot
matching plan, but it is not yet trying to manage all final delivery variants.

## Plain-Language Meaning

- `init-job`: make one standard work order for the project.
- `run-project`: let the worker follow that work order step by step.
- `reuse_existing`: do not recalculate this step, just use the file already on disk.
- `dry-run`: rehearse without overwriting the approved project outputs.
- `preview_render`: make a usable captioned preview video with the current PNG subtitle path.
