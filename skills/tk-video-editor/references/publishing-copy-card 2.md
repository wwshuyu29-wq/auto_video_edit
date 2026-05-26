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

The rewrite must be driven by the reference TikTok post's publishing title and
caption, not only by the generated product script. Treat the reference title and
caption as the posting template, then replace claims with product-safe facts
shown in the final video.

## Inputs

```json
{
  "platform": "TikTok",
  "product": {},
  "reference_post": {
    "title": "How to write a research paper like a phd/master student",
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

- Use the competitor title and caption as category and structure references, not as copy to paste.
- First classify the publishing template type:
  - `mistake_urgency_cta`: regret/mistake warning + direct website/tool CTA.
  - `how_to_easy_way`: practical how-to promise + academic credibility/ease.
  - `pain_question_solution`: familiar pain/question + cleaner workflow answer.
  - `workflow_direct_demo`: direct "how I use this tool" workflow demo.
  - `result_reveal`: before/after or visible result reveal.
- Preserve the reference post's emotional rhythm, CTA placement, punctuation
  energy, and hashtag category when safe.
- Preserve the academic/research niche and creator workflow feel.
- Adapt to product truth:
  - Literfy: real papers -> saved sources -> structured review starting point.
  - Citely: source tracing -> reference details -> check before relying.
  - FigPad: figure draft -> editable/reviewable output -> user checks details.
- Do not claim perfect output, guaranteed accuracy, submission-ready work, or replacement of real research.
- Hashtags should mix product, academic niche, and reference-style tags.
- Avoid making the caption sound like website ad copy.

If the reference post uses regret/urgency such as `dont make the mistakes i did. Use this website now!!!`, preserve that publishing rhythm but replace the action with the product-safe workflow shown in the final video.

## Template Summary Output

Every output should include `template_type_summaries` so the user can compare
how different TikTok publishing formats work. Each summary explains:

- video publishing title logic
- video publishing caption logic
- best-fit product/video situations
- reusable title and caption shape

## Output

```json
{
  "platform": "TikTok",
  "product_name": "Literfy",
  "reference_post": {
    "title": "How to write a research paper like a phd/master student",
    "caption": "How to write a research paper like a phd/master student!!! #research #phd #literaturereview #citation #researchpaper",
    "template_type": "how_to_easy_way",
    "title_pattern": "How to + specific academic task + credibility/ease qualifier",
    "caption_pattern": "Name the task, show the shortcut workflow, and remind users to review the output."
  },
  "template_type_summaries": [
    {
      "template_type": "how_to_easy_way",
      "title_logic": "Promise a practical method for a specific academic task.",
      "caption_logic": "Name the task, show the shortcut workflow, and remind users to review the output.",
      "best_for": "Literature review, paper discovery, citation generation, and structured research workflows."
    }
  ],
  "publishing_variants": [
    {
      "variant_id": "a_reference_faithful",
      "publishing_template": {
        "template_type": "how_to_easy_way",
        "reference_title": "How to write a research paper like a phd/master student",
        "reference_caption": "How to write a research paper like a phd/master student!!! #research #phd #literaturereview #citation #researchpaper"
      },
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
