# Development Roadmap

## Phase 1: Cloud-Ready Structure

- [x] Keep the existing local skill runnable.
- [x] Add `apps/web`.
- [x] Add `apps/worker`.
- [x] Add `packages/skill-core`.
- [x] Add `packages/schemas`.
- [x] Add cloud architecture docs.
- [x] Add a minimal worker CLI that can inspect one project and dry-run one stage.
- [x] Extend the worker CLI to run a full local project workflow.
- [x] Add a standard `project_job.json` work-order file for worker execution.

## Phase 2: Web MVP

- [ ] Scaffold Next.js in `apps/web`.
- [ ] Add product selector for Literfy, Citely, and FigPad only.
- [ ] Add reference URL/video input.
- [ ] Add footage upload UI.
- [ ] Add project status page.
- [ ] Add artifact viewers for viral pattern card, product script card, and shot matching plan.

## Phase 3: Worker MVP

- [ ] Scaffold worker service in `apps/worker`.
- [ ] Add local job runner.
- [ ] Add FFmpeg availability check.
- [ ] Add object storage download/upload adapter.
- [ ] Add render result manifest output.
- [ ] Add cleanup policy for temporary files.

## Phase 4: Storage And Database

- [ ] Choose object storage: Cloudflare R2, S3, or Supabase Storage.
- [ ] Choose database: Supabase Postgres is the current default.
- [ ] Create tables for projects, assets, jobs, artifacts, and deliveries.
- [ ] Store object storage keys, not large files, in the database.

## Phase 5: Template Library

- [ ] Turn the Google Scholar reference style into a named template.
- [ ] Store template-level subtitle style rules.
- [ ] Store template-level cover rules.
- [ ] Store template-level shot rhythm and hook logic.
- [ ] Add future TikTok reference templates without rewriting the workflow.
