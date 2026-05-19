# FigPad Materials Summary

Project: `projects/figpad/research-connect-google-scholar-template`

## Key Understanding

FigPad has too many features to force into one TikTok video. The better production logic is:

- One video = one core feature story.
- If two clips are very short and logically connected, combine them into one feature story.
- Use the same Google Scholar opening template, but change the product proof section per feature.

## Current Raw Footage

| Clip | Duration | Function | Best Use |
|---|---:|---|---|
| `00_google_scholar_hook` | 4.67s | Google Scholar trust opening | Cover / first hook |
| `01_figpad_dashboard` | 3.00s | FigPad dashboard | Product entry / click feature |
| `02_figpad_landing_page` | 6.77s | FigPad landing page | Strong CTA, "go to this website" |
| `03_text_to_figure_prompt` | 4.91s | Generate figure prompt input | Type prompt / generate figure |
| `04_text_to_figure_result` | 3.26s | Generated figure result | First proof result |
| `05_click_svg_edit` | 3.60s | Click SVG Edit after generated result | Bridge from generation to editability |
| `06_svg_editor_edit_demo` | 3.32s | SVG editor edit demo | Online editing proof |
| `07_svg_editor_edit_demo_2` | 4.91s | Second SVG editor edit demo | Stronger editability proof |
| `08_svg_canvas_zoom` | 5.29s | Canvas zoom in/out | Infinite canvas / flexible editing proof |
| `09_export_ppt_workflow` | 5.68s | Export PPT workflow | Export editable PPT |
| `10_ppt_export_result` | 2.92s | Exported PPT result | Final proof / PowerPoint continuation |
| `11_svg_converter_page` | 1.27s | SVG Converter page | Short transition / feature intro |
| `12_svg_converter_upload_convert` | 4.51s | Upload and convert bitmap | Main converter action |
| `13_svg_converter_download_svg` | 4.22s | Download converted SVG | Converter result proof |
| `14_image_to_image_workflow` | 9.02s | Image-to-image workflow | Separate feature video candidate |
| `15_svg_editor_new_project` | 3.87s | SVG Editor new project setup | Editor entry / editable project beat |

## Recommended Video Splits

### Video 1: Generate Figure -> SVG Edit -> Infinite Canvas

This is the strongest first FigPad video because it proves FigPad is not only a static AI image generator.

Suggested logic:

```text
Google Scholar hook
-> FigPad website reveal
-> generate figure prompt
-> generated scientific figure result
-> click SVG Edit
-> edit inside SVG editor
-> zoom/pan infinite canvas
-> optional PPT export or CTA
```

Why it works:

- Starts with an academic trust object.
- Shows a concrete before/after workflow.
- The key differentiator is editability after generation.
- "Infinite canvas" makes the editor feel more powerful than a normal image output.

Risk:

- Too many product actions can feel rushed. Keep this version around 25-30s and cut aggressively.

### Video 2: Bitmap -> SVG Converter

This should be a separate short video unless we only use it as a quick bonus beat.

Suggested logic:

```text
Google Scholar hook
-> "Still using flat images in your figures?"
-> open SVG Converter
-> upload bitmap
-> convert to SVG
-> download SVG
```

Why it works:

- The pain point is very specific.
- The visual proof is clear: flat bitmap becomes SVG/vector-style output.
- The clip set is short enough for a tight 18-24s video.

Risk:

- Do not claim every converted SVG is perfectly editable or scientifically accurate.

### Video 3: Editable PPT Export

This can either be combined with Video 1 as the ending proof, or become its own video if the exported PPT workflow is visually strong enough.

Suggested logic:

```text
Generate/edit figure
-> export as editable PPT
-> open/view result in PowerPoint
-> keep editing in Office
```

Why it works:

- Strong academic workflow value: researchers often need figures in slides.
- "Editable PPT" is more concrete than "download output".

Risk:

- Do not imply every detail is preserved perfectly in all Office versions.

### Video 4: Image-to-Image

Use `14_image_to_image_workflow` as a separate feature video candidate.

Reason:

- The clip is 9s and visually contains its own workflow.
- Combining it with generate/SVG/PPT would overcrowd one video.

## Open Questions Before Script Writing

1. Confirmed first public video direction: `Generate Figure -> SVG Edit -> SVG Editor -> editable canvas`.
2. Confirmed product wording: use `SVG Editor`, not `SVG Edit` as the editor name. `SVG Edit` can describe the button only if that is what the UI shows.
3. Confirmed canvas wording: use `editable canvas`, not `infinite canvas`.
4. For the first FigPad video, do you want the hook to be closer to the reference style:
   - `How to make your scientific figure like a PhD/Master student (The easy way)`
   - or more problem-driven:
   - `Still exporting static science figures?`
5. Decision pending: include PPT export in the first video, or keep the first video tightly focused on editable canvas.
