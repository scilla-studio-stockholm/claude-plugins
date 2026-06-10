# OST golden fixture

A frozen, **synthetic** end-to-end example of the `product-discovery` (OST) pipeline in the
flat 2.0.0 workspace model. Use it to validate that the skills still produce a structurally
correct run, and to demo the OST Viewer without a live pipeline run.

## What's here

```
fixtures/golden/
├── README.md            ← you are here
├── RUBRIC.md            ← the structural checklist + verification commands
├── input/               ← frozen input you can re-run the pipeline against
│   ├── product-outcome.md
│   ├── experience-map.md
│   └── transcripts/     ← 4 synthetic discovery interviews (intervju-1..4-aurora)
└── expected-output/
    └── OST-discovery/   ← one full reference run in the flat 2.0.0 model
        ├── 1-opportunity.md … 4-experiments.md   ← 4 self-contained milestone docs
        ├── decisions.json                        ← the ratified spine
        ├── product-context/                      ← outcome + experience map
        └── _working/                             ← all phase JSON + intermediate markdown
```

## The case (fictional)

A fictional B2B company, **Flowbase**, sells API licences. New customers take too many
support-assisted steps to get from a signed contract to their first successful production
API call. The product outcome is a **self-serve activation / time-to-value** target:

> Öka andelen nya kunder som på egen hand når sitt första lyckade produktionsanrop mot
> API:et utan att kontakta Flowbase, från 40 % till 80 % inom 60 dagar från avtalstecknande.

The discovery team is **Team Aurora**. The run selects an activation-phase opportunity
("no guide / no self-serve onboarding"), brainstorms 18 solutions, narrows to 3, generates
and categorises assumptions, flags the riskiest, and designs validation experiments.

## Safe to distribute

Everything here is **synthetic**. It was derived from a real validated test run, but the
company, team, people, internal system names, and domain specifics have all been replaced
with a fictional generic-SaaS case. No real client, person, or product is identifiable.
The transcripts in `input/` are authored from scratch (not anonymised real interviews).

A safety gate (see `RUBRIC.md`) greps the whole fixture for identifying terms and must
return zero before any change here is committed.

## How to use it

**Validate the pipeline (structural golden-run):** run the checks in `RUBRIC.md` against
`expected-output/OST-discovery/`. They confirm the flat 5-file root, the 18-candidate
brainstorm, the 9 method-pass assumption set, self-contained milestones, schema-valid JSON,
and that every viewer tab has data to render.

**Demo the OST Viewer:** point the viewer (`product-discovery/templates/viewer/`) at
`expected-output/OST-discovery/` — it reads `decisions.json` from the scope root and the
view JSON from `_working/`.

**Re-run the pipeline from scratch (optional):** copy `input/` into a fresh
`OST-discovery/` scope and run the skills 00b → 13. Note that the skills are
non-deterministic, so a fresh run will **not** reproduce `expected-output/` byte-for-byte —
the committed output is a *reference*, not a diff target. For the same reason, the `~rad`
line references in the reference run's citations are **approximate/illustrative** and won't
line up exactly with the synthetic transcripts.
