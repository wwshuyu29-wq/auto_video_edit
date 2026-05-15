# Reflection: First Literfy Run

## What Went Wrong

1. The first script rewrite imitated the reference video only at the structure level. It did not initially preserve the reference video's exact subtitle grammar, short-command rhythm, or punctuation style.
2. The `strong_cta` beat was initially treated like a generic product reveal. It should have mapped to a landing page because the reference video's second sentence is a direct website CTA.
3. Asset matching over-relied on keyword overlap. It selected outline/result clips for beats that needed opening/CTA visuals.
4. The first script templates sounded too much like generated ad copy in places. TikTok creator style needs concrete workflow instructions and result proof.

## Required Behavior Going Forward

For every reference video:

1. Extract a `caption_logic` section before rewriting:
   - exact visible subtitle sequence
   - sentence roles
   - punctuation pattern
   - command verbs
   - CTA placement
   - result-proof wording
2. Product script rewrite must reuse the caption grammar, not just the story arc.
3. Asset matching must prioritize beat roles over keyword overlap.
4. Result claims must be mapped to product facts and forbidden-claim boundaries.

## Review Checklist

Before approving `product_script_card.json`:

- Does the first subtitle match the reference hook pattern?
- Does the second subtitle carry the same CTA force?
- Do command beats use short verbs like `Click`, `Type`, `Select`, `Generate`?
- Is there a `Pro tip!` style beat if the reference has one?
- Does the result proof use an exclamation mark or reveal wording if the reference does?
- Are all product claims allowed by `product-facts.md`?

Before approving `shot_matching_plan.json`:

- Does `hook` use the trust-object/opening clip?
- Does `strong_cta` use landing page/homepage/website reveal?
- Does product proof use actual product result clips?
- Are action clips and result clips separated?
- Is any clip reused for different semantic roles without a good reason?
