# Competitor Teardown

## Goal

Extract transferable creative logic from competitor TikTok videos without copying their wording, identity, or unique assets.

## Teardown Fields

For each account or video, capture:

- Account positioning: niche, audience, product category, persona, trust source.
- Repeating content formula: what the account does again and again.
- Hook: exact first-frame idea, first line, promise, conflict, or curiosity gap.
- Viewer trigger: pain, shame, aspiration, fear, speed, price, convenience, status, novelty, proof.
- Structure: hook, context, proof/demo, objection handling, payoff, CTA.
- Visual pattern: handheld, face-to-camera, POV, product close-up, screen recording, before/after, street/interview, UGC, text-only.
- Pacing: average shot length, jump-cut density, caption density, music/voice balance.
- Proof: demo result, testimonial, comparison, numbers, visible transformation, social proof.
- CTA: soft follow/save/comment, hard purchase, quiz, link, DM keyword.
- Reusable formula: one sentence that abstracts the logic.

## Viral Pattern Output

Use this compact schema:

```json
{
  "reference": "account or video",
  "positioning": "...",
  "repeatable_formula": "...",
  "hook_types": ["..."],
  "structure": ["HOOK", "PROBLEM", "PROOF", "PAYOFF", "CTA"],
  "visual_rules": ["..."],
  "caption_rules": ["..."],
  "cta_rules": ["..."],
  "risks": ["claims or style elements that should not be copied directly"]
}
```

## Operator Notes

If several videos from the same account use one logic, compress them into one formula and list variations. The goal is to find the machine behind the posts, not to summarize every video.

Good formulas are product-agnostic enough to reuse, for example:

- "Start with a common mistake, demonstrate the hidden consequence, then show a one-step product fix."
- "Open with a surprising before/after, show the exact action that caused it, then invite viewers to try it."
- "Call out a specific identity group, show a relatable failure, then reveal the tool that removes the friction."
