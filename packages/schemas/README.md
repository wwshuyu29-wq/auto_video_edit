# Schemas

This directory stores cloud-facing JSON schemas shared by the web app, worker, and skill core.

The existing skill module schemas still live beside their modules in:

```text
skills/tk-video-editor/modules/*/schema.json
```

Cloud schemas describe project/job/storage state. Skill schemas describe the stable content artifacts.

Current cloud schemas:

- `cloud_project.schema.json`: top-level project record
- `render_job.schema.json`: queued or running job record
- `storage_asset.schema.json`: object storage file record
- `project_job.schema.json`: worker work-order file used to run one project locally or in a worker
