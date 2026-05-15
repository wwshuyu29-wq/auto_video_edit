# Product Script Card

## Purpose

The product script card is the stable output of `product_script_rewrite`.

It converts a viral pattern card into product-specific TikTok scripts. It should sound like a creator showing a useful workflow, not a homepage ad.

It does not analyze competitor videos again and does not choose footage.

When the viral pattern card includes `caption_logic`, this module must preserve the reference video's sentence roles and punctuation rhythm unless doing so would violate product facts or forbidden claims.

## Input Shape

```json
{
  "viral_pattern_card": {},
  "product": {
    "name": "Literfy",
    "category": "AI literature review tool",
    "target_user": "students and researchers",
    "core_features": ["find relevant papers", "generate literature review", "citation generation"],
    "main_pain_points": ["spending hours searching papers"],
    "proof_points": ["can generate structured review drafts"],
    "forbidden_claims": ["do not claim it replaces human research"]
  },
  "platform": "TikTok",
  "video_length": "25-35s",
  "tone": "native creator style, casual, not too salesy",
  "cta": "try the product"
}
```

## Output Shape

The module must write `output/product_script_card.json`.

It should normally include three versions:

- `safe_version`: truthful, specific, lower-risk.
- `viral_version`: stronger hook, faster rhythm.
- `native_creator_version`: casual user recommendation.

Each script includes beat-by-beat copy and visual needs:

```json
{
  "scripts": [
    {
      "type": "native_creator_version",
      "style": "casual user recommendation",
      "script_title": "I wish I knew this before opening 50 research tabs",
      "script_angle": "I wish I knew this earlier",
      "target_viewer": "students writing literature reviews",
      "version": "TikTok native creator style",
      "full_script": [
        {
          "time": "0-3s",
          "beat": "hook",
          "voiceover": "If your literature review starts with 30 random tabs open, this is for you.",
          "on_screen_text": "Still searching papers manually?",
          "visual_need": "messy laptop / many tabs / stressed study scene",
          "product_feature": ""
        }
      ],
      "caption": "Writing a literature review does not have to start with chaos.",
      "hashtags": ["#researchtools", "#aitools"],
      "compliance_notes": ["Avoid saying the tool guarantees perfect citations"]
    }
  ],
  "scores": {
    "hook_strength": 8,
    "product_fit": 9,
    "native_tiktok_feel": 7,
    "clarity": 8,
    "conversion_potential": 7
  }
}
```

## Marketing Rules

Prefer:

- "I found a tool that saves me from opening 50 research tabs."
- "This is what I use before starting my literature review."
- "Stop doing this manually."

Avoid:

- "Introducing our powerful AI tool."
- Generic feature lists.
- Unsupported academic or accuracy guarantees.

Always map:

```text
feature -> user scenario -> pain -> visible result -> CTA
```

## Reference Caption Adaptation

For the `research.connect` style, adapt at the caption-grammar level:

```text
How to [product-safe task] like a PhD/Master student (The easy way)
Just go to this website!
Click [product workflow]
Type [input]
It finds/shows [product-safe proof]
Pro tip! [user-controlled step]
Then [generate next artifact]
It's done! let's see...
[product-safe result proof]!
```

For Literfy, safe result proof examples:

- `A review draft based on real papers!`
- `A literature review outline from selected papers!`
- `A structured starting point from real sources!`

Unsafe result proof examples:

- `A perfect literature review!`
- `Submit this directly!`
- `A publication-ready paper!`
