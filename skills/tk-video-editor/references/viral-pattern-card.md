# Viral Pattern Card

## Purpose

The viral pattern card is the stable output of `viral_deconstruction`.

It answers:

- Why does this competitor/account/video work?
- How does the opening grab attention?
- How does the content move from pain to proof?
- How does the creator show the tool or result?
- How does the ending convert?
- What can be reused safely?
- What cannot be copied?

It does not write scripts for the user's product.

## Standard Skill Output Contract

`viral_deconstruction` is a decision module, not a summary module. It must produce a reusable template card with:

- `template_id`: stable reference-template identifier, such as `research_connect_google_scholar`.
- `caption_logic`: visible sentence sequence, roles, punctuation rhythm, command grammar, CTA position, and result-proof position.
- `template_fingerprint`: compact facts that let downstream modules compare templates.
- `rewrite_boundaries`: what can be reused and what cannot be copied.
- `evidence_gaps`: missing evidence that weakens the analysis.

The downstream script module should be able to adapt Literfy, Citely, or FigPad from this card without a product-specific hardcoded template.

Known reference templates are stored in `references/template-library.json`.
Use this library when a URL/account/template is recognized, then let explicit
user-supplied `caption_logic` override the library if the user has a more
accurate transcript or subtitle sequence.

## Caption Logic

For TikTok references with visible text, the card must include `caption_logic`. This is the sentence-level operating system of the video. It should capture:

- Visible subtitle sequence.
- Role of each line: hook, CTA, command, tip, proof, reveal, CTA.
- Punctuation pattern: question marks, exclamation marks, parentheses, ellipses.
- Command grammar: `Click`, `Type`, `Select`, `Generate`, `Watch`.
- First-frame text density and line breaks.
- Any repeated phrase formulas.

The product rewrite stage should preserve this grammar where safe. Do not only summarize the video's topic.

Recommended roles:

```text
hook
strong_cta
command
input
pro_tip
workflow_progress
reveal_setup
result_proof
bonus_proof
cta
```

These roles are more important than the exact words. Exact words are reference evidence, not product copy.

Current canonical template IDs:

```text
research_connect_google_scholar
soft_student_era_human_hook
ice_uni_paper_hook
custom_reference_template
```

## Input Shape

```json
{
  "account_url": "https://www.tiktok.com/@example",
  "video_list": [
    {
      "video_url": "https://www.tiktok.com/@example/video/123",
      "views": 1200000,
      "likes": 53000,
      "comments": 1200,
      "caption": "Original caption",
      "transcript": "Voiceover or subtitle transcript",
      "frames_summary": "Key visual moments and on-screen text"
    }
  ],
  "target_platform": "TikTok",
  "analysis_goal": "Extract reusable product-marketing video structures"
}
```

## Output Shape

The module must write `output/viral_pattern_card.json`.

```json
{
  "account_positioning": "This account uses a student-friendly tone to solve academic workflow pain.",
  "template_id": "research_connect_google_scholar",
  "main_content_logic": "Status-gap hook -> tool reveal -> simple workflow -> result proof -> CTA",
  "template_fingerprint": {
    "line_count": 9,
    "roles": ["hook", "strong_cta", "command", "input", "pro_tip", "workflow_progress", "reveal_setup", "result_proof", "bonus_proof"],
    "has_early_cta": true,
    "has_command_chain": true,
    "has_result_reveal": true
  },
  "rewrite_boundaries": [
    "Do not write product script in this module.",
    "Do not copy exact reference wording unless it is generic platform grammar.",
    "Only preserve template roles, pacing, and rhetorical shape."
  ],
  "viral_patterns": [
    {
      "pattern_name": "Academic shortcut demo",
      "hook_type": "status gap / easier method",
      "hook_examples": ["How to write your paper like a PhD student"],
      "opening_0_3s": "Shows a familiar academic interface with a status-upgrade caption.",
      "middle_structure": [
        "Show the old/familiar workflow",
        "Reveal the tool",
        "Show 2-3 simple steps",
        "Show the finished output"
      ],
      "ending_cta": "Show result and invite trial/save/comment.",
      "visual_style": {
        "camera": "handheld laptop screen + screen recording",
        "pace": "1-3 seconds per beat",
        "subtitle_style": "large white text with black outline",
        "music": "light background music"
      },
      "why_it_works": [
        "The pain is familiar",
        "The output is visible",
        "The shortcut feels low effort"
      ],
      "reuse_risk": "Do not copy exact wording or imply false affiliation."
    }
  ],
  "recommended_templates": [
    {
      "template_name": "Problem-Solution-Demo-CTA",
      "timeline": [
        {"time": "0-2s", "purpose": "hook", "content": "Point to a high-frequency pain"},
        {"time": "2-6s", "purpose": "product appears", "content": "Reveal tool or result"},
        {"time": "6-15s", "purpose": "proof", "content": "Show workflow steps"},
        {"time": "15-22s", "purpose": "result", "content": "Show final output"},
        {"time": "22-28s", "purpose": "CTA", "content": "Invite trial/save/comment"}
      ]
    }
  ],
  "scores": {
    "hook_clarity": 8,
    "structure_reusability": 9,
    "product_adaptability": 7,
    "copy_risk": 3
  },
  "evidence_gaps": []
}
```

Recommended additional field:

```json
{
  "caption_logic": {
    "visible_sequence": [
      "How to write your thesis paper like a PhD/Master student (The easy way)",
      "Just go to this website!",
      "Click researcher",
      "Type your research paper topic",
      "Pro tip! use latex for pdfs",
      "Then watch it do its magic in 2-3 mins",
      "It's done! let's see...",
      "A complete research paper!",
      "With meaningful visualizations!"
    ],
    "sentence_roles": ["hook", "strong_cta", "command", "command", "pro_tip", "time_promise", "reveal_setup", "result_proof", "bonus_proof"],
    "punctuation_pattern": "question/status hook, exclamation CTA, short commands, Pro tip!, ellipsis before reveal, exclamation result proof",
    "reuse_rule": "Preserve rhythm and roles, replace claims with product-safe equivalents."
  }
}
```

## Scoring Notes

- `hook_clarity`: Can a viewer understand the promise in under 2 seconds?
- `structure_reusability`: Can the pattern support multiple product scripts?
- `product_adaptability`: Can the pattern map to the user's product truth?
- `copy_risk`: Higher means more risk of copying words, brand assets, or unsupported claims.
