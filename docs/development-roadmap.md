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
- [x] Extend the worker CLI to include preview rendering as the fourth workflow step.

## Phase 2: Web MVP

- [x] Scaffold Next.js in `apps/web`.
- [x] Add product selector for Literfy, Citely, and FigPad only.
- [x] Add reference URL/video input.
- [x] Add local footage upload UI.
- [x] Add local footage indexing into `asset_library.json`.
- [x] Add project status page.
- [x] Add first-pass artifact viewers for viral pattern card, product script card, and shot matching plan.
- [x] Add thumbnail/contact-sheet review for uploaded footage.
- [x] Add first-pass manual labeling for uploaded footage.
- [x] Add worker preflight checks before running a project.
- [x] Add editable artifact review screens before each worker stage.
- [x] Add structured form editor for product script cards.
- [x] Add structured form editor for shot matching plans.

## Phase 3: Worker MVP

- [x] Scaffold worker service in `apps/worker`.
- [x] Add local job runner.
- [x] Add FFmpeg availability check.
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
