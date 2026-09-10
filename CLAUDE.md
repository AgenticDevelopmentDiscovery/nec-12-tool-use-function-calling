# nel-course — project instructions

This is a **template**. A team clones it, replaces the content in `sections/`
with their own subject, and improves it one critique round at a time.

Everything below describes how this project works. It is written to be read by a
person as much as by an agent — the method is the thing being taught, so there is
no separate protocol file to keep in sync.

---

## What this project is

An **evolutionary framework for a document**: one artifact, improved by repeated
critique, never restarted.

The word *evolutionary* is doing real work, and it is worth being precise about
what it does and does not mean here. There is no population and no selection
among variants. There is **one document**, moved forward and never reverted. Each
round the document is read by a panel of independent reviewers, their findings
are reconciled into a ranked docket, the team acts on part of it, and the next
round reads what resulted.

What accumulates is not a better draft chosen from many. It is a record of what
was found and what was done about it — which is why `rounds/` is committed.

## The three outputs

One Markdown source in `sections/` becomes three artifacts:

| Output | Built by | What it is |
| --- | --- | --- |
| **Document** | `just doc` | `output/document.pdf` — the long-form read |
| **Presentation** | `just slides` | `output/slides.pdf` — one slide per `##` heading |
| **Website** | `just site` | `_site/` — one page, sidebar contents, both PDFs linked |

`just build` makes all three. `just serve` previews the site at `localhost:8000`.
`just deploy` publishes to GitHub Pages.

There is no generator and no engine. The section order is a **shell glob** over
`sections/*.prose.md`, so the numeric prefixes on the filenames are the document
order. Add a section by adding a numbered pair — nothing needs registering.

### The slide constraint is a writing constraint

Slides are made at `--slide-level=2`: **every `##` heading becomes one slide, and
what sits under it must fit.**

Treat overflow as a finding about the prose, not a formatting nuisance. A `##`
unit that will not fit a slide is almost always carrying more than one idea, or
padded. Split it or cut it. Shrinking the font hides the signal.

Nothing in the build checks this for you — pandoc hides the TeX log unless the
render fails, so an overfull frame is silent. That is deliberate. Overflow is a
judgement about whether a slide reads, not a threshold to pass: look at the deck,
or ask the agent to look at it with you. The `visual` reviewer names the `##`
units it believes are carrying too much, and you confirm against the page.

This is the whole reason the presentation shares a source with the document
rather than being written separately: it is a standing check on whether the prose
has kept its shape.

## The artifact: a section is a pair

Each section is **two registers of one subject**:

```
sections/03-content.prose.md      what ships — rendered into all three outputs
sections/03-content.concepts.md   the spine  — never rendered, always reviewed
```

The sidecar is not a draft of the prose and not a summary of it. It holds what
the prose cannot say in its own voice:

- **Claims** — the load-bearing assertions, one line each.
- **Decisions** — why the section reads the way it does, and what was rejected.
- **Open questions** — what the team does not know yet.
- **Not doing** — scope deliberately excluded.

Keep it in note form. Prose in a `.concepts.md` file is a sign you wrote in the
wrong register.

**Why bother.** Two things fall out of it, and neither is available from prose
alone. The team stops relitigating settled choices, because the reason is written
down where the next round will find it. And the panel can see the gap between
intention and delivery: a spine that keeps growing while the prose stalls is a
finding the reviewers are briefed to report. Promise is not delivery.

Both registers go to every reviewer.

### One level up: the proposal

`topic.md` is to the whole tutorial what a `.concepts.md` is to one section: the
register that does not ship, holding what the team intends before any of it is
prose. It states the topic, the case for it, the capability the reader walks away
with, and what is deliberately out of scope.

It goes to every reviewer, and that is the point of it. Without a stated promise
the panel can only judge whether the prose is good — not whether it is the
tutorial the team said they were writing. Promise is not delivery at the document
level either.

Write it before the first section, and revise it when the subject moves. A
proposal that no longer matches the tutorial is worse than none, because the panel
will hold the document to it.

### The shipped arc

The template ships four sections, in the order a tutorial teaches:

| Section | Answers | Holds |
| --- | --- | --- |
| `01-context` | WHAT | what the topic is, and where it came from |
| `02-motivation` | WHY | why it matters for agentic development, and when it does not |
| `03-content` | HOW | the mental model, worked use, and the pitfalls |
| `04-conclusion` | WHAT ELSE | what the reader can now do, and what is still open |

WHAT before WHY is deliberate. A reader who does not yet know what the thing is
cannot judge an argument for why it matters, so a tutorial that opens with the
case for itself is asking the reader to evaluate a claim about something they
cannot picture.

`03-content` is the tutorial and should be the longest by some margin. It ships
with four `##` units and will usually need more — each new heading is another
slide, and splitting is how you find the joints in your own explanation.

The arc is a default, not a guardrail. Change it if your subject wants a
different shape; the build is a glob, so renaming and renumbering the pairs is
the whole operation.

## The loop: one round at a time

```
/round
```

That is the whole verb. It is defined in [.claude/skills/round/SKILL.md](.claude/skills/round/SKILL.md).
One round is:

1. **Gate.** `just build`. If the document does not render, the round stops here
   and nothing else is spent. Mechanical rejection is cheap; judgment is not.
2. **Panel.** Every persona in `personas/` (except the aggregator) reads the
   document **independently and concurrently**, and writes its own report into
   `rounds/round-NNN/`.
3. **Synthesis.** The aggregator reconciles those reports into one ranked docket
   at `rounds/round-NNN/SYNTHESIS.md`.
4. **Stop.** The docket is a proposal. A human decides what to act on.

Acting on an item is ordinary editing work, done after the round and separately
from it. The loop closes when the *next* round reads the result — the aggregator
opens every synthesis by reporting whether the last docket was actually done.

### Why the reviewers are independent

They run in parallel and cannot see each other's reports. This is not an
optimization.

If the second reviewer can read the first, it is anchored by it, and the
agreement you get afterwards is an artifact of dispatch order rather than
evidence about the document. Independence is what makes two seats naming the same
passage *mean something* — and that agreement is the strongest signal the
aggregator has when it ranks the docket.

The same reasoning keeps last round's synthesis away from the panel. A reviewer
who knows the outstanding docket grades the team's compliance instead of reading
the document. Continuity belongs to the aggregator, which needs a fresh reading to
compare against.

## The panel

The panel **is** the contents of `personas/`. There is no roster to maintain:
add a reviewer by dropping a file in, remove one by deleting it. Nothing else
reads a list of seats — `/round` globs the directory and the aggregator reports
whatever filed. The three below are what the template ships with, not a fixed set.

| Seat | Asks |
| --- | --- |
| [clarity](personas/clarity.md) | Is there a through-line, and does the prose earn its length? |
| [pedagogy](personas/pedagogy.md) | Is this ready for the declared audience? |
| [visual](personas/visual.md) | Do the figures teach, and does it survive all three renderings? |

[aggregator](personas/aggregator.md) is **not a seat**. It reads the reports, not
the document.

The declared `audience` in [metadata.yaml](metadata.yaml) is the standard the
pedagogy reviewer judges against. It is the highest-leverage field in this
project: a vague audience produces vague review, because the reviewer has nothing
to hold the document to. Write it before the first round.

## Guardrails

**Never edit `sections/` during a round.** `/round` produces feedback and stops.
A reviewer that also revises has no one checking it.

**Never edit a past round.** `rounds/round-NNN/` records what was true then. If a
review was wrong, the next round says so — do not retouch the history that makes
recurrence visible.

**Never invent findings during synthesis.** The aggregator carries only what a
reviewer raised. Anything it noticed itself goes under *Panel health*, where it
reads as what it is: evidence that a seat is missing or a brief needs sharpening.

**Never soften the recurrence report.** A docket item surviving three rounds is
the most useful thing the loop can tell a team, and the most tempting thing to
phrase gently.

**Do not average recommendations.** The panel's tier is the lowest any seat gave.
Two reviewers finding minor polish do not outvote one that found a hole; they were
each looking at something different, and the one that found the hole found a real
hole.

**Do not commit unless asked.**

## House conventions

> **This section is yours.** Everything above describes the framework; put
> anything specific to *your* project here — notation you have settled on,
> sections that are off limits, a collaborator's preferences, deliberate
> departures from the guardrails above and why.

- **The `scaffold:*` skills do not apply to this project.** `md2tex`, `tex2md`
  and `progression` operate on a LaTeX layout — `sections/<name>.tex`, `main.tex`,
  a `PROGRESSION.md` — that does not exist here. Their vocabulary overlaps this
  one ("sidecar", "propagate the concepts"), so they look applicable and are not.
  This project's registers are `.prose.md` and `.concepts.md`, and the only verb
  is `/round`.

## Your topic

What your team is actually working on is written in **[topic.md](topic.md)**, not
here. This file describes the method; that one describes the subject, and keeping
them apart is what lets the panel read the proposal without reading the protocol.

Before the first round, in this order:

1. **[topic.md](topic.md)** — the proposal. What the topic is, why it belongs in
   this course, what the reader will be able to do, and what is out of scope.
2. **[metadata.yaml](metadata.yaml)** — the title, the authors, and the
   `audience` the pedagogy reviewer judges against.
3. **`sections/`** — replace the placeholder content, guided by the two above.
