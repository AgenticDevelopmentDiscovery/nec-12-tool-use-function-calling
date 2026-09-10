# figures/

Drop figures here and reference them from a `.prose.md` section:

```markdown
![A caption that teaches on its own.](figures/my-figure.svg){#fig:mine width=70%}
```

Paths are written **relative to the repository root**, not to the section file —
that is where pandoc runs from.

## Format

**Prefer SVG or PDF.** Both are vector, so they stay sharp in the document, on a
projector, and on a high-DPI screen. Use PNG for screenshots and photographs,
nothing else.

> **SVG in the PDF outputs needs `rsvg-convert`.** The website uses SVG directly,
> but pandoc has to rasterize it for LaTeX. If `just doc` fails with
> *"check that rsvg-convert is in path"*, install it:
> `brew install librsvg` (macOS) or `apt-get install librsvg2-bin` (Debian).
> CI already has it. A PDF figure needs no converter at all, but will not display
> on the website — so SVG plus librsvg is usually the better trade.

## What the panel looks for

The `visual` reviewer does not count figures. It asks whether each one makes a
relationship visible that the prose leaves abstract, and it will tell you to
delete any figure that merely decorates.

This template ships with **no figures**, so expect the first round to say so.
The most valuable one in most tutorials shows the mental model in
§ Content § How it works — the boxes, the arrows, the one relationship the prose
leaves abstract. If you add only one, add that.
