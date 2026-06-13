export const meta = {
  name: 'ost-solution-phase',
  description: 'Run the OST solution phase (assists 07→09) as one pipeline, stopping at the trio HITL gate',
  whenToUse: 'When the trio has ratified decided.opportunity in decisions.json and wants the divergent brainstorm, clustering, and top-3 selection in one run.',
  phases: [
    { title: 'Brainstorm', detail: '3 rounds × 3 role agents per assist 07' },
    { title: 'Compose', detail: 'write solution-candidates.{json,md}' },
    { title: 'Cluster', detail: 'assist 08 thematic clusters' },
    { title: 'Select', detail: 'assist 09 top-3 proposal + milestone doc' },
  ],
}

// args: { pluginRoot, scope, date: "YYYY-MM-DD" }
const input = typeof args === 'string' ? JSON.parse(args) : args
if (!input || !input.pluginRoot || !input.scope || !input.date) {
  throw new Error('args must be { pluginRoot, scope, date: "YYYY-MM-DD" }')
}
const { pluginRoot, scope, date } = input
const skill = (dir) => `${pluginRoot}/skills/${dir}/SKILL.md`
const SKILL07 = skill('07-OST-brainstorm-solutions')

const COMMON = `
Operating rules for this workflow run (they override the skill's interactive behavior, nothing else):
- Today's date is ${date}. The resolved scope is: ${scope} (flat single-product layout). Do not re-resolve scope or ask the user anything.
- Read the SKILL.md named below from disk and execute the named steps exactly, including reading the knowledge anchors it names (references/ next to the SKILL.md).
- Skip any "launch the viewer" step.
- If a hard-exit condition fires, write NO output files; return the skill's ERROR block as your result text and nothing else.
- Your final text is consumed by a script, not a human. On success return exactly: OK <one line: files written>. On hard-exit return the ERROR block.`

const IDEAS_SCHEMA = {
  type: 'object',
  required: ['ideas'],
  properties: {
    ideas: {
      type: 'array', minItems: 2, maxItems: 2,
      items: {
        type: 'object', required: ['title', 'description'],
        properties: { title: { type: 'string', description: '5-12 words' }, description: { type: 'string', description: '1-3 sentences' } },
      },
    },
    error: { type: 'string', description: 'hard-exit ERROR block if prerequisites fail; omit on success' },
  },
}

const ROLES = [
  { key: 'pm', name: 'Product Manager', anchor: 'role-product-manager.md' },
  { key: 'ux', name: 'UX Designer', anchor: 'role-ux-designer.md' },
  { key: 'tl', name: 'Tech Lead', anchor: 'role-tech-lead.md' },
]

// ---- Phase 1: Brainstorm — 3 sequential rounds, 3 parallel blind role agents per round ----
phase('Brainstorm')
const pool = [] // {id, generating_role, round_number, title, description}
for (const round of [1, 2, 3]) {
  log(`Brainstorm round ${round} (pool: ${pool.length} ideas)`)
  const poolBlock = pool.length
    ? `\nPrior idea pool (cross-round anti-duplication context):\n${JSON.stringify(pool, null, 2)}\nAnti-duplication rule (verbatim from the skill): each idea must be either NEW (different core mechanism / target / surface from any prior idea in the pool) OR an explicit build-on of a specific prior idea (cite the prior idea by id or title in your description, e.g., 'Builds on sol-r1-pm-2 by ...'). Paraphrases or rewordings of prior ideas are not allowed.`
    : ''
  const results = await parallel(ROLES.map((r) => () =>
    agent(`You are one of the three role-diversified brainstorm sub-agents defined by the skill at: ${SKILL07} (read it, steps 1-11, to understand your framing duties).

Your role: ${r.name}. Read your role anchor in full: ${pluginRoot}/skills/07-OST-brainstorm-solutions/references/${r.anchor}
Also read, as the skill instructs: references/solution-brainstorm.md (broad solution-scope definition), references/tech-product-trio-responsibility-split.md and references/product-trio-operational-practices.md (cross-role baselines), references/opportunity-solution-tree-teresa-torres.md (explore-multiple-solutions framing) — all in the same references/ folder.

Ground yourself in ${scope}/decisions.json: decided.opportunity (id, phase_id, quote, source, scores, rationale) and product_outcome. If decisions.json is missing or decided.opportunity is absent, return the skill's ERROR block in the "error" field and an empty-ideas placeholder is NOT allowed — put two empty-string ideas and the error field.

Round ${round} task (verbatim from the skill): produce 2 solution candidates from your role's frame. Each candidate has a short title (5-12 words) and a 1-3 sentence description. Range freely across user-facing features, process redesigns, policy changes, integration changes, automation, internal tooling, removed steps, or org-level changes - whatever your role's lens suggests would plausibly move the product outcome on this opportunity. No effort vocabulary. Write titles/descriptions in the language of the chosen opportunity quote.${poolBlock}`,
      { label: `r${round}:${r.key}`, phase: 'Brainstorm', schema: IDEAS_SCHEMA })
  ))
  for (let i = 0; i < ROLES.length; i++) {
    const r = results[i]
    if (!r || r.error) return { stopped_at: `brainstorm-r${round}-${ROLES[i].key}`, error: r ? r.error : 'sub-agent failed' }
    r.ideas.forEach((idea, j) => pool.push({
      id: `sol-r${round}-${ROLES[i].key}-${j + 1}`,
      generating_role: { pm: 'product-manager', ux: 'ux-designer', tl: 'tech-lead' }[ROLES[i].key],
      round_number: round,
      title: idea.title,
      description: idea.description,
    }))
  }
}
if (pool.length !== 18) return { stopped_at: 'brainstorm', error: `ERROR: expected 18 ideas, got ${pool.length}` }

// ---- Phase 2: Compose solution-candidates.{json,md} ----
phase('Compose')
const compose = await agent(`${COMMON}

Execute steps 12-15 (compose v0.1 JSON, render markdown, write paired output) of the skill at: ${SKILL07}
The three brainstorm rounds are already done. Use this collected pool verbatim (ids, roles, rounds, titles, descriptions are final — byte-identical carry-through):
${JSON.stringify(pool, null, 2)}
Pull chosen_opportunity, product_outcome, and team from ${scope}/decisions.json per the skill's steps 6-7. Write ${scope}/_working/solution-candidates.json and .md per the skill's template and output principles.`,
  { label: 'compose:solution-candidates', phase: 'Compose' })
if (typeof compose === 'string' && compose.startsWith('ERROR')) return { stopped_at: 'compose', error: compose }

// ---- Phases 3-4: Cluster (08) → Select top 3 (09) ----
const results = { brainstorm: `18 ideas (3 rounds × 3 roles × 2)`, compose }
for (const s of [
  { title: 'Cluster', dir: '08-OST-cluster-solutions' },
  { title: 'Select', dir: '09-OST-select-top-three-solutions' },
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

log('Solution phase complete — top-3 proposal written, waiting on trio HITL in decisions.json')
return {
  status: 'awaiting_trio_hitl',
  milestone: `${scope}/2-solutions.md`,
  ratified_record: `${scope}/decisions.json (decided.solutions)`,
  ...results,
}
