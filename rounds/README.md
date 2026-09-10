# rounds/

One folder per critique round, committed. This is the project's memory.

```
rounds/
  round-001/
    clarity.md        one reviewer's independent report
    pedagogy.md
    visual.md
    SYNTHESIS.md      the aggregator's ranked docket — read this one
  round-002/
    ...
```

## Why these are committed

The reviews are not scratch. Kept in the repository, they let you answer the one
question that actually tells you whether the loop is working:

> **Is the same finding still here three rounds later?**

A docket item that survives four rounds is not a hard problem. It is a problem
the team keeps deciding not to solve — and seeing that in the diff is far more
useful than any single review.

The aggregator reads the previous `SYNTHESIS.md` for exactly this reason, and
opens every synthesis with a *Since last round* verdict on each prior item.

## Reading a round

Start with `SYNTHESIS.md`; it is the actionable artifact. The individual reports
are there for when you want to know *why* an item is on the docket, or when you
disagree with the docket and want to check the aggregator against its sources.

## Rules

- **Never edit a past round.** It is a record of what was true then. If a review
  was wrong, the next round says so.
- **Do not act on individual reports directly.** They have not been reconciled;
  two of them may want opposite things. That is what the synthesis is for.
- **Do not delete rounds to tidy up.** The history is the point.
