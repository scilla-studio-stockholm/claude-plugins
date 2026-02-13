---
name: knowledge-finder
description: Exhaustively search existing research to surface what's already known before starting new research. Use when someone asks "what do we know about...", wants to validate a hypothesis against existing data, needs to check if a product idea has supporting evidence, or wants to avoid duplicating research. Searches across multiple folders of past research (transcripts, reports, decks, spreadsheets) regardless of how files are organized. Produces bulletproof, fully-traced evidence summaries.
user_invocable: true
---

# Knowledge Finder

Surface existing knowledge from past research before starting new studies. Prevents duplicate research, validates hypotheses against existing data, and ensures decisions build on accumulated evidence.

**Core principle:** Exhaustive, traceable, truthful. Every claim traced to source. Every contradiction surfaced. No gaps.

## Workflow

### Step 1: Identify Research Sources

Ask the user where to look:

```
Where should I look for past research?

Option A: Give me folder paths (e.g., ./research, ./interviews, ./projects/Q3)
Option B: Describe what you're looking for and I'll search your files

Note: Research is often scattered across project folders. List ALL locations that might contain:
- Interview transcripts
- Survey results/exports  
- Research reports or decks
- Analytics summaries
- Customer feedback logs
- Usability test notes
- Sales/support call notes
```

If user provides paths → verify they exist, list file count by type.  
If user describes what to find → search for files matching: research, discovery, interview, transcript, survey, findings, insights, user, customer, feedback, usability, NPS.

### Step 2: Understand the Query

Ask what they want to know:

```
What do you want to find out? This could be:

- A question: "Why are users dropping off at checkout?"
- A hypothesis: "We think enterprise users need SSO"
- A product idea: "Adding a dashboard feature"
- A customer segment: "Enterprise buyers in healthcare"
- A problem space: "Onboarding friction"
- A job to be done: "Generating reports for stakeholders"
- A competitor concern: "How users compare us to Competitor X"
- An objection: "Pricing pushback from prospects"
```

Confirm the query before searching. Clarify ambiguous terms.

### Step 3: Run Exhaustive Search

Execute the search script:

```bash
python scripts/search_files.py <folders> --query "<user query>" -o results.json
```

**Critical: Review output stats.**
- Files analyzed: Should match expected file count
- Files with matches: If zero, try broader terms
- Total evidence: If very high (100+), prepare for comprehensive synthesis

The script searches ALL supported file types. See `references/file_type_handling.md` for details on:
- How each file type is parsed
- Location tracking by type (line, page, row, etc.)
- Speaker detection in transcripts
- Date detection from filenames and content

### Step 4: Synthesize Findings

Load the synthesis prompt from `references/synthesis_prompt.md` and apply it to the search results.

**Non-negotiable synthesis rules:**

1. **EXHAUSTIVE**: Include ALL evidence in the catalog. Never sample, summarize away, or "select key findings."

2. **TRACEABLE**: Every claim links to specific evidence with exact location (file, line/page/row, speaker).

3. **TRUTHFUL**: Show contradictions explicitly. Do not smooth over conflicting evidence. Reality is messy.

4. **QUANTIFIED**: Count everything. "7 of 12 participants (58%)" not "several users."

5. **DATED**: Flag evidence older than 12 months with ⚠️. Old findings may be obsolete.

6. **HUMBLE**: Distinguish strong evidence (multiple sources, consistent) from weak (single mention, dated).

### Step 5: Generate Report

Use the template in `assets/output_template.md`. Required sections:

1. **Summary** (2-3 sentences, honest about evidence strength)
2. **Evidence Catalog** (complete - every piece of evidence by source)
3. **Key Findings** (themes with 2+ supporting pieces)
4. **Contradictions & Tensions** (conflicting evidence, with counts and hypotheses)
5. **Isolated Observations** (single mentions - labeled as hypotheses)
6. **Gaps & Unknowns** (unanswered questions)
7. **Recommendation** (proceed / proceed with caveats / new research needed)

---

## Critical Analysis Standards

### What Makes a "Finding"

A finding requires:
- 2+ pieces of supporting evidence
- From different sources (not same person repeated)
- Consistent enough to form a pattern

Single mentions are **not findings**. They're hypotheses. Label them as "isolated observations."

### Handling Contradictions

When evidence conflicts:

1. **Present both sides with full evidence** - don't pick a winner
2. **Count supporters** - "5 participants said X, 3 said the opposite"
3. **Hypothesize explanations:**
   - Segment difference (enterprise vs SMB, new vs experienced)
   - Context difference (onboarding vs mature usage)
   - Timing (pre-launch vs post-launch)
   - Methodology (survey vs interview depth)
4. **Do NOT resolve artificially** - let the user see the complexity

### Evidence Quality Assessment

For each finding, evaluate:

| Factor | Strong | Weak |
|--------|--------|------|
| Recency | <12 months | >12 months ⚠️ |
| Consistency | Multiple sources agree | Single mention |
| Specificity | Clear, quotable | Vague, interpretive |
| Diversity | Multiple participants | Same person repeated |

### Red Flags to Surface

Always flag:
- All evidence from single source → ⚠️ Single Source Warning
- All evidence >12 months old → ⚠️ Dated Evidence Warning  
- Findings that contradict each other → Dedicated Contradictions section
- Crucial gaps → Prominent in Gaps section

---

## Query Types and Search Strategies

| Query Type | Search Approach | Look For |
|------------|-----------------|----------|
| Question ("Why do users...") | Search problem terms + behavior terms | Pain points, causes, contexts |
| Hypothesis ("Users need X") | Search for X + alternatives | Mentions of need, workarounds, requests |
| Product idea ("Add feature Y") | Search for Y + problem it solves | Demand signals, related requests, objections |
| Segment ("Enterprise users") | Search segment + pain/need/behavior terms | Segment-specific patterns |
| Problem space ("Onboarding") | Search space + friction/confusion/drop-off | Specific failure points |
| JTBD ("Generate reports") | Search job + outcome + context | When/why they need it, current solutions |
| Competitor | Search competitor name + compare/switch/vs | Comparison points, switching triggers |
| Objection | Search objection + price/cost/concern | Frequency, contexts, counterarguments |

---

## Output Quality Checklist

Before delivering the report, verify:

- [ ] Every finding has 2+ pieces of evidence
- [ ] Every evidence piece has exact source location
- [ ] Evidence catalog is COMPLETE (not sampled)
- [ ] Contradictions have dedicated section
- [ ] Single mentions labeled as isolated observations
- [ ] Dated evidence (>12mo) flagged with ⚠️
- [ ] Gaps section identifies unanswered questions
- [ ] Recommendation matches evidence strength
- [ ] File count in metadata matches files searched

---

## Dependencies

Required Python packages:
```bash
pip install python-docx pdfplumber openpyxl
```

The script will warn if packages are missing and continue with supported file types.

---

## When to Use This Skill

✅ **Use when:**
- Starting a new research project (check what exists first)
- Validating a hypothesis before testing
- Checking demand for a product idea
- Preparing for stakeholder questions
- Onboarding to a new domain/product
- Auditing existing research coverage

❌ **Don't use when:**
- Research files don't exist yet
- Need real-time/live data (use analytics tools)
- Looking for a single specific document (just search)
