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
