export const meta = {
  name: 'ost-opportunity-phase',
  description: 'Run the OST opportunity phase (assists 02→06) as one pipeline, stopping at the trio HITL gate',
  whenToUse: 'When a discovery trio has cleaned transcripts and an extracted experience map, and wants the full opportunity phase (extract → validate → cluster → compare → select proposal) in one run.',
  phases: [
    { title: 'Extract', detail: 'one agent per transcript, citat-stickies per assist 02' },
    { title: 'Merge', detail: 'compose opportunities-extracted.md' },
    { title: 'Validate', detail: 'assist 03 verdict table' },
    { title: 'Cluster', detail: 'assist 04 phase clustering' },
    { title: 'Compare', detail: 'assist 05 Torres matrix' },
    { title: 'Select', detail: 'assist 06 proposal + milestone doc' },
  ],
}

// args: { pluginRoot, scope, transcripts: [absolute paths], date: "YYYY-MM-DD" }
// pluginRoot = product-discovery plugin root (contains skills/), scope = OST-discovery/ path.
const input = typeof args === 'string' ? JSON.parse(args) : args
if (!input || !input.pluginRoot || !input.scope || !Array.isArray(input.transcripts) || !input.transcripts.length || !input.date) {
  throw new Error('args must be { pluginRoot, scope, transcripts: [paths], date: "YYYY-MM-DD" } — transcripts non-empty')
}
const { pluginRoot, scope, transcripts, date } = input
const skill = (dir) => `${pluginRoot}/skills/${dir}/SKILL.md`

// Shared rules so SKILL.md execution stays faithful but non-interactive inside a workflow.
const COMMON = `
Operating rules for this workflow run (they override the skill's interactive behavior, nothing else):
- Today's date is ${date}. The resolved scope is already known: ${scope} (flat single-product layout). Do not re-resolve scope or ask the user anything.
- Read the SKILL.md named below from disk and execute it exactly: same knowledge-anchor reads (references/ symlinks next to the SKILL.md), same output files, same templates, same output principles. Do not paraphrase quotes; carry fields byte-identical as the skill demands.
- Skip any "launch the viewer" step — the workflow handles presentation.
- If a hard-exit condition fires, do NOT write output files; return the skill's ERROR block as your result text and nothing else.
- Your final text is consumed by a script, not a human. On success return exactly: OK <one line: files written>. On hard-exit return the ERROR block.`

const STICKIES_SCHEMA = {
  type: 'object',
  required: ['file', 'interviewee_context', 'stickies', 'counts', 'flags'],
  properties: {
    file: { type: 'string', description: 'shortened transcript filename' },
    interviewee_context: { type: 'string', description: 'one-line context tag: interviewee + project type' },
    stickies: {
      type: 'array',
      items: {
        type: 'object',
        required: ['bucket', 'quote', 'attribution'],
        properties: {
          bucket: { type: 'string', enum: ['Klar opportunity', 'Möjlig opportunity', 'Lösning förklädd'] },
          quote: { type: 'string', description: 'verbatim quote with [tweaks]/[...] per the format anchor' },
          attribution: { type: 'string', description: '<first name>, <shortened filename>, ~rad <line>' },
        },
      },
    },
    counts: {
      type: 'object',
      required: ['klar', 'mojlig', 'losning'],
      properties: { klar: { type: 'number' }, mojlig: { type: 'number' }, losning: { type: 'number' } },
    },
    flags: { type: 'array', items: { type: 'string' }, description: 'low-signal / under-extraction / out-of-scope flags per skill step 12, empty if none' },
  },
}

// ---- Phase 1: Extract — one agent per transcript, in parallel ----
phase('Extract')
log(`Extracting opportunities from ${transcripts.length} transcript(s)`)
const extractions = await parallel(transcripts.map((t) => () =>
  agent(`${COMMON}

Execute the extractor skill at: ${skill('02-OST-opportunity-extractor')}
Apply it to this single transcript only: ${t}
Read the transcript IN FULL (never sample or skim). Do NOT write opportunities-extracted.md yourself — a merge step composes it. Instead return the extracted citat-stickies as structured output, in transcript order, following every extraction/exclusion/tweak rule in the skill and its references/opportunity-citation-format.md anchor. Output content language: match the transcript (Swedish stays Swedish).`,
    { label: `extract:${t.split('/').pop()}`, phase: 'Extract', schema: STICKIES_SCHEMA })
))
const ok = extractions.filter(Boolean)
if (ok.length !== transcripts.length) {
  log(`WARNING: ${transcripts.length - ok.length} transcript extraction(s) failed or were skipped`)
}
if (!ok.length) throw new Error('No transcript yielded an extraction result — aborting before any file is written')

// ---- Phase 2: Merge — compose the canonical opportunities-extracted.md ----
phase('Merge')
const mergeResult = await agent(`${COMMON}

Execute steps 9-12 (formatting, grouping, metadata block, save) of the extractor skill at: ${skill('02-OST-opportunity-extractor')}
The per-transcript extraction is already done. Compose ${scope}/_working/opportunities-extracted.md from this pre-extracted data, byte-faithful to each quote and attribution, grouped one H3 section per source file in the order given, each section prefixed with its context tag, with the metadata block (counts per bucket per file and total, plus any flags) at top and YAML frontmatter per the skill.

Pre-extracted data (JSON):
${JSON.stringify(ok, null, 2)}`,
  { label: 'merge:opportunities-extracted', phase: 'Merge' })
if (typeof mergeResult === 'string' && mergeResult.startsWith('ERROR')) return { stopped_at: 'merge', error: mergeResult }

// ---- Phases 3-6: Validate → Cluster → Compare → Select, sequential ----
const STAGES = [
  { title: 'Validate', dir: '03-OST-validate-opportunities' },
  { title: 'Cluster', dir: '04-OST-cluster-opportunities' },
  { title: 'Compare', dir: '05-OST-compare-opportunities' },
  { title: 'Select', dir: '06-OST-select-opportunity' },
]
const results = { extracted: ok.length, merge: mergeResult }
for (const s of STAGES) {
  phase(s.title)
  const r = await agent(`${COMMON}

Execute the skill at: ${skill(s.dir)}
All upstream files for this round already exist under ${scope}. Default input paths apply.`,
    { label: s.title.toLowerCase(), phase: s.title })
  results[s.title.toLowerCase()] = r
  if (typeof r === 'string' && r.startsWith('ERROR')) {
    log(`${s.title} hard-exited — stopping the pipeline (no downstream writes)`)
    return { stopped_at: s.title.toLowerCase(), error: r, ...results }
  }
}

log('Opportunity phase complete — proposal written, waiting on trio HITL in decisions.json')
return {
  status: 'awaiting_trio_hitl',
  milestone: `${scope}/1-opportunity.md`,
  ratified_record: `${scope}/decisions.json (decided.opportunity)`,
  ...results,
}
