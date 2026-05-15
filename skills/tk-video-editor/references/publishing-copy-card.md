# Publishing Copy Card

## Purpose

Generate TikTok publishing metadata after the video and cover are selected.

This module only writes publishing text:

- title options
- recommended title
- caption options
- recommended caption
- hashtags
- posting notes
- compliance notes

It must not rewrite subtitles, change cover text, choose footage, or render video.

## Inputs

```json
{
  "platform": "TikTok",
  "product": {},
  "reference_post": {
    "caption": "How to write a research paper like a phd/master student!!! #research #phd #literaturereview #citation #researchpaper"
  },
  "variants": [
    {
      "id": "a_reference_faithful",
      "video": "/abs/video.mp4",
      "cover": "/abs/cover.jpg",
      "captions_path": "/abs/captions.json"
    }
  ]
}
```

## Rewrite Rules

- Use the competitor caption as a category and structure reference, not as copy to paste.
- Preserve the academic/research niche and creator workflow feel.
- Adapt to product truth: for Literfy, the safe claim is real papers -> selected sources -> outline -> review draft starting point.
- Do not claim perfect output, guaranteed accuracy, submission-ready work, or replacement of real research.
- Hashtags should mix product, academic niche, and reference-style tags.
- Avoid making the caption sound like website ad copy.

## Output

```json
{
  "platform": "TikTok",
  "product_name": "Literfy",
  "publishing_variants": [
    {
      "variant_id": "a_reference_faithful",
      "recommended_title": "...",
      "recommended_caption": "...",
      "hashtags": ["#literfy", "#research", "..."],
      "scores": {
        "reference_fit": 9,
        "native_tiktok_feel": 8,
        "product_truth_safety": 9,
        "hashtag_relevance": 9
      }
    }
  ]
}
```
