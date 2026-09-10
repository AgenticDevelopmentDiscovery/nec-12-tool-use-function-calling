---
name: round
description: Run one critique round on the document. Builds the three outputs as a gate, dispatches every reviewer persona in personas/ independently, then synthesizes their reports into one ranked docket at rounds/round-NNN/SYNTHESIS.md. Use when the user says "/round", "run a round", "critique the document", "get feedback", "what should we fix", or "review this draft". One round per invocation. Produces feedback and a docket; never edits sections/.
---

# Run one critique round

One round is: **gate, panel, synthesis, stop.**

It ends with a ranked docket and a recommendation. It does **not** edit the
document — deciding what to act on is the team's job, and handing that decision
to the reviewer is how a critique loop turns into an echo chamber.

---

## 1. Number the round

List `rounds/`. The new round is the next integer after the highest existing
`round-NNN`, zero-padded to three digits. If none exist, this is `round-001`.

Create `rounds/round-NNN/`.

## 2. Gate on the build

Run `just build`.

**If it fails, stop the round.** Report the error and what to fix. A document
that does not render is not ready to be read, and a reviewer call spent on one is
wasted. This gate is cheap and mechanical on purpose: never spend judgment on a
draft that a command could have rejected.

The gate is render-or-not, nothing more. It does not check whether the slides
*read* — overflow is silent, and judging it is the `visual` reviewer's job, not
the gate's.

## 3. Establish the panel

The panel **is** the directory listing: every `personas/*.md` **except**
`aggregator.md`, which is not a seat.

Do not hardcode the roster. Adding a reviewer to this project means dropping a
file into `personas/`, and this step is what makes that true.

## 4. Dispatch the reviewers — independently

Launch **one subagent per persona, all in a single message so they run
concurrently.** Give each one:

- the full text of its persona file, as its brief;
- every `sections/*.prose.md` and every `sections/*.concepts.md`;
- `topic.md` — the proposal, which is what the document promised to be;
- `metadata.yaml` — the declared `audience` is the standard they judge against;
- the round number;
- the build result from step 2.

Each subagent writes `rounds/round-NNN/<persona-name>.md` in the output format
its persona file specifies, and reports back only that it finished.

**Reviewers must not see each other's reports.** Independence is what makes
agreement between two seats mean something — if they can read each other, the
second reviewer is anchored by the first and the consensus you get is an artifact
of the dispatch order, not evidence about the document. Do not summarize one
review into another's prompt. Do not run them in sequence sharing context.

**Do not give them the previous round's synthesis either.** A reviewer who knows
last round's docket grades the team's compliance instead of reading the document.
Continuity is the aggregator's job, and it needs a fresh reading to compare
against.

## 5. Aggregate

Read `personas/aggregator.md` and follow it exactly. Its inputs are the reports
just written, plus `rounds/round-<N-1>/SYNTHESIS.md` if a previous round exists.

Write `rounds/round-NNN/SYNTHESIS.md`.

The three rules that matter most, restated because they are the ones most often
softened:

- **The panel's recommendation is the lowest tier any seat gave.** Never averaged.
- **Introduce no finding no reviewer raised.** Anything you noticed yourself goes
  under *Panel health*, not the docket.
- **Report honestly whether the last docket was acted on.** The prose is the
  evidence, not anyone's intention.

## 6. Stop and report

Tell the user, in a few lines:

- the panel recommendation and each seat's tier;
- the *Do next* items from the synthesis;
- the path to `rounds/round-NNN/SYNTHESIS.md`.

Then **stop**. Do not edit `sections/`, do not commit, do not start another round.

If the user then asks you to act on an item, that is ordinary editing work
against the docket — not part of this skill.

---

## Notes

**One round per invocation.** Running two rounds without a revision between them
produces two readings of the same document; the second costs a full panel and
tells you nothing new.

**A round is cheap to repeat and expensive to fake.** If the team has not
changed the prose since the last round, say so and ask whether they want to spend
the panel anyway.
