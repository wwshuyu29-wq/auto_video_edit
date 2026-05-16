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

## Object Storage

Object storage is cloud storage for large files.

Plain meaning: a cloud hard drive for videos and images.

GitHub stores code and small JSON/MD files. Object storage stores raw videos, final videos, covers, and temporary render files.
