export const meta = {
  name: 'ost-assumption-phase',
  description: 'Run the OST assumption phase (assists 10→12) as one pipeline, stopping at the trio HITL gate',
  whenToUse: 'When the trio has ratified decided.solutions in decisions.json and wants assumption generation (3 methods × 3 solutions), categorization, and riskiest-assumption scoring in one run.',
  phases: [
    { title: 'Preflight', detail: 'assist 10 input checks + context extraction' },
    { title: 'Generate', detail: '9 method-pass agents (3 methods × 3 picks)' },
    { title: 'Dedup', detail: '3 per-solution dedup passes' },
    { title: 'Compose', detail: 'write assumptions.{json,md}' },
    { title: 'Categorize', detail: 'assist 11 Cagan categories' },
    { title: 'Riskiest', detail: 'assist 12 importance/evidence scoring + milestone doc' },
  ],
}

// args: { pluginRoot, scope, date: "YYYY-MM-DD" }
const input = typeof args === 'string' ? JSON.parse(args) : args
if (!input || !input.pluginRoot || !input.scope || !input.date) {
  throw new Error('args must be { pluginRoot, scope, date: "YYYY-MM-DD" }')
}
const { pluginRoot, scope, date } = input
const skill = (dir) => `${pluginRoot}/skills/${dir}/SKILL.md`
const SKILL10 = skill('10-OST-generate-assumptions')

const COMMON = `
Operating rules for this workflow run (they override the skill's interactive behavior, nothing else):
- Today's date is ${date}. The resolved scope is: ${scope} (flat single-product layout). Do not re-resolve scope or ask the user anything.
- Read the SKILL.md named below from disk and execute the named steps exactly, including reading the knowledge anchors it names (references/ next to the SKILL.md).
- Skip any "launch the viewer" step.
- If a hard-exit condition fires, write NO output files; return the skill's ERROR block as your result text and nothing else.
- Your final text is consumed by a script, not a human. On success return exactly: OK <one line: files written>. On hard-exit return the ERROR block.`

// ---- Phase 1: Preflight — run assist 10's steps 1-8 once, extract shared context ----
phase('Preflight')
const PREFLIGHT_SCHEMA = {
  type: 'object',
  required: ['ok'],
  properties: {
    ok: { type: 'boolean' },
    error: { type: 'string', description: 'the skill ERROR block when ok=false' },
    team: { type: 'string' },
    product_outcome: { type: 'string' },
    chosen_opportunity: {
      type: 'object', required: ['id', 'phase_id', 'quote', 'source'],
      properties: { id: { type: 'string' }, phase_id: { type: 'string' }, quote: { type: 'string' }, source: { type: 'string' } },
    },
    picks: {
      type: 'array', minItems: 3, maxItems: 3,
      items: {
        type: 'object', required: ['id', 'title', 'description', 'rationale', 'generating_role', 'round_number'],
        properties: {
          id: { type: 'string' }, title: { type: 'string' }, description: { type: 'string' },
          rationale: { type: 'string' }, generating_role: { type: 'string' }, round_number: { type: 'number' },
        },
      },
    },
    experience_map_path: { type: 'string', description: 'resolved path to experience-map .json or .md' },
  },
}
const pre = await agent(`${COMMON}

Execute steps 1-8 (locate inputs, hard-exit checks, parse, merge, cross-check) of the skill at: ${SKILL10}
Do NOT spawn sub-agents and do NOT write any files — generation happens elsewhere. Return the extracted context as structured output: team, product_outcome, chosen_opportunity, the 3 merged picks (with generating_role and round_number from top-three-solutions.json), and the resolved experience-map path. On any hard-exit trigger set ok=false and put the ERROR block in "error".`,
  { label: 'preflight', phase: 'Preflight', schema: PREFLIGHT_SCHEMA })
if (!pre || !pre.ok) return { stopped_at: 'preflight', error: pre ? pre.error : 'preflight agent failed' }

// ---- Phase 2: Generate — 9 method-pass agents in parallel ----
phase('Generate')
const METHODS = ['storymap', 'pre-mortem', 'outcome-impact']
const GEN_SCHEMA = {
  type: 'object', required: ['assumptions'],
  properties: {
    assumptions: {
      type: 'array', minItems: 6, maxItems: 6,
      items: { type: 'object', required: ['text'], properties: { text: { type: 'string', description: '1-2 sentences max' } } },
    },
  },
}
const jobs = []
for (const method of METHODS) for (const pick of pre.picks) jobs.push({ method, pick })
const gen = await parallel(jobs.map((j) => () =>
  agent(`You are one of the 9 method-pass sub-agents defined by step 9 of the skill at: ${SKILL10} — read that step and the "three methods" section of references/assumption-generation.md (in the references/ folder next to the SKILL.md) for your exact framing, the definition of assumption, and the task wording. Apply the "${j.method}" method.
${j.method === 'storymap' ? `Storymap only: read the experience map at ${pre.experience_map_path} — it is today's journey; reason about the future flow the solution implies, not today's.` : ''}
Chosen opportunity: ${JSON.stringify(pre.chosen_opportunity)}
Product outcome: ${pre.product_outcome}
The solution you reason about: ${JSON.stringify(j.pick)}
If ${scope}/tree.json exists (cross-round living tree), read it: assumptions already validated in prior rounds count as evidence (you may still list one if it remains load-bearing — note it has prior support); invalidated ones must not silently reappear as fresh assumptions. Absence of tree.json is fine.
Produce exactly 6 assumptions per the skill's task wording (1-2 sentences each, no categorization, no effort vocabulary, language of the solution description).`,
    { label: `${j.method}:${j.pick.id}`, phase: 'Generate', schema: GEN_SCHEMA })
))
if (gen.filter(Boolean).length !== 9) return { stopped_at: 'generate', error: `ERROR: ${9 - gen.filter(Boolean).length} of 9 method-pass agents failed` }

// ---- Phase 3: Dedup — one pass per solution ----
phase('Dedup')
const DEDUP_SCHEMA = {
  type: 'object', required: ['assumptions'],
  properties: {
    assumptions: {
      type: 'array', minItems: 6, maxItems: 18,
      items: {
        type: 'object', required: ['text', 'source_methods'],
        properties: {
          text: { type: 'string' },
          source_methods: { type: 'array', minItems: 1, maxItems: 3, items: { type: 'string', enum: ['storymap', 'pre-mortem', 'outcome-impact'] } },
        },
      },
    },
  },
}
const deduped = await parallel(pre.picks.map((pick) => () => {
  const raw = jobs.map((j, idx) => ({ j, idx })).filter(({ j }) => j.pick.id === pick.id)
    .flatMap(({ j, idx }) => gen[idx].assumptions.map((a) => ({ text: a.text, source_method: j.method })))
  return agent(`Execute the per-solution dedup pass defined by step 10 of the skill at: ${SKILL10} (read that step for the exact dedup task wording — merge same-belief entries, preserve source methods as an array, never invent or drop distinct assumptions).
Solution: ${JSON.stringify({ id: pick.id, title: pick.title, description: pick.description })}
The 18 raw method-tagged assumptions for THIS solution:
${JSON.stringify(raw, null, 2)}`,
    { label: `dedup:${pick.id}`, phase: 'Dedup', schema: DEDUP_SCHEMA })
}))
if (deduped.filter(Boolean).length !== 3) return { stopped_at: 'dedup', error: 'ERROR: a dedup pass failed' }

// Deterministic ids + canonical source_methods order (skill step 11) — plain code, not an agent.
const ORDER = ['storymap', 'pre-mortem', 'outcome-impact']
const perSolution = pre.picks.map((pick, i) => ({
  solution: pick,
  assumptions: deduped[i].assumptions.map((a, n) => ({
    id: `asm-${pick.id}-${String(n + 1).padStart(3, '0')}`,
    text: a.text,
    source_methods: ORDER.filter((m) => a.source_methods.includes(m)),
  })),
}))

// ---- Phase 4: Compose assumptions.{json,md} ----
phase('Compose')
const compose = await agent(`${COMMON}

Execute steps 12 onward (compose the v0.1 JSON, render markdown, write paired output) of the skill at: ${SKILL10}
Generation, dedup, and id assignment are already done. Use this data verbatim (ids, texts, source_methods are final — byte-identical carry-through):
${JSON.stringify({ team: pre.team, product_outcome: pre.product_outcome, chosen_opportunity: pre.chosen_opportunity, per_solution: perSolution }, null, 2)}
Write ${scope}/_working/assumptions.json and .md per the skill's schema, template, and output principles.`,
  { label: 'compose:assumptions', phase: 'Compose' })
if (typeof compose === 'string' && compose.startsWith('ERROR')) return { stopped_at: 'compose', error: compose }

// ---- Phases 5-6: Categorize (11) → Riskiest (12) ----
const results = { generated: 54, deduped: perSolution.map((s) => s.assumptions.length).join('+'), compose }
for (const s of [
  { title: 'Categorize', dir: '11-OST-assumption-categorizer' },
  { title: 'Riskiest', dir: '12-OST-riskiest-assumptions' },
]) {
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

log('Assumption phase complete — riskiest-assumption proposal written, waiting on trio HITL in decisions.json')
return {
  status: 'awaiting_trio_hitl',
  milestone: `${scope}/3-riskiest-assumptions.md`,
  ratified_record: `${scope}/decisions.json (decided.assumptions)`,
  ...results,
}
