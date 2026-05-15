# Product Script Rewrite

## Goal

Turn a competitor's viral structure into original scripts for the user's product.

## Inputs

- Product: name, category, price, market, target user.
- Feature list: concrete functions and visible proof.
- Benefits: what changes for the user.
- Constraints: banned claims, compliance issues, unavailable footage, brand tone.
- Offer: discount, trial, bundle, guarantee, lead magnet, or no offer.

## Rewrite Rules

- Preserve the logic, not the words.
- Make one promise per video.
- Tie every claim to a product feature or visible proof.
- Use plain spoken language; avoid generic ad copy.
- Keep the first caption or spoken line short enough to read in under 2 seconds.
- Write for the footage that exists. If a beat needs footage that is missing, mark it as `needs_shot`.

## Script Variant Format

```json
{
  "title": "internal variant name",
  "duration_target_s": 25,
  "angle": "mistake / before-after / demo / comparison / objection / founder POV",
  "hook": "...",
  "beats": [
    {
      "beat": "HOOK",
      "time_s": "0-3",
      "copy": "...",
      "visual_need": "...",
      "product_feature": "...",
      "caption": "..."
    }
  ],
  "cta": "...",
  "claim_risks": ["..."],
  "missing_assets": ["..."]
}
```

## Useful TikTok Angles

- Mistake: "Most people use X wrong."
- Pattern interrupt: "I stopped doing X and this happened."
- Specific identity: "If you are a [persona], this saves you from [pain]."
- Proof first: show result, then explain.
- Comparison: old way versus product way.
- Objection: "I thought this was only for X, but..."
- Micro demo: one feature, one outcome, one CTA.

## Quality Bar

Reject scripts that are too broad, too polished, or impossible to prove. TikTok product videos usually work better when they feel observed, specific, and slightly imperfect.
