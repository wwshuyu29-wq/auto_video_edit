# Vercel Blob Storage Runbook

This project uses Vercel Blob as the cloud hard drive for large files: raw footage, reference videos, generated videos, covers, subtitles, and JSON delivery artifacts.

## One-Time Setup

1. Create or open the Vercel project for `apps/web`.
2. In Vercel, add a Blob store to the project.
3. Pull the Blob token locally:

```bash
cd apps/web
vercel env pull .env.local --yes
```

The local `.env.local` file should contain:

```text
BLOB_READ_WRITE_TOKEN=...
```

Do not commit `.env.local`. It is a secret file.

## Preview What Will Upload

From `apps/web`:

```bash
npm run blob:plan
```

This scans every project under `../../projects`, skips temporary render folders by default, and writes:

```text
../../cloud_asset_manifest.json
```

The manifest is the cloud storage notebook. It records the local file path, Blob key, file type, size, checksum, and upload URL after a real upload.

## Upload Everything

From `apps/web`:

```bash
npm run blob:upload
```

The default Blob key mirrors the local project path, for example:

```text
projects/figpad/research-connect-google-scholar-template/output/final_delivery/figpad_svg_editor_v1_video.mp4
```

## Upload One Project

From `apps/web`:

```bash
node scripts/upload-project-assets-to-blob.mjs --project figpad/research-connect-google-scholar-template --dry-run
node scripts/upload-project-assets-to-blob.mjs --project figpad/research-connect-google-scholar-template --execute --overwrite
```

## Temporary Files

Temporary render folders such as `preview_render`, `render_work`, `segments`, and `qa_frames` are skipped by default.

Include them only when needed:

```bash
node scripts/upload-project-assets-to-blob.mjs --all --execute --overwrite --include-temporary
```

## Access Mode

Uploads are public by default because final videos and covers are meant to be previewed in the web app.

For private uploads:

```bash
node scripts/upload-project-assets-to-blob.mjs --all --execute --private
```

Private Blob files need server-side read logic before the browser can show them.
