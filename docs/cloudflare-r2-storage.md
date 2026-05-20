# Cloudflare R2 Storage Runbook

This project uses Cloudflare R2 as the cloud hard drive for large video assets. R2 is better suited than Vercel Blob for this repo because the local video library is already larger than the Vercel Hobby Blob quota.

## What Goes Into R2

Upload these large or generated files:

- raw `.mov` and `.mp4` footage
- reference videos and extracted reference frames
- final generated videos
- covers and contact sheets
- subtitles
- JSON delivery artifacts and manifests

The upload key mirrors the local path, for example:

```text
projects/literfy/research-connect-7633832153922489621/output/final_delivery/find_papers_citation_v2/literfy_find_papers_citation_v2_video.mp4
```

## Cloudflare Dashboard Setup

1. Open Cloudflare and choose your account.
2. Go to `R2 Object Storage`.
3. Create a bucket named:

```text
auto-video-assets
```

4. Create an R2 API token with object read and write access for this bucket.
5. Copy the values into `apps/web/.env.local`.

## Local Environment Variables

`apps/web/.env.local` needs:

```text
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET=auto-video-assets
R2_PUBLIC_BASE_URL=
```

Where to find them:

- `R2_ACCOUNT_ID`: Cloudflare account ID.
- `R2_ACCESS_KEY_ID`: R2 token Access Key ID.
- `R2_SECRET_ACCESS_KEY`: R2 token Secret Access Key.
- `R2_BUCKET`: bucket name.
- `R2_PUBLIC_BASE_URL`: optional. Add this later if you connect a public/custom domain for browser preview links.

Do not commit `.env.local`.

## Preview What Will Upload

From `apps/web`:

```bash
npm run r2:plan
```

This writes:

```text
../../r2_asset_manifest.json
```

It does not upload anything.

## Upload Everything

From `apps/web`:

```bash
npm run r2:upload
```

The upload command skips temporary render folders by default, including `preview_render`, `render_work`, `segments`, and `qa_frames`.

## Upload One Project

```bash
node scripts/upload-project-assets-to-r2.mjs --project literfy/research-connect-7633832153922489621 --dry-run
node scripts/upload-project-assets-to-r2.mjs --project literfy/research-connect-7633832153922489621 --execute --overwrite
```

## Include Temporary Render Files

Only do this when you intentionally want to preserve work files:

```bash
node scripts/upload-project-assets-to-r2.mjs --all --execute --overwrite --include-temporary
```

## Important Note

R2 objects are private by default. That is fine for backup and worker processing. To preview files directly in a browser, configure a public/custom domain in Cloudflare and set `R2_PUBLIC_BASE_URL`.
