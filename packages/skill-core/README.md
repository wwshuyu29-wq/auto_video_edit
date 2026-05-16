# Skill Core

`skill-core` is the cloud-facing wrapper around the current `skills/tk-video-editor` implementation.

The current rule is conservative:

- Keep `skills/tk-video-editor` runnable as the local Codex skill.
- Add wrapper functions here for cloud/web/worker code.
- Migrate internals gradually only when a module needs stable package APIs.

## Current Source Of Truth

The existing implementation remains here:

```text
skills/tk-video-editor/
```

The wrapper resolves that path and can call module runner scripts without duplicating logic.
