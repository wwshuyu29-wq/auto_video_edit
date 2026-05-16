# Web App

This app is the front desk for the auto video workflow.

## Current Goal

Build a local control console before wiring real database and cloud storage.

The app reads and writes local project JSON artifacts from the repository so the UI reflects real workflow state instead of placeholder demo data.

## Current Local Features

- Create a project scaffold for Literfy, Citely, or FigPad.
- Save reference inputs into `full_workflow_input.json`.
- Upload local `.mov` / `.mp4` footage into `materials/raw`.
- Index footage into `output/asset_library.json` and `output/material_index.json`.
- Sync indexed assets back into `full_workflow_input.json` so the worker can use them.
- Start the local worker and show stage-level status/logs.

## Planned Local Run

```bash
cd apps/web
npm install
npm run dev
```

Open `http://localhost:3000`.
