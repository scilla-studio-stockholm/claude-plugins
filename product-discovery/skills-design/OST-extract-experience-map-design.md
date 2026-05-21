---
title: "OST-extract-experience-map: design spec"
date: 2026-05-09
purpose: Locked design for assist 2 in opportunity-solution-tree-agents.md - reads a screenshot of a trio's experience map and produces paired JSON + markdown of the journey structure (phases, steps, friction, decision branches, extensions). Opportunities are not in scope for this skill. Input to the implementation plan.

---

# OST-extract-experience-map: design spec

This is the locked design for **assist 2** in `opportunity-solution-tree-agents.md`. It is the third skill built (after `OST-opportunity-extractor` and `OST-validate-opportunities`) and the first that uses vision. The implementation plan derives from this document.

## What the skill does

For product trios and researchers, when extracting a screenshot of an experience map into structured form, output paired JSON (per the experience-mapping schema) plus markdown rendering of the journey structure (phases, steps, friction levels, decision branches, team-specific extensions).

Input is a single PNG or JPG screenshot of an experience map. Output is two files in `workspace/1-opportunity-val/` with the same root name: a JSON file conforming to schema v0.1 in `../knowledge/discovery/experience-mapping.md`, and a markdown rendering generated deterministically from the JSON.

**Out of scope for this skill:** reading or populating `phases[].opportunities[]`. At the stage where this skill runs, opportunity citat-stickies have not yet been clustered onto the map. Opportunities are added to the journey by a separate workflow downstream. The schema retains `phases[].opportunities[]` as an optional slot that downstream skills or manual processes populate; this skill always omits the key.

## Scope decisions (locked 2026-05-09)

The brainstorm narrowed scope significantly from the original spec in `opportunity-solution-tree-agents.md`. Each decision below resolves an open question that was parked there.

| Question | Decision |
|---|---|
| Miro MCP vs vision/screenshot | Screenshot only, via the Read tool's vision support. No MCP for v1. |
| Schema-validation strictness | Tiered. Hard exit on missing required fields, best-effort with warnings on optional fields. |
| Journey-logic evaluation as extra output | Out of scope. Skill transcribes only. Journey-quality feedback is the trio's job (or a future assist). |
| Opportunity extraction | Out of scope. At OST-extract-experience-map time, opportunities have not yet been clustered onto the map. The schema slot stays open for a downstream workflow. |
| Skill vs agent | Plain skill. The brainstorm-input recommendation of "agent" was based on now-dropped scope (MCP, transcript correlation, iteration). |
| Output-file convention | Paired output at `workspace/1-opportunity-val/experience-map-extracted-<YYYY-MM-DD>.{json,md}`, per cross-cutting datakontrakt. |

## Skill identity

| Field | Value |
|---|---|
| File path | `.claude/skills/OST-extract-experience-map/SKILL.md` |
| Skill name | `OST-extract-experience-map` |
| Slash-command (optional) | `/OST-extract-experience-map` if frequency justifies it |
| Body language | English, matching the precedent set by `OST-validate-opportunities` |

**Description field** (load-bearing for natural-language trigger):

> For product trios and researchers, when extracting a screenshot of an experience map into structured form, output paired JSON (per the experience-mapping schema) plus markdown rendering of the journey structure (phases, steps, friction, decision branches).

This follows the "for X, when Y, output Z" pattern. It is generic, not Metria-specific. It is distinct from `OST-validate-opportunities` (validates opportunity text, no vision) and `OST-opportunity-extractor` (reads transcripts, not maps).

## Inputs and prerequisites

**Operator passes:** path to a PNG or JPG screenshot of an experience map. The skill defaults to `workspace/context/experience-map.png`, falling back to `workspace/context/experience-map.jpg` if the PNG is absent. If neither file exists, the skill asks the operator for the path. If both exist, the PNG is used and a warning is emitted.

**Optional fallback file:** `workspace/context/product-outcome.md`. Used only if the `product_outcome` field cannot be extracted from the screenshot header. When the fallback is used, the skill emits a warning in the markdown output.

**Knowledge anchor read at runtime:** `../knowledge/discovery/experience-mapping.md` for schema v0.1 and the structural pattern. Per the cross-cutting datakontrakt decision, this is read at runtime rather than hard-coded into the prompt.

**What the skill does NOT extract or validate:**

- Opportunities (`phases[].opportunities[]`). At OST-extract-experience-map time, opportunities are not yet on the map. They are populated by a separate downstream workflow.
- The format of citat-stickies. Format validation belongs to `OST-validate-opportunities` downstream. Duplicating taxonomy across skills is an anti-pattern called out in the skill template.

## Steps

The skill follows the same numbered-step pattern as `OST-validate-opportunities`:

1. **Read the knowledge anchor** at `../knowledge/discovery/experience-mapping.md` for schema v0.1 and the structural pattern.
2. **Get input from the user.** Default to `workspace/context/experience-map.png`, falling back to `workspace/context/experience-map.jpg` if the PNG is absent. If neither exists, ask for the path.
3. **Read the screenshot** via the Read tool (vision).
4. **Extract journey-structure fields** from the image in a single vision pass against schema v0.1: `team`, `title`, `product_outcome`, `narrativ`, `phases[].name/order/friction_level`, `phases[].steps[].description/decision_branches`, `extensions`. Do NOT extract `phases[].opportunities[]` — that key is always omitted from the output JSON. Extract required fields with confidence; extract optional fields best-effort.
5. **Apply tiered strictness** (see Error handling section).
6. **Compose the JSON object** strictly against schema v0.1, with `phases[].opportunities` omitted from every phase per the optional-key convention.
7. **Render markdown deterministically from the JSON** via an embedded template in the prompt (see Output composition).
8. **Write paired output** to `workspace/1-opportunity-val/experience-map-extracted-<YYYY-MM-DD>.json` and the matching `.md`.

The extraction is a single vision pass. No retries, no multi-screenshot iteration, no self-validation pass against the schema after composition. If the screenshot quality is insufficient for required fields, the skill exits with a clear error and asks the operator to re-screenshot.

## Output composition

Two files with the same root name:

```text
workspace/1-opportunity-val/experience-map-extracted-<YYYY-MM-DD>.json
workspace/1-opportunity-val/experience-map-extracted-<YYYY-MM-DD>.md
```

**The JSON** is strict schema v0.1 from `../knowledge/discovery/experience-mapping.md`. No extra fields. `phases[].opportunities` is always omitted: OST-extract-experience-map does not populate it, and per the missing-optional-fields convention, absent keys signal absence rather than empty arrays.

**The markdown** is generated deterministically from the JSON via an embedded template in the prompt:

```markdown
---
title: Experience map - <title> (<team>)
date: <YYYY-MM-DD>
purpose: Extracted experience map for OST opportunity work, paired with experience-map-extracted-<date>.json

---

# Experience map: <title> (<team>)

Source screenshot: `<path>`
Schema version: 0.1
Paired JSON: `experience-map-extracted-<YYYY-MM-DD>.json`

## Product outcome

<full outcome formulation>

## Narrativ
[only if present]

<narrativ>

## Journey

### Phase 1: <name> (friction: <low|medium|high>)
[friction line shows "(friction: not recorded)" when the field is omitted from JSON]

**Steps:**
- <description>
- [step description not legible]
  - Branch: <label> -> <leads_to>

[repeat for each phase in order]

## Extensions
[only if present]

**Systems in use:** Outlook, Freshdesk, ...

## Warnings
[only if any]

- product_outcome was missing from the screenshot; fell back to workspace/context/product-outcome.md
- Phase 4 friction_level was ambiguous; field omitted from JSON [uncertain]
- Phase 2 step 3 description was illegible; description field omitted from JSON [uncertain]
```

The frontmatter on the markdown output complies with the Metria global rule that every `.md` file has YAML frontmatter. This creates a discrepancy with `OST-validate-opportunities`, whose output template currently lacks frontmatter; that is captured as a follow-up and will be fixed separately rather than by leaving this skill non-compliant.

## Knowledge-doc updates required before ship

The skill formalizes optionality on two fields that the existing v0.1 schema doc treats ambiguously. As part of building this skill, `../knowledge/discovery/experience-mapping.md` is updated to:

- Mark `phases[].friction_level` and `phases[].steps[].description` as optional, with the convention that an absent key means the field could not be observed.
- State the missing-key convention explicitly so downstream skills handle it consistently.

This stays within schema v0.1 because we are clarifying ambiguous text, not adding, removing, or breaking fields.

## Error handling

**Tiered strictness:**

| Category | Field | Behavior on extraction miss |
|---|---|---|
| Required | `product_outcome` | Fall back to `workspace/context/product-outcome.md`. If that is missing too: hard exit. |
| Required | `title`, `team`, `phases[].name`, `phases[].order` | Hard exit. |
| Required | `phases[]` not empty, `phases[].steps[]` not empty | Hard exit. |
| Optional | `narrativ`, `phases[].friction_level`, `phases[].steps[].description`, `phases[].steps[].decision_branches`, `extensions` | Best-effort. If ambiguous: skip or mark `[uncertain]`, add an entry to the Warnings section. |
| Always omitted | `phases[].opportunities` | Out of scope; populated by a downstream workflow. |
| Auto-generated | `schema_version` (always `"0.1"`), IDs (`fas-N`, `step-N-M`) | Assigned by the skill; never extracted from the screenshot. |

**Convention for missing optional fields in JSON:** the skill omits the key entirely rather than writing `null`. A phase with no extractable friction has no `friction_level` key. A step with no extractable description has no `description` key. The markdown rendering shows `(friction: not recorded)` and `[step description not legible]` for these cases. Downstream skills must handle key absence as the missing-value signal.

**Hard-exit message format:**

```text
ERROR: Required field 'product_outcome' could not be extracted.
- Screenshot: workspace/context/experience-map.png
- Looked for: header text formulating an outcome (e.g. starting with "Reduce", "Increase", or a measurable behavior change).
- Found: header area appears cropped or absent.
- Fallback: workspace/context/product-outcome.md not found.
- Remedy: Re-screenshot the map including the header section, or create workspace/context/product-outcome.md with the trio's outcome formulation.
```

The pattern is three pieces: what failed, what the skill saw, what to do about it. No silent degradation. No retries. No self-validation of composed JSON.

**Other error scenarios:**

- **Screenshot path missing or not an image** → hard exit "expected PNG or JPG at <path>".
- **Screenshot exists but is not an experience map** (vision cannot detect any phase structure) → hard exit "could not detect a journey structure (phases) in <path>; verify this is an experience map screenshot".
- **Opportunity stickies visible on the map** → ignored. The skill does not read them, regardless of whether they are present. Out-of-scope content is silently passed over, not warned about.

## Testing

Smoke test only for v1, no formal regression harness:

```text
Input:  knowledge/discovery/Trio - Team Norrsken - Opportunity Solution Tree - Licenstilldelning.jpg
Expect: 7 phases matching the names listed in experience-mapping.md
        ("Förfrågan inkommer", "Behovsanalys & avtal", "Avtalsskrivning",
         "Kreditkontroll & ekonomi", "Licens-upplägg", "Rabatter",
         "Aktivering & leverans"), friction levels per the documented gradient,
        and the systems_in_use list under extensions.
```

Eyeball the JSON output. If phases are missing, friction is wrong, or stickies are paraphrased, the prompt is wrong. A formal regression harness is overkill for v1 with two operators.

## Open follow-ups

These are added to the existing cleanup TODO list rather than blocking v1.

1. **Skill-template body-language line.** `skills-design/skill-template.md` still says "Svenska i body och output". After this skill ships, update the template to reflect the English convention now confirmed across `OST-validate-opportunities` and `OST-extract-experience-map`. Already on the cleanup list.
2. **`OST-validate-opportunities` output frontmatter.** Add YAML frontmatter to its output template, matching the format used here, so generated `.md` files comply with the Metria global frontmatter rule.
3. **Trio process guide design-time names.** Already on the cleanup list for "Format-validator" → `OST-validate-opportunities`. The same guide refers to assist 2 by a design-time name; rename to `OST-extract-experience-map` in the same sweep.
4. **Schema evolution to v0.2.** Bumps when (a) a trio creates a map whose structure does not fit (friction at step level, journey-level start/end states) or (b) a downstream skill requests new fields. Procedure: add an "Evolution" entry to `experience-mapping.md` and bump `schema_version` in skill prompts. Not triggered yet.
5. **Miro MCP path.** Revisit if re-running the skill on the same map becomes painful enough that operators want a refresh-from-board command. Trigger is operator pain, not theoretical completeness.
6. **Multi-screenshot or very large maps.** Current design assumes one screenshot fits the whole map at readable quality. If trios produce maps too large for a single screenshot, add a stitch feature.
7. **Transcript correlation.** Parked entirely. Revisit only if a downstream opportunity-clustering workflow needs it.
8. **Journey-logic evaluation.** Parked entirely. Revisit only if trios produce maps with logic flaws that go undetected by trio review and start affecting downstream assists.
