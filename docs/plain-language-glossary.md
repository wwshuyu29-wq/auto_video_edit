# Plain Language Glossary

This project should explain technical terms in plain language.

## CLI

CLI means command-line interface.

Plain meaning: a text command that works like a temporary button.

Before we build a real web page with buttons, we can type a command such as:

```bash
python3 apps/worker/worker_cli.py inspect --project-dir projects/citely/research-connect-google-scholar-template
```

That command tells the computer what to do. Later, the web page button will call the same kind of logic behind the scenes.

## Worker

A worker is the part of the system that does the heavy work.

Plain meaning: the backstage assistant.

The web page is the front desk. It collects uploads and shows results. The worker does slow jobs such as analyzing scripts, matching footage, and rendering videos.

## Worker Scheduling

Worker scheduling means deciding which backstage job should run, in what order, and with which files.

Plain meaning: a to-do list manager for the backstage assistant.

Example:

1. Analyze the reference video.
2. Rewrite the product script.
3. Match footage to the script.
4. Render the video.
5. Save the result.

## Dry Run

A dry run means testing the process without changing important files.

Plain meaning: rehearsal mode.

In this project, `--dry-run` lets us check whether the worker can call a module correctly without overwriting the approved project outputs.

## Schema

A schema is a rulebook for data shape.

Plain meaning: a form template.

For example, a project schema says every project should have a project id, product name, status, asset ids, and delivery information.

## Project Job

A project job is the worker's work order.

Plain meaning: one instruction sheet that tells the backstage assistant what project to open, which steps to run, which files to reuse, and where outputs belong.

In this repo, that file is usually:

```text
project_job.json
```

Example ideas inside it:

- which project is being processed
- whether the worker should run a step again
- whether the worker should reuse an existing result
- where the main JSON outputs live

## Preview Render

Preview render means a usable captioned video preview, not the final publishing system.

Plain meaning: an automatically generated first cut.

In this project, preview render is good enough to verify:

- the chosen shots
- subtitle timing
- pacing
- visual flow

Later, the same worker can be extended to handle more advanced final delivery rules.

## Object Storage

Object storage is cloud storage for large files.

Plain meaning: a cloud hard drive for videos and images.

GitHub stores code and small JSON/MD files. Object storage stores raw videos, final videos, covers, and temporary render files.

## Asset Library

Asset library means the structured list of usable video materials.

Plain meaning: the system's footage notebook.

When you upload `.mov` or `.mp4` clips, the web app saves them into the project folder and writes a file called:

```text
output/asset_library.json
```

The worker reads this file to know which clips exist, where each clip lives, how long it is, whether it is vertical, and whether it can be used for matching.

## Indexing

Indexing means scanning uploaded videos and writing their basic information into JSON.

Plain meaning: making a catalog before editing.

The first version detects basic metadata such as duration and orientation, and it generates a simple thumbnail so the footage can be reviewed on the web page.

## Thumbnail

A thumbnail is a still image taken from a video.

Plain meaning: the cover preview for one clip.

It helps you quickly recognize whether a clip is a landing page, a search result, a citation screen, or a final CTA shot without opening the full video.

## Manual Labels

Manual labels are human-written notes attached to a clip.

Plain meaning: your editor notes for the system.

Examples:

- `shot_type`: landing page screen recording
- `scene`: Citely verify references result
- `best_use`: product proof, CTA, transition
- `text_overlay_safe_area`: upper center

These labels make asset matching more reliable because the system can choose footage from your judgment, not only from file names.

## Preflight

Preflight means checking whether a project is ready before the worker starts.

Plain meaning: the checklist before the backstage assistant begins editing.

It checks things such as:

- whether FFmpeg and ffprobe are installed
- whether the project has a valid work order
- whether the product is one of Literfy, Citely, or FigPad
- whether footage has been indexed
- whether indexed footage files still exist
- whether required reused artifacts exist

If there is a blocker, the web page disables `Run Worker` and the API refuses to start the worker. Warnings do not stop the run, but they tell us quality may be weaker.

## Artifact

An artifact is a saved middle result from the workflow.

Plain meaning: one checkpoint file.

In this project, the most important editable artifacts are:

- `viral_pattern_card.json`: why the reference video/account works
- `product_script_card.json`: product-safe TikTok script variants
- `shot_matching_plan.json`: which clip supports each script beat

These are deliberately separate. If a video feels wrong, we can inspect the checkpoint and see whether the issue came from viral logic, product script, or footage matching.

## Editable Artifact Review

Editable artifact review means checking and editing those checkpoint files before the worker renders the video.

Plain meaning: human approval before the machine starts cutting.

The first web version edits raw JSON. That is useful for flexibility and debugging. Later, we can build more friendly form editors for script lines, subtitles, clip choices, and timing.
