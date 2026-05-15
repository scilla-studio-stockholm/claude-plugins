---
name: OST-validate-opportunities
description: For product trios and researchers, when validating opportunities written in interview-citation format, output a per-opportunity verdict (approved / needs tweak / solution in disguise) with motivation in a markdown table.
---

# Validate opportunities

You help a product trio quality-check opportunities they have drafted in interview-citation format, flagging which ones are well-formed and which need tweaks or are solutions in disguise.

This skill is assist 3a (validator) in `skills-design/opportunity-solution-tree-agents.md`.

## Steps

1. **Resolve scope.** Follow `../../knowledge/discovery/workspace-scope.md`. Portfolio scope only.

2. **Resolve input path:**
   - Default to `<scope>/opportunities-extracted.md` if it exists; otherwise ask the user for a path.

3. **Read the knowledge anchors:**
   - `../../knowledge/discovery/opportunity-citation-format.md` — the citation-format rules (what a valid citation contains, when and when not to tweak, examples).
   - `../../knowledge/discovery/opportunity-solution-tree-teresa-torres.md` — OST opportunity-space principles, used to detect solutions in disguise.

4. **Parse the markdown** to extract individual opportunities. Each opportunity in citation format has:
   - The verbatim quote (optionally with bracketed tweaks like `[interruption]` or `[...]`)
   - Source attribution (interviewee + interview reference + approximate timestamp)

5. **For each opportunity, apply the rules** from the citation-format anchor and Torres OST principles, and determine a verdict:
   - **✅ Approved (Godkänd)** — matches the citation format, is a real problem or need, source clearly attributed.
   - **🔧 Needs tweak (Behöver tweak)** — citation format mostly OK but the wording needs work (deictic language without brackets, internal references, missing source, no quote marks, etc.).
   - **⚠️ Solution in disguise** — describes a solution rather than a problem. The opportunity should be reframed as a need or pain. Keep this label in English; it is a Torres OST concept name.

6. **For each opportunity, write a brief motivation** explaining the verdict. Be concrete:
   - For "Needs tweak", name what specifically: e.g. "deictic 'det där' without bracketed clarification" or "no source attribution" or "long quote that should be cut with [...]".
   - For "Solution in disguise", point at the part of the wording that describes a solution: e.g. "'we need a better search function' is a proposed feature, not a need".
   - For "Approved", a dash is enough.

7. **Generate a markdown table** in this format:

   ```markdown
   # Opportunity validation — <YYYY-MM-DD>

   Source file: `<input filepath>`

   | # | Opportunity (excerpt) | Verdict | Motivation |
   |---|---|---|---|
   | 1 | "<quote excerpt>" | ✅ Approved | - |
   | 2 | "<quote excerpt>" | ⚠️ Solution in disguise | <one-line reason> |
   | 3 | "<quote excerpt>" | 🔧 Needs tweak | <one-line reason> |

   ## Summary

   - Approved: <N>
   - Needs tweak: <N>
   - Solution in disguise: <N>
   ```

8. **Save the output** as `<scope>/opportunities-validated.md` unless the user specifies a different path.

## Output principles

- **Output language matches input language.** Detect the language from the actual opportunity quotes, not from file metadata. If opportunities are in Swedish, the verdict labels and motivations are in Swedish (Godkänd / Behöver tweak). If English, English (Approved / Needs tweak).
- **Keep "solution in disguise" as English term** regardless of input language. It is a Torres OST concept name and is not translated.
- **Verbatim quote excerpts.** Truncate to ~50 characters in the table column for readability if needed, but never paraphrase. The full quote stays verbatim from the input.
- **Concrete motivations.** Vague motivations like "format wrong" or "needs work" are not enough. Say what specifically.
- **No rewrite suggestions.** This skill flags only. The trio decides how to fix. AI-suggested wording would taint the trio's voice in their backlog.

## What this skill does NOT do

- Does not suggest concrete rewrites for problematic opportunities. The trio's own formulation is canonical; the skill's job is to point at issues, not fix them.
- Does not parse interview transcripts to find new opportunities. That is `extract-opportunities`.
- Does not cluster opportunities against an experience map. That is `OST-cluster-opportunities`.
- Does not compare opportunities against a product outcome. That is `OST-compare-opportunities`.
- If the input file is plain prose (no quote + source structure), note that and ask the user whether they meant to run `extract-opportunities` first.
