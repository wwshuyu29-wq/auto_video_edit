# Auto Video Web App Requirements

## Product Goal

Users submit:

1. A TikTok competitor profile URL or individual TikTok video URLs.
2. Their product features, target audience, offer, and forbidden claims.
3. Their own handheld footage library.

The system outputs:

- Competitor content formula teardown.
- Product-adapted video angles.
- Beat-by-beat rewritten scripts.
- Shot requirements and footage matches.
- A storyboard/edit plan ready for automated cutting.

Phase 1 output should be rewritten storyboard scripts, not fully automatic publishing.

## Core Flow

1. User creates project.
2. User submits TikTok profile/video references.
3. System ingests available reference metadata, thumbnails, captions, transcripts, screenshots, or uploaded reference videos.
4. System identifies repeated viral cover/hook/script formulas.
5. User adds product feature truth table.
6. System rewrites 3-5 script variants.
7. User uploads footage.
8. System indexes footage and matches shots to script beats.
9. System returns a storyboard, shot table, and optional render plan.

## TikTok Ingestion Reality

Directly reading arbitrary TikTok profile pages is not stable because TikTok pages are dynamic, heavily protected, and often require login, cookies, region-specific rendering, or anti-bot checks.

The web app needs a dedicated ingestion layer with multiple modes:

### Mode A: Official API Where Possible

TikTok Display API can list videos for an authorized user's own account through `/v2/video/list/`, but this requires OAuth and the `video.list` scope. It is not a general competitor-scraping API.

TikTok Research API can expose public videos, captions, subtitles, comments, and account data for approved non-profit research use. It is not suitable as the default commercial competitor-analysis path.

### Mode B: User-Provided Artifacts

Most reliable MVP path:

- User pastes URLs.
- User uploads screenshots of profile grid.
- User uploads downloaded reference videos or screen recordings.
- User optionally uploads captions/transcripts.

The analysis engine works from these artifacts even when live scraping fails.

### Mode C: Browser Automation / Scraper Adapter

Useful for internal ops, but should be isolated:

- Playwright/browser worker with logged-in session.
- Rate limits and retry queue.
- Detection of blocked/captcha/login states.
- No assumption that all videos or metrics are retrievable.

Treat this as best-effort, not the core product promise.

### Mode D: Third-Party Data Providers

Optional if a provider is reliable and legally acceptable:

- Public profile metadata.
- Recent post thumbnails.
- Video captions/descriptions.
- Engagement metrics.
- Downloadable media where permitted.

Vendor lock-in and compliance risk must be reviewed before building around one provider.

## Recommended MVP

Do not make live TikTok scraping the blocker.

MVP input should accept:

- TikTok profile URL for context.
- Screenshot of profile grid.
- 3-10 selected reference videos uploaded by the user.
- Product feature table.
- Footage library.

MVP output:

- Format teardown.
- Hook library.
- 5 rewritten scripts.
- Storyboard table.
- Footage needs table.
- Optional EDL JSON.

## Product Feature Truth Table

Ask the user to fill:

| Feature | User pain solved | Visible proof | Claim strength | Forbidden wording |
|---|---|---|---|---|
| ... | ... | ... | proven / inferred / weak | ... |

Only use `proven` and clearly supported `inferred` claims in scripts.

## Storyboard Output Schema

```json
{
  "reference_formula": "...",
  "product_angle": "...",
  "scripts": [
    {
      "title": "...",
      "hook": "...",
      "duration_target_s": 25,
      "beats": [
        {
          "beat": "HOOK",
          "time_s": "0-3",
          "caption": "...",
          "voiceover": "...",
          "visual_need": "...",
          "product_feature": "...",
          "footage_match": "missing / matched / needs upload"
        }
      ],
      "cta": "...",
      "risk_notes": []
    }
  ]
}
```

## Product Positioning Note

The product should not promise "enter any TikTok profile and we fully scrape everything" at launch. A stronger promise is:

"Upload a competitor TikTok page, reference videos, product facts, and your footage. Get product-adapted scripts and shot plans in minutes."

This is more reliable and still valuable.
