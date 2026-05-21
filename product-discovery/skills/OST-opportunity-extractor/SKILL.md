---
name: OST-opportunity-extractor
description: Extract opportunity candidates from cleaned interview transcripts as citat-stickies. Reads each transcript in full and extracts customer-voice utterances that carry pain, friction, unmet need, workaround, avoidance, worry, or expressed wish. Output is per-file groups of verbatim citat-stickies pre-classified for trio review. Use when a discovery trio needs to surface opportunities from interview material before opportunity selection.
---

# Opportunity extractor

You help a product trio extract opportunity candidates from interview transcripts as citat-stickies.

This skill is assist 3a (extractor) in `skills-design/opportunity-solution-tree-agents.md`.

## Substrate: semantic reading, not keyword search

You read each transcript in full and decide what is opportunity-bearing. You are not a search index. Earlier versions of this skill wrapped a keyword-based search tool — that approach missed implicit friction, language-mismatched terms, and signals that lived in episode structure rather than vocabulary. Do not reintroduce that approach.

If a transcript is long enough that you would be tempted to skim or sample, dispatch one subagent per transcript via `superpowers:dispatching-parallel-agents` with this same skill body and merge results. Never sample.

## Prerequisites

- Transcripts must be cleaned with speaker labels. If they are not, recommend `scilla-research:transcript-cleaner` first and exit.

## Steps

1. **Resolve scope.** Follow `references/workspace-scope.md`. Opportunity-selection scope only — the resolved path must contain `/opportunity-selection/`. If no opportunity-selection round exists for the target product yet, create a new round folder dated today: `discovery/<team>/<product>/opportunity-selection/<YYYY-MM-DD>/`.

2. **Load context via parent walk-up (optional):**
   - `<scope>/../../_product-context/product-outcome.md` (if it exists; the extractor can run without it)

3. **Read the format anchor:** `references/opportunity-citation-format.md` — for citat-stickie format, tweak rules, and when to tweak.

4. **Confirm transcript inputs.** If the user gave file paths, use them. If they gave a folder, list the transcript files and confirm. Skip non-transcript siblings in the same folder (synthesis docs, coaching notes, interviewer-technique feedback). If a transcript file has a feedback or coaching preamble before the actual conversation, identify where the conversation starts and only extract from the conversation portion.

5. **Read each transcript in full.** Identify the customer-side speakers (the interviewee) and the interviewer-side speakers. Everything you extract must come from the customer side.

6. **Identify opportunity-bearing utterances.** A customer utterance is an opportunity candidate when it carries any of:
   - **Explicit friction** — "det är jobbigt", "det krånglar", "det tar tid", direct complaint
   - **Implicit friction in a recounted episode** — describes manual cleanup, retries, second-guessing, work that should be automatic but isn't, doing-it-twice
   - **Workaround behavior** — "vi gör det i Excel sen", "jag mejlar X", "vi tar i för säkerhets skull", routing around the official path
   - **Unmet need** — "vi får inte ut", "det finns inte", "vi saknar", "ingen vet"
   - **Avoidance** — "jag undviker", "vi slipper inte", "det är därför vi inte..."
   - **Expressed wish** — "det hade varit guld", "om man kunde", "drömmen vore"
   - **Worry or risk** — "det är en risk att", "vi är nervösa för", "om vi missar"
   - **Quantified cost** — time, money, headcount, effort — any number attached to a pain

7. **Do NOT extract:**
   - Interviewer questions, pivots, or framing
   - Affirmation tokens ("ja", "mm", "exakt") without content
   - Pure workflow descriptions without friction signal (the customer describing their process neutrally)
   - Customer agreement with a leading question — that's interview artifact, not signal
   - Setup, intro, sign-off, or rapport material
   - Section headers added by the transcript-cleaner (lines starting with `#`)
   - Anything from a feedback or coaching preamble prepended to the transcript file

8. **Classify each extracted utterance** into one of three buckets:
   - `[Klar opportunity]` — friction/need is clear and self-supporting in the quote
   - `[Möjlig opportunity]` — friction or need is hinted at, but the trio needs context to decide
   - `[Lösning förklädd]` — the customer is describing a specific solution (a feature, a UI, a process), not the underlying need. Flag for the validator.

   There is no `[Bakgrund]` bucket. Contextual or neutral material is not extracted at all.

9. **Format each as a citat-stickie:**

   ```markdown
   [Bucket]

   > "Verbatim quote, with [tweaks] only for deictic refs / internal abbreviations; cuts marked [...]"
   >
   > <Customer first name>, <shortened filename>, ~rad <line>
   ```

   Apply the tweak rules from the format anchor. When uncertain, prefer raw quote.

10. **Group by source file.** One H3 section per transcript. Inside each section, citat-stickies in transcript order (so the trio can find them by scrolling). Each section starts with a one-line context tag: interviewee + project type.

11. **Add a metadata block** at the top:
   - Number of transcripts read
   - Number of opportunity candidates extracted, by bucket, per file and total
   - Any transcripts where extraction yielded few candidates — flag for the trio

12. **Save the result** as `<scope>/opportunities-extracted.md` with YAML frontmatter (title, date, team, purpose: "Extracted opportunity candidates from interview transcripts for this opportunity-selection round", source_transcripts, based_on_outcome if known, tags).

## Output principles

- **Verbatim quotes.** Do not paraphrase. Tweak only per the format anchor's rules. When in doubt, leave raw.
- **No fabrication.** If a quote doesn't exist verbatim in the transcript, you have no quote. Re-read.
- **Exhaustive on the customer side.** Include every customer utterance that carries opportunity signal. The trio narrows. Better to over-include a Möjlig than to drop a Klar.
- **No interviewer voice in the output.** If interviewer phrasing contaminated an answer (forced pivot, leading question), note it once in the metadata block, not as a citat-stickie.
- **Skill body in English. Output content in Swedish** (matching the language of the transcripts). Keep English concept names (opportunity, citat-stickie).

## When extraction yields suspiciously few candidates

If one transcript produces 0–3 candidates while siblings produce 10+, flag in the metadata block with one of:
- Likely under-extracted — re-read with a slower pass
- Interview produced low signal — interviewer accepted surface answers, didn't probe; trio should consider re-interviewing
- Out-of-scope customer — describes a workflow the outcome doesn't target

Do not silently drop a transcript with few hits.

## What this skill does NOT do

- Validate opportunity format on items the trio already has (separate `OST-validate-opportunities` skill).
- Cluster opportunities against an experience map (separate `OST-cluster-opportunities` skill).
- Judge which opportunities are strongest (separate comparator/selector skills).
