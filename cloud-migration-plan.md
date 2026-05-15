# Auto Video Cloud Migration Plan

## Goal

Move the local TikTok automation workflow to a cloud-ready architecture without uploading bulky raw footage or generated videos into Git.

## Recommended MVP Stack

- GitHub: store code, skills, schemas, templates, product library, and knowledge base.
- Vercel + Next.js: web UI for uploading reference links, product info, and assets.
- Supabase Postgres: projects, products, script cards, shot plans, render jobs, delivery metadata.
- Cloudflare R2 or AWS S3: raw `.mov`, reference videos, generated covers, final videos, and temporary render artifacts.
- Render worker: a separate worker service with FFmpeg and the current Python skill scripts. Good first choices are RunPod, Fly.io, Railway, Render, or an EC2/Lightsail instance.
- Queue: start with Supabase job rows or Upstash Redis. Move to a dedicated queue when batch volume grows.

## What Should Go To GitHub

- `skills/`
- `product-library/`
- reusable `projects/*/output/*.json` templates only when they are examples
- `knowledge-base.md`
- `README.md`
- cloud app source code

## What Should Not Go To GitHub

- raw user footage
- downloaded TikTok/reference videos
- temporary segments
- overlay PNG batches
- preview renders
- final delivery videos and covers
- API keys or `.env` files

## Cloud Data Flow

1. User creates a project in the web UI.
2. User uploads reference URL/video, product profile, and footage.
3. Files are stored in R2/S3; metadata is stored in Supabase.
4. Orchestrator job generates:
   - viral pattern card
   - product script card
   - shot matching plan
   - publishing copy card
5. Render worker downloads only the needed assets, runs FFmpeg/PNG caption rendering, uploads final video and cover.
6. Web UI shows the final delivery files and reports.
7. Cleanup policy deletes temporary cloud artifacts after a retention window.

## First Migration Step

Create a GitHub repo from `/Users/kk/Desktop/auto video`, add `.gitignore`, then upload only code and configuration. Keep existing local videos in the current desktop folder until object storage is connected.
