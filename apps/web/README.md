# Web App

This directory will contain the cloud UI for the automated TikTok video workflow.

## Planned Responsibilities

- Create and manage video projects.
- Collect product choice, reference TikTok link/video, product footage, and style notes.
- Show intermediate decision artifacts:
  - viral pattern card
  - product script card
  - shot matching plan
  - publishing copy card
- Submit render jobs to the worker.
- Display final delivery files from object storage.

The web app should not run heavy FFmpeg jobs directly. Rendering belongs in `apps/worker`.
